from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.session import get_db
from app.schemas.project_schema import ProjectCreate

from app.services.project_service import ProjectService
from app.services.report_service import ReportService

from app.database.models import ResearchProject, Report
from app.database.models import ReportSection

from fastapi.responses import FileResponse
from app.services.export_service import ExportService
import os

from app.database.models import Source
from app.database.models import IEEEReport

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


@router.post("/{project_id}/split_report")
def split_report(project_id: int, db: Session = Depends(get_db)):
    service = ReportService(db)
    result = service.split_report_into_sections(project_id)

    return {
        "status": "ok",
        **result
    }


@router.get("/{project_id}/sections")
def get_sections(project_id: int, db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .filter(Report.project_id == project_id)
        .order_by(desc(Report.id))
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    sections = (
        db.query(ReportSection)
        .filter(ReportSection.report_id == report.id)
        .order_by(ReportSection.order)
        .all()
    )

    return [
        {
            "id": s.id,
            "title": s.title,
            "content": s.content,
            "order": s.order,
        }
        for s in sections
    ]



@router.get("/{project_id}/download/word")
def download_report_word(project_id: int, db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .filter(Report.project_id == project_id)
        .order_by(desc(Report.id))
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    path = ExportService.export_to_word(report)
    return FileResponse(path, filename="report.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@router.get("/{project_id}/download/pdf")
def download_report_pdf(project_id: int, db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .filter(Report.project_id == project_id)
        .order_by(desc(Report.id))
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    path = ExportService.export_to_pdf(report)
    return FileResponse(path, filename="report.pdf", media_type="application/pdf")


@router.get("/{project_id}/sources")
def get_sources(project_id: int, db: Session = Depends(get_db)):
    sources = (
        db.query(Source)
        .filter(Source.project_id == project_id)
        .all()
    )

    return [
        {
            "id": s.id,
            "url": s.url,
            "title": s.title,
        }
        for s in sources
    ]



@router.get("/{project_id}/ieee")
def get_ieee_report(project_id: int, db: Session = Depends(get_db)):
    ieee = (
        db.query(IEEEReport)
        .filter(IEEEReport.project_id == project_id)
        .order_by(desc(IEEEReport.id))
        .first()
    )

    if not ieee:
        raise HTTPException(status_code=404, detail="IEEE report not found")

    return {
        "id": ieee.id,
        "title": ieee.title,
        "full_content": ieee.full_content,
        "project_id": ieee.project_id
    }


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # ---------------------------
    # Delete child tables first
    # ---------------------------

    # Delete Reports
    reports = db.query(Report).filter(Report.project_id == project_id).all()
    for r in reports:
        db.query(ReportSection).filter(ReportSection.report_id == r.id).delete()

    db.query(Report).filter(Report.project_id == project_id).delete()

    # Delete Sources
    db.query(Source).filter(Source.project_id == project_id).delete()

    # Delete IEEE
    db.query(IEEEReport).filter(IEEEReport.project_id == project_id).delete()

    # Delete Project
    db.delete(project)
    db.commit()

    return {"status": "deleted", "project_id": project_id}
