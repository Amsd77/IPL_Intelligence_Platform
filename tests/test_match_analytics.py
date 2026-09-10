from unittest.mock import MagicMock

import pytest

from src.analytics.match_analytics import get_match_summary


def test_get_match_summary_returns_match():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.first.return_value = {
        "match_id": 335982,
        "season": "2007/08",
        "match_date": "2008-04-18",
        "city": "Bangalore",
        "match_type": "T20",
        "gender": "male",
        "toss_decision": "field",
        "player_of_match": "BB McCullum",
        "toss_winner": "Royal Challengers Bangalore",
        "winner": "Kolkata Knight Riders",
        "teams": "Kolkata Knight Riders vs Royal Challengers Bangalore",
    }

    mock_mappings = MagicMock()
    mock_mappings.first.return_value = mock_result.first.return_value
    session.execute.return_value.mappings.return_value = mock_mappings

    result = get_match_summary(session, 335982)

    assert result is not None
    assert result["match_id"] == 335982
    assert result["season"] == "2007/08"
    assert result["winner"] == "Kolkata Knight Riders"
    assert result["toss_winner"] == "Royal Challengers Bangalore"
    assert result["teams"] == (
        "Kolkata Knight Riders vs Royal Challengers Bangalore"
    )


def test_get_match_summary_returns_none_for_unknown_match():
    session = MagicMock()

    mock_mappings = MagicMock()
    mock_mappings.first.return_value = None

    session.execute.return_value.mappings.return_value = mock_mappings

    result = get_match_summary(session, 999999999)

    assert result is None


@pytest.mark.parametrize("match_id", [0, -1, -100])
def test_get_match_summary_rejects_invalid_match_id(match_id):
    session = MagicMock()

    with pytest.raises(ValueError, match="match_id must be greater than zero"):
        get_match_summary(session, match_id)

    session.execute.assert_not_called()