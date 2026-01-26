
from app.services.web_search_service import WebSearchService

def test_search():
    queries = ["Brihadisvara Temple", "Thanjavur Temple", "Rajarajesvaram"]
    for q in queries:
        print(f"Testing search for: {q}")
        results = WebSearchService.search(q)
        print(f"Results for {q}: {len(results)}")

if __name__ == "__main__":
    test_search()
