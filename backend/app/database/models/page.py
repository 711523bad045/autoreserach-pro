from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.base import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    url = Column(Text)
    status = Column(Text)
    raw_html = Column(Text)
    cleaned_text = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    # Relationship
    chunks = relationship("Chunk", back_populates="page")
