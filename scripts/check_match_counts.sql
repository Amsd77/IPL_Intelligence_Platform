-- ============================================================
-- Match-level row count verification
-- ============================================================

SELECT
    m.match_id,
    m.season,
    COUNT(DISTINCT mi.innings_id) AS innings,
    COUNT(DISTINCT fd.delivery_id) AS deliveries,
    COUNT(DISTINCT de.delivery_extra_id) AS extras,
    COUNT(DISTINCT dw.delivery_wicket_id) AS wickets
FROM dim_match m
LEFT JOIN match_innings mi
    ON m.match_id = mi.match_id
LEFT JOIN fact_delivery fd
    ON mi.innings_id = fd.innings_id
LEFT JOIN delivery_extras de
    ON fd.delivery_id = de.delivery_id
LEFT JOIN delivery_wickets dw
    ON fd.delivery_id = dw.delivery_id
WHERE m.match_id = 1082591
GROUP BY
    m.match_id,
    m.season;