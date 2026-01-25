# telemetry route using DB model connect() accessors
from fastapi import APIRouter, HTTPException

from kafka_client import KAFKA_TOPICS
from producer import Producer
from topic import Topic
from models import TelemetryIn
from db_models import DeviceModel, DeviceTypeModel, TelemetryModel
from utils import validate_telemetry_schema
# Using kafka client manager to allow real Kafka or mock fallback
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/telemetry")
async def ingest_telemetry(payload: TelemetryIn):
    try:
        device = await DeviceModel.connect().find_one({"_id": ObjectId(payload.device_id)})
        if not device:
            raise HTTPException(status_code=404, detail="device not found")
        if device.get("status") != "ON":
            return {"ignored": True}

        # fetch device type
        device_type = await DeviceTypeModel.connect().find_one({"_id": ObjectId(device["device_type_id"])})
        if not device_type:
            raise HTTPException(status_code=500, detail="device type missing")

        ok, err = validate_telemetry_schema(device_type.get("attributes", {}), payload.data)
        if not ok:
            raise HTTPException(status_code=400, detail=err)

        doc = {
            "device_id": device["_id"],
            "data": payload.data,
            "telemetry_sent_on": payload.telemetry_sent_on,
            "created_at": datetime.utcnow(),
        }
        res = await TelemetryModel.connect().insert_one(doc)
        producer = Producer("localhost:7092")
        await producer.start()
        external_source_topic = Topic(KAFKA_TOPICS.get("fetch_external_source"), producer=producer)
        await external_source_topic.publish({
            "meta": {
                "event": {
                    "topic": external_source_topic.name,
                    "name": "fetch_external_source",
                    "version": "v1.0",
                    "type": "fetch"
                }
            },
            "payload": {
                "telemetry_id": str(res.inserted_id),
                "device_id": str(device["_id"]),
                "telemetry_sent_on": payload.telemetry_sent_on.isoformat(),
                "data": payload.data,
            }
        })

        validate_alerts_topic = Topic(KAFKA_TOPICS.get("alert_validator"), producer=producer)
        await validate_alerts_topic.publish({
            "meta": {
                "event": {
                    "topic": validate_alerts_topic.name,
                    "name": "validate_alerts",
                    "version": "v1.0",
                    "type": "validate"
                }
            },
            "payload": {
                "telemetry_id": str(res.inserted_id),
                "device_id": str(device["_id"]),
                "telemetry_sent_on": payload.telemetry_sent_on.isoformat(),
                "data": payload.data,
            }
        })

        await producer.stop()
        return {"ok": True, "telemetry_id": str(res.inserted_id)}
    except Exception:
        raise HTTPException(status_code=500, detail="internal server error")