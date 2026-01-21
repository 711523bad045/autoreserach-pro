from collections import deque
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.crawler.fetcher import Fetcher
from app.crawler.parser import Parser
from app.crawler.cleaner import Cleaner
from app.nlp.chunker import TextChunker
from app.database import models


class CrawlerEngine:

    MAX_PAGES_PER_SOURCE = 20  # safety limit

    @staticmethod
    def crawl_project(db: Session, project_id: int):
        print("CRAWLER STARTED FOR PROJECT:", project_id)

        sources = db.query(models.Source).filter(models.Source.project_id == project_id).all()
        print("SOURCES FOUND:", sources)

        for source in sources:
            base_domain = source.domain
            if not base_domain.startswith("http"):
                base_domain = "https://" + base_domain

            base_netloc = urlparse(base_domain).netloc

            print("CRAWLING SOURCE:", base_domain)

            queue = deque([base_domain])
            visited = set()

            pages_crawled = 0

            while queue and pages_crawled < CrawlerEngine.MAX_PAGES_PER_SOURCE:
                url = queue.popleft()

                if url in visited:
                    continue

                visited.add(url)

                print("FETCHING:", url)

                try:
                    html = Fetcher.fetch(url)
                    raw_text, links = Parser.extract_text_and_links(html, url)
                    clean_text = Cleaner.clean(raw_text)

                    # Save page
                    page = models.Page(
                        source_id=source.id,
                        url=url,
                        status=models.PageStatus.crawled,
                        raw_html=html,
                        cleaned_text=clean_text,
                    )
                    db.add(page)
                    db.commit()
                    db.refresh(page)  # 🔥 IMPORTANT: get page.id

                    # 🔥 Chunk the page text
                    chunks = TextChunker.chunk_text(clean_text, max_chars=1000)

                    for idx, chunk_text in enumerate(chunks):
                        chunk = models.Chunk(
                            page_id=page.id,
                            chunk_index=idx,
                            content=chunk_text,
                        )
                        db.add(chunk)

                    db.commit()

                    pages_crawled += 1
                    print("SAVED PAGE + CHUNKS:", url, "chunks:", len(chunks))

                    # Enqueue internal links only
                    for link in links:
                        if urlparse(link).netloc == base_netloc:
                            if link not in visited:
                                queue.append(link)

                except Exception as e:
                    print("FAILED:", url, e)

        print("CRAWLING FINISHED")
