from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from typing import List

from models import (
    ExternalSourceTypeCreate,
    ExternalSourceCreate,
    ExternalSourceTelemetryCreate,
    DeviceExternalSourceCreate,
)
from db_models import (
    ExternalSourceTypeModel,
    ExternalSourceModel,
    ExternalSourceTelemetryModel,
    DeviceExternalSourceModel,
    DeviceModel,
)
from utils import serialize_mongo

router = APIRouter()


@router.post("/external-source-types")
async def create_external_source_type(payload: ExternalSourceTypeCreate):
    try:
        doc = payload.dict()
        doc["created_at"] = datetime.now()
        res = await ExternalSourceTypeModel.connect().insert_one(doc)
        created = await ExternalSourceTypeModel.connect().find_one({"_id": res.inserted_id})
        created["_id"] = str(created["_id"])
        return created
    except Exception:
        raise HTTPException(status_code=500, detail="internal server error")


@router.post("/external-sources")
async def create_external_source(payload: ExternalSourceCreate):
    try:
        try:
            st_obj = ObjectId(payload.source_type_id)
        except Exception:
            raise HTTPException(status_code=400, detail="invalid source_type_id format")

        existing = await ExternalSourceTypeModel.connect().find_one({"_id": st_obj})
        if not existing:
            raise HTTPException(status_code=400, detail="source_type_id does not exist")

        doc = payload.dict()
        doc["source_type_id"] = st_obj
        doc["status"] = "ACTIVE"
        doc["created_at"] = datetime.now()
        res = await ExternalSourceModel.connect().insert_one(doc)
        created = await ExternalSourceModel.connect().find_one({"_id": res.inserted_id})
        created["_id"] = str(created["_id"])
        created["source_type_id"] = str(created["source_type_id"]) if created.get("source_type_id") else None
        return created
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal server error")

@router.post("/device-external-sources")
async def link_device_to_external_source(payload: DeviceExternalSourceCreate):
    try:
        try:
            d_obj = ObjectId(payload.device_id)
            s_obj = ObjectId(payload.source_id)
        except Exception:
            raise HTTPException(status_code=400, detail="invalid id format")

        device = await DeviceModel.connect().find_one({"_id": d_obj})
        if not device:
            raise HTTPException(status_code=404, detail="device not found")
        source = await ExternalSourceModel.connect().find_one({"_id": s_obj})
        if not source:
            raise HTTPException(status_code=404, detail="source not found")

        doc = {
            "device_id": d_obj,
            "source_id": s_obj,
            "created_at": datetime.now(),
        }
        res = await DeviceExternalSourceModel.connect().insert_one(doc)
        created = await DeviceExternalSourceModel.connect().find_one({"_id": res.inserted_id})
        created["_id"] = str(created["_id"])
        created["device_id"] = str(created["device_id"]) if created.get("device_id") else None
        created["source_id"] = str(created["source_id"]) if created.get("source_id") else None
        return created
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="internal server error")
