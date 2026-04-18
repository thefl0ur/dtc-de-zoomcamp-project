CREATE OR REPLACE VIEW interactions AS
SELECT *
FROM read_json_auto('s3://llm-processed/interactions/**/*.json')