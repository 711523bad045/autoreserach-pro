from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base


# Research Project
class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)


# Report (MAIN)
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"), index=True)

    title = Column(String(255))
    full_content = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # PROGRESS TRACKING (MUST BE HERE)
    progress = Column(Integer, default=0)
    status = Column(String(50), default="idle")
    current_step = Column(String(255), nullable=True)

    sections = relationship("ReportSection", back_populates="report")



# Report Sections
class ReportSection(Base):
    __tablename__ = "report_sections"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True)

    title = Column(String(255), index=True)
    content = Column(Text)
    order = Column(Integer)

    report = relationship("Report", back_populates="sections")


# IEEE Report
class IEEEReport(Base):
    __tablename__ = "ieee_reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"), index=True)

    title = Column(String(255))
    full_content = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
