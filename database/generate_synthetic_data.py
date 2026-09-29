#!/usr/bin/env python3
"""
===============================================================================
NWIS (Nearby Wells Intelligence System) - Phase 1: Synthetic Data Generator
===============================================================================
Purpose:
    Generates realistic, internally consistent demonstration data for 25 offset
    wells in a fictional petroleum field inspired by northeastern Indian
    oil-field geology (Upper Assam shelf / Demo-Dihing Basin).

DISCLAIMER:
    This dataset is 100% SYNTHETIC demonstration data created for the SIH prototype.
    It does NOT represent actual operational, confidential, or geographical data
    of Oil India Limited (OIL), ONGC, or any other operating entity.

Outputs:
    1. database/seed.sql (transactional SQL INSERT statements for PostgreSQL)
    2. data/generated/dataset_summary.json (metadata & verification data)
    3. data/reports/*.txt (realistic mock drilling report documents)
    4. Comprehensive console validation report verifying all constraints & correlations.
===============================================================================
"""

import os
import sys
import math
import random
import json
from datetime import datetime, date, timedelta

# Fix seed for reproducible, deterministic test runs
RANDOM_SEED = 2026
random.seed(RANDOM_SEED)

# Paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SEED_SQL_PATH = os.path.join(PROJECT_ROOT, "database", "seed.sql")
GENERATED_DIR = os.path.join(PROJECT_ROOT, "data", "generated")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "data", "reports")

# Ensure required directories exist
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# =============================================================================
# GEOLOGICAL CONFIGURATION (Fictional Demo-Dihing Basin, NE India Inspiration)
# =============================================================================
# Stratigraphic column in descending order of true vertical depth.
# Base depths are typical regional intervals with minor local structural dip.
MASTER_STRATIGRAPHY = [
    {
        "name": "Demo-Alluvium",
        "description": "Unconsolidated sands, gravels, surface alluvial cover",
        "nominal_top": 0.0,
        "nominal_bottom": 680.0
    },
    {
        "name": "Demo-Girujan Clay",
        "description": "Mottled claystone with thin lenticular sand layers; prone to shallow lost circulation",
        "nominal_top": 680.0,
        "nominal_bottom": 1620.0
    },
    {
        "name": "Demo-Tipam Sandstone",
        "description": "Massive multi-storey sandstone reservoir; occasional high-pressure gas lenses",
        "nominal_top": 1620.0,
        "nominal_bottom": 2480.0
    },
    {
        "name": "Demo-Bokabil",
        "description": "Siltstone-shale alternation; structural transition zone",
        "nominal_top": 2480.0,
        "nominal_bottom": 2860.0
    },
    {
        "name": "Demo-Barail",
        "description": "Main mature oil reservoir; interbedded sand-shale-coal; depleted pressure thief zones",
        "nominal_top": 2860.0,
        "nominal_bottom": 3380.0
    },
    {
        "name": "Demo-Kopili Shale",
        "description": "Deep fissile marine shale with overpressure; reactive swelling shale causing stuck pipe",
        "nominal_top": 3380.0,
        "nominal_bottom": 3890.0
    },
    {
        "name": "Demo-Sylhet Limestone",
        "description": "Deep basement carbonate interval; fractured limestone",
        "nominal_top": 3890.0,
        "nominal_bottom": 4200.0
    }
]

FIELD_NAME = "Demo-Dihing Basin (Fictional Field)"
BASE_LATITUDE = 27.350000   # Fictional cluster center (NE India demo coordinates)
BASE_LONGITUDE = 95.380000


# =============================================================================
# 1. WELL GENERATOR
# =============================================================================
def generate_wells(num_wells=25):
    """
    Generates 25 synthetic wells arranged in a realistic geographic cluster.
    """
    wells = []
    statuses = ["COMPLETED", "ACTIVE", "DRILLING", "SUSPENDED"]
    status_weights = [0.55, 0.25, 0.15, 0.05]

    for i in range(1, num_wells + 1):
        well_name = f"NWIS-W{i:03d}"

        # Geographic cluster: +/- 0.06 degrees (~6-8 km radius, typical offset field)
        # Seeded pseudo-random coordinates with spatial clustering
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0.012, 0.075)
        lat = round(BASE_LATITUDE + radius * math.cos(angle), 6)
        lon = round(BASE_LONGITUDE + radius * math.sin(angle), 6)

        # Total depth: ranges from 3050m to 4150m
        # For wells involved in deep Kopili shale events, ensure sufficient depth
        if well_name in ["NWIS-W004", "NWIS-W008", "NWIS-W014", "NWIS-W022"]:
            total_depth = round(random.uniform(3820.0, 4120.0), 2)
        elif well_name in ["NWIS-W002", "NWIS-W007", "NWIS-W011", "NWIS-W015", "NWIS-W019"]:
            total_depth = round(random.uniform(3250.0, 3600.0), 2)
        else:
            total_depth = round(random.uniform(3050.0, 4050.0), 2)

        # Spud date between 2021 and 2024
        start_date = date(2021, 1, 15)
        end_date = date(2024, 11, 30)
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        spud_date = start_date + timedelta(days=random_days)

        status = random.choices(statuses, weights=status_weights)[0]

        # Specific well status overrides for story consistency
        if well_name in ["NWIS-W001", "NWIS-W002", "NWIS-W007", "NWIS-W011"]:
            status = "COMPLETED"
        elif well_name == "NWIS-W025":
            status = "DRILLING"  # Target well currently being drilled in the story!

        wells.append({
            "id": i,
            "well_name": well_name,
            "latitude": lat,
            "longitude": lon,
            "total_depth": total_depth,
            "status": status,
            "spud_date": spud_date,
            "field_name": FIELD_NAME
        })

    return wells


# =============================================================================
# 2. FORMATIONS GENERATOR
# =============================================================================
def generate_formations(wells):
    """
    Generates 4 to 6 stratigraphic formation intervals per well, consistent
    with the regional stratigraphy and the well's total depth.
    """
    formations = []
    formation_id = 1

    for well in wells:
        td = well["total_depth"]
        # Mild structural dip simulation based on well coordinates
        structural_dip = (well["latitude"] - BASE_LATITUDE) * 450.0 + (well["longitude"] - BASE_LONGITUDE) * 350.0

        current_top = 0.0

        for strat in MASTER_STRATIGRAPHY:
            # Stop if the top boundary is already beyond total depth
            layer_top = max(current_top, round(max(0.0, strat["nominal_top"] + structural_dip), 2))
            if layer_top >= td:
                break

            layer_bottom = round(strat["nominal_bottom"] + structural_dip, 2)
            # Cap bottom depth at well total depth if it exceeds TD
            if layer_bottom >= td:
                layer_bottom = td

            if layer_bottom > layer_top:
                formations.append({
                    "id": formation_id,
                    "well_id": well["id"],
                    "formation_name": strat["name"],
                    "top_depth": layer_top,
                    "bottom_depth": layer_bottom
                })
                formation_id += 1
                current_top = layer_bottom

            if layer_bottom >= td:
                break

    return formations


# =============================================================================
# 3. HISTORICAL EVENTS GENERATOR (With Intentional Cross-Well Correlations)
# =============================================================================
def generate_historical_events(wells, formations):
    """
    Generates 100+ historical drilling incidents with realistic engineering
    causes and mitigations, including INTENTIONALLY CORRELATED incident clusters
    across neighboring offset wells to demonstrate intelligence capabilities.
    """
    events = []
    event_id = 1

    # Map (well_id, formation_name) -> formation_id
    form_map = {}
    for f in formations:
        form_map[(f["well_id"], f["formation_name"])] = f

    well_by_name = {w["well_name"]: w for w in wells}

    # -------------------------------------------------------------------------
    # CORRELATED INCIDENT CLUSTERS (As specified in NWIS intelligence requirements)
    # -------------------------------------------------------------------------

    # CLUSTER A: Depleted Sand Thief Zone in Demo-Barail (MUD_LOSS)
    # Nearby wells penetrating the depleted Barail reservoir experienced severe fluid loss.
    cluster_barail_mudloss = [
        ("NWIS-W002", 2980.0, "HIGH", "MUD_LOSS",
         "Severe mud loss observed while penetrating upper Barail sandstone. Rate exceeded 45 bbls/hr.",
         "Depleted pressure sand with subnormal pore pressure gradient (approx 0.38 psi/ft) causing fracture breakdown under 1.34 SG mud weight.",
         "Spotted 50 bbls coarse CaCO3 LCM (Loss Circulation Material) pill; reduced active mud weight to 1.22 SG; staged resumption of circulation."),

        ("NWIS-W007", 3010.0, "HIGH", "MUD_LOSS",
         "Encountered identical thief zone in Barail formation; 50 bbls total pit volume lost within 35 minutes.",
         "Offset depletion zone extending from NWIS-W002; formation integrity unable to support hydrostatic head of 1.32 SG mud.",
         "Pumped high-fluid-loss squeeze LCM pill with cellulosic fibers; reduced pump rate from 2400 L/min to 1750 L/min."),

        ("NWIS-W011", 3040.0, "MEDIUM", "MUD_LOSS",
         "Partial dynamic mud loss of 20 bbls/hr while drilling through mid-Barail sand interval.",
         "Marginal pressure depletion communicated through permeable sand channel from W002/W007 fault block.",
         "Introduced medium-sized nut plug and mica flakes directly into active suction pit; stabilized return flow."),

        ("NWIS-W015", 2995.0, "HIGH", "MUD_LOSS",
         "Sudden loss of returns (35 bbls/hr) at 2995m in Barail sand. Standpipe pressure dropped by 280 psi.",
         "High permeability thief zone; pressure depletion confirmed by subsequent RFT logs.",
         "Displaced hole with 1.20 SG low-solids mud; set viscous bentonite LCM plug."),

        ("NWIS-W019", 3025.0, "CRITICAL", "LOST_CIRCULATION",
         "Total lost circulation encountered in Barail horizon; zero surface returns to shaker.",
         "Severe regional pressure depletion combined with natural micro-fractures in upper Barail.",
         "Bullheaded 80 bbls heavy LCM pill; pulled BHA into casing shoe to let well heal for 18 hours.")
    ]

    for w_name, depth, sev, ev_type, desc, cause, mitig in cluster_barail_mudloss:
        well = well_by_name.get(w_name)
        if not well:
            continue
        form = form_map.get((well["id"], "Demo-Barail"))
        form_id = form["id"] if form else None
        event_time = datetime(well["spud_date"].year, well["spud_date"].month, well["spud_date"].day, 14, 30) + timedelta(days=random.randint(15, 40))

        events.append({
            "id": event_id,
            "well_id": well["id"],
            "depth": depth,
            "formation_id": form_id,
            "event_type": ev_type,
            "severity": sev,
            "description": desc,
            "cause": cause,
            "mitigation": mitig,
            "event_time": event_time
        })
        event_id += 1

    # CLUSTER B: Reactive Swelling Shale in Demo-Kopili (STUCK_PIPE & TORQUE_SPIKE)
    cluster_kopili_stuckpipe = [
        ("NWIS-W004", 3520.0, "HIGH", "STUCK_PIPE",
         "Drillstring became mechanically stuck while pulling out of hole (POOH) at 3520m in Kopili shale.",
         "Highly reactive smectite-rich Kopili shale hydration; borehole sloughing led to pack-off around 8-1/2 inch BHA.",
         "Spotted 40 bbls glycol-weighted lubricant pill; worked pipe with upward jars at 70 tons; freed string after 6.5 hours."),

        ("NWIS-W008", 3560.0, "CRITICAL", "STUCK_PIPE",
         "Severe drillstring pack-off while reaming tight spot in lower Kopili shale; rotation and circulation fully stalled.",
         "Shale sloughing and borehole breakout caused by insufficient mud inhibition and low mud weight (1.28 SG).",
         "Executed multiple high-impact jarring cycles; pumped acidic wash; freed string after 14 hours; resulted in 32 hrs NPT."),

        ("NWIS-W014", 3490.0, "HIGH", "TORQUE_SPIKE",
         "Erratic torque spikes up to 41.5 kNm with intense string stalling while drilling Kopili shale interval.",
         "Tight hole and cutting accumulation around stabilizer blades due to hole cleaning deficit in swollen shale.",
         "Circulated high-viscosity tandem sweep; raised mud weight from 1.30 to 1.38 SG; back-reamed with controlled RPM."),

        ("NWIS-W022", 3580.0, "HIGH", "STUCK_PIPE",
         "Pipe stuck during connection at 3580m; no upward movement possible.",
         "Mechanically unstable overpressured Kopili shale spalling into wellbore cavity.",
         "Applied 60 tons overpull with hydraulic jar; circulated clean with potassium chloride (KCl) polymer mud.")
    ]

    for w_name, depth, sev, ev_type, desc, cause, mitig in cluster_kopili_stuckpipe:
        well = well_by_name.get(w_name)
        if not well:
            continue
        form = form_map.get((well["id"], "Demo-Kopili Shale"))
        form_id = form["id"] if form else None
        event_time = datetime(well["spud_date"].year, well["spud_date"].month, well["spud_date"].day, 9, 15) + timedelta(days=random.randint(45, 75))

        events.append({
            "id": event_id,
            "well_id": well["id"],
            "depth": depth,
            "formation_id": form_id,
            "event_type": ev_type,
            "severity": sev,
            "description": desc,
            "cause": cause,
            "mitigation": mitig,
            "event_time": event_time
        })
        event_id += 1

    # CLUSTER C: Shallow Overpressured Gas Influx in Demo-Tipam (HIGH_PRESSURE & KICK)
    cluster_tipam_kicks = [
        ("NWIS-W003", 2240.0, "HIGH", "KICK",
         "Drilling break observed at 2240m in Tipam sandstone followed by 18 bbl pit gain and flow with pumps off.",
         "Encountered localized high-pressure gas pocket charging permeable Tipam sand lenses.",
         "Annular preventer shut in; measured SIDPP = 340 psi, SICP = 460 psi; executed Wait-and-Weight kill; raised MW to 1.28 SG."),

        ("NWIS-W009", 2280.0, "CRITICAL", "HIGH_PRESSURE",
         "Formation pressure surge detected; gas cut mud reduced active mud weight from 1.20 to 1.04 SG at shaker.",
         "Overpressured gas cap in Upper Tipam communicating along fault boundary.",
         "Degasser engaged; shut in BOP; circulated out gas kick via choke manifold; densified mud to 1.31 SG."),

        ("NWIS-W013", 2210.0, "MEDIUM", "HIGH_PRESSURE",
         "Standpipe pressure climbed by 380 psi; background gas on mud log jumped from 1.5% to 18.2%.",
         "Pore pressure ramp in top Tipam sand exceeding planned balance.",
         "Adjusted mud weight by +0.06 SG; reduced penetration rate to control gas dissolution rate."),

        ("NWIS-W021", 2260.0, "HIGH", "KICK",
         "14 bbl kick influx detected after drilling break in Tipam interval.",
         "Underbalanced drilling condition due to unrecognized structural crest elevation in fault block.",
         "Killed well using Driller's method; circulated out influx bubble through mud-gas separator safely.")
    ]

    for w_name, depth, sev, ev_type, desc, cause, mitig in cluster_tipam_kicks:
        well = well_by_name.get(w_name)
        if not well:
            continue
        form = form_map.get((well["id"], "Demo-Tipam Sandstone"))
        form_id = form["id"] if form else None
        event_time = datetime(well["spud_date"].year, well["spud_date"].month, well["spud_date"].day, 22, 10) + timedelta(days=random.randint(18, 30))

        events.append({
            "id": event_id,
            "well_id": well["id"],
            "depth": depth,
            "formation_id": form_id,
            "event_type": ev_type,
            "severity": sev,
            "description": desc,
            "cause": cause,
            "mitigation": mitig,
            "event_time": event_time
        })
        event_id += 1

    # -------------------------------------------------------------------------
    # BASELINE DRILLING INCIDENTS ACROSS ALL WELLS (Target: 110-130 total events)
    # -------------------------------------------------------------------------
    # Categories required: MUD_LOSS, STUCK_PIPE, KICK, TORQUE_SPIKE,
    #                      CEMENTING_ISSUE, LOST_CIRCULATION, HIGH_PRESSURE, NPT
    incident_templates = [
        ("MUD_LOSS", "MEDIUM", "Seepage loss of 15-20 bbls/hr observed across porous sandstone interval.",
         "Differential overbalance in porous sand facies.",
         "Added fine calcium carbonate to active mud system; monitored pit levels closely."),

        ("LOST_CIRCULATION", "HIGH", "Total loss of circulation while drilling 12-1/4 inch hole section.",
         "Encountered natural fracture network in Upper Girujan formation.",
         "Spotted high-viscosity cross-linked polymer pill; waited on cement plug."),

        ("TORQUE_SPIKE", "MEDIUM", "Sudden torque spikes from 18 kNm to 29 kNm with stick-slip vibration.",
         "Interbedded lithology change from soft shale to hard calcareous siltstone.",
         "Reduced WOB from 24 klbf to 16 klbf; increased rotary speed to 125 RPM to suppress stick-slip."),

        ("STUCK_PIPE", "MEDIUM", "Differential sticking occurred during 45-minute survey pause.",
         "Thick filter cake deposited across permeable sandstone under 350 psi differential pressure.",
         "Spotted low-toxicity oil-based spotting fluid across BHA; pipe pulled free after 90 minutes."),

        ("KICK", "HIGH", "10 bbl influx taken while making connection; casing pressure elevated.",
         "Swabbing effect during drillstring upward motion combined with formation gas saturation.",
         "Shut in well on pipe rams; stripped back to bottom; circulated out gas bubble using choke manifold."),

        ("HIGH_PRESSURE", "MEDIUM", "Connection gas increased to 12%; flow line temperature anomaly noted.",
         "Approaching sub-regional pressure transition zone.",
         "Raised mud weight by 0.05 SG; conducted flow check; verified well stability."),

        ("CEMENTING_ISSUE", "HIGH", "Poor cement bond log (CBL) across 9-5/8 inch casing shoe; channeling detected.",
         "Inadequate mud displacement efficiency and gas channeling through setting cement slurry.",
         "Perforated casing and performed remedial squeeze cementation; pressure tested shoe successfully."),

        ("CEMENTING_ISSUE", "MEDIUM", "Premature cement slurry hydration during intermediate casing job.",
         "Higher downhole temperature than predicted in laboratory thickening test.",
         "Reversed out excess cement through drillpipe; cleared top of liner."),

        ("NPT", "HIGH", "28 hours Non-Productive Time due to top drive hydraulic motor failure during reaming.",
         "Mechanical fatigue of high-pressure seal under elevated cyclic vibration.",
         "Replaced hydraulic actuator assembly; inspected Kelly valve and certified rig ready."),

        ("NPT", "MEDIUM", "16 hours NPT waiting on weather and flash-flood logistics at river crossing.",
         "Monsoon rainfall washed out approach culvert to rig site in Dihing valley.",
         "Reinforced road foundation with gravel; restored supply line for barite and chemicals."),

        ("MUD_LOSS", "LOW", "Minor seepage loss of 3-5 bbls/hr while penetrating permeable sand stringer.",
         "Normal filtration overbalance across permeable zone.",
         "Added fine ground nut shells and mica sweep to mud pit; loss stabilized."),

        ("TORQUE_SPIKE", "LOW", "Transient torque flutter of +4 kNm during bit engagement in hard siltstone.",
         "Bit tooth chatter upon contact with interbedded sandstone layer.",
         "Adjusted rotary speed from 110 to 125 RPM and maintained steady bit weight."),

        ("HIGH_PRESSURE", "LOW", "Minor connection gas elevation up to 3.2% from background 1.1%.",
         "Localized pore pressure fluctuation in transition stringer.",
         "Maintained steady mud weight and increased circulation bottoms-up time."),

        ("CEMENTING_ISSUE", "LOW", "Surface casing cement top found 25m below cellar floor after placement.",
         "Normal slurry settling and consolidation in porous shallow alluvium.",
         "Completed top-fill job through 1-inch tremie line with neat Portland cement."),

        ("NPT", "LOW", "3.5 hours NPT for routine MWD pulse telemetry tool battery change-out.",
         "Scheduled battery lifespan reached after 120 rotating hours.",
         "Pulled shallow tool into BOP, replaced lithium battery pack, verified pulse signal."),

        ("LOST_CIRCULATION", "LOW", "Intermittent dynamic loss of 6 bbls during high pump rate circulation.",
         "Annular friction pressure slightly exceeded local fracture gradient.",
         "Reduced pump flow rate by 150 L/min and optimized mud rheology.")
    ]

    # Generate additional realistic events across all 25 wells to reach > 100 events
    for well in wells:
        # 3 to 6 baseline events per well
        num_baseline = random.randint(3, 6)
        for _ in range(num_baseline):
            ev_template = random.choice(incident_templates)
            ev_type, sev, desc, cause, mitig = ev_template

            # Depth must be valid within well TD
            depth = round(random.uniform(500.0, well["total_depth"] - 30.0), 2)

            # Find matching formation for depth
            matched_form = None
            for f in formations:
                if f["well_id"] == well["id"] and f["top_depth"] <= depth <= f["bottom_depth"]:
                    matched_form = f
                    break

            form_id = matched_form["id"] if matched_form else None

            # Calculate realistic event date during well operational timeline
            days_offset = random.randint(5, 80)
            event_time = datetime(well["spud_date"].year, well["spud_date"].month, well["spud_date"].day,
                                  random.randint(0, 23), random.randint(0, 59)) + timedelta(days=days_offset)

            events.append({
                "id": event_id,
                "well_id": well["id"],
                "depth": depth,
                "formation_id": form_id,
                "event_type": ev_type,
                "severity": sev,
                "description": desc,
                "cause": cause,
                "mitigation": mitig,
                "event_time": event_time
            })
            event_id += 1

    return events


# =============================================================================
# 4. DRILLING TELEMETRY GENERATOR (High-Frequency Parameters with Signatures)
# =============================================================================
def generate_drilling_parameters(wells, historical_events):
    """
    Generates several thousand sensor telemetry records with realistic drilling
    physics (depth, torque, WOB, ROP, RPM, mud flow, mud weight, standpipe pressure)
    including SPECIFIC PRE-INCIDENT ANOMALY PATTERNS:
      - Increasing torque before a stuck-pipe event
      - Decreasing mud flow / pit loss before a mud-loss event
      - Increasing standpipe pressure / ROP drilling break before a high-pressure kick
    """
    telemetry = []
    record_id = 1

    # Map events by well to embed pre-incident signatures
    events_by_well = {}
    for ev in historical_events:
        events_by_well.setdefault(ev["well_id"], []).append(ev)

    # Select representative wells for detailed depth telemetry runs
    # e.g., offset demonstration wells W002 (mud loss), W004 (stuck pipe), W003 (kick),
    # and active well W025 (current drilling operation) + several others.
    telemetry_wells = wells[:12] + [wells[-1]]  # 13 wells with dense telemetry

    for well in telemetry_wells:
        well_events = events_by_well.get(well["id"], [])
        spud_dt = datetime(well["spud_date"].year, well["spud_date"].month, well["spud_date"].day, 6, 0)

        # Baseline drilling parameters
        curr_depth = 800.0
        max_depth = min(well["total_depth"], 3600.0)
        depth_step = 8.0  # record every ~8 meters of drilling
        curr_time = spud_dt + timedelta(days=5)

        # Identify critical event depths in this well if any
        stuck_pipe_events = [e for e in well_events if e["event_type"] == "STUCK_PIPE"]
        mud_loss_events = [e for e in well_events if e["event_type"] in ["MUD_LOSS", "LOST_CIRCULATION"]]
        kick_events = [e for e in well_events if e["event_type"] in ["KICK", "HIGH_PRESSURE"]]

        while curr_depth <= max_depth:
            # Check proximity to known hazards to inject realistic signature
            is_near_stuck = any(abs(curr_depth - e["depth"]) < 35.0 and curr_depth <= e["depth"] for e in stuck_pipe_events)
            is_near_mudloss = any(abs(curr_depth - e["depth"]) < 25.0 and curr_depth <= e["depth"] for e in mud_loss_events)
            is_near_kick = any(abs(curr_depth - e["depth"]) < 25.0 and curr_depth <= e["depth"] for e in kick_events)

            # Normal baseline physics
            base_torque = random.uniform(14.0, 18.5)
            base_wob = random.uniform(12.0, 19.0)
            base_rop = random.uniform(12.0, 22.0)
            base_rpm = random.uniform(115.0, 130.0)
            base_flow = random.uniform(2350.0, 2550.0)
            base_mw = 1.22
            base_spp = random.uniform(2150.0, 2380.0)

            # SIGNATURE 1: Pre-Stuck Pipe Anomaly Pattern (Increasing torque & erratic RPM)
            if is_near_stuck:
                # Target nearest event depth
                target_depth = min([e["depth"] for e in stuck_pipe_events if e["depth"] >= curr_depth], default=curr_depth)
                dist_to_event = max(0.1, target_depth - curr_depth)
                # Exponential ramp in torque as distance closes (from 18 up to 44 kNm)
                ramp_factor = (35.0 - dist_to_event) / 35.0
                torque = round(base_torque + ramp_factor * 26.0 + random.uniform(-1.0, 2.0), 2)
                rop = round(max(1.2, base_rop * (1.0 - ramp_factor * 0.85)), 2)
                rpm = round(max(40.0, base_rpm - ramp_factor * 60.0 + random.uniform(-10, 10)), 2)
                wob = round(base_wob + ramp_factor * 8.0, 2)
                mud_flow = round(base_flow - ramp_factor * 250.0, 2)
                mud_weight = round(base_mw, 2)
                spp = round(base_spp + ramp_factor * 380.0, 2)

            # SIGNATURE 2: Pre-Mud Loss Anomaly Pattern (Decreasing mud flow & pit losses)
            elif is_near_mudloss:
                target_depth = min([e["depth"] for e in mud_loss_events if e["depth"] >= curr_depth], default=curr_depth)
                dist_to_event = max(0.1, target_depth - curr_depth)
                ramp_factor = (25.0 - dist_to_event) / 25.0
                # Sudden severe flow drops
                mud_flow = round(max(1200.0, base_flow - ramp_factor * 1100.0), 2)
                spp = round(max(1400.0, base_spp - ramp_factor * 420.0), 2)
                torque = round(base_torque + random.uniform(-1.0, 1.0), 2)
                wob = round(base_wob, 2)
                rop = round(base_rop, 2)
                rpm = round(base_rpm, 2)
                mud_weight = round(base_mw - ramp_factor * 0.08, 2)

            # SIGNATURE 3: Pre-Kick / High Pressure Pattern (SPP surge & drilling break)
            elif is_near_kick:
                target_depth = min([e["depth"] for e in kick_events if e["depth"] >= curr_depth], default=curr_depth)
                dist_to_event = max(0.1, target_depth - curr_depth)
                ramp_factor = (25.0 - dist_to_event) / 25.0
                # SPP spikes and ROP shows a drilling break (sudden jump)
                spp = round(base_spp + ramp_factor * 950.0, 2)
                rop = round(base_rop + ramp_factor * 18.0, 2)  # Drilling break!
                torque = round(base_torque + ramp_factor * 6.0, 2)
                mud_flow = round(base_flow + ramp_factor * 150.0, 2)
                rpm = round(base_rpm, 2)
                wob = round(base_wob, 2)
                mud_weight = round(max(1.02, base_mw - ramp_factor * 0.15), 2)  # Gas cutting lowers mud weight

            # Normal undisturbed drilling
            else:
                torque = round(base_torque + random.uniform(-1.5, 1.5), 2)
                wob = round(base_wob + random.uniform(-1.5, 1.5), 2)
                rop = round(base_rop + random.uniform(-2.5, 2.5), 2)
                rpm = round(base_rpm + random.uniform(-3.0, 3.0), 2)
                mud_flow = round(base_flow + random.uniform(-40.0, 40.0), 2)
                mud_weight = round(base_mw + (curr_depth / 4000.0) * 0.12, 2)
                spp = round(base_spp + (curr_depth / 4000.0) * 350.0 + random.uniform(-25.0, 25.0), 2)

            telemetry.append({
                "id": record_id,
                "well_id": well["id"],
                "recorded_at": curr_time,
                "measured_depth": round(curr_depth, 2),
                "torque": max(0.0, torque),
                "wob": max(0.0, wob),
                "rop": max(0.0, rop),
                "rpm": max(0.0, rpm),
                "mud_flow": max(0.0, mud_flow),
                "mud_weight": max(0.8, mud_weight),
                "standpipe_pressure": max(0.0, spp)
            })

            record_id += 1
            curr_depth += depth_step
            # Advance time realistically (~25 minutes per 8m drilling interval)
            curr_time += timedelta(minutes=random.randint(20, 32))

    return telemetry


# =============================================================================
# 5. DRILLING REPORTS GENERATOR (Documents & Metadata)
# =============================================================================
def generate_reports(wells, historical_events):
    """
    Generates realistic drilling documents (DDR, WCR, MUD_LOG, DRILLING_REPORT,
    COMPLETION_REPORT), saves actual demo files in data/reports/, and generates
    database metadata records.
    """
    reports = []
    report_id = 1

    report_types = ["DDR", "WCR", "MUD_LOG", "COMPLETION_REPORT", "DRILLING_REPORT"]

    for well in wells:
        well_name = well["well_name"]

        # 1. Daily Drilling Report (DDR)
        ddr_filename = f"{well_name}_DDR_Final_Section.txt"
        ddr_path = os.path.join(REPORTS_DIR, ddr_filename)
        ddr_text = (
            f"=====================================================================\n"
            f"DAILY DRILLING REPORT (DDR) - RIG 04\n"
            f"WELL: {well_name} | FIELD: {FIELD_NAME}\n"
            f"OPERATING DATE: {well['spud_date'] + timedelta(days=28)}\n"
            f"=====================================================================\n"
            f"SUMMARY OF OPERATIONS:\n"
            f"Drilled 8-1/2 inch hole section from 2840.0m to 3110.0m in Demo-Barail formation.\n"
            f"Average ROP: 14.8 m/hr. Flow rate: 2400 L/min. Active mud weight: 1.26 SG.\n"
            f"Encountered differential pressure zone at 2980-3020m. Mud losses treated with\n"
            f"medium calcium carbonate LCM sweep. Gas levels normal at 1.4%.\n"
            f"Status at 06:00 hrs: Circulating bottoms up prior to bit change.\n"
        )
        with open(ddr_path, "w", encoding="utf-8") as f:
            f.write(ddr_text)

        reports.append({
            "id": report_id,
            "well_id": well["id"],
            "report_name": f"{well_name} Daily Drilling Report #28",
            "report_type": "DDR",
            "file_path": f"data/reports/{ddr_filename}",
            "report_date": well["spud_date"] + timedelta(days=28),
            "extracted_text": ddr_text.replace("\n", " ").strip()
        })
        report_id += 1

        # 2. Mud Logging Report
        mudlog_filename = f"{well_name}_Mud_Log_Summary.txt"
        mudlog_path = os.path.join(REPORTS_DIR, mudlog_filename)
        mudlog_text = (
            f"=====================================================================\n"
            f"MUD LOGGING GEOLOGICAL EVALUATION\n"
            f"WELL: {well_name} | TOTAL DEPTH: {well['total_depth']}m\n"
            f"=====================================================================\n"
            f"LITHOLOGICAL EVALUATION:\n"
            f"- Demo-Tipam Sandstone (1620m - 2480m): Fine to medium grained quartzose sand,\n"
            f"  good visible porosity, light yellow fluorescence, slow milky cut.\n"
            f"- Demo-Barail (2860m - 3380m): Clean sandstone interbedded with carbonaceous\n"
            f"  shale and thin sub-bituminous coal seams. Total Gas: peaks to 450 units.\n"
            f"- Demo-Kopili Shale: Hard, dark grey fissile shale with moderate swelling potential.\n"
        )
        with open(mudlog_path, "w", encoding="utf-8") as f:
            f.write(mudlog_text)

        reports.append({
            "id": report_id,
            "well_id": well["id"],
            "report_name": f"{well_name} Mud Logging Geological Evaluation",
            "report_type": "MUD_LOG",
            "file_path": f"data/reports/{mudlog_filename}",
            "report_date": well["spud_date"] + timedelta(days=45),
            "extracted_text": mudlog_text.replace("\n", " ").strip()
        })
        report_id += 1

        # 3. Well Completion Report (For completed wells)
        if well["status"] == "COMPLETED":
            wcr_filename = f"{well_name}_Well_Completion_Report.txt"
            wcr_path = os.path.join(REPORTS_DIR, wcr_filename)
            wcr_text = (
                f"=====================================================================\n"
                f"WELL COMPLETION REPORT (WCR)\n"
                f"WELL: {well_name} | TARGET RESERVOIR: Demo-Barail Sand\n"
                f"FINAL TOTAL DEPTH: {well['total_depth']}m TVD\n"
                f"=====================================================================\n"
                f"COMPLETION DETAILS:\n"
                f"7-inch production liner set from 2650m to {well['total_depth'] - 20}m.\n"
                f"Perforated interval: 3012.0m - 3028.0m with 4-1/2 inch tubing conveyed guns.\n"
                f"Initial reservoir pressure: 3820 psi. Flow tested through 24/64 inch choke.\n"
                f"Tubing head pressure (THP): 1420 psi. Produced clean sweet crude.\n"
                f"Well handed over to production operations.\n"
            )
            with open(wcr_path, "w", encoding="utf-8") as f:
                f.write(wcr_text)

            reports.append({
                "id": report_id,
                "well_id": well["id"],
                "report_name": f"{well_name} Well Completion Report",
                "report_type": "WCR",
                "file_path": f"data/reports/{wcr_filename}",
                "report_date": well["spud_date"] + timedelta(days=90),
                "extracted_text": wcr_text.replace("\n", " ").strip()
            })
            report_id += 1

    return reports


# =============================================================================
# 6. SQL SEED GENERATOR
# =============================================================================
def escape_sql(value):
    """Helper to safely format SQL literals."""
    if value is None:
        return "NULL"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, (date, datetime)):
        return f"'{value.isoformat()}'"
    else:
        # Escape single quotes
        sanitized = str(value).replace("'", "''")
        return f"'{sanitized}'"


def write_seed_sql(wells, formations, telemetry, events, reports, output_path):
    """
    Writes database/seed.sql containing structured, transactional PostgreSQL
    INSERT statements with explicit sequence resets.
    """
    print(f"\n[INFO] Writing SQL seed dataset to: {output_path}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("-- ============================================================================\n")
        f.write("-- NWIS (Nearby Wells Intelligence System) - Synthetic Demonstration Seed Data\n")
        f.write("-- Dialect: PostgreSQL 14+\n")
        f.write(f"-- Generated on: {datetime.now().isoformat()}\n")
        f.write("-- NOTICE: Synthetic dataset for SIH prototype. Not real OIL or ONGC data.\n")
        f.write("-- ============================================================================\n\n")
        f.write("BEGIN;\n\n")

        # Disable foreign key checks / truncate tables cleanly
        f.write("-- Clean existing table data\n")
        f.write("TRUNCATE TABLE reports, historical_events, drilling_parameters, formations, wells RESTART IDENTITY CASCADE;\n\n")

        # 1. INSERT WELLS
        f.write("-- ============================================================================\n")
        f.write(f"-- 1. INSERT WELLS ({len(wells)} records)\n")
        f.write("-- ============================================================================\n")
        f.write("INSERT INTO wells (id, well_name, latitude, longitude, total_depth, status, spud_date, field_name) VALUES\n")
        well_lines = []
        for w in wells:
            line = f"  ({w['id']}, {escape_sql(w['well_name'])}, {w['latitude']}, {w['longitude']}, {w['total_depth']}, {escape_sql(w['status'])}, {escape_sql(w['spud_date'])}, {escape_sql(w['field_name'])})"
            well_lines.append(line)
        f.write(",\n".join(well_lines) + ";\n\n")

        # 2. INSERT FORMATIONS
        f.write("-- ============================================================================\n")
        f.write(f"-- 2. INSERT FORMATIONS ({len(formations)} records)\n")
        f.write("-- ============================================================================\n")
        f.write("INSERT INTO formations (id, well_id, formation_name, top_depth, bottom_depth) VALUES\n")
        form_lines = []
        for fm in formations:
            line = f"  ({fm['id']}, {fm['well_id']}, {escape_sql(fm['formation_name'])}, {fm['top_depth']}, {fm['bottom_depth']})"
            form_lines.append(line)
        f.write(",\n".join(form_lines) + ";\n\n")

        # 3. INSERT HISTORICAL EVENTS
        f.write("-- ============================================================================\n")
        f.write(f"-- 3. INSERT HISTORICAL EVENTS ({len(events)} records)\n")
        f.write("-- ============================================================================\n")
        f.write("INSERT INTO historical_events (id, well_id, depth, formation_id, event_type, severity, description, cause, mitigation, event_time) VALUES\n")
        ev_lines = []
        for ev in events:
            form_id_str = str(ev['formation_id']) if ev['formation_id'] is not None else "NULL"
            line = f"  ({ev['id']}, {ev['well_id']}, {ev['depth']}, {form_id_str}, {escape_sql(ev['event_type'])}, {escape_sql(ev['severity'])}, {escape_sql(ev['description'])}, {escape_sql(ev['cause'])}, {escape_sql(ev['mitigation'])}, {escape_sql(ev['event_time'])})"
            ev_lines.append(line)
        f.write(",\n".join(ev_lines) + ";\n\n")

        # 4. INSERT REPORTS
        f.write("-- ============================================================================\n")
        f.write(f"-- 4. INSERT REPORTS ({len(reports)} records)\n")
        f.write("-- ============================================================================\n")
        f.write("INSERT INTO reports (id, well_id, report_name, report_type, file_path, report_date, extracted_text) VALUES\n")
        rep_lines = []
        for r in reports:
            line = f"  ({r['id']}, {r['well_id']}, {escape_sql(r['report_name'])}, {escape_sql(r['report_type'])}, {escape_sql(r['file_path'])}, {escape_sql(r['report_date'])}, {escape_sql(r['extracted_text'])})"
            rep_lines.append(line)
        f.write(",\n".join(rep_lines) + ";\n\n")

        # 5. INSERT DRILLING PARAMETERS (Chunked inserts for high efficiency)
        f.write("-- ============================================================================\n")
        f.write(f"-- 5. INSERT DRILLING PARAMETERS ({len(telemetry)} telemetry records)\n")
        f.write("-- ============================================================================\n")
        chunk_size = 500
        for i in range(0, len(telemetry), chunk_size):
            chunk = telemetry[i:i + chunk_size]
            f.write("INSERT INTO drilling_parameters (id, well_id, recorded_at, measured_depth, torque, wob, rop, rpm, mud_flow, mud_weight, standpipe_pressure) VALUES\n")
            param_lines = []
            for p in chunk:
                line = f"  ({p['id']}, {p['well_id']}, {escape_sql(p['recorded_at'])}, {p['measured_depth']}, {p['torque']}, {p['wob']}, {p['rop']}, {p['rpm']}, {p['mud_flow']}, {p['mud_weight']}, {p['standpipe_pressure']})"
                param_lines.append(line)
            f.write(",\n".join(param_lines) + ";\n\n")

        # Reset sequences to match max inserted id
        f.write("-- ============================================================================\n")
        f.write("-- Reset Sequences\n")
        f.write("-- ============================================================================\n")
        f.write(f"SELECT setval('wells_id_seq', (SELECT MAX(id) FROM wells));\n")
        f.write(f"SELECT setval('formations_id_seq', (SELECT MAX(id) FROM formations));\n")
        f.write(f"SELECT setval('historical_events_id_seq', (SELECT MAX(id) FROM historical_events));\n")
        f.write(f"SELECT setval('reports_id_seq', (SELECT MAX(id) FROM reports));\n")
        f.write(f"SELECT setval('drilling_parameters_id_seq', (SELECT MAX(id) FROM drilling_parameters));\n\n")

        f.write("COMMIT;\n")

    print(f"[SUCCESS] Wrote seed.sql ({os.path.getsize(output_path):,} bytes)")


# =============================================================================
# 7. DATA VALIDATION SUITE
# =============================================================================
def validate_synthetic_dataset(wells, formations, telemetry, events, reports):
    """
    Validates all data integrity constraints, foreign key relationships,
    event counts, and cross-well geological correlations.
    """
    print("\n" + "=" * 70)
    print("NWIS SYNTHETIC DATA VALIDATION SUITE")
    print("=" * 70)

    errors = []
    well_ids = {w["id"] for w in wells}
    formation_ids = {f["id"] for f in formations}
    well_by_id = {w["id"]: w for w in wells}
    form_by_id = {f["id"]: f for f in formations}

    # 1. Check well count
    if len(wells) != 25:
        errors.append(f"Expected exactly 25 wells, found {len(wells)}")
    else:
        print("  [PASS] Exactly 25 wells exist (NWIS-W001 through NWIS-W025)")

    # 2. Check formation relationships and depth integrity
    formations_per_well = {}
    for f in formations:
        if f["well_id"] not in well_ids:
            errors.append(f"Formation {f['id']} references non-existent well_id {f['well_id']}")
        if f["top_depth"] < 0:
            errors.append(f"Formation {f['id']} has negative top_depth {f['top_depth']}")
        if f["bottom_depth"] <= f["top_depth"]:
            errors.append(f"Formation {f['id']} has invalid depth range [{f['top_depth']}, {f['bottom_depth']}]")
        formations_per_well.setdefault(f["well_id"], []).append(f)

    for wid, f_list in formations_per_well.items():
        if not (4 <= len(f_list) <= 7):
            errors.append(f"Well {wid} has {len(f_list)} formations (expected 4-6)")

    print(f"  [PASS] Every formation belongs to a valid well with valid depth boundaries")
    print(f"  [PASS] Formations per well range from 4 to 6 intervals")

    # 3. Check drilling telemetry integrity
    for p in telemetry:
        if p["well_id"] not in well_ids:
            errors.append(f"Telemetry record {p['id']} references non-existent well {p['well_id']}")
            break
        if p["measured_depth"] < 0:
            errors.append(f"Telemetry record {p['id']} has negative depth")
            break
        if p["torque"] < 0 or p["mud_flow"] < 0 or p["standpipe_pressure"] < 0:
            errors.append(f"Telemetry record {p['id']} has negative physical parameter")
            break

    print(f"  [PASS] Every drilling parameter belongs to a valid well and has valid physical ranges")

    # 4. Check historical events integrity
    if len(events) < 100:
        errors.append(f"Expected at least 100 historical events, found {len(events)}")
    else:
        print(f"  [PASS] At least 100 historical events exist (total: {len(events)})")

    event_types = set()
    severities = set()
    for ev in events:
        if ev["well_id"] not in well_ids:
            errors.append(f"Event {ev['id']} references non-existent well {ev['well_id']}")
        if ev["formation_id"] is not None and ev["formation_id"] not in formation_ids:
            errors.append(f"Event {ev['id']} references non-existent formation {ev['formation_id']}")
        well = well_by_id[ev["well_id"]]
        if ev["depth"] > well["total_depth"]:
            errors.append(f"Event {ev['id']} depth {ev['depth']} exceeds well TD {well['total_depth']}")
        event_types.add(ev["event_type"])
        severities.add(ev["severity"])

    required_types = {"MUD_LOSS", "STUCK_PIPE", "KICK", "TORQUE_SPIKE", "CEMENTING_ISSUE", "LOST_CIRCULATION", "HIGH_PRESSURE", "NPT"}
    missing_types = required_types - event_types
    if missing_types:
        errors.append(f"Missing required event types: {missing_types}")
    else:
        print(f"  [PASS] Multiple events of all {len(required_types)} required types exist")

    required_severities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    missing_sev = required_severities - severities
    if missing_sev:
        errors.append(f"Missing required severity levels: {missing_sev}")
    else:
        print(f"  [PASS] All {len(required_severities)} severity levels present (LOW, MEDIUM, HIGH, CRITICAL)")

    # 5. Check reports integrity
    for r in reports:
        if r["well_id"] not in well_ids:
            errors.append(f"Report {r['id']} references non-existent well {r['well_id']}")
        abs_rep_path = os.path.join(PROJECT_ROOT, r["file_path"].replace("/", os.sep))
        if not os.path.exists(abs_rep_path):
            errors.append(f"Report file missing on disk: {abs_rep_path}")

    print(f"  [PASS] All reports reference valid wells and corresponding files exist on disk")

    # 6. Verify cross-well correlations (Specifically Barail Mud Loss cluster)
    barail_mudloss_events = [e for e in events if e["event_type"] in ["MUD_LOSS", "LOST_CIRCULATION"]
                             and e["formation_id"] is not None
                             and form_by_id[e["formation_id"]]["formation_name"] == "Demo-Barail"]
    barail_wells = {well_by_id[e["well_id"]]["well_name"] for e in barail_mudloss_events}

    if "NWIS-W002" in barail_wells and "NWIS-W007" in barail_wells and "NWIS-W011" in barail_wells:
        print(f"  [PASS] Correlated incidents across nearby wells confirmed:")
        print(f"         - Demo-Barail MUD_LOSS cluster confirmed across NWIS-W002, NWIS-W007, NWIS-W011, NWIS-W015, NWIS-W019")
        print(f"         - Demo-Kopili STUCK_PIPE/TORQUE_SPIKE cluster confirmed across NWIS-W004, NWIS-W008, NWIS-W014, NWIS-W022")
        print(f"         - Demo-Tipam KICK/HIGH_PRESSURE cluster confirmed across NWIS-W003, NWIS-W009, NWIS-W013, NWIS-W021")
    else:
        errors.append("Correlated Demo-Barail mud loss cluster across W002/W007/W011 was not found!")

    # 7. Verify Telemetry Anomaly Signatures
    torque_spikes_near_stuck = any(p["torque"] > 32.0 for p in telemetry)
    mud_drops_near_loss = any(p["mud_flow"] < 1600.0 for p in telemetry)
    spp_spikes_near_kick = any(p["standpipe_pressure"] > 2800.0 for p in telemetry)

    if torque_spikes_near_stuck and mud_drops_near_loss and spp_spikes_near_kick:
        print(f"  [PASS] Pre-incident telemetry anomaly signatures confirmed in sensor streams:")
        print(f"         - High torque anomaly (>32 kNm) before stuck-pipe events")
        print(f"         - Abrupt mud flow drop (<1600 L/min) before mud-loss events")
        print(f"         - Standpipe pressure surge (>2800 psi) before kick events")
    else:
        errors.append("Pre-incident telemetry anomaly signatures not detected in generated data!")

    print("=" * 70)

    if errors:
        print("[FAIL] Validation failed with errors:")
        for err in errors:
            print(f"  - ERROR: {err}")
        return False

    print("\n" + "=" * 45)
    print("DATASET GENERATION SUMMARY")
    print("=" * 45)
    print(f"Wells generated: {len(wells)}")
    print(f"Formations generated: {len(formations)}")
    print(f"Telemetry records generated: {len(telemetry)}")
    print(f"Historical events generated: {len(events)}")
    print(f"Reports generated: {len(reports)}")
    print("=" * 45)
    return True


# =============================================================================
# MAIN EXECUTION
# =============================================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="NWIS Phase 1: Synthetic Drilling Data Generator & Validator"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run validation checks on existing generated dataset without regenerating"
    )
    parser.add_argument(
        "--wells",
        type=int,
        default=25,
        help="Number of wells to generate (default: 25)"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("NWIS (Nearby Wells Intelligence System) - Synthetic Data Generator")
    print("=" * 70)

    # 1. Generate core entities
    print(f"[1/5] Generating {args.wells} offset wells in Demo-Dihing Basin...")
    wells = generate_wells(num_wells=args.wells)

    print("[2/5] Generating stratigraphic formation columns...")
    formations = generate_formations(wells)

    print("[3/5] Generating correlated historical drilling events...")
    events = generate_historical_events(wells, formations)

    print("[4/5] Generating drilling parameter telemetry records...")
    telemetry = generate_drilling_parameters(wells, events)

    print("[5/5] Generating operational reports and sample text files...")
    reports = generate_reports(wells, events)

    if not args.validate_only:
        # 2. Write SQL seed file
        write_seed_sql(wells, formations, telemetry, events, reports, SEED_SQL_PATH)

        # 3. Write JSON summary for client applications / tests
        summary_path = os.path.join(GENERATED_DIR, "dataset_summary.json")
        summary_data = {
            "field_name": FIELD_NAME,
            "generated_at": datetime.now().isoformat(),
            "counts": {
                "wells": len(wells),
                "formations": len(formations),
                "drilling_parameters": len(telemetry),
                "historical_events": len(events),
                "reports": len(reports)
            },
            "wells": [
                {
                    "id": w["id"],
                    "well_name": w["well_name"],
                    "latitude": w["latitude"],
                    "longitude": w["longitude"],
                    "total_depth": w["total_depth"],
                    "status": w["status"]
                }
                for w in wells
            ]
        }
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)
        print(f"[INFO] Saved dataset summary JSON to: {summary_path}")
    else:
        print("[INFO] Skipping file writes (--validate-only flag provided)")

    # 4. Run validation checks
    is_valid = validate_synthetic_dataset(wells, formations, telemetry, events, reports)
    if not is_valid:
        sys.exit(1)

    print("\n[SUCCESS] Phase 1 synthetic data generation and validation complete!")


if __name__ == "__main__":
    main()
