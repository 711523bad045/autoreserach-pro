from app.services.semantic_scholar_service import SemanticScholarService
from app.services.openalex_service import OpenAlexService


class ResearchProvider:

    # Minimum usable papers (with abstracts) before we consider it worth
    # trying a second provider to top up the pool, even if the first
    # provider "succeeded".
    MIN_DESIRED_PAPERS = 5

    @staticmethod
    def _dedupe(papers):
        seen = set()
        unique = []
        for p in papers:
            key = (p.get("paperId") or p.get("title") or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(p)
        return unique

    @staticmethod
    def search(topic):

        combined = []

        print("Trying Semantic Scholar...")
        try:
            papers = SemanticScholarService.search_papers(topic)
        except Exception as e:
            print(f"Semantic Scholar unexpected error: {e}")
            papers = []

        if papers:
            print("Semantic Scholar Success")
            combined.extend(papers)
        else:
            print("Semantic Scholar failed.")

        # Try OpenAlex if Semantic Scholar failed OR didn't return enough
        # usable results — don't give up on extra sources just because the
        # first provider technically returned *something*.
        if len(combined) < ResearchProvider.MIN_DESIRED_PAPERS:
            print("Trying OpenAlex...")
            try:
                openalex_papers = OpenAlexService.search_papers(topic)
            except Exception as e:
                print(f"OpenAlex unexpected error: {e}")
                openalex_papers = []

            if openalex_papers:
                print("OpenAlex Success")
                combined.extend(openalex_papers)
            elif not combined:
                print("All providers failed.")

        combined = ResearchProvider._dedupe(combined)

        print(f"ResearchProvider: {len(combined)} unique paper(s) total.")

        return combined