import logging
from bson import ObjectId
import httpx
from datetime import datetime
from db_models import DeviceExternalSourceModel, ExternalSourceModel, ExternalSourceTelemetryModel



class FetchExternalSourceHandler:
    """Consume telemetry events and call external sources configured for the device."""

    async def run(self, payload, meta):
        topic_name = meta.get("topic") or meta.get("topic_name")
        print("ExternalEnrichmentConsumer starting, processing payload from topic %s" % topic_name)
        try:
            msg = payload
            if not msg:
                print("ExternalEnrichmentConsumer received empty payload, skipping")
                return

            print("ExternalEnrichmentConsumer received message for device %s" % msg.get("device_id"))
            device_id = msg.get("device_id")
            telemetry_sent_on = msg.get("telemetry_sent_on")

            mappings_cursor = DeviceExternalSourceModel.connect().find({"device_id": ObjectId(device_id)})
            async for m in mappings_cursor:
                try:
                    src = await ExternalSourceModel.connect().find_one({"_id": m["source_id"]})
                    if not src or src.get("status") != "ACTIVE":
                        continue
                    if src.get("source_kind") != "api":
                        continue

                    endpoint = src.get("endpoint_url")
                    params = {"created_on": telemetry_sent_on}

                    async with httpx.AsyncClient(timeout=5.0) as client:
                        r = await client.get(f"{endpoint}/{src.get("source_type_id")}/data", params=params)

                    if r.status_code == 200:
                        try:
                            data = r.json()
                        except Exception:
                            print("failed to decode JSON from external source %s" % endpoint)
                            continue

                        await ExternalSourceTelemetryModel.connect().insert_one({
                            "source_id": src["_id"],
                            "data": data,
                            "requested_for": telemetry_sent_on,
                            "created_at": datetime.utcnow(),
                        })
                except Exception:
                    print("external source fetch failed for device %s" % device_id)
                    continue
        except Exception:
            print("unexpected error in external enrichment consumer run")
