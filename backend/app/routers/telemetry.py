"""
===============================================================================
NWIS Backend - Telemetry Router
===============================================================================
Exposes endpoints for depth-indexed sensor telemetry parameters (torque, WOB,
ROP, RPM, mud flow, mud weight, SPP) and a simulated active-well real-time stream.
===============================================================================
"""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.well import Well
from app.models.drilling_parameter import DrillingParameter
from app.schemas.drilling_parameter import TelemetryResponse, ActiveTelemetryResponse

router = APIRouter(prefix="/api/wells", tags=["Telemetry"])


@router.get(
    "/active/telemetry",
    response_model=ActiveTelemetryResponse,
    summary="Get simulated real-time telemetry for active well",
    description=(
        "Simulates a real-time drilling telemetry feed for a designated active/demo well "
        "(NWIS-W025) to power the upcoming Phase 3 dashboard. "
        "IMPORTANT: This is synthetic demonstration data and NOT real operational data."
    )
)
def get_active_telemetry(db: Session = Depends(get_db)):
    # Find active/drilling well (prefer well 25 or any well with status 'DRILLING')
    active_well = db.query(Well).filter(Well.status == "DRILLING").order_by(Well.id.desc()).first()
    if not active_well:
        active_well = db.query(Well).first()

    if not active_well:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No wells available to derive simulated telemetry."
        )

    # Fetch latest telemetry record for this well
    latest_record = (
        db.query(DrillingParameter)
        .filter(DrillingParameter.well_id == active_well.id)
        .order_by(DrillingParameter.measured_depth.desc())
        .first()
    )

    if latest_record:
        return ActiveTelemetryResponse(
            well_id=active_well.id,
            well_name=active_well.well_name,
            timestamp=datetime.now(timezone.utc),
            measured_depth=float(latest_record.measured_depth),
            torque=float(latest_record.torque),
            wob=float(latest_record.wob),
            rop=float(latest_record.rop),
            rpm=float(latest_record.rpm),
            mud_flow=float(latest_record.mud_flow),
            mud_weight=float(latest_record.mud_weight),
            standpipe_pressure=float(latest_record.standpipe_pressure),
            is_simulated=True,
            disclaimer="Simulated demonstration telemetry for SIH prototype. NOT actual OIL or ONGC operational data."
        )

    # Fallback default realistic values if no records exist
    return ActiveTelemetryResponse(
        well_id=active_well.id,
        well_name=active_well.well_name,
        timestamp=datetime.now(timezone.utc),
        measured_depth=3020.5,
        torque=18.4,
        wob=12.1,
        rop=8.3,
        rpm=95.0,
        mud_flow=420.0,
        mud_weight=1.18,
        standpipe_pressure=2100.0,
        is_simulated=True,
        disclaimer="Simulated demonstration telemetry for SIH prototype. NOT actual OIL or ONGC operational data."
    )


@router.get(
    "/{well_id}/telemetry",
    response_model=List[TelemetryResponse],
    summary="Get drilling telemetry parameters for a well",
    description=(
        "Retrieve historical high-frequency sensor telemetry records (torque, WOB, ROP, "
        "flow rate, standpipe pressure) for a specific well across an optional depth range."
    )
)
def get_well_telemetry(
    well_id: int,
    start_depth: Optional[float] = Query(None, ge=0.0, description="Starting measured depth in meters"),
    end_depth: Optional[float] = Query(None, ge=0.0, description="Ending measured depth in meters"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum telemetry records to return (capped at 1000)"),
    db: Session = Depends(get_db)
):
    # Verify well exists
    well = db.query(Well).filter(Well.id == well_id).first()
    if not well:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Well with id {well_id} not found."
        )

    if start_depth is not None and end_depth is not None and start_depth > end_depth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_depth cannot be greater than end_depth."
        )

    query = db.query(DrillingParameter).filter(DrillingParameter.well_id == well_id)

    if start_depth is not None:
        query = query.filter(DrillingParameter.measured_depth >= start_depth)
    if end_depth is not None:
        query = query.filter(DrillingParameter.measured_depth <= end_depth)

    records = query.order_by(DrillingParameter.measured_depth.asc()).limit(limit).all()

    return [
        TelemetryResponse(
            id=r.id,
            well_id=r.well_id,
            recorded_at=r.recorded_at,
            measured_depth=float(r.measured_depth),
            torque=float(r.torque),
            wob=float(r.wob),
            rop=float(r.rop),
            rpm=float(r.rpm),
            mud_flow=float(r.mud_flow),
            mud_weight=float(r.mud_weight),
            standpipe_pressure=float(r.standpipe_pressure)
        )
        for r in records
    ]
