import os
from pathlib import Path
import duckdb
import streamlit as st

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT")
MINIO_USER = os.environ.get("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.environ.get("MINIO_ROOT_PASSWORD")
DATA_SOURCE = os.environ.get("DATA_SOURCE")

WAREHOUSE = Path("/app/warehouse")
MODELS = [
    "interactions.sql",
    "failure_by_model.sql",
    "failure_timeline.sql",
]

@st.cache_resource
def get_connection():
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(f"""
        SET s3_endpoint='{MINIO_ENDPOINT}';
        SET s3_access_key_id='{MINIO_USER}';
        SET s3_secret_access_key='{MINIO_SECRET_KEY}';
        SET s3_use_ssl=false;
        SET s3_url_style='path';
    """)
    for filename in MODELS:
        sql = (WAREHOUSE / filename).read_text()
        try:
            con.execute(sql)
        except Exception as e:
            st.warning(f"View {filename} not ready yet: {e}")
            
    return con

def load_data(con):
    return con.execute(f"SELECT * FROM {DATA_SOURCE}").fetchdf()


st.title("Dashboard")

con = get_connection()

def query(con: duckdb.DuckDBPyConnection, sql: str):
    return con.execute(sql).fetchdf()

try:
    total = query(con, "SELECT COUNT(*) AS n FROM interactions").iloc[0]["n"]
    last = query(con, "SELECT MAX(timestamp_utc) AS t FROM interactions").iloc[0]["t"]
    st.caption(f"Total interactions: {total} | Last event: {last}")
except Exception as e:
    st.info(f"Waiting for data...")

try:
    st.subheader("Failure breakdown by model")
    df_model = query(con, "SELECT * FROM failure_by_model WHERE failures > 0")
    if df_model.empty:
        st.info("No failure data yet — waiting for Flink to process events.")
    else:
        st.bar_chart(df_model, x="model_name", y="total", color="severity")
except Exception as e:
    st.info(f"Waiting for data...")

try:
    st.subheader("Failure rate over time")
    df_time = query(con, "SELECT * FROM failure_timeline")
    if df_time.empty:
        st.info("No window data yet — waiting for Flink to process events.")
    else:
        st.line_chart(
            df_time.pivot(index="window_time", columns="model_name", values="failure_rate"),
            x_label="Time",
            y_label="Failure rate",
        )
except Exception as e:
    st.info(f"Waiting for data...")
