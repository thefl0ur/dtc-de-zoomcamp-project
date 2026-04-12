FROM flink:2.2.0-scala_2.12-java17

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /opt/pyflink
COPY pyproject.toml .
RUN uv python install 3.12 && uv sync
ENV PATH="/opt/pyflink/.venv/bin:$PATH"

# Download connector libraries

WORKDIR /opt/flink/lib
RUN mkdir -p /opt/flink/plugins/s3-fs-hadoop && \
    wget https://repo.maven.apache.org/maven2/org/apache/flink/flink-json/2.2.0/flink-json-2.2.0.jar; \
    wget https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/4.0.1-2.0/flink-sql-connector-kafka-4.0.1-2.0.jar; \
    wget https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-jdbc-core/4.0.0-2.0/flink-connector-jdbc-core-4.0.0-2.0.jar; \
    wget https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-jdbc-postgres/4.0.0-2.0/flink-connector-jdbc-postgres-4.0.0-2.0.jar; \
    wget https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.10/postgresql-42.7.10.jar; \
    wget -P /opt/flink/plugins/s3-fs-hadoop https://repo.maven.apache.org/maven2/org/apache/flink/flink-s3-fs-hadoop/2.2.0/flink-s3-fs-hadoop-2.2.0.jar

WORKDIR /opt/flink