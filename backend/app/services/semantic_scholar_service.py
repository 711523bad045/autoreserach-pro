import os
import re
import time
import requests


class SemanticScholarService:
    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    HEADERS = {
        "User-Agent": "AutoResearch-Pro/1.0"
    }

    FIELDS = (
        "paperId,title,abstract,year,citationCount,"
        "authors,venue,url,externalIds"
    )

    @staticmethod
    def _build_search_query(topic: str) -> str:
        """
        Turn a project/topic title into a search-engine-friendly query.
        Long, punctuation-heavy project names (e.g. "ResearchPilot AI: An
        AI-Powered Automated Research Paper Generation System") rarely match
        real paper titles verbatim, so we strip punctuation and drop very
        common filler words, keeping the meaningful keywords.
        """
        if not topic:
            return topic

        # Drop punctuation (keep letters, numbers, spaces, hyphens)
        cleaned = re.sub(r"[^\w\s-]", " ", topic)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        stopwords = {
            "a", "an", "the", "of", "for", "and", "or", "to", "in", "on",
            "with", "using", "based", "system", "systems"
        }
        words = [w for w in cleaned.split(" ") if w.lower() not in stopwords]

        # Keep it focused — very long queries tend to match fewer papers.
        return " ".join(words[:12]) if words else cleaned

    @staticmethod
    def search_papers(query: str, limit: int = 100):

        search_query = SemanticScholarService._build_search_query(query)

        params = {
            "query": search_query,
            "limit": limit,
            "fields": SemanticScholarService.FIELDS,
        }

        api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
        headers = dict(SemanticScholarService.HEADERS)
        if api_key:
            headers["x-api-key"] = api_key

        max_attempts = 3
        backoff = 2

        for attempt in range(max_attempts):

            try:
                response = requests.get(
                    f"{SemanticScholarService.BASE_URL}/paper/search",
                    params=params,  # requests handles URL-encoding correctly
                    headers=headers,
                    timeout=30,
                )

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    wait = float(retry_after) if retry_after else backoff
                    print(
                        f"Semantic Scholar Rate Limit "
                        f"(Attempt {attempt + 1}/{max_attempts}, "
                        f"waiting {wait:.1f}s)"
                    )
                    time.sleep(wait)
                    backoff *= 2
                    continue

                response.raise_for_status()

                data = response.json()
                papers = data.get("data", [])

                print(f"Retrieved {len(papers)} papers")

                return papers

            except requests.exceptions.RequestException as e:
                print(f"Semantic Scholar Error: {e}")
                time.sleep(backoff)
                backoff *= 2

        # All retries failed
        return []