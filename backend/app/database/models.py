from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


# =====================================================
# RESEARCH PROJECT
# =====================================================

class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)


# =====================================================
# MAIN REPORT
# =====================================================

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("research_projects.id"),
        index=True
    )

    title = Column(String(255))

    full_content = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    progress = Column(Integer, default=0)

    status = Column(String(50), default="idle")

    current_step = Column(String(255), nullable=True)

    sections = relationship(
        "ReportSection",
        back_populates="report",
        cascade="all, delete-orphan"
    )


# =====================================================
# REPORT SECTIONS
# =====================================================

class ReportSection(Base):
    __tablename__ = "report_sections"

    id = Column(Integer, primary_key=True, index=True)

    report_id = Column(
        Integer,
        ForeignKey("reports.id"),
        index=True
    )

    title = Column(String(255), index=True)

    content = Column(Text)

    order = Column(Integer)

    report = relationship(
        "Report",
        back_populates="sections"
    )


# =====================================================
# IEEE REPORT
# =====================================================

class IEEEReport(Base):
    __tablename__ = "ieee_reports"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("research_projects.id"),
        index=True
    )

    title = Column(String(255))

    full_content = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# =====================================================
# SOURCES
# =====================================================

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("research_projects.id"),
        index=True
    )

    title = Column(Text)

    url = Column(Text)

    content = Column(Text)


# =====================================================
# TEXT CHUNKS
# =====================================================

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)

    source_id = Column(
        Integer,
        ForeignKey("sources.id"),
        index=True
    )

    content = Column(Text)

    embedding_id = Column(Integer, nullable=True)


# =====================================================
# RESEARCH PAPERS
# =====================================================

class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("research_projects.id"),
        index=True
    )

    paper_id = Column(String(120))

    title = Column(Text)

    authors = Column(Text)

    abstract = Column(Text)

    venue = Column(String(255))

    year = Column(Integer)

    citation_count = Column(Integer)

    doi = Column(String(255))

    url = Column(Text)

    score = Column(Float)

    used_in_report = Column(Integer, default=0)


# =====================================================
# RESEARCH GAPS
# =====================================================

class ResearchGap(Base):
    __tablename__ = "research_gaps"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("research_projects.id")
    )

    gap = Column(Text)

    confidence = Column(Float)

    supporting_papers = Column(Integer)

    future_direction = Column(Text)


# =====================================================
# CITATION EVIDENCE
# =====================================================

class CitationEvidence(Base):
    __tablename__ = "citation_evidence"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("research_projects.id")
    )

    section = Column(String(255))

    paper_title = Column(Text)

    paper_year = Column(Integer)

    citation_count = Column(Integer)

    paper_url = Column(Text)

    confidence = Column(Float)


# =====================================================
# AI REVIEW
# =====================================================

class AIReview(Base):
    __tablename__ = "ai_reviews"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("research_projects.id")
    )

    grammar_score = Column(Integer)

    evidence_score = Column(Integer)

    citation_score = Column(Integer)

    hallucination_score = Column(Integer)

    overall_score = Column(Integer)

    feedback = Column(Text)

class Diagram(Base):
    __tablename__ = "diagrams"

    id = Column(Integer, primary_key=True)

    project_id = Column(
        Integer,
        ForeignKey("research_projects.id"),
        index=True
    )

    title = Column(String(255))

    diagram_type = Column(String(100))

    json_data = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )