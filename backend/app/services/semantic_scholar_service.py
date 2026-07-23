import time
import requests


class SemanticScholarService:
    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    HEADERS = {
        "User-Agent": "AutoResearch-Pro/1.0"
    }

    @staticmethod
    def search_papers(query: str, limit: int = 100):

        url = (
            f"{SemanticScholarService.BASE_URL}/paper/search"
            f"?query={query}"
            f"&limit={limit}"
            f"&fields="
            f"paperId,"
            f"title,"
            f"abstract,"
            f"year,"
            f"citationCount,"
            f"authors,"
            f"venue,"
            f"url,"
            f"externalIds"
        )

        # Retry 3 times
        for attempt in range(3):

            try:

                response = requests.get(
                    url,
                    headers=SemanticScholarService.HEADERS,
                    timeout=30,
                )

                # Too Many Requests
                if response.status_code == 429:

                    print(
                        f"Semantic Scholar Rate Limit (Attempt {attempt+1}/3)"
                    )

                    time.sleep(3)

                    continue

                response.raise_for_status()

                data = response.json()

                papers = data.get("data", [])

                print(f"Retrieved {len(papers)} papers")

                return papers

            except requests.exceptions.RequestException as e:

                print(f"Semantic Scholar Error: {e}")

                time.sleep(2)

        # All retries failed
        return []