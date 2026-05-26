from pathlib import Path
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import requests
from notifier import send_discord_message

BASE_DIR = Path(__file__).parent
LOG_PATH = BASE_DIR / "tracker.log"
JSON_PATH = BASE_DIR / "products.json"

handler = TimedRotatingFileHandler(
    LOG_PATH,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S",
    handlers=[handler]
)

logger = logging.getLogger(__name__)

ALGOLIA_URL = "https://vtvkm5urpx-dsn.algolia.net/1/indexes/*/queries"
JB_HIFI_URL = "https://www.jbhifi.com.au/products/"

ALGOLIA_HEADERS = {
    "x-algolia-api-key": "1d989f0839a992bbece9099e1b091f07",
    "x-algolia-application-id": "VTVKM5URPX",
    "content-type": "application/json"
}

ALGOLIA_REQUEST = {
    "requests": [{
        "indexName": "shopify_products",
        "params": (
            "query="
            "&hitsPerPage=50"
            "&responseFields=[\"hits\"]"
            "&filters=vendor:\"POKEMON TCG\""
            "&attributesToRetrieve=[\"title\", \"handle\", \"product_image\"]"
            "&attributesToHighlight=[]"
            "&attributesToSnippet=[]"
        ),
    }]
}

def get_products():
    response = requests.post(ALGOLIA_URL, headers=ALGOLIA_HEADERS, json=ALGOLIA_REQUEST)
    raw_products = response.json()["results"][0]["hits"]
    return [
        {
            "objectID": p["objectID"],
            "name": p["title"],
            "url": JB_HIFI_URL + p["handle"],
            "image": p["product_image"]
        }
    for p in raw_products]


def check_products(scraped_products):
    existing_products = []
    if JSON_PATH.exists():
        try:
            existing_products = json.loads(JSON_PATH.read_text())
        except json.JSONDecodeError:
            existing_products = []

    existing_map = {p["objectID"]: p for p in existing_products}
    scraped_map = {p["objectID"]: p for p in scraped_products}

    existing_ids = set(existing_map)
    scraped_ids = set(scraped_map)

    new_ids = scraped_ids - existing_ids
    removed_ids = existing_ids - scraped_ids

    new_products = [scraped_map[i] for i in new_ids]
    removed_products = [existing_map[i] for i in removed_ids]

    updated_products = [scraped_map[i] for i in scraped_ids]

    JSON_PATH.write_text(json.dumps(updated_products, indent=4))

    return new_products, removed_products

def main():
    products = get_products()
    new_prods, removed_prods = check_products(products)

    if new_prods or removed_prods:
        logger.info("Changes detected. Sending to Discord...")
        logger.info("New products: %d, Removed products: %d", len(new_prods), len(removed_prods))

        r = send_discord_message(new_prods, removed_prods)
        if r.status_code < 300:
            logger.info("Discord message sent successfully.")
        else:
            logger.error("Discord message failed.")
            logger.error(r.text)

if __name__ == "__main__":
    main()
