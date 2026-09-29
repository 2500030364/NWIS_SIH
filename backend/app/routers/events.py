"""
===============================================================================
NWIS Backend - Historical Events Router
===============================================================================
Exposes endpoints for querying historical drilling incidents, hazards, causes,
and engineering mitigations across offset wells.
===============================================================================
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.historical_event import HistoricalEvent
from app.models.formation import Formation
from app.schemas.historical_event import HistoricalEventResponse

router = APIRouter(prefix="/api/events", tags=["Historical Events"])


@router.get(
    "",
    response_model=List[HistoricalEventResponse],
    summary="Search historical drilling events",
    description=(
        "Retrieve categorized historical drilling events (e.g. MUD_LOSS, STUCK_PIPE, KICK) "
        "with optional multi-parameter filtering across wells, formations, depth ranges, and severity levels."
    )
)
def get_events(
    well_id: Optional[int] = Query(None, description="Filter by parent well ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g. MUD_LOSS, STUCK_PIPE, KICK)"),
    severity: Optional[str] = Query(None, description="Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)"),
    formation: Optional[str] = Query(None, description="Filter by geological formation name"),
    min_depth: Optional[float] = Query(None, ge=0.0, description="Minimum depth in meters"),
    max_depth: Optional[float] = Query(None, ge=0.0, description="Maximum depth in meters"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db)
):
    if min_depth is not None and max_depth is not None and min_depth > max_depth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_depth cannot be greater than max_depth."
        )

    query = (
        db.query(HistoricalEvent, Formation.formation_name)
        .outerjoin(Formation, HistoricalEvent.formation_id == Formation.id)
    )

    if well_id is not None:
        query = query.filter(HistoricalEvent.well_id == well_id)
    if event_type:
        query = query.filter(HistoricalEvent.event_type.ilike(event_type.strip()))
    if severity:
        query = query.filter(HistoricalEvent.severity.ilike(severity.strip()))
    if formation:
        query = query.filter(Formation.formation_name.ilike(f"%{formation.strip()}%"))
    if min_depth is not None:
        query = query.filter(HistoricalEvent.depth >= min_depth)
    if max_depth is not None:
        query = query.filter(HistoricalEvent.depth <= max_depth)

    results = query.order_by(HistoricalEvent.event_time.desc(), HistoricalEvent.depth.asc()).limit(limit).all()

    response = []
    for ev, form_name in results:
        response.append(
            HistoricalEventResponse(
                id=ev.id,
                well_id=ev.well_id,
                depth=float(ev.depth),
                formation=form_name,
                event_type=ev.event_type,
                severity=ev.severity,
                description=ev.description,
                cause=ev.cause,
                mitigation=ev.mitigation,
                event_time=ev.event_time
            )
        )
    return response


@router.get(
    "/count",
    summary="Get total count of historical events",
    description="Retrieve the total number of historical drilling events stored in the database."
)
def get_events_count(db: Session = Depends(get_db)):
    total = db.query(HistoricalEvent).count()
    return {"count": total}


@router.get(
    "/{event_id}",
    response_model=HistoricalEventResponse,
    summary="Get single historical event details",
    description="Retrieve full engineering narrative, root cause, and mitigation for a specific historical event by ID."
)
def get_event(event_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(HistoricalEvent, Formation.formation_name)
        .outerjoin(Formation, HistoricalEvent.formation_id == Formation.id)
        .filter(HistoricalEvent.id == event_id)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historical event with id {event_id} not found."
        )

    ev, form_name = result
    return HistoricalEventResponse(
        id=ev.id,
        well_id=ev.well_id,
        depth=float(ev.depth),
        formation=form_name,
        event_type=ev.event_type,
        severity=ev.severity,
        description=ev.description,
        cause=ev.cause,
        mitigation=ev.mitigation,
        event_time=ev.event_time
    )
