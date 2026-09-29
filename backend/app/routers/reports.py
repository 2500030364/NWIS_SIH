"""
===============================================================================
NWIS Backend - Reports Router
===============================================================================
Exposes endpoints for querying operational drilling reports from PostgreSQL.
===============================================================================
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.report import Report
from app.models.well import Well
from app.schemas.report import ReportResponse

router = APIRouter(prefix="/api/reports", tags=["Operational Reports"])


@router.get(
    "",
    response_model=List[ReportResponse],
    summary="List operational drilling reports",
    description="Retrieve operational reports (DDR, WCR, Mud Logs, Completion Reports) from PostgreSQL with optional filtering."
)
def get_reports(
    well_id: Optional[int] = Query(None, description="Filter by well ID"),
    report_type: Optional[str] = Query(None, description="Filter by report type (e.g. DDR, WCR, MUD_LOG)"),
    search: Optional[str] = Query(None, description="Search keyword in report name or text"),
    limit: int = Query(default=50, ge=1, le=200, description="Max reports to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    query = (
        db.query(Report, Well.well_name)
        .join(Well, Report.well_id == Well.id)
    )

    if well_id is not None:
        query = query.filter(Report.well_id == well_id)
    if report_type and report_type.upper() != "ALL":
        query = query.filter(Report.report_type.ilike(report_type.strip()))
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (Report.report_name.ilike(search_term)) |
            (Report.extracted_text.ilike(search_term))
        )

    results = query.order_by(Report.report_date.desc(), Report.id.desc()).offset(offset).limit(limit).all()

    response = []
    for rep, w_name in results:
        excerpt = rep.extracted_text[:280] + "..." if rep.extracted_text and len(rep.extracted_text) > 280 else rep.extracted_text
        response.append(
            ReportResponse(
                id=rep.id,
                well_id=rep.well_id,
                well_name=w_name,
                report_name=rep.report_name,
                report_type=rep.report_type,
                file_path=rep.file_path,
                report_date=rep.report_date,
                excerpt=excerpt,
                extracted_text=rep.extracted_text,
                created_at=rep.created_at
            )
        )

    return response


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report details",
    description="Retrieve full report text and metadata by report ID."
)
def get_report(report_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(Report, Well.well_name)
        .join(Well, Report.well_id == Well.id)
        .filter(Report.id == report_id)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id {report_id} not found."
        )

    rep, w_name = result
    excerpt = rep.extracted_text[:280] + "..." if rep.extracted_text and len(rep.extracted_text) > 280 else rep.extracted_text

    return ReportResponse(
        id=rep.id,
        well_id=rep.well_id,
        well_name=w_name,
        report_name=rep.report_name,
        report_type=rep.report_type,
        file_path=rep.file_path,
        report_date=rep.report_date,
        excerpt=excerpt,
        extracted_text=rep.extracted_text,
        created_at=rep.created_at
    )
