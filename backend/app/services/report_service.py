from sqlalchemy.orm import Session
from app.database.models import Report
from app.llm.ollama_client import OllamaClient


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = OllamaClient()

    def generate_simple_report(self, project_id: int, topic: str = None):
        # If topic not provided, load from project
        from app.database.models import ResearchProject

        project = self.db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            raise Exception("Project not found")

        topic = topic or project.title

        print("🧠 Generating research using Ollama for topic:", topic)

        prompt = f"""
You are a professional research assistant.

Write a detailed, well-structured research brief on the following topic:

Topic:
{topic}

The report MUST include:

1. Introduction
2. Background / Overview
3. Key Concepts
4. Key Findings
5. Applications / Use Cases
6. Challenges / Limitations
7. Conclusion

Write in a professional, clear, structured manner.
"""

        result = self.llm.generate(prompt)

        if not result or not result.strip():
            result = "Failed to generate content."

        # Check if report already exists → overwrite
        existing = self.db.query(Report).filter(Report.project_id == project_id).first()

        if existing:
            existing.full_content = result
            existing.title = f"Research Report: {topic}"
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # Create new report
        report = Report(
            project_id=project_id,
            title=f"Research Report: {topic}",
            full_content=result
        )

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def ask_from_report(self, project_id: int, question: str) -> str:
        report = self.db.query(Report).filter(Report.project_id == project_id).first()

        if not report or not report.full_content:
            return "No report found."

        prompt = f"""
You are answering using ONLY the report below.

If the answer is not present in the report, say:
"Not found in the report."

Report:
{report.full_content}

Question:
{question}

Give a short, clear answer.
"""

        answer = self.llm.generate(prompt)

        if not answer:
            return "No answer generated."

        return answer.strip()
