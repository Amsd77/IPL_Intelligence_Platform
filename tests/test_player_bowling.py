import pytest

from src.analytics.player_bowling import (
    get_player_bowling_stats,
    get_top_bowlers,
)


def test_get_top_bowlers_rejects_invalid_limit():
    with pytest.raises(ValueError):
        get_top_bowlers(None, 0)


def test_get_top_bowlers_rejects_negative_limit():
    with pytest.raises(ValueError):
        get_top_bowlers(None, -1)


def test_bowling_stats_function_exists():
    assert callable(get_player_bowling_stats)


def test_top_bowlers_function_exists():
    assert callable(get_top_bowlers)