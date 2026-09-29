"""SQLAlchemy model for reports table."""

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    report_name = Column(String(150), nullable=False)
    report_type = Column(String(50), nullable=False, index=True)
    file_path = Column(String(255), nullable=False)
    report_date = Column(Date, nullable=False, index=True)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    well = relationship("Well", backref="reports")
