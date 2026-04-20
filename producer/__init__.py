import csv
import json
import random
import time

from kafka import KafkaProducer
from shared.schema import Interaction
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file="../.env",
        case_insensitive=True,
    )
    topic: str
    broker: str = Field(alias="broker_external")
    data_path: str = "../data/llm_system_interactions.csv"

settings = Settings()

producer = KafkaProducer(
    bootstrap_servers=settings.broker,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

with open(settings.data_path, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        interaction = Interaction.model_validate(row)
        producer.send(settings.topic, value=interaction.model_dump(mode="json"))
        time.sleep(random.uniform(0.05, 0.3))

producer.flush()
