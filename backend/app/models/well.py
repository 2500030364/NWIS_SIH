"""SQLAlchemy model for wells table."""

from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Well(Base):
    __tablename__ = "wells"

    id = Column(Integer, primary_key=True, index=True)
    well_name = Column(String(50), unique=True, nullable=False, index=True)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    total_depth = Column(Numeric(8, 2), nullable=False)
    status = Column(String(20), nullable=False, index=True)
    spud_date = Column(Date, nullable=False)
    field_name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    formations = relationship(
        "Formation",
        back_populates="well",
        cascade="all, delete-orphan",
        order_by="Formation.top_depth"
    )
    drilling_parameters = relationship(
        "DrillingParameter",
        back_populates="well",
        cascade="all, delete-orphan"
    )
    historical_events = relationship(
        "HistoricalEvent",
        back_populates="well",
        cascade="all, delete-orphan",
        order_by="HistoricalEvent.depth"
    )
