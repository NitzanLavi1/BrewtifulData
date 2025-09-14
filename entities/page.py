import requests
from bs4 import BeautifulSoup
from core.config import BASE_URL, HEADERS
from entities.beer import Beer
from typing import List, Optional

class Page:
    def __init__(self, page_num: int) -> None:
        self.page_num: int = page_num
        self.url: str = BASE_URL + str(page_num)
        self.soup: Optional[BeautifulSoup] = None

    def fetch(self) -> None:
        response = requests.get(self.url, headers=HEADERS)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.text, "html.parser")

    def get_beers(self) -> List[Beer]:
        if self.soup is None:
            self.fetch()
        beer_rows = self.soup.select("div.beer-row")
        return [Beer.from_html(beer) for beer in beer_rows]