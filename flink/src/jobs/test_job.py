from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaSource,
    KafkaOffsetsInitializer,
)
from pyflink.datastream.connectors.file_system import FileSink, OutputFileConfig
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.formats.json import JsonRowSerializationSchema
from pyflink.common import WatermarkStrategy
from pyflink.common.serialization import Encoder

REDPANDA_BROKERS = "redpanda:29092"
TOPIC = "interactions"
MINIO_BUCKET = "s3://llm-raw/interactions/"

env = StreamExecutionEnvironment.get_execution_environment()
env.enable_checkpointing(30_000)  # checkpoint every 30s
env.set_parallelism(1)

# Configure MinIO as S3 endpoint
# env.get_checkpoint_config()
# config = env.get_configuration()
# config.set_string("s3.endpoint", "http://minio:9000")
# config.set_string("s3.access-key", "minioadmin")
# config.set_string("s3.secret-key", "minioadmin")
# config.set_string("s3.path.style.access", "true")  # required for MinIO

# Source — read raw JSON strings from Redpanda
source = (
    KafkaSource.builder()
    .set_bootstrap_servers(REDPANDA_BROKERS)
    .set_topics(TOPIC)
    .set_group_id("flink-raw-sink")
    .set_starting_offsets(KafkaOffsetsInitializer.earliest())
    .set_value_only_deserializer(SimpleStringSchema())
    .build()
)

stream = env.from_source(
    source,
    watermark_strategy=WatermarkStrategy.no_watermarks(),
    source_name="redpanda-source",
)

# Sink — write raw JSON strings to MinIO, one file per 5 minutes
sink = (
    FileSink.for_row_format(
        MINIO_BUCKET,
        Encoder.simple_string_encoder(),
    )
    .with_output_file_config(
        OutputFileConfig.builder()
        .with_part_prefix("interactions")
        .with_part_suffix(".json")
        .build()
    )
    .build()
)

stream.sink_to(sink)
env.execute("raw-sink")