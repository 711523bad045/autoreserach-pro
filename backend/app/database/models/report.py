from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    full_content = Column(Text)

    project_id = Column(Integer, ForeignKey("research_projects.id"))

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    project = relationship("ResearchProject", back_populates="reports")
    sections = relationship("ReportSection", back_populates="report", cascade="all, delete-orphan")
