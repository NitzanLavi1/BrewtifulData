import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from llava_analysis import analyze_beer_with_llava, check_llava_model, DEFAULT_MODEL
from config import BASE_URL, NUM_PAGES, HEADERS, OUTPUT_DIR, PAGINATED_DIR, MASTER_CSV, MASTER_HEADER, BATCH_SIZE, BEER_IMAGE_DIR

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PAGINATED_DIR, exist_ok=True)

def batch_csv_path(batch_start, batch_end):
    return os.path.join(PAGINATED_DIR, f"beers_{batch_start}_{batch_end}.csv")

def batch_is_complete(batch_csv):
    if not os.path.exists(batch_csv):
        return False
    with open(batch_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        return len(rows) > 1

def init_master_csv():
    if not os.path.exists(MASTER_CSV):
        with open(MASTER_CSV, mode="w", newline="", encoding="utf-8") as master_csv:
            writer = csv.writer(master_csv)
            writer.writerow(MASTER_HEADER)

def parse_beer_div(beer):
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

    return {
        "name": name,
        "brewery": brewery,
        "country": country,
        "price": price,
        "rating": rating,
        "abv": abv,
        "style": style,
        "beer_url": beer_url,
        "image_url": image_url
    }

def scrape_page(page_num):
    url = BASE_URL + str(page_num)
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    beer_rows = soup.select("div.beer-row")
    return beer_rows

def download_image(image_url, image_name):
    image_path = os.path.join(BEER_IMAGE_DIR, image_name)  # Use BEER_IMAGE_DIR
    img_resp = requests.get(image_url)
    with open(image_path, "wb") as f:
        f.write(img_resp.content)
    return image_path

def analyze_image(image_path, beer_data, model_name):
    analysis = analyze_beer_with_llava(image_path, beer_data, model_name)  # Pass image_path
    os.remove(image_path)
    return analysis

def write_batch(batch_csv, batch_rows):
    with open(batch_csv, mode="w", newline="", encoding="utf-8") as batch_file:
        writer = csv.writer(batch_file)
        writer.writerow(MASTER_HEADER)
        writer.writerows(batch_rows)

def append_master(batch_rows):
    with open(MASTER_CSV, mode="a", newline="", encoding="utf-8") as master_csv:
        writer = csv.writer(master_csv)
        writer.writerows(batch_rows)

def run(start_page=1):
    ensure_dirs()
    has_llava, model_name = check_llava_model()
    if not has_llava:
        print("❌ No LLaVA model found. Please pull a LLaVA model first.")
        return

    init_master_csv()
    page_num = start_page
    while page_num <= NUM_PAGES:
        batch_start = page_num
        batch_end = min(page_num + BATCH_SIZE - 1, NUM_PAGES)
        batch_csv = batch_csv_path(batch_start, batch_end)

        if batch_is_complete(batch_csv):
            page_num = batch_end + 1
            continue

        batch_rows = []
        for p in range(batch_start, batch_end + 1):
            try:
                beer_rows = scrape_page(p)
                if not beer_rows:
                    break

                for beer in beer_rows:
                    parsed = parse_beer_div(beer)
                    if not parsed:
                        print("Beer NOT appended (missing or invalid data).")
                        continue

                    image_file = "N/A"
                    label_color = "N/A"
                    text_color = "N/A"
                    analysis_error = ""

                    if parsed["image_url"]:
                        image_name = os.path.basename(parsed["image_url"].split("/")[-1])
                        try:
                            image_path = download_image(parsed["image_url"], image_name)
                            beer_data = {
                                'image_file': image_name,
                                'beer_name': parsed["name"],
                                'brewery': parsed["brewery"],
                                'style': parsed["style"],
                                'abv': parsed["abv"],
                                'price': parsed["price"],
                                'rating': parsed["rating"],
                                'country': parsed["country"]
                            }
                            analysis = analyze_image(image_path, beer_data, model_name)
                            label_color = analysis.get("label_color", "N/A")
                            text_color = analysis.get("text_color", "N/A")
                            analysis_error = analysis.get("error", "")
                            image_file = image_name
                        except Exception as e:
                            analysis_error = str(e)
                            image_file = "N/A"

                    link_formula = f'=HYPERLINK("{parsed["beer_url"]}", "Beer Page")' if parsed["beer_url"] != "N/A" else "N/A"
                    row = [
                        parsed["name"], parsed["brewery"], parsed["price"], parsed["rating"], parsed["abv"], parsed["style"],
                        image_file, link_formula, parsed["country"], label_color, text_color, analysis_error
                    ]
                    # Show the final dictionary before appending
                    beer_dict = {
                        "name": parsed["name"],
                        "brewery": parsed["brewery"],
                        "price": parsed["price"],
                        "rating": parsed["rating"],
                        "abv": parsed["abv"],
                        "style": parsed["style"],
                        "image_file": image_file,
                        "beer_url": parsed["beer_url"],
                        "country": parsed["country"],
                        "label_color": label_color,
                        "text_color": text_color,
                        "analysis_error": analysis_error
                    }
                    print(f"Final beer dict before append: {beer_dict}")
                    batch_rows.append(row)
                    print(f"Beer appended: {parsed['name']}")
            except Exception as e:
                continue

            time.sleep(1)

        write_batch(batch_csv, batch_rows)
        append_master(batch_rows)
        print(f"Appended {len(batch_rows)} rows to master CSV.")
        page_num = batch_end + 1

    print(f"\n✅ Scraping and analysis complete. Data saved to batch CSVs in '{PAGINATED_DIR}' and master at '{MASTER_CSV}'")