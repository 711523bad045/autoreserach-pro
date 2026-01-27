from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class ReportSection(Base):
    __tablename__ = "report_sections"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True)

    title = Column(String(255), index=True)
    content = Column(Text)
    order = Column(Integer)

    # Relationship
    report = relationship("Report", back_populates="sections")
