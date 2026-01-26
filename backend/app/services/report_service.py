from sqlalchemy.orm import Session
from sqlalchemy import desc
import traceback
import time

from app.database.models import Report, Source, Chunk, ResearchProject, ReportSection
from app.database.models import IEEEReport
from app.llm.ollama_client import OllamaClient
from app.services.web_search_service import WebSearchService, WebScraper


class ReportService:
    def __init__(self, db: Session):
        self.db = db

        # ⚡ FAST model for everything
        self.llm = OllamaClient(model="qwen2.5:0.5b")

        # ⚡ FAST model for IEEE (changed from 1.5b to 0.5b for speed)
        self.ieee_llm = OllamaClient(model="qwen2.5:0.5b")

        # ⚡ FAST model for Q&A
        self.qa_llm = OllamaClient(model="qwen2.5:0.5b")

    def generate_simple_report(self, project_id: int):
        project = self.db.query(ResearchProject).filter(
            ResearchProject.id == project_id
        ).first()
        
        if not project:
            raise Exception("Project not found")

        topic = project.title

        # Check for existing report
        existing = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if existing and existing.full_content and len(existing.full_content) > 5000:
            print("♻️ Reusing existing report")
            return existing

        print("🧠 Generating NEW report for:", topic)

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

        # Web search
        try:
            urls = WebSearchService.search(topic, max_results=5)
        except Exception as e:
            print(f"❌ Web search error: {e}")
            urls = []
            
        if not urls:
            report.full_content = "❌ No sources found"
            self.db.commit()
            raise Exception("❌ No sources found")

        all_chunks = []
        source_urls = []

        # Scrape sources
        for url in urls:
            try:
                title, content = WebScraper.scrape(url)
                if not content or len(content) < 1000:
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
                
            except Exception as e:
                print(f"⚠️ Error scraping {url}: {e}")
                continue

        if len(all_chunks) < 3:
            raise Exception("❌ Too little content")

        print(f"📚 Collected {len(all_chunks)} chunks")

        # ✅ REDUCED SECTION SIZES FOR SPEED
        sections_plan = [
            ("Introduction", 300),
            ("Background", 400),
            ("Core Concepts", 500),
            ("Architecture and Working", 500),
            ("Applications", 400),
            ("Advantages and Limitations", 400),
            ("Conclusion", 300),
        ]

        full_text = f"# {topic}\n\n"
        report.full_content = full_text
        self.db.commit()

        # Generate sections
        for idx, (section_title, target_words) in enumerate(sections_plan):
            print(f"\n🧠 [{idx+1}/{len(sections_plan)}] {section_title}")
            
            # Show progress
            full_text += f"\n## {section_title}\n\n⏳ Generating...\n"
            report.full_content = full_text
            self.db.commit()

            # Varied context
            chunk_start = (idx * 3) % len(all_chunks)
            chunk_end = min(chunk_start + 4, len(all_chunks))
            context = "\n\n".join(all_chunks[chunk_start:chunk_end])

            prompt = f"""Write a {target_words}-word section about {section_title} for a research paper on {topic}.

Be concise and clear. Use this reference:
{context[:1500]}

Write {section_title}:"""

            try:
                start = time.time()
                section_text = self.llm.generate(prompt)
                elapsed = time.time() - start
                
                print(f"   ✓ Done in {elapsed:.1f}s")
                
            except Exception as e:
                print(f"   ✗ Error: {e}")
                section_text = f"{context[:1000]}"

            if not section_text or len(section_text.strip()) < 200:
                section_text = f"{context[:1000]}"

            # Replace progress indicator with content
            full_text = full_text.replace(
                f"\n## {section_title}\n\n⏳ Generating...\n",
                f"\n## {section_title}\n\n{section_text}\n"
            )

            report.full_content = full_text
            self.db.commit()

        # Add references
        if source_urls:
            full_text += "\n\n---\n\n## References\n\n"
            for idx, u in enumerate(source_urls, 1):
                full_text += f"{idx}. {u}\n"

        report.full_content = full_text
        self.db.commit()
        self.db.refresh(report)

        print(f"\n✅ Complete: {len(full_text)} chars")

        return report

    def ask_from_report(self, project_id: int, question: str):
        report = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )
        
        if not report or not report.full_content:
            return "No report found."

        context = report.full_content[:4000]

        prompt = f"""Answer in 5 lines using this content:

{context}

Question: {question}

Answer:"""

        try:
            return self.qa_llm.generate(prompt).strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def expand_to_ieee(self, project_id: int):
        print("\n📄 Generating IEEE paper...")

        existing = (
            self.db.query(IEEEReport)
            .filter(IEEEReport.project_id == project_id)
            .order_by(desc(IEEEReport.id))
            .first()
        )

        if existing and existing.full_content and len(existing.full_content) > 1000:
            print("♻️ Reusing existing IEEE report")
            return existing

        report = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if not report or not report.full_content:
            raise Exception("No base report found")

        print("🧠 Converting to IEEE format...")

        # ⚡ REDUCED INPUT SIZE - only use first 6000 chars instead of 10000
        prompt = f"""Convert this to IEEE paper format with these sections: Title, Abstract, Keywords, Introduction, Background, Core Concepts, Architecture, Applications, Advantages/Limitations, Conclusion, References.

Use formal academic tone. Keep it concise.

Base report:
{report.full_content[:6000]}

Write IEEE paper:"""

        try:
            start_time = time.time()
            ieee_text = self.ieee_llm.generate(prompt)
            elapsed = time.time() - start_time
            print(f"✅ IEEE generated in {elapsed:.1f}s")
            
        except Exception as e:
            print(f"❌ IEEE generation error: {str(e)}")
            # Fallback: use original report with IEEE header
            ieee_text = f"""### Title: {report.title.replace('Research:', '').strip()}

### Abstract:
{report.full_content[:1000]}

### Keywords:
Research, Analysis, Technology

{report.full_content}
"""
            print("⚠️ Using fallback IEEE format")

        if not ieee_text or len(ieee_text.strip()) < 500:
            print("⚠️ IEEE output too short, using fallback")
            ieee_text = f"""### Title: {report.title.replace('Research:', '').strip()}

### Abstract:
{report.full_content[:1000]}

### Keywords:
Research, Analysis, Technology

{report.full_content}
"""

        ieee = IEEEReport(
            project_id=project_id,
            title=f"IEEE: {report.title.replace('Research:', '').strip()}",
            full_content=ieee_text
        )

        self.db.add(ieee)
        self.db.commit()
        self.db.refresh(ieee)

        print(f"✅ IEEE saved ({len(ieee_text)} chars)")

        return ieee

    def split_report_into_sections(self, project_id: int):
        print("\n✂️ Splitting into sections...")

        report = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if not report or not report.full_content:
            raise Exception("No report to split")

        self.db.query(ReportSection).filter(
            ReportSection.report_id == report.id
        ).delete()
        self.db.commit()

        lines = report.full_content.split("\n")
        sections = []
        current_title = None
        current_content = []
        order = 1

        def is_heading(line):
            line = line.strip()
            return line.startswith("#")

        def clean_heading(line):
            return line.lstrip("#").strip()

        for line in lines:
            if is_heading(line):
                if current_title and current_content:
                    content_text = "\n".join(current_content).strip()
                    if len(content_text) >= 200:
                        sections.append((current_title, content_text, order))
                        order += 1

                current_title = clean_heading(line)
                current_content = []
            else:
                if current_title is not None:
                    current_content.append(line)

        if current_title and current_content:
            content_text = "\n".join(current_content).strip()
            if len(content_text) >= 200:
                sections.append((current_title, content_text, order))

        objects = []
        for title, content, order_num in sections:
            obj = ReportSection(
                report_id=report.id,
                title=title,
                content=content,
                order=order_num
            )
            objects.append(obj)

        if objects:
            self.db.bulk_save_objects(objects)
            self.db.commit()
            print(f"✅ Split into {len(objects)} sections")

        return {"sections_created": len(objects)}