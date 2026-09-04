from pathlib import Path

from src.ingestion.json_reader import read_json
from src.ingestion.parser import parse_match
from src.validation.match_validator import validate_match


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "cricsheet"/"ipl_json"


def test_real_match_is_valid() -> None:
    """The sample Cricsheet match should pass validation."""

    json_files = sorted(DATA_DIR.glob("*.json"))

    assert json_files, "No Cricsheet JSON files found."

    file_path = json_files[0]

    data = read_json(file_path)

    match = parse_match(
        data=data,
        match_id=int(file_path.stem),
    )

    result = validate_match(match)

    assert result.is_valid, [
        f"{error.field}: {error.message}"
        for error in result.errors
    ]