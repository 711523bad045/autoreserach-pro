import requests
import json
from typing import Iterator


class OllamaClient:
    """
    Production Ollama HTTP client with streaming support.
    """

    def __init__(self, model_name: str = "phi3:mini", base_url: str = "http://127.0.0.1:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        """
        Non-streaming generation (kept for compatibility).
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }

        response = requests.post(url, json=payload, timeout=600)

        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error: {response.text}")

        data = response.json()
        return data["response"]

    def stream_generate(self, prompt: str) -> Iterator[str]:
        """
        Streaming token generator.
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
        }

        with requests.post(url, json=payload, stream=True, timeout=600) as r:
            r.raise_for_status()

            for line in r.iter_lines():
                if not line:
                    continue

                data = json.loads(line.decode("utf-8"))

                if "response" in data:
                    yield data["response"]

                if data.get("done"):
                    break
