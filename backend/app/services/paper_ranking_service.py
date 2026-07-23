from difflib import SequenceMatcher


class PaperRankingService:

    HIGH_QUALITY_VENUES = [
        "ieee",
        "springer",
        "acm",
        "elsevier",
        "nature",
        "science",
        "cvpr",
        "iccv",
        "neurips",
        "icml",
        "aaai",
        "ijcai",
    ]

    @staticmethod
    def similarity(a, b):
        return SequenceMatcher(
            None,
            (a or "").lower(),
            (b or "").lower()
        ).ratio()

    @staticmethod
    def venue_score(venue):

        venue = (venue or "").lower()

        for v in PaperRankingService.HIGH_QUALITY_VENUES:
            if v in venue:
                return 15

        return 5

    @staticmethod
    def rank(papers, topic=""):

        ranked = []
        seen = set()

        for paper in papers:

            title = paper.get("title") or ""

            # Remove duplicate titles
            key = title.lower().strip()

            if key in seen:
                continue

            seen.add(key)

            citations = paper.get("citationCount") or 0
            year = paper.get("year") or 2000
            abstract = paper.get("abstract") or ""
            venue = paper.get("venue") or ""

            score = 0

            # ---------------------------
            # Topic Relevance (35)
            # ---------------------------

            relevance = PaperRankingService.similarity(
                topic,
                title + " " + abstract
            )

            score += relevance * 35

            # ---------------------------
            # Citations (25)
            # ---------------------------

            score += min(citations / 500, 1.0) * 25

            # ---------------------------
            # Recent Papers (20)
            # ---------------------------

            if year >= 2025:
                score += 20
            elif year >= 2023:
                score += 16
            elif year >= 2021:
                score += 12
            elif year >= 2019:
                score += 8
            else:
                score += 4

            # ---------------------------
            # Venue Quality (15)
            # ---------------------------

            score += PaperRankingService.venue_score(
                venue
            )

            # ---------------------------
            # Abstract Quality (5)
            # ---------------------------

            score += min(
                len(abstract) / 1500,
                1.0
            ) * 5

            paper["ranking_score"] = round(score, 2)

            ranked.append(paper)

        ranked.sort(
            key=lambda x: x["ranking_score"],
            reverse=True
        )

        return ranked[:20]