from pathlib import Path

from src.ingestion.json_reader import read_json
from src.ingestion.parser import parse_match
from src.validation.match_validator import validate_match


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "cricsheet"/"ipl_json"


def main() -> None:
    json_files = sorted(DATA_DIR.glob("*.json"))

    if not json_files:
        raise RuntimeError(
            f"No JSON files found in {DATA_DIR}"
        )

    file_path = json_files[0]

    data = read_json(file_path)

    match = parse_match(
        data=data,
        match_id=int(file_path.stem),
    )

    result = validate_match(match)

    print("=" * 60)
    print("MATCH VALIDATION")
    print("=" * 60)

    print(f"File      : {file_path.name}")
    print(f"Match ID  : {match.match_id}")
    print(f"Teams     : {len(match.teams)}")
    print(f"Players   : {len(match.players)}")
    print(f"Innings   : {len(match.innings)}")

    total_deliveries = sum(
        len(innings.deliveries)
        for innings in match.innings
    )

    print(f"Deliveries: {total_deliveries}")

    print("\nVALIDATION RESULT")
    print("-" * 60)

    if result.is_valid:
        print("STATUS: VALID")
        print("No validation errors found.")

    else:
        print("STATUS: INVALID")
        print(f"Errors: {len(result.errors)}")

        for error in result.errors:
            print(
                f"- {error.field}: "
                f"{error.message}"
            )


if __name__ == "__main__":
    main()