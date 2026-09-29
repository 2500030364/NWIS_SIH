"""SQLAlchemy model for historical_events table."""

from sqlalchemy import Column, Integer, Numeric, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class HistoricalEvent(Base):
    __tablename__ = "historical_events"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    depth = Column(Numeric(8, 2), nullable=False, index=True)
    formation_id = Column(Integer, ForeignKey("formations.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    description = Column(Text, nullable=False)
    cause = Column(Text, nullable=True)
    mitigation = Column(Text, nullable=True)
    event_time = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    well = relationship("Well", back_populates="historical_events")
    formation = relationship("Formation", back_populates="historical_events")
