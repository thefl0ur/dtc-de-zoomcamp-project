terraform {
  required_providers {
    minio = {
      source  = "aminueza/minio"
      version = "~> 2.0"
    }
    kafka = {
      source  = "Mongey/kafka"
      version = "~> 0.7"
    }
  }
}

provider "minio" {
  minio_server   = "localhost:9000"
  minio_user     = var.minio_user
  minio_password = var.minio_password
  minio_ssl      = false
}

provider "kafka" {
  bootstrap_servers = [var.broker_external]
  tls_enabled       = false
}

resource "minio_s3_bucket" "raw" {
  bucket = "llm-raw"
}

resource "minio_s3_bucket" "processed" {
  bucket = "llm-processed"
}

resource "kafka_topic" "interactions" {
  name               = "interactions"
  replication_factor = 1
  partitions         = 1
  config = {
    "retention.ms" = "604800000"
  }
}

resource "local_file" "env" {
  content = templatefile("${path.module}/env.tpl", {
    minio_endpoint   = var.minio_endpoint
    minio_user       = var.minio_user
    minio_password   = var.minio_password
    broker           = var.broker
    broker_external  = var.broker_external
    raw_bucket       = minio_s3_bucket.raw.bucket
    processed_bucket = minio_s3_bucket.processed.bucket
    topic            = kafka_topic.interactions.name
    backend          = var.backend
    data_source      = "read_json_auto('s3://${minio_s3_bucket.raw.bucket}/**/*.json')"
  })
  filename = "${path.module}/../.env"
}

resource "local_file" "flink_conf" {
  content = templatefile("${path.module}/flink-config.yaml.tpl", {
    minio_endpoint = var.minio_endpoint
    minio_user     = var.minio_user
    minio_password = var.minio_password
  })
  filename = "${path.module}/../flink/flink-config.yaml"
}