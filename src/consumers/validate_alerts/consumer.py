import logging
from datetime import datetime

from bson import ObjectId
from db_models import AlertModel, DeviceAlertRuleModel
from utils import safe_eval_condition



class ValidateAlertsHandler:
    async def run(self, payload, meta):
        if not payload:
            return
        topic = meta.get("topic") or meta.get("topic_name")
        print("ValidateAlertsHandler starting, subscribing to topic %s" % getattr(topic, 'name', '<unknown>'))
        try:
            print("ValidateAlertsHandler received message for device %s" % payload.get("device_id"))
            device_id = payload.get("device_id")
            data = payload.get("data", {})
            rules_cursor = DeviceAlertRuleModel.connect().find({"device_id": ObjectId(device_id)})
            async for rule in rules_cursor:
                try:
                    matches = safe_eval_condition(rule["condition"], data)
                except Exception:
                    matches = False
                if matches:
                    await AlertModel.connect().insert_one({
                        "device_id": ObjectId(device_id),
                        "alert_name": rule.get("name"),
                        "severity": rule.get("severity"),
                        "value": {"evaluated_at": datetime.utcnow(), "data": data},
                        "triggered_at": datetime.utcnow(),
                        "status": "OPEN",
                    })
        except Exception:
            print("unexpected error in alert evaluator consumer for device %s" % (payload and payload.get("device_id")))
