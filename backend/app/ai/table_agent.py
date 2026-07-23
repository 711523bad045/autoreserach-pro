import json

from app.llm.groq_client import GroqClient

llm = GroqClient()


class TableAgent:

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

Generate ONE comparison table.

Return ONLY JSON.

Example:

{{
  "title":"Comparison of Existing Methods",
  "columns":["Method","Accuracy","Advantage","Limitation"],
  "rows":[
      ["CNN","91%","Fast","Lower accuracy"],
      ["ResNet","94%","Robust","Large model"],
      ["Proposed","97%","Best performance","Higher training time"]
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
                "title": "Comparison of Methods",
                "columns": [
                    "Method",
                    "Accuracy",
                    "Advantage",
                    "Limitation"
                ],
                "rows": [
                    ["Baseline", "85%", "Simple", "Low accuracy"],
                    ["Existing", "90%", "Stable", "Complex"],
                    ["Proposed", "95%", "High accuracy", "Training cost"]
                ]
            }