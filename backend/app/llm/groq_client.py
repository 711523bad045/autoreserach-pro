from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class GroqClient:

    def __init__(
        self,
        model="llama-3.3-70b-versatile"
    ):
        self.model = model

    def generate(self, prompt):

        response = client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": """You are an IEEE research writer.

Never invent facts.

Use formal academic language.

Avoid plagiarism.

Write original content.

Use clear paragraphs."""
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.3,

            max_completion_tokens=4096

        )

        return response.choices[0].message.content