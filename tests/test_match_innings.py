from unittest.mock import MagicMock

import pytest

from src.analytics.match_innings import get_match_innings_stats


def test_get_match_innings_stats_returns_rows():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.mappings.return_value = [
        {
            "innings_id": 1353,
            "match_id": 335982,
            "innings_number": 1,
            "batting_team_id": 6,
            "batting_team": "Kolkata Knight Riders",
            "runs": 222,
            "wickets_lost": 3,
            "deliveries": 124,
            "legal_deliveries": 120,
            "run_rate": 11.10,
        }
    ]

    session.execute.return_value = mock_result

    result = get_match_innings_stats(session, 335982)

    assert len(result) == 1
    assert result[0]["match_id"] == 335982
    assert result[0]["batting_team"] == "Kolkata Knight Riders"
    assert result[0]["runs"] == 222
    assert result[0]["wickets_lost"] == 3
    assert result[0]["legal_deliveries"] == 120


def test_get_match_innings_stats_returns_empty_list_for_unknown_match():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.mappings.return_value = []

    session.execute.return_value = mock_result

    result = get_match_innings_stats(session, 999999999)

    assert result == []


@pytest.mark.parametrize("match_id", [0, -1, -100])
def test_get_match_innings_stats_rejects_invalid_match_id(match_id):
    session = MagicMock()

    with pytest.raises(ValueError, match="match_id must be greater than zero"):
        get_match_innings_stats(session, match_id)

    session.execute.assert_not_called()