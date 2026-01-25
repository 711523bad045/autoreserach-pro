from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.base import Base

class IEEEReport(Base):
    __tablename__ = "ieee_reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"), index=True)

    title = Column(String(255))
    full_content = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
