FROM python:3.11-slim

ENV POETRY_VERSION=1.7.1
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --only main

COPY . .
RUN poetry install --only main

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
