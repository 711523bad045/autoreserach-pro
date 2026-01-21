from sqlalchemy.orm import Session
from app.database import models


class ProjectRepository:

    @staticmethod
    def create(db: Session, title: str, description: str = None):
        project = models.ResearchProject(
            title=title,
            description=description,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get(db: Session, project_id: int):
        return db.query(models.ResearchProject).filter(models.ResearchProject.id == project_id).first()

    @staticmethod
    def list(db: Session):
        return db.query(models.ResearchProject).order_by(models.ResearchProject.created_at.desc()).all()
