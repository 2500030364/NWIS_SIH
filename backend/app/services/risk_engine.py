"""
===============================================================================
NWIS Backend - Smart Risk Engine Service (Phase 4)
===============================================================================
Transparent, explainable decision-support risk engine combining:
1. Stratigraphic formation alignment (well_id, measured_depth, interval bounds)
2. Offset well geospatial proximity analysis (Haversine distance)
3. Historical drilling incidents and geological hazard frequency
4. Sensor telemetry pattern and anomaly detection rules
===============================================================================
"""

import math
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.well import Well
from app.models.formation import Formation
from app.models.historical_event import HistoricalEvent
from app.models.drilling_parameter import DrillingParameter
from app.schemas.risk import (
    RiskAssessmentItem,
    SupportingEvent,
    WellRiskResponse,
    WellAlertsResponse,
)


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points on Earth in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# Global in-memory active well state for interactive demo progression
_ACTIVE_WELL_STATE: Dict[str, Any] = {
    "well_id": 1,
    "current_depth": 3020.0,
    "step_size_m": 5.0,
}


def get_active_well_depth(db: Session, well_id: int) -> float:
    """Returns the current simulated measured depth for the active well."""
    if _ACTIVE_WELL_STATE.get("well_id") == well_id:
        return float(_ACTIVE_WELL_STATE.get("current_depth", 3020.0))
    # Otherwise check latest telemetry record
    latest = (
        db.query(DrillingParameter)
        .filter(DrillingParameter.well_id == well_id)
        .order_by(DrillingParameter.measured_depth.desc())
        .first()
    )
    if latest:
        return float(latest.measured_depth)
    return 3020.0


def set_active_well_depth(well_id: int, depth: float) -> float:
    """Sets the current simulated measured depth for interactive testing."""
    _ACTIVE_WELL_STATE["well_id"] = well_id
    _ACTIVE_WELL_STATE["current_depth"] = round(float(depth), 2)
    return _ACTIVE_WELL_STATE["current_depth"]


def step_active_well_depth(well_id: int, delta_m: float = 5.0) -> float:
    """Advances or steps the active well depth for live streaming simulation."""
    current = get_active_well_depth(None, well_id) if _ACTIVE_WELL_STATE.get("well_id") == well_id else 3020.0
    new_depth = round(current + delta_m, 2)
    _ACTIVE_WELL_STATE["well_id"] = well_id
    _ACTIVE_WELL_STATE["current_depth"] = new_depth
    return new_depth


class RiskEngine:
    """Explainable expert decision-support risk engine."""

    RISK_CATEGORIES = [
        ("MUD_LOSS", "Potential Mud Loss Risk"),
        ("STUCK_PIPE", "Potential Stuck Pipe Risk"),
        ("KICK", "Potential Gas Kick Risk"),
        ("TORQUE_SPIKE", "Potential Torque Spike Risk"),
        ("HIGH_PRESSURE", "Potential High Pressure Risk"),
        ("CEMENTING_ISSUE", "Potential Cementing Issue Risk"),
        ("LOST_CIRCULATION", "Potential Lost Circulation Risk"),
        ("NPT", "Potential Non-Productive Time (NPT) Risk"),
    ]

    # Associated event type mappings
    CATEGORY_EVENT_MAPPINGS = {
        "MUD_LOSS": ["MUD_LOSS", "LOST_CIRCULATION"],
        "LOST_CIRCULATION": ["LOST_CIRCULATION", "MUD_LOSS"],
        "STUCK_PIPE": ["STUCK_PIPE", "TORQUE_SPIKE"],
        "TORQUE_SPIKE": ["TORQUE_SPIKE", "STUCK_PIPE"],
        "KICK": ["KICK", "HIGH_PRESSURE"],
        "HIGH_PRESSURE": ["HIGH_PRESSURE", "KICK"],
        "CEMENTING_ISSUE": ["CEMENTING_ISSUE"],
        "NPT": ["NPT", "STUCK_PIPE", "LOST_CIRCULATION"],
    }

    MITIGATION_RECOMMENDATIONS = {
        "MUD_LOSS": "Prepare 40-50 bbls coarse calcium carbonate (CaCO3) LCM pill in slug pit. Reduce flow rate by 15-20%. Monitor active pit volume and standpipe pressure for loss signatures.",
        "LOST_CIRCULATION": "Spot high-fluid loss squeeze pill immediately. Have thixotropic cement plug materials on standby. Minimize surge pressures during pipe reciprocation.",
        "STUCK_PIPE": "Work string immediately with maximum allowable overpull and downward jarring. Spot 50 bbls oil/glycol-based shale lubricant pipe-freeing agent. Increase circulating rate to clear sloughed cuttings.",
        "TORQUE_SPIKE": "Perform wiper trip across tight shale interval. Check mud rheology and add drilling friction reducer. Verify bottom hole assembly stabilizers are clean.",
        "KICK": "Space out, shut down mud pumps, confirm positive flow. Close annular preventer. Record Shut-In Drill Pipe Pressure (SIDPP) and Shut-In Casing Pressure (SICP). Execute Wait and Weight kill method.",
        "HIGH_PRESSURE": "Increase active mud weight by 0.05-0.08 SG with barite weighting agent. Monitor background and connection gas peaks at shale shaker.",
        "CEMENTING_ISSUE": "Run ultrasonic cement evaluation (CBL/VDL) across intermediate casing shoe. Verify centralizer spacing and plan remedial squeeze cementing if isolation is compromised.",
        "NPT": "Review offset well history logs for this interval. Keep fishing jars and backup BHA components readily accessible on rig floor.",
    }

    def __init__(self, db: Session):
        self.db = db

    def get_formation_for_depth(self, well_id: int, measured_depth: float) -> Tuple[str, Optional[Tuple[float, float]]]:
        """
        Determines current stratigraphic formation based on well_id and measured_depth.
        Falls back to regional basin stratigraphic boundaries if well specific record is not found.
        """
        formation = (
            self.db.query(Formation)
            .filter(
                Formation.well_id == well_id,
                Formation.top_depth <= measured_depth,
                Formation.bottom_depth >= measured_depth,
            )
            .first()
        )

        if formation:
            return (
                formation.formation_name,
                (float(formation.top_depth), float(formation.bottom_depth)),
            )

        # Regional stratigraphic fallback (Demo-Dihing Basin standard column)
        regional_columns = [
            ("Demo-Alluvium", 0.0, 705.0),
            ("Demo-Girujan Clay", 705.0, 1645.0),
            ("Demo-Tipam Sandstone", 1645.0, 2505.0),
            ("Demo-Bokabil", 2505.0, 2885.0),
            ("Demo-Barail", 2885.0, 3405.0),
            ("Demo-Kopili Shale", 3405.0, 4200.0),
        ]
        for name, top, btm in regional_columns:
            if top <= measured_depth <= btm:
                return name, (top, btm)

        return "Unknown Formation", None

    def get_nearby_offset_wells(self, active_well: Well, radius_km: float = 20.0) -> List[Tuple[Well, float]]:
        """Returns offset wells within radius_km sorted by Haversine distance ascending."""
        all_wells = self.db.query(Well).filter(Well.id != active_well.id).all()
        nearby = []
        for w in all_wells:
            dist = haversine_distance_km(
                float(active_well.latitude),
                float(active_well.longitude),
                float(w.latitude),
                float(w.longitude),
            )
            if dist <= radius_km:
                nearby.append((w, round(dist, 2)))

        nearby.sort(key=lambda x: x[1])
        return nearby

    def analyze_telemetry_patterns(
        self, well_id: int, current_depth: float
    ) -> Dict[str, Any]:
        """
        Analyzes recent telemetry records around current_depth for anomalous signatures:
        - torque escalation (tight hole / stuck pipe indicator)
        - mud flow decrease (mud loss indicator)
        - standpipe pressure surge (kick / pack-off indicator)
        """
        # Query 10 telemetry rows at or preceding current_depth
        records = (
            self.db.query(DrillingParameter)
            .filter(
                DrillingParameter.well_id == well_id,
                DrillingParameter.measured_depth <= current_depth + 10.0,
            )
            .order_by(DrillingParameter.measured_depth.desc())
            .limit(10)
            .all()
        )

        if not records:
            # Fallback simulated baseline telemetry at this depth
            # If in Barail (2900-3200m) simulate characteristic mud loss trend
            if 2950.0 <= current_depth <= 3080.0:
                return {
                    "mud_flow_trend": "DECREASING",
                    "mud_flow_val": 1620.0,
                    "torque_trend": "NORMAL",
                    "torque_val": 18.2,
                    "spp_trend": "NORMAL",
                    "spp_val": 2150.0,
                    "rop_val": 9.5,
                    "anomaly_found": True,
                    "summary": "Mud flow sensor indicates drop to 1620 L/min (-23% below nominal 2100 L/min).",
                }
            elif 3480.0 <= current_depth <= 3620.0:
                # Kopili shale stuck pipe trend
                return {
                    "mud_flow_trend": "NORMAL",
                    "mud_flow_val": 2100.0,
                    "torque_trend": "INCREASING",
                    "torque_val": 31.8,
                    "spp_trend": "ELEVATED",
                    "spp_val": 2720.0,
                    "rop_val": 3.8,
                    "anomaly_found": True,
                    "summary": "Torque escalated to 31.8 kNm (>26 kNm threshold) with decreasing ROP (tight hole).",
                }
            elif 2180.0 <= current_depth <= 2300.0:
                # Tipam kick trend
                return {
                    "mud_flow_trend": "INCREASING",
                    "mud_flow_val": 2450.0,
                    "torque_trend": "NORMAL",
                    "torque_val": 16.5,
                    "spp_trend": "SURGE",
                    "spp_val": 2850.0,
                    "rop_val": 22.0,
                    "anomaly_found": True,
                    "summary": "Standpipe pressure surged to 2850 psi with rapid drilling break ROP jump.",
                }
            return {
                "mud_flow_trend": "STABLE",
                "mud_flow_val": 2100.0,
                "torque_trend": "STABLE",
                "torque_val": 17.5,
                "spp_trend": "STABLE",
                "spp_val": 2200.0,
                "rop_val": 14.0,
                "anomaly_found": False,
                "summary": "All telemetry parameters nominal and within safe operational envelopes.",
            }

        closest = min(records, key=lambda r: abs(float(r.measured_depth) - current_depth))
        avg_torque = sum(float(r.torque) for r in records) / len(records)
        avg_flow = sum(float(r.mud_flow) for r in records) / len(records)
        avg_spp = sum(float(r.standpipe_pressure) for r in records) / len(records)
        min_flow = min(float(r.mud_flow) for r in records)
        max_torque = max(float(r.torque) for r in records)
        max_spp = max(float(r.standpipe_pressure) for r in records)

        torque_trend = "NORMAL"
        torque_val = float(closest.torque)
        if float(closest.torque) > 26.0 or max_torque > 26.0 or float(closest.torque) > avg_torque * 1.25:
            torque_trend = "INCREASING"
            if max_torque > 26.0:
                torque_val = max_torque

        flow_trend = "NORMAL"
        flow_val = float(closest.mud_flow)
        if float(closest.mud_flow) < 1750.0 or min_flow < 1750.0 or float(closest.mud_flow) < avg_flow * 0.85:
            flow_trend = "DECREASING"
            if min_flow < 1750.0:
                flow_val = min_flow

        spp_trend = "NORMAL"
        spp_val = float(closest.standpipe_pressure)
        if float(closest.standpipe_pressure) > 2650.0 or max_spp > 2650.0 or float(closest.standpipe_pressure) > avg_spp * 1.20:
            spp_trend = "SURGE"
            if max_spp > 2650.0:
                spp_val = max_spp

        summary_parts = []
        if torque_trend == "INCREASING":
            summary_parts.append(f"Torque elevated ({torque_val:.1f} kNm).")
        if flow_trend == "DECREASING":
            summary_parts.append(f"Mud flow dropped ({flow_val:.0f} L/min).")
        if spp_trend == "SURGE":
            summary_parts.append(f"Standpipe pressure surge ({spp_val:.0f} psi).")

        return {
            "mud_flow_trend": flow_trend,
            "mud_flow_val": flow_val,
            "torque_trend": torque_trend,
            "torque_val": torque_val,
            "spp_trend": spp_trend,
            "spp_val": spp_val,
            "rop_val": float(closest.rop),
            "anomaly_found": len(summary_parts) > 0,
            "summary": " ".join(summary_parts) if summary_parts else "All sensor streams within expected baseline limits.",
        }

    def evaluate_well_risks(
        self,
        well_id: int,
        target_depth: Optional[float] = None,
        radius_km: float = 20.0,
    ) -> WellRiskResponse:
        """
        Comprehensive explainable risk assessment for a well at target_depth.
        Returns assessed risk categories, confidence scores, levels, and supporting evidence.
        """
        well = self.db.query(Well).filter(Well.id == well_id).first()
        if not well:
            raise ValueError(f"Well with ID {well_id} not found.")

        current_depth = (
            float(target_depth)
            if target_depth is not None
            else get_active_well_depth(self.db, well_id)
        )

        current_formation, formation_bounds = self.get_formation_for_depth(
            well_id, current_depth
        )
        offset_wells = self.get_nearby_offset_wells(well, radius_km)
        offset_well_ids = [w.id for w, _ in offset_wells]
        offset_dist_map = {w.id: dist for w, dist in offset_wells}
        offset_name_map = {w.id: w.well_name for w, _ in offset_wells}

        # Analyze current telemetry signatures
        telemetry_insights = self.analyze_telemetry_patterns(well_id, current_depth)

        # Retrieve all historical events from nearby offset wells
        events_query = (
            self.db.query(HistoricalEvent, Formation)
            .outerjoin(Formation, HistoricalEvent.formation_id == Formation.id)
            .filter(HistoricalEvent.well_id.in_(offset_well_ids))
        )
        all_nearby_events = events_query.all()

        assessed_risks: List[RiskAssessmentItem] = []

        for category_code, category_title in self.RISK_CATEGORIES:
            mapped_types = self.CATEGORY_EVENT_MAPPINGS.get(category_code, [category_code])

            # Filter relevant events for this category
            matching_events: List[Tuple[HistoricalEvent, Optional[Formation]]] = []
            for ev, form in all_nearby_events:
                if ev.event_type in mapped_types:
                    matching_events.append((ev, form))

            # Score calculations:
            # Separate events into same-formation / depth-adjacent events vs remote events
            same_formation_events = [
                (ev, form)
                for ev, form in matching_events
                if form and form.formation_name.lower() == current_formation.lower()
            ]

            # Depth-adjacent events (within +/- 150m of current depth)
            depth_adjacent_events = [
                (ev, form)
                for ev, form in matching_events
                if abs(float(ev.depth) - current_depth) <= 150.0
            ]

            # Primary relevant events for this specific depth & formation
            primary_events = same_formation_events if same_formation_events else depth_adjacent_events
            if not primary_events:
                primary_events = matching_events

            # Unique supporting wells
            supporting_wells_list = sorted(
                list(set(offset_name_map[ev.well_id] for ev, _ in primary_events if ev.well_id in offset_name_map))
            )
            all_supporting_wells = sorted(
                list(set(offset_name_map[ev.well_id] for ev, _ in matching_events if ev.well_id in offset_name_map))
            )

            # 1. Historical frequency score (0.0 - 0.35)
            # Give higher weight to events in the same formation or depth interval
            unique_supporting_wells = supporting_wells_list if supporting_wells_list else all_supporting_wells
            freq_score = min(0.35, len(supporting_wells_list) * 0.10)
            if not supporting_wells_list and all_supporting_wells:
                freq_score = min(0.10, len(all_supporting_wells) * 0.03)

            # 2. Formation matching score (0.0 - 0.25)
            formation_score = 0.0
            if same_formation_events:
                formation_score = 0.25
            elif matching_events and current_formation != "Unknown Formation":
                formation_score = 0.03

            # 3. Depth proximity score (0.0 - 0.25)
            depth_score = 0.0
            depths_for_interval = [float(ev.depth) for ev, _ in primary_events]
            all_depths = [float(ev.depth) for ev, _ in matching_events]
            depth_interval_str = None

            if depths_for_interval:
                min_depth = min(depths_for_interval)
                max_depth = max(depths_for_interval)
                depth_interval_str = f"{min_depth:.0f}m – {max_depth:.0f}m"

                # Check if current depth falls inside historical interval
                if (min_depth - 30.0) <= current_depth <= (max_depth + 30.0):
                    depth_score = 0.25
                else:
                    min_dist_to_event = min(abs(current_depth - d) for d in depths_for_interval)
                    if min_dist_to_event <= 150.0:
                        depth_score = 0.20 * max(0.0, 1.0 - (min_dist_to_event / 150.0))
            elif all_depths:
                min_depth = min(all_depths)
                max_depth = max(all_depths)
                depth_interval_str = f"{min_depth:.0f}m – {max_depth:.0f}m"

            # 4. Telemetry trend correlation score (0.0 - 0.25)
            telemetry_score = 0.0
            telemetry_evidence = None

            if category_code in ("MUD_LOSS", "LOST_CIRCULATION"):
                if telemetry_insights["mud_flow_trend"] == "DECREASING":
                    telemetry_score = 0.20
                    telemetry_evidence = f"Sensor telemetry: mud flow decreased to {telemetry_insights['mud_flow_val']:.0f} L/min."
                elif telemetry_insights["mud_flow_trend"] == "NORMAL":
                    telemetry_score = 0.02
            elif category_code in ("STUCK_PIPE", "TORQUE_SPIKE"):
                if telemetry_insights["torque_trend"] == "INCREASING":
                    telemetry_score = 0.20
                    telemetry_evidence = f"Sensor telemetry: torque elevated to {telemetry_insights['torque_val']:.1f} kNm."
                elif telemetry_insights["torque_trend"] == "NORMAL":
                    telemetry_score = 0.02
            elif category_code in ("KICK", "HIGH_PRESSURE"):
                if telemetry_insights["spp_trend"] in ("SURGE", "ELEVATED"):
                    telemetry_score = 0.20
                    telemetry_evidence = f"Sensor telemetry: standpipe pressure surge to {telemetry_insights['spp_val']:.0f} psi."
                elif telemetry_insights["spp_trend"] == "NORMAL":
                    telemetry_score = 0.02

            # Aggregate total score
            raw_score = freq_score + formation_score + depth_score + telemetry_score

            # Depth proximity gating: If current depth is far away (>150m) from historical event depths,
            # cap severity at MEDIUM/LOW so operators are not alarmed when far above or below the hazard zone
            if depth_score == 0.0:
                raw_score = min(raw_score, 0.35)

            # Safe Zone Gating: If current depth is far away (>250m) and not in same formation,
            # clamp the score so shallow/safe formations never trigger false alarms
            if all_depths:
                min_dist_overall = min(abs(current_depth - d) for d in all_depths)
                if min_dist_overall > 250.0 and not same_formation_events:
                    raw_score = min(raw_score * 0.25, 0.22)

            if not matching_events:
                score = 0.05
            else:
                score = min(0.96, max(0.05, raw_score))

            score = round(score, 3)

            # Assign explainable severity level
            if score >= 0.70:
                level = "CRITICAL"
            elif score >= 0.45:
                level = "HIGH"
            elif score >= 0.25:
                level = "MEDIUM"
            else:
                level = "LOW"

            # Build explainability narrative
            explanation_bullets = []
            if unique_supporting_wells:
                explanation_bullets.append(
                    f"• {len(unique_supporting_wells)} nearby offset wells experienced {category_code.replace('_', ' ').lower()}-related events ({', '.join(unique_supporting_wells[:4])})."
                )
            else:
                explanation_bullets.append(
                    f"• No historical {category_code.replace('_', ' ').lower()} incidents recorded in neighboring wells."
                )

            if depth_interval_str:
                explanation_bullets.append(
                    f"• Historical incident depth interval: {depth_interval_str}."
                )
                if depth_score >= 0.20:
                    explanation_bullets.append(
                        f"• Current measured depth ({current_depth:.0f}m) lies directly within or immediately adjacent to this historical hazard zone."
                    )
                else:
                    explanation_bullets.append(
                        f"• Current measured depth ({current_depth:.0f}m) is separated from historical event clusters."
                    )

            if same_formation_events:
                explanation_bullets.append(
                    f"• Incident cluster confirmed in current formation: {current_formation}."
                )

            if telemetry_evidence:
                explanation_bullets.append(f"• {telemetry_evidence}")

            explanation_text = "\n".join(explanation_bullets)

            # Format supporting events list
            supp_event_objs = []
            # Sort matching events by proximity to current depth
            sorted_matching = sorted(matching_events, key=lambda x: abs(float(x[0].depth) - current_depth))
            for ev, form in sorted_matching[:5]:
                dist_km = offset_dist_map.get(ev.well_id, 0.0)
                well_name = offset_name_map.get(ev.well_id, f"Well-{ev.well_id}")
                supp_event_objs.append(
                    SupportingEvent(
                        well_name=well_name,
                        well_id=ev.well_id,
                        event_type=ev.event_type,
                        depth=float(ev.depth),
                        severity=ev.severity,
                        description=ev.description,
                        cause=ev.cause,
                        mitigation=ev.mitigation,
                        distance_km=dist_km,
                    )
                )

            assessed_risks.append(
                RiskAssessmentItem(
                    risk_type=category_code,
                    title=category_title,
                    score=score,
                    level=level,
                    current_depth=current_depth,
                    current_formation=current_formation,
                    historical_depth_interval=depth_interval_str,
                    explanation=explanation_text,
                    supporting_wells=unique_supporting_wells,
                    supporting_events=supp_event_objs,
                    telemetry_evidence=telemetry_evidence or telemetry_insights.get("summary"),
                    recommended_mitigation=self.MITIGATION_RECOMMENDATIONS.get(category_code),
                )
            )

        # Sort assessed risks by score descending
        assessed_risks.sort(key=lambda r: r.score, reverse=True)

        # Highest risk level determination
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        highest_level = "LOW"
        if assessed_risks:
            highest_level = assessed_risks[0].level

        return WellRiskResponse(
            well_id=well.id,
            well_name=well.well_name,
            current_depth=current_depth,
            current_formation=current_formation,
            total_risks_assessed=len(assessed_risks),
            highest_risk_level=highest_level,
            risks=assessed_risks,
        )

    def get_active_alerts(
        self,
        well_id: int,
        target_depth: Optional[float] = None,
        radius_km: float = 20.0,
        min_level: str = "MEDIUM",
    ) -> WellAlertsResponse:
        """
        Returns only active alerts for the well (filtered to actionable levels: CRITICAL, HIGH, MEDIUM).
        """
        assessment = self.evaluate_well_risks(well_id, target_depth, radius_km)

        level_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        threshold = level_weights.get(min_level.upper(), 2)

        actionable_alerts = [
            r for r in assessment.risks if level_weights.get(r.level, 0) >= threshold
        ]

        return WellAlertsResponse(
            well_id=assessment.well_id,
            well_name=assessment.well_name,
            current_depth=assessment.current_depth,
            current_formation=assessment.current_formation,
            active_alert_count=len(actionable_alerts),
            alerts=actionable_alerts,
        )
