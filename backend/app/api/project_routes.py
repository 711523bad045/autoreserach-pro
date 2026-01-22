from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.project_schema import ProjectCreate

from app.services.project_service import ProjectService
from app.services.crawl_service import CrawlService
from app.services.rag_service import RAGService
from app.services.report_service import ReportService

from app.repositories.report_repository import ReportRepository
from app.database.models import ResearchProject


router = APIRouter(prefix="/projects", tags=["Projects"])


# -------------------------------
# Project management
# -------------------------------

@router.post("/")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return ProjectService.create_project(db, payload.title, payload.description)


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    return ProjectService.list_projects(db)


@router.post("/{project_id}/sources")
def add_source(project_id: int, domain: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectService.add_source(db, project_id, domain)


@router.post("/{project_id}/crawl")
def start_crawl(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return CrawlService.start_crawl(db, project_id)


# -------------------------------
# RAG Q&A
# -------------------------------

@router.post("/{project_id}/ask")
def ask_question(project_id: int, question: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    rag = RAGService()
    answer = rag.ask_question(db, project_id, question)
    return {
        "question": question,
        "answer": answer
    }


@router.post("/{project_id}/ask_stream")
def ask_question_stream(project_id: int, question: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    rag = RAGService()

    def token_generator():
        for token in rag.ask_question_stream(db, project_id, question):
            yield token

    return StreamingResponse(
        token_generator(),
        media_type="text/plain"
    )


# -------------------------------
# Report (TEST)
# -------------------------------

@router.post("/{project_id}/test_report")
def test_report(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    repo = ReportRepository(db)

    report = repo.create_report(project_id, "Test Report")

    repo.add_section(
        report.id,
        "intro",
        "Introduction",
        0,
        "This is a test section."
    )

    return {"report_id": report.id}


# -------------------------------
# Report (REAL - AI Generated)
# -------------------------------

@router.post("/{project_id}/generate_simple_report")
def generate_simple_report(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    service = ReportService(db)
    report = service.generate_simple_report(project_id)

    return {
        "status": "ok",
        "report_id": report.id
    }
