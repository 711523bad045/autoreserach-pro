from sqlalchemy.orm import Session
from app.database.models import Report, Source, Chunk, ResearchProject
from app.llm.ollama_client import OllamaClient
from app.services.web_search_service import WebSearchService, WebScraper


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = OllamaClient(model="qwen2.5:1.5b")

    # =====================================================
    # STAGE 1 — FAST BRIEF REPORT (DEFAULT)
    # =====================================================
    def generate_simple_report(self, project_id: int):
        project = self.db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            raise Exception("Project not found")

        topic = project.title

        # ♻️ Reuse if already exists
        existing = self.db.query(Report).filter(Report.project_id == project_id).first()
        if existing and existing.full_content and len(existing.full_content) > 500:
            print("♻️ Reusing existing report")
            return existing

        print("🧠 Generating FAST brief report for:", topic)

        # -------------------------------------------------
        # 1. Search
        # -------------------------------------------------
        urls = WebSearchService.search(topic, max_results=5)

        # If nothing found → still continue using topic only
        if not urls:
            print("⚠️ No web sources found, generating general report")

        # -------------------------------------------------
        # 2. Scrape (limit!)
        # -------------------------------------------------
        all_text = []
        source_urls = []

        for url in urls[:3]:  # only 3 pages for speed
            title, content = WebScraper.scrape(url)
            if not content:
                continue

            source_urls.append(url)
            all_text.append(content[:4000])  # limit size

        raw_material = "\n\n".join(all_text[:3])

        # -------------------------------------------------
        # 3. FAST PROMPT (ONE CALL ONLY)
        # -------------------------------------------------
        prompt = f"""
You are a professional technical writer.

Write a CLEAR, WELL-STRUCTURED, INFORMATIVE overview report about:

TOPIC: {topic}

Requirements:
- 800 to 1200 words
- Simple professional language
- Structured with headings:
  Introduction
  Background
  Key Concepts
  Applications
  Challenges
  Future Scope
  Conclusion
- Do NOT mention Wikipedia or sources inside text

Use the following material ONLY as background reference (you may paraphrase and summarize):

{raw_material}

Now write the full report.
"""

        print("✍️ Generating brief report...")
        text = self.llm.generate(prompt)

        if not text or len(text.strip()) < 300:
            text = f"# {topic}\n\nThis topic does not have enough available information online. Please try a different topic."

        # -------------------------------------------------
        # 4. Append Sources Section
        # -------------------------------------------------
        if source_urls:
            text += "\n\n---\n\n## Sources\n"
            text += "This report was prepared using information summarized from the following sources:\n\n"
            for u in source_urls:
                text += f"- {u}\n"

        # -------------------------------------------------
        # 5. Save
        # -------------------------------------------------
        report = Report(
            project_id=project_id,
            title=f"Report: {topic}",
            full_content=text
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    # =====================================================
    # STAGE 2 — EXPAND TO IEEE PAPER
    # =====================================================
    def expand_to_ieee(self, project_id: int):
        report = self.db.query(Report).filter(Report.project_id == project_id).first()
        if not report:
            raise Exception("No base report found")

        print("📄 Expanding to IEEE research paper...")

        prompt = f"""
You are a professional academic research writer.

Convert the following technical report into a FULL IEEE STYLE research paper.

Requirements:
- 3000 to 4000 words
- Formal academic tone
- Add:
  Abstract
  Keywords
  Introduction
  Literature Review
  Methodology
  Discussion
  Applications
  Challenges
  Future Work
  Conclusion
- Add in-text citation style like: [1], [2], [3]
- Add References section at the end
- Do NOT invent sources
- Use the report content as the main material

REPORT:
{report.full_content}

Now generate the full IEEE formatted paper.
"""

        long_text = self.llm.generate(prompt)

        if long_text and len(long_text) > len(report.full_content):
            report.full_content = long_text
            report.title = report.title.replace("Report:", "IEEE Paper:")
            self.db.commit()
            self.db.refresh(report)

        return report

    # =====================================================
    # Q&A
    # =====================================================
    def ask_from_report(self, project_id: int, question: str):
        report = self.db.query(Report).filter(Report.project_id == project_id).first()
        if not report:
            return "No report found."

        prompt = f"""
Answer using ONLY this document:

{report.full_content}

Question: {question}
"""

        return self.llm.generate(prompt)
