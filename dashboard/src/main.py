import os
from pathlib import Path
import duckdb
import streamlit as st

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")

DATA_SOURCE = os.environ.get("DATA_SOURCE", "read_json_auto('s3://llm-raw/**/*.json')")
BACKEND = os.environ.get("BACKEND", "s3")
WAREHOUSE = Path("/app/warehouse")

MODELS = [
    "interactions.sql",
    "failure_by_model.sql",
    "failure_timeline.sql",
]

@st.cache_resource
def get_connection():
    con = duckdb.connect()
    if BACKEND == "s3":
        con.execute("INSTALL httpfs; LOAD httpfs;")
        con.execute(f"""
            SET s3_endpoint='{MINIO_ENDPOINT}';
            SET s3_access_key_id='{MINIO_ACCESS_KEY}';
            SET s3_secret_access_key='{MINIO_SECRET_KEY}';
            SET s3_use_ssl=false;
            SET s3_url_style='path';
        """)
        for filename in MODELS:
            sql = (WAREHOUSE / filename).read_text()
            con.execute(sql)
            
    elif BACKEND == "bigquery":
        con.execute("INSTALL bigquery FROM community; LOAD bigquery;")
    # config from env vars
    return con

def load_data(con):
    return con.execute(f"SELECT * FROM {DATA_SOURCE}").fetchdf()


st.title("Dashboard")

con = get_connection()

def query(con: duckdb.DuckDBPyConnection, sql: str):
    return con.execute(sql).fetchdf()

try:
    # --- status row ---
    total = query(con, "SELECT COUNT(*) AS n FROM interactions").iloc[0]["n"]
    last = query(con, "SELECT MAX(timestamp_utc) AS t FROM interactions").iloc[0]["t"]
    st.caption(f"Total interactions: {total} | Last event: {last}")

    # Tile 1 — placeholder: failures by model
    st.subheader("Failure breakdown by model")
    df_model = query(con, "SELECT * FROM failure_by_model WHERE failures > 0")
    st.bar_chart(df_model, x="model_name", y="total", color="severity")

    # Tile 2 — placeholder: events over time
    st.subheader("Failure rate over time")
    df_time = query(con, "SELECT * FROM failure_timeline")
    st.line_chart(df_time, x="hour", y=["failure_rate", "hallucinations", "safety_blocks", "latency_timeouts"])

except Exception as e:
    st.error(f"Could not load data: {e}")