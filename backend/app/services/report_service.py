from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models import Report, Source, Chunk, ResearchProject, ReportSection
from app.llm.ollama_client import OllamaClient
from app.services.web_search_service import WebSearchService, WebScraper


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = OllamaClient(model="qwen2.5:1.5b")

    # =====================================================
    # FAST BRIEF REPORT (REUSE IF EXISTS)
    # =====================================================
    def generate_simple_report(self, project_id: int):
        project = self.db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            raise Exception("Project not found")

        topic = project.title

        # --------------------------------------------
        # ✅ REUSE EXISTING REPORT IF PRESENT
        # --------------------------------------------
        existing = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if existing and existing.full_content and len(existing.full_content) > 300:
            print("♻️ Reusing existing report from DB")
            return existing

        print("🧠 No existing report found. Generating new report for:", topic)

        # ----------------------------------------
        # Web search
        # ----------------------------------------
        urls = WebSearchService.search(topic, max_results=5)
        if not urls:
            raise Exception("❌ Web search returned ZERO urls.")

        all_chunks = []
        source_urls = []

        # ----------------------------------------
        # Scrape + Save Sources + Save Chunks
        # ----------------------------------------
        for url in urls:
            title, content = WebScraper.scrape(url)
            if not content:
                continue

            src = Source(
                project_id=project_id,
                url=url,
                title=title,
                content=content
            )
            self.db.add(src)
            self.db.commit()
            self.db.refresh(src)

            source_urls.append(url)

            words = content.split()
            chunk_size = 350
            chunk_index = 0

            for i in range(0, len(words), chunk_size):
                chunk_text = " ".join(words[i:i + chunk_size])
                if len(chunk_text) < 300:
                    continue

                chunk = Chunk(
                    source_id=src.id,
                    page_url=url,
                    content=chunk_text,
                    chunk_index=chunk_index
                )
                self.db.add(chunk)

                all_chunks.append(chunk_text)
                chunk_index += 1

            self.db.commit()

        if len(all_chunks) < 3:
            raise Exception("❌ Scraping failed or too little content.")

        print(f"📚 Collected {len(all_chunks)} chunks")

        # ----------------------------------------
        # Build SMALL context
        # ----------------------------------------
        context = "\n\n".join(all_chunks[:5])

        # ----------------------------------------
        # FAST SINGLE PASS PROMPT
        # ----------------------------------------
        prompt = f"""
You are a professional technical writer.

Topic: {topic}

Using the information below, write a CLEAR, WELL-STRUCTURED, MEDIUM-LENGTH report.

RULES:
- 6 to 8 sections
- Each section 2–4 paragraphs
- Use clear headings
- Factual, structured
- Not extremely long
- No academic fluff

RAW MATERIAL:
{context}

Produce the full report now.
"""

        print("✍️ Generating FAST report...")
        final_text = self.llm.generate(prompt)

        if not final_text or len(final_text.strip()) < 300:
            final_text = f"# {topic}\n\n" + "\n\n".join(all_chunks[:5])

        # ----------------------------------------
        # Append Sources
        # ----------------------------------------
        if source_urls:
            final_text += "\n\n---\n\n## Sources\n"
            for u in source_urls:
                final_text += f"- {u}\n"

        # ----------------------------------------
        # Save report
        # ----------------------------------------
        report = Report(
            project_id=project_id,
            title=f"Research: {topic}",
            full_content=final_text
        )

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        print("✅ Report saved to DB")

        return report

    # =====================================================
    # ASK FROM REPORT
    # =====================================================
    def ask_from_report(self, project_id: int, question: str):
        report = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if not report:
            return "No report found."

        prompt = f"""
Answer using ONLY the report below.

Report:
{report.full_content}

Question:
{question}
"""
        return self.llm.generate(prompt)

    # =====================================================
    # EXPAND TO IEEE (MODIFY SAME REPORT)
    # =====================================================
    def expand_to_ieee(self, project_id: int):
        report = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if not report or not report.full_content:
            raise Exception("No base report found to expand.")

        print("📄 Converting report to IEEE format...")

        prompt = f"""
You are an academic research paper formatter.

Convert the following report into a SHORT BUT PROPER IEEE STYLE research paper with:

- Title
- Abstract
- Keywords
- Introduction
- Methodology
- Results and Discussion
- Conclusion
- References

Rules:
- Formal academic tone
- Structured headings
- Do not remove information
- Keep it concise

Base Report:
{report.full_content}
"""

        ieee_text = self.llm.generate(prompt)

        if not ieee_text or len(ieee_text.strip()) < 300:
            raise Exception("IEEE conversion failed.")

        report.title = f"IEEE Paper: {report.title.replace('Research:', '').strip()}"
        report.full_content = ieee_text

        self.db.commit()
        self.db.refresh(report)

        print("✅ IEEE conversion complete")

        return report
