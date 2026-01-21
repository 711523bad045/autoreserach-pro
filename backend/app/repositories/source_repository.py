from sqlalchemy.orm import Session
from app.database import models


class SourceRepository:

    @staticmethod
    def create(db: Session, project_id: int, domain: str):
        source = models.Source(
            project_id=project_id,
            domain=domain,
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        return source

    @staticmethod
    def list_by_project(db: Session, project_id: int):
        return db.query(models.Source).filter(models.Source.project_id == project_id).all()
