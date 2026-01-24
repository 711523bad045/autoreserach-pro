import requests
import urllib.parse


class WebSearchService:
    @staticmethod
    def search(query: str, max_results: int = 5):
        print("🔎 Searching Wikipedia for:", query)

        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AutoResearchBot/1.0"
        }

        try:
            r = requests.get(search_url, params=params, headers=headers, timeout=20)

            print("🌐 Wikipedia status code:", r.status_code)

            if r.status_code != 200:
                print("❌ Wikipedia HTTP error")
                print(r.text[:500])
                return []

            # DEBUG: check what we actually got
            if not r.text.strip().startswith("{"):
                print("❌ Wikipedia returned non-JSON content:")
                print(r.text[:500])
                return []

            data = r.json()

            if "query" not in data or "search" not in data["query"]:
                print("❌ Wikipedia JSON has no search results")
                print(data)
                return []

            results = data["query"]["search"]

            if not results:
                print("❌ No Wikipedia pages found")
                return []

            urls = []
            for item in results[:max_results]:
                title = item["title"]
                title_encoded = urllib.parse.quote(title.replace(" ", "_"))
                page_url = f"https://en.wikipedia.org/wiki/{title_encoded}"
                urls.append(page_url)

            print("✅ Found URLs:")
            for u in urls:
                print("   ", u)

            return urls

        except Exception as e:
            print("❌ Wikipedia search failed with exception:", e)
            return []


class WebScraper:
    @staticmethod
    def scrape(url: str):
        try:
            print("🌐 Scraping:", url)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AutoResearchBot/1.0"
            }

            r = requests.get(url, headers=headers, timeout=25)

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, "html.parser")

            # Remove junk
            for s in soup(["script", "style", "noscript", "header", "footer", "nav", "form", "aside"]):
                s.extract()

            content = soup.find("div", {"id": "mw-content-text"})
            if not content:
                print("⚠️ No content div found")
                return url, ""

            text = content.get_text(separator=" ")
            text = " ".join(text.split())

            # Limit size
            text = text[:30000]

            title = soup.title.string if soup.title else url

            if len(text) < 1500:
                print("⚠️ Too little content")
                return title, ""

            print("✅ Scraped", len(text), "chars")

            return title, text

        except Exception as e:
            print("❌ Scrape failed:", e)
            return url, ""
