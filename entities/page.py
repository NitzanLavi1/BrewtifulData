import requests
from bs4 import BeautifulSoup
from core.config import BASE_URL, HEADERS
from entities.beer import Beer

class Page:
    def __init__(self, page_num):
        self.page_num = page_num
        self.url = BASE_URL + str(page_num)
        self.soup = None

    def fetch(self):
        response = requests.get(self.url, headers=HEADERS)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.text, "html.parser")

    def get_beers(self):
        if self.soup is None:
            self.fetch()
        beer_rows = self.soup.select("div.beer-row")
        return [Beer.from_html(beer) for beer in beer_rows]