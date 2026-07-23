import json

from app.llm.groq_client import GroqClient

llm = GroqClient()


class EvidenceService:

    @staticmethod
    def extract(paper):

        title = paper.get("title", "")
        abstract = paper.get("abstract", "")

        if not abstract:
            return None

        prompt = f"""
You are an expert research analyst.

Read the following research paper abstract.

Extract ONLY the important research evidence.

Return ONLY valid JSON.

{{
    "problem":"",
    "method":"",
    "dataset":"",
    "result":"",
    "limitation":"",
    "future_work":"",
    "keywords":[]
}}

Title:
{title}

Abstract:
{abstract}
"""

        try:

            response = llm.generate(prompt)

            response = (
                response.replace("```json", "")
                .replace("```", "")
                .strip()
            )

            evidence = json.loads(response)

        except Exception as e:

            print("Evidence Extraction Error:", e)

            evidence = {
                "problem": "",
                "method": "",
                "dataset": "",
                "result": "",
                "limitation": "",
                "future_work": "",
                "keywords": [],
            }

        evidence["title"] = title
        evidence["year"] = paper.get("year")
        evidence["citationCount"] = paper.get("citationCount")
        evidence["venue"] = paper.get("venue")
        evidence["url"] = paper.get("url")

        return evidence

    @staticmethod
    def extract_many(papers):

        results = []

        for paper in papers:

            item = EvidenceService.extract(paper)

            if item:
                results.append(item)

        return results