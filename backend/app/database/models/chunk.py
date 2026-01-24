from sqlalchemy import Column, Integer, Text, ForeignKey, String
from app.database.base import Base

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    page_url = Column(String(500))
    content = Column(Text)
    chunk_index = Column(Integer)
