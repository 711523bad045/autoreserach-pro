import json

from app.llm.groq_client import GroqClient, GroqQuotaExceededError

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

        except GroqQuotaExceededError:
            # Let this propagate — the caller (extract_many) needs to know
            # the quota died so it can stop looping instead of retrying
            # every remaining paper against a dead API.
            raise

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
        quota_hit = False

        for paper in papers:

            try:
                item = EvidenceService.extract(paper)

            except GroqQuotaExceededError as e:
                print(
                    f"Evidence extraction stopped early — Groq quota "
                    f"exhausted after {len(results)}/{len(papers)} "
                    f"paper(s): {e}"
                )
                quota_hit = True
                break

            if item:
                results.append(item)

        if quota_hit and not results:
            print(
                "Warning: no evidence could be extracted before the quota "
                "ran out. The report will rely on whatever knowledge base "
                "entries can still be built (likely very sparse)."
            )

        return results