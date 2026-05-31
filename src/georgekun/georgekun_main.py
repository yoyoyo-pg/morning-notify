import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

from gcalendar import get_today_events
from news import get_news
from journal import create_journal_page
from notifier import send

_JST = timezone(timedelta(hours=9))
_WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]

_COLOR = 0x37474F  # ダークグレー


def build_embeds() -> tuple[str, list[dict]]:
    now = datetime.now(_JST)
    date_str = f"{now.month}/{now.day}({_WEEKDAYS[now.weekday()]})"

    content = "\n".join([
        f"💪 起きろ！{date_str}だ！",
        "",
        "男は言い訳をしない。",
        "今日やるべきことをやれ。それだけだ。",
    ])
    embeds = []

    try:
        events = get_today_events()
        description = "\n".join(f"・{e['time']} {e['summary']}" for e in events) if events else "今日はフリーだ。だからこそ全力で動ける。"
        calendar_embed = {
            "title": "📅 本日のスケジュール",
            "description": description,
            "color": _COLOR,
        }
    except Exception:
        calendar_embed = {
            "title": "📅 本日のスケジュール",
            "description": "スケジュールを取得できなかった。確認しろ。",
            "color": _COLOR,
        }
    embeds.append(calendar_embed)

    try:
        news = get_news()
        fields = [
            {
                "name": f"【{category}】",
                "value": "\n".join(f"[{title}]({link})" for title, link in items) or "取得できなかった",
                "inline": False,
            }
            for category, items in news.items()
        ]
        news_embed = {
            "title": "📰 今日の情報を確認しろ",
            "color": _COLOR,
            "fields": fields,
        }
    except Exception:
        news_embed = {
            "title": "📰 今日の情報を確認しろ",
            "description": "ニュースを取得できなかった",
            "color": _COLOR,
        }
    embeds.append(news_embed)

    try:
        journal_title = f"ジャーナル {now.year}/{now.month:02d}/{now.day:02d}({_WEEKDAYS[now.weekday()]})"
        journal_url = create_journal_page(journal_title)
        embeds.append({
            "title": "📓 今日の記録",
            "description": f"[Notionでオープン →]({journal_url})",
            "color": _COLOR,
            "url": journal_url,
        })
    except Exception:
        pass

    closing = "\n\nお前が動かなければ、誰も動かない。\n今すぐ始めろ。💪"
    return content + closing, embeds


if __name__ == "__main__":
    content, embeds = build_embeds()
    url = os.environ.get("DISCORD_WEBHOOK_URL_GEORGE") or os.environ["DISCORD_WEBHOOK_URL"]
    send(embeds, content=content, webhook_url=url)
