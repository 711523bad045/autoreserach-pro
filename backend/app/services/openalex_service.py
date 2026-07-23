import requests


class OpenAlexService:
    BASE_URL = "https://api.openalex.org/works"

    @staticmethod
    def search_papers(query: str, limit: int = 100):

        params = {
            "search": query,
            "per-page": limit,
        }

        try:

            response = requests.get(
                OpenAlexService.BASE_URL,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

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

                    abstract = " ".join(
                        word for word, _ in words
                    )

                # ----------------------------
                # Venue
                # ----------------------------
                venue = ""

                primary_location = item.get("primary_location")

                if (
                    primary_location
                    and primary_location.get("source")
                ):
                    venue = (
                        primary_location["source"]
                        .get("display_name", "")
                    )

                # ----------------------------
                # Authors
                # ----------------------------
                authors = []

                for author in item.get("authorships") or []:

                    author_info = author.get("author")

                    if author_info:
                        authors.append(
                            author_info.get(
                                "display_name",
                                ""
                            )
                        )

                papers.append(
                    {
                        "paperId": item.get("id", ""),
                        "title": item.get("display_name", ""),
                        "abstract": abstract,
                        "year": item.get("publication_year"),
                        "citationCount": item.get(
                            "cited_by_count",
                            0,
                        ),
                        "venue": venue,
                        "url": item.get("id", ""),
                        "authors": authors,
                    }
                )

            print(
                f"OpenAlex returned {len(papers)} papers."
            )

            return papers

        except Exception as e:

            print(f"OpenAlex Error: {e}")

            return []