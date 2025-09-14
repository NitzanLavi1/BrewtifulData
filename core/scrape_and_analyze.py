import logging
from entities.beer import Beer
from entities.csv_ent import CsvManager
import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from core.llava_analysis import analyze_beer_with_llava, check_llava_model, DEFAULT_MODEL
from core.config import BASE_URL, NUM_PAGES, HEADERS, OUTPUT_DIR, PAGINATED_DIR, MASTER_CSV, MASTER_HEADER, BATCH_SIZE, BEER_IMAGE_DIR, START_PAGE
from entities.image_manager import ImageManager
from entities.page import Page

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

csv_manager = CsvManager(MASTER_HEADER)

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PAGINATED_DIR, exist_ok=True)

def batch_csv_path(csv_manager, batch_start, batch_end):
    return csv_manager.batch_csv_path(PAGINATED_DIR, batch_start, batch_end)

def batch_is_complete(csv_manager, batch_csv):
    return csv_manager.is_complete(batch_csv)

def init_master_csv(csv_manager):
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

def write_batch(csv_manager, batch_csv, batch_rows):
    csv_manager.write_batch(batch_csv, batch_rows)

def append_master(csv_manager, batch_rows):
    csv_manager.append_master(MASTER_CSV, batch_rows)

def run(logger, csv_manager):
    has_llava, model_name = check_llava_model()
    if not has_llava:
        logger.error("No LLaVA model found. Please pull a LLaVA model first.")
        return

    page_num = START_PAGE
    while page_num <= NUM_PAGES:
        batch_start = page_num
        batch_end = min(page_num + BATCH_SIZE - 1, NUM_PAGES)
        batch_csv = csv_manager.batch_csv_path(PAGINATED_DIR, batch_start, batch_end)

        if csv_manager.is_complete(batch_csv):
            page_num = batch_end + 1
            continue

        batch_rows = []
        for p in range(batch_start, batch_end + 1):
            logger.info(f"--- Scraping page {p} ---")
            try:
                page = Page(p)
                beer_objs = page.get_beers()
                if not beer_objs:
                    break

                for beer_obj in beer_objs:
                    if not beer_obj or not beer_obj.has_valid_rating():
                        logger.warning("Beer NOT appended (missing or invalid data).")
                        continue

                    start_time = time.time()
                    img_manager = ImageManager(beer_obj.image_url, BEER_IMAGE_DIR)
                    if beer_obj.has_image():
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
                            beer_obj.set_analysis(
                                img_manager.image_filename(),
                                analysis.get("label_color", "N/A"),
                                analysis.get("text_color", "N/A"),
                                analysis.get("error", "")
                            )
                        except Exception as e:
                            beer_obj.set_analysis("N/A", "N/A", "N/A", str(e))
                        finally:
                            ImageManager.remove_image(image_path)
                    end_time = time.time()
                    elapsed = end_time - start_time

                    batch_rows.append(beer_obj.to_csv_row())
                    logger.info(f"Beer appended: {beer_obj.name} (time: {elapsed:.2f} sec)")
            except Exception as e:
                logger.error(f"Error scraping page {p}: {e}")
                continue

            time.sleep(1)

        csv_manager.write_batch(batch_csv, batch_rows)
        csv_manager.append_master(MASTER_CSV, batch_rows)
        logger.info(f"Appended {len(batch_rows)} rows to master CSV.")
        page_num = batch_end + 1

    logger.info(f"Scraping and analysis complete. Data saved to batch CSVs in '{PAGINATED_DIR}' and master at '{MASTER_CSV}'")