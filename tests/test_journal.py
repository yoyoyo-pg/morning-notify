import os
from unittest.mock import patch, MagicMock, call

import pytest

os.environ.setdefault("NOTION_API_KEY", "test_notion_key")
os.environ.setdefault("NOTION_PARENT_PAGE_ID", "test_parent_id")
os.environ.setdefault("NOTION_TEMPLATE_PAGE_ID", "test_template_id")

from journal import create_journal_page, _strip_block

_TITLE = "ジャーナル 2026/04/26(日)"
_NOTION_URL = "https://notion.so/test-page-abcdef"

_TEMPLATE_BLOCKS = [
    {
        "object": "block", "id": "b1", "type": "heading_2",
        "created_time": "2026-01-01", "has_children": False, "archived": False,
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": "ルーチン・やれたこと"}}], "color": "default"},
    },
    {
        "object": "block", "id": "b2", "type": "to_do",
        "created_time": "2026-01-01", "has_children": False, "archived": False,
        "to_do": {"rich_text": [{"type": "text", "text": {"content": "Duolingo"}}], "checked": False, "color": "default"},
    },
    {
        "object": "block", "id": "b3", "type": "divider",
        "created_time": "2026-01-01", "has_children": False, "archived": False,
        "divider": {},
    },
    {
        "object": "block", "id": "b4", "type": "heading_2",
        "created_time": "2026-01-01", "has_children": False, "archived": False,
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": "一日の振り返り"}}], "color": "default"},
    },
]


def _mock_notion(url: str = _NOTION_URL) -> MagicMock:
    m = MagicMock()
    m.blocks.children.list.return_value = {"results": _TEMPLATE_BLOCKS}
    m.pages.create.return_value = {"url": url}
    return m


# ── _strip_block ───────────────────────────────────────────────

def test_strip_block_removes_metadata():
    block = _TEMPLATE_BLOCKS[1]  # to_do
    result = _strip_block(block)
    assert "id" not in result
    assert "created_time" not in result
    assert "has_children" not in result
    assert "archived" not in result


def test_strip_block_keeps_content():
    block = _TEMPLATE_BLOCKS[1]  # to_do
    result = _strip_block(block)
    assert result["type"] == "to_do"
    assert result["object"] == "block"
    assert result["to_do"]["checked"] is False
    assert result["to_do"]["rich_text"][0]["text"]["content"] == "Duolingo"


# ── create_journal_page ────────────────────────────────────────

def test_create_journal_page_returns_url():
    with patch("journal.Client", return_value=_mock_notion()):
        url = create_journal_page(_TITLE)
    assert url == _NOTION_URL


def test_create_journal_page_sets_title():
    mock = _mock_notion()
    with patch("journal.Client", return_value=mock):
        create_journal_page(_TITLE)

    kwargs = mock.pages.create.call_args[1]
    assert kwargs["properties"]["title"][0]["text"]["content"] == _TITLE


def test_create_journal_page_sets_parent_id():
    mock = _mock_notion()
    with patch("journal.Client", return_value=mock):
        create_journal_page(_TITLE)

    kwargs = mock.pages.create.call_args[1]
    assert kwargs["parent"]["page_id"] == "test_parent_id"


def test_create_journal_page_fetches_template():
    mock = _mock_notion()
    with patch("journal.Client", return_value=mock):
        create_journal_page(_TITLE)

    mock.blocks.children.list.assert_called_once_with(block_id="test_template_id")


def test_create_journal_page_passes_stripped_blocks():
    mock = _mock_notion()
    with patch("journal.Client", return_value=mock):
        create_journal_page(_TITLE)

    children = mock.pages.create.call_args[1]["children"]
    assert len(children) == len(_TEMPLATE_BLOCKS)
    for block in children:
        assert "id" not in block
        assert "created_time" not in block
        assert "has_children" not in block
