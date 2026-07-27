import re
import requests


class OpenAlexService:
    BASE_URL = "https://api.openalex.org/works"

    @staticmethod
    def _build_search_query(topic: str) -> str:
        """
        Same idea as SemanticScholarService: a project's own invented name
        (e.g. "ResearchPilot AI: An AI-Powered Automated Research Paper
        Generation System") is not a phrase that appears in real papers, so
        we extract keywords instead of searching the literal title.
        """
        if not topic:
            return topic

        cleaned = re.sub(r"[^\w\s-]", " ", topic)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        stopwords = {
            "a", "an", "the", "of", "for", "and", "or", "to", "in", "on",
            "with", "using", "based", "system", "systems"
        }
        words = [w for w in cleaned.split(" ") if w.lower() not in stopwords]

        return " ".join(words[:12]) if words else cleaned

    @staticmethod
    def _parse_results(data):
        papers = []

        for item in data.get("results", []):

            # ----------------------------
            # Abstract
            # ----------------------------
            abstract = ""

            inverted = item.get("abstract_inverted_index")

            if inverted:
                words = sorted(
                    inverted.items(),
                    key=lambda x: min(x[1])
                )
                abstract = " ".join(word for word, _ in words)

            # ----------------------------
            # Venue
            # ----------------------------
            venue = ""

            primary_location = item.get("primary_location")

            if primary_location and primary_location.get("source"):
                venue = primary_location["source"].get("display_name", "")

            # ----------------------------
            # Authors
            # ----------------------------
            authors = []

            for author in item.get("authorships") or []:
                author_info = author.get("author")
                if author_info:
                    authors.append(author_info.get("display_name", ""))

            papers.append(
                {
                    "paperId": item.get("id", ""),
                    "title": item.get("display_name", ""),
                    "abstract": abstract,
                    "year": item.get("publication_year"),
                    "citationCount": item.get("cited_by_count", 0),
                    "venue": venue,
                    "url": item.get("id", ""),
                    "authors": authors,
                }
            )

        return papers

    @staticmethod
    def _run_query(query: str, limit: int):
        params = {
            "search": query,
            "per-page": limit,
        }

        response = requests.get(
            OpenAlexService.BASE_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return OpenAlexService._parse_results(response.json())

    @staticmethod
    def search_papers(query: str, limit: int = 100):
        try:
            # First attempt: the literal topic, in case it's a real term.
            papers = OpenAlexService._run_query(query, limit)

            # Second attempt: if the literal query was too specific / a made
            # -up project name, retry with extracted keywords for a broader,
            # more forgiving full-text match.
            keyword_query = OpenAlexService._build_search_query(query)

            if len(papers) < 3 and keyword_query and keyword_query != query:
                print(
                    f"OpenAlex: only {len(papers)} result(s) for literal "
                    f"query, retrying with keywords: '{keyword_query}'"
                )
                keyword_papers = OpenAlexService._run_query(
                    keyword_query, limit
                )

                # Merge + dedupe by paper id / title, keeping order.
                seen = {p["paperId"] or p["title"] for p in papers}
                for p in keyword_papers:
                    key = p["paperId"] or p["title"]
                    if key not in seen:
                        papers.append(p)
                        seen.add(key)

            print(f"OpenAlex returned {len(papers)} papers.")
            return papers

        except Exception as e:
            print(f"OpenAlex Error: {e}")
            return []