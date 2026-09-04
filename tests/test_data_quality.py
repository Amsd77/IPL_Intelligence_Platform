from pathlib import Path

from src.ingestion.json_reader import read_json
from src.ingestion.parser import parse_match
from src.validation.data_quality import (
    run_data_quality_checks,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cricsheet"
    /"ipl_json"
    / "1082591.json"
)


def load_real_match():
    data = read_json(SOURCE_FILE)

    return parse_match(
        data=data,
        match_id=1082591,
    )


def test_real_match_passes_data_quality():

    match = load_real_match()

    result = run_data_quality_checks(match)

    assert result.is_valid


def test_real_match_has_no_errors():

    match = load_real_match()

    result = run_data_quality_checks(match)

    assert result.errors == []