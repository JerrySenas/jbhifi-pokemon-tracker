from scraper import get_products
from checker import get_product_changes
from notifier import send_discord_message
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import json

BASE_DIR = Path(__file__).parent
LOG_PATH = BASE_DIR / "tracker.log"
JSON_PATH = BASE_DIR / "products.json"
STATE_PATH = BASE_DIR / "state.json"

handler = TimedRotatingFileHandler(
    LOG_PATH,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S",
    handlers=[handler]
)

logger = logging.getLogger(__name__)


def load_last_page(default: int = 100) -> int:
    """Load last scraped page number from state file."""
    if STATE_PATH.exists():
        try:
            with STATE_PATH.open("r") as state_file:
                state = json.load(state_file)
                return int(state.get("last_page", default))
        except (json.JSONDecodeError, ValueError):
            logger.warning("State file corrupted, resetting last_page to default.")
    return default


def save_last_page(last_page: int):
    """Save last scraped page number to state file."""
    with STATE_PATH.open("w") as state_file:
        json.dump({"last_page": last_page}, state_file, indent=4)

def init_json_file():
    """Ensure products.json exists."""
    if not JSON_PATH.exists():
        with JSON_PATH.open("w") as json_file:
            json_file.write("[]")

def main():
    logger.info("=== Tracker started ===")

    init_json_file()
    last_page = load_last_page()

    products = get_products(last_page)
    if not products:
        logger.warning("No products found during scrape.")
        return
    
    new_last_page = products[-1]["page"]
    save_last_page(new_last_page)

    logger.info("Tracker finished")

    new_prods, removed_prods = get_product_changes(products)
    logger.info(f"Found {len(new_prods)} new products!")
    logger.info(f"{len(removed_prods)} products have been removed.")

    if len(new_prods) > 0 or len(removed_prods) > 0:
        logger.info(f"Changes commited.")
        r = send_discord_message(new_prods, removed_prods)
        if r.status_code < 299:
            logger.info(f"Discord message sent successfully.")
        else:
            logger.info(f"Discord message failed to send.")
            logger.info(r.text)

    if new_prods or removed_prods:
        logger.info("Changes detected. Sending to Discord...")
        try:
            r = send_discord_message(new_prods, removed_prods)
            if r.status_code < 300:
                logger.info("Discord message sent successfully.")
            else:
                logger.error("Discord message failed.")
                logger.error(r.text)
        except Exception as e:
            logger.exception(f"Error sending Discord message: {e}")

    logger.info("=== Tracker finished ===")

if __name__ == "__main__":
    main()
