import requests
from bs4 import BeautifulSoup

url = "https://beerizer.com/?page=1"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Target the specific beer by ID
beer = soup.select_one("div#beer-418178")

if beer:
    # --- Name ---
    name_tag = beer.select_one('[itemprop="name"]')
    name = name_tag.get_text(strip=True) if name_tag else "N/A"

    # --- Brewery (in span.brewery-title) ---
    brewery_tag = beer.select_one("span.brewery-title")
    brewery = brewery_tag.get_text(strip=True) if brewery_tag else "N/A"

    # --- Price (from <meta itemprop="price">) ---
    price_tag = beer.select_one('meta[itemprop="price"]')
    price = price_tag["content"] if price_tag else "N/A"

    # --- Rating (from <meta itemprop="ratingValue">) ---
    rating_tag = beer.select_one('meta[itemprop="ratingValue"]')
    rating = rating_tag["content"] if rating_tag else "N/A"

    # --- ABV (from <span class="abv value">) ---
    abv_tag = beer.select_one("span.abv.value")
    abv = abv_tag.get_text(strip=True) if abv_tag else "N/A"

    # --- Style (div.right-item-row.style > div) ---
    style_tag = beer.select_one("div.right-item-row.style > div")
    style = style_tag.get_text(strip=True) if style_tag else "N/A"

    # --- Image (from <img itemprop="image">) ---
    image_tag = beer.select_one('[itemprop="image"]')
    image_url = image_tag["src"] if image_tag else "N/A"

    print("🍺 Beer Info:")
    print(f"Name: {name}")
    print(f"Brewery: {brewery}")
    print(f"Price: €{price}")
    print(f"Rating: {rating}")
    print(f"ABV: {abv}")
    print(f"Style: {style}")
    print(f"Image URL: {image_url}")

else:
    print("Beer not found.")
