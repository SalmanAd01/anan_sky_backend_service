from fastapi import APIRouter, HTTPException, Depends
from models import DeviceCreate, CommandIn
from datetime import datetime
from bson import ObjectId
import httpx
from db_models import (
    AlertModel,
    DeviceModel,
    DeviceTypeModel,
    DeviceCommandModel,
    TelemetryModel,
    DeviceExternalSourceModel,
    ExternalSourceTelemetryModel,
    DeviceAlertRuleModel,
)
from utils import serialize_mongo

router = APIRouter()


@router.post("/devices")
async def create_device(payload: DeviceCreate):
    try:
        type_obj_id = ObjectId(payload.device_type_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid device_type_id format")

    existing = await DeviceTypeModel.connect().find_one({"_id": type_obj_id})
    if not existing:
        raise HTTPException(status_code=400, detail="device_type_id does not exist")
    doc = payload.dict()
    doc["status"] = "ON"
    doc["created_at"] = datetime.now()
    res = await DeviceModel.connect().insert_one(doc)
    created = await DeviceModel.connect().find_one({"_id": res.inserted_id})
    created["_id"] = str(created["_id"])
    return created


@router.post("/devices/{device_id}/command")
async def device_command(device_id: str, cmd: CommandIn):
    device = await DeviceModel.connect().find_one({"_id": ObjectId(device_id)})
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    if cmd.command not in ("ON", "OFF"):
        raise HTTPException(status_code=400, detail="invalid command")
    await DeviceModel.connect().update_one({"_id": device["_id"]}, {"$set": {"status": cmd.command}})
    await DeviceCommandModel.connect().insert_one({
        "device_id": device["_id"],
        "command": cmd.command,
        "status": "ACKNOWLEDGED",
        "created_at": datetime.now(),
    })
    # If device_url is present, POST the command to that URL. Failures are non-fatal.
    device_url = device.get("device_url")
    if device_url:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(device_url, json={"command": cmd.command})
        except Exception:
            # Don't fail the API call if device is unreachable.
            pass
    return {"ok": True}


@router.get("/devices/{device_id}/data")
async def get_device_dashboard(device_id: str):
    device = await DeviceModel.connect().find_one({"_id": ObjectId(device_id)})
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    device_type = await DeviceTypeModel.connect().find_one({"_id": ObjectId(device["device_type_id"])})
    all_telemetry = await TelemetryModel.connect().find({"device_id": ObjectId(device["_id"])}, sort=[("created_at", -1)]).to_list(length=None)
    # latest external telemetry
    ext = None
    mapping = await DeviceExternalSourceModel.connect().find_one({"device_id": ObjectId(device["_id"])})
    if mapping:
        ext = await ExternalSourceTelemetryModel.connect().find({"source_id": mapping["source_id"]}, sort=[("created_at", -1)]).to_list(length=None)
    all_alert = await AlertModel.connect().find({"device_id": ObjectId(device["_id"])}).to_list(length=None)
    
    
    return {
        "device": serialize_mongo(device),
        "device_type": serialize_mongo(device_type),
        "all_telemetry": serialize_mongo(all_telemetry),
        "all_external_telemetry": serialize_mongo(ext),
        "all_alert": serialize_mongo(all_alert),
    }


@router.get("/devices/type/{type_id}")
async def get_devices_by_type(type_id: str):
    res = []
    async for d in DeviceModel.connect().find({"device_type_id": type_id}):
        res.append(d)
    return res

@router.get("/devices/{device_id}")
async def get_device(device_id: str):
    device = await DeviceModel.connect().find_one({"_id": ObjectId(device_id)})
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    device_type = await DeviceTypeModel.connect().find_one({"_id": ObjectId(device["device_type_id"])})
    alert_configs = []
    async for r in DeviceAlertRuleModel.connect().find({"device_id": ObjectId(device["_id"])}):
        alert_configs.append(r)
    
    return {
        "device": serialize_mongo(device),
        "device_type": serialize_mongo(device_type),
        "alert_configs": serialize_mongo(alert_configs),
    }

@router.get("/devices")
async def list_devices():
    res = await DeviceModel.connect().find().to_list(length=None)
    return serialize_mongo(res)