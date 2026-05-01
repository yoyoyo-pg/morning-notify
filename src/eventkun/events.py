from datetime import datetime, timezone, timedelta

import requests

_CONNPASS_API_URL = "https://connpass.com/api/v1/event/"
_COUNT = 5
_JST = timezone(timedelta(hours=9))
_WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]


def get_events() -> list[dict]:
    """Connpass APIから愛知県の直近イベントを取得する。

    Returns:
        list[dict]: 各要素は {"title": str, "date": str, "place": str, "url": str}
        取得失敗時は空リストを返す。
    """
    try:
        today = datetime.now(_JST).strftime("%Y%m%d")
        params = {
            "prefecture": "aichi",
            "count": _COUNT,
            "order": 2,
            "start_from": today,
        }
        response = requests.get(_CONNPASS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        events = []
        for item in data.get("events", []):
            started_at = item.get("started_at", "")
            date_str = _format_date(started_at)
            place = item.get("place") or "オンライン"
            events.append({
                "title": item.get("title", ""),
                "date": date_str,
                "place": place,
                "url": item.get("event_url", ""),
            })
        return events
    except Exception:
        return []


def _format_date(started_at: str) -> str:
    """ISO8601形式の日時文字列を 'MM/DD(曜)' 形式に変換する。"""
    try:
        dt = datetime.fromisoformat(started_at)
        weekday = _WEEKDAYS[dt.weekday()]
        return f"{dt.month:02d}/{dt.day:02d}({weekday})"
    except Exception:
        return started_at
