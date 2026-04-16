import os
import duckdb
import streamlit as st

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")

DATA_SOURCE = os.environ.get("DATA_SOURCE", "read_json_auto('s3://llm-raw/**/*.json')")
BACKEND = os.environ.get("BACKEND", "s3")

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
    elif BACKEND == "bigquery":
        con.execute("INSTALL bigquery FROM community; LOAD bigquery;")
    # config from env vars
    return con

def load_data(con):
    return con.execute(f"SELECT * FROM {DATA_SOURCE}").fetchdf()


st.title("Dashboard")

con = get_connection()

try:
    df = load_data(con)
    st.caption(f"Loaded {len(df)} interactions")

    # Tile 1 — placeholder: failures by model
    st.subheader("Failures by model")
    st.bar_chart(
        df[df["is_failure"] == True]
        .groupby("model_name")
        .size()
        .reset_index(name="count")
        .set_index("model_name")
    )

    # Tile 2 — placeholder: events over time
    st.subheader("Interactions over time")
    st.line_chart(
        df.groupby("timestamp_utc")
        .size()
        .reset_index(name="count")
        .set_index("timestamp_utc")
    )

except Exception as e:
    st.error(f"Could not load data: {e}")