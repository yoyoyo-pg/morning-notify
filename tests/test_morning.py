from unittest.mock import patch
from datetime import datetime, timezone, timedelta

from main import build_embeds

_JST = timezone(timedelta(hours=9))


def test_build_embeds_content_has_date():
    now = datetime.now(_JST)
    date_str = f"{now.month}/{now.day}"

    with patch("main.get_today_events", return_value=[]), \
         patch("main.get_news", return_value={}), \
         patch("main.create_journal_page", side_effect=Exception):
        content, _ = build_embeds()

    assert date_str in content
    assert "起きろ" in content
    assert "今すぐ始めろ" in content


def test_build_embeds_has_calendar_and_news():
    events = [{"time": "10:00", "summary": "MTG"}]
    news = {"国内": [("記事1", "https://example.com/1")]}

    with patch("main.get_today_events", return_value=events), \
         patch("main.get_news", return_value=news), \
         patch("main.create_journal_page", side_effect=Exception):
        _, embeds = build_embeds()

    titles = [e["title"] for e in embeds]
    assert any("スケジュール" in t for t in titles)
    assert any("情報" in t for t in titles)
    assert "MTG" in embeds[0]["description"]


def test_build_embeds_calendar_fallback():
    with patch("main.get_today_events", side_effect=Exception("api error")), \
         patch("main.get_news", return_value={}), \
         patch("main.create_journal_page", side_effect=Exception):
        _, embeds = build_embeds()

    assert "確認しろ" in embeds[0]["description"]


def test_build_embeds_no_journal_on_error():
    with patch("main.get_today_events", return_value=[]), \
         patch("main.get_news", return_value={}), \
         patch("main.create_journal_page", side_effect=Exception("notion error")):
        _, embeds = build_embeds()

    titles = [e["title"] for e in embeds]
    assert not any("記録" in t for t in titles)
    assert len(embeds) == 2
