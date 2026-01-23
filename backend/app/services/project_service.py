from sqlalchemy.orm import Session
from app.repositories.project_repository import ProjectRepository
from app.repositories.source_repository import SourceRepository

class ProjectService:

    @staticmethod
    def create_project(db: Session, title: str, description: str):
        return ProjectRepository.create(db, title, description)

    @staticmethod
    def list_projects(db: Session):
        return ProjectRepository.list(db)

    @staticmethod
    def add_source(db: Session, project_id: int, url: str):
        return SourceRepository.create(db, project_id, url)
