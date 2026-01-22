from sqlalchemy.orm import Session
from typing import List

from app.services.vector_service import VectorService
from app.llm.ollama_client import OllamaClient


class RAGService:

    def __init__(self):
        # FAST model
        self.llm = OllamaClient(model_name="qwen2.5:1.5b")
        self.cache = {}

    # ----------------------------------------
    # Internal helpers
    # ----------------------------------------

    def _retrieve_context(self, db: Session, top_k: int = 5) -> List[str]:
        chunks = VectorService.build_index(db, limit=top_k)

        texts = []
        for ch in chunks:
            if ch.content:
                texts.append(ch.content[:800])  # HARD LIMIT

        return texts

    def _build_prompt(self, contexts: List[str], question: str) -> str:
        context_text = "\n\n".join(contexts)

        prompt = f"""
You are a research assistant.

You MUST answer using ONLY the context below.
If the answer is not present in the context, say:
"I could not find the answer in the provided documents."

Context:
{context_text}

Question:
{question}

Answer in 6–10 sentences maximum. Be concise and factual.
""".strip()

        return prompt

    # ----------------------------------------
    # Public API
    # ----------------------------------------

    def ask_question(self, db: Session, project_id: int, question: str, top_k: int = 5):
        cache_key = (project_id, question)
        if cache_key in self.cache:
            return self.cache[cache_key]

        contexts = self._retrieve_context(db, top_k)

        if not contexts:
            result = {
                "answer": "No relevant information found in knowledge base."
            }
            self.cache[cache_key] = result
            return result

        prompt = self._build_prompt(contexts, question)

        answer = self.llm.generate(prompt)

        result = {
            "answer": answer
        }

        self.cache[cache_key] = result
        return result

    # ----------------------------------------
    # Used by report generator
    # ----------------------------------------

    def generate_section(self, db: Session, section_title: str) -> str:
        contexts = self._retrieve_context(db, top_k=5)

        if not contexts:
            return "No data available for this section."

        prompt = self._build_prompt(contexts, section_title)

        answer = self.llm.generate(prompt)

        return answer
