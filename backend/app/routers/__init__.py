"""Routers package for NWIS."""

from app.routers.wells import router as wells_router
from app.routers.formations import router as formations_router
from app.routers.events import router as events_router
from app.routers.telemetry import router as telemetry_router
from app.routers.search import router as search_router

__all__ = [
    "wells_router",
    "formations_router",
    "events_router",
    "telemetry_router",
    "search_router",
]
