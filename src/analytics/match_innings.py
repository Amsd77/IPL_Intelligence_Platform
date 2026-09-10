from sqlalchemy import text
from sqlalchemy.orm import Session


MATCH_INNINGS_QUERY = text(
    """
    WITH delivery_stats AS (
        SELECT
            mi.innings_id,
            mi.match_id,
            mi.innings_number,
            mi.batting_team_id,

            COUNT(d.delivery_id) AS deliveries,

            COUNT(d.delivery_id) FILTER (
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM delivery_extras de
                    WHERE de.delivery_id = d.delivery_id
                      AND de.extra_type IN ('wides', 'noballs')
                )
            ) AS legal_deliveries,

            COALESCE(
                SUM(d.total_runs),
                0
            ) AS runs

        FROM match_innings mi

        LEFT JOIN fact_delivery d
            ON d.innings_id = mi.innings_id

        WHERE mi.match_id = :match_id

        GROUP BY
            mi.innings_id,
            mi.match_id,
            mi.innings_number,
            mi.batting_team_id
    ),

    wicket_stats AS (
        SELECT
            mi.innings_id,

            COUNT(dw.delivery_wicket_id) FILTER (
                WHERE dw.kind <> 'retired hurt'
            ) AS wickets_lost

        FROM match_innings mi

        LEFT JOIN fact_delivery d
            ON d.innings_id = mi.innings_id

        LEFT JOIN delivery_wickets dw
            ON dw.delivery_id = d.delivery_id

        WHERE mi.match_id = :match_id

        GROUP BY
            mi.innings_id
    )

    SELECT
        ds.innings_id,
        ds.match_id,
        ds.innings_number,

        t.team_id AS batting_team_id,
        t.team_name AS batting_team,

        ds.runs,
        COALESCE(ws.wickets_lost, 0) AS wickets_lost,
        ds.deliveries,
        ds.legal_deliveries,

        ROUND(
            CASE
                WHEN ds.legal_deliveries > 0
                THEN
                    ds.runs::numeric * 6
                    / ds.legal_deliveries
                ELSE NULL
            END,
            2
        ) AS run_rate

    FROM delivery_stats ds

    JOIN dim_team t
        ON t.team_id = ds.batting_team_id

    LEFT JOIN wicket_stats ws
        ON ws.innings_id = ds.innings_id

    ORDER BY
        ds.innings_number
    """
)

def get_match_innings_stats(
    session: Session,
    match_id: int,
) -> list[dict]:
    """
    Return innings-level statistics for a single match.

    Metrics:
        - innings number
        - batting team
        - runs
        - wickets lost
        - deliveries
        - legal deliveries
        - run rate
    """

    if match_id <= 0:
        raise ValueError("match_id must be greater than zero")

    result = session.execute(
        MATCH_INNINGS_QUERY,
        {"match_id": match_id},
    )

    return [
        dict(row)
        for row in result.mappings()
    ]