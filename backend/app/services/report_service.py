from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models import Report, Source, Chunk, ResearchProject, ReportSection
from app.database.models import IEEEReport
from app.llm.ollama_client import OllamaClient
from app.services.web_search_service import WebSearchService, WebScraper


class ReportService:
    def __init__(self, db: Session):
        self.db = db

        # ⚡ FAST model for normal report
        self.llm = OllamaClient(model="qwen2.5:0.5b")

        # 🧠 Better model ONLY for IEEE
        self.ieee_llm = OllamaClient(model="qwen2.5:1.5b")

        # ⚡ FAST model for Q&A
        self.qa_llm = OllamaClient(model="qwen2.5:0.5b")

    # =====================================================
    # LONG NORMAL REPORT (10k–15k words)
    # =====================================================
    def generate_simple_report(self, project_id: int):
        project = self.db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            raise Exception("Project not found")

        topic = project.title

        # --------------------------------------------
        # ✅ REUSE EXISTING NORMAL REPORT
        # --------------------------------------------
        existing = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if existing and existing.full_content and len(existing.full_content) > 8000:
            print("♻️ Reusing existing NORMAL long report from DB")
            return existing

        print("🧠 Generating NEW LONG report for:", topic)

        if existing:
            report = existing
            report.full_content = "⏳ Preparing sources...\n"
            self.db.commit()
        else:
            report = Report(
                project_id=project_id,
                title=f"Research: {topic}",
                full_content="⏳ Preparing sources...\n"
            )
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)



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

        context = "\n\n".join(all_chunks[:4])

        # ----------------------------------------
        # Section plan (≈ 11k–13k words total)
        # ----------------------------------------
        sections_plan = [
            ("Introduction", 2000),
            ("Background", 2000),
            ("Core Concepts", 2000),
            ("Architecture / Working", 2000),
            ("Applications", 1500),
            ("Advantages and Limitations", 1500),
            ("Conclusion", 1000),
        ]

        # ----------------------------------------
        # Create EMPTY report first (for live UI)
        # ----------------------------------------
        # reuse existing report object
        full_text = f"# {topic}\n\n"
        report.full_content = full_text
        self.db.commit()


        # ----------------------------------------
        # Generate section by section
        # ----------------------------------------
        for section_title, target_words in sections_plan:
            print(f"🧠 Generating section: {section_title}")

            section_prompt = f"""
You are writing a VERY DETAILED research paper.

Topic: {topic}

Now write ONLY this section:

{section_title}

Rules:
- Write around {target_words} words
- Very detailed explanation
- Use paragraphs and subheadings
- Formal but simple English
- Do not summarize
- Do not write other sections
- Only write this section

Use this reference information:
{context}
"""

            section_text = self.llm.generate(section_prompt)

            if not section_text or len(section_text.strip()) < 500:
                section_text = f"(Fallback content)\n\n{context}"

            full_text += f"\n\n## {section_title}\n\n{section_text}\n"

            # ✅ SAVE PROGRESS FOR UI
            report.full_content = full_text
            self.db.commit()

            print(f"✅ Finished: {section_title} | Total chars: {len(full_text)}")

        # ----------------------------------------
        # Append references
        # ----------------------------------------
        if source_urls:
            full_text += "\n\n---\n\n## References\n"
            for u in source_urls:
                full_text += f"- {u}\n"

        # ----------------------------------------
        # Final save
        # ----------------------------------------
        report.full_content = full_text
        self.db.commit()
        self.db.refresh(report)

        print("✅ LONG Normal report fully saved to DB")

        # ----------------------------------------
        # 🔁 AUTO GENERATE IEEE
        # ----------------------------------------
        print("🔁 Auto generating IEEE version...")
        try:
            print("🔁 Auto generating IEEE version...")
            self.expand_to_ieee(project_id)
        except Exception as e:
            print("⚠️ IEEE generation failed, skipping:", e)


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

        context = report.full_content[:4000]

        prompt = f"""
Answer the question using ONLY the content below.

Rules:
- Answer in 5 to 6 lines only
- Be direct
- No extra explanation
- No markdown

Content:
{context}

Question:
{question}
"""

        return self.qa_llm.generate(prompt)

    # =====================================================
    # GENERATE / LOAD IEEE REPORT
    # =====================================================
    def expand_to_ieee(self, project_id: int):

        existing = (
            self.db.query(IEEEReport)
            .filter(IEEEReport.project_id == project_id)
            .order_by(desc(IEEEReport.id))
            .first()
        )

        if existing and existing.full_content and len(existing.full_content) > 1000:
            print("♻️ Reusing existing IEEE report from DB")
            return existing

        report = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if not report or not report.full_content:
            raise Exception("No normal report found to convert.")

        print("📄 Generating IEEE report using 1.5B model...")

        prompt = f"""
You are an academic paper writer.

Convert the following report into a PROPER IEEE STYLE paper with:

- Title
- Abstract
- Keywords
- Introduction
- Background
- Core Concepts
- Architecture / Working
- Applications
- Advantages and Limitations
- Conclusion
- References

Rules:
- Formal academic tone
- Expand explanations
- Do not remove information
- Do not hallucinate
- Proper section headings

Base Report:
{report.full_content[:12000]}
"""

        ieee_text = self.ieee_llm.generate(prompt)

        if not ieee_text or len(ieee_text.strip()) < 1000:
            raise Exception("IEEE generation failed.")

        ieee = IEEEReport(
            project_id=project_id,
            title=f"IEEE Paper: {report.title.replace('Research:', '').strip()}",
            full_content=ieee_text
        )

        self.db.add(ieee)
        self.db.commit()
        self.db.refresh(ieee)

        print("✅ IEEE report saved to DB")

        return ieee

        # =====================================================
    # SPLIT NORMAL REPORT INTO SECTIONS (ROBUST)
    # =====================================================
    def split_report_into_sections(self, project_id: int):

        print("✂️ Splitting report into sections...")

        # Load latest report
        report = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if not report or not report.full_content:
            raise Exception("No report found to split.")

        # Delete old sections for this report
        self.db.query(ReportSection).filter(
            ReportSection.report_id == report.id
        ).delete()
        self.db.commit()

        text = report.full_content
        lines = text.split("\n")

        sections = []
        current_title = None
        current_content = []
        order = 1

        def is_heading(line: str):
            line = line.strip()
            return (
                line.startswith("# ")
                or line.startswith("## ")
                or line.startswith("### ")
                or line.startswith("#### ")
            )

        def clean_heading(line: str):
            return line.lstrip("#").strip()

        for line in lines:
            line = line.rstrip()

            if is_heading(line):
                # Save previous section
                if current_title and current_content:
                    sections.append(
                        (current_title, "\n".join(current_content).strip())
                    )

                current_title = clean_heading(line)
                current_content = []
            else:
                if current_title:
                    current_content.append(line)

        # Save last section
        if current_title and current_content:
            sections.append(
                (current_title, "\n".join(current_content).strip())
            )

        # Insert into DB
        objects = []
        for title, content in sections:
            if len(content.strip()) < 200:
                continue

            obj = ReportSection(
                report_id=report.id,
                title=title,
                content=content,
                order=order
            )
            objects.append(obj)
            order += 1

        if objects:
            self.db.bulk_save_objects(objects)
            self.db.commit()

        print(f"✅ Split into {len(objects)} sections")

        return {"sections_created": len(objects)}


