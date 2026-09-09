from sqlalchemy import text
from sqlalchemy.orm import Session


TEAM_BOWLING_QUERY = text(
    """
    WITH extra_aggregates AS (
        SELECT
            de.delivery_id,

            SUM(
                CASE
                    WHEN de.extra_type IN ('wides', 'noballs')
                    THEN 1
                    ELSE 0
                END
            ) AS illegal_extra_count,

            SUM(
                CASE
                    WHEN de.extra_type IN (
                        'byes',
                        'legbyes',
                        'penalty'
                    )
                    THEN de.runs
                    ELSE 0
                END
            ) AS non_bowler_runs

        FROM delivery_extras de

        GROUP BY
            de.delivery_id
    ),

    wicket_aggregates AS (
        SELECT
            dw.delivery_id,

            COUNT(*) FILTER (
                WHERE dw.kind IN (
                    'caught',
                    'bowled',
                    'lbw',
                    'caught and bowled',
                    'stumped',
                    'hit wicket'
                )
            ) AS bowler_wickets

        FROM delivery_wickets dw

        GROUP BY
            dw.delivery_id
    ),

    delivery_aggregates AS (
        SELECT
            d.delivery_id,
            d.innings_id,
            d.total_runs,

            CASE
                WHEN COALESCE(ea.illegal_extra_count, 0) > 0
                THEN 0
                ELSE 1
            END AS is_legal_delivery,

            d.total_runs
                - COALESCE(ea.non_bowler_runs, 0)
                AS runs_conceded,

            COALESCE(wa.bowler_wickets, 0)
                AS bowler_wickets

        FROM fact_delivery d

        LEFT JOIN extra_aggregates ea
            ON ea.delivery_id = d.delivery_id

        LEFT JOIN wicket_aggregates wa
            ON wa.delivery_id = d.delivery_id
    ),

    team_bowling AS (
        SELECT
            mt.team_id,

            COUNT(DISTINCT mi.match_id) AS matches,

            COUNT(DISTINCT mi.innings_id) AS innings,

            COUNT(da.delivery_id) AS deliveries,

            SUM(da.is_legal_delivery) AS legal_deliveries,

            SUM(da.runs_conceded) AS runs_conceded,

            SUM(da.bowler_wickets) AS wickets

        FROM delivery_aggregates da

        JOIN match_innings mi
            ON mi.innings_id = da.innings_id

        JOIN match_team mt
            ON mt.match_id = mi.match_id
            AND mt.team_id <> mi.batting_team_id

        GROUP BY
            mt.team_id
    )

    SELECT
        t.team_id,
        t.team_name,

        tb.matches,
        tb.innings,
        tb.deliveries,
        tb.legal_deliveries,
        tb.runs_conceded,
        tb.wickets,

        ROUND(
            CASE
                WHEN tb.wickets > 0
                THEN
                    tb.runs_conceded::numeric
                    / tb.wickets
                ELSE NULL
            END,
            2
        ) AS bowling_average,

        ROUND(
            CASE
                WHEN tb.legal_deliveries > 0
                THEN
                    tb.runs_conceded::numeric * 6
                    / tb.legal_deliveries
                ELSE NULL
            END,
            2
        ) AS economy_rate,

        ROUND(
            CASE
                WHEN tb.wickets > 0
                THEN
                    tb.legal_deliveries::numeric
                    / tb.wickets
                ELSE NULL
            END,
            2
        ) AS bowling_strike_rate,

        ROUND(
            CASE
                WHEN tb.innings > 0
                THEN
                    tb.runs_conceded::numeric
                    / tb.innings
                ELSE NULL
            END,
            2
        ) AS average_runs_conceded_per_innings

    FROM team_bowling tb

    JOIN dim_team t
        ON t.team_id = tb.team_id

    ORDER BY
        tb.wickets DESC,
        t.team_name
    """
)


def get_team_bowling_stats(
    session: Session,
) -> list[dict]:
    """
    Return bowling statistics for every team.

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
        - average runs conceded per innings
    """

    result = session.execute(TEAM_BOWLING_QUERY)

    return [
        dict(row)
        for row in result.mappings()
    ]


def get_top_bowling_teams(
    session: Session,
    limit: int = 20,
) -> list[dict]:
    """
    Return top teams ordered by total wickets taken.
    """

    if limit <= 0:
        raise ValueError("limit must be greater than zero")

    query = text(
        TEAM_BOWLING_QUERY.text
        + "\nLIMIT :limit"
    )

    result = session.execute(
        query,
        {"limit": limit},
    )

    return [
        dict(row)
        for row in result.mappings()
    ]