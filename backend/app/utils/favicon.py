from urllib.parse import urlparse


def get_favicon_url(page_url: str) -> str:
    """
    Returns a best-guess favicon URL for a given page.
    """
    parsed = urlparse(page_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return f"{base}/favicon.ico"
