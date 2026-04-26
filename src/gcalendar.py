# TODO: Google Calendar 連携（未実装）
# import os
# from datetime import datetime, timezone, timedelta
#
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
#
# _JST = timezone(timedelta(hours=9))
#
#
# def get_today_events() -> list[dict]:
#     creds = Credentials(
#         token=None,
#         refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
#         token_uri="https://oauth2.googleapis.com/token",
#         client_id=os.environ["GOOGLE_CLIENT_ID"],
#         client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
#     )
#     service = build("calendar", "v3", credentials=creds)
#
#     now = datetime.now(_JST)
#     day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
#     day_end = day_start + timedelta(days=1)
#
#     result = service.events().list(
#         calendarId="primary",
#         timeMin=day_start.isoformat(),
#         timeMax=day_end.isoformat(),
#         singleEvents=True,
#         orderBy="startTime",
#     ).execute()
#
#     events = []
#     for item in result.get("items", []):
#         start = item["start"].get("dateTime") or item["start"].get("date", "")
#         if "T" in start:
#             dt = datetime.fromisoformat(start).astimezone(_JST)
#             time_str = dt.strftime("%H:%M")
#         else:
#             time_str = "終日"
#         events.append({"time": time_str, "summary": item.get("summary", "（無題）")})
#
#     return events
