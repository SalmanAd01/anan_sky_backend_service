from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime


class DeviceTypeCreate(BaseModel):
    name: str
    attributes: Dict[str, Dict[str, Any]] = Field(...)


class DeviceCreate(BaseModel):
    device_type_id: str
    name: str
    device_code: str
    communication_type: str
    device_url: str


class TelemetryIn(BaseModel):
    device_id: str
    telemetry_sent_on: datetime
    data: Dict[str, Any]


class CommandIn(BaseModel):
    command: str


class AlertCreate(BaseModel):
    device_id: str
    alert_name: str
    severity: str
    value: Dict[str, Any]
    triggered_at: datetime | None = None
    status: str = "OPEN"


class AlertStatusUpdate(BaseModel):
    status: str


class DeviceAlertRuleCreate(BaseModel):
    device_id: str
    name: str
    condition: str
    severity: str


class ExternalSourceTypeCreate(BaseModel):
    name: str
    attributes: Dict[str, Dict[str, Any]]


class ExternalSourceCreate(BaseModel):
    source_type_id: str
    name: str
    source_kind: str
    endpoint_url: str | None = None


class ExternalSourceTelemetryCreate(BaseModel):
    source_id: str
    data: Dict[str, Any]
    requested_for: datetime | None = None


class DeviceExternalSourceCreate(BaseModel):
    device_id: str
    source_id: str
