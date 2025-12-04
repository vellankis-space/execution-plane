# Start OTEL Collector for local development

To run the backend locally with OTEL Collector in Docker:

```bash
# 1. Start only the OTEL Collector service
docker-compose up -d otel-collector

# 2. Set environment variable for backend
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# 3. Run backend locally
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or add to your `.env` file:
```
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

This allows the local backend to send traces to the dockerized OTEL Collector.
