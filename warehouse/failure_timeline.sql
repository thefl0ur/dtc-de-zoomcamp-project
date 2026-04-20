CREATE OR REPLACE VIEW failure_timeline AS
SELECT
    epoch_ms(CAST(window_start AS BIGINT)) AS window_time,
    model_name,
    failure_rate
FROM read_json_auto('s3://llm-processed/failure_windows/**/*.json')
ORDER BY window_start
