import os
from config import OUTPUT_DIR, PAGINATED_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PAGINATED_DIR, exist_ok=True)

MASTER_CSV = os.path.join(OUTPUT_DIR, "master.csv")

BASE_URL = "https://beerizer.com/?page="
NUM_PAGES = 1676
HEADERS = {"User-Agent": "Mozilla/5.0"}
BATCH_SIZE = 15
MASTER_HEADER = [
    "Name", "Brewery", "Price", "Rating", "ABV", "Style", "Image_File", "URL", "Country",
    "Label_Color", "Text_Color", "Analysis_Error"
]

batch_csv = os.path.join(PAGINATED_DIR, f"beers_{batch_start}_{batch_end}.csv")