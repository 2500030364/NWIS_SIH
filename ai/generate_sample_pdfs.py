"""
===============================================================================
NWIS Sample PDF Reports Generator
===============================================================================
Generates 8 realistic synthetic drilling reports (DDR, WCR, Mud Log, Incident)
in PDF format inside data/reports/ consistent with the Phase 1 database.

NOTICE: Synthetic demonstration documents for SIH prototype.
        NOT actual Oil India Limited (OIL) or ONGC operational reports.
===============================================================================
"""

import os
from typing import List, Dict, Any

# Target directory
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "reports"))
os.makedirs(REPORTS_DIR, exist_ok=True)


SAMPLE_REPORTS_DATA = [
    {
        "filename": "NWIS-W002_Daily_Drilling_Report_Mud_Loss.pdf",
        "title": "DAILY DRILLING REPORT (DDR) - RIG 04",
        "well_name": "NWIS-W002",
        "report_type": "DDR",
        "date": "2024-04-18",
        "depth": 2980.0,
        "formation": "Demo-Barail",
        "event_type": "MUD_LOSS",
        "severity": "HIGH",
        "sections": [
            ("OPERATIONAL SUMMARY",
             "Drilled 8-1/2 inch hole section from 2940m to 2980m in Demo-Barail formation.\n"
             "At 2980m measured depth, severe dynamic mud loss was observed at surface.\n"
             "Loss rate abruptly exceeded 45 bbls/hr (7.15 m3/hr). Standpipe pressure dropped from 2350 psi to 1920 psi."),
            ("ROOT CAUSE ANALYSIS",
             "Penetrated depleted pore pressure sandstone reservoir with subnormal pressure gradient (~0.38 psi/ft).\n"
             "Excess hydrostatic head from 1.34 SG active drilling mud exceeded formation breakdown pressure,\n"
             "inducing fracture opening in permeable Barail sand facies."),
            ("CORRECTIVE MITIGATION",
             "1. Immediately reduced circulation rate from 2400 L/min to 1600 L/min.\n"
             "2. Mixed and spotted 50 bbls coarse calcium carbonate (CaCO3) Loss Circulation Material (LCM) pill.\n"
             "3. Reduced active mud weight to 1.22 SG using low-solids water-based polymer mud.\n"
             "4. Staged resumption of drilling; loss rate successfully arrested to <2 bbls/hr seepage.")
        ]
    },
    {
        "filename": "NWIS-W004_Incident_Report_Stuck_Pipe.pdf",
        "title": "DRILLING INCIDENT REPORT - STUCK PIPE",
        "well_name": "NWIS-W004",
        "report_type": "INCIDENT_REPORT",
        "date": "2021-09-12",
        "depth": 3520.0,
        "formation": "Demo-Kopili Shale",
        "event_type": "STUCK_PIPE",
        "severity": "HIGH",
        "sections": [
            ("INCIDENT DESCRIPTION",
             "While pulling out of hole (POOH) for bit change at 3520m in Demo-Kopili Shale,\n"
             "drillstring became mechanically stuck. Overpull exceeded 75 tons with zero upward movement.\n"
             "Surface rotary torque spiked up to 39.5 kNm prior to string stalling."),
            ("ROOT CAUSE INVESTIGATION",
             "Highly reactive smectite-rich Kopili marine shale experienced severe chemical hydration\n"
             "and borehole breakout due to insufficient potassium chloride (KCl) inhibition in the mud.\n"
             "Large cavings sloughed into the borehole cavity, causing severe mechanical pack-off around the 8-1/2 inch BHA."),
            ("REMEDIAL MITIGATION",
             "1. Pumped 40 bbls glycol-weighted lubricant pill across the stuck interval.\n"
             "2. Engaged hydraulic drilling jar upward at 70 tons combined with string torque working.\n"
             "3. String came free after 6.5 hours of continuous jarring operations.\n"
             "4. Circulated high-viscosity sweep to carry shale cavings to surface; densified mud to 1.35 SG.")
        ]
    },
    {
        "filename": "NWIS-W003_Mud_Log_Evaluation_Gas_Kick.pdf",
        "title": "MUD LOGGING GEOLOGICAL EVALUATION & WELL CONTROL",
        "well_name": "NWIS-W003",
        "report_type": "MUD_LOG",
        "date": "2024-05-18",
        "depth": 2240.0,
        "formation": "Demo-Tipam Sandstone",
        "event_type": "KICK",
        "severity": "HIGH",
        "sections": [
            ("LITHOLOGICAL EVALUATION",
             "Drilling 12-1/4 inch hole section in Demo-Tipam Sandstone (1620m - 2480m).\n"
             "Clean, porous, sub-angular to sub-rounded quartzose sandstone. Visible porosity 22-26%.\n"
             "At 2240m, sudden drilling break observed (ROP jumped from 9 m/hr to 26 m/hr)."),
            ("WELL CONTROL INCIDENT",
             "Flow check performed: positive flow detected with mud pumps off. Pit gain of 18 bbls recorded.\n"
             "Encountered abnormal high-pressure gas pocket charging permeable Tipam sandstone lenses.\n"
             "Total gas on mud log detector peaked at 48% with significant methane (C1) and ethane (C2) readings."),
            ("WELL KILL MITIGATION",
             "1. Shut in well on annular preventer; recorded initial pressures: SIDPP = 340 psi, SICP = 460 psi.\n"
             "2. Formulated kill mud calculation: raised required mud weight from 1.18 SG to 1.30 SG.\n"
             "3. Executed Wait-and-Weight kill method; circulated gas kick bubble out safely via choke manifold.\n"
             "4. Verified zero trapped pressure; resumed controlled drilling operations.")
        ]
    },
    {
        "filename": "NWIS-W005_Cementing_Evaluation_Report.pdf",
        "title": "INTERMEDIATE CASING CEMENTING EVALUATION",
        "well_name": "NWIS-W005",
        "report_type": "DRILLING_REPORT",
        "date": "2022-04-10",
        "depth": 1620.0,
        "formation": "Demo-Girujan Clay",
        "event_type": "CEMENTING_ISSUE",
        "severity": "HIGH",
        "sections": [
            ("OPERATIONAL DESCRIPTION",
             "Ran 9-5/8 inch intermediate casing to 1620m across Demo-Girujan Clay interval.\n"
             "Pumped 450 sacks of Class G cement slurry followed by 1.25 SG displacement mud.\n"
             "Cement top found lower than calculated; post-job Cement Bond Log (CBL) revealed channeling."),
            ("ROOT CAUSE ANALYSIS",
             "Inadequate mud displacement efficiency and gas channeling through setting cement slurry.\n"
             "Washouts in soft Girujan clay sections prevented laminar slurry placement."),
            ("REMEDIAL MITIGATION",
             "1. Perforated 9-5/8 inch casing at 1580m using 4-inch casing guns (4 SPF).\n"
             "2. Established pump-in injection rate and performed remedial cement squeeze with micro-fine cement.\n"
             "3. Pressure tested squeeze interval to 2500 psi for 15 minutes; successfully sealed annulus.")
        ]
    },
    {
        "filename": "NWIS-W007_Drilling_Report_Lost_Circulation.pdf",
        "title": "OFFSET DRILLING REPORT - LOSS CIRCULATION",
        "well_name": "NWIS-W007",
        "report_type": "DRILLING_REPORT",
        "date": "2024-03-24",
        "depth": 3010.0,
        "formation": "Demo-Barail",
        "event_type": "MUD_LOSS",
        "severity": "HIGH",
        "sections": [
            ("INCIDENT OVERVIEW",
             "Drilling 8-1/2 inch hole section in Demo-Barail mature oil reservoir sand at 3010m.\n"
             "Experienced severe mud loss into depleted offset reservoir; 50 bbls active pit loss in 35 minutes.\n"
             "This matches the identical thief zone behavior observed in nearby well NWIS-W002 at 2980m."),
            ("GEOLOGICAL INTERPRETATION",
             "Inter-well pressure depletion communication across permeable Barail channel facies.\n"
             "Regional reservoir pressure drawdown requires lower equivalent circulating density (ECD)."),
            ("ACTION PLAN & MITIGATION",
             "1. Mixed 45 bbls high-fluid-loss squeeze LCM pill with blended cellulosic fibers and nut plug.\n"
             "2. Squeezed pill into thief formation at 3010m; hesitation squeeze held 250 psi.\n"
             "3. Reduced circulation rate to 1750 L/min and reduced mud weight from 1.32 to 1.21 SG.")
        ]
    },
    {
        "filename": "NWIS-W008_Incident_Report_Severe_Packoff.pdf",
        "title": "MAJOR HAZARD REPORT - STRING PACK-OFF & NPT",
        "well_name": "NWIS-W008",
        "report_type": "INCIDENT_REPORT",
        "date": "2024-05-28",
        "depth": 3560.0,
        "formation": "Demo-Kopili Shale",
        "event_type": "STUCK_PIPE",
        "severity": "CRITICAL",
        "sections": [
            ("OPERATIONAL NARRATIVE",
             "While reaming tight hole section at 3560m in deep Demo-Kopili Shale, severe mechanical pack-off occurred.\n"
             "Standpipe pressure spiked to 3800 psi (pressure relief valve triggered). Rotation stalled completely."),
            ("CAUSE INVESTIGATION",
             "Deep overpressured Kopili marine shale spalling due to insufficient mud weight (1.28 SG).\n"
             "Severe borehole ovalization and stress-induced spalling created thick debris bed around stabilizers."),
            ("MITIGATION & RECOVERY",
             "1. Disengaged top drive; applied maximum allowable upward jar impacts (75 tons overpull).\n"
             "2. Spotted concentrated acid wash followed by synthetic oil-based lubricant pill.\n"
             "3. Drillstring freed after 14 hours of jarring; total 32 hours Non-Productive Time (NPT) logged.\n"
             "4. Raised drilling mud weight to 1.38 SG to provide adequate mechanical borehole support.")
        ]
    },
    {
        "filename": "NWIS-W001_Well_Completion_Report.pdf",
        "title": "WELL COMPLETION & TESTING REPORT",
        "well_name": "NWIS-W001",
        "report_type": "WCR",
        "date": "2021-11-15",
        "depth": 3561.82,
        "formation": "Demo-Barail",
        "event_type": "NPT",
        "severity": "LOW",
        "sections": [
            ("FINAL WELL ARCHITECTURE",
             "Target Reservoir: Demo-Barail Sandstone.\n"
             "Final Drilled True Vertical Depth: 3561.82m TVD.\n"
             "7-inch production liner set from 2650m to 3540m; cemented with Class G neat cement."),
            ("PERFORATION & TESTING",
             "Perforated interval: 3012.0m to 3028.0m with 4-1/2 inch tubing-conveyed perforating (TCP) guns (6 SPF).\n"
             "Initial reservoir pressure measured at 3820 psi. Flow tested through 24/64 inch adjustable choke.\n"
             "Tubing Head Pressure: 1420 psi. Produced clean sweet crude oil at commercial rates.\n"
             "Well handed over to production operations safely.")
        ]
    },
    {
        "filename": "NWIS-W011_Daily_Drilling_Report.pdf",
        "title": "DAILY DRILLING REPORT #34",
        "well_name": "NWIS-W011",
        "report_type": "DDR",
        "date": "2024-01-20",
        "depth": 3040.0,
        "formation": "Demo-Barail",
        "event_type": "MUD_LOSS",
        "severity": "MEDIUM",
        "sections": [
            ("DAILY OPERATIONS SUMMARY",
             "Drilling 8-1/2 inch hole from 2990m to 3040m in Demo-Barail sandstone.\n"
             "Observed moderate dynamic seepage loss of 20 bbls/hr at 3040m depth.\n"
             "Loss rate correlates with depleted reservoir fault block communicated from offset well NWIS-W002."),
            ("TREATMENT & STABILIZATION",
             "1. Added fine and medium ground walnut shells and mica flakes directly to active mud system.\n"
             "2. Adjusted mud rheology: plastic viscosity (PV) 18 cP, yield point (YP) 22 lb/100ft2.\n"
             "3. Seepage reduced to <3 bbls/hr within 45 minutes; continued drilling smoothly.")
        ]
    }
]


def create_pdf_with_fitz(report_data: Dict[str, Any], output_path: str):
    """Generates standard PDF using PyMuPDF (fitz)."""
    import fitz

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size

    y = 50

    # Header Banner
    page.draw_rect(fitz.Rect(40, y, 555, y + 55), color=(0.1, 0.2, 0.5), fill=(0.92, 0.95, 1.0))
    page.insert_text(fitz.Point(50, y + 22), report_data["title"], fontsize=13, fontname="helv", color=(0.1, 0.2, 0.5))
    page.insert_text(
        fitz.Point(50, y + 42),
        "SYNTHETIC DEMONSTRATION DOCUMENT - NOT REAL OPERATIONAL DATA (SIH PROTOTYPE)",
        fontsize=8, fontname="helv", color=(0.6, 0.1, 0.1)
    )
    y += 75

    # Key Metadata Table
    page.draw_rect(fitz.Rect(40, y, 555, y + 60), color=(0.7, 0.7, 0.7), fill=(0.97, 0.97, 0.97))
    page.insert_text(fitz.Point(50, y + 20), f"WELL IDENTIFIER: {report_data['well_name']}", fontsize=10, fontname="helv")
    page.insert_text(fitz.Point(300, y + 20), f"OPERATIONAL DATE: {report_data['date']}", fontsize=10, fontname="helv")
    page.insert_text(fitz.Point(50, y + 38), f"FORMATION: {report_data['formation']}", fontsize=10, fontname="helv")
    page.insert_text(fitz.Point(300, y + 38), f"MEASURED DEPTH: {report_data['depth']} m", fontsize=10, fontname="helv")
    page.insert_text(fitz.Point(50, y + 54), f"EVENT TYPE: {report_data['event_type']}", fontsize=10, fontname="helv")
    page.insert_text(fitz.Point(300, y + 54), f"SEVERITY LEVEL: {report_data['severity']}", fontsize=10, fontname="helv")
    y += 80

    # Sections
    for sec_title, sec_content in report_data["sections"]:
        page.insert_text(fitz.Point(50, y), sec_title, fontsize=11, fontname="helv", color=(0.15, 0.25, 0.45))
        y += 16
        for line in sec_content.split("\n"):
            page.insert_text(fitz.Point(50, y), line.strip(), fontsize=9.5, fontname="helv")
            y += 14
        y += 12

    # Footer
    page.insert_text(
        fitz.Point(50, 810),
        "NWIS — Nearby Wells Intelligence System | Document Intelligence Phase 3 Prototype",
        fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5)
    )

    doc.save(output_path)
    doc.close()


def create_minimal_pdf(report_data: Dict[str, Any], output_path: str):
    """
    Fallback: Generates a 100% compliant pure-Python PDF 1.4 file
    without external libraries.
    """
    text_content = (
        f"{report_data['title']}\n"
        f"SYNTHETIC DEMONSTRATION DOCUMENT - NOT REAL OPERATIONAL DATA (SIH PROTOTYPE)\n\n"
        f"WELL: {report_data['well_name']} | DATE: {report_data['date']}\n"
        f"FORMATION: {report_data['formation']} | DEPTH: {report_data['depth']}m\n"
        f"EVENT TYPE: {report_data['event_type']} | SEVERITY: {report_data['severity']}\n\n"
    )
    for sec_title, sec_content in report_data["sections"]:
        text_content += f"{sec_title}:\n{sec_content}\n\n"

    # Escape PDF text
    pdf_escaped = text_content.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream_content = f"BT\n/F1 10 Tf\n50 780 Td\n14 TL\n"
    for line in pdf_escaped.split("\n"):
        stream_content += f"({line}) '\n"
    stream_content += "ET\n"

    stream_bytes = stream_content.encode("latin-1", "replace")
    stream_len = len(stream_bytes)

    pdf_body = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"5 0 obj\n<< /Length " + str(stream_len).encode("ascii") + b" >>\nstream\n"
        + stream_bytes +
        b"\nendstream\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000236 00000 n \n"
        b"0000000307 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(307 + stream_len + 30).encode("ascii") +
        b"\n%%EOF\n"
    )

    with open(output_path, "wb") as f:
        f.write(pdf_body)


def generate_all_sample_reports():
    """Generates all 8 synthetic demonstration PDF reports in data/reports/."""
    print(f"[INFO] Generating {len(SAMPLE_REPORTS_DATA)} synthetic demonstration PDFs in: {REPORTS_DIR}")

    try:
        import pymupdf as fitz
        use_fitz = True
    except ImportError:
        try:
            import fitz
            use_fitz = True
        except ImportError:
            use_fitz = False

    generated_files = []
    for rep in SAMPLE_REPORTS_DATA:
        out_path = os.path.join(REPORTS_DIR, rep["filename"])
        if use_fitz:
            create_pdf_with_fitz(rep, out_path)
        else:
            create_minimal_pdf(rep, out_path)
        generated_files.append(out_path)
        print(f"  [+] Created: {rep['filename']} ({os.path.getsize(out_path):,} bytes)")

    print(f"[SUCCESS] All {len(generated_files)} synthetic demonstration reports created successfully.")
    return generated_files


if __name__ == "__main__":
    generate_all_sample_reports()
