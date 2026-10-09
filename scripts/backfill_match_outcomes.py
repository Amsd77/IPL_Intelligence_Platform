from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.connection import engine
from src.database.models import Match, Team
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


def backfill_match_outcomes() -> None:
    json_files = sorted(DATA_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in: {DATA_DIR}"
        )

    updated = 0
    unchanged = 0
    missing = 0

    with Session(engine) as session:

        # ---------------------------------------------
        # Build team lookup
        # ---------------------------------------------

        teams = session.scalars(
            select(Team)
        ).all()

        team_map = {
            team.team_name: team.team_id
            for team in teams
        }

        # ---------------------------------------------
        # Process source files
        # ---------------------------------------------

        for file_path in json_files:

            match_id = int(file_path.stem)

            data = read_json(file_path)

            match = parse_match(
                data=data,
                match_id=match_id,
            )

            db_match = session.get(
                Match,
                match_id,
            )

            if db_match is None:
                missing += 1

                print(
                    f"SKIPPED: Match {match_id} "
                    f"does not exist in dim_match"
                )

                continue

            deciding_team_id = None

            if match.outcome_deciding_team is not None:

                deciding_team_id = team_map.get(
                    match.outcome_deciding_team
                )

                if deciding_team_id is None:
                    raise ValueError(
                        "Outcome deciding team not found "
                        f"in dim_team: "
                        f"{match.outcome_deciding_team} "
                        f"(match {match_id})"
                    )

            old_values = (
                db_match.outcome_result,
                db_match.outcome_deciding_team_id,
            )

            new_values = (
                match.outcome_result,
                deciding_team_id,
            )

            if old_values == new_values:
                unchanged += 1
                continue

            db_match.outcome_result = (
                match.outcome_result
            )

            db_match.outcome_deciding_team_id = (
                deciding_team_id
            )

            updated += 1

        # ---------------------------------------------
        # Commit
        # ---------------------------------------------

        session.commit()

    print()
    print("=" * 60)
    print("MATCH OUTCOME BACKFILL COMPLETE")
    print("=" * 60)
    print(f"Source files : {len(json_files)}")
    print(f"Updated      : {updated}")
    print(f"Unchanged    : {unchanged}")
    print(f"Missing DB   : {missing}")
    print("=" * 60)


if __name__ == "__main__":
    backfill_match_outcomes()