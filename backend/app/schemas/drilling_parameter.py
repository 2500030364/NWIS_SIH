"""Pydantic schemas for Drilling Parameters (Telemetry) responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TelemetryResponse(BaseModel):
    id: Optional[int] = Field(None, description="Record ID")
    well_id: int = Field(..., description="Parent well ID", example=4)
    recorded_at: datetime = Field(..., description="Sensor timestamp")
    measured_depth: float = Field(..., description="Measured depth in meters", example=3520.0)
    torque: float = Field(..., description="Rotary torque in kNm", example=39.51)
    wob: float = Field(..., description="Weight on bit in klbf", example=18.5)
    rop: float = Field(..., description="Rate of penetration in m/hr", example=3.24)
    rpm: float = Field(..., description="Rotary speed in RPM", example=58.94)
    mud_flow: float = Field(..., description="Pump flow rate in L/min", example=2148.74)
    mud_weight: float = Field(..., description="Drilling fluid specific gravity (SG)", example=1.33)
    standpipe_pressure: float = Field(..., description="Standpipe pressure (SPP) in psi", example=2632.79)

    model_config = ConfigDict(from_attributes=True)


class ActiveTelemetryResponse(BaseModel):
    well_id: int = Field(..., description="Active demonstration well ID", example=25)
    well_name: str = Field(..., description="Active well name", example="NWIS-W025")
    timestamp: datetime = Field(..., description="Current simulated telemetry timestamp")
    measured_depth: float = Field(..., description="Current drilled depth in meters", example=3600.0)
    torque: float = Field(..., description="Surface torque in kNm", example=25.51)
    wob: float = Field(..., description="Weight on bit in klbf", example=20.67)
    rop: float = Field(..., description="Rate of penetration in m/hr", example=12.68)
    rpm: float = Field(..., description="Rotary speed in RPM", example=96.44)
    mud_flow: float = Field(..., description="Circulation flow rate in L/min", example=2422.31)
    mud_weight: float = Field(..., description="Active mud density in SG", example=1.22)
    standpipe_pressure: float = Field(..., description="Standpipe pressure in psi", example=2280.87)
    is_simulated: bool = Field(True, description="Flag indicating simulated demonstration data")
    disclaimer: str = Field(
        "Simulated demonstration telemetry for SIH prototype. NOT actual OIL or ONGC operational data.",
        description="Data disclaimer"
    )

    model_config = ConfigDict(from_attributes=True)
