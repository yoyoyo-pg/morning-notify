import os

from notion_client import Client

from routine import ROUTINE_ITEMS


def _heading_2(text: str) -> dict:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _to_do(text: str = "") -> dict:
    rich_text = [{"type": "text", "text": {"content": text}}] if text else []
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {"rich_text": rich_text, "checked": False},
    }


def _paragraph() -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": []},
    }


_DIVIDER = {"object": "block", "type": "divider", "divider": {}}


def create_journal_page(title: str) -> str:
    """Notionに日次ジャーナルページを作成してURLを返す。"""
    notion = Client(auth=os.environ["NOTION_API_KEY"])
    parent_id = os.environ["NOTION_PARENT_PAGE_ID"]

    children = [
        _heading_2("ルーチン・やれたこと"),
        *[_to_do(item) for item in ROUTINE_ITEMS],
        _DIVIDER,
        _heading_2("一日の振り返り"),
        _paragraph(),
    ]

    response = notion.pages.create(
        parent={"page_id": parent_id},
        properties={
            "title": [{"type": "text", "text": {"content": title}}],
        },
        children=children,
    )

    return response["url"]
