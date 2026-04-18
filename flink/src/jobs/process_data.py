import json
from datetime import datetime

from pyflink.common import Duration, Types, WatermarkStrategy
from pyflink.common.serialization import Encoder, SimpleStringSchema
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.file_system import FileSink, OutputFileConfig
from pyflink.datastream.connectors.kafka import KafkaOffsetsInitializer, KafkaSource
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.datastream.connectors.file_system import BucketAssigner
from pyflink.datastream.connectors.file_system import FileSink#, DateBucketAssigner
from pyflink.java_gateway import get_gateway

REDPANDA_BROKERS = "redpanda:29092"
TOPIC = "interactions"
MINIO_RAW = "s3://llm-raw/interactions/"
MINIO_PROCESSED = "s3://llm-processed/interactions/"
MINIO_WINDOWS = "s3://llm-processed/failure_windows/"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def classify_severity(row: dict) -> dict:
    if not row["is_failure"]:
        row["severity"] = "ok"
    elif row["failure_type"] in ("hallucination", "toxicity"):
        row["severity"] = "critical"
    elif row["failure_type"] in ("latency_timeout", "formatting_error"):
        row["severity"] = "warning"
    else:
        row["severity"] = "unknown"
    return row


class InteractionTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp: int) -> int:
        ts = json.loads(value)["timestamp_utc"]
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)  # milliseconds


class DateBucketAssigner(BucketAssigner):

    def open(self, context):
        # Required in some PyFlink versions
        pass

    def get_bucket_id(self, element, context):
        ts = json.loads(element)["timestamp_utc"]
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return f"date={dt.strftime('%Y-%m-%d')}"


def make_file_sink(path: str, prefix: str) -> FileSink:
    gateway = get_gateway()
    j_date_assigner = gateway.jvm.org.apache.flink.streaming.api.functions.sink.filesystem.bucketassigners.DateTimeBucketAssigner("'date='yyyy-MM-dd")
    bucket_assigner = BucketAssigner(j_bucket_assigner=j_date_assigner)

    return (
        FileSink.for_row_format(path, Encoder.simple_string_encoder())
        .with_bucket_assigner(bucket_assigner)
        .with_output_file_config(
            OutputFileConfig.builder()
            .with_part_prefix(prefix)
            .with_part_suffix(".json")
            .build()
        )
        .build()
    )


env = StreamExecutionEnvironment.get_execution_environment()
env.enable_checkpointing(30_000)
env.set_parallelism(1)

source = (
    KafkaSource.builder()
    .set_bootstrap_servers(REDPANDA_BROKERS)
    .set_topics(TOPIC)
    .set_group_id("flink-enriched-sink")
    .set_starting_offsets(KafkaOffsetsInitializer.earliest())
    .set_value_only_deserializer(SimpleStringSchema())
    .build()
)

watermark_strategy = (
    WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(30))
    .with_timestamp_assigner(InteractionTimestampAssigner())
)

raw_stream = env.from_source(
    source,
    watermark_strategy=watermark_strategy,
    source_name="redpanda-source",
)

# keep raw stream writing to llm-raw unchanged
raw_stream.sink_to(make_file_sink(MINIO_RAW, "interactions"))

# enrich
enriched_stream = raw_stream.map(
    lambda msg: json.dumps(classify_severity(json.loads(msg))),
    output_type=Types.STRING(),
)

enriched_stream.sink_to(make_file_sink(MINIO_PROCESSED, "interactions"))

# 5-min tumbling window failure rate per model
def to_window_row(msg: str) -> str:
    row = json.loads(msg)
    return json.dumps({
        "model_name": row["model_name"],
        "model_provider": row["model_provider"],
        "is_failure": row["is_failure"],
        "timestamp_utc": row["timestamp_utc"],
    })


class FailureRateWindowFunction:
    def open(self, runtime_context):
        pass

    def apply(self, key, window, inputs):
        rows = list(inputs)
        total = len(rows)
        failures = sum(1 for r in rows if json.loads(r)["is_failure"])
        result = json.dumps({
            "window_start": str(window.start),
            "window_end": str(window.end),
            "model_name": key[0],
            "model_provider": key[1],
            "total": total,
            "failures": failures,
            "failure_rate": round(failures / total, 3) if total else 0.0,
        })
        yield result

from pyflink.common.time import Time
(

    enriched_stream
    .map(to_window_row, output_type=Types.STRING())
    .key_by(
        lambda msg: (json.loads(msg)["model_name"], json.loads(msg)["model_provider"]),
        key_type=Types.TUPLE([Types.STRING(), Types.STRING()]),
    )

    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    # .window(TumblingEventTimeWindows.of(Duration.of_minutes(5)))
    .apply(FailureRateWindowFunction())
    .sink_to(make_file_sink(MINIO_WINDOWS, "window"))
)

env.execute("enriched-sink")