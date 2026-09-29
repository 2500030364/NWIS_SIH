"""
===============================================================================
NWIS (Nearby Wells Intelligence System) - FastAPI Main Application
===============================================================================
Phase 2: Core Backend API
===============================================================================
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.database import check_db_connection
from app.routers.wells import router as wells_router
from app.routers.formations import router as formations_router
from app.routers.events import router as events_router
from app.routers.telemetry import router as telemetry_router
from app.routers.search import router as search_router
from app.routers.risks import router as risks_router
from app.routers.reports import router as reports_router
from app.routers.assistant import router as assistant_router
from fastapi.staticfiles import StaticFiles

load_dotenv()


# API Metadata & Swagger descriptions
API_DESCRIPTION = """
### NWIS — Nearby Wells Intelligence System (Phase 2: Core Backend API)

NWIS is an AI-powered decision-support platform for petroleum drilling operations.
This backend API provides structured access to:
- **Wells**: Master well catalog and Haversine geospatial proximity search
- **Formations**: Stratigraphic intervals and basin geological column
- **Historical Events**: Categorized drilling incidents, root causes, and engineering mitigations
- **Telemetry**: Depth-indexed sensor telemetry parameters and active-well simulation
- **Health**: Service and database connectivity monitoring

> **NOTICE / DISCLAIMER:**
> All data served by this API is **100% synthetic demonstration data** created for the
> Smart India Hackathon (SIH) prototype. It does **NOT** represent actual, operational,
> or confidential data from Oil India Limited (OIL), ONGC, or any other commercial operator.
"""

app = FastAPI(
    title="NWIS — Nearby Wells Intelligence System API",
    description=API_DESCRIPTION,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# -----------------------------------------------------------------------------
# CORS Configuration (Ready for Phase 3 React + Leaflet frontend)
# -----------------------------------------------------------------------------
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
)
allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Error Handling (Shield raw SQL and database internals from API clients)
# -----------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", [])])
        msg = err.get("msg", "Invalid parameter")
        errors.append({"field": field, "message": msg})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed.", "errors": errors}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Hide raw internal tracebacks/SQL errors from clients
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact the API administrator."}
    )


# -----------------------------------------------------------------------------
# Health Check Endpoints
# -----------------------------------------------------------------------------
@app.get(
    "/api/health",
    tags=["Health"],
    summary="Service Health Check",
    description="Returns the operational status of the NWIS Backend API service."
)
def get_service_health():
    return {
        "status": "healthy",
        "service": "NWIS Backend",
        "version": "1.0.0"
    }


@app.get(
    "/api/health/db",
    tags=["Health"],
    summary="Database Connectivity Check",
    description="Tests if the backend can successfully connect and execute queries on the PostgreSQL database."
)
def get_database_health():
    is_reachable = check_db_connection()
    if is_reachable:
        return {
            "status": "connected",
            "database": "PostgreSQL",
            "reachable": True
        }
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "unreachable",
            "database": "PostgreSQL",
            "reachable": False,
            "error": "Could not connect to PostgreSQL database. Verify that the database is running."
        }
    )


# -----------------------------------------------------------------------------
# Include Routers
# -----------------------------------------------------------------------------
app.include_router(wells_router)
app.include_router(formations_router)
app.include_router(events_router)
app.include_router(telemetry_router)
app.include_router(search_router)
app.include_router(risks_router)
app.include_router(reports_router)
app.include_router(assistant_router)

# Mount static reports directory so PDF/text reports can be viewed/downloaded
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
REPORTS_DIR = os.path.join(PROJECT_ROOT, "data", "reports")
if os.path.exists(REPORTS_DIR):
    app.mount("/reports_static", StaticFiles(directory=REPORTS_DIR), name="reports_static")


# Root redirect or greeting
@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "Welcome to NWIS (Nearby Wells Intelligence System) API.",
        "documentation": "/docs",
        "health": "/api/health"
    }

