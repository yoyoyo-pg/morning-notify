from unittest.mock import patch, Mock

from sakanakun_main import build_embed, get_articles

_ALL_SOURCES = ["AI", "セキュリティ", "Zenn", "AWS新機能", "AWSステータス", "JPCERT/CC"]


def _make_entry(title: str, link: str) -> Mock:
    return Mock(title=title, link=link)


def _make_feed(entries: list[dict]) -> Mock:
    mock = Mock()
    mock.entries = [_make_entry(e["title"], e["link"]) for e in entries]
    return mock


def _make_entries(n: int, prefix: str = "記事") -> list[dict]:
    return [{"title": f"{prefix}{i}", "link": f"https://example.com/{i}"} for i in range(n)]


# ── get_articles ───────────────────────────────────────────────

def test_get_articles_returns_both_sources():
    feeds = [_make_feed(_make_entries(3, s)) for s in _ALL_SOURCES]
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    assert "AI" in result
    assert "Zenn" in result
    assert len(result["AI"]) == 3
    assert len(result["Zenn"]) == 3


def test_get_articles_limits_to_3_per_source():
    feeds = [_make_feed(_make_entries(5)) for _ in _ALL_SOURCES]
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    assert len(result["Zenn"]) == 3
    assert len(result["AI"]) == 3


def test_get_articles_returns_title_url_tuple():
    entries = [{"title": "記事A", "link": "https://zenn.dev/a"}]
    feeds = [_make_feed([]) for _ in _ALL_SOURCES]
    feeds[2] = _make_feed(entries)  # Zenn は3番目
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    title, url = result["Zenn"][0]
    assert title == "記事A"
    assert url == "https://zenn.dev/a"


def test_get_articles_returns_empty_on_failure():
    with patch("sakanakun_main.feedparser.parse", side_effect=Exception("connection error")):
        result = get_articles()

    assert result["Zenn"] == []
    assert result["AI"] == []


def test_get_articles_partial_failure():
    feeds = [Exception("ai down")] + [_make_feed(_make_entries(3, s)) for s in _ALL_SOURCES[1:]]
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    assert result["AI"] == []
    assert len(result["Zenn"]) == 3


# ── build_embed ────────────────────────────────────────────────

def test_build_embed_with_articles():
    articles = {
        "Zenn":  [("Zenn記事1", "https://zenn.dev/1"), ("Zenn記事2", "https://zenn.dev/2")],
        "AI":    [("AI記事1", "https://example.com/1")],
    }
    with patch("sakanakun_main.get_articles", return_value=articles):
        embed = build_embed()

    assert embed["title"] == "🐟 ギョギョ！今日の技術情報だよ〜！"
    assert "description" not in embed
    assert len(embed["fields"]) == 2
    assert embed["fields"][0]["name"] == "Zenn"
    assert "Zenn記事1" in embed["fields"][0]["value"]
    assert embed["fields"][1]["name"] == "AI"


def test_build_embed_no_articles_shows_fallback():
    with patch("sakanakun_main.get_articles", return_value={s: [] for s in _ALL_SOURCES}):
        embed = build_embed()

    assert "description" in embed
    assert "fields" not in embed


def test_build_embed_partial_source():
    articles = {
        "Zenn":  [("Zenn記事1", "https://zenn.dev/1")],
        "AI":    [],
    }
    with patch("sakanakun_main.get_articles", return_value=articles):
        embed = build_embed()

    assert len(embed["fields"]) == 1
    assert embed["fields"][0]["name"] == "Zenn"
