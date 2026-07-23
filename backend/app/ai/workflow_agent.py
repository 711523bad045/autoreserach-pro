import json

from app.llm.groq_client import GroqClient


llm = GroqClient()


class WorkflowAgent:

    @staticmethod
    def generate(topic, knowledge):

        prompt = f"""
You are a senior AI Research Architect.

Generate a PROFESSIONAL research workflow.

TOPIC
------
{topic}

KNOWLEDGE
---------
Problems:
{knowledge["problems"]}

Methods:
{knowledge["methods"]}

Datasets:
{knowledge["datasets"]}

Results:
{knowledge["results"]}

Future Work:
{knowledge["future_work"]}

RULES

1. Create a workflow specifically for this topic.
2. NEVER use MRI workflow unless the topic is about MRI.
3. NEVER use Blockchain workflow unless topic is blockchain.
4. Return ONLY JSON.
5. Exactly 6-8 workflow steps.
6. Step names should be short.
7. No explanation.

Output format:

{{
    "title":"Workflow",
    "steps":[
        "Step 1",
        "Step 2",
        "Step 3",
        "Step 4",
        "Step 5",
        "Step 6"
    ]
}}
"""

        try:

            response = llm.generate(prompt)

            start = response.find("{")
            end = response.rfind("}")

            if start == -1 or end == -1:
                raise Exception("Invalid JSON")

            return json.loads(response[start:end + 1])

        except Exception as e:

            print("Workflow Agent Error:", e)

            return {
                "title": "Workflow",
                "steps": [
                    "Input",
                    "Preprocessing",
                    "Feature Extraction",
                    "Model",
                    "Evaluation",
                    "Output"
                ]
            }