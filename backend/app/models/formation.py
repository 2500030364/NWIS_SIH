"""SQLAlchemy model for formations table."""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Formation(Base):
    __tablename__ = "formations"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    formation_name = Column(String(100), nullable=False, index=True)
    top_depth = Column(Numeric(8, 2), nullable=False)
    bottom_depth = Column(Numeric(8, 2), nullable=False)

    # Relationships
    well = relationship("Well", back_populates="formations")
    historical_events = relationship("HistoricalEvent", back_populates="formation")
