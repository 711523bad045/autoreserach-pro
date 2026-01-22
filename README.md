AutoResearch Pro
Enterprise-Grade Autonomous Research Assistant (Offline RAG System)

AutoResearch Pro is a production-grade, fully offline, autonomous research system that automatically collects information from the web, processes and stores it in a structured knowledge base, builds a semantic vector index, and enables intelligent retrieval using a Retrieval-Augmented Generation (RAG) architecture.

This repository currently contains the complete data ingestion, knowledge base, and vector retrieval engine. The reasoning and report generation layers will be added in the next phase.

Project Vision

The final system will:

Take a research topic or project

Automatically crawl relevant websites

Extract, clean, and chunk content

Generate embeddings and store them in FAISS

Store all metadata in MySQL

Use an offline LLM (Phi-3 Mini via Ollama) with RAG to:

Answer questions

Summarize content

Generate structured research reports

Export professional PDF reports

Maintain full research history

Current Status (End of Day 1)
Implemented and Working

Production-grade FastAPI backend

Clean layered architecture (API → Service → Repository → DB)

MySQL database with fully designed enterprise schema

Autonomous multi-page web crawler

HTML cleaning and text extraction pipeline

Text chunking pipeline (~1000 characters per chunk)

Persistent storage of:

Pages

Cleaned text

Chunks

Embedding generation using SentenceTransformers

FAISS vector index

Semantic search over crawled knowledge base

Verified end-to-end ingestion and retrieval pipeline

Not Yet Implemented

LLM integration (Phi-3 Mini via Ollama)

Question answering API

Summarization engine

Report generation

PDF export

Background job queue

Frontend UI

Architecture
Backend Structure
backend/app/
  api/            # FastAPI routes (thin controllers)
  core/           # Configuration
  crawler/        # Web crawling engine
  database/       # SQLAlchemy base, session, models
  repositories/   # Data access layer
  services/       # Business logic
  schemas/        # Pydantic schemas
  nlp/            # Text cleaning and chunking
  vectorstore/    # FAISS integration
  main.py         # Application entry point

Architecture Pattern
API Layer
   ↓
Service Layer
   ↓
Repository Layer
   ↓
Database


All business logic is kept out of the API layer. The system is designed for scalability and long-term maintainability.

Database Schema
Core Tables

companies

research_projects

topics

sources

pages

chunks

embeddings (metadata ready)

crawl_jobs

reports

Logical Relationships
ResearchProject
 ├── Sources
 │    └── Pages
 │         └── Chunks
 ├── CrawlJobs
 └── Reports


The schema is normalized and designed for multi-project, multi-source, and large-scale knowledge bases.

Web Crawler
Features

Breadth-first crawling

Domain restriction

Link discovery

URL deduplication

Crawl limits per source

Error handling and status tracking

Data Stored

URL

Raw HTML

Cleaned text

Crawl status

Metadata

Implementation:

app/crawler/engine.py

NLP Processing Pipeline
Pipeline
HTML
 → Remove scripts and styles
 → Extract clean text
 → Normalize whitespace
 → Chunk into ~1000 character segments
 → Store in database


Implementation:

app/nlp/chunker.py


Each crawled page is automatically processed and split into multiple chunks.

Vector Store and Semantic Search
Libraries

sentence-transformers

faiss-cpu

Current Embedding Model
all-MiniLM-L6-v2


(This will later be replaced or complemented by Phi-3 for generation.)

Components
app/vectorstore/faiss_store.py
app/services/vector_service.py

Functionality

Reads all chunks from database

Generates embeddings

Builds FAISS index

Performs semantic similarity search

Verification

In Python shell:

from app.database.session import SessionLocal
from app.services.vector_service import VectorService

db = SessionLocal()
VectorService.build_index(db)
VectorService.search("python tutorial")


If results are returned, the system is functioning correctly.

What the System Can Do Right Now

Create projects

Add sources

Crawl websites automatically

Extract and clean text

Chunk content

Store all data in MySQL

Generate embeddings

Build FAISS index

Perform semantic search over the knowledge base

This already represents the core of a production-grade RAG ingestion and retrieval system.

Next Phase (Day 2 Plan)

Integrate Ollama

Run Phi-3 Mini locally

Create LLM client module

Build RAG answer pipeline:

User Question
 → FAISS Search
 → Top-K Chunks
 → Prompt Construction
 → Phi-3 Mini
 → Answer


Add API endpoint:

POST /projects/{id}/ask

Technology Stack
Backend

FastAPI

SQLAlchemy

MySQL (MariaDB)

NLP and AI

SentenceTransformers

FAISS

(Next phase: Ollama + Phi-3 Mini)

Crawling

requests

BeautifulSoup

Summary

At the end of Day 1, AutoResearch Pro has a complete, production-grade:

Data ingestion pipeline

Knowledge base

Vector indexing system

Semantic retrieval engine

This is the most complex and critical part of any RAG system and is now fully operational.

The next phase will add the reasoning and generation layer.