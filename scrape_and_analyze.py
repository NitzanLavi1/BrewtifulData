import os
import requests
from bs4 import BeautifulSoup
import csv
import time
from llava_analysis import analyze_beer_with_llava, check_llava_model, DEFAULT_MODEL
from config import BASE_URL, NUM_PAGES, HEADERS, OUTPUT_DIR, BATCH_SIZE, MASTER_CSV, MASTER_HEADER

def batch_is_complete(batch_csv):
    if not os.path.exists(batch_csv):
        return False
    with open(batch_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        return len(rows) > 1

def run_scraping_and_analysis():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    has_llava, model_name = check_llava_model()
    if not has_llava:
        print("❌ No LLaVA model found. Please pull a LLaVA model first.")
        return

    if not os.path.exists(MASTER_CSV):
        with open(MASTER_CSV, mode="w", newline="", encoding="utf-8") as master_csv:
            writer = csv.writer(master_csv)
            writer.writerow(MASTER_HEADER)

    page_num = 1
    while page_num <= NUM_PAGES:
        batch_start = page_num
        batch_end = min(page_num + BATCH_SIZE - 1, NUM_PAGES)
        batch_csv = f"beers_{batch_start}_{batch_end}.csv"

        if batch_is_complete(batch_csv):
            print(f"⏩ Batch {batch_start}-{batch_end} already exists and is complete, skipping.")
            page_num = batch_end + 1
            continue

        batch_rows = []
        for p in range(batch_start, batch_end + 1):
            print(f"Scraping page {p}...")
            url = BASE_URL + str(p)
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
                    
                    flag_tag = beer.select_one("span.brewery-title img.flag")
                    country = "Unknown"
                    if flag_tag:
                        country = flag_tag.get("title", flag_tag.get("alt", "Unknown"))

                    price_tag = beer.select_one('meta[itemprop="price"]')
                    price = price_tag["content"] if price_tag else "N/A"

                    rating_tag = beer.select_one('meta[itemprop="ratingValue"]')
                    rating = rating_tag["content"] if rating_tag else None
                    if not rating or rating == "N/A":
                        continue

                    abv_tag = beer.select_one("span.abv.value")
                    abv = abv_tag.get_text(strip=True) if abv_tag else "N/A"

                    style_tag = beer.select_one("div.right-item-row.style > div")
                    style = style_tag.get_text(strip=True) if style_tag else "N/A"

                    beer_url_tag = beer.select_one("a.beer-title[itemprop='url']")
                    beer_url = beer_url_tag["href"] if beer_url_tag else "N/A"

                    image_tag = beer.select_one('[itemprop="image"]')
                    image_url = image_tag["src"] if image_tag else None

                    image_file = "N/A"
                    label_color = "N/A"
                    text_color = "N/A"
                    analysis_error = ""

                    if image_url:
                        image_name = os.path.basename(image_url.split("/")[-1])
                        image_path = os.path.join(OUTPUT_DIR, image_name)

                        try:
                            start_time = time.time()
                            img_resp = requests.get(image_url)
                            with open(image_path, "wb") as f:
                                f.write(img_resp.content)
                            print(f"Downloaded image: {image_name}")

                            beer_data = {
                                'image_file': image_name,
                                'beer_name': name,
                                'brewery': brewery,
                                'style': style,
                                'abv': abv,
                                'price': price,
                                'rating': rating,
                                'country': country
                            }
                            analysis = analyze_beer_with_llava(beer_data, model_name)
                            label_color = analysis.get("label_color", "N/A")
                            text_color = analysis.get("text_color", "N/A")
                            analysis_error = analysis.get("error", "")

                            os.remove(image_path)
                            print(f"Deleted image: {image_name}")

                            end_time = time.time()
                            elapsed = end_time - start_time
                            print(f"⏱️  Time for {name}: {elapsed:.2f} seconds")

                            image_file = image_name

                        except Exception as e:
                            print(f"Failed to download or analyze image for {name}: {e}")
                            analysis_error = str(e)
                            image_file = "N/A"

                    link_formula = f'=HYPERLINK("{beer_url}", "Beer Page")' if beer_url != "N/A" else "N/A"
                    row = [
                        name, brewery, price, rating, abv, style, image_file, link_formula, country,
                        label_color, text_color, analysis_error
                    ]
                    batch_rows.append(row)

            except Exception as e:
                print(f"Error scraping page {p}: {e}")
                continue

            time.sleep(1)

        print(f"💾 Saving batch {batch_start}-{batch_end} to {batch_csv} and appending to master CSV.")
        with open(batch_csv, mode="w", newline="", encoding="utf-8") as batch_file:
            writer = csv.writer(batch_file)
            writer.writerow(MASTER_HEADER)
            writer.writerows(batch_rows)

        with open(MASTER_CSV, mode="a", newline="", encoding="utf-8") as master_csv:
            writer = csv.writer(master_csv)
            writer.writerows(batch_rows)

        page_num = batch_end + 1

<<<<<<< HEAD
    batch_rows = []
    for p in range(batch_start, batch_end + 1):
        print(f"Scraping page {p}...")
        url = BASE_URL + str(p)
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
                
                flag_tag = beer.select_one("span.brewery-title img.flag")
                country = "Unknown"
                if flag_tag:
                    country = flag_tag.get("title", flag_tag.get("alt", "Unknown"))

                price_tag = beer.select_one('meta[itemprop="price"]')
                price = price_tag["content"] if price_tag else "N/A"

                rating_tag = beer.select_one('meta[itemprop="ratingValue"]')
                rating = rating_tag["content"] if rating_tag else None
                if not rating or rating == "N/A":
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
                label_color = "N/A"
                text_color = "N/A"
                analysis_error = ""

                if image_url:
                    image_name = os.path.basename(image_url.split("/")[-1])
                    image_path = os.path.join(OUTPUT_DIR, image_name)

                    try:
                        start_time = time.time()
                        img_resp = requests.get(image_url)
                        with open(image_path, "wb") as f:
                            f.write(img_resp.content)
                        print(f"Downloaded image: {image_name}")

                        beer_data = {
                            'image_file': image_name,
                            'beer_name': name,
                            'brewery': brewery,
                            'style': style,
                            'abv': abv,
                            'price': price,
                            'rating': rating,
                            'country': country
                        }
                        analysis = analyze_beer_with_llava(beer_data, model_name)
                        label_color = analysis.get("label_color", "N/A")
                        text_color = analysis.get("text_color", "N/A")
                        analysis_error = analysis.get("error", "")

                        os.remove(image_path)
                        print(f"Deleted image: {image_name}")

                        end_time = time.time()
                        elapsed = end_time - start_time
                        print(f"⏱️  Time for {name}: {elapsed:.2f} seconds")

                        image_file = image_name

                    except Exception as e:
                        print(f"Failed to download or analyze image for {name}: {e}")
                        analysis_error = str(e)
                        image_file = "N/A"

                link_formula = f'=HYPERLINK("{beer_url}", "Beer Page")' if beer_url != "N/A" else "N/A"
                row = [
                    name, brewery, price, rating, abv, style, image_file, link_formula, country,
                    label_color, text_color, analysis_error
                ]
                batch_rows.append(row)

        except Exception as e:
            print(f"Error scraping page {p}: {e}")
            continue

        time.sleep(1)  # Be respectful: wait 1s between pages

    # Save batch and append to master
    print(f"💾 Saving batch {batch_start}-{batch_end} to {batch_csv} and appending to master CSV.")
    with open(batch_csv, mode="w", newline="", encoding="utf-8") as batch_file:
        writer = csv.writer(batch_file)
        writer.writerow(master_header)
        writer.writerows(batch_rows)

    with open(MASTER_CSV, mode="a", newline="", encoding="utf-8") as master_csv:
        writer = csv.writer(master_csv)
        writer.writerows(batch_rows)

    page_num = batch_end + 1

<<<<<<< HEAD
print(f"\n✅ Scraping and analysis complete. Data saved to batch CSVs and '{MASTER_CSV}'")
=======
print(f"\n✅ Scraping and analysis complete. Data saved to batch CSVs and '{MASTER_CSV}'")
>>>>>>> 3a0065e (Update README and scripts)
=======
    print(f"\n✅ Scraping and analysis complete. Data saved to batch CSVs and '{MASTER_CSV}'")
>>>>>>> 1c63645 (Refactor outputs, update config, .gitignore, and add .gitkeep)
