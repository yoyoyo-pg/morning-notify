import feedparser

_FEEDS = {
    "国内": "https://news.yahoo.co.jp/rss/categories/domestic.xml",
    "経済": "https://news.yahoo.co.jp/rss/topics/business.xml",
    "国際": "https://news.yahoo.co.jp/rss/topics/world.xml",
}

_ITEMS_PER_CATEGORY = 3


def get_news() -> dict[str, list[tuple[str, str]]]:
    result = {}
    for category, url in _FEEDS.items():
        try:
            feed = feedparser.parse(url)
            result[category] = [(e.title, e.link) for e in feed.entries[:_ITEMS_PER_CATEGORY]]
        except Exception:
            result[category] = []
    return result
