import requests
from typing import List


class OllamaClient:
    def __init__(self, model="qwen2.5:0.5b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "top_p": 0.9,
                "num_ctx": 2048
            }
        }

        # Increased timeout for safety (per section)
        r = requests.post(self.url, json=payload, timeout=180)
        r.raise_for_status()

        data = r.json()
        return data.get("response", "")

    def embed(self, text: str) -> List[float]:
        r = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=120
        )
        r.raise_for_status()
        return r.json()["embedding"]
