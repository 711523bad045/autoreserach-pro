from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False)

    project_id = Column(Integer, ForeignKey("research_projects.id"))
    project = relationship("ResearchProject", backref="sources")
