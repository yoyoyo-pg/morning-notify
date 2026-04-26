import pytest
# TODO: Google Calendar 連携（未実装）のためスキップ
# import os
# from unittest.mock import patch, MagicMock
#
# os.environ.setdefault("GOOGLE_CLIENT_ID", "test_id")
# os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test_secret")
# os.environ.setdefault("GOOGLE_REFRESH_TOKEN", "test_token")
#
# from calendar import get_today_events

_MOCK_EVENTS = {
    "items": [
        {"summary": "チームミーティング", "start": {"dateTime": "2026-04-26T10:00:00+09:00"}},
        {"summary": "1on1",               "start": {"dateTime": "2026-04-26T14:00:00+09:00"}},
        {"summary": "終日イベント",        "start": {"date": "2026-04-26"}},
    ]
}


def _mock_service(events: dict) -> MagicMock:
    service = MagicMock()
    service.events().list().execute.return_value = events
    return service


def test_get_today_events_parses_datetime():
    with patch("calendar.build", return_value=_mock_service(_MOCK_EVENTS)), \
         patch("calendar.Credentials"):
        events = get_today_events()

    assert events[0] == {"time": "10:00", "summary": "チームミーティング"}
    assert events[1] == {"time": "14:00", "summary": "1on1"}


def test_get_today_events_handles_all_day():
    with patch("calendar.build", return_value=_mock_service(_MOCK_EVENTS)), \
         patch("calendar.Credentials"):
        events = get_today_events()

    assert events[2] == {"time": "終日", "summary": "終日イベント"}


def test_get_today_events_empty():
    with patch("calendar.build", return_value=_mock_service({"items": []})), \
         patch("calendar.Credentials"):
        events = get_today_events()

    assert events == []


def test_get_today_events_no_summary():
    mock_events = {"items": [{"start": {"dateTime": "2026-04-26T09:00:00+09:00"}}]}

    with patch("calendar.build", return_value=_mock_service(mock_events)), \
         patch("calendar.Credentials"):
        events = get_today_events()

    assert events[0]["summary"] == "（無題）"
