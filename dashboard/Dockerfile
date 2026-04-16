FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

COPY . /app

RUN uv sync --frozen

CMD ["uv", "run", "streamlit", "run", "src/main.py"]