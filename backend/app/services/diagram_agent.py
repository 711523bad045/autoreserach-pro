import json

from app.llm.groq_client import GroqClient

llm = GroqClient()


class DiagramAgent:

    @staticmethod
    def generate_architecture(topic, knowledge):

        prompt = f"""
You are a software architect.

Topic:
{topic}

Methods:
{knowledge["methods"]}

Datasets:
{knowledge["datasets"]}

Return ONLY valid JSON.

Example:

{{
 "title":"Architecture",
 "nodes":["User","Input","AI","Output"],
 "edges":[
   ["User","Input"],
   ["Input","AI"],
   ["AI","Output"]
 ]
}}
"""

        try:

            response = llm.generate(prompt)

            response = (
                response.replace("```json", "")
                .replace("```", "")
                .strip()
            )

            return json.loads(response)

        except Exception as e:

            print("Diagram Error:", e)

            return {
                "title": "Architecture",
                "nodes": [],
                "edges": []
            }