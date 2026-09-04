from sqlalchemy.orm import Session

from src.database.connection import engine
from src.database.audit import (
    start_etl_run,
    start_file_log,
    record_file_quality_issue,
)


def main() -> None:

    print("=" * 60)
    print("DQ ERROR PERSISTENCE TEST")
    print("=" * 60)

    with Session(engine) as session:

        run_id = start_etl_run(
            session=session,
            files_discovered=1,
        )

        file_log_id = start_file_log(
            session=session,
            run_id=run_id,
            file_name="TEST_DQ_ERROR.json",
            match_id=None,
        )

        record_file_quality_issue(
            session=session,
            file_log_id=file_log_id,
            rule_id="TEST_DQ001",
            field="winner",
            message="Test DQ error persistence.",
            severity="ERROR",
        )

        print(f"Run ID      : {run_id}")
        print(f"File Log ID : {file_log_id}")
        print("Severity    : ERROR")
        print("Result      : PERSISTED")


if __name__ == "__main__":
    main()