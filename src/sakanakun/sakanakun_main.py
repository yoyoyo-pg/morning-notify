import os

import feedparser
from dotenv import load_dotenv

load_dotenv()

from notifier import send

_FEEDS = {
    "AI":           "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
    "セキュリティ":  "https://rss.itmedia.co.jp/rss/2.0/security.xml",
    "Zenn":         "https://zenn.dev/feed",
    "AWS新機能":     "https://aws.amazon.com/jp/about-aws/whats-new/recent/feed/",
    "AWSステータス": "https://status.aws.amazon.com/rss/all.rss",
    "JPCERT/CC":    "https://www.jpcert.or.jp/rss/jpcert.rdf",
}
_ITEMS_PER_SOURCE = 3
_COLOR = 0x00BCD4  # 水色


def get_articles() -> dict[str, list[tuple[str, str]]]:
    """(title, url) のリストを返す。"""
    result = {}
    for source, url in _FEEDS.items():
        try:
            feed = feedparser.parse(url)
            items = [(e.title, e.link) for e in feed.entries[:_ITEMS_PER_SOURCE]]
            result[source] = items
        except Exception:
            result[source] = []
    return result


def build_embed() -> dict:
    articles = get_articles()
    fields = []
    for source, items in articles.items():
        if items:
            value = "\n".join(f"・[{title}]({url})" for title, url in items)
            fields.append({"name": source, "value": value, "inline": False})

    if not fields:
        return {
            "title": "🐟 ギョギョ！今日の技術情報だよ〜！",
            "description": "ギョ…今日は記事が取れなかったギョ…！🐡",
            "color": _COLOR,
        }
    return {
        "title": "🐟 ギョギョ！今日の技術情報だよ〜！",
        "color": _COLOR,
        "fields": fields,
    }


if __name__ == "__main__":
    embed = build_embed()
    url = os.environ.get("DISCORD_WEBHOOK_URL_SAKANAKUN") or os.environ["DISCORD_WEBHOOK_URL"]
    send([embed], webhook_url=url)
