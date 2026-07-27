import re
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


def _clean_text(text: str) -> str:
    """Strip stray markdown symbols and collapse whitespace."""
    if not text:
        return ""
    cleaned = re.sub(r"[#*_`]", "", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _build_abstract(source_text: str, max_words: int = 150) -> str:
    """
    Build a real abstract paragraph from a section's text (normally the
    Introduction), instead of blindly slicing the first N raw characters
    of the whole markdown report (which used to include literal '#'
    headings and produce garbage output).
    """
    cleaned = _clean_text(source_text)
    if not cleaned:
        return ""

    words = cleaned.split(" ")
    if len(words) > max_words:
        cleaned = " ".join(words[:max_words]).rstrip(".,;: ") + "..."
    return cleaned


def _derive_keywords(topic: str, max_keywords: int = 6):
    """
    Derive keywords from the project topic instead of using a hardcoded,
    unrelated placeholder list. Heuristic: split the topic on common
    connector words/punctuation into meaningful phrases, pull out any
    parenthetical acronyms (e.g. "(IoT)") as extra keywords, and dedupe.
    """
    if not topic:
        return []

    parenthetical = re.findall(r"\(([^)]+)\)", topic)
    base = re.sub(r"\([^)]*\)", "", topic)

    parts = re.split(
        r"\s*[:,]\s*|\s+for\s+|\s+using\s+|\s+with\s+|\s+via\s+|-[Bb]ased\s+",
        base,
    )

    stopwords = {
        "a", "an", "the", "of", "and", "or", "to", "in", "on",
        "system", "systems"
    }

    keywords = []
    for part in parts:
        part = part.strip(" -")
        if not part:
            continue
        words = [w for w in part.split() if w.lower() not in stopwords]
        phrase = " ".join(words).strip()
        if phrase and len(phrase) > 2:
            keywords.append(phrase)

    for p in parenthetical:
        if p not in keywords:
            keywords.append(p)

    seen = set()
    unique = []
    for k in keywords:
        key = k.lower()
        if key not in seen:
            seen.add(key)
            unique.append(k)

    return unique[:max_keywords]


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
        builder.set_keywords(_derive_keywords(topic))

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

       # Semantic Scholar Search (falls back to / merges with OpenAlex
       # inside ResearchProvider)
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

            print("Problems:", len(knowledge.get("problems", [])))

            print("Methods:", len(knowledge.get("methods", [])))

            print("Datasets:", len(knowledge.get("datasets", [])))

            print("Results:", len(knowledge.get("results", [])))

            print("Limitations:", len(knowledge.get("limitations", [])))

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
            # Don't mask the real error behind a generic "Groq quota" message.
            # Log the full traceback and surface the actual exception to the caller.
            print(f"Report generation pipeline error: {e}")
            traceback.print_exc()
            raise Exception(f"Report generation failed while gathering research: {e}")

        if not papers:
            report.full_content = "No research papers found."
            self.db.commit()
            raise Exception(
                "No research papers found for this topic. Try a broader or "
                "differently phrased project title."
            )

        all_chunks = []
        source_urls = []

        # Scrape sources
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
            report.full_content = (
                f" Only {len(all_chunks)} usable source(s) with abstracts were found "
                "(need at least 3). This usually happens when the search API is "
                "rate-limited and falls back to a provider with fewer results. "
                "Try again shortly, or use a broader project title.\n"
            )
            self.db.commit()
            raise Exception(
                f"Too little content: only {len(all_chunks)} paper(s) with abstracts "
                "were found (minimum 3 required). This is usually caused by a "
                "Semantic Scholar rate limit forcing a fallback to a provider that "
                "returned few results — try again in a bit or broaden the topic."
            )

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

        intro_text = ""

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

            try:
                start = time.time()
                section_text = ReportAgent.write_section(
                    topic=topic,
                    section=section_title,
                    knowledge=knowledge,
                    words=target_words
                )
                elapsed = time.time() - start
                
                print(f"   ✓ Done in {elapsed:.1f}s")
                
            except Exception as e:
                print(f"   ✗ Error: {e}")
                traceback.print_exc()
                section_text = f"{context[:1000]}"

            if not section_text or len(section_text.strip()) < 200:
                print(f"   ⚠ '{section_title}' output too short/empty, using raw context fallback")
                section_text = f"{context[:1000]}"

            # Add to the structured builder AFTER the fallback is resolved,
            # so builder.report["sections"] always matches what actually
            # ends up in full_text — previously this was added before the
            # fallback logic ran, so a short/failed section could leave the
            # structured report with different (or missing) content than
            # the markdown version.
            builder.add_section(section_title, section_text)

            if section_title == "Introduction":
                intro_text = section_text

            # Replace progress indicator with content
            full_text = full_text.replace(
                f"\n## {section_title}\n\n Generating...\n",
                f"\n## {section_title}\n\n{section_text}\n"
            )

            report.full_content = full_text
            
            
            self.db.commit()

        # Build a real abstract from the Introduction section instead of
        # leaving it blank / slicing raw markdown.
        builder.set_abstract(_build_abstract(intro_text))

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

        # NOTE: this requires a `structured_content` JSON column on the
        # Report model to actually persist. If that column doesn't exist,
        # setting the attribute directly would just create a throwaway
        # Python attribute that vanishes on the next DB fetch — check via
        # the mapped table's columns instead of hasattr (which would be
        # true either way once we set it below).
        has_column = "structured_content" in report.__table__.columns

        if has_column:
            report.structured_content = structured_report
        else:
            print(
                "WARNING: Report model has no 'structured_content' column — "
                "skipping persistence. Add this column to app/database/models.py "
                "so expand_to_ieee can use the clean structured data instead of "
                "falling back to markdown re-parsing."
            )

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

        builder = ReportBuilder()

        clean_title = report.title.replace("Research:", "").strip()
        builder.set_title(clean_title)

        structured = getattr(report, "structured_content", None)

        if structured and structured.get("sections"):
            # Preferred path: reuse the already-clean structured data built
            # during generate_simple_report, instead of re-parsing the
            # markdown text (which was the source of the duplicated/blank
            # Abstract & Keywords and the stray "# Title" pseudo-section).
            print(" Using structured_content (preferred, clean path)")

            builder.set_abstract(
                structured.get("abstract")
                or _build_abstract(report.full_content[:1500])
            )
            builder.set_keywords(
                structured.get("keywords") or _derive_keywords(clean_title)
            )

            for sec in structured["sections"]:
                title = (sec.get("title") or "").lstrip("#").strip()
                content = (sec.get("content") or "").strip()
                if title:
                    builder.add_section(title, content)

            for ref in structured.get("references", []):
                builder.add_reference(ref)

        else:
            # Legacy fallback for older reports that don't have
            # structured_content saved. Parses the markdown text directly,
            # fixed to skip the bogus title-only preamble chunk and to pull
            # references out as real reference entries instead of dumping
            # them (and any trailing figure/gap-analysis text) into a
            # generic "References" section.
            print(" No structured_content found — using legacy text parser")

            raw_sections = report.full_content.split("##")[1:]
            intro_text = ""

            for sec in raw_sections:
                sec = sec.strip()
                if not sec:
                    continue

                lines = sec.split("\n", 1)
                title = lines[0].strip().lstrip("#").strip()
                body = lines[1].strip() if len(lines) > 1 else ""

                if not title:
                    continue

                if title.lower() == "references":
                    for line in body.splitlines():
                        line = line.strip()
                        if line.lower().startswith("http"):
                            builder.add_reference(line)
                    continue

                builder.add_section(title, body)

                if title.lower() == "introduction":
                    intro_text = body

            builder.set_abstract(
                _build_abstract(intro_text) or _build_abstract(report.full_content[:1500])
            )
            builder.set_keywords(_derive_keywords(clean_title))

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
                    ieee_text = f"""### Title: {clean_title}

        ### Abstract:
        {report.full_content[:1000]}

        ### Keywords:
        Research, Analysis, Technology

        {report.full_content}
"""

        ieee = IEEEReport(
            project_id=project_id,
            title=f"IEEE: {clean_title}",
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