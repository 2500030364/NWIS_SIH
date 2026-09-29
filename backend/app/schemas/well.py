"""Pydantic schemas for Well responses."""

from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class WellBase(BaseModel):
    well_name: str = Field(..., description="Unique well identifier", example="NWIS-W001")
    latitude: float = Field(..., description="Latitude in decimal degrees", example=27.38199)
    longitude: float = Field(..., description="Longitude in decimal degrees", example=95.40971)
    total_depth: float = Field(..., description="Total target or drilled depth in meters", example=3561.82)
    status: str = Field(..., description="Operational status (ACTIVE, COMPLETED, DRILLING, SUSPENDED)", example="COMPLETED")
    spud_date: date = Field(..., description="Date drilling began", example="2021-08-13")
    field_name: str = Field(..., description="Field or block name", example="Demo-Dihing Basin (Fictional Field)")


class WellResponse(WellBase):
    id: int = Field(..., description="Unique well ID", example=1)

    model_config = ConfigDict(from_attributes=True)


class NearbyWellResponse(BaseModel):
    well_id: int = Field(..., description="Well ID", example=2)
    well_name: str = Field(..., description="Well Name", example="NWIS-W002")
    latitude: float = Field(..., description="Latitude", example=27.390381)
    longitude: float = Field(..., description="Longitude", example=95.348599)
    distance_km: float = Field(..., description="Distance in kilometers from query point", example=6.12)
    total_depth: float = Field(..., description="Total depth in meters", example=3397.22)
    status: str = Field(..., description="Current status", example="COMPLETED")
    field_name: Optional[str] = Field(None, description="Field name")

    model_config = ConfigDict(from_attributes=True)


class WellDetailResponse(WellResponse):
    """Detailed response for a specific well."""
    pass


class OffsetRelevanceItem(BaseModel):
    well_id: int
    well_name: str
    latitude: float
    longitude: float
    distance_km: float
    total_depth: float
    status: str
    relevance_level: str = Field(..., description="HIGH, MEDIUM, or LOW")
    relevance_score: int = Field(..., description="Relevance score from 0 to 100")
    reasons: list[str] = Field(default_factory=list, description="List of reasons why this well is relevant")
    shared_formation: Optional[str] = None
    comparable_events_count: int = 0


class DrillAheadZoneEvent(BaseModel):
    well_id: int
    well_name: str
    distance_km: float
    depth: float
    formation_name: str
    event_type: str
    severity: str
    description: str
    mitigation: Optional[str] = None
    source_document: Optional[str] = None


class DrillAheadZone(BaseModel):
    depth_start: float
    depth_end: float
    formation_name: str
    status: str = Field(..., description="'CURRENT_BIT', 'CLEAR', 'WATCH', or 'HAZARD_ZONE'")
    concentration: str = Field(..., description="'NONE', 'LOW', 'MODERATE', or 'CONCENTRATED'")
    event_count: int
    summary: str
    events: list[DrillAheadZoneEvent] = Field(default_factory=list)


class DrillAheadResponse(BaseModel):
    active_well_id: int
    active_well_name: str
    current_depth: float
    current_formation: str
    lookahead_m: float
    zones: list[DrillAheadZone]


class WellComparisonResponse(BaseModel):
    active_well: dict
    offset_well: dict
    formation_comparison: dict
    telemetry_comparison: dict
    historical_events: list[dict]
    historical_mitigations: list[dict]

