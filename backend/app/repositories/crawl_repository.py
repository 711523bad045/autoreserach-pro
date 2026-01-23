from sqlalchemy.orm import Session
from datetime import datetime
from app.database import models


class CrawlRepository:

    @staticmethod
    def create_job(db: Session, project_id: int):
        job = models.CrawlJob(
            project_id=project_id,
            status=models.CrawlStatus.pending.value,
            started_at=datetime.utcnow(),
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def update_status(db: Session, job_id: int, status: models.CrawlStatus, error_message=None):
        job = db.query(models.CrawlJob).filter(models.CrawlJob.id == job_id).first()
        if not job:
            return None

        job.status = status.value

        if status in [models.CrawlStatus.success, models.CrawlStatus.failed]:
            job.finished_at = datetime.utcnow()

        if error_message:
            job.error_message = error_message

        db.commit()
        return job
