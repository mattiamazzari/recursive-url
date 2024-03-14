from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from bs4 import BeautifulSoup
from typing import List, Dict, Union

class RecursiveUrlParser:
    def __init__(self, url: Union[str, List[str]], chunk_size: int = 512, chunk_overlap: int = 128, recursive: bool = False, option: Dict[str, Union[str, int, bool]] = {}):
        self.url = url
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.recursive = recursive
        self.option = option

    def parse(self):
        loader = RecursiveUrlLoader(
            url=self.url,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            recursive=self.recursive,
            extractor=self._custom_extractor
        )
        return loader.load()

    def _custom_extractor(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text()
