"""Pydantic schemas for Knowledge Assistant."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AssistantQueryRequest(BaseModel):
    query: str = Field(..., description="Drilling question in plain English", example="What happened in nearby wells around 3000m in Demo-Barail?")
    active_well_id: Optional[int] = Field(1, description="Active well ID for context")
    current_depth: Optional[float] = Field(3020.0, description="Current bit depth in meters")
    radius_km: Optional[float] = Field(20.0, description="Search radius in kilometers")


class AssistantCaseItem(BaseModel):
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
    source_page: Optional[int] = None


class AssistantCitationItem(BaseModel):
    document_name: str
    file_path: str
    page_number: int
    well_name: str
    excerpt: str


class AssistantQueryResponse(BaseModel):
    query: str
    cases_found: int
    answer_summary: str
    cases: List[AssistantCaseItem]
    citations: List[AssistantCitationItem]
    disclaimer: str = "Source-grounded historical decision support. Not an autonomous operational recommendation."
