# AGENTS.md

## プロジェクト概要

毎朝7時(JST)に天気・Googleカレンダー・ニュースをDiscordへ通知するPythonスクリプト。GitHub Actionsで定期実行する。

## リポジトリ構成

```
morning-notify/
├── .github/workflows/morning-notify.yml   # スケジュール実行定義
├── src/
│   ├── main.py          # エントリーポイント。各モジュールを呼び出して通知を組み立てる
│   ├── weather.py       # wttr.in APIで名古屋の天気を取得
│   ├── calendar.py      # Google Calendar APIで当日の予定を取得
│   ├── news.py          # RSSフィードから日本語ニュースを取得
│   └── notifier.py      # Discordへ通知を送信
├── tests/
├── requirements.txt
└── .env.example
```

## 技術スタック

- **言語**: Python 3.11+
- **天気**: [wttr.in](https://wttr.in) JSON API（APIキー不要）
- **カレンダー**: `google-api-python-client`
- **ニュース**: `feedparser` + 日本語RSSフィード
- **通知**: Discord Webhook（`requests`ライブラリ）
- **CI/CD**: GitHub Actions

## コマンド

```bash
pip install -r requirements.txt   # 依存インストール
python src/main.py                # ローカル実行
pytest tests/                     # テスト実行
```

## 制約

- 認証情報をコードにハードコードしない（必ず環境変数から読む）
- 既存のモジュール構成（weather / calendar / news / notifier）を理由なく変えない
- 新しい外部APIを勝手に追加しない
- Google Calendar認証は非対話型（refresh token方式）のみ使用する
- GitHub Actions の cron はUTC基準: `0 22 * * *` = JST 7:00
- テストは外部APIをモックして書く（実APIは叩かない）
- ニュースRSSは取得できない場合のフォールバックを必ず設けること
