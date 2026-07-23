from app.llm.groq_client import GroqClient


class MermaidAgent:

    @staticmethod
    def architecture(topic, knowledge):

        prompt = f"""
You are an IEEE system architect.

Topic:
{topic}

Methods:
{knowledge["methods"]}

Return ONLY Mermaid flowchart syntax.

Example:

flowchart TD

A[Input]
B[Preprocessing]
C[AI Model]
D[Prediction]

A --> B
B --> C
C --> D

Do not explain.
Do not use markdown.
Return only Mermaid.
"""

        llm = GroqClient()

        return llm.generate(prompt)

    @staticmethod
    def workflow(topic, knowledge):

        prompt = f"""
Create a Mermaid workflow diagram.

Topic:
{topic}

Return ONLY Mermaid flowchart syntax.

Example:

flowchart TD

A[Collect Data]
B[Clean Data]
C[Train Model]
D[Test]
E[Deploy]

A --> B
B --> C
C --> D
D --> E
"""

        llm = GroqClient()

        return llm.generate(prompt)