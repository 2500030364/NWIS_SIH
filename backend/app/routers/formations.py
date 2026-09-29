"""
===============================================================================
NWIS Backend - Formations Router
===============================================================================
Exposes endpoints for listing available geological formations and their
stratigraphic depth distributions across the demo field.
===============================================================================
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.formation import Formation
from app.schemas.formation import FormationSummary

router = APIRouter(prefix="/api/formations", tags=["Formations"])


@router.get(
    "",
    response_model=List[FormationSummary],
    summary="List available stratigraphic formations",
    description="Retrieve a distinct summary of all geological formations encountered across offset wells, with average depth boundaries."
)
def get_formations(db: Session = Depends(get_db)):
    results = (
        db.query(
            Formation.formation_name,
            func.count(Formation.well_id).label("well_count"),
            func.avg(Formation.top_depth).label("avg_top"),
            func.avg(Formation.bottom_depth).label("avg_bottom"),
            func.min(Formation.top_depth).label("min_top")
        )
        .group_by(Formation.formation_name)
        .order_by(func.min(Formation.top_depth).asc())
        .all()
    )

    summaries = []
    for r in results:
        summaries.append(
            FormationSummary(
                formation_name=r.formation_name,
                well_count=r.well_count,
                typical_top_depth=round(float(r.avg_top), 2) if r.avg_top else None,
                typical_bottom_depth=round(float(r.avg_bottom), 2) if r.avg_bottom else None
            )
        )
    return summaries
