from sqlalchemy.orm import Session
from sqlalchemy import desc
import traceback
import time

from app.database.models import Report, Source, Chunk, ResearchProject, ReportSection
from app.database.models import IEEEReport

from app.llm.groq_client import GroqClient

from app.services.research_provider import ResearchProvider
from app.services.paper_ranking_service import PaperRankingService
from app.services.embedding_service import EmbeddingService
from app.services.evidence_service import EvidenceService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.report_agent import ReportAgent
from app.services.figure_service import FigureService
from app.services.report_builder import ReportBuilder

class ReportService:
    def __init__(self, db: Session):
        self.db = db

        self.llm =GroqClient()

        self.ieee_llm =GroqClient()

        self.qa_llm = GroqClient()

    def generate_simple_report(self, project_id: int):
        project = self.db.query(ResearchProject).filter(
            ResearchProject.id == project_id
        ).first()
        
        if not project:
            raise Exception("Project not found")

        topic = project.title
        builder = ReportBuilder()
        builder.set_title(topic)

        # Check for existing report
        existing = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if existing and existing.full_content and len(existing.full_content) > 5000:
            print("Reusing existing report")
            return existing

        print("Generating NEW report for:", topic)

        if existing:
            report = existing
            report.full_content = " Preparing sources...\n"
            self.db.commit()
        else:
            report = Report(
                project_id=project_id,
                title=f"Research: {topic}",
                full_content=" Preparing sources...\n"
            )
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)

       # Semantic Scholar Search
        try:
            papers = ResearchProvider.search(topic)

            papers = PaperRankingService.rank(
                papers,
                topic=topic
            )

            print("Extracting evidence...")

            evidence = EvidenceService.extract_many(papers)
            knowledge = KnowledgeBaseService.build(
                evidence
            )

            print()

            print("Knowledge Base")

            print("----------------")

            print("Problems:", len(knowledge["problems"]))

            print("Methods:", len(knowledge["methods"]))

            print("Datasets:", len(knowledge["datasets"]))

            print("Results:", len(knowledge["results"]))

            print("Limitations:", len(knowledge["limitations"]))

            from app.services.research_gap_service import ResearchGapService

            gap_service = ResearchGapService()

            gap_analysis = gap_service.detect(
                topic,
                evidence
            )
            print()
            print("Generating Figures...")

            figures = FigureService.generate_all(
                project_id=project_id,
                topic=topic,
                knowledge=knowledge,
            )
            builder.add_figure(
                "System Architecture",
                figures["architecture"]
            )

            builder.add_figure(
                "Workflow Diagram",
                figures["workflow"]
            )

            builder.add_figure(
                "Accuracy Comparison",
                figures["accuracy"]
            )

            builder.add_figure(
                "Performance Comparison",
                figures["comparison"]
            )

            print("All figures generated.")
                                

            print(f"Using {len(papers)} top ranked papers.")
        except Exception as e:
            print(f"Semantic Scholar Error: {e}")

            raise Exception(
                "Groq API quota exceeded. Wait for the quota to reset or use another API key."
            )

        if not papers:
            report.full_content = "No research papers found."
            self.db.commit()
            raise Exception("No research papers found.")

        all_chunks = []
        source_urls = []

        # Scrape sources
        all_chunks = []
        source_urls = []

        for paper in papers:

            try:
                title = paper.get("title", "Unknown")

                abstract = paper.get("abstract", "")

                year = paper.get("year", "")

                citations = paper.get("citationCount", 0)

                url = paper.get("url", "")

                if not abstract:
                    continue

                src = Source(
                    project_id=project_id,
                    title=title,
                    url=url,
                    content=abstract
                )

                self.db.add(src)
                self.db.commit()
                self.db.refresh(src)

                source_urls.append(url)

                all_chunks.append(
                    f"""
        Title: {title}

        Year: {year}

        Citation Count: {citations}

        Abstract:
        {abstract}
        """
                )

            except Exception as e:
                print(f"Paper Error: {e}")
                continue
                

        if len(all_chunks) < 3:
            raise Exception(" Too little content")

        print(f" Collected {len(all_chunks)} chunks")
        embedding_service = EmbeddingService()

        index, embeddings = embedding_service.build_index(all_chunks)

        #  REDUCED SECTION SIZES FOR SPEED
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
            print(f"\n [{idx+1}/{len(sections_plan)}] {section_title}")
            
            # Show progress
            full_text += f"\n## {section_title}\n\n Generating...\n"
            report.full_content = full_text
           
            self.db.commit()

            # Varied context
            retrieved_chunks = embedding_service.search(
                section_title,
                all_chunks,
                index,
                k=5
            )

            context = "\n\n".join(retrieved_chunks)

            prompt = f"""
You are an IEEE research writer.

Topic:
{topic}

Section:
{section_title}

Reference Material:
{context[:2500]}

Instructions:

- Use ONLY the supplied reference material.
- Never invent facts.
- Write in formal academic English.
- Avoid plagiarism.
- Produce original wording.
- Explain concepts clearly.
- Do not use bullet points unless necessary.
- Target approximately {target_words} words.

Write only the {section_title} section.
"""

            try:
                start = time.time()
                section_text = ReportAgent.write_section(
                    topic=topic,
                    section=section_title,
                    knowledge=knowledge,
                    words=target_words
                )
                builder.add_section(
                    section_title,
                    section_text
                )
                elapsed = time.time() - start
                
                print(f"   ✓ Done in {elapsed:.1f}s")
                
            except Exception as e:
                print(f"   ✗ Error: {e}")
                section_text = f"{context[:1000]}"

            if not section_text or len(section_text.strip()) < 200:
                section_text = f"{context[:1000]}"

            # Replace progress indicator with content
            full_text = full_text.replace(
                f"\n## {section_title}\n\n Generating...\n",
                f"\n## {section_title}\n\n{section_text}\n"
            )

            report.full_content = full_text
            
            
            self.db.commit()

        # Add references
        if source_urls:
            full_text += "\n\n---\n\n## References\n\n"
            for idx, u in enumerate(source_urls, 1):
                builder.add_reference(u)
                full_text += f"{idx}. {u}\n"
        full_text += "\n\n---\n"
        full_text += """

        # System Architecture

        [[IMAGE:architecture]]

        Figure 1. Overall System Architecture


        # Workflow Diagram

        [[IMAGE:workflow]]

        Figure 2. Proposed Workflow


        # Performance Evaluation

        [[IMAGE:accuracy]]

        Figure 3. Accuracy Comparison


        [[IMAGE:comparison]]

        Figure 4. Performance Comparison

        """

        full_text += "\n# Research Gap Analysis\n\n"

        full_text += str(gap_analysis)

        report.full_content = full_text
        
        self.db.commit()
        self.db.refresh(report)
        structured_report = builder.build()

        report.structured_content = structured_report

        self.db.commit()

        print("\n===== Structured Report =====")

        print(structured_report)

        print(f"\nComplete: {len(full_text)} chars")

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
        print("\n Generating IEEE paper...")

        existing = (
            self.db.query(IEEEReport)
            .filter(IEEEReport.project_id == project_id)
            .order_by(desc(IEEEReport.id))
            .first()
        )

        if existing and existing.full_content and len(existing.full_content) > 1000:
            print(" Reusing existing IEEE report")
            return existing

        report = (
            self.db.query(Report)
            .filter(Report.project_id == project_id)
            .order_by(desc(Report.id))
            .first()
        )

        if not report or not report.full_content:
            raise Exception("No base report found")

        print(" Converting to IEEE format...")
        from app.services.ieee_formatter import IEEEFormatter

        #  REDUCED INPUT SIZE - only use first 6000 chars instead of 10000


        builder = ReportBuilder()

        builder.set_title(report.title.replace("Research:", "").strip())

        builder.abstract = report.full_content[:1000]

        builder.keywords = [
            "Artificial Intelligence",
            "Research",
            "Machine Learning"
        ]

        sections = report.full_content.split("##")

        for sec in sections:

            sec = sec.strip()

            if not sec:
                continue

            lines = sec.split("\n", 1)

            title = lines[0].strip()

            body = lines[1].strip() if len(lines) > 1 else ""

            builder.add_section(title, body)
        builder.add_figure(
            "System Architecture",
            "architecture"
        )

        builder.add_figure(
            "Workflow Diagram",
            "workflow"
        )

        builder.add_figure(
            "Accuracy Comparison",
            "accuracy"
        )

        builder.add_figure(
            "Performance Comparison",
            "comparison"
        )
        ieee_text = IEEEFormatter.format(builder)

        print("IEEE report created using ReportBuilder.")

        if not ieee_text or len(ieee_text.strip()) < 500:
                    print(" IEEE output too short, using fallback")
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

        print(f" IEEE saved ({len(ieee_text)} chars)")

        return ieee

    def split_report_into_sections(self, project_id: int):
        print("\n Splitting into sections...")

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
            print(f" Split into {len(objects)} sections")

        return {"sections_created": len(objects)}