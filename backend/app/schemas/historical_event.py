"""Pydantic schemas for Historical Events responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class HistoricalEventResponse(BaseModel):
    id: int = Field(..., description="Unique event ID", example=1)
    well_id: int = Field(..., description="Parent well ID", example=2)
    depth: float = Field(..., description="Measured depth of incident in meters", example=2980.0)
    formation: Optional[str] = Field(None, description="Formation name where event occurred", example="Demo-Barail")
    event_type: str = Field(..., description="Incident category", example="MUD_LOSS")
    severity: str = Field(..., description="Severity level (LOW, MEDIUM, HIGH, CRITICAL)", example="HIGH")
    description: str = Field(..., description="Operational incident description")
    cause: Optional[str] = Field(None, description="Identified root cause")
    mitigation: Optional[str] = Field(None, description="Remedial action taken")
    event_time: datetime = Field(..., description="Timestamp of incident")

    model_config = ConfigDict(from_attributes=True)


class WellHistoryEvent(BaseModel):
    id: int = Field(..., description="Event ID", example=1)
    depth: float = Field(..., description="Depth in meters", example=2980.0)
    formation: Optional[str] = Field(None, description="Formation name", example="Demo-Barail")
    event_type: str = Field(..., description="Event category", example="MUD_LOSS")
    severity: str = Field(..., description="Severity", example="HIGH")
    description: str = Field(..., description="Description")
    cause: Optional[str] = Field(None, description="Cause")
    mitigation: Optional[str] = Field(None, description="Mitigation")
    event_time: datetime = Field(..., description="Event timestamp")

    model_config = ConfigDict(from_attributes=True)
