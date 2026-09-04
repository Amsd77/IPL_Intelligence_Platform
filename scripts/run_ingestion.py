from pathlib import Path
from time import perf_counter

from sqlalchemy.orm import Session

from src.database.audit import (
    start_etl_run,
    start_file_log,
    record_file_quality_issue,
    update_file_success,
    update_file_failure,
    finish_etl_run,
)

from src.validation.data_quality import run_data_quality_checks
from src.database.connection import engine

from src.ingestion.json_reader import read_json
from src.ingestion.parser import parse_match
from src.validation.match_validator import validate_match
from src.transformation.transformer import transform_match
from src.database.loader import load_match


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cricsheet"
    /"ipl_json"
)


def process_file(
    file_path: Path,
    session: Session,
    run_id: int,
) -> None:
    """Process and audit one source file."""

    print("-" * 60)
    print(f"Processing: {file_path.name}")

    started = perf_counter()

    match_id = int(file_path.stem)

    file_log_id = start_file_log(
        session=session,
        run_id=run_id,
        file_name=file_path.name,
        match_id=match_id,
    )

    current_stage = "READ"

    try:

        # ---------------------------------------------
        # READ
        # ---------------------------------------------

        current_stage = "READ"

        data = read_json(file_path)

        # ---------------------------------------------
        # PARSE
        # ---------------------------------------------

        current_stage = "PARSE"

        match = parse_match(
            data=data,
            match_id=match_id,
        )

        # ---------------------------------------------
        # VALIDATE
        # ---------------------------------------------

        current_stage = "VALIDATE"

        validation_result = validate_match(match)

        if not validation_result.is_valid:

            raise ValueError(
                "Validation failed: "
                + str(
                    validation_result.errors
                )
            )
            
        # ---------------------------------------------
        # DATA QUALITY
        # ---------------------------------------------

        current_stage = "DATA_QUALITY"

        quality_result = run_data_quality_checks(match)

        if not quality_result.is_valid:

            error_messages = []

            for issue in quality_result.errors:

                record_file_quality_issue(
                    session=session,
                    file_log_id=file_log_id,
                    rule_id=issue.rule_id,
                    field=issue.field,
                    message=issue.message,
                    severity=issue.severity.value,
                )

                error_messages.append(
                    f"{issue.rule_id}: "
                    f"{issue.field}: "
                    f"{issue.message}"
                )

            error_message = " | ".join(error_messages)

            print(
                f"DATA QUALITY FAILED: {file_path.name}"
            )

            print(
                f"Errors: {error_message}"
            )

            raise ValueError(
                "Data quality failed: "
                + error_message
            )
        # Warnings do not block ingestion

        if quality_result.warnings:

            print(
                f"DATA QUALITY WARNINGS: {file_path.name}"
            )

            for issue in quality_result.warnings:

                record_file_quality_issue(
                    session=session,
                    file_log_id=file_log_id,
                    rule_id=issue.rule_id,
                    field=issue.field,
                    message=issue.message,
                    severity=issue.severity.value,
                )

                print(
                    f"  WARNING: "
                    f"{issue.rule_id}: "
                    f"{issue.field}: "
                    f"{issue.message}"
                )
                
        # ---------------------------------------------
        # TRANSFORM
        # ---------------------------------------------

        current_stage = "TRANSFORM"

        package = transform_match(match)

        # ---------------------------------------------
        # LOAD
        # ---------------------------------------------

        current_stage = "LOAD"

        load_match(package)

        # ---------------------------------------------
        # SUCCESS
        # ---------------------------------------------

        duration = (
            perf_counter() - started
        )

        update_file_success(
            session=session,
            file_log_id=file_log_id,
            duration_seconds=duration,
        )

        print(
            f"SUCCESS: {file_path.name}"
        )

    except Exception as exc:

        duration = (
            perf_counter() - started
        )

        update_file_failure(
            session=session,
            file_log_id=file_log_id,
            stage=current_stage,
            error_message=str(exc),
            duration_seconds=duration,
        )

        print(
            f"FAILED: {file_path.name}"
        )

        print(
            f"Stage : {current_stage}"
        )

        print(
            f"Reason: {exc}"
        )

        raise


def main() -> None:

    print("=" * 60)
    print("IPL INTELLIGENCE INGESTION PIPELINE")
    print("=" * 60)

    files = sorted(
        DATA_DIR.glob("*.json")
    )

    if not files:

        raise RuntimeError(
            f"No JSON files found in {DATA_DIR}"
        )

    batch = files

    print(
        f"Files discovered : {len(files)}"
    )

    print(
        f"Files processing  : {len(batch)}"
    )

    success_count = 0
    failure_count = 0

    # ---------------------------------------------
    # Create ETL run
    # ---------------------------------------------

    with Session(engine) as session:

        run_id = start_etl_run(
            session=session,
            files_discovered=len(files),
        )

        print(
            f"ETL Run ID       : {run_id}"
        )

        # -----------------------------------------
        # Process files
        # -----------------------------------------

        for file_path in batch:

            try:

                process_file(
                    file_path=file_path,
                    session=session,
                    run_id=run_id,
                )

                success_count += 1

            except Exception:

                failure_count += 1

        # -----------------------------------------
        # Finish ETL run
        # -----------------------------------------

        finish_etl_run(
            session=session,
            run_id=run_id,
            files_processed=len(batch),
            files_succeeded=success_count,
            files_failed=failure_count,
        )

    # ---------------------------------------------
    # Summary
    # ---------------------------------------------

    print("=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)

    print(
        f"Run ID     : {run_id}"
    )

    print(
        f"Discovered : {len(files)}"
    )

    print(
        f"Processed  : {len(batch)}"
    )

    print(
        f"Successful : {success_count}"
    )

    print(
        f"Failed     : {failure_count}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()