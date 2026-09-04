from src.database.audit import (
    start_etl_run,
    start_file_log,
    update_file_success,
    finish_etl_run,
)

from src.database.connection import engine

from sqlalchemy.orm import Session


def main() -> None:

    print("=" * 60)
    print("ETL AUDIT TEST")
    print("=" * 60)

    with Session(engine) as session:

        # ------------------------------------------
        # Start run
        # ------------------------------------------

        run_id = start_etl_run(
            session,
            files_discovered=5,
        )

        print(
            f"ETL run created: {run_id}"
        )

        # ------------------------------------------
        # Start file
        # ------------------------------------------

        file_log_id = start_file_log(
            session,
            run_id=run_id,
            file_name="audit_test.json",
            match_id=999999,
        )

        print(
            f"File log created: {file_log_id}"
        )

        # ------------------------------------------
        # Mark success
        # ------------------------------------------

        update_file_success(
            session,
            file_log_id=file_log_id,
            duration_seconds=1.234,
        )

        print(
            "File marked SUCCESS"
        )

        # ------------------------------------------
        # Finish run
        # ------------------------------------------

        finish_etl_run(
            session,
            run_id=run_id,
            files_processed=1,
            files_succeeded=1,
            files_failed=0,
        )

        print(
            "ETL run marked SUCCESS"
        )

    print("=" * 60)
    print("AUDIT TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()