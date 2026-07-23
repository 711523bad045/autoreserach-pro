import re

from app.llm.groq_client import GroqClient


class DiagramService:

    @staticmethod
    def generate_architecture(report_text: str):

        prompt = f"""
You are an IEEE research expert.

Read the research report.

Return ONLY a Mermaid graph.

Rules:

- graph TD
- 6 to 10 nodes
- No explanation
- No markdown
- No ```mermaid
- Only Mermaid syntax

Research:

{report_text[:6000]}
"""

        mermaid = GroqClient.generate(prompt)

        mermaid = mermaid.replace("```mermaid", "")
        mermaid = mermaid.replace("```", "")
        mermaid = mermaid.strip()

        if not mermaid.startswith("graph"):
            mermaid = DiagramService.default_diagram()

        return mermaid

    @staticmethod
    def generate_flowchart(report_text: str):

        prompt = f"""
Generate ONLY a Mermaid flowchart.

Rules:

graph TD

No markdown.

Research:

{report_text[:6000]}
"""

        mermaid = GroqClient.generate(prompt)

        mermaid = mermaid.replace("```mermaid", "")
        mermaid = mermaid.replace("```", "")
        mermaid = mermaid.strip()

        if not mermaid.startswith("graph"):
            mermaid = DiagramService.default_flow()

        return mermaid

    @staticmethod
    def default_diagram():

        return """
graph TD

A[Input Data]
-->B[Preprocessing]

B-->C[Feature Extraction]

C-->D[AI Model]

D-->E[Prediction]

E-->F[Output]
"""

    @staticmethod
    def default_flow():

        return """
graph TD

A[Collect Papers]

-->B[Analyze]

B-->C[Extract Knowledge]

C-->D[Generate Report]

D-->E[Export PDF]
"""