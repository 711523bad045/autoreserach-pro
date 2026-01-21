from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.project_service import ProjectService
from app.services.crawl_service import CrawlService
from app.schemas.project_schema import ProjectCreate

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return ProjectService.create_project(db, payload.title, payload.description)


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    return ProjectService.list_projects(db)


@router.post("/{project_id}/sources")
def add_source(project_id: int, domain: str, db: Session = Depends(get_db)):
    return ProjectService.add_source(db, project_id, domain)


@router.post("/{project_id}/crawl")
def start_crawl(project_id: int, db: Session = Depends(get_db)):
    return CrawlService.start_crawl(db, project_id)
