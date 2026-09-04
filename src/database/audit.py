from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session


def start_etl_run(
    session: Session,
    files_discovered: int,
) -> int:
    """
    Create a new ETL run record.

    Returns:
        run_id
    """

    result = session.execute(
        text(
            """
            INSERT INTO etl_run (
                status,
                files_discovered
            )
            VALUES (
                :status,
                :files_discovered
            )
            RETURNING run_id
            """
        ),
        {
            "status": "RUNNING",
            "files_discovered": files_discovered,
        },
    )

    run_id = result.scalar_one()

    session.commit()

    return run_id


def start_file_log(
    session: Session,
    run_id: int,
    file_name: str,
    match_id: int | None,
) -> int:
    """
    Create an audit record for one file.

    Returns:
        file_log_id
    """

    result = session.execute(
        text(
            """
            INSERT INTO etl_file_log (
                run_id,
                file_name,
                match_id,
                status,
                stage
            )
            VALUES (
                :run_id,
                :file_name,
                :match_id,
                :status,
                :stage
            )
            RETURNING file_log_id
            """
        ),
        {
            "run_id": run_id,
            "file_name": file_name,
            "match_id": match_id,
            "status": "PROCESSING",
            "stage": "START",
        },
    )

    file_log_id = result.scalar_one()

    session.commit()

    return file_log_id


def update_file_success(
    session: Session,
    file_log_id: int,
    duration_seconds: float,
) -> None:
    """Mark a file as successfully processed."""

    session.execute(
        text(
            """
            UPDATE etl_file_log
            SET
                status = :status,
                stage = :stage,
                finished_at = :finished_at,
                duration_seconds = :duration_seconds
            WHERE file_log_id = :file_log_id
            """
        ),
        {
            "status": "SUCCESS",
            "stage": "COMPLETE",
            "finished_at": datetime.now(timezone.utc),
            "duration_seconds": duration_seconds,
            "file_log_id": file_log_id,
        },
    )

    session.commit()


def update_file_failure(
    session: Session,
    file_log_id: int,
    stage: str,
    error_message: str,
    duration_seconds: float,
) -> None:
    """Mark a file as failed."""

    session.execute(
        text(
            """
            UPDATE etl_file_log
            SET
                status = :status,
                stage = :stage,
                error_message = :error_message,
                finished_at = :finished_at,
                duration_seconds = :duration_seconds
            WHERE file_log_id = :file_log_id
            """
        ),
        {
            "status": "FAILED",
            "stage": stage,
            "error_message": error_message,
            "finished_at": datetime.now(timezone.utc),
            "duration_seconds": duration_seconds,
            "file_log_id": file_log_id,
        },
    )

    session.commit()


def finish_etl_run(
    session: Session,
    run_id: int,
    files_processed: int,
    files_succeeded: int,
    files_failed: int,
) -> None:
    """Complete the ETL run."""

    if files_failed == 0:
        status = "SUCCESS"
    elif files_succeeded > 0:
        status = "PARTIAL"
    else:
        status = "FAILED"

    session.execute(
        text(
            """
            UPDATE etl_run
            SET
                status = :status,
                finished_at = :finished_at,
                files_processed = :files_processed,
                files_succeeded = :files_succeeded,
                files_failed = :files_failed
            WHERE run_id = :run_id
            """
        ),
        {
            "status": status,
            "finished_at": datetime.now(timezone.utc),
            "files_processed": files_processed,
            "files_succeeded": files_succeeded,
            "files_failed": files_failed,
            "run_id": run_id,
        },
    )

    session.commit()
    
def record_file_quality_issue(
    session: Session,
    file_log_id: int,
    rule_id: str,
    field: str,
    message: str,
    severity: str,
) -> None:
    """Persist one data-quality issue for a processed file."""

    session.execute(
        text(
            """
            INSERT INTO etl_file_quality_issue (
                file_log_id,
                rule_id,
                field,
                message,
                severity
            )
            VALUES (
                :file_log_id,
                :rule_id,
                :field,
                :message,
                :severity
            )
            """
        ),
        {
            "file_log_id": file_log_id,
            "rule_id": rule_id,
            "field": field,
            "message": message,
            "severity": severity,
        },
    )

    session.commit()