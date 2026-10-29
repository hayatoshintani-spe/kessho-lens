# AGENTS.md

Codex・Claude Code など AI コーディングエージェント共通の作業ガイド。
(Claude Code は `CLAUDE.md` 経由でこのファイルを読む。ルールはここに一本化する)

## プロジェクト概要

Tsuburaya Intelligence Brief (リポジトリ名: kessho-lens)。
外部ニュースを円谷向けの IntelCard / Daily Brief / AI Council Session に変換し、
毎朝 7:00 JST にメール配信する。詳細は `README.md`。

| ディレクトリ | 内容 |
|---|---|
| `backend/` | FastAPI (Python 3.11)。エントリ `main.py`、ルーター `api/`、ロジック `src/intel/`、保存 `src/data/storage.py` |
| `frontend/` | Next.js 14 App Router + TypeScript + Tailwind。画面 `app/intel/*`、API クライアント `lib/intel-api.ts` |
| `shared/` | 共有型 `types.ts` / `schemas.py` (両方を同期させる) |
| `data/` | JSON ファイル DB (`intel_cards.json` など) |
| `.github/workflows/daily-brief.yml` | 日次配信の一次スケジューラ (GitHub Actions)。Vercel Cron は保険 |

## セットアップ・確認コマンド

```bash
# backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8000          # http://localhost:8000/docs
python -m compileall -q .                       # 最低限の構文チェック

# frontend
cd frontend && npm install
npm run lint
npm run build                                   # 型チェックを含む
```

テストスイートは未整備。変更後は上記の lint / build / compileall を通し、
API を変えた場合は `uvicorn` を起動して該当エンドポイントを叩いて確認する。

## 守るべきルール

- **API キーなしでも動くこと。** `ANTHROPIC_API_KEY` 未設定時のテンプレートフォールバック
  (`card_generator.py` / `brief_generator.py` / `council.py`) を壊さない。
- **LLM コストガードを外さない。** 手動更新は 24h あたり `DAILY_BRIEF_MAX_RUNS_PER_DAY`
  (既定 5) 回に制限している (`backend/api/intel.py`)。新しく LLM を呼ぶ経路を足す場合も上限を設ける。
- **ストレージは `src/data/storage.py` 経由のみ。** JSON は temp → rename の原子的書き込み。
  `data/*.json` を直接書き換えるコードを追加しない。
- **型を変えたら `shared/types.ts`・`shared/schemas.py`・`frontend/lib/intel-types.ts` を揃える。**
- **シークレットをコミットしない。** 新しい環境変数は `.env.example`・`render.yaml`・README の
  環境変数一覧に追記する。
- `/api/intel/cron/*` は `Authorization: Bearer $CRON_SECRET` 認証を維持する。
- コメント・UI 文言・コミット本文の説明は日本語可。既存ファイルの書き方 (日本語 docstring、
  命名) に合わせる。
- コミットは Conventional Commits 形式 (`feat:` / `fix:` / `chore:` / `ci:` …)。

## エージェント間の分担 (Codex ⇄ Claude Code)

- 作業は 1 タスク 1 ブランチ・1 PR。同じブランチを同時に 2 エージェントで触らない。
- PR 本文に「何を・なぜ・どう確認したか」を書き、もう一方のエージェントがレビューできる状態にする。
- レビュー指摘への対応は PR 上で返信し、未対応の理由も明記する。
- 判断に迷う設計変更 (データ構造、外部サービス追加、スケジューラ変更) は実装前に Issue / PR で提案する。
