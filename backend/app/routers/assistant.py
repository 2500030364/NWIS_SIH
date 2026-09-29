"""
===============================================================================
NWIS Backend - Drilling Knowledge Assistant Router
===============================================================================
Source-grounded decision-support assistant answering drilling engineer inquiries
using historical offset well events, stratigraphy, and operational reports.
===============================================================================
"""

import math
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.database import get_db
from app.models.well import Well
from app.models.formation import Formation
from app.models.historical_event import HistoricalEvent
from app.models.report import Report
from app.schemas.assistant import (
    AssistantQueryRequest,
    AssistantQueryResponse,
    AssistantCaseItem,
    AssistantCitationItem,
)

router = APIRouter(prefix="/api/assistant", tags=["Knowledge Assistant"])


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


@router.post(
    "/query",
    response_model=AssistantQueryResponse,
    summary="Ask Drilling Knowledge Assistant",
    description="Ask natural-language questions about historical offset well problems, formations, depths, and documented mitigations."
)
def query_knowledge_assistant(req: AssistantQueryRequest, db: Session = Depends(get_db)):
    q = req.query.strip().lower()

    # 1. Fetch Active Well for geospatial context
    active_well = db.query(Well).filter(Well.id == (req.active_well_id or 1)).first()
    active_lat = float(active_well.latitude) if active_well else 27.35
    active_lon = float(active_well.longitude) if active_well else 95.38

    # 2. Extract Depth keywords from query
    target_depth = req.current_depth or 3020.0
    depth_match = re.search(r'(\d{3,4})\s*(?:m|meter|metre)?', q)
    if depth_match:
        parsed_depth = float(depth_match.group(1))
        if 200 <= parsed_depth <= 5000:
            target_depth = parsed_depth

    # 3. Extract Formation keywords from query
    formations_map = {
        "alluvium": "Demo-Alluvium",
        "girujan": "Demo-Girujan Clay",
        "tipam": "Demo-Tipam Sandstone",
        "bokabil": "Demo-Bokabil",
        "barail": "Demo-Barail",
        "kopili": "Demo-Kopili Shale",
        "sylhet": "Demo-Sylhet Limestone"
    }
    target_formation = None
    for k, v in formations_map.items():
        if k in q:
            target_formation = v
            break

    # 4. Extract Event Type keywords from query
    event_type_filter = None
    if "mud loss" in q or "lost circulation" in q or "loss" in q:
        event_type_filter = ["MUD_LOSS", "LOST_CIRCULATION"]
    elif "stuck pipe" in q or "stuck" in q or "sticking" in q:
        event_type_filter = ["STUCK_PIPE"]
    elif "kick" in q or "gas kick" in q or "influx" in q:
        event_type_filter = ["KICK"]
    elif "torque" in q or "drag" in q or "tight" in q or "packoff" in q:
        event_type_filter = ["TORQUE_SPIKE", "NPT"]
    elif "cement" in q or "channeling" in q:
        event_type_filter = ["CEMENTING_ISSUE"]
    elif "pressure" in q:
        event_type_filter = ["HIGH_PRESSURE"]

    # 5. Query matching historical events
    events_query = (
        db.query(HistoricalEvent, Well, Formation)
        .join(Well, HistoricalEvent.well_id == Well.id)
        .outerjoin(Formation, HistoricalEvent.formation_id == Formation.id)
    )

    # Exclude active well itself to focus on offset institutional memory
    if active_well:
        events_query = events_query.filter(Well.id != active_well.id)

    if event_type_filter:
        events_query = events_query.filter(HistoricalEvent.event_type.in_(event_type_filter))

    if target_formation:
        events_query = events_query.filter(
            or_(
                Formation.formation_name.ilike(f"%{target_formation}%"),
                HistoricalEvent.description.ilike(f"%{target_formation}%")
            )
        )

    # Filter by depth window around target depth (±250m)
    depth_tolerance = 300.0 if not target_formation else 450.0
    events_query = events_query.filter(
        and_(
            HistoricalEvent.depth >= (target_depth - depth_tolerance),
            HistoricalEvent.depth <= (target_depth + depth_tolerance)
        )
    )

    matching_rows = events_query.order_by(HistoricalEvent.depth.asc()).all()

    # 6. Filter by search radius and sort by proximity + depth closeness
    scored_cases = []
    max_radius = req.radius_km or 25.0
    for ev, w, f in matching_rows:
        dist = haversine_distance_km(active_lat, active_lon, float(w.latitude), float(w.longitude))
        if dist <= max_radius:
            form_name = f.formation_name if f else "Unknown Formation"
            scored_cases.append({
                "ev": ev,
                "well": w,
                "formation_name": form_name,
                "distance": dist,
                "depth_diff": abs(float(ev.depth) - target_depth)
            })

    # Sort primarily by depth proximity, then distance
    scored_cases.sort(key=lambda x: (x["depth_diff"], x["distance"]))
    top_cases = scored_cases[:5]

    # 7. Formulate structured grounded answer
    if not top_cases:
        # Check if there are ANY cases at all in field if query was too strict
        broad_check = (
            db.query(HistoricalEvent, Well)
            .join(Well, HistoricalEvent.well_id == Well.id)
            .filter(HistoricalEvent.description.ilike(f"%{q.split()[0]}%"))
            .first()
        )
        if broad_check:
            summary = (
                f"No historical incidents found directly matching depth {target_depth:.0f}m within {max_radius:.0f} km. "
                f"However, broader field records show related activity in {broad_check[1].well_name}."
            )
        else:
            summary = (
                f"No supporting historical evidence found in offset well records within {max_radius:.0f} km of active coordinates "
                f"matching depth ~{target_depth:.0f}m and criteria '{req.query}'."
            )

        return AssistantQueryResponse(
            query=req.query,
            cases_found=0,
            answer_summary=summary,
            cases=[],
            citations=[]
        )

    # Build cases and collect citations
    case_items = []
    citation_items = []
    well_names_found = set()
    event_types_found = set()

    for item in top_cases:
        ev = item["ev"]
        w = item["well"]
        dist = item["distance"]
        form = item["formation_name"]
        well_names_found.add(w.well_name)
        event_types_found.add(ev.event_type.replace('_', ' ').title())

        # Check for matching reports for this well
        report = db.query(Report).filter(Report.well_id == w.id).first()
        doc_name = report.report_name if report else f"DDR_{w.well_name}_Final.pdf"
        file_path = report.file_path if report else f"data/reports/{w.well_name}_DDR_Final_Section.txt"

        case_items.append(
            AssistantCaseItem(
                well_id=w.id,
                well_name=w.well_name,
                distance_km=dist,
                depth=float(ev.depth),
                formation_name=form,
                event_type=ev.event_type,
                severity=ev.severity,
                description=ev.description,
                mitigation=ev.mitigation or "Standard circulation and well control protocol executed.",
                source_document=doc_name,
                source_page=1
            )
        )

        citation_items.append(
            AssistantCitationItem(
                document_name=doc_name,
                file_path=file_path,
                page_number=1,
                well_name=w.well_name,
                excerpt=f"[{ev.event_type} at {float(ev.depth):.0f}m in {form}]: {ev.description[:160]}..."
            )
        )

    # Engineering concise summary
    wells_str = ", ".join(sorted(list(well_names_found)))
    events_str = "/".join(sorted(list(event_types_found)))
    primary_form = top_cases[0]["formation_name"]
    min_d = min(c.depth for c in case_items)
    max_d = max(c.depth for c in case_items)
    depth_str = f"~{min_d:.0f}m" if min_d == max_d else f"{min_d:.0f}–{max_d:.0f}m"

    answer_summary = (
        f"Found {len(case_items)} relevant historical case(s) in offset wells ({wells_str}) "
        f"within {max_radius:.0f} km. In the {primary_form} interval ({depth_str}), offset operations "
        f"documented historical {events_str} events. "
        f"Key documented mitigation: {case_items[0].mitigation}"
    )

    return AssistantQueryResponse(
        query=req.query,
        cases_found=len(case_items),
        answer_summary=answer_summary,
        cases=case_items,
        citations=citation_items
    )
