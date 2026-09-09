from unittest.mock import MagicMock

import pytest

from src.analytics.team_batting import (
    get_team_batting_stats,
    get_top_batting_teams,
)


def test_get_team_batting_stats():
    session = MagicMock()

    session.execute.return_value.mappings.return_value = [
        {
            "team_id": 4,
            "team_name": "Mumbai Indians",
            "matches": 291,
            "innings": 296,
            "runs": 45203,
            "balls_faced": 33803,
            "wickets_lost": 1690,
            "batting_average": 26.75,
            "strike_rate": 133.72,
            "average_score": 152.71,
        }
    ]

    result = get_team_batting_stats(session)

    assert len(result) == 1
    assert result[0]["team_name"] == "Mumbai Indians"
    assert result[0]["runs"] == 45203
    assert result[0]["innings"] == 296


def test_get_top_batting_teams():
    session = MagicMock()

    session.execute.return_value.mappings.return_value = [
        {
            "team_id": 4,
            "team_name": "Mumbai Indians",
            "matches": 291,
            "innings": 296,
            "runs": 45203,
            "balls_faced": 33803,
            "wickets_lost": 1690,
            "batting_average": 26.75,
            "strike_rate": 133.72,
            "average_score": 152.71,
        },
        {
            "team_id": 9,
            "team_name": "Chennai Super Kings",
            "matches": 265,
            "innings": 266,
            "runs": 41444,
            "balls_faced": 31049,
            "wickets_lost": 1368,
            "batting_average": 30.29,
            "strike_rate": 133.48,
            "average_score": 155.80,
        },
    ]

    result = get_top_batting_teams(session, 1)

    assert len(result) == 1
    assert result[0]["team_name"] == "Mumbai Indians"


def test_get_top_batting_teams_rejects_invalid_limit():
    session = MagicMock()

    with pytest.raises(ValueError):
        get_top_batting_teams(session, 0)