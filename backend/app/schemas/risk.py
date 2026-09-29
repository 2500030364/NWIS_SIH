"""
===============================================================================
NWIS Backend - Risk Assessment & Alerts Schemas
===============================================================================
Pydantic v2 schemas for explainable drilling risk evaluation, offset-well
evidence aggregation, and operational alerts.
===============================================================================
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SupportingEvent(BaseModel):
    well_name: str
    well_id: int
    event_type: str
    depth: float
    severity: str
    description: str
    cause: Optional[str] = None
    mitigation: Optional[str] = None
    distance_km: float


class RiskAssessmentItem(BaseModel):
    risk_type: str = Field(..., description="Hazard category: MUD_LOSS, STUCK_PIPE, KICK, TORQUE_SPIKE, HIGH_PRESSURE, CEMENTING_ISSUE, LOST_CIRCULATION, NPT")
    title: str = Field(..., description="Human-friendly advisory title (e.g. 'Potential Mud Loss Risk')")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized risk score from 0.0 to 1.0")
    level: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH, CRITICAL")
    current_depth: float = Field(..., description="Current evaluated measured depth in meters")
    current_formation: str = Field(..., description="Current penetrated stratigraphic formation")
    historical_depth_interval: Optional[str] = Field(None, description="Depth range of nearby historical incidents (e.g. '2980m - 3040m')")
    explanation: str = Field(..., description="Clear human-readable explainability narrative")
    supporting_wells: List[str] = Field(default_factory=list, description="List of offset wells providing historical evidence")
    supporting_events: List[SupportingEvent] = Field(default_factory=list, description="Detailed records of historical incidents")
    telemetry_evidence: Optional[str] = Field(None, description="Sensor trend observation supporting the risk")
    recommended_mitigation: Optional[str] = Field(None, description="Operational recommendations to mitigate this hazard")


class WellRiskResponse(BaseModel):
    well_id: int
    well_name: str
    current_depth: float
    current_formation: str
    total_risks_assessed: int
    highest_risk_level: str
    risks: List[RiskAssessmentItem]
    disclaimer: str = "Prototype decision-support intelligence based on synthetic demonstration data. Does NOT guarantee drilling events."


class WellAlertsResponse(BaseModel):
    well_id: int
    well_name: str
    current_depth: float
    current_formation: str
    active_alert_count: int
    alerts: List[RiskAssessmentItem]
    disclaimer: str = "Prototype decision-support intelligence based on synthetic demonstration data."


class ActiveWellState(BaseModel):
    well_id: int
    well_name: str
    current_depth: float
    current_formation: str
    total_depth: float
    status: str
    active_alerts: int
    highest_severity: str
    last_updated: str
