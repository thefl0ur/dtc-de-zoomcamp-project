CREATE OR REPLACE VIEW failure_by_model AS
SELECT
    model_name,
    model_provider,
    failure_type,
    severity,
    COUNT(*) AS total,
    SUM(CASE WHEN is_failure THEN 1 ELSE 0 END) AS failures,
    ROUND(AVG(CASE WHEN is_failure THEN 1.0 ELSE 0.0 END), 3) AS failure_rate
FROM interactions
GROUP BY model_name, model_provider, failure_type, severity;