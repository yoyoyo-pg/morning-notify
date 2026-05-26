from unittest.mock import patch, Mock

from sakanakun_main import build_embed, get_articles, _extract_summary


def _make_entry(title: str, link: str, summary: str = "") -> Mock:
    return Mock(title=title, link=link, summary=summary)


def _make_feed(entries: list[dict]) -> Mock:
    mock = Mock()
    mock.entries = [
        _make_entry(e["title"], e["link"], e.get("summary", ""))
        for e in entries
    ]
    return mock


def _make_entries(n: int, prefix: str = "記事") -> list[dict]:
    return [{"title": f"{prefix}{i}", "link": f"https://example.com/{i}"} for i in range(n)]


# ── _extract_summary ───────────────────────────────────────────

def test_extract_summary_strips_html():
    entry = _make_entry("t", "u", "<p>本文です。</p><br/>続き")
    assert _extract_summary(entry) == "本文です。続き"


def test_extract_summary_truncates_long_text():
    entry = _make_entry("t", "u", "あ" * 100)
    result = _extract_summary(entry)
    assert result.endswith("…")
    assert len(result) <= 81  # 80文字 + "…"


def test_extract_summary_empty_returns_empty():
    entry = _make_entry("t", "u", "")
    assert _extract_summary(entry) == ""


def test_extract_summary_no_attribute_returns_empty():
    entry = Mock(spec=[])  # summaryなし
    assert _extract_summary(entry) == ""


# ── get_articles ───────────────────────────────────────────────

def test_get_articles_returns_both_sources():
    feeds = [_make_feed(_make_entries(3, "Zenn")), _make_feed(_make_entries(3, "Qiita"))]
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    assert "Zenn" in result
    assert "Qiita" in result
    assert len(result["Zenn"]) == 3
    assert len(result["Qiita"]) == 3


def test_get_articles_limits_to_3_per_source():
    feeds = [_make_feed(_make_entries(5)), _make_feed(_make_entries(5))]
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    assert len(result["Zenn"]) == 3
    assert len(result["Qiita"]) == 3


def test_get_articles_returns_title_url_summary_tuple():
    entries = [{"title": "記事A", "link": "https://zenn.dev/a", "summary": "概要です"}]
    feeds = [_make_feed(entries), _make_feed([])]
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    title, url, summary = result["Zenn"][0]
    assert title == "記事A"
    assert url == "https://zenn.dev/a"
    assert summary == "概要です"


def test_get_articles_returns_empty_on_failure():
    with patch("sakanakun_main.feedparser.parse", side_effect=Exception("connection error")):
        result = get_articles()

    assert result["Zenn"] == []
    assert result["Qiita"] == []


def test_get_articles_partial_failure():
    feeds = [Exception("zenn down"), _make_feed(_make_entries(3, "Qiita"))]
    with patch("sakanakun_main.feedparser.parse", side_effect=feeds):
        result = get_articles()

    assert result["Zenn"] == []
    assert len(result["Qiita"]) == 3


# ── build_embed ────────────────────────────────────────────────

def test_build_embed_with_articles():
    articles = {
        "Zenn":  [("Zenn記事1", "https://zenn.dev/1", "Zennの概要"), ("Zenn記事2", "https://zenn.dev/2", "")],
        "Qiita": [("Qiita記事1", "https://qiita.com/1", "Qiitaの概要")],
    }
    with patch("sakanakun_main.get_articles", return_value=articles):
        embed = build_embed()

    assert embed["title"] == "🐟 ギョギョ！今週の技術トレンドまとめだよ〜！"
    assert "description" not in embed
    assert len(embed["fields"]) == 2
    assert embed["fields"][0]["name"] == "Zenn"
    assert "Zenn記事1" in embed["fields"][0]["value"]
    assert "Zennの概要" in embed["fields"][0]["value"]
    assert embed["fields"][1]["name"] == "Qiita"


def test_build_embed_no_articles_shows_fallback():
    with patch("sakanakun_main.get_articles", return_value={"Zenn": [], "Qiita": []}):
        embed = build_embed()

    assert "description" in embed
    assert "fields" not in embed


def test_build_embed_partial_source():
    articles = {
        "Zenn":  [("Zenn記事1", "https://zenn.dev/1", "概要")],
        "Qiita": [],
    }
    with patch("sakanakun_main.get_articles", return_value=articles):
        embed = build_embed()

    assert len(embed["fields"]) == 1
    assert embed["fields"][0]["name"] == "Zenn"


def test_build_embed_summary_appears_as_blockquote():
    """要約が > 形式で記事リンクの次行に表示される。"""
    articles = {
        "Zenn":  [("記事A", "https://zenn.dev/a", "これが概要")],
        "Qiita": [],
    }
    with patch("sakanakun_main.get_articles", return_value=articles):
        embed = build_embed()

    value = embed["fields"][0]["value"]
    assert "  > これが概要" in value


def test_build_embed_empty_summary_not_shown():
    """要約が空のとき > 行は出力されない。"""
    articles = {
        "Zenn":  [("記事B", "https://zenn.dev/b", "")],
        "Qiita": [],
    }
    with patch("sakanakun_main.get_articles", return_value=articles):
        embed = build_embed()

    value = embed["fields"][0]["value"]
    assert "  > " not in value
