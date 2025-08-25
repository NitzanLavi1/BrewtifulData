import os

OUTPUT_DIR = "outputs"
PAGINATED_DIR = os.path.join(OUTPUT_DIR, "paginated")
MASTER_CSV = os.path.join(OUTPUT_DIR, "master.csv")
BEER_IMAGE_DIR = os.path.join(OUTPUT_DIR, "beer_images")  # Directory for beer images

# LLaVA analysis output files
LLAVA_OUTPUT_CSV = os.path.join(OUTPUT_DIR, "llava_colors.csv")
LLAVA_OUTPUT_JSON = os.path.join(OUTPUT_DIR, "llava_colors.json")
LLAVA_BEERS_CSV = os.path.join(OUTPUT_DIR, "beers.csv")

BASE_URL = "https://beerizer.com/?page="
NUM_PAGES = 1676
HEADERS = {"User-Agent": "Mozilla/5.0"}
BATCH_SIZE = 100
MASTER_HEADER = [
    "Name", "Brewery", "Price", "Rating", "ABV", "Style", "Image_File", "URL", "Country",
    "Label_Color", "Text_Color", "Analysis_Error"
]

# Ensure output directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PAGINATED_DIR, exist_ok=True)
os.makedirs(BEER_IMAGE_DIR, exist_ok=True)