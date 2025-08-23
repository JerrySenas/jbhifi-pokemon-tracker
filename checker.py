import json
from pathlib import Path
from scraper import get_products

JSON_PATH = Path(__file__).parent / "products.json"

def get_product_changes(scraped_products):
    with JSON_PATH.open("r") as products_json:
        existing_products = json.load(products_json)
        existing_ids = set([item["id"] for item in existing_products])

    scraped_ids = set([item["id"] for item in scraped_products])

    new_ids = scraped_ids.difference(existing_ids)
    removed_ids = existing_ids.difference(scraped_ids)
    new_products = [product for product in scraped_products if product["id"] in new_ids]
    # removed_products = [product for product in existing_products if product["id"] in removed_ids]

    return new_products, removed_ids

def commit_changes(new_products, removed_ids):
    with JSON_PATH.open("r") as products_json:
        existing_products = json.load(products_json)
        modified_products = [product for product in existing_products if product["id"] not in removed_ids]
        removed_products = [product for product in existing_products if product["id"] in removed_ids]
        modified_products.extend(new_products)
    
    with JSON_PATH.open("w") as products_json:
        json.dump(modified_products, products_json, indent=4)

    return removed_products
        


if __name__ == "__main__":
    products = get_product_changes(get_products())
    commit_changes(products[0], products[1])
