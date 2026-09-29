# NWIS Backend API
### Nearby Wells Intelligence System — Phase 2: Core Backend API

---

## 1. Overview

The **NWIS Backend API** is built using **FastAPI** and **SQLAlchemy** to connect to the PostgreSQL database established in Phase 1. It exposes high-performance RESTful endpoints to query:
- Well catalogs and geospatial proximity searches (using the Haversine formula)
- Stratigraphic formation intervals
- Categorized historical drilling incidents, hazards, and mitigations
- High-frequency sensor telemetry parameters (torque, WOB, ROP, RPM, mud flow, SPP)
- Real-time simulated active-well telemetry streams for the upcoming Phase 3 dashboard
- Service and database health monitoring

> [!NOTE]
> **Data Disclaimer:**
> All data returned by this API is **100% synthetic demonstration data** created for the SIH prototype. It does **NOT** represent actual, operational, or confidential data from Oil India Limited (OIL), ONGC, or any other commercial operator.

---

## 2. Backend Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application setup, CORS, and health checks
│   ├── database.py                 # SQLAlchemy engine, session maker, & get_db dependency
│   ├── models/                     # SQLAlchemy ORM models matching Phase 1 schema
│   │   ├── __init__.py
│   │   ├── well.py                 # wells table model
│   │   ├── formation.py            # formations table model
│   │   ├── drilling_parameter.py   # drilling_parameters telemetry model
│   │   └── historical_event.py     # historical_events incidents model
│   ├── schemas/                    # Pydantic v2 validation & response models
│   │   ├── __init__.py
│   │   ├── well.py                 # WellResponse, NearbyWellResponse
│   │   ├── formation.py            # FormationResponse, FormationSummary
│   │   ├── drilling_parameter.py   # TelemetryResponse, ActiveTelemetryResponse
│   │   └── historical_event.py     # HistoricalEventResponse, WellHistoryEvent
│   └── routers/                    # Endpoint route handlers
│       ├── __init__.py
│       ├── wells.py                # /api/wells, /nearby, /{id}, /{id}/history
│       ├── formations.py           # /api/formations, /{id}/formations
│       ├── events.py               # /api/events, /{id}
│       └── telemetry.py            # /api/wells/active/telemetry, /{id}/telemetry
│
├── tests/                          # Integration test suite
│   ├── __init__.py
│   └── test_api.py                 # 19 comprehensive API integration tests
│
├── requirements.txt                # Python backend dependencies
├── .env.example                    # Environment variables template
├── .env                            # Active environment configuration
└── README.md                       # Backend documentation & guide
```

---

## 3. Prerequisites & Setup

### Step 1: Navigate to the Backend Directory
```powershell
cd d:\SIH\NWIS\backend
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

Ensure `.env` matches your database configuration:
```ini
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=nwis_db
DATABASE_USER=nwis_user
DATABASE_PASSWORD=nwis_password

API_PORT=8000
API_HOST=0.0.0.0

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
```

### Step 3: Install Dependencies
```powershell
py -m pip install -r requirements.txt
```

---

## 4. Running the Backend Server

Start FastAPI with Uvicorn:
```powershell
py -m uvicorn app.main:app --reload --port 8000
```

Once running:
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Database Health**: [http://localhost:8000/api/health/db](http://localhost:8000/api/health/db)

---

## 5. Implemented API Endpoints

### 1. Health Checks
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status and version. |
| `GET` | `/api/health/db` | Verifies active PostgreSQL connectivity. |

### 2. Wells APIs
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/wells` | Lists all 25 wells (supports `status` and `field_name` filtering). |
| `GET` | `/api/wells/nearby` | Haversine distance search. Requires `lat`, `long`, `radius` (km). Returns wells sorted by proximity. |
| `GET` | `/api/wells/{well_id}` | Detailed metadata for a single well. Returns 404 if not found. |
| `GET` | `/api/wells/{well_id}/history` | Historical drilling incident timeline for a well (filters by `formation`, `event_type`, `severity`). |
| `GET` | `/api/wells/{well_id}/formations` | Stratigraphic formation intervals for a well, sorted by top depth. |

### 3. Formations APIs
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/formations` | Basin geological column summary with well penetration counts and typical depth boundaries. |

### 4. Historical Events APIs
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/events` | Multi-parameter search across incidents (`well_id`, `event_type`, `severity`, `formation`, `min_depth`, `max_depth`). |
| `GET` | `/api/events/{event_id}` | Full engineering narrative, root cause, and mitigation for a single event. |

### 5. Telemetry APIs
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/wells/active/telemetry` | Real-time simulated telemetry stream for designated active/demo well (`NWIS-W025`). |
| `GET` | `/api/wells/{well_id}/telemetry` | Historical sensor telemetry records (`start_depth`, `end_depth`, `limit`). |

---

## 6. Running Tests

The test suite validates all endpoints, edge cases (invalid IDs, negative radius, inverted depth ranges), and database connectivity:

```powershell
py tests/test_api.py
```

**Expected Result:**
```
Ran 19 tests in 0.540s
OK
```

---

## 7. Next Steps (Phase 3 Preview)

The backend is now fully prepared for **Phase 3: React + Leaflet Frontend Dashboard**, which will consume these endpoints to render:
- Interactive 2D map of offset wells with radius circle
- Real-time telemetry gauge cards (Torque, WOB, ROP, SPP)
- Stratigraphic well correlation logs
- Offset hazard timeline and incident alert indicators
