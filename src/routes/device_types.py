from fastapi import APIRouter, HTTPException
from models import DeviceTypeCreate
from datetime import datetime
from db_models import DeviceTypeModel
from utils import serialize_mongo

router = APIRouter()


@router.post("/device-types")
async def create_device_type(payload: DeviceTypeCreate):
    doc = payload.dict()
    doc["created_at"] = datetime.now()
    res = await DeviceTypeModel.connect().insert_one(doc)
    created = await DeviceTypeModel.connect().find_one({"_id": res.inserted_id})
    created["_id"] = str(created["_id"])
    return created

@router.get("/device-types")
async def list_device_types():
    res = await DeviceTypeModel.connect().find().to_list(length=None)
    return serialize_mongo(res)
