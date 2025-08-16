import requests
import logging
import time

BASE_URL = "https://www.jbhifi.com.au/products/"
logger = logging.getLogger(__name__)

def get_products(pages: int):
    start_time = time.time()
    poke_products = []

    for i in range(min(pages + 5, 100)):
        logger.info(f"Checking page {i}...")
        page_start_time = time.time()
        url = f"https://www.jbhifi.com.au/products.json?limit=250&page={i}"

        r = requests.get(url)
        data = r.json()

        for item in data["products"]:
            if item["vendor"] == "POKEMON TCG":
                logger.info(f"Found product: {item['title']}")
                poke_products.append({
                    "id": item["id"],
                    "name": item["title"],
                    "url": "https://www.jbhifi.com.au/products/" + item["handle"],
                    "image": item["images"][0]["src"],
                    "page": i
                })
        time_taken = time.time() - page_start_time
        if time_taken < 0.5:
            time.sleep(0.5 - time_taken)
        logger.info(f"    Finished in: {'%.2f' % (time_taken)} s.\n")

    logger.info(f"{len(poke_products)} products found.")
    logger.info(f"Scraping finished in: {'%.2f' % (time.time() - start_time)} s.")

    return poke_products

if __name__ == "__main__":
    start_time = time.time()
    raw_prods = get_products()
    links = [f"https://www.jbhifi.com.au/products/{prod['handle']}" for prod in raw_prods]

    for link in links:
        print(link)
    print(f"Time taken: {'%.2f' % (time.time() - start_time)} s.")
