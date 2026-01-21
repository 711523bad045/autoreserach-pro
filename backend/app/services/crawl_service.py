from sqlalchemy.orm import Session
from app.repositories.crawl_repository import CrawlRepository
from app.crawler.engine import CrawlerEngine
from app.database import models


class CrawlService:

    @staticmethod
    def start_crawl(db: Session, project_id: int):
        print("START CRAWL FOR PROJECT:", project_id)

        job = CrawlRepository.create_job(db, project_id)

        try:
            CrawlerEngine.crawl_project(db, project_id)

            CrawlRepository.update_status(db, job.id, models.CrawlStatus.success)

        except Exception as e:
            CrawlRepository.update_status(db, job.id, models.CrawlStatus.failed, str(e))

        return job
