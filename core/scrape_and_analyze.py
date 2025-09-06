from entities.beer import Beer
from entities.csv_manager import CsvManager
import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from core.llava_analysis import analyze_beer_with_llava, check_llava_model, DEFAULT_MODEL
from core.config import BASE_URL, NUM_PAGES, HEADERS, OUTPUT_DIR, PAGINATED_DIR, MASTER_CSV, MASTER_HEADER, BATCH_SIZE, BEER_IMAGE_DIR, START_PAGE
from entities.image_manager import ImageManager

csv_manager = CsvManager(MASTER_HEADER)

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PAGINATED_DIR, exist_ok=True)

def batch_csv_path(batch_start, batch_end):
    return csv_manager.batch_csv_path(PAGINATED_DIR, batch_start, batch_end)

def batch_is_complete(batch_csv):
    return csv_manager.is_complete(batch_csv)

def init_master_csv():
    csv_manager.init_master_csv(MASTER_CSV)

def scrape_page(page_num):
    url = BASE_URL + str(page_num)
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    beer_rows = soup.select("div.beer-row")
    return beer_rows

def analyze_image(image_path, beer_data, model_name):
    analysis = analyze_beer_with_llava(image_path, beer_data, model_name)  # Pass image_path
    os.remove(image_path)
    return analysis

def write_batch(batch_csv, batch_rows):
    csv_manager.write_batch(batch_csv, batch_rows)

def append_master(batch_rows):
    csv_manager.append_master(MASTER_CSV, batch_rows)

def run():
    ensure_dirs()
    has_llava, model_name = check_llava_model()
    if not has_llava:
        print("❌ No LLaVA model found. Please pull a LLaVA model first.")
        return

    init_master_csv()
    page_num = START_PAGE
    while page_num <= NUM_PAGES:
        batch_start = page_num
        batch_end = min(page_num + BATCH_SIZE - 1, NUM_PAGES)
        batch_csv = batch_csv_path(batch_start, batch_end)

        if batch_is_complete(batch_csv):
            page_num = batch_end + 1
            continue

        batch_rows = []
        for p in range(batch_start, batch_end + 1):
            print(f"--- Scraping page {p} ---")
            try:
                beer_rows = scrape_page(p)
                if not beer_rows:
                    break

                for beer in beer_rows:
                    beer_obj = Beer.from_html(beer)
                    if not beer_obj:
                        print("Beer NOT appended (missing or invalid data).")
                        continue

                    image_file = "N/A"
                    label_color = "N/A"
                    text_color = "N/A"
                    analysis_error = ""

                    start_time = time.time()
                    img_manager = ImageManager(beer_obj.image_url, BEER_IMAGE_DIR)
                    if img_manager.has_image():
                        try:
                            image_path = img_manager.download_image()
                            beer_data = {
                                'image_file': img_manager.image_filename(),
                                'beer_name': beer_obj.name,
                                'brewery': beer_obj.brewery,
                                'style': beer_obj.style,
                                'abv': beer_obj.abv,
                                'price': beer_obj.price,
                                'rating': beer_obj.rating,
                                'country': beer_obj.country
                            }
                            analysis = analyze_image(image_path, beer_data, model_name)
                            label_color = analysis.get("label_color", "N/A")
                            text_color = analysis.get("text_color", "N/A")
                            analysis_error = analysis.get("error", "")
                            image_file = img_manager.image_filename()
                        except Exception as e:
                            analysis_error = str(e)
                            image_file = "N/A"
                        finally:
                            ImageManager.remove_image(image_path)
                    end_time = time.time()
                    elapsed = end_time - start_time

                    link_formula = f'=HYPERLINK("{beer_obj.beer_url}", "Beer Page")' if beer_obj.beer_url != "N/A" else "N/A"
                    row = [
                        beer_obj.name, beer_obj.brewery, beer_obj.price, beer_obj.rating, beer_obj.abv, beer_obj.style,
                        image_file, link_formula, beer_obj.country, label_color, text_color, analysis_error
                    ]
                    batch_rows.append(row)
                    print(f"Beer appended: {beer_obj.name} (time: {elapsed:.2f} sec)")
            except Exception as e:
                continue

            time.sleep(1)

        write_batch(batch_csv, batch_rows)
        append_master(batch_rows)
        print(f"Appended {len(batch_rows)} rows to master CSV.")
        page_num = batch_end + 1

    print(f"\n✅ Scraping and analysis complete. Data saved to batch CSVs in '{PAGINATED_DIR}' and master at '{MASTER_CSV}'")