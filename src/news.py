import feedparser

_FEEDS = {
    "政治":       "https://www3.nhk.or.jp/rss/news/cat04.xml",
    "経済":       "https://www3.nhk.or.jp/rss/news/cat05.xml",
    "技術":       "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",
    "AI":         "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
    "セキュリティ": "https://rss.itmedia.co.jp/rss/2.0/security.xml",
}

_ITEMS_PER_CATEGORY = 2


def get_news() -> dict[str, list[tuple[str, str]]]:
    result = {}
    for category, url in _FEEDS.items():
        try:
            feed = feedparser.parse(url)
            result[category] = [(e.title, e.link) for e in feed.entries[:_ITEMS_PER_CATEGORY]]
        except Exception:
            result[category] = []
    return result
