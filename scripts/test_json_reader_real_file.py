from pathlib import Path

from src.ingestion.json_reader import read_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "cricsheet"/"ipl_json"


def main() -> None:
    """Read one real Cricsheet match file."""

    json_files = sorted(DATA_DIR.glob("*.json"))

    if not json_files:
        raise RuntimeError(
            f"No JSON files found in {DATA_DIR}"
        )

    file_path = json_files[0]

    match = read_json(file_path)

    print("=" * 60)
    print("REAL CRICSHEET JSON TEST")
    print("=" * 60)

    print(f"File: {file_path.name}")
    print(f"Root type: {type(match).__name__}")
    print(f"Top-level keys: {list(match.keys())}")

    print("\nInfo keys:")
    print(list(match.get("info", {}).keys()))

    print("\nNumber of innings:")
    print(len(match.get("innings", [])))


if __name__ == "__main__":
    main()