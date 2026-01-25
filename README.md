# Telemetry Processing System

1. What the system does

This system ingests device telemetry data, enriches it using external data sources, and evaluates alert rules in near real-time.

Core responsibilities:

- Accept telemetry data via HTTP APIs
- Store telemetry and metadata in MongoDB
- Publish events to Kafka for asynchronous processing
- Fetch data from external sources using Kafka consumers
- Validate alert rules against incoming telemetry and generate alerts

The system is designed to be event-driven, asynchronous, and scalable, separating API responsibilities from background processing.

2. How to run it

Prerequisites

- Python 3.10+
- MongoDB
- Kafka

Environment Variables

```bash
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=anan_sky_db

KAFKA_BOOTSTRAP_SERVERS=localhost:7092
KAFKA_GROUP_ID=telemetry-consumer

MODE=server          # server | consumer
CONSUMER_TYPE=fetch_external_source  # or alert_evaluator
```

Run API Server

```bash
MODE=server uvicorn src.main:app --reload
```

Run Kafka Consumer

```bash
MODE=consumer CONSUMER_TYPE=fetch_external_source python src/main.py

# or

MODE=consumer CONSUMER_TYPE=alert_evaluator python src/main.py
```

3. Key decisions made

- Single MongoDB client per process
  - Used a singleton Motor client to avoid connection overhead and ensure reuse across API routes and background consumers.

- Explicit database access (no ODM)
  - Database operations are handled via lightweight model classes instead of a full ORM/ODM to keep queries explicit and performant.

- Kafka for async processing
  - Time-consuming or non-critical work (external data fetch, alert evaluation) is handled asynchronously using Kafka consumers.

- Decoupled API and consumers
  - The API server and Kafka consumers can run independently, allowing horizontal scaling of each component.

- Schema validation at API boundary
  - Pydantic models are used to validate incoming data before it enters the system.

4. What I would improve or change in production

- Add MongoDB indexes and migrations for high-volume telemetry
- Implement dead-letter queues (DLQ) for failed Kafka messages
- Add observability (metrics, structured logging, tracing)
- Introduce authentication & authorization
- Add retry and backoff strategies for external API calls
- Separate database logic into a stricter Repository layer
- Add automated tests for consumers and alert evaluation logic
- Support schema versioning for telemetry payloads

---

Implementation notes, quick developer guide and where to look

This repository (`src/`) contains the FastAPI server, Kafka helpers, MongoDB access wrappers and per-consumer implementations. Below are the most relevant files and folders:

- `src/main.py` — application entrypoint. Starts FastAPI when `MODE=server` or runs the consumer runner when `MODE=consumer`.
- `src/config.py` — central configuration.
- `src/db.py` and `src/db_models.py` — Motor client wrapper and simple collection helpers.
- `src/models.py` — Pydantic models used by API endpoints.
- `src/kafka_client.py`, `src/producer.py`, `src/topic.py` — helpers to publish and consume Kafka messages.
- `src/consumers/runner.py` — consumer runner and lifecycle management (creates aiokafka consumer within an asyncio loop; restart/backoff logic).
- `src/consumers/config.py` — topic names, compatibility helpers and mapping registry.
- `src/consumers/external_source/` and `src/consumers/validate_alerts/` — per-consumer implementations and handlers.
- `src/routes/` — FastAPI routes for telemetry, devices, alerts and external sources.
- `src/scripts/` — small simulators (device telemetry, external source events) to exercise the system locally.
