create-topic:
	@docker compose exec redpanda rpk topic create interactions

validate:
	@docker compose exec redpanda rpk topic consume interactions -n 10