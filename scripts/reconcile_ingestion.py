from pathlib import Path

from sqlalchemy import text

from src.database.connection import engine
from src.ingestion.json_reader import read_json
from src.ingestion.parser import parse_match


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cricsheet"
    / "ipl_json"
)


def get_source_counts() -> dict:
    """Calculate record counts directly from the source JSON files."""

    files = sorted(DATA_DIR.glob("*.json"))

    matches = 0
    innings = 0
    deliveries = 0
    extras = 0
    wickets = 0

    for file_path in files:

        match_id = int(file_path.stem)

        data = read_json(file_path)

        match = parse_match(
            data=data,
            match_id=match_id,
        )

        matches += 1

        innings += len(match.innings)

        for inning in match.innings:

            deliveries += len(inning.deliveries)

            for delivery in inning.deliveries:

                extras += len(delivery.extras)

                wickets += len(delivery.wickets)

    return {
        "matches": matches,
        "innings": innings,
        "deliveries": deliveries,
        "extras": extras,
        "wickets": wickets,
    }


def get_database_counts() -> dict:
    """Read corresponding record counts from PostgreSQL."""

    queries = {
        "matches": """
            SELECT COUNT(*)
            FROM dim_match
        """,

        "innings": """
            SELECT COUNT(*)
            FROM match_innings
        """,

        "deliveries": """
            SELECT COUNT(*)
            FROM fact_delivery
        """,

        "extras": """
            SELECT COUNT(*)
            FROM delivery_extras
        """,

        "wickets": """
            SELECT COUNT(*)
            FROM delivery_wickets
        """,
    }

    counts = {}

    with engine.connect() as connection:

        for name, query in queries.items():

            result = connection.execute(
                text(query)
            )

            counts[name] = result.scalar_one()

    return counts


def main() -> None:

    print("=" * 70)
    print("IPL INGESTION RECONCILIATION")
    print("=" * 70)

    print()
    print("Calculating SOURCE counts...")
    print("This may take a little while because all JSON files are scanned.")

    source = get_source_counts()

    print("Source scan completed.")

    print()
    print("Reading DATABASE counts...")

    database = get_database_counts()

    print("Database scan completed.")

    print()
    print("-" * 70)

    print(
        f"{'Metric':<15}"
        f"{'Source':>15}"
        f"{'Database':>15}"
        f"{'Difference':>15}"
        f"{'Status':>12}"
    )

    print("-" * 70)

    all_match = True

    for metric in [
        "matches",
        "innings",
        "deliveries",
        "extras",
        "wickets",
    ]:

        source_count = source[metric]
        database_count = database[metric]

        difference = database_count - source_count

        status = "PASS" if difference == 0 else "FAIL"

        if difference != 0:
            all_match = False

        print(
            f"{metric:<15}"
            f"{source_count:>15,}"
            f"{database_count:>15,}"
            f"{difference:>15,}"
            f"{status:>12}"
        )

    print("-" * 70)

    print()

    if all_match:
        print("RECONCILIATION : PASS")
        print("Source and database record counts match.")
    else:
        print("RECONCILIATION : FAIL")
        print("Source and database record counts do not match.")

    print("=" * 70)


if __name__ == "__main__":
    main()