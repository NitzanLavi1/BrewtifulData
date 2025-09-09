import logging
from entities.csv_ent import CsvManager
from core.config import MASTER_HEADER
from core.scrape_and_analyze import run, ensure_dirs, init_master_csv

def main():
    # Set up logger
    logger = logging.getLogger("beer_project")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # Initialize CSV manager
    csv_manager = CsvManager(MASTER_HEADER)

    # Project setup
    ensure_dirs()
    init_master_csv(csv_manager)

    # Call run, passing dependencies
    run(logger=logger, csv_manager=csv_manager)

if __name__ == "__main__":
    main()