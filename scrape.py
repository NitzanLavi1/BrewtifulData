import os
import requests
from bs4 import BeautifulSoup
import csv
import time

# --- Configuration ---
BASE_URL = "https://beerizer.com/?page="
NUM_PAGES = 5  # Change this to scrape more
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_DIR = "beer_images"
CSV_PATH = "beers.csv"

# --- Prepare folders ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Open CSV for writing ---
with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Name", "Brewery", "Price", "Rating", "ABV", "Style", "Image_File", "URL", "Country"])

    for page_num in range(1, NUM_PAGES + 1):
        print(f"Scraping page {page_num}...")
        url = BASE_URL + str(page_num)

        try:
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, "html.parser")
            beer_rows = soup.select("div.beer-row")

            if not beer_rows:
                print("No more beers found — stopping.")
                break

            for beer in beer_rows:
                name_tag = beer.select_one('[itemprop="name"]')
                name = name_tag.get_text(strip=True) if name_tag else "N/A"

                brewery_tag = beer.select_one("span.brewery-title")
                brewery = brewery_tag.get_text(strip=True) if brewery_tag else "N/A"
                
                # Extract country from flag image
                flag_tag = beer.select_one("span.brewery-title img.flag")
                country = "Unknown"
                if flag_tag:
                    country = flag_tag.get("title", flag_tag.get("alt", "Unknown"))

                price_tag = beer.select_one('meta[itemprop="price"]')
                price = price_tag["content"] if price_tag else "N/A"

                rating_tag = beer.select_one('meta[itemprop="ratingValue"]')
                rating = rating_tag["content"] if rating_tag else "N/A"
                if rating == "N/A":
                    continue  # Skip this beer if no rating

                abv_tag = beer.select_one("span.abv.value")
                abv = abv_tag.get_text(strip=True) if abv_tag else "N/A"

                style_tag = beer.select_one("div.right-item-row.style > div")
                style = style_tag.get_text(strip=True) if style_tag else "N/A"

                beer_url_tag = beer.select_one("a.beer-title[itemprop='url']")
                beer_url = beer_url_tag["href"] if beer_url_tag else "N/A"

                image_tag = beer.select_one('[itemprop="image"]')
                image_url = image_tag["src"] if image_tag else None

                image_file = "N/A"
                if image_url:
                    image_name = os.path.basename(image_url.split("/")[-1])
                    image_path = os.path.join(OUTPUT_DIR, image_name)

                    # Only download if image doesn't already exist
                    if not os.path.exists(image_path):
                        try:
                            img_resp = requests.get(image_url)
                            with open(image_path, "wb") as f:
                                f.write(img_resp.content)
                            print(f"Downloaded image: {image_name}")
                        except Exception as e:
                            print(f"Failed to download image for {name}: {e}")
                    image_file = image_name

                link_formula = f'=HYPERLINK("{beer_url}", "Beer Page")' if beer_url != "N/A" else "N/A"
                writer.writerow([name, brewery, price, rating, abv, style, image_file, link_formula, country])

            time.sleep(1)  # Be respectful: wait 1s between pages

        except Exception as e:
            print(f"Error scraping page {page_num}: {e}")
            continue

print(f"\n✅ Scraping complete. Data saved to '{CSV_PATH}', images in '{OUTPUT_DIR}/'")
