from pathlib import Path

from sqlalchemy.orm import Session

from src.database.connection import engine
from src.database.audit import start_etl_run
from scripts.run_ingestion import process_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TEST_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cricsheet"
    / "ipl_json"
    / "729281.json"
)


def main() -> None:

    print("=" * 60)
    print("DQ PERSISTENCE TEST")
    print("=" * 60)

    if not TEST_FILE.exists():
        raise FileNotFoundError(
            f"Test file not found: {TEST_FILE}"
        )

    with Session(engine) as session:

        run_id = start_etl_run(
            session=session,
            files_discovered=1,
        )

        print(f"Test ETL Run ID : {run_id}")

        try:

            process_file(
                file_path=TEST_FILE,
                session=session,
                run_id=run_id,
            )

        except Exception as exc:

            print(f"Unexpected failure: {exc}")

            raise

    print("=" * 60)
    print("DQ PERSISTENCE TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()