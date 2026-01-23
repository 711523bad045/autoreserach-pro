from sqlalchemy.orm import Session
from app.database import models

class SourceRepository:
    @staticmethod
    def create(db: Session, project_id: int, url: str):
        source = models.Source(
            project_id=project_id,
            url=url,
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        return source
