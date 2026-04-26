import os

import requests


def send(message: str) -> None:
    url = os.environ["DISCORD_WEBHOOK_URL"]
    requests.post(url, json={"content": message}, timeout=10).raise_for_status()
