from app.llm.groq_client import GroqClient

llm = GroqClient()


class ReportAgent:

    @staticmethod
    def write_section(
        topic,
        section,
        knowledge,
        words=500
    ):

        prompt = f"""
You are a senior IEEE research paper writer.

Write ONLY the CONTENT for the requested section.

TOPIC
------
{topic}

SECTION
-------
{section}

AVAILABLE EVIDENCE
------------------

Problems:
{knowledge["problems"]}

Methods:
{knowledge["methods"]}

Datasets:
{knowledge["datasets"]}

Results:
{knowledge["results"]}

Limitations:
{knowledge["limitations"]}

Future Work:
{knowledge["future_work"]}

Keywords:
{knowledge["keywords"]}

WRITING RULES
-------------

1. Use ONLY the supplied evidence.
2. Never invent facts.
3. Do not hallucinate.
4. Write in professional IEEE academic English.
5. Produce approximately {words} words.
6. Write clear, detailed paragraphs.
7. Explain the concepts logically.
8. Avoid repetition.
9. Do not use markdown.
10. Do not use bullet points unless absolutely necessary.
11. Do NOT write the section heading.
12. Do NOT write words like:
    - Introduction
    - Background
    - Conclusion
    - Related Work
    - Methodology
13. Return ONLY the body content.
14. Do NOT use #, ## or markdown headings.
15. Do NOT start with "This section".
16. Use formal research writing style.
17. Ensure originality and avoid plagiarism.

Return only the section content.
"""

        try:
            response = llm.generate(prompt)

            if not response:
                return ""

            # Remove accidental headings returned by the LLM
            lines = response.splitlines()

            cleaned = []

            skip_words = [
                "introduction",
                "background",
                "related work",
                "methodology",
                "architecture",
                "applications",
                "advantages",
                "limitations",
                "future work",
                "conclusion",
                "#",
                "##"
            ]

            for line in lines:
                text = line.strip()

                lower = text.lower().replace(":", "")

                if lower in skip_words:
                    continue

                if lower.startswith("#"):
                    continue

                cleaned.append(line)

            return "\n".join(cleaned).strip()

        except Exception as e:
            print("Report Agent Error:", e)
            return ""