CREATE OR REPLACE VIEW failure_timeline AS
SELECT
    DATE_TRUNC('hour', timestamp_utc::TIMESTAMP) AS hour,
    COUNT(*) AS total,
    SUM(CASE WHEN is_failure THEN 1 ELSE 0 END) AS failures,
    ROUND(AVG(CASE WHEN is_failure THEN 1.0 ELSE 0.0 END), 3) AS failure_rate,
    SUM(CASE WHEN hallucination_flag THEN 1 ELSE 0 END) AS hallucinations,
    SUM(CASE WHEN safety_block_flag THEN 1 ELSE 0 END) AS safety_blocks,
    SUM(CASE WHEN latency_timeout_flag THEN 1 ELSE 0 END) AS latency_timeouts
FROM interactions
GROUP BY 1
ORDER BY 1;