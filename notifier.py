import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
TIMEZONE = timezone(timedelta(hours=10))

def send_discord_message(new, removed):
    datetime_now = datetime.now(tz=TIMEZONE).isoformat()
    message_embeds = [
        {
            "title": product["name"],
            "description": f"URL: {product["url"]}",
            "timestamp": datetime_now,
            "image": {"url": product["image"]},
            "color": 65280
        }
        for product in new
    ]
    message_embeds.extend([
        {
            "title": product["name"],
            "description": f"URL: {product["url"]}",
            "timestamp": datetime_now,
            "image": {"url": product["image"]},
            "color": 16711680
        }
        for product in removed
    ])

    r = requests.post(
        url=DISCORD_WEBHOOK,
        json={
            "content": f"<@&1407662797893926953> **{len(new)}** products have been added!\n**{len(removed)}** products have been removed!",
            "allowed_mentions": {
                "parse": ["roles"]
            },
            "embeds": message_embeds
        }
    )
    return r.status_code

if __name__ == "__main__":
    sample_new_prods = [
        {
            "id": 7334667026633,
            "name": "Pokemon TCG - 2025 Trainer's Toolkit",
            "url": "https://www.jbhifi.com.au/products/pokemon-tcg-2025-trainers-toolkit-card-game",
            "image": "https://cdn.shopify.com/s/files/1/0024/9803/5810/files/815368-Product-0-I-638907255603826049.jpg?v=1755128835",
            "page": 10
        },
        {
            "id": 7334571081929,
            "name": "Pokemon TCG Charmander M2 Deck Box",
            "url": "https://www.jbhifi.com.au/products/pokemon-tcg-charmander-m2-deck-box-card-game-accessory",
            "image": "https://cdn.shopify.com/s/files/1/0024/9803/5810/files/829355-Product-0-I-638900553004106518.jpg?v=1754458567",
            "page": 16
        }
    ]
    sample_removed_prods = [
        {
            "id": 7334056034505,
            "name": "Pokemon TCG - Dragapult ex League Battle Deck",
            "url": "https://www.jbhifi.com.au/products/pokemon-tcg-dragapult-ex-league-battle-deck-card-game",
            "image": "https://cdn.shopify.com/s/files/1/0024/9803/5810/files/812805-Product-0-I-638833214405084595.jpg?v=1747724707",
            "page": 43
        },
        {
            "id": 7332418093257,
            "name": "Pokemon TCG - Ultra Pro Playmat Shimmering Skyline",
            "url": "https://www.jbhifi.com.au/products/pokemon-tcg-ultra-pro-playmat-shimmering-skyline-card-game-accessory",
            "image": "https://cdn.shopify.com/s/files/1/0024/9803/5810/files/722272-Product-0-I-638484991202200978.jpg?v=1712902339",
            "page": 43
        }
    ]
    send_discord_message(sample_new_prods, sample_removed_prods)
