import os

from notion_client import Client

_BLOCK_META_KEYS = frozenset({
    "id", "created_time", "last_edited_time",
    "created_by", "last_edited_by",
    "has_children", "archived", "in_trash", "parent",
})


def _strip_block(block: dict) -> dict:
    """Notion APIのメタデータを除去し、pages.create に渡せる形にする。"""
    block_type = block["type"]
    content = {k: v for k, v in block[block_type].items() if k not in _BLOCK_META_KEYS}
    return {"object": "block", "type": block_type, block_type: content}


def create_journal_page(title: str) -> str:
    """テンプレートページを元にNotionへ日次ジャーナルページを作成してURLを返す。"""
    notion = Client(auth=os.environ["NOTION_API_KEY"])
    template_id = os.environ["NOTION_TEMPLATE_PAGE_ID"]
    parent_id = os.environ["NOTION_PARENT_PAGE_ID"]

    blocks = notion.blocks.children.list(block_id=template_id)["results"]
    children = [_strip_block(b) for b in blocks]

    response = notion.pages.create(
        parent={"page_id": parent_id},
        properties={"title": [{"type": "text", "text": {"content": title}}]},
        children=children,
    )
    return response["url"]
