# LLM System Ops Telemetry Dashboard System (LLMSOPTDS)

Locall streaming pipeline that simulates LLM telemetry, detects and classifies failures , stores them in a lakehouse, and provide insights in dashboard.

System is intended to use by platform engineer, who need to quickly react to new insidents.

Currently system displays 2 tile in dashboard: failures by model and failures timeline.

## Data set

Used dataset is [LLM System Ops Production Telemetry & SFT](https://www.kaggle.com/datasets/tarekmasryo/llm-system-ops-production-telemetry-and-sft/data).

> A synthetic, production-style, multi-table LLM telemetry dataset for LLMOps analytics and decision-grade experiments.

Info about obtaining data set for running see [below](#getting-data-set)

## System architecture

### Ingest

Uv-based python script `producer/` that simulates source of events

Reads data from dataset and submit events into topic

### Stream processing

Pyflink job

Parse, validate (minimal) incoming data.

Working artifacts:
* unmodified data in `raw/interactions` bucket (data lake)
* enriched data in `processed/interactions` bucket
* aggregates data in `processed/failure_windows` bucket

### Storage

MinIO server

### Warehouse

Somewhere artificial layer for local system. Consist of views in `warehouse` readed by DuckDB in dashboard app and data `processed/` bucket.

### Dashboard

Streamlit app with 2 tiles
* failures by model
* failures timeline

## Reproducibility

### Getting data set

Download [dataset](https://www.kaggle.com/datasets/tarekmasryo/llm-system-ops-production-telemetry-and-sft/data) and extract all content (or only `llm_system_interactions.csv`) into folder `data/`

### Booting

Make sure required software is installed:

* [UV](https://docs.astral.sh/uv/getting-started/installation/)
* [docker](https://docs.docker.com/engine/install/)
* [terraform](https://developer.hashicorp.com/terraform/install)

1. Load and build images

```bash
docker compose pull
docker compose build
```

2. Init producer on local machine - this script is running on host.

```bash
cd producer && uv sync
```

3. Start `MinIO` and `Redpanda` services and waits for booting

```bash
docker compose up -d minio redpanda
```

4. Init terraform and create resources

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

5. Start remaining services

```
docker compose up -d
```

6. Check Flink starts

Go to [http://localhost:8081/](http://localhost:8081/). You should see 

```
Available Task Slots
1

Total Task Slots 1      Task Managers 1
```

### Running

1. Submit Flink job

```bash
docker compose exec jobmanager flink run -py /opt/src/jobs/process_data.py -d
```

2. Start producer

Running through whole data is about 25 minutes.

```bash
cd producer
uv run __init__.py
```

### Access dashboard

Go to [`localhost:8501`](http://localhost:8501)

## Evaluation Criteria

My opinion on evaluation project and some notes about it

### Problem description

- [ ] 0 points: Problem is not described
- [X] 2 points: Problem is described but shortly or not clearly
- [ ] 4 points: Problem is well described and it's clear what the problem the project solves

### Cloud

- [X] 0 points: Cloud is not used, things run only locally
- [ ] 2 points: The project is developed in the cloud
- [ ] 4 points: The project is developed in the cloud and IaC tools are used

> I miss deadlines and lost my free trial on GCP.

### Data ingestion (Stream

- [ ] 0 points: No streaming system (like Kafka, Pulsar, etc)
- [ ] 2 points: A simple pipeline with one consumer and one producer
- [X] 4 points: Using consumer/producers and streaming technologies (like Kafka streaming, Spark streaming, Flink, etc)

### Data warehouse

- [ ] 0 points: No DWH is used
- [X] 2 points: Tables are created in DWH, but not optimized
- [ ] 4 points: Tables are partitioned and clustered in a way that makes sense for the upstream queries (with explanation)

> while I have partitioned data (by date), no clustering

### Transformations (dbt, spark, etc)

- [ ] 0 points: No tranformations
- [ ] 2 points: Simple SQL transformation (no dbt or similar tools)
- [X] 4 points: Tranformations are defined with dbt, Spark or similar technologies

> Flink job transform incoming data (enrichment, add `severity` column)

### Dashboard

- [ ] 0 points: No dashboard
- [ ] 2 points: A dashboard with 1 tile
- [X] 4 points: A dashboard with 2 tiles

### Reproducibility

- [ ] 0 points: No instructions how to run the code at all
- [ ] 2 points: Some instructions are there, but they are not complete
- [X] 4 points: Instructions are clear, it's easy to run the code, and the code works

> I rerun whole cycle