from unittest.mock import MagicMock

import pytest

from src.analytics.team_head_to_head import (
    get_team_head_to_head,
    get_team_head_to_head_by_season,
)


def test_get_team_head_to_head_returns_result():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.first.return_value = {
        "team_a_id": 9,
        "team_a_name": "Chennai Super Kings",
        "team_b_id": 4,
        "team_b_name": "Mumbai Indians",
        "matches": 41,
        "team_a_wins": 16,
        "team_b_wins": 20,
        "ties": 1,
        "no_results": 4,
    }

    session.execute.return_value.mappings.return_value = mock_result

    result = get_team_head_to_head(
        session,
        9,
        4,
    )

    assert result is not None
    assert result["team_a_id"] == 9
    assert result["team_b_id"] == 4
    assert result["team_a_name"] == "Chennai Super Kings"
    assert result["team_b_name"] == "Mumbai Indians"
    assert result["matches"] == 41
    assert result["team_a_wins"] == 16
    assert result["team_b_wins"] == 20
    assert result["ties"] == 1
    assert result["no_results"] == 4


def test_get_team_head_to_head_returns_none_for_unknown_pair():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.first.return_value = None

    session.execute.return_value.mappings.return_value = mock_result

    result = get_team_head_to_head(
        session,
        9,
        999999,
    )

    assert result is None


@pytest.mark.parametrize(
    "team_a_id, team_b_id",
    [
        (0, 4),
        (-1, 4),
        (9, 0),
        (9, -1),
    ],
)
def test_get_team_head_to_head_rejects_invalid_team_ids(
    team_a_id,
    team_b_id,
):
    session = MagicMock()

    with pytest.raises(
        ValueError,
        match="must be greater than zero",
    ):
        get_team_head_to_head(
            session,
            team_a_id,
            team_b_id,
        )

    session.execute.assert_not_called()


def test_get_team_head_to_head_rejects_same_team():
    session = MagicMock()

    with pytest.raises(
        ValueError,
        match="must be different",
    ):
        get_team_head_to_head(
            session,
            9,
            9,
        )

    session.execute.assert_not_called()


def test_get_team_head_to_head_by_season_returns_rows():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.mappings.return_value = [
        {
            "season": "2024",
            "matches": 2,
            "team_a_wins": 1,
            "team_b_wins": 1,
            "ties": 0,
            "no_results": 0,
        },
        {
            "season": "2025",
            "matches": 2,
            "team_a_wins": 2,
            "team_b_wins": 0,
            "ties": 0,
            "no_results": 0,
        },
    ]

    session.execute.return_value = mock_result

    result = get_team_head_to_head_by_season(
        session,
        9,
        4,
    )

    assert len(result) == 2

    assert result[0]["season"] == "2024"
    assert result[0]["matches"] == 2
    assert result[0]["team_a_wins"] == 1
    assert result[0]["team_b_wins"] == 1

    assert result[1]["season"] == "2025"
    assert result[1]["matches"] == 2
    assert result[1]["team_a_wins"] == 2
    assert result[1]["team_b_wins"] == 0


def test_get_team_head_to_head_by_season_returns_empty_list():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.mappings.return_value = []

    session.execute.return_value = mock_result

    result = get_team_head_to_head_by_season(
        session,
        9,
        999999,
    )

    assert result == []


def test_get_team_head_to_head_by_season_rejects_same_team():
    session = MagicMock()

    with pytest.raises(
        ValueError,
        match="must be different",
    ):
        get_team_head_to_head_by_season(
            session,
            9,
            9,
        )

    session.execute.assert_not_called()