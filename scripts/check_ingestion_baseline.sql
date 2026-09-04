-- ============================================================
-- IPL INTELLIGENCE PLATFORM
-- Full Ingestion Baseline Check
-- ============================================================

-- ------------------------------------------------------------
-- 1. Dimension / Match Counts
-- ------------------------------------------------------------

SELECT 'dim_match' AS table_name, COUNT(*) AS row_count
FROM dim_match

UNION ALL

SELECT 'dim_team', COUNT(*)
FROM dim_team

UNION ALL

SELECT 'dim_player', COUNT(*)
FROM dim_player

UNION ALL

SELECT 'dim_venue', COUNT(*)
FROM dim_venue

UNION ALL

SELECT 'match_team', COUNT(*)
FROM match_team

UNION ALL

SELECT 'match_innings', COUNT(*)
FROM match_innings

UNION ALL

SELECT 'fact_delivery', COUNT(*)
FROM fact_delivery

UNION ALL

SELECT 'delivery_extras', COUNT(*)
FROM delivery_extras

UNION ALL

SELECT 'delivery_wickets', COUNT(*)
FROM delivery_wickets

ORDER BY table_name;


-- ------------------------------------------------------------
-- 2. Audit Counts
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS etl_runs
FROM etl_run;

SELECT
    COUNT(*) AS etl_file_logs
FROM etl_file_log;


-- ------------------------------------------------------------
-- 3. Latest ETL Run
-- ------------------------------------------------------------

SELECT
    run_id,
    status,
    files_discovered,
    files_processed,
    files_succeeded,
    files_failed,
    started_at,
    finished_at
FROM etl_run
ORDER BY run_id DESC
LIMIT 1;


-- ------------------------------------------------------------
-- 4. Match Date Range
-- ------------------------------------------------------------

SELECT
    MIN(match_date) AS earliest_match,
    MAX(match_date) AS latest_match,
    COUNT(*) AS matches
FROM dim_match;


-- ------------------------------------------------------------
-- 5. Seasons
-- ------------------------------------------------------------

SELECT
    season,
    COUNT(*) AS matches
FROM dim_match
GROUP BY season
ORDER BY season;