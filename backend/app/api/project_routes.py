from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.session import get_db
from app.schemas.project_schema import ProjectCreate

from app.services.project_service import ProjectService
from app.services.report_service import ReportService

from app.database.models import ResearchProject, Report

router = APIRouter(prefix="/projects", tags=["Projects"])


# -------------------------------
# PROJECTS
# -------------------------------

@router.post("/")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return ProjectService.create_project(db, payload.title, payload.description)


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    return ProjectService.list_projects(db)


# -------------------------------
# SOURCES
# -------------------------------

@router.post("/{project_id}/sources")
def add_source(project_id: int, url: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        return ProjectService.add_source(db, project_id, url)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Source already exists in this project")


# -------------------------------
# REPORT
# -------------------------------

@router.post("/{project_id}/generate_simple_report")
def generate_simple_report(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    service = ReportService(db)

    # Use project title as topic
    report = service.generate_simple_report(project_id)

    return {
        "status": "ok",
        "report_id": report.id
    }


@router.get("/{project_id}/report")
def get_report(project_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.project_id == project_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "title": report.title,
        "content": report.full_content
    }


@router.post("/{project_id}/ask_from_report")
def ask_from_report(project_id: int, question: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    service = ReportService(db)
    answer = service.ask_from_report(project_id, question)

    return {
        "question": question,
        "answer": answer
    }
