from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cricsheet"
    / "ipl_json"
)


def main() -> None:

    print("=" * 60)
    print("CRICSHEET SOURCE INTEGRITY CHECK")
    print("=" * 60)

    files = sorted(DATA_DIR.glob("*.json"))

    print(f"JSON files found : {len(files)}")

    # ---------------------------------------------------------
    # Check numeric IDs
    # ---------------------------------------------------------

    non_numeric = [
        file.name
        for file in files
        if not file.stem.isdigit()
    ]

    print(
        f"Non-numeric IDs  : {len(non_numeric)}"
    )

    if non_numeric:
        for file_name in non_numeric[:10]:
            print(f"  {file_name}")

    # ---------------------------------------------------------
    # Check duplicate IDs
    # ---------------------------------------------------------

    match_ids = [
        int(file.stem)
        for file in files
        if file.stem.isdigit()
    ]

    unique_ids = set(match_ids)

    duplicate_ids = [
        match_id
        for match_id in unique_ids
        if match_ids.count(match_id) > 1
    ]

    print(
        f"Unique match IDs  : {len(unique_ids)}"
    )

    print(
        f"Duplicate IDs     : {len(duplicate_ids)}"
    )

    if duplicate_ids:
        for match_id in duplicate_ids[:10]:
            print(f"  {match_id}")

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    integrity_ok = (
        len(files) == len(unique_ids)
        and not non_numeric
        and not duplicate_ids
    )

    print("-" * 60)

    if integrity_ok:
        print("SOURCE INTEGRITY : PASS")
    else:
        print("SOURCE INTEGRITY : FAIL")

    print("=" * 60)


if __name__ == "__main__":
    main()