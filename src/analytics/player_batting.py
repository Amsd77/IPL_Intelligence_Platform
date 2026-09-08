from sqlalchemy import text
from sqlalchemy.orm import Session


PLAYER_BATTING_QUERY = text(
    """
    SELECT
        p.player_id,
        p.player_name,

        COUNT(DISTINCT mi.match_id) AS matches,

        COUNT(DISTINCT mi.innings_id) AS innings,

        COALESCE(SUM(d.batter_runs), 0) AS runs,

        COUNT(*) FILTER (
            WHERE d.actual_delivery IS NOT NULL
        ) AS balls_faced,

        COUNT(DISTINCT dw.delivery_wicket_id) AS dismissals,

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
                    WHERE d.actual_delivery IS NOT NULL
                ) > 0
                THEN
                    SUM(d.batter_runs)::numeric * 100
                    /
                    COUNT(*) FILTER (
                        WHERE d.actual_delivery IS NOT NULL
                    )
                ELSE 0
            END,
            2
        ) AS strike_rate

    FROM dim_player p

    JOIN fact_delivery d
        ON d.batter_id = p.player_id

    JOIN match_innings mi
        ON mi.innings_id = d.innings_id

    LEFT JOIN delivery_wickets dw
        ON dw.delivery_id = d.delivery_id
        AND dw.player_out_id = p.player_id

    GROUP BY
        p.player_id,
        p.player_name

    ORDER BY
        runs DESC,
        p.player_name
    """
)


def get_player_batting_stats(
    session: Session,
) -> list[dict]:
    """
    Return batting statistics for every player.

    Metrics:
        - matches
        - innings
        - runs
        - balls faced
        - dismissals
        - batting average
        - strike rate
    """

    result = session.execute(PLAYER_BATTING_QUERY)

    return [
        dict(row)
        for row in result.mappings()
    ]


def get_top_batters(
    session: Session,
    limit: int = 20,
) -> list[dict]:
    """
    Return the top batters ordered by total runs.
    """

    if limit <= 0:
        raise ValueError("limit must be greater than zero")

    stats = get_player_batting_stats(session)

    return stats[:limit]