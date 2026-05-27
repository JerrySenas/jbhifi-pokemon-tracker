from pathlib import Path
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import requests
from notifier import send_discord_message

BASE_DIR = Path(__file__).parent
LOG_PATH = BASE_DIR / "backend_tracker.log"
JSON_PATH = BASE_DIR / "backend_products.json"

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
            "&hitsPerPage=1000"
            "&responseFields=[\"hits\"]"
            "&filters=vendor:\"POKEMON TCG\""
            "&attributesToRetrieve=[\"title\", \"handle\", \"product_image\", \"availability\"]"
            "&attributesToHighlight=[]"
            "&attributesToSnippet=[]"
        ),
    }]
}

def get_num_products():
    request = {
        "requests": [{
            "indexName": "shopify_products",
            "params": (
                "query="
                "&hitsPerPage=0"
                "&responseFields=[\"nbHits\"]"
                "&filters=vendor:\"POKEMON TCG\""
            ),
        }]
    }
    response = requests.post(ALGOLIA_URL, headers=ALGOLIA_HEADERS, json=request)

    return response.json()["results"][0]["nbHits"]


def get_all_products():
    all_products = []
    page = 0

    while True:
        params = (
            "query="
            "&hitsPerPage=1000"
            f"&page={page}"
            "&responseFields=[\"hits\", \"nbPages\"]"
            "&filters=vendor:\"POKEMON TCG\""
            "&attributesToRetrieve=[\"title\", \"handle\", \"product_image\"]"
            "&attributesToHighlight=[]"
            "&attributesToSnippet=[]"
        )

        request = {
            "requests": [{
                "indexName": "shopify_products",
                "params": params
            }]
        }

        response = requests.post(ALGOLIA_URL, headers=ALGOLIA_HEADERS, json=request).json()["results"][0]
        raw_products = response["hits"]

        all_products.extend([
            {
                "objectID": p["objectID"],
                "name": p["title"],
                "url": JB_HIFI_URL + p.get("handle") if p.get("handle") else "No URL",
                "image": p.get("product_image") or "No Image"
            }
        for p in raw_products
        ])

        if page >= response["nbPages"] - 1:
            break

        page+= 1

    return all_products


def check_products(num, scraped_products):
    existing_products = []
    if JSON_PATH.exists():
        try:
            existing_products = json.loads(JSON_PATH.read_text())["products"]
        except json.JSONDecodeError:
            existing_products = []

    existing_map = {p["objectID"]: p for p in existing_products}
    scraped_map = {p["objectID"]: p for p in scraped_products}

    existing_ids = set(existing_map)
    scraped_ids = set(scraped_map)

    new_ids = scraped_ids - existing_ids
    new_products = [scraped_map[i] for i in new_ids]

    updated_products = [scraped_map[i] for i in scraped_ids]

    new_json = {
        "nbHits": num,
        "products": updated_products
    }

    JSON_PATH.write_text(json.dumps(new_json, indent=4))

    return new_products

def prepare_discord_embeds(new):
    embeds = []

    embeds.extend(
        [
            {
                "title": product["name"],
                "description": f"URL: {product['url']}\n",
                "image": {"url": product['image']},
                "color": 3447003
            }
            for product in new
        ]
    )

    return embeds

def main():
    if JSON_PATH.exists():
        try:
            curr_num_products = json.loads(JSON_PATH.read_text())["nbHits"]
        except json.JSONDecodeError:
            curr_num_products = 0
        except KeyError:
            curr_num_products = 0
    else:
        curr_num_products = 0
    
    new_num_products = get_num_products()
    if new_num_products == curr_num_products:
        return

    products = get_all_products()
    new_prods = check_products(new_num_products, products)

    if new_prods:
        logger.info("Changes detected. Sending to Discord...")
        logger.info("New products: %d", len(new_prods))

        embeds = prepare_discord_embeds(new_prods)
        r = send_discord_message(
            embeds,
            f"<@&1407662797893926953> **{len(new_prods)}** products have been added to the backend."
        )

        if r.status_code < 300:
            logger.info("Discord message sent successfully.")
        else:
            logger.error("Discord message failed.")
            logger.error(r.text)

if __name__ == "__main__":
    main()
