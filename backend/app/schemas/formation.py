"""Pydantic schemas for Formation responses."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FormationResponse(BaseModel):
    id: int = Field(..., description="Unique formation interval ID", example=1)
    well_id: int = Field(..., description="Parent well ID", example=1)
    formation_name: str = Field(..., description="Geological formation name", example="Demo-Barail")
    top_depth: float = Field(..., description="Top depth in meters", example=2884.79)
    bottom_depth: float = Field(..., description="Bottom depth in meters", example=3404.79)

    model_config = ConfigDict(from_attributes=True)


class WellFormationInterval(BaseModel):
    formation_name: str = Field(..., description="Geological formation name", example="Demo-Barail")
    top_depth: float = Field(..., description="Top depth in meters", example=2884.79)
    bottom_depth: float = Field(..., description="Bottom depth in meters", example=3404.79)

    model_config = ConfigDict(from_attributes=True)


class FormationSummary(BaseModel):
    formation_name: str = Field(..., description="Geological formation name", example="Demo-Barail")
    well_count: int = Field(..., description="Number of wells penetrating this formation", example=25)
    typical_top_depth: Optional[float] = Field(None, description="Average top depth in meters", example=2870.0)
    typical_bottom_depth: Optional[float] = Field(None, description="Average bottom depth in meters", example=3390.0)

    model_config = ConfigDict(from_attributes=True)
