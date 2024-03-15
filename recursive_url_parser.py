import logging
from typing import Any, Dict, Iterator
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseBlobParser
from langchain.document_loaders.blob_loaders import Blob
from cat.mad_hatter.decorators import hook
import httpx
from httpx import HTTPError, Timeout

logger = logging.getLogger(__name__)

max_depth = 1
timeout = 10
filter_key_words = ""

def update_variables(settings):
    global max_depth, timeout, filter_key_words
    max_depth = settings["max_depth"]
    timeout = settings["timeout"]
    filter_key_words = settings["filter_key_words"]

class RecursiveURLParser(BaseBlobParser):
    """Parse HTML content recursively from a given URL."""

    def __init__(
        self,
        *,
        max_depth: int = 1,
        features: str = "lxml",
        get_text_separator: str = "",
        filter_keywords: list[str] = None,
        timeout: int = 10,
        **kwargs: Any,
    ) -> None:
        """Initialize the parser."""
        try:
            import bs4  # noqa:F401
        except ImportError:
            raise ImportError(
                "beautifulsoup4 package not found, please install it with "
                "`pip install beautifulsoup4`"
            )

        self.max_depth = max_depth
        self.bs_kwargs = {"features": features, **kwargs}
        self.get_text_separator = get_text_separator
        self.filter_keywords = filter_keywords or []
        self.timeout = timeout
        self.visited_urls = set()

    def _fetch_url_content(self, url: str) -> str:
        headers = {"User-Agent": "Magic Browser"}
        
        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                return response.text
            except (HTTPError, Timeout) as e:
                logger.error(f"Error fetching URL {url}: {e}")
                return ""

    def _extract_links(self, html_content: str, base_url: str) -> Iterator[str]:
        """Extract links from HTML content."""
        soup = BeautifulSoup(html_content, **self.bs_kwargs)
        for link in soup.find_all("a", href=True):
            href = link["href"]
            absolute_url = urljoin(base_url, href)
            if self._is_valid_url(absolute_url):
                logger.error(f"Found link: {absolute_url}")
                yield absolute_url

    def _is_valid_url(self, url: str) -> bool:
        """Check if the URL is valid."""
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme and parsed_url.netloc)

    def _crawl_recursive(self, url: str, depth: int) -> Iterator[Document]:
        if depth > self.max_depth:
            return
        
        try:
            html_content = self._fetch_url_content(url)
            if not html_content:
                return
            
            if self._is_informative_content(html_content):
                links = self._extract_links(html_content, url)
                text = BeautifulSoup(html_content, **self.bs_kwargs).get_text(
                    self.get_text_separator
                )

                yield Document(page_content=text, metadata={"source": url})

                for link in links:
                    if link not in self.visited_urls:
                        self.visited_urls.add(link)
                        for document in self._crawl_recursive(link, depth + 1):
                            yield document
                    else:
                        logger.error(f"Ignored already visited URL {link}")  
            else:
                logger.info(f"Ignored non-informative content from URL {url}")
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")

    def _is_informative_content(self, html_content: str) -> bool:
        """Check if the HTML content is informative based on predefined rules."""
        soup = BeautifulSoup(html_content, **self.bs_kwargs)
        text = soup.get_text(separator=self.get_text_separator)
        for keyword in self.filter_keywords:
            if keyword in text:
                return True
        return False

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        """Parse HTML content recursively."""
        base_url = blob.source
        for document in self._crawl_recursive(base_url, depth=0):
            yield document

@hook(priority=10)
def rabbithole_instantiates_parsers(file_handlers: dict, cat) -> dict:
    """Hook the available parsers for ingesting files in the declarative memory."""
    settings = cat.mad_hatter.get_plugin().load_settings()
    update_variables(settings)
    file_handlers["text/html"] = RecursiveURLParser(filter_keywords=filter_key_words.split(','), max_depth=max_depth, timeout=timeout)
    return file_handlers