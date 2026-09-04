from src.validation.models import (
    DataQualityResult,
    Severity,
)


def test_empty_result_is_valid():

    result = DataQualityResult()

    assert result.is_valid
    assert result.errors == []
    assert result.warnings == []


def test_error_makes_result_invalid():

    result = DataQualityResult()

    result.add_error(
        rule_id="DQ001",
        field="match_id",
        message="Match ID is invalid.",
    )

    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.errors[0].severity == Severity.ERROR


def test_warning_does_not_make_result_invalid():

    result = DataQualityResult()

    result.add_warning(
        rule_id="DQ011",
        field="player_of_match",
        message="Player of match is missing.",
    )

    assert result.is_valid
    assert len(result.errors) == 0
    assert len(result.warnings) == 1
    assert result.warnings[0].severity == Severity.WARNING