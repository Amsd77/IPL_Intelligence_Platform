from sqlalchemy import text
from sqlalchemy.orm import Session


PLAYER_BOWLING_QUERY = text(
    """
    WITH delivery_extras_agg AS (
        SELECT
            delivery_id,
            SUM(
                CASE
                    WHEN extra_type IN ('byes', 'legbyes', 'penalty')
                    THEN runs
                    ELSE 0
                END
            ) AS non_bowler_runs,

            MAX(
                CASE
                    WHEN extra_type IN ('wides', 'noballs')
                    THEN 1
                    ELSE 0
                END
            ) AS is_illegal_delivery

        FROM delivery_extras

        GROUP BY delivery_id
    ),

    delivery_wickets_agg AS (
        SELECT
            delivery_id,

            COUNT(*) FILTER (
                WHERE kind IN (
                    'caught',
                    'bowled',
                    'lbw',
                    'caught and bowled',
                    'stumped',
                    'hit wicket'
                )
            ) AS bowler_wickets

        FROM delivery_wickets

        GROUP BY delivery_id
    )

    SELECT
        p.player_id,
        p.player_name,

        COUNT(DISTINCT mi.match_id) AS matches,

        COUNT(DISTINCT mi.innings_id) AS innings,

        COUNT(*) AS deliveries,

        COUNT(*) FILTER (
            WHERE COALESCE(e.is_illegal_delivery, 0) = 0
        ) AS legal_deliveries,

        COALESCE(
            SUM(
                d.total_runs
                - COALESCE(e.non_bowler_runs, 0)
            ),
            0
        ) AS runs_conceded,

        COALESCE(
            SUM(
                COALESCE(w.bowler_wickets, 0)
            ),
            0
        ) AS wickets

    FROM fact_delivery d

    JOIN dim_player p
        ON p.player_id = d.bowler_id

    JOIN match_innings mi
        ON mi.innings_id = d.innings_id

    LEFT JOIN delivery_extras_agg e
        ON e.delivery_id = d.delivery_id

    LEFT JOIN delivery_wickets_agg w
        ON w.delivery_id = d.delivery_id

    GROUP BY
        p.player_id,
        p.player_name

    ORDER BY
        wickets DESC,
        p.player_name
    """
)


def get_player_bowling_stats(
    session: Session,
) -> list[dict]:
    """
    Return bowling statistics for every player.

    Metrics:
        - matches
        - innings
        - deliveries
        - legal deliveries
        - runs conceded
        - wickets
        - bowling average
        - economy rate
        - bowling strike rate
    """

    result = session.execute(PLAYER_BOWLING_QUERY)

    stats = []

    for row in result.mappings():

        data = dict(row)

        runs_conceded = float(data["runs_conceded"])
        wickets = int(data["wickets"])
        legal_deliveries = int(data["legal_deliveries"])

        if wickets > 0:
            bowling_average = round(
                runs_conceded / wickets,
                2,
            )
        else:
            bowling_average = None

        if legal_deliveries > 0:
            economy_rate = round(
                runs_conceded * 6 / legal_deliveries,
                2,
            )
        else:
            economy_rate = None

        if wickets > 0:
            bowling_strike_rate = round(
                legal_deliveries / wickets,
                2,
            )
        else:
            bowling_strike_rate = None

        data["runs_conceded"] = runs_conceded
        data["wickets"] = wickets
        data["bowling_average"] = bowling_average
        data["economy_rate"] = economy_rate
        data["bowling_strike_rate"] = bowling_strike_rate

        stats.append(data)

    return stats


def get_top_bowlers(
    session: Session,
    limit: int = 20,
) -> list[dict]:
    """
    Return the top bowlers ordered by wickets.
    """

    if limit <= 0:
        raise ValueError(
            "limit must be greater than zero"
        )

    stats = get_player_bowling_stats(session)

    return stats[:limit]