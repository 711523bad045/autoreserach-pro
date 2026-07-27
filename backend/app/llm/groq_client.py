from groq import Groq, RateLimitError
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class GroqQuotaExceededError(Exception):
    """
    Raised when the Groq API reports a rate limit / quota error (HTTP 429).
    This is distinct from a generic failure: once this happens, further
    calls in the same run are almost certainly going to fail too (daily
    token quotas don't reset for minutes/hours), so callers should stop
    retrying and degrade gracefully instead of hammering the API.
    """
    pass


class GroqClient:

    # Class-level flag: once we see a 429, avoid even attempting further
    # network calls for the rest of this process run. Saves time and log
    # spam once the daily quota is known to be exhausted.
    _quota_exhausted = False
    _quota_message = ""

    def __init__(
        self,
        model="llama-3.3-70b-versatile"
    ):
        self.model = model

    def generate(self, prompt):

        if GroqClient._quota_exhausted:
            raise GroqQuotaExceededError(
                GroqClient._quota_message or "Groq API quota exhausted."
            )

        try:
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

        except RateLimitError as e:
            GroqClient._quota_exhausted = True
            GroqClient._quota_message = str(e)
            raise GroqQuotaExceededError(str(e)) from e