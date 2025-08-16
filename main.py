from scraper import get_products
from checker import get_product_changes, commit_changes
import logging

logger = logging.getLogger(__name__)

def main():
    with open("tracker.log") as log_file:
        lines = log_file.readlines()
        if len(lines) == 0:
            last_page == 100
        else:
            last_page = int(lines[-1])

    logging.basicConfig(filename="tracker.log",
                        level=logging.INFO,
                        format="%(asctime)s %(message)s",
                        datefmt="%Y-%m-%d %I:%M:%S",
                        filemode="w")
    logger.info("Starting tracker")

    products = get_products(last_page)
    new_last_page = str(products[-1]["page"])

    logger.info("Tracker finished")

    new_prods, removed_prods = get_product_changes(products)
    logger.info(f"Found {len(new_prods)} new products!")
    logger.info(f"{len(removed_prods)} products have been removed.")
    commit_changes(new_prods, removed_prods)
    logger.info(f"Changes commited.")


    with open("tracker.log", mode="a") as log_file:
        log_file.write(new_last_page)

if __name__ == "__main__":
    main()
