from sqlalchemy import text
from sqlalchemy.orm import Session


MATCH_SUMMARY_QUERY = text(
    """
    SELECT
        m.match_id,
        m.season,
        m.match_date,
        m.city,
        m.match_type,
        m.gender,
        m.toss_decision,
        m.player_of_match,

        toss_team.team_name AS toss_winner,
        winner_team.team_name AS winner,

        STRING_AGG(
            DISTINCT playing_team.team_name,
            ' vs '
            ORDER BY playing_team.team_name
        ) AS teams

    FROM dim_match m

    LEFT JOIN dim_team toss_team
        ON toss_team.team_id = m.toss_winner_id

    LEFT JOIN dim_team winner_team
        ON winner_team.team_id = m.winner_id

    LEFT JOIN match_team mt
        ON mt.match_id = m.match_id

    LEFT JOIN dim_team playing_team
        ON playing_team.team_id = mt.team_id

    WHERE m.match_id = :match_id

    GROUP BY
        m.match_id,
        m.season,
        m.match_date,
        m.city,
        m.match_type,
        m.gender,
        m.toss_decision,
        m.player_of_match,
        toss_team.team_name,
        winner_team.team_name
    """
)


def get_match_summary(
    session: Session,
    match_id: int,
) -> dict | None:
    """
    Return summary information for a single match.

    Returns None when the match does not exist.
    """

    if match_id <= 0:
        raise ValueError("match_id must be greater than zero")

    result = session.execute(
        MATCH_SUMMARY_QUERY,
        {"match_id": match_id},
    ).mappings().first()

    if result is None:
        return None

    return dict(result)