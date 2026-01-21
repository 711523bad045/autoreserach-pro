from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Float,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.base import Base


# =========================
# ENUMS
# =========================

class CrawlStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class PageStatus(str, enum.Enum):
    pending = "pending"
    crawled = "crawled"
    failed = "failed"


class ReportStatus(str, enum.Enum):
    draft = "draft"
    final = "final"


# =========================
# MIXINS
# =========================

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# =========================
# CORE TABLES
# =========================

class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    website = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    projects = relationship("ResearchProject", back_populates="company")


class ResearchProject(Base, TimestampMixin):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)

    company = relationship("Company", back_populates="projects")
    topics = relationship("Topic", back_populates="project", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="project", cascade="all, delete-orphan")
    crawl_jobs = relationship("CrawlJob", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")


class Topic(Base, TimestampMixin):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=False)

    project = relationship("ResearchProject", back_populates="topics")


# =========================
# CRAWLING
# =========================

class CrawlJob(Base, TimestampMixin):
    __tablename__ = "crawl_jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(CrawlStatus), default=CrawlStatus.pending)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=False)

    project = relationship("ResearchProject", back_populates="crawl_jobs")


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(500), nullable=False)

    project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=False)

    project = relationship("ResearchProject", back_populates="sources")
    pages = relationship("Page", back_populates="source", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("domain", "project_id", name="uq_source_domain_project"),
    )


class Page(Base, TimestampMixin):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1000), nullable=False)
    status = Column(Enum(PageStatus), default=PageStatus.pending)

    raw_html = Column(Text, nullable=True)
    cleaned_text = Column(Text, nullable=True)

    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)

    source = relationship("Source", back_populates="pages")
    chunks = relationship("Chunk", back_populates="page", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("url", "source_id", name="uq_page_url_source"),
    )


# =========================
# NLP PIPELINE
# =========================

class Chunk(Base, TimestampMixin):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)

    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)

    page = relationship("Page", back_populates="chunks")
    embedding = relationship("Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("page_id", "chunk_index", name="uq_chunk_page_index"),
    )


class Embedding(Base, TimestampMixin):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)

    vector_id = Column(Integer, nullable=False, index=True)  # FAISS index id
    model_name = Column(String(255), nullable=False)
    dimension = Column(Integer, nullable=False)

    chunk_id = Column(Integer, ForeignKey("chunks.id"), nullable=False, unique=True)

    chunk = relationship("Chunk", back_populates="embedding")


# =========================
# REPORTING
# =========================

class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)

    status = Column(Enum(ReportStatus), default=ReportStatus.draft)

    summary = Column(Text, nullable=True)
    full_content = Column(Text, nullable=True)

    pdf_path = Column(String(1000), nullable=True)

    project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=False)

    project = relationship("ResearchProject", back_populates="reports")
