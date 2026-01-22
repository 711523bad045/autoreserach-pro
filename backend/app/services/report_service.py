from sqlalchemy.orm import Session

from app.repositories.report_repository import ReportRepository
from app.services.rag_service import RAGService


class ReportService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = ReportRepository(db)
        self.rag = RAGService()

    def generate_simple_report(self, project_id: int):
        # 1. Create report
        report = self.repo.create_report(project_id, "AI Generated Report")

        # 2. Define sections (Option 1)
        sections = [
            ("introduction", "Introduction"),
            ("overview", "Overview"),
            ("concepts", "Key Concepts"),
            ("details", "Important Details"),
            ("applications", "Applications"),
            ("conclusion", "Conclusion"),
        ]

        # 3. Generate each section
        for order, (key, title) in enumerate(sections):
            content_md = self.rag.generate_section(self.db, title)

            self.repo.add_section(
                report.id,
                key,
                title,
                order,
                content_md
            )

        return report
