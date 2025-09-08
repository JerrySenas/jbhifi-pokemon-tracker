import json
from pathlib import Path
from scraper import get_products

JSON_PATH = Path(__file__).parent / "products.json"

def get_product_changes(scraped_products):
    with JSON_PATH.open("r") as products_json:
        existing_products = json.load(products_json)

    new_products = [product for product in scraped_products if product not in existing_products]
    removed_products = [product for product in existing_products if product not in scraped_products]
    
    if len(new_products) > 0 or len(removed_products) > 0:
        modified_products = [product for product in existing_products if product not in removed_products]
        modified_products.extend(new_products)
        with JSON_PATH.open("w") as products_json:
            json.dump(modified_products, products_json, indent=4)
    return new_products, removed_products


if __name__ == "__main__":
    products = get_product_changes(get_products())
