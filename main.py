from scraper import get_products
from checker import get_product_changes, commit_changes
from notifier import send_discord_message
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
LOG_PATH = Path(__file__).parent / "tracker.log"
JSON_PATH = Path(__file__).parent / "products.json"

def main():
    if LOG_PATH.exists():
        with open(LOG_PATH) as log_file:
            lines = log_file.readlines()
            try:
                last_page = int(lines[-1])
            except ValueError:
                last_page = 100
    else:
        with open(LOG_PATH, "w") as log_file:
            log_file.write("Log file init")
            last_page = 100

    if not JSON_PATH.exists():
        with open(JSON_PATH, "w") as json_file:
            json_file.write("[]")

    logging.basicConfig(filename=LOG_PATH,
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
    logger.info(f"{len(removed_prods)} products have been marked for removal.")
    if len(new_prods) > 0 or len(removed_prods) > 0:
        commit_changes(new_prods, removed_prods)
        logger.info(f"Changes commited.")
        r = send_discord_message(new_prods, removed_prods)
        if r.status_code < 299:
            logger.info(f"Discord message sent successfully.")
        else:
            logger.info(f"Discord message failed to send.")
            logger.info(r.text)


    with open(LOG_PATH, mode="a") as log_file:
        log_file.write(new_last_page)

if __name__ == "__main__":
    main()
