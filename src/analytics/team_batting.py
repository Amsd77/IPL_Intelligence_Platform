from sqlalchemy import text
from sqlalchemy.orm import Session


TEAM_BATTING_QUERY = text(
    """
    SELECT
        t.team_id,
        t.team_name,

        COUNT(DISTINCT mi.match_id) AS matches,

        COUNT(DISTINCT mi.innings_id) AS innings,

        COALESCE(SUM(d.batter_runs), 0) AS runs,

        COUNT(*) FILTER (
            WHERE NOT EXISTS (
                SELECT 1
                FROM delivery_extras de
                WHERE de.delivery_id = d.delivery_id
                  AND de.extra_type = 'wides'
            )
        ) AS balls_faced,

        COUNT(DISTINCT dw.delivery_wicket_id) AS wickets_lost,

        ROUND(
            CASE
                WHEN COUNT(DISTINCT dw.delivery_wicket_id) > 0
                THEN
                    SUM(d.batter_runs)::numeric
                    / COUNT(DISTINCT dw.delivery_wicket_id)
                ELSE NULL
            END,
            2
        ) AS batting_average,

        ROUND(
            CASE
                WHEN COUNT(*) FILTER (
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM delivery_extras de
                        WHERE de.delivery_id = d.delivery_id
                          AND de.extra_type = 'wides'
                    )
                ) > 0
                THEN
                    SUM(d.batter_runs)::numeric * 100
                    /
                    COUNT(*) FILTER (
                        WHERE NOT EXISTS (
                            SELECT 1
                            FROM delivery_extras de
                            WHERE de.delivery_id = d.delivery_id
                              AND de.extra_type = 'wides'
                        )
                    )
                ELSE 0
            END,
            2
        ) AS strike_rate,

        ROUND(
            SUM(d.batter_runs)::numeric
            / NULLIF(COUNT(DISTINCT mi.innings_id), 0),
            2
        ) AS average_score

    FROM dim_team t

    JOIN match_innings mi
        ON mi.batting_team_id = t.team_id

    JOIN fact_delivery d
        ON d.innings_id = mi.innings_id

    LEFT JOIN delivery_wickets dw
        ON dw.delivery_id = d.delivery_id
        AND dw.player_out_id = d.batter_id

    GROUP BY
        t.team_id,
        t.team_name

    ORDER BY
        runs DESC,
        t.team_name
    """
)


def get_team_batting_stats(
    session: Session,
) -> list[dict]:
    """
    Return batting statistics for every team.

    Metrics:
        - matches
        - innings
        - runs
        - balls faced
        - wickets lost
        - batting average
        - strike rate
        - average score
    """

    result = session.execute(TEAM_BATTING_QUERY)

    return [
        dict(row)
        for row in result.mappings()
    ]


def get_top_batting_teams(
    session: Session,
    limit: int = 20,
) -> list[dict]:
    """
    Return the top batting teams ordered by total runs.
    """

    if limit <= 0:
        raise ValueError("limit must be greater than zero")

    stats = get_team_batting_stats(session)

    return stats[:limit]