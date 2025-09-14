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
    image_file: str = "N/A"
    label_color: str = "N/A"
    text_color: str = "N/A"
    analysis_error: str = ""

    @classmethod
    def from_html(cls, beer) -> "Beer | None":
        name_tag = beer.select_one('[itemprop="name"]')
        name = name_tag.get_text(strip=True) if name_tag else "N/A"

        brewery_tag = beer.select_one("span.brewery-title")
        brewery = brewery_tag.get_text(strip=True) if brewery_tag else "N/A"
        
        flag_tag = beer.select_one("span.brewery-title img.flag")
        country = "Unknown"
        if flag_tag:
            country = flag_tag.get("title", flag_tag.get("alt", "Unknown"))

        price_tag = beer.select_one('meta[itemprop="price"]')
        price = price_tag["content"] if price_tag else "N/A"
        
        rating_tag = beer.find('meta', attrs={'itemprop': 'ratingValue'})
        rating = rating_tag["content"] if rating_tag and rating_tag.has_attr("content") else None
        if not rating or rating == "N/A":
            return None  # Skip this beer if no rating

        abv_tag = beer.select_one("span.abv.value")
        abv = abv_tag.get_text(strip=True) if abv_tag else "N/A"

        style_tag = beer.select_one("div.right-item-row.style > div")
        style = style_tag.get_text(strip=True) if style_tag else "N/A"

        beer_url_tag = beer.select_one("a.beer-title[itemprop='url']")
        beer_url = beer_url_tag["href"] if beer_url_tag else "N/A"

        image_tag = beer.select_one('[itemprop="image"]')
        image_url = image_tag["src"] if image_tag else None

        return cls(
            name=name,
            brewery=brewery,
            country=country,
            price=price,
            rating=rating,
            abv=abv,
            style=style,
            beer_url=beer_url,
            image_url=image_url
        )

    def has_valid_rating(self) -> bool:
        return self.rating not in (None, "N/A", "")

    def has_image(self) -> bool:
        return bool(self.image_url)

    def image_filename(self) -> str:
        if self.image_url:
            return self.image_url.split("/")[-1]
        return "N/A"

    def set_analysis(self, image_file: str, label_color: str, text_color: str, analysis_error: str) -> None:
        self.image_file = image_file
        self.label_color = label_color
        self.text_color = text_color
        self.analysis_error = analysis_error

    def to_csv_row(self) -> list[str]:
        link_formula = f'=HYPERLINK("{self.beer_url}", "Beer Page")' if self.beer_url != "N/A" else "N/A"
        return [
            self.name, self.brewery, self.price, self.rating, self.abv, self.style,
            self.image_file, link_formula, self.country, self.label_color, self.text_color, self.analysis_error
        ]