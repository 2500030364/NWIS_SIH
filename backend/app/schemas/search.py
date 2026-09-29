"""Pydantic schemas for Semantic Search responses."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class SearchResultItem(BaseModel):
    score: float = Field(..., description="Cosine similarity score (0 to 1)", example=0.82)
    well_name: str = Field(..., description="Associated well identifier", example="NWIS-W002")
    report_name: str = Field(..., description="Report filename", example="NWIS-W002_Daily_Drilling_Report_Mud_Loss.pdf")
    report_type: Optional[str] = Field("GENERAL_REPORT", description="Report category (DDR, WCR, MUD_LOG, INCIDENT_REPORT)", example="DDR")
    page: int = Field(1, description="Page number where text was found", example=1)
    text: str = Field(..., description="Relevant report excerpt")
    event_type: Optional[str] = Field(None, description="Drilling hazard category if detected", example="MUD_LOSS")
    formation: Optional[str] = Field(None, description="Geological formation name if detected", example="Demo-Barail")
    depth: Optional[float] = Field(None, description="Measured depth in meters if detected", example=2980.0)
    severity: Optional[str] = Field(None, description="Severity level if detected", example="HIGH")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional document chunk metadata")

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    query: str = Field(..., description="Search query submitted", example="stuck pipe in Demo-Barail around 3000m")
    total_results: int = Field(..., description="Number of matching excerpts returned", example=3)
    results: List[SearchResultItem] = Field(..., description="Ranked list of relevant excerpts")

    model_config = ConfigDict(from_attributes=True)
