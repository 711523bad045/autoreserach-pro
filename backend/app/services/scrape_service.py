import requests
from bs4 import BeautifulSoup


class ScrapeService:
    @staticmethod
    def fetch_text(url: str) -> str:
        try:
            if not url.startswith("http"):
                url = "https://" + url

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            r = requests.get(url, headers=headers, timeout=25)
            soup = BeautifulSoup(r.text, "html.parser")

            for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form", "aside"]):
                tag.decompose()

            paragraphs = []
            for p in soup.find_all("p"):
                text = p.get_text().strip()
                if len(text) > 80:
                    paragraphs.append(text)

            text = "\n\n".join(paragraphs)

            if len(text) < 1500:
                print("⚠️ Too little content from:", url)
                return ""

            return text[:20000]

        except Exception as e:
            print("❌ Scrape failed:", url, e)
            return ""
