from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class Parser:

    @staticmethod
    def extract_text_and_links(html: str, base_url: str):
        soup = BeautifulSoup(html, "lxml")

        # Remove scripts and styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full = urljoin(base_url, href)
            parsed = urlparse(full)
            if parsed.scheme in ("http", "https"):
                links.add(full)

        return text, list(links)
