from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base
from sqlalchemy import ForeignKey


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"), index=True)
    title = Column(String(512))
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    sections = relationship("ReportSection", back_populates="report")


class ReportSection(Base):
    __tablename__ = "report_sections"

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    section_key = Column(String(100))
    title = Column(String(255))
    order_index = Column(Integer)
    content_markdown = Column(Text)

    report = relationship("Report", back_populates="sections")
