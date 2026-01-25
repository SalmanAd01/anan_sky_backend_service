from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from typing import List

from db import get_db
from models import AlertCreate, AlertStatusUpdate, DeviceAlertRuleCreate
from db_models import AlertModel, DeviceModel, DeviceAlertRuleModel

router = APIRouter()


@router.post("/device-alert-rules")
async def create_device_alert_rule(payload: DeviceAlertRuleCreate):
    try:
        try:
            dev_obj = ObjectId(payload.device_id)
        except Exception:
            raise HTTPException(status_code=400, detail="invalid device_id format")

        existing = await DeviceModel.connect().find_one({"_id": dev_obj})
        if not existing:
            raise HTTPException(status_code=404, detail="device not found")

        doc = {
            "device_id": dev_obj,
            "name": payload.name,
            "condition": payload.condition,
            "severity": payload.severity,
            "created_at": datetime.utcnow(),
        }
        res = await DeviceAlertRuleModel.connect().insert_one(doc)
        created = await DeviceAlertRuleModel.connect().find_one({"_id": res.inserted_id})
        if created and "_id" in created:
            created["_id"] = str(created["_id"])
        if created and "device_id" in created:
            created["device_id"] = str(created["device_id"])
        return created
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal server error")


@router.get("/device-alert-rules")
async def list_device_alert_rules(device_id: str | None = None):
    try:
        query = {}
        if device_id:
            try:
                query["device_id"] = ObjectId(device_id)
            except Exception:
                raise HTTPException(status_code=400, detail="invalid device_id format")
        res = []
        async for r in DeviceAlertRuleModel.connect().find(query).sort("created_at", -1):
            r["_id"] = str(r["_id"])
            r["device_id"] = str(r["device_id"]) if r.get("device_id") else None
            res.append(r)
        return res
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal server error")


@router.delete("/device-alert-rules/{rule_id}")
async def delete_device_alert_rule(rule_id: str):
    try:
        try:
            rid = ObjectId(rule_id)
        except Exception:
            raise HTTPException(status_code=400, detail="invalid rule id format")
        res = await DeviceAlertRuleModel.connect().delete_one({"_id": rid})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="rule not found")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal server error")


@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    try:
        try:
            aobj = ObjectId(alert_id)
        except Exception:
            raise HTTPException(status_code=400, detail="invalid alert id format")
        alert = await AlertModel.connect().find_one({"_id": aobj})
        if not alert:
            raise HTTPException(status_code=404, detail="alert not found")
        alert["_id"] = str(alert["_id"])
        alert["device_id"] = str(alert["device_id"]) if alert.get("device_id") else None
        return alert
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal server error")


@router.get("/alerts")
async def list_alerts(device_id: str | None = None) -> List[dict]:
    try:
        query = {}
        if device_id:
            try:
                query["device_id"] = ObjectId(device_id)
            except Exception:
                raise HTTPException(status_code=400, detail="invalid device_id format")
        res = []
        async for a in AlertModel.connect().find(query).sort("triggered_at", -1):
            a["_id"] = str(a["_id"])
            a["device_id"] = str(a["device_id"]) if a.get("device_id") else None
            res.append(a)
        return res
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal server error")
