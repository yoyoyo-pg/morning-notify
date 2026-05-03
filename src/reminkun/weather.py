import requests

_URL = "https://wttr.in/Nagoya?format=j1&lang=ja"
_LINK = "https://wttr.in/Nagoya"
_HOURLY_TARGETS = [("朝", "600", "06:00"), ("昼", "1200", "12:00"), ("夜", "1800", "18:00")]


def get_weather() -> dict:
    resp = requests.get(_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    current = data["current_condition"][0]
    today = data["weather"][0]
    hourly = today["hourly"]
    precip_prob = max(int(h.get("chanceofrain", 0)) for h in hourly)

    hourly_map = {h["time"]: h for h in hourly if "time" in h}
    hourly_summary = []
    for label, time_key, time_str in _HOURLY_TARGETS:
        h = hourly_map.get(time_key)
        if h:
            hourly_summary.append({
                "label": label,
                "time": time_str,
                "temp": h["tempC"],
                "rain": int(h.get("chanceofrain", 0)),
                "desc": h["weatherDesc"][0]["value"],
            })

    return {
        "desc": current["weatherDesc"][0]["value"],
        "temp": current["temp_C"],
        "temp_max": today["maxtempC"],
        "temp_min": today["mintempC"],
        "precip_prob": precip_prob,
        "hourly_summary": hourly_summary,
        "url": _LINK,
    }
