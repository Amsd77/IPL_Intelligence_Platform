from pathlib import Path

from src.ingestion.json_reader import read_json
from src.ingestion.parser import parse_match
from src.validation.match_validator import validate_match
from src.transformation.transformer import transform_match


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "cricsheet"/"ipl_json"


def test_transform_real_match() -> None:
    """A validated match should transform successfully."""

    json_files = sorted(DATA_DIR.glob("*.json"))

    assert json_files, "No Cricsheet JSON files found."

    file_path = json_files[0]

    data = read_json(file_path)

    match = parse_match(
        data=data,
        match_id=int(file_path.stem),
    )

    validation_result = validate_match(match)

    assert validation_result.is_valid

    transformed = transform_match(match)

    assert transformed.match.match_id == 1082591

    assert len(transformed.teams) == 2

    assert len(transformed.players) == 22

    assert transformed.venue is not None

    assert len(transformed.innings) == 2

    total_deliveries = sum(
        len(innings.deliveries)
        for innings in transformed.innings
    )

    assert total_deliveries == 248
    
def test_delivery_sequence_is_unique_within_innings() -> None:
    """Every delivery gets a unique internal sequence."""

    json_files = sorted(DATA_DIR.glob("*.json"))

    assert json_files

    file_path = json_files[0]

    data = read_json(file_path)

    match = parse_match(
        data=data,
        match_id=int(file_path.stem),
    )

    transformed = transform_match(match)

    for innings in transformed.innings:

        sequences = [
            delivery.delivery_sequence
            for delivery in innings.deliveries
        ]

        assert sequences == list(
            range(1, len(sequences) + 1)
        )