from pydantic import BaseModel
from datetime import datetime


class Interaction(BaseModel):
    interaction_id: str
    session_id: str
    user_id: str
    timestamp_utc: datetime
    model_provider: str
    model_name: str
    latency_ms: float
    total_tokens: int
    cost_usd: float
    is_failure: bool
    failure_type: str | None
    hallucination_flag: bool
    toxicity_flag: bool
    safety_block_flag: bool
    latency_timeout_flag: bool
    response_quality_score: float
    channel: str
    use_case: str