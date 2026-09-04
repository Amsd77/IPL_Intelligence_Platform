from pathlib import Path

import pytest

from src.ingestion.json_reader import (
    JsonReaderError,
    read_json,
)


def test_read_json_success(tmp_path: Path) -> None:
    """Reader should return a dictionary for valid JSON."""

    json_file = tmp_path / "match.json"

    json_file.write_text(
        '{"info": {"season": 2024}, "innings": []}',
        encoding="utf-8",
    )

    data = read_json(json_file)

    assert isinstance(data, dict)
    assert data["info"]["season"] == 2024


def test_read_json_missing_file() -> None:
    """Reader should raise an application-level error for missing files."""

    file_path = Path("does_not_exist.json")

    with pytest.raises(JsonReaderError):
        read_json(file_path)


def test_read_json_invalid_json(tmp_path: Path) -> None:
    """Reader should reject malformed JSON."""

    json_file = tmp_path / "invalid.json"

    json_file.write_text(
        '{"info": ',
        encoding="utf-8",
    )

    with pytest.raises(JsonReaderError):
        read_json(json_file)


def test_read_json_root_must_be_dictionary(tmp_path: Path) -> None:
    """Reader should reject a JSON array at the root."""

    json_file = tmp_path / "array.json"

    json_file.write_text(
        '["IPL", "Cricket"]',
        encoding="utf-8",
    )

    with pytest.raises(JsonReaderError):
        read_json(json_file)