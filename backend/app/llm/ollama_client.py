import requests

class OllamaClient:
    def __init__(self, model="qwen2.5:3b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        r = requests.post(self.url, json=payload, timeout=300)
        r.raise_for_status()
        return r.json()["response"]
