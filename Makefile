create-topic:
	@docker compose exec redpanda rpk topic create interactions

validate:
	@docker compose exec redpanda rpk topic consume interactions -n 10

create-bucket:
	@docker compose exec minio mc alias set myminio http://localhost:9000 minioadmin minioadmin
	@docker compose exec minio mc mb myminio/llm-raw

flinks:
	@docker compose exec jobmanager flink run -py /opt/src/jobs/test_job.py -d