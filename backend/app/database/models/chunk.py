from sqlalchemy import Column, Integer, Text, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database.base import Base

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)

    source_id = Column(
        Integer,
        ForeignKey("sources.id", ondelete="CASCADE"),
        index=True
    )

    page_url = Column(String(500))
    content = Column(Text)
    chunk_index = Column(Integer)

    source = relationship("Source", back_populates="chunks")
