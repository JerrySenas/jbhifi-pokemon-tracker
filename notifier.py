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
            "description": f"URL: {product['url']}",
            "timestamp": datetime_now,
            "image": {"url": product['image']},
            "color": 65280
        }
        for product in new
    ]
    message_embeds.extend([
        {
            "title": product["name"],
            "description": f"URL: {product['url']}",
            "timestamp": datetime_now,
            "image": {"url": product['image']},
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
    return r

def still_alive():
    requests.post(
        url=DISCORD_WEBHOOK,
        json={
            "content": "*You took a peek into Celadon Gym.*\n\"Zzz...\"\n*It seems Erika has dozed off...*"
        }
    )

if __name__ == "__main__":
    still_alive()
