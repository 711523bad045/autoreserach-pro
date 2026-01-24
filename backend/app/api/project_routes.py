from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

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
# REPORT
# -------------------------------

@router.post("/{project_id}/generate_simple_report")
def generate_simple_report(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # ✅ REUSE EXISTING REPORT IF EXISTS
    existing = (
        db.query(Report)
        .filter(Report.project_id == project_id)
        .order_by(desc(Report.id))
        .first()
    )

    if existing and existing.full_content and len(existing.full_content) > 300:
        print("♻️ Reusing existing report")
        return {
            "status": "ok",
            "report_id": existing.id,
            "reused": True
        }

    # Otherwise generate new
    service = ReportService(db)
    report = service.generate_simple_report(project_id)

    return {
        "status": "ok",
        "report_id": report.id,
        "reused": False
    }


@router.post("/{project_id}/expand_to_ieee")
def expand_to_ieee(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    service = ReportService(db)
    report = service.expand_to_ieee(project_id)

    return {
        "status": "ok",
        "report_id": report.id
    }


@router.get("/{project_id}/report")
def get_report(project_id: int, db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .filter(Report.project_id == project_id)
        .order_by(desc(Report.id))  # ✅ Always get latest
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "title": report.title,
        "full_content": report.full_content or "",
        "project_id": report.project_id
    }


@router.post("/{project_id}/ask_from_report")
def ask_from_report(project_id: int, question: str, db: Session = Depends(get_db)):
    service = ReportService(db)
    answer = service.ask_from_report(project_id, question)

    return {
        "question": question,
        "answer": answer
    }
