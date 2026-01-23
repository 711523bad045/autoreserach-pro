import requests
from bs4 import BeautifulSoup

class ScrapeService:
    @staticmethod
    def fetch_text(domain: str) -> str:
        try:
            if not domain.startswith("http"):
                domain = "https://" + domain

            r = requests.get(domain, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")

            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            text = soup.get_text(separator=" ")
            text = " ".join(text.split())

            return text[:15000]  # limit size
        except Exception as e:
            print("Scrape failed:", e)
            return ""
