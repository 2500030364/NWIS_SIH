# NWIS — Nearby Wells Intelligence System
### AI-Powered Decision-Support Platform for Petroleum Drilling Operations
**Smart India Hackathon (SIH) Prototype — Institutional Memory & Subsurface Risk Cockpit**

---

> [!IMPORTANT]
> **PROTOTYPE & SYNTHETIC DATA DISCLAIMER:**
> NWIS is an engineering decision-support prototype. It is **NOT** a certified well-control system and does not claim to predict real drilling events with absolute certainty. All well trajectories, stratigraphic tops, telemetry sensor streams, historical incidents, and reports in this repository are **100% synthetic demonstration data** modeled after the Upper Assam / Demo-Dihing Basin. They do **NOT** contain or represent actual, operational, or confidential data from Oil India Limited (OIL), ONGC, or any commercial operator.

---

## 1. Executive Summary & Problem Statement

During petroleum drilling operations, engineering teams face significant subsurface uncertainties:
- Sudden **mud loss and lost circulation** when drilling through depleted sands or fractured intervals.
- Severe **pipe sticking** in reactive, sloughing shales (e.g., Kopili Shale) leading to days of Non-Productive Time (NPT) and high fishing costs.
- High-pressure **gas kicks and influxes** requiring emergency well control actions.
- **Institutional knowledge loss**: Critical drilling learnings from previously drilled offset wells remain buried in hundreds of unstructured Daily Drilling Reports (DDRs) and Well Completion Reports (WCRs).

### The NWIS Solution
**NWIS (Nearby Wells Intelligence System)** delivers **"Institutional Memory"** straight to the drilling rig's operational cockpit by connecting 5 core pillars:
1. **Geospatial Offset Discovery**: Automatically locates offset wells within configurable radii (5 km, 10 km, 20 km) using great-circle Haversine calculations.
2. **Stratigraphic Formation Alignment**: Dynamically aligns the active bit depth with regional basin geological tops and bottoms.
3. **Transparent Smart Risk Engine**: Correlates historical offset incidents, depth intervals, and real-time sensor signatures (torque ramps, flow drops, standpipe pressure surges) into explainable alerts (LOW, MEDIUM, HIGH, CRITICAL).
4. **AI Document Intelligence**: Semantic retrieval of unstructured drilling reports via PyMuPDF text extraction, OCR fallback, SentenceTransformer dense vector embeddings (`all-MiniLM-L6-v2`), and high-speed FAISS vector similarity search.
5. **Industrial Operations Cockpit**: A modern, light-theme operational dashboard (inspired by modern control room ergonomics such as XpertTrack) featuring interactive Leaflet mapping, live sensor telemetry, historical timelines, and an Explainable Evidence Inspector.

---

## 2. System Architecture

```
                                  NWIS USER INTERFACE
                    Industrial Operations Cockpit (React + Vite + Leaflet)
                 ┌─────────────────────────────────────────────────────────┐
                 │  KPI Strip  │  Interactive Well Map  │  Live Telemetry  │
                 │  Risk Alerts│  Historical Search     │  Evidence Drawer │
                 └────────────────────────────┬────────────────────────────┘
                                              │ REST Polling / HTTP
                                              ▼
                                       FASTAPI BACKEND
                                   http://localhost:8000
                 ┌─────────────────────────────────────────────────────────┐
                 │  • /api/wells (Catalog & Haversine Nearby Search)       │
                 │  • /api/formations (Basin Stratigraphic Column)         │
                 │  • /api/events (Categorized Incidents & History)        │
                 │  • /api/telemetry (Depth-Indexed Sensor Channels)       │
                 │  • /api/search (FAISS Semantic Vector Retrieval)        │
                 │  • /api/risks & /api/alerts (Smart Risk Engine)         │
                 │  • /api/wells/active/step (Simulated Bit Progression)   │
                 └──────┬─────────────────────┬─────────────────────┬──────┘
                        │                     │                     │
           SQLAlchemy   ▼         Embeddings  ▼         Rules/Stats ▼
        ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
        │     POSTGRESQL      │ │   AI SEARCH ENGINE  │ │  SMART RISK ENGINE  │
        │    (Port 5433/5432) │ │  (FAISS + MinILM)   │ │  (Multi-Factor)     │
        │ • 25 Offset Wells   │ │ • PyMuPDF / OCR     │ │ • Formation Match   │
        │ • 153 Formations    │ │ • 384-dim Vectors   │ │ • Depth Proximity   │
        │ • 122 Past Events   │ │ • Semantic Chunks   │ │ • Telemetry Anomaly │
        │ • 4,375 Telemetry   │ │ • Report Excerpts   │ │ • Explainable Proof │
        └─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

---

## 3. Technology Stack

| Layer | Technologies Used | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19, Vite, Tailwind CSS v4, Lucide Icons | Responsive industrial operations cockpit interface |
| **Mapping** | Leaflet.js | Geospatial visualization of active well & offset clusters with radius circles |
| **Telemetry Viz** | Recharts | Multi-channel sensor telemetry trends (Torque, Mud Flow, SPP vs. Depth) |
| **Backend API** | FastAPI, Uvicorn, Pydantic v2 | High-performance asynchronous REST API with auto-generated OpenAPI/Swagger |
| **Relational DB** | PostgreSQL 16, SQLAlchemy 2.0, Psycopg2 | Master well catalog, stratigraphic tops, telemetry time-series, historical events |
| **Document Processing** | PyMuPDF (`fitz`), Tesseract OCR | Digital PDF text extraction with scanned document fallback |
| **Vector Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) | 384-dimensional dense semantic text representations |
| **Vector Search** | FAISS (`faiss-cpu`, IndexFlatIP) | Sub-millisecond cosine similarity nearest-neighbor lookup |
| **Containerization** | Docker, Docker Compose, Nginx Alpine | Fully containerized multi-container deployment |

---

## 4. Complete Directory Structure

```
NWIS/
├── backend/
│   ├── app/
│   │   ├── models/             # SQLAlchemy ORM models (Well, Formation, Event, Telemetry, Report)
│   │   ├── schemas/            # Pydantic validation schemas (Well, Risk, Search, Telemetry)
│   │   ├── routers/            # FastAPI route handlers (wells, formations, events, risks, search)
│   │   ├── services/           # Business logic: RiskEngine, Telemetry pattern analyzer
│   │   ├── database.py         # PostgreSQL connection pool & session manager
│   │   └── main.py             # FastAPI application entrypoint & middleware
│   ├── tests/                  # Automated integration tests (test_api.py, test_risk_engine.py, test_search.py)
│   ├── Dockerfile              # Python 3.11-slim container with Tesseract & PyTorch/AI dependencies
│   ├── requirements.txt        # Backend dependencies
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/         # Cockpit UI components:
│   │   │   ├── Header.jsx      # Live rig telemetry badge & depth step controls
│   │   │   ├── KpiStrip.jsx    # 6 industrial status cards
│   │   │   ├── Sidebar.jsx     # Navigation tabs & active risk badge
│   │   │   ├── WellMap.jsx     # Leaflet map with pulsing active well & radius overlays
│   │   │   ├── WellDetailDrawer.jsx # Offset well attributes & event timeline
│   │   │   ├── TelemetryPanel.jsx   # Real-time sensor metrics & Recharts multi-line graph
│   │   │   ├── RiskAlertCenter.jsx  # Severity-tagged risk cards with filter controls
│   │   │   ├── RiskEvidenceModal.jsx# "Why Did NWIS Raise This Alert?" explainability modal
│   │   │   ├── HistoricalSearch.jsx # AI semantic report query engine
│   │   │   ├── DrillingIntelligenceView.jsx # Cross-well formation hazard analysis
│   │   │   └── ReportsView.jsx # Synthetic DDR/WCR report document library
│   │   ├── services/api.js     # Centralized REST client with fallback & error handling
│   │   ├── App.jsx             # Main cockpit state coordinator
│   │   └── index.css           # Modern industrial light palette (#F8F9F8, #1E2E1E, #E5A93C)
│   ├── nginx.conf              # Reverse proxy configuration for containerized deployment
│   ├── Dockerfile              # Multi-stage build (Node 20 build -> Nginx Alpine serve)
│   ├── package.json
│   └── vite.config.js
├── ai/
│   ├── document_processor.py   # PDF text extraction (PyMuPDF) + OCR fallback + metadata tagger
│   ├── text_chunker.py         # Overlapping semantic text chunker
│   ├── embeddings.py           # SentenceTransformer (all-MiniLM-L6-v2) embedding generator
│   ├── vector_store.py         # FAISS vector index manager (IndexFlatIP)
│   ├── generate_sample_pdfs.py # Synthetic demonstration PDF report generator
│   └── ingest.py               # Complete document ingestion pipeline CLI
├── database/
│   ├── schema.sql              # Relational schema DDL (tables, foreign keys, indexes, check constraints)
│   ├── seed.sql                # Pre-generated SQL inserts for 25 wells, formations, events, telemetry
│   └── generate_synthetic_data.py # Synthetic data generation engine with cross-well hazard clusters
├── data/
│   ├── reports/                # Operational PDF and text reports
│   └── generated/              # FAISS index (faiss_index.bin) and metadata (faiss_metadata.json)
├── docker-compose.yml          # 3-Tier orchestration: postgres + backend + frontend
├── .env.example                # Template configuration
├── .env                        # Local active environment configuration
└── README.md                   # Complete system documentation
```

---

## 5. Industrial Design Language (Cockpit UX)

The user interface follows the ergonomics of **modern industrial operations control rooms** (inspired by high-density, professional control interfaces like XpertTrack):

- **Dominant Light Palette**: 
  - Primary Background: Crisp Warm White / Off-White (`#F8F9F8` / `#FFFFFF`).
  - Dark Space: Deep Industrial Olive Green (`#1E2E1E` / `#2D422D`) used for navigation, headers, and primary emphasis.
  - Accent Color: Solid Mustard Gold (`#E5A93C`) used for active indicators, depth controls, and alert tags.
  - Alert Spectrum: Industrial Amber (`#D97706`) for High Risk, Crimson (`#DC2626`) for Critical Hazards, Emerald (`#16A34A`) for Normal status.
- **Operational Density**: High information density without visual clutter; cards prioritize telemetry values, units, and clear typography.
- **No Flashing/Gimmicks**: Clean status rings and subtle pulse badges that communicate live rig connectivity without distracting operations personnel.

---

## 6. How to Start the System

You can run NWIS either **locally on Windows via PowerShell** or **fully containerized using Docker**.

### Method A: Local Windows Execution (Recommended for Fast SIH Demo)

#### 1. Prerequisites Check
- **Python 3.10+**
- **Node.js 18+** & `npm`
- **PostgreSQL 15+** installed locally or running via Docker

#### 2. Configure Environment
In Windows PowerShell at `d:\SIH\NWIS`:
```powershell
Copy-Item .env.example .env
```
Ensure `.env` matches your local PostgreSQL credentials (default port is `5433` for custom local instances or `5432` for standard installs):
```ini
POSTGRES_DB=nwis_db
POSTGRES_USER=nwis_user
POSTGRES_PASSWORD=nwis_password
POSTGRES_PORT=5433
POSTGRES_HOST=127.0.0.1
DATABASE_URL=postgresql://nwis_user:nwis_password@127.0.0.1:5433/nwis_db
```

#### 3. Database Initialization (If Not Already Running)
If PostgreSQL is running, initialize the schema and demonstration dataset:
```powershell
# Execute schema and seed scripts
psql -h 127.0.0.1 -p 5433 -U nwis_user -d nwis_db -f database/schema.sql
psql -h 127.0.0.1 -p 5433 -U nwis_user -d nwis_db -f database/seed.sql
```

#### 4. Document Intelligence Ingestion
Generate demonstration PDF reports and build the FAISS vector index:
```powershell
# 1. Generate realistic synthetic PDF drilling reports
python -m ai.generate_sample_pdfs

# 2. Run the ingestion pipeline (extract -> chunk -> embed -> index)
python -m ai.ingest
```

#### 5. Launch FastAPI Backend
```powershell
cd d:\SIH\NWIS\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*API Swagger Documentation is available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

#### 6. Launch Industrial Cockpit Frontend
In a new PowerShell window:
```powershell
cd d:\SIH\NWIS\frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
*Cockpit UI is available at: [http://127.0.0.1:5173](http://127.0.0.1:5173)*

---

### Method B: Full Docker Compose Startup

To launch the complete PostgreSQL, FastAPI, and React Nginx stack in isolated containers:

```powershell
cd d:\SIH\NWIS
docker-compose up --build -d
```
- **Cockpit Dashboard**: [http://localhost:3000](http://localhost:3000)
- **FastAPI API & Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL**: `localhost:5432`

---

## 7. Automated Testing Suite

NWIS includes a multi-phase automated test suite covering APIs, the smart risk engine, and document search:

```powershell
# Run backend API integration tests (19 tests)
$env:PYTHONPATH="d:\SIH\NWIS\backend;d:\SIH\NWIS"; python backend/tests/test_api.py

# Run Smart Risk Engine & Explainability tests (8 tests)
$env:PYTHONPATH="d:\SIH\NWIS\backend;d:\SIH\NWIS"; python backend/tests/test_risk_engine.py

# Run AI Document Semantic Search tests (8 tests)
$env:PYTHONPATH="d:\SIH\NWIS\backend;d:\SIH\NWIS"; python backend/tests/test_search.py
```

---

## 8. Core API Endpoints

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/api/health` | Service status and version |
| **Health** | `GET` | `/api/health/db` | Live PostgreSQL connectivity check |
| **Wells** | `GET` | `/api/wells` | Catalog of 25 wells (filter by status, field) |
| **Wells** | `GET` | `/api/wells/{id}` | Specific well metadata, coordinates, and total depth |
| **Wells** | `GET` | `/api/wells/nearby` | Haversine geospatial proximity search (`lat`, `long`, `radius`) |
| **Formations**| `GET` | `/api/formations` | Basin stratigraphic column summary |
| **Formations**| `GET` | `/api/wells/{id}/formations`| Measured top and bottom depths for specific well |
| **Events** | `GET` | `/api/events` | Historical incidents catalog (filter by `event_type`, `severity`)|
| **Events** | `GET` | `/api/wells/{id}/history` | Chronological incident timeline for selected well |
| **Telemetry** | `GET` | `/api/wells/{id}/telemetry` | Sensor parameters (Torque, WOB, ROP, RPM, Mud Flow, SPP) |
| **Telemetry** | `GET` | `/api/wells/active/telemetry` | Real-time simulated telemetry for active drilling bit |
| **Simulation**| `GET` | `/api/wells/active/state` | Current simulated depth, formation, and active alert count |
| **Simulation**| `POST`| `/api/wells/active/step` | Advance/retreat simulated bit depth (`delta_m`) |
| **Simulation**| `POST`| `/api/wells/active/set_depth`| Explicitly jump simulated bit to any measured depth |
| **Search** | `GET` | `/api/search` | Natural language semantic search over reports via FAISS |
| **Risks** | `GET` | `/api/risks/{id}` | Multi-factor risk evaluation across all 8 hazard categories |
| **Alerts** | `GET` | `/api/alerts/{id}` | Actionable alerts filtered by severity (MEDIUM, HIGH, CRITICAL) |

---

## 9. The SIH 3-Minute Demonstration Flow

Use this exact scripted walkthrough for hackathon evaluators to demonstrate the full end-to-end capabilities of NWIS.

### Minute 1: The Operational Challenge & Industrial Cockpit (0:00 - 1:00)
1. **Open the Cockpit**: Open [http://127.0.0.1:5173](http://127.0.0.1:5173).
2. **Present the Problem**:
   > *"Good morning, Jury. In deep drilling operations, institutional knowledge is lost across shifts and years. When an engineer drills a new well, they rarely know the exact hazard history of wells drilled 2 kilometers away. NWIS gives drilling engineers 'Institutional Memory'."*
3. **Show the KPI Strip**:
   - Point to `ACTIVE WELL: NWIS-W001`, `DEPTH: 3020 m`, `FORMATION: Demo-Barail`, and `NEARBY WELLS: 12`.
4. **Demonstrate Geospatial Offset Discovery**:
   - Show the **Interactive Well Map**. The active well is pulsing in mustard gold.
   - Toggle the radius buttons from `5 km` → `10 km` → `20 km`. Point out the dynamic concentric coverage circles.
   - Click offset well `NWIS-W002` (distance ~3.2 km). 
   - The **Well Detail Drawer** slides open, displaying its total depth, formations, and historical incidents (severe mud losses and torque spikes).

---

### Minute 2: Approaching a Hazard & Explainable AI Alerts (1:00 - 2:00)
1. **Observe Real-Time Telemetry**:
   - Scroll down to the **Live Drilling Telemetry** section.
   - Show the 7 real-time telemetry cards: Torque (24.8 kNm), Mud Flow (1680 L/min), Standpipe Pressure (2780 psi), WOB, ROP, RPM, and Mud Weight.
   - Show the multi-channel trend chart illustrating the recent mud flow drop and torque rise.
2. **Advance the Active Bit Depth**:
   - In the top header control, click the **`[+5m]`** button to simulate drilling from 3020m to 3025m.
   - Notice the telemetry and formation indicators update dynamically.
3. **Trigger the Risk Alert**:
   - Look at the **Risk & Operational Alert Center**.
   - An alert appears: `POTENTIAL MUD LOSS RISK — HIGH (Score: 0.81)`.
4. **Open the Explainability Inspector**:
   - Click **`[View Historical Evidence]`** on the alert card.
   - The modal opens: **"Why Did NWIS Raise This Alert?"**.
   - Show the jury the 4 pillars of explainability:
     - **Offset Well Evidence**: 3 nearby offset wells (`NWIS-W002`, `NWIS-W007`, `NWIS-W011`) suffered severe mud loss in this exact formation (`Demo-Barail`).
     - **Depth Interval Proximity**: Historical incidents occurred between 2980m and 3040m. The current bit depth (3025m) falls squarely inside this historical hazard window.
     - **Sensor Telemetry Signatures**: Mud flow dropped below 1750 L/min, and SPP declined.
     - **Recommended Mitigations**: Pre-treat mud system with medium-sized LCM (Lost Circulation Material) prior to penetrating sand intervals.
   - Highlight: *"NWIS is not a black box—every alert is backed by auditable engineering proof."*

---

### Minute 3: Unstructured Intelligence Retrieval via AI Vector Search (2:00 - 3:00)
1. **Navigate to Historical Search**:
   - Click **`Historical Search`** on the left sidebar.
2. **Execute a Natural Language Query**:
   - Type or click the quick chip: `"mud loss around 3000m in Demo-Barail"`.
   - Click **`Search Historical Intelligence`**.
3. **Show Semantic Excerpt Retrieval**:
   - Sub-millisecond response from FAISS.
   - Show the top retrieved report from `NWIS-W002` (Daily Drilling Report).
   - Point out the extracted paragraph describing: *"Encountered severe total mud loss of 45 bbl/hr at 3010m in Barail sandstone. Pushed 35 bbl mica LCM pill with positive pill squeeze."*
4. **Show Cross-Well Drilling Intelligence**:
   - Click **`Well Intelligence`** in the sidebar.
   - Point to the cross-well hazard summary answering: *"What happened in nearby offset wells when they drilled through Demo-Barail?"*
   - Show the hazard distribution chart (65% Mud Loss, 25% Stuck Pipe).
5. **Conclude with Impact**:
   > *"By connecting geospatial offset history, live telemetry signatures, and unstructured drilling reports into an explainable cockpit, NWIS prevents multi-million dollar NPT incidents and protects crew safety. Thank you!"*

---

## 10. Known Prototype Limitations

- **Simulated Active Well**: Real-time rig data is simulated via REST polling and depth stepping rather than live WITSML / OPC-UA / Kafka rig feeds.
- **Stratigraphic Correlation**: Assumes horizontally continuous geological layers; fault throws and dipping beds are modeled as regional depth bounds rather than 3D seismic structural models.
- **OCR Engine**: Scanned PDF fallback relies on local Tesseract OCR. For low-resolution or handwritten rig logs, performance depends on scan DPI.
- **Vector Search Model**: Uses `all-MiniLM-L6-v2` (384-dim). In enterprise production, domain-specific fine-tuned petroleum embeddings would further improve specialized terminology matching.
