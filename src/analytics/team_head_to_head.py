from sqlalchemy import text
from sqlalchemy.orm import Session


TEAM_HEAD_TO_HEAD_QUERY = text(
    """
    SELECT
        team_a.team_id AS team_a_id,
        team_a.team_name AS team_a_name,
        team_b.team_id AS team_b_id,
        team_b.team_name AS team_b_name,

        COUNT(*) AS matches,

        COUNT(*) FILTER (
            WHERE m.winner_id = team_a.team_id
        ) AS team_a_wins,

        COUNT(*) FILTER (
            WHERE m.winner_id = team_b.team_id
        ) AS team_b_wins,

        COUNT(*) FILTER (
            WHERE m.outcome_result = 'tie'
        ) AS ties,

        COUNT(*) FILTER (
            WHERE m.outcome_result = 'no result'
        ) AS no_results

    FROM dim_match m

    JOIN match_team mt_a
        ON mt_a.match_id = m.match_id
       AND mt_a.team_id = :team_a_id

    JOIN match_team mt_b
        ON mt_b.match_id = m.match_id
       AND mt_b.team_id = :team_b_id

    JOIN dim_team team_a
        ON team_a.team_id = :team_a_id

    JOIN dim_team team_b
        ON team_b.team_id = :team_b_id

    GROUP BY
        team_a.team_id,
        team_a.team_name,
        team_b.team_id,
        team_b.team_name
    """
)


TEAM_HEAD_TO_HEAD_BY_SEASON_QUERY = text(
    """
    SELECT
        m.season,

        COUNT(*) AS matches,

        COUNT(*) FILTER (
            WHERE m.winner_id = :team_a_id
        ) AS team_a_wins,

        COUNT(*) FILTER (
            WHERE m.winner_id = :team_b_id
        ) AS team_b_wins,

        COUNT(*) FILTER (
            WHERE m.outcome_result = 'tie'
        ) AS ties,

        COUNT(*) FILTER (
            WHERE m.outcome_result = 'no result'
        ) AS no_results

    FROM dim_match m

    JOIN match_team mt_a
        ON mt_a.match_id = m.match_id
       AND mt_a.team_id = :team_a_id

    JOIN match_team mt_b
        ON mt_b.match_id = m.match_id
       AND mt_b.team_id = :team_b_id

    GROUP BY
        m.season

    ORDER BY
        m.season
    """
)


def _validate_team_ids(
    team_a_id: int,
    team_b_id: int,
) -> None:
    """Validate the requested team IDs."""

    if team_a_id <= 0:
        raise ValueError(
            "team_a_id must be greater than zero"
        )

    if team_b_id <= 0:
        raise ValueError(
            "team_b_id must be greater than zero"
        )

    if team_a_id == team_b_id:
        raise ValueError(
            "team_a_id and team_b_id must be different"
        )


def get_team_head_to_head(
    session: Session,
    team_a_id: int,
    team_b_id: int,
) -> dict | None:
    """
    Return head-to-head statistics between two teams.

    Metrics:
        - matches
        - team_a_wins
        - team_b_wins
        - ties
        - no_results

    Returns None when the two teams have never played
    each other.
    """

    _validate_team_ids(
        team_a_id,
        team_b_id,
    )

    result = session.execute(
        TEAM_HEAD_TO_HEAD_QUERY,
        {
            "team_a_id": team_a_id,
            "team_b_id": team_b_id,
        },
    ).mappings().first()

    if result is None:
        return None

    return dict(result)


def get_team_head_to_head_by_season(
    session: Session,
    team_a_id: int,
    team_b_id: int,
) -> list[dict]:
    """
    Return season-wise head-to-head statistics between two teams.

    Metrics for each season:
        - season
        - matches
        - team_a_wins
        - team_b_wins
        - ties
        - no_results

    Returns an empty list when the two teams have never played
    each other.
    """

    _validate_team_ids(
        team_a_id,
        team_b_id,
    )

    result = session.execute(
        TEAM_HEAD_TO_HEAD_BY_SEASON_QUERY,
        {
            "team_a_id": team_a_id,
            "team_b_id": team_b_id,
        },
    )

    return [
        dict(row)
        for row in result.mappings()
    ]
