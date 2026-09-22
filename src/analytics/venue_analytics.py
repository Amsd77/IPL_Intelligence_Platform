from sqlalchemy import text
from sqlalchemy.orm import Session


VENUE_STATS_QUERY = text(
    """
    WITH innings_delivery_stats AS (
        SELECT
            mi.innings_id,
            mi.match_id,

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

        JOIN fact_delivery d
            ON d.innings_id = mi.innings_id

        JOIN dim_match m
            ON m.match_id = mi.match_id

        WHERE m.venue_id = :venue_id

        GROUP BY
            mi.innings_id,
            mi.match_id
    ),

    innings_wicket_stats AS (
        SELECT
            mi.innings_id,

            COUNT(dw.delivery_wicket_id) FILTER (
                WHERE dw.kind <> 'retired hurt'
            ) AS wickets

        FROM match_innings mi

        JOIN fact_delivery d
            ON d.innings_id = mi.innings_id

        JOIN dim_match m
            ON m.match_id = mi.match_id

        LEFT JOIN delivery_wickets dw
            ON dw.delivery_id = d.delivery_id

        WHERE m.venue_id = :venue_id

        GROUP BY
            mi.innings_id
    ),

    innings_stats AS (
        SELECT
            ids.innings_id,
            ids.match_id,
            ids.runs,
            ids.legal_deliveries,

            ROUND(
                CASE
                    WHEN ids.legal_deliveries > 0
                    THEN
                        ids.runs::numeric * 6
                        / ids.legal_deliveries
                    ELSE NULL
                END,
                2
            ) AS run_rate,

            COALESCE(iws.wickets, 0) AS wickets

        FROM innings_delivery_stats ids

        LEFT JOIN innings_wicket_stats iws
            ON iws.innings_id = ids.innings_id
    ),

    venue_stats AS (
        SELECT
            COUNT(DISTINCT match_id) AS matches,
            COUNT(*) AS innings,

            COALESCE(
                SUM(runs),
                0
            ) AS total_runs,

            ROUND(
                SUM(runs)::numeric
                / NULLIF(COUNT(*), 0),
                2
            ) AS average_runs_per_innings,

            MAX(runs) AS highest_innings_score,

            ROUND(
                AVG(run_rate),
                2
            ) AS average_run_rate,

            COALESCE(
                SUM(wickets),
                0
            ) AS total_wickets,

            ROUND(
                SUM(wickets)::numeric
                / NULLIF(COUNT(*), 0),
                2
            ) AS average_wickets_per_innings

        FROM innings_stats
    )

    SELECT
        v.venue_id,
        v.venue_name,
        v.city,

        vs.matches,
        vs.innings,
        vs.total_runs,
        vs.average_runs_per_innings,
        vs.highest_innings_score,
        vs.average_run_rate,
        vs.total_wickets,
        vs.average_wickets_per_innings

    FROM dim_venue v

    CROSS JOIN venue_stats vs

    WHERE v.venue_id = :venue_id
    """
)


TOP_VENUES_QUERY = text(
    """
    WITH innings_delivery_stats AS (
        SELECT
            mi.innings_id,
            mi.match_id,
            m.venue_id,

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

        JOIN dim_match m
            ON m.match_id = mi.match_id

        JOIN fact_delivery d
            ON d.innings_id = mi.innings_id

        GROUP BY
            mi.innings_id,
            mi.match_id,
            m.venue_id
    ),

    innings_wicket_stats AS (
        SELECT
            mi.innings_id,

            COUNT(dw.delivery_wicket_id) FILTER (
                WHERE dw.kind <> 'retired hurt'
            ) AS wickets

        FROM match_innings mi

        JOIN dim_match m
            ON m.match_id = mi.match_id

        JOIN fact_delivery d
            ON d.innings_id = mi.innings_id

        LEFT JOIN delivery_wickets dw
            ON dw.delivery_id = d.delivery_id

        GROUP BY
            mi.innings_id
    ),

    innings_stats AS (
        SELECT
            ids.innings_id,
            ids.match_id,
            ids.venue_id,
            ids.runs,
            ids.legal_deliveries,

            ROUND(
                CASE
                    WHEN ids.legal_deliveries > 0
                    THEN
                        ids.runs::numeric * 6
                        / ids.legal_deliveries
                    ELSE NULL
                END,
                2
            ) AS run_rate,

            COALESCE(iws.wickets, 0) AS wickets

        FROM innings_delivery_stats ids

        LEFT JOIN innings_wicket_stats iws
            ON iws.innings_id = ids.innings_id
    )

    SELECT
        v.venue_id,
        v.venue_name,
        v.city,

        COUNT(DISTINCT i.match_id) AS matches,
        COUNT(*) AS innings,

        COALESCE(
            SUM(i.runs),
            0
        ) AS total_runs,

        ROUND(
            SUM(i.runs)::numeric
            / NULLIF(COUNT(*), 0),
            2
        ) AS average_runs_per_innings,

        MAX(i.runs) AS highest_innings_score,

        ROUND(
            AVG(i.run_rate),
            2
        ) AS average_run_rate,

        COALESCE(
            SUM(i.wickets),
            0
        ) AS total_wickets,

        ROUND(
            SUM(i.wickets)::numeric
            / NULLIF(COUNT(*), 0),
            2
        ) AS average_wickets_per_innings

    FROM dim_venue v

    JOIN innings_stats i
        ON i.venue_id = v.venue_id

    GROUP BY
        v.venue_id,
        v.venue_name,
        v.city

    ORDER BY
        total_runs DESC,
        v.venue_name

    LIMIT :limit
    """
)


def get_venue_stats(
    session: Session,
    venue_id: int,
) -> dict | None:
    """
    Return aggregate statistics for a single venue.

    Metrics:
        - matches
        - innings
        - total runs
        - average runs per innings
        - highest innings score
        - average run rate
        - total wickets
        - average wickets per innings

    Returns None when the venue does not exist.
    """

    if venue_id <= 0:
        raise ValueError("venue_id must be greater than zero")

    result = session.execute(
        VENUE_STATS_QUERY,
        {"venue_id": venue_id},
    ).mappings().first()

    if result is None:
        return None

    return dict(result)


def get_top_venues(
    session: Session,
    limit: int = 20,
) -> list[dict]:
    """
    Return venues ordered by total runs.
    """

    if limit <= 0:
        raise ValueError("limit must be greater than zero")

    result = session.execute(
        TOP_VENUES_QUERY,
        {"limit": limit},
    )

    return [
        dict(row)
        for row in result.mappings()
    ]
