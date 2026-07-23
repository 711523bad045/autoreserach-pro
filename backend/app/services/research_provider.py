from app.services.semantic_scholar_service import SemanticScholarService
from app.services.openalex_service import OpenAlexService


class ResearchProvider:

    @staticmethod
    def search(topic):

        print("Trying Semantic Scholar...")

        papers = SemanticScholarService.search_papers(topic)

        if papers:
            print("Semantic Scholar Success")
            return papers

        print("Semantic Scholar failed.")

        print("Trying OpenAlex...")

        papers = OpenAlexService.search_papers(topic)

        if papers:
            print("OpenAlex Success")
            return papers

        print("All providers failed.")

        return []