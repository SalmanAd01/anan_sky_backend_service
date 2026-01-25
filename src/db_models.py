from pydantic import Field
from typing import Optional, Dict, Any, Any as AnyType
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from db import get_db
from bson import ObjectId


class MongoModel(AsyncIOMotorCollection):
    COLLECTION: str  # overridden in subclasses

    @classmethod
    def connect(cls) -> AnyType:
        if not getattr(cls, "COLLECTION", None):
            raise RuntimeError(f"Model {cls.__name__} missing COLLECTION attribute")
        db = get_db()
        return getattr(db, cls.COLLECTION)



class DeviceTypeModel(MongoModel):
    COLLECTION: str = "device_types"
    _id: Optional[ObjectId] = Field(None, alias="_id")
    name: str
    attributes: Dict[str, Dict[str, Any]]
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} if 'ObjectId' in globals() else {}
        allow_population_by_field_name = True



class DeviceModel(MongoModel):
    _id: Optional[ObjectId] = Field(None, alias="_id")
    device_type_id: ObjectId
    name: str
    device_code: str
    communication_type: str
    status: str
    device_url: Optional[str] = None
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} if 'ObjectId' in globals() else {}
        allow_population_by_field_name = True

    COLLECTION: str = "devices"


class TelemetryModel(MongoModel):
    _id: Optional[ObjectId] = Field(None, alias="_id")
    device_id: ObjectId
    data: Dict[str, Any]
    telemetry_sent_on: datetime
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} if 'ObjectId' in globals() else {}
        allow_population_by_field_name = True

    COLLECTION: str = "device_telemetry"


class DeviceAlertRuleModel(MongoModel):
    _id: Optional[ObjectId] = Field(None, alias="_id")
    device_id: ObjectId
    name: str
    condition: str
    severity: str
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} if 'ObjectId' in globals() else {}
        allow_population_by_field_name = True

    COLLECTION: str = "device_alert_rules"


class AlertModel(MongoModel):
    _id: Optional[ObjectId] = Field(None, alias="_id")
    device_id: ObjectId
    alert_name: str
    severity: str
    value: Dict[str, Any]
    triggered_at: datetime
    status: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} if 'ObjectId' in globals() else {}
        allow_population_by_field_name = True

    COLLECTION: str = "alerts"


class ExternalSourceTypeModel(MongoModel):
    _id: Optional[ObjectId] = Field(None, alias="_id")
    name: str
    attributes: Dict[str, Dict[str, Any]]
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} if 'ObjectId' in globals() else {}
        allow_population_by_field_name = True

    COLLECTION: str = "external_source_types"


class ExternalSourceModel(MongoModel):
    _id: Optional[ObjectId] = Field(None, alias="_id")
    source_type_id: ObjectId
    name: str
    source_kind: str
    endpoint_url: Optional[str]
    status: str
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} if 'ObjectId' in globals() else {}
        allow_population_by_field_name = True

    COLLECTION: str = "external_sources"


class ExternalSourceTelemetryModel(MongoModel):
    _id: Optional[ObjectId] = Field(None, alias="_id")
    source_id: ObjectId
    data: Dict[str, Any]
    requested_for: datetime
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} if 'ObjectId' in globals() else {}
        allow_population_by_field_name = True

    COLLECTION: str = "external_source_telemetry"


class DeviceExternalSourceModel(MongoModel):
    _id: Optional[ObjectId] = Field(None, alias="_id")
    device_id: ObjectId
    source_id: ObjectId
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} if 'ObjectId' in globals() else {}
        allow_population_by_field_name = True

    COLLECTION: str = "device_external_sources"


class DeviceCommandModel(MongoModel):
    _id: Optional[ObjectId] = Field(None, alias="_id")
    device_id: ObjectId
    command: str
    status: str
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} if 'ObjectId' in globals() else {}
        allow_population_by_field_name = True

    COLLECTION: str = "device_commands"
