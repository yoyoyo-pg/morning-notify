import os
import re

import feedparser
from dotenv import load_dotenv

load_dotenv()

from notifier import send

_FEEDS = {
    "Zenn":  "https://zenn.dev/feed",
    "Qiita": "https://qiita.com/popular-items/feed.atom",
}
_ITEMS_PER_SOURCE = 3
_SUMMARY_MAX_LEN = 80
_COLOR = 0x00BCD4  # 水色


def _extract_summary(entry) -> str:
    """RSSのsummaryからHTMLタグを除去して切り詰める。"""
    raw = getattr(entry, "summary", "") or ""
    text = re.sub(r"<[^>]+>", "", raw).strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) > _SUMMARY_MAX_LEN:
        text = text[:_SUMMARY_MAX_LEN].rstrip() + "…"
    return text


def get_articles() -> dict[str, list[tuple[str, str, str]]]:
    """(title, url, summary) のリストを返す。"""
    result = {}
    for source, url in _FEEDS.items():
        try:
            feed = feedparser.parse(url)
            items = []
            for e in feed.entries[:_ITEMS_PER_SOURCE]:
                summary = _extract_summary(e)
                items.append((e.title, e.link, summary))
            result[source] = items
        except Exception:
            result[source] = []
    return result


def build_embed() -> dict:
    articles = get_articles()
    fields = []
    for source, items in articles.items():
        if items:
            lines = []
            for title, url, summary in items:
                lines.append(f"・[{title}]({url})")
                if summary:
                    lines.append(f"  > {summary}")
            fields.append({"name": source, "value": "\n".join(lines), "inline": False})

    if not fields:
        return {
            "title": "🐟 ギョギョ！今週の技術まとめだよ〜！",
            "description": "ギョ…今週は記事が取れなかったギョ…！🐡",
            "color": _COLOR,
        }
    return {
        "title": "🐟 ギョギョ！今週の技術トレンドまとめだよ〜！",
        "color": _COLOR,
        "fields": fields,
    }


if __name__ == "__main__":
    embed = build_embed()
    url = os.environ.get("DISCORD_WEBHOOK_URL_SAKANAKUN") or os.environ["DISCORD_WEBHOOK_URL"]
    send([embed], webhook_url=url)
