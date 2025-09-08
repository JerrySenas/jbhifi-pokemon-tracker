import json
from pathlib import Path
from scraper import get_products

JSON_PATH = Path(__file__).parent / "products.json"

def get_product_changes(scraped_products):
    if JSON_PATH.exists():
        with JSON_PATH.open("r") as products_json:
            try:
                existing_products = json.load(products_json)
            except json.JSONDecodeError:
                existing_products = []

    existing_ids = [p["id"] for p in existing_products]
    scraped_ids = [p["id"] for p in scraped_products]

    new_products = [p for p in scraped_products if p["id"] not in existing_ids]
    removed_products = [p for p in existing_products if p["id"] not in scraped_ids]
    
    if new_products or removed_products:
        updated_products = [p for p in existing_products if p["id"] in scraped_ids]
        updated_products.extend(new_products)

        with JSON_PATH.open("w") as products_json:
            json.dump(updated_products, products_json, indent=4)

    return new_products, removed_products


if __name__ == "__main__":
    products = get_products(3)
    new, removed = get_product_changes(products)
    print(f"New: {len(new)}, Removed: {len(removed)}")
