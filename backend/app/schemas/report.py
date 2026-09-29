"""Pydantic schemas for reports."""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    well_id: int
    well_name: Optional[str] = None
    report_name: str
    report_type: str
    file_path: str
    report_date: date
    excerpt: Optional[str] = None
    extracted_text: Optional[str] = None
    created_at: datetime


class ReportListResponse(BaseModel):
    total_count: int
    reports: List[ReportResponse]
