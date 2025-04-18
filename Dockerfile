FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY mocks/ mocks/

RUN pip install --no-cache-dir .

RUN useradd --create-home appuser
USER appuser

ENV NETSUITE_MOCK=true
ENV PYTHONPATH=/app/src

CMD ["python", "/app/src/server.py"]