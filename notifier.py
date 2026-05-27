from datetime import datetime, timezone, timedelta
import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1407651931081543750/uTEZmxY-OyBkSXb7Lf-A9Ak3FSJ-Orn0z6abJKHeSK-f1QGwFZUs0_w16oLzKJmHopsp"
TIMEZONE = timezone(timedelta(hours=10))

def send_discord_message(embeds, message):
    datetime_now = datetime.now(tz=TIMEZONE).isoformat()

    for embed in embeds:
        embed["timestamp"] = datetime_now

    r = requests.post(
        url=DISCORD_WEBHOOK,
        json={
            "content": message,
            "allowed_mentions": {
                "parse": ["roles"]
            },
            "embeds": embeds
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
