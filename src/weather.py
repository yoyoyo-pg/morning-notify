import requests

_URL = "https://wttr.in/Nagoya?format=j1&lang=ja"


def get_weather() -> dict:
    resp = requests.get(_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    current = data["current_condition"][0]
    hourly = data["weather"][0]["hourly"]
    precip_prob = max(int(h.get("chanceofrain", 0)) for h in hourly)

    return {
        "desc": current["weatherDesc"][0]["value"],
        "temp": current["temp_C"],
        "precip_prob": precip_prob,
    }
