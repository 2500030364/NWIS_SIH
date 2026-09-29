"""
===============================================================================
NWIS Backend - Wells Router
===============================================================================
Exposes endpoints for listing wells, spatial radius search using Haversine
formula, individual well details, and well historical drilling event timelines.
===============================================================================
"""

import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.well import Well
from app.models.formation import Formation
from app.models.historical_event import HistoricalEvent
from app.models.drilling_parameter import DrillingParameter
from app.models.report import Report
from app.schemas.well import (
    WellResponse,
    NearbyWellResponse,
    WellDetailResponse,
    OffsetRelevanceItem,
    DrillAheadZoneEvent,
    DrillAheadZone,
    DrillAheadResponse,
    WellComparisonResponse,
)
from app.schemas.formation import WellFormationInterval
from app.schemas.historical_event import WellHistoryEvent


router = APIRouter(prefix="/api/wells", tags=["Wells"])


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two geographic coordinates on Earth
    using the Haversine formula (Earth mean radius = 6371.0 km).
    """
    R = 6371.0  # Earth's radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


@router.get(
    "",
    response_model=List[WellResponse],
    summary="List all wells",
    description="Retrieve a list of all wells in the field with optional filtering by operational status and field name."
)
def get_wells(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by well status (e.g. COMPLETED, DRILLING, ACTIVE)"),
    field_name: Optional[str] = Query(None, description="Filter by field name"),
    db: Session = Depends(get_db)
):
    query = db.query(Well)
    if status_filter:
        query = query.filter(Well.status.ilike(f"%{status_filter.strip()}%"))
    if field_name:
        query = query.filter(Well.field_name.ilike(f"%{field_name.strip()}%"))
    return query.order_by(Well.id).all()


@router.get(
    "/nearby",
    response_model=List[NearbyWellResponse],
    summary="Find nearby offset wells",
    description=(
        "Calculates distances from a target coordinate (lat/long) to all wells using "
        "the Haversine formula and returns wells within the requested radius in kilometers, "
        "sorted by proximity."
    )
)
def get_nearby_wells(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees (-90 to 90)"),
    long: float = Query(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees (-180 to 180)"),
    radius: float = Query(..., gt=0.0, le=500.0, description="Search radius in kilometers (must be > 0)"),
    db: Session = Depends(get_db)
):
    all_wells = db.query(Well).all()
    nearby_results = []

    for w in all_wells:
        dist = haversine_distance_km(lat, long, float(w.latitude), float(w.longitude))
        if dist <= radius:
            nearby_results.append(
                NearbyWellResponse(
                    well_id=w.id,
                    well_name=w.well_name,
                    latitude=float(w.latitude),
                    longitude=float(w.longitude),
                    distance_km=round(dist, 2),
                    total_depth=float(w.total_depth),
                    status=w.status,
                    field_name=w.field_name
                )
            )

    # Sort results by distance ascending
    nearby_results.sort(key=lambda x: x.distance_km)
    return nearby_results


@router.get(
    "/compare",
    response_model=WellComparisonResponse,
    summary="Compare Active Well with an Offset Well",
    description="Provides side-by-side comparison of formation, depth, sensor parameters, historical events, and mitigations."
)
def compare_wells(
    active_well_id: int = Query(1, description="Active Well ID"),
    offset_well_id: int = Query(7, description="Offset Well ID to compare against"),
    current_depth: float = Query(3020.0, description="Current bit depth in meters"),
    db: Session = Depends(get_db)
):
    active_well = db.query(Well).filter(Well.id == active_well_id).first()
    offset_well = db.query(Well).filter(Well.id == offset_well_id).first()

    if not active_well:
        raise HTTPException(status_code=404, detail=f"Active well {active_well_id} not found.")
    if not offset_well:
        raise HTTPException(status_code=404, detail=f"Offset well {offset_well_id} not found.")

    dist = haversine_distance_km(
        float(active_well.latitude), float(active_well.longitude),
        float(offset_well.latitude), float(offset_well.longitude)
    )

    active_form = (
        db.query(Formation)
        .filter(
            Formation.well_id == active_well_id,
            Formation.top_depth <= current_depth,
            Formation.bottom_depth >= current_depth
        )
        .first()
    )
    active_form_name = active_form.formation_name if active_form else "Demo-Barail"

    offset_form = (
        db.query(Formation)
        .filter(
            Formation.well_id == offset_well_id,
            Formation.top_depth <= current_depth,
            Formation.bottom_depth >= current_depth
        )
        .first()
    )
    offset_form_name = offset_form.formation_name if offset_form else "Demo-Barail"

    active_telemetry_row = (
        db.query(DrillingParameter)
        .filter(
            DrillingParameter.well_id == active_well_id,
            DrillingParameter.measured_depth <= current_depth
        )
        .order_by(DrillingParameter.measured_depth.desc())
        .first()
    )
    if not active_telemetry_row:
        active_telemetry_row = db.query(DrillingParameter).filter(DrillingParameter.well_id == active_well_id).first()

    offset_telemetry_row = (
        db.query(DrillingParameter)
        .filter(
            DrillingParameter.well_id == offset_well_id,
            DrillingParameter.measured_depth <= (current_depth + 50)
        )
        .order_by(DrillingParameter.measured_depth.desc())
        .first()
    )
    if not offset_telemetry_row:
        offset_telemetry_row = db.query(DrillingParameter).filter(DrillingParameter.well_id == offset_well_id).first()

    offset_events = (
        db.query(HistoricalEvent, Formation.formation_name)
        .outerjoin(Formation, HistoricalEvent.formation_id == Formation.id)
        .filter(
            HistoricalEvent.well_id == offset_well_id,
            HistoricalEvent.depth >= max(0, current_depth - 150),
            HistoricalEvent.depth <= (current_depth + 150)
        )
        .order_by(HistoricalEvent.depth.asc())
        .all()
    )

    events_list = []
    mitigations_list = []
    for ev, f_name in offset_events:
        events_list.append({
            "id": ev.id,
            "depth": float(ev.depth),
            "formation": f_name or offset_form_name,
            "event_type": ev.event_type,
            "severity": ev.severity,
            "description": ev.description,
            "cause": ev.cause or "Depletion and pore pressure differential in offset sands.",
            "mitigation": ev.mitigation or "Pumped LCM pill and adjusted circulation rate."
        })
        if ev.mitigation:
            mitigations_list.append({
                "event_type": ev.event_type,
                "depth": float(ev.depth),
                "action_documented": ev.mitigation,
                "cause_documented": ev.cause,
                "source": f"DDR / WCR for {offset_well.well_name}",
                "disclaimer": "NOTE: This is historical information, not an autonomous operational recommendation."
            })

    same_formation = active_form_name == offset_form_name

    def format_telem(row):
        if not row:
            return {"depth": current_depth, "rop": 12.0, "wob": 15.0, "rpm": 120.0, "torque": 18.0, "standpipe_pressure": 2400.0, "mud_flow": 2200.0, "mud_weight": 1.25}
        return {
            "depth": float(row.measured_depth),
            "rop": float(row.rop),
            "wob": float(row.wob),
            "rpm": float(row.rpm),
            "torque": float(row.torque),
            "standpipe_pressure": float(row.standpipe_pressure),
            "mud_flow": float(row.mud_flow),
            "mud_weight": float(row.mud_weight)
        }

    return WellComparisonResponse(
        active_well={
            "id": active_well.id,
            "well_name": active_well.well_name,
            "current_depth": current_depth,
            "total_depth": float(active_well.total_depth),
            "status": active_well.status,
            "current_formation": active_form_name,
            "telemetry": format_telem(active_telemetry_row)
        },
        offset_well={
            "id": offset_well.id,
            "well_name": offset_well.well_name,
            "distance_km": round(dist, 2),
            "total_depth": float(offset_well.total_depth),
            "status": offset_well.status,
            "formation_at_depth": offset_form_name,
            "telemetry": format_telem(offset_telemetry_row)
        },
        formation_comparison={
            "active_formation": active_form_name,
            "offset_formation": offset_form_name,
            "is_matched": same_formation,
            "notes": (
                "Both wells penetrate the same geological formation interval."
                if same_formation
                else "Wells are currently in differing stratigraphic layers."
            )
        },
        telemetry_comparison={
            "torque_variance": round(
                abs(float(active_telemetry_row.torque if active_telemetry_row else 18) - 
                    float(offset_telemetry_row.torque if offset_telemetry_row else 18)), 2
            ),
            "pressure_variance": round(
                abs(float(active_telemetry_row.standpipe_pressure if active_telemetry_row else 2400) - 
                    float(offset_telemetry_row.standpipe_pressure if offset_telemetry_row else 2400)), 2
            )
        },
        historical_events=events_list,
        historical_mitigations=mitigations_list
    )


@router.get(
    "/{well_id}/relevance",
    response_model=List[OffsetRelevanceItem],
    summary="Get offset well relevance ranking",
    description="Multi-factor prototype relevance ranking based on proximity, stratigraphic match, depth overlap, and historical incident frequency."
)
def get_offset_relevance(
    well_id: int,
    current_depth: float = Query(3020.0, description="Current bit depth in meters"),
    radius_km: float = Query(20.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    active_well = db.query(Well).filter(Well.id == well_id).first()
    if not active_well:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    active_lat = float(active_well.latitude)
    active_lon = float(active_well.longitude)

    active_form = (
        db.query(Formation)
        .filter(
            Formation.well_id == well_id,
            Formation.top_depth <= current_depth,
            Formation.bottom_depth >= current_depth
        )
        .first()
    )
    active_form_name = active_form.formation_name if active_form else "Demo-Barail"

    all_other_wells = db.query(Well).filter(Well.id != well_id).all()
    relevance_list = []

    for w in all_other_wells:
        dist = haversine_distance_km(active_lat, active_lon, float(w.latitude), float(w.longitude))
        if dist > radius_km:
            continue

        score = 0
        reasons = []

        # 1. Proximity score (up to 35 pts)
        if dist <= 2.5:
            score += 35
            reasons.append(f"Immediate proximity ({dist:.2f} km)")
        elif dist <= 5.0:
            score += 25
            reasons.append(f"Nearby offset location ({dist:.2f} km)")
        elif dist <= 10.0:
            score += 15
            reasons.append(f"Mid-range offset ({dist:.2f} km)")
        else:
            score += 5
            reasons.append(f"Regional offset ({dist:.2f} km)")

        # 2. Formation similarity (up to 30 pts)
        offset_has_form = (
            db.query(Formation)
            .filter(
                Formation.well_id == w.id,
                Formation.formation_name.ilike(f"%{active_form_name}%")
            )
            .first()
        )
        if offset_has_form:
            score += 30
            reasons.append(f"Shares {active_form_name} formation ({float(offset_has_form.top_depth):.0f}–{float(offset_has_form.bottom_depth):.0f} m)")
        else:
            reasons.append("Different stratigraphic tops")

        # 3. Depth overlap (up to 15 pts)
        if float(w.total_depth) >= current_depth:
            score += 15
            reasons.append(f"Drilled beyond active depth (Total Depth: {float(w.total_depth):.0f} m)")
        else:
            reasons.append(f"Shallower total depth ({float(w.total_depth):.0f} m)")

        # 4. Historical events in comparable interval (up to 20 pts)
        comparable_events = (
            db.query(HistoricalEvent)
            .filter(
                HistoricalEvent.well_id == w.id,
                HistoricalEvent.depth >= max(0, current_depth - 150),
                HistoricalEvent.depth <= (current_depth + 150)
            )
            .all()
        )
        event_cnt = len(comparable_events)
        if event_cnt > 0:
            score += min(20, event_cnt * 10)
            event_types = set(e.event_type.replace('_', ' ').title() for e in comparable_events)
            reasons.append(f"{event_cnt} historical event(s) in comparable interval: {', '.join(event_types)}")

        if score >= 65:
            level = "HIGH"
        elif score >= 35:
            level = "MEDIUM"
        else:
            level = "LOW"

        relevance_list.append(
            OffsetRelevanceItem(
                well_id=w.id,
                well_name=w.well_name,
                latitude=float(w.latitude),
                longitude=float(w.longitude),
                distance_km=dist,
                total_depth=float(w.total_depth),
                status=w.status,
                relevance_level=level,
                relevance_score=score,
                reasons=reasons,
                shared_formation=active_form_name if offset_has_form else None,
                comparable_events_count=event_cnt
            )
        )

    relevance_list.sort(key=lambda x: (x.relevance_score, -x.distance_km), reverse=True)
    return relevance_list


@router.get(
    "/{well_id}/drill-ahead",
    response_model=DrillAheadResponse,
    summary="Get Drill-Ahead Look-Ahead Timeline",
    description="Identifies historical event zones ahead of the active bit depth across offset wells."
)
def get_drill_ahead(
    well_id: int,
    current_depth: float = Query(3020.0, description="Current bit depth in meters"),
    lookahead_m: float = Query(500.0, description="Lookahead distance in meters"),
    radius_km: float = Query(20.0, description="Offset well radius in kilometers"),
    db: Session = Depends(get_db)
):
    active_well = db.query(Well).filter(Well.id == well_id).first()
    if not active_well:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found.")

    active_lat = float(active_well.latitude)
    active_lon = float(active_well.longitude)

    all_wells = db.query(Well).filter(Well.id != well_id).all()
    nearby_offsets = {}
    for w in all_wells:
        d = haversine_distance_km(active_lat, active_lon, float(w.latitude), float(w.longitude))
        if d <= radius_km:
            nearby_offsets[w.id] = (w.well_name, d)

    offset_ids = list(nearby_offsets.keys())

    active_formations = (
        db.query(Formation)
        .filter(Formation.well_id == well_id)
        .order_by(Formation.top_depth.asc())
        .all()
    )

    def get_form_at(d: float):
        for f in active_formations:
            if float(f.top_depth) <= d <= float(f.bottom_depth):
                return f.formation_name
        return "Demo-Barail"

    current_form_name = get_form_at(current_depth)

    events_ahead = (
        db.query(HistoricalEvent)
        .filter(
            HistoricalEvent.well_id.in_(offset_ids),
            HistoricalEvent.depth >= max(0, current_depth - 10),
            HistoricalEvent.depth <= (current_depth + lookahead_m)
        )
        .order_by(HistoricalEvent.depth.asc())
        .all()
    )

    zones = []
    zone_step = 25.0
    start_d = current_depth
    end_d = current_depth + lookahead_m

    d = start_d
    while d < end_d:
        z_start = round(d, 1)
        z_end = round(d + zone_step, 1)
        form_name = get_form_at((z_start + z_end) / 2.0)

        z_events = [
            e for e in events_ahead
            if (z_start <= float(e.depth) < z_end) or (abs(float(e.depth) - z_start) <= 5.0)
        ]

        event_items = []
        for e in z_events:
            w_name, w_dist = nearby_offsets.get(e.well_id, ("Unknown", 0.0))
            event_items.append(
                DrillAheadZoneEvent(
                    well_id=e.well_id,
                    well_name=w_name,
                    distance_km=w_dist,
                    depth=float(e.depth),
                    formation_name=form_name,
                    event_type=e.event_type,
                    severity=e.severity,
                    description=e.description,
                    mitigation=e.mitigation,
                    source_document=f"DDR_{w_name}_2024.pdf"
                )
            )

        ev_count = len(event_items)
        has_critical = any(e.severity == "CRITICAL" for e in event_items)
        has_high = any(e.severity == "HIGH" for e in event_items)

        if z_start == current_depth:
            status_val = "CURRENT_BIT"
            concentration_val = "CONCENTRATED" if ev_count >= 2 else ("MODERATE" if ev_count == 1 else "NONE")
            summary_val = f"Current bit depth position at {current_depth:.0f}m in {current_form_name}."
            if ev_count > 0:
                summary_val += f" Warning: {ev_count} historical event(s) recorded in nearby offset wells at this exact depth."
        elif ev_count >= 2 or has_critical:
            status_val = "HAZARD_ZONE"
            concentration_val = "CONCENTRATED"
            types_str = ", ".join(set(e.event_type.replace('_', ' ').title() for e in event_items))
            summary_val = f"Historical event concentration: {ev_count} incident(s) ({types_str}) recorded across offset wells."
        elif ev_count == 1 or has_high:
            status_val = "WATCH"
            concentration_val = "MODERATE"
            summary_val = f"Historical watch zone: {event_items[0].event_type.replace('_', ' ').title()} recorded at {event_items[0].depth:.0f}m in {event_items[0].well_name}."
        else:
            status_val = "CLEAR"
            concentration_val = "NONE"
            summary_val = "No significant historical events reported in offset wells for this depth interval."

        zones.append(
            DrillAheadZone(
                depth_start=z_start,
                depth_end=z_end,
                formation_name=form_name,
                status=status_val,
                concentration=concentration_val,
                event_count=ev_count,
                summary=summary_val,
                events=event_items
            )
        )

        d += zone_step

    return DrillAheadResponse(
        active_well_id=active_well.id,
        active_well_name=active_well.well_name,
        current_depth=current_depth,
        current_formation=current_form_name,
        lookahead_m=lookahead_m,
        zones=zones
    )


@router.get(
    "/{well_id}",
    response_model=WellDetailResponse,
    summary="Get single well details",
    description="Retrieve comprehensive master information for a specific well by its ID."
)
def get_well(well_id: int, db: Session = Depends(get_db)):
    well = db.query(Well).filter(Well.id == well_id).first()
    if not well:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Well with id {well_id} not found."
        )
    return well


@router.get(
    "/{well_id}/history",
    response_model=List[WellHistoryEvent],
    summary="Get historical incident timeline for a well",
    description="Retrieve chronological or depth-ordered drilling events, hazards, and mitigations recorded for the specified well."
)
def get_well_history(
    well_id: int,
    formation: Optional[str] = Query(None, description="Filter by formation name (e.g. Demo-Barail)"),
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g. MUD_LOSS, STUCK_PIPE, KICK)"),
    severity: Optional[str] = Query(None, description="Filter by severity level (LOW, MEDIUM, HIGH, CRITICAL)"),
    db: Session = Depends(get_db)
):
    # Verify well exists
    well = db.query(Well).filter(Well.id == well_id).first()
    if not well:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Well with id {well_id} not found."
        )

    query = (
        db.query(HistoricalEvent, Formation.formation_name)
        .outerjoin(Formation, HistoricalEvent.formation_id == Formation.id)
        .filter(HistoricalEvent.well_id == well_id)
    )

    if event_type:
        query = query.filter(HistoricalEvent.event_type.ilike(event_type.strip()))
    if severity:
        query = query.filter(HistoricalEvent.severity.ilike(severity.strip()))
    if formation:
        query = query.filter(Formation.formation_name.ilike(f"%{formation.strip()}%"))

    results = query.order_by(HistoricalEvent.depth.asc()).all()

    response = []
    for ev, form_name in results:
        response.append(
            WellHistoryEvent(
                id=ev.id,
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
    "/{well_id}/formations",
    response_model=List[WellFormationInterval],
    summary="Get formation intervals for a well",
    description="Retrieve all stratigraphic formation intervals encountered by a specific well, ordered by top depth."
)
def get_well_formations(well_id: int, db: Session = Depends(get_db)):
    well = db.query(Well).filter(Well.id == well_id).first()
    if not well:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Well with id {well_id} not found."
        )

    formations = (
        db.query(Formation)
        .filter(Formation.well_id == well_id)
        .order_by(Formation.top_depth.asc())
        .all()
    )

    return [
        WellFormationInterval(
            formation_name=f.formation_name,
            top_depth=float(f.top_depth),
            bottom_depth=float(f.bottom_depth)
        )
        for f in formations
    ]
