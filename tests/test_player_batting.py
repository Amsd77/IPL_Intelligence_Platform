import pytest

from src.analytics.player_batting import get_top_batters


def test_top_batters_rejects_invalid_limit():
    with pytest.raises(ValueError):
        get_top_batters(None, limit=0)


def test_top_batters_rejects_negative_limit():
    with pytest.raises(ValueError):
        get_top_batters(None, limit=-1)