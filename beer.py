from dataclasses import dataclass

@dataclass
class Beer:
    name: str
    brewery: str
    country: str
    price: str
    rating: str
    abv: str
    style: str
    beer_url: str
    image_url: str

    def has_valid_rating(self) -> bool:
        return self.rating not in (None, "N/A", "")

    def has_image(self) -> bool:
        return bool(self.image_url)

    def image_filename(self) -> str:
        if self.image_url:
            return self.image_url.split("/")[-1]
        return "N/A"