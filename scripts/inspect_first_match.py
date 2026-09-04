from pathlib import Path
import json
from pprint import pprint


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "cricsheet"/"ipl_json"


def main() -> None:
    json_files = sorted(DATA_DIR.glob("*.json"))

    if not json_files:
        raise RuntimeError(
            f"No JSON files found in {DATA_DIR}"
        )

    file_path = json_files[0]

    print("=" * 70)
    print("CRICSHEET SOURCE STRUCTURE INSPECTION")
    print("=" * 70)

    print(f"File: {file_path.name}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    print("\nTop-level keys:")
    print(list(data.keys()))

    print("\nMETA:")
    pprint(data.get("meta"))

    print("\nINFO keys:")
    info = data.get("info", {})
    print(list(info.keys()))

    print("\nINFO:")
    pprint(info)

    print("\nINGREDIENTS / INNINGS:")
    innings = data.get("innings", [])
    print(f"Number of innings: {len(innings)}")

    if innings:
        print("\nFirst innings structure:")
        pprint(innings[0])


if __name__ == "__main__":
    main()