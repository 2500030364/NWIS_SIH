"""
===============================================================================
NWIS Backend - Risk Assessment & Alerts Router (Phase 4)
===============================================================================
Exposes REST endpoints for:
1. GET /api/risks/{well_id}   - Full explainable risk evaluation across 8 hazard categories
2. GET /api/alerts/{well_id}  - Filtered actionable operational alerts
3. GET /api/wells/active/state - Current state of the simulated active drilling well
4. POST /api/wells/active/set_depth - Set active well depth for interactive testing
5. POST /api/wells/active/step      - Progress active well depth by delta meters
===============================================================================
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.well import Well
from app.schemas.risk import (
    WellRiskResponse,
    WellAlertsResponse,
    ActiveWellState,
)
from app.services.risk_engine import (
    RiskEngine,
    get_active_well_depth,
    set_active_well_depth,
    step_active_well_depth,
    _ACTIVE_WELL_STATE,
)

router = APIRouter(tags=["Risk Engine & Alerts"])


@router.get(
    "/api/risks/{well_id}",
    response_model=WellRiskResponse,
    summary="Evaluate drilling risks for a well",
    description=(
        "Evaluates 8 key drilling hazard categories (MUD_LOSS, STUCK_PIPE, KICK, "
        "TORQUE_SPIKE, HIGH_PRESSURE, CEMENTING_ISSUE, LOST_CIRCULATION, NPT) for the "
        "specified well at its current or specified measured depth. Combines stratigraphic "
        "formation alignment, offset-well historical incident frequency, depth proximity, "
        "and real-time telemetry signatures into transparent, explainable scores and advisories."
    ),
)
def get_well_risks(
    well_id: int,
    depth: Optional[float] = Query(None, ge=0.0, description="Override measured depth in meters (optional)"),
    radius_km: float = Query(25.0, gt=0.0, le=200.0, description="Offset well search radius in kilometers"),
    db: Session = Depends(get_db),
):
    try:
        engine = RiskEngine(db)
        return engine.evaluate_well_risks(well_id, target_depth=depth, radius_km=radius_km)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating risk engine: {str(e)}",
        )


@router.get(
    "/api/alerts/{well_id}",
    response_model=WellAlertsResponse,
    summary="Get active drilling alerts for a well",
    description=(
        "Retrieves actionable high-priority alerts (MEDIUM, HIGH, CRITICAL) for display "
        "on the operational cockpit dashboard. Every alert includes transparent explainability "
        "narratives, supporting nearby wells, and engineering mitigation guidance."
    ),
)
def get_well_alerts(
    well_id: int,
    depth: Optional[float] = Query(None, ge=0.0, description="Override measured depth in meters (optional)"),
    radius_km: float = Query(25.0, gt=0.0, le=200.0, description="Offset well search radius in kilometers"),
    min_level: str = Query("MEDIUM", description="Filter threshold: LOW, MEDIUM, HIGH, CRITICAL"),
    db: Session = Depends(get_db),
):
    try:
        engine = RiskEngine(db)
        return engine.get_active_alerts(
            well_id, target_depth=depth, radius_km=radius_km, min_level=min_level
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving alerts: {str(e)}",
        )


@router.get(
    "/api/wells/active/state",
    response_model=ActiveWellState,
    summary="Get active drilling well state & KPIs",
    description=(
        "Returns real-time operational status for the active demo well (NWIS-W001 or W025), "
        "including current depth, current formation, active alert count, and highest severity."
    ),
)
def get_active_state(
    well_id: Optional[int] = Query(None, description="Optional well ID to inspect as active (defaults to W001)"),
    db: Session = Depends(get_db),
):
    target_well_id = well_id or _ACTIVE_WELL_STATE.get("well_id", 1)
    well = db.query(Well).filter(Well.id == target_well_id).first()
    if not well:
        well = db.query(Well).first()
        target_well_id = well.id if well else 1

    current_depth = get_active_well_depth(db, target_well_id)
    engine = RiskEngine(db)
    current_formation, _ = engine.get_formation_for_depth(target_well_id, current_depth)
    alerts_data = engine.get_active_alerts(target_well_id, target_depth=current_depth)

    highest_sev = "LOW"
    if alerts_data.alerts:
        highest_sev = alerts_data.alerts[0].level

    return ActiveWellState(
        well_id=target_well_id,
        well_name=well.well_name if well else f"NWIS-W{target_well_id:03d}",
        current_depth=round(current_depth, 2),
        current_formation=current_formation,
        total_depth=float(well.total_depth) if well else 3500.0,
        status=well.status if well else "DRILLING",
        active_alerts=alerts_data.active_alert_count,
        highest_severity=highest_sev,
        last_updated=datetime.now(timezone.utc).isoformat(),
    )


@router.post(
    "/api/wells/active/set_depth",
    summary="Set active well measured depth",
    description="Set the simulated measured depth for interactive testing and live demo scenarios.",
)
def set_active_depth(
    depth: float = Query(..., ge=0.0, le=10000.0, description="New measured depth in meters"),
    well_id: Optional[int] = Query(None, description="Well ID to set depth for"),
    db: Session = Depends(get_db),
):
    target_well_id = well_id or _ACTIVE_WELL_STATE.get("well_id", 1)
    new_depth = set_active_well_depth(target_well_id, depth)
    engine = RiskEngine(db)
    formation, _ = engine.get_formation_for_depth(target_well_id, new_depth)
    return {
        "well_id": target_well_id,
        "current_depth": new_depth,
        "current_formation": formation,
        "status": "updated",
    }


@router.post(
    "/api/wells/active/step",
    summary="Advance active well depth by delta meters",
    description="Steps the active well depth forward by a designated distance to simulate ongoing drilling.",
)
def step_active_depth(
    delta_m: float = Query(5.0, description="Depth increment in meters (can be negative to step back)"),
    well_id: Optional[int] = Query(None, description="Well ID to advance"),
    db: Session = Depends(get_db),
):
    target_well_id = well_id or _ACTIVE_WELL_STATE.get("well_id", 1)
    new_depth = step_active_well_depth(target_well_id, delta_m)
    engine = RiskEngine(db)
    formation, _ = engine.get_formation_for_depth(target_well_id, new_depth)
    return {
        "well_id": target_well_id,
        "current_depth": new_depth,
        "current_formation": formation,
        "delta_m": delta_m,
        "status": "stepped",
    }
