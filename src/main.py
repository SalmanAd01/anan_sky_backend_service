from fastapi import FastAPI
from routes import device_types, devices, telemetry, alerts, external_sources
from config import MODE

app = FastAPI(title="Telemetry Platform")

app.include_router(device_types.router)
app.include_router(devices.router)
app.include_router(telemetry.router)
app.include_router(alerts.router)
app.include_router(external_sources.router)

@app.get("/")
async def root():
    return {"ok": True}


def run_consumer():
    import asyncio
    from config import (
        KAFKA_BOOTSTRAP_SERVERS,
        KAFKA_GROUP_ID,
        CONSUMER_TYPE,
    )
    from consumers.runner import KafkaConsumerRunner

    mapping_cls = None

    if CONSUMER_TYPE == "fetch_external_source":
        from consumers.external_source.config import (
            FetchExternalSourceTopicActionMapping,
        )
        mapping_cls = FetchExternalSourceTopicActionMapping
    elif CONSUMER_TYPE == "alert_evaluator":
        from consumers.validate_alerts.config import (
            ValidateAlertsTopicActionMapping,
        )
        mapping_cls = ValidateAlertsTopicActionMapping
    else:
        raise ValueError(f"Unknown CONSUMER_TYPE: {CONSUMER_TYPE}")

    asyncio.run(
        KafkaConsumerRunner(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=KAFKA_GROUP_ID,
            mapping_cls=mapping_cls,
        ).start()
    )


if __name__ == "__main__":
    if MODE == "consumer":
        run_consumer()
