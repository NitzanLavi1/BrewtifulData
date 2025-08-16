import requests
from bs4 import BeautifulSoup

url = "https://beerizer.com/shop"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")

# Example: each beer listing is a div—adjust based on inspection
try:
    for beer in soup.select("id="beer-41264""):
        try:
            name = beer.select_one("class = "title"").get_text(strip=True)
        except:
            print("Name not found, using fallback selector.")
        try:
            brewery = beer.select_one(".brewery-name, .brewery").get_text(strip=True)
        except:
            print("Brewery not found, using fallback selector.")
        price = beer.select_one(".from-price, .price").get_text(strip=True)
        rating = beer.select_one(".rating, .untappd-rating").get_text(strip=True)
        image_url = beer.select_one("img")["src"]
        print(name, price, rating, image_url)
except Exception as e:
    print(f"An error occurred: {e}")
    print("Please check the selectors and ensure they match the current HTML structure.")

    