from collections import Counter, defaultdict
from pathlib import Path

from src.ingestion.json_reader import read_json
from src.ingestion.parser import parse_match
from src.validation.data_quality import run_data_quality_checks


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cricsheet"
    / "ipl_json"
)


def main() -> None:

    print("=" * 70)
    print("IPL DATA QUALITY WARNING ANALYSIS")
    print("=" * 70)

    files = sorted(DATA_DIR.glob("*.json"))

    print(f"Files discovered : {len(files)}")
    print()

    warning_rule_counts = Counter()
    warning_field_counts = Counter()

    affected_matches = defaultdict(list)

    total_warnings = 0
    matches_with_warnings = 0

    processing_errors = 0

    for index, file_path in enumerate(files, start=1):

        try:
            match_id = int(file_path.stem)

            data = read_json(file_path)

            match = parse_match(
                data=data,
                match_id=match_id,
            )

            quality_result = run_data_quality_checks(match)

            if quality_result.warnings:

                matches_with_warnings += 1

                for warning in quality_result.warnings:

                    total_warnings += 1

                    warning_rule_counts[
                        warning.rule_id
                    ] += 1

                    warning_field_counts[
                        warning.field
                    ] += 1

                    affected_matches[
                        warning.rule_id
                    ].append(match_id)

        except Exception as exc:

            processing_errors += 1

            print(
                f"ERROR processing {file_path.name}: {exc}"
            )

        if index % 100 == 0:
            print(
                f"Processed {index}/{len(files)} files..."
            )

    # ---------------------------------------------------------
    # Warning summary
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("WARNING SUMMARY")
    print("-" * 70)

    print(
        f"Total warnings          : {total_warnings:,}"
    )

    print(
        f"Matches with warnings   : {matches_with_warnings:,}"
    )

    print(
        f"Processing errors       : {processing_errors:,}"
    )

    # ---------------------------------------------------------
    # Rule counts
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("WARNINGS BY RULE")
    print("-" * 70)

    if warning_rule_counts:

        print(
            f"{'Rule ID':<15}"
            f"{'Count':>10}"
        )

        print("-" * 30)

        for rule_id, count in warning_rule_counts.most_common():

            print(
                f"{rule_id:<15}"
                f"{count:>10,}"
            )

    else:

        print("No warnings found.")

    # ---------------------------------------------------------
    # Field counts
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("WARNINGS BY FIELD")
    print("-" * 70)

    if warning_field_counts:

        print(
            f"{'Field':<25}"
            f"{'Count':>10}"
        )

        print("-" * 40)

        for field, count in warning_field_counts.most_common():

            print(
                f"{field:<25}"
                f"{count:>10,}"
            )

    # ---------------------------------------------------------
    # Affected matches
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("AFFECTED MATCHES")
    print("-" * 70)

    if affected_matches:

        for rule_id, match_ids in sorted(
            affected_matches.items()
        ):

            unique_match_ids = sorted(
                set(match_ids)
            )

            print()
            print(
                f"{rule_id} "
                f"({len(unique_match_ids)} matches)"
            )

            # Print only first 20 IDs to keep console manageable
            preview = unique_match_ids[:20]

            print(
                "  "
                + ", ".join(
                    str(match_id)
                    for match_id in preview
                )
            )

            if len(unique_match_ids) > 20:

                print(
                    f"  ... and "
                    f"{len(unique_match_ids) - 20} more"
                )

    print()
    print("=" * 70)
    print("DATA QUALITY ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()