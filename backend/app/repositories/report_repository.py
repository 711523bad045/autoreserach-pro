from app.database.models.report import Report, ReportSection


class ReportRepository:
    def __init__(self, db):
        self.db = db

    def create_report(self, project_id: int, title: str):
        report = Report(
            project_id=project_id,
            title=title,
            status="generating"
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def add_section(self, report_id: int, section_key: str, title: str, order: int, content: str):
        section = ReportSection(
            report_id=report_id,
            section_key=section_key,
            title=title,
            order_index=order,
            content_markdown=content
        )
        self.db.add(section)
        self.db.commit()
        return section

    def get_report_by_project(self, project_id: int):
        return self.db.query(Report).filter(Report.project_id == project_id).first()
