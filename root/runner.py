import logging
from entities.csv_ent import CsvManager
from core.config import MASTER_HEADER, MASTER_CSV
from core.scrape_and_analyze import run, ensure_dirs

def main():
    # Set up logger
    logger = logging.getLogger("beer_project")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # Initialize CSV manager
    csv_manager = CsvManager(MASTER_HEADER)

    # Project setup
    ensure_dirs()
    csv_manager.init_master_csv(MASTER_CSV)

    # Call run, passing dependencies
    run(logger=logger, csv_manager=csv_manager)

if __name__ == "__main__":
    main()