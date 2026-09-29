"""SQLAlchemy model for drilling_parameters table."""

from sqlalchemy import Column, Integer, BigInteger, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class DrillingParameter(Base):
    __tablename__ = "drilling_parameters"

    id = Column(BigInteger, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)
    measured_depth = Column(Numeric(8, 2), nullable=False, index=True)
    torque = Column(Numeric(8, 2), nullable=False)
    wob = Column(Numeric(8, 2), nullable=False)
    rop = Column(Numeric(8, 2), nullable=False)
    rpm = Column(Numeric(8, 2), nullable=False)
    mud_flow = Column(Numeric(8, 2), nullable=False)
    mud_weight = Column(Numeric(6, 2), nullable=False)
    standpipe_pressure = Column(Numeric(8, 2), nullable=False)

    # Relationships
    well = relationship("Well", back_populates="drilling_parameters")
