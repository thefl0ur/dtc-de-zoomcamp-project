import csv
import json
import random
import time

from kafka import KafkaProducer
from shared.schema import Interaction

CSV_PATH = "../data/llm_system_interactions.csv"
BROKER = "localhost:9092"
TOPIC = "interactions"

producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    count = 0
    for row in csv.DictReader(f):
        interaction = Interaction.model_validate(row)
        producer.send(TOPIC, value=interaction.model_dump(mode="json"))
        time.sleep(random.uniform(0.05, 0.3))
        count += 1
        if count >100:
            break

producer.flush()
