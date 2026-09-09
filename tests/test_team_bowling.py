import pytest

from src.analytics.team_bowling import (
    get_team_bowling_stats,
    get_top_bowling_teams,
)


def test_get_team_bowling_stats_requires_session():
    with pytest.raises(AttributeError):
        get_team_bowling_stats(None)


def test_get_top_bowling_teams_rejects_invalid_limit():
    with pytest.raises(ValueError):
        get_top_bowling_teams(None, 0)


def test_get_top_bowling_teams_rejects_negative_limit():
    with pytest.raises(ValueError):
        get_top_bowling_teams(None, -1)