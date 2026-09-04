from pathlib import Path

from src.ingestion.json_reader import read_json
from src.ingestion.parser import parse_match
from src.validation.match_validator import validate_match
from src.transformation.transformer import transform_match
from src.database.loader import load_match


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "cricsheet"/"ipl_json"


def main() -> None:
    json_files = sorted(DATA_DIR.glob("*.json"))

    if not json_files:
        raise RuntimeError(
            f"No JSON files found in {DATA_DIR}"
        )

    file_path = json_files[0]

    print("=" * 60)
    print("IPL INTELLIGENCE - DATABASE LOAD")
    print("=" * 60)

    print(f"Source file : {file_path.name}")

    # --------------------------------------------------
    # 1. Read JSON
    # --------------------------------------------------

    data = read_json(file_path)

    print("JSON reader : OK")

    # --------------------------------------------------
    # 2. Parse
    # --------------------------------------------------

    match = parse_match(
        data=data,
        match_id=int(file_path.stem),
    )

    print("Parser      : OK")

    # --------------------------------------------------
    # 3. Validate
    # --------------------------------------------------

    validation_result = validate_match(match)

    if not validation_result.is_valid:

        print("\nVALIDATION FAILED")

        for error in validation_result.errors:
            print(
                f"- {error.field}: "
                f"{error.message}"
            )

        raise RuntimeError(
            "Match failed validation."
        )

    print("Validator   : OK")

    # --------------------------------------------------
    # 4. Transform
    # --------------------------------------------------

    package = transform_match(match)

    print("Transformer : OK")

    # --------------------------------------------------
    # 5. Load
    # --------------------------------------------------

    load_match(package)

    print("=" * 60)
    print("DATABASE LOAD COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()