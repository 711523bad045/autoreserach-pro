import os
import uuid

from docx import Document
from docx.shared import Inches

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
)

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

GENERATED_DIAGRAMS = os.path.join(
    BASE_DIR,
    "generated_diagrams"
)


class ExportService:

    @staticmethod
    def export_to_word(report):

        filename = f"report_{uuid.uuid4().hex}.docx"
        filepath = os.path.join("tmp", filename)

        os.makedirs("tmp", exist_ok=True)

        doc = Document()

        doc.add_heading(report.title, 0)

        project_id = report.project_id

        image_map = {
            "[[IMAGE:architecture]]": f"{project_id}_architecture.png",
            "[[IMAGE:workflow]]": f"{project_id}_workflow.png",
            "[[IMAGE:accuracy]]": f"{project_id}_accuracy.png",
            "[[IMAGE:comparison]]": f"{project_id}_comparison.png",
        }

        for line in report.full_content.split("\n"):

            line = line.strip()

            if not line:
                doc.add_paragraph("")
                continue

            inserted = False

            for tag, filename in image_map.items():

                if tag in line:

                    image = os.path.join(GENERATED_DIAGRAMS, filename)

                    print(image)
                    print(os.path.exists(image))

                    if os.path.exists(image):
                        doc.add_picture(image, width=Inches(6))

                    inserted = True
                    break

            if inserted:
                continue

            doc.add_paragraph(line)

        doc.save(filepath)

        return filepath

    @staticmethod
    def export_to_pdf(report):

        filename = f"report_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join("tmp", filename)

        os.makedirs("tmp", exist_ok=True)

        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        story = []

        story.append(
            Paragraph(
                f"<b>{report.title}</b>",
                styles["Title"],
            )
        )

        story.append(Spacer(1, 20))

        project_id = report.project_id

        image_map = {
            "[[IMAGE:architecture]]": f"{project_id}_architecture.png",
            "[[IMAGE:workflow]]": f"{project_id}_workflow.png",
            "[[IMAGE:accuracy]]": f"{project_id}_accuracy.png",
            "[[IMAGE:comparison]]": f"{project_id}_comparison.png",
        }

        for line in report.full_content.split("\n"):

            line = line.strip()

            if not line:
                story.append(Spacer(1, 6))
                continue

            inserted = False

            for tag, filename in image_map.items():

                if tag in line:

                    image = os.path.join(GENERATED_DIAGRAMS, filename)

                    print(image)
                    print(os.path.exists(image))

                    if os.path.exists(image):
                        story.append(
                            Image(
                                image,
                                width=6.2 * inch,
                                height=3.6 * inch,
                            )
                        )

                    inserted = True
                    break

            if inserted:
                continue

            if line.startswith("# "):
                story.append(
                    Paragraph(
                        f"<b>{line[2:]}</b>",
                        styles["Heading1"],
                    )
                )
                continue

            if line.startswith("## "):
                story.append(
                    Paragraph(
                        f"<b>{line[3:]}</b>",
                        styles["Heading2"],
                    )
                )
                continue

            if line.startswith("### "):
                story.append(
                    Paragraph(
                        f"<b>{line[4:]}</b>",
                        styles["Heading3"],
                    )
                )
                continue

            story.append(
                Paragraph(
                    line,
                    styles["BodyText"],
                )
            )

        doc.build(story)

        return filepath