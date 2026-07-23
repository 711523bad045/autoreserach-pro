from app.llm.groq_client import GroqClient


class ResearchGapService:

    def __init__(self):
        self.llm = GroqClient()

    def detect(self, topic, papers):

        context = ""

        for paper in papers[:20]:

            context += f"""

Title:
{paper.get("title")}

Abstract:
{paper.get("abstract")}

"""

        prompt = f"""
You are an experienced research scientist.

Topic:

{topic}

Below are abstracts from top-ranked scientific papers.

Your task:

1. Find research gaps.

2. Mention unresolved problems.

3. Mention contradictory findings.

4. Suggest future research.

5. Give confidence (0-100).

Return JSON.

{context}
"""

        return self.llm.generate(prompt)