---
description: 毎朝の経営ブリーフィングを生成（予定・重要メール・外部トピック・宿題を1枚に統合）
argument-hint: [任意：特に見たい論点]
allowed-tools: Read, Write, Grep, Glob, WebSearch, WebFetch, mcp__Gmail__search_threads, mcp__Gmail__get_thread, mcp__Google_Calendar__list_events, mcp__Google_Calendar__list_calendars
model: opus
---

参謀長（sanbo-cho）として、今日の経営ブリーフィングを作成せよ。

追加で注目したい論点があれば考慮せよ: $ARGUMENTS

手順:
1. `advisory/knowledge/my-mandate.md` を読み、上司のミッション・KPI・最重要論点TOP3を把握。
2. Google Calendar で今日の予定を取得し、準備が要る予定を特定。
3. Gmail で未読・重要スレッドを確認（意思決定/締切/依頼のみ抽出、ノイズ除外）。
4. 可能なら `data/intel_briefs.json` または WebSearch で外部トピック（IP/競合/規制/資本市場）を1〜3件。
5. `advisory/02_issues/` と `advisory/10_decision-log/` から動いている論点・保留判断を拾う。
6. sanbo-cho の「毎朝ブリーフ」フォーマットで1枚に統合。「今日の一点集中」を必ず先頭に。
7. 生成したブリーフを `advisory/01_daily-brief/YYYY-MM-DD.md` に保存。

上司が2〜3分で「今日どこに頭を使うか」を決められることがゴール。冗長さは敵。
