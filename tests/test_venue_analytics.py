from unittest.mock import MagicMock

import pytest

from src.analytics.venue_analytics import (
    get_top_venues,
    get_venue_stats,
)


def test_get_venue_stats_returns_venue():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.first.return_value = {
        "venue_id": 7,
        "venue_name": "Eden Gardens",
        "city": "Kolkata",
        "matches": 77,
        "innings": 154,
        "total_runs": 23658,
        "average_runs_per_innings": 153.62,
        "highest_innings_score": 232,
        "average_run_rate": 8.16,
        "total_wickets": 878,
        "average_wickets_per_innings": 5.70,
    }

    session.execute.return_value.mappings.return_value = mock_result

    result = get_venue_stats(session, 7)

    assert result is not None
    assert result["venue_id"] == 7
    assert result["venue_name"] == "Eden Gardens"
    assert result["city"] == "Kolkata"
    assert result["matches"] == 77
    assert result["innings"] == 154
    assert result["total_runs"] == 23658
    assert result["highest_innings_score"] == 232


def test_get_venue_stats_returns_none_for_unknown_venue():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.first.return_value = None

    session.execute.return_value.mappings.return_value = mock_result

    result = get_venue_stats(session, 999999999)

    assert result is None


@pytest.mark.parametrize("venue_id", [0, -1, -100])
def test_get_venue_stats_rejects_invalid_venue_id(venue_id):
    session = MagicMock()

    with pytest.raises(
        ValueError,
        match="venue_id must be greater than zero",
    ):
        get_venue_stats(session, venue_id)

    session.execute.assert_not_called()


def test_get_top_venues_returns_rows():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.mappings.return_value = [
        {
            "venue_id": 7,
            "venue_name": "Eden Gardens",
            "city": "Kolkata",
            "matches": 77,
            "innings": 154,
            "total_runs": 23658,
            "average_runs_per_innings": 153.62,
            "highest_innings_score": 232,
            "average_run_rate": 8.16,
            "total_wickets": 878,
            "average_wickets_per_innings": 5.70,
        },
        {
            "venue_id": 6,
            "venue_name": "Wankhede Stadium",
            "city": "Mumbai",
            "matches": 73,
            "innings": 148,
            "total_runs": 23407,
            "average_runs_per_innings": 158.16,
            "highest_innings_score": 235,
            "average_run_rate": 8.41,
            "total_wickets": 891,
            "average_wickets_per_innings": 6.02,
        },
    ]

    session.execute.return_value = mock_result

    result = get_top_venues(session, 2)

    assert len(result) == 2
    assert result[0]["venue_id"] == 7
    assert result[0]["venue_name"] == "Eden Gardens"
    assert result[0]["total_runs"] == 23658
    assert result[1]["venue_id"] == 6
    assert result[1]["total_runs"] == 23407


def test_get_top_venues_rejects_invalid_limit():
    session = MagicMock()

    with pytest.raises(
        ValueError,
        match="limit must be greater than zero",
    ):
        get_top_venues(session, 0)

    session.execute.assert_not_called()


@pytest.mark.parametrize("limit", [-1, -10])
def test_get_top_venues_rejects_negative_limit(limit):
    session = MagicMock()

    with pytest.raises(
        ValueError,
        match="limit must be greater than zero",
    ):
        get_top_venues(session, limit)

    session.execute.assert_not_called()