import json

from app.llm.groq_client import GroqClient

llm = GroqClient()


class ChartAgent:

    @staticmethod
    def generate(topic, knowledge):

        prompt = f"""
You are an IEEE research analyst.

Research Topic:
{topic}

Methods:
{knowledge["methods"]}

Results:
{knowledge["results"]}

Generate ONE comparison chart.

Return ONLY JSON.

Example:

{{
    "title":"Accuracy Comparison",
    "labels":[
        "Method A",
        "Method B",
        "Method C",
        "Proposed"
    ],
    "values":[
        89,
        92,
        94,
        97
    ]
}}
"""

        try:

            response = llm.generate(prompt)

            start = response.find("{")
            end = response.rfind("}")

            return json.loads(response[start:end+1])

        except Exception:

            return {
                "title":"Performance Comparison",
                "labels":["Baseline","Existing","Proposed"],
                "values":[85,90,95]
            }