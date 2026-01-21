import requests


class Fetcher:

    @staticmethod
    def fetch(url: str) -> str:
        headers = {
            "User-Agent": "AutoResearchProBot/1.0"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text
