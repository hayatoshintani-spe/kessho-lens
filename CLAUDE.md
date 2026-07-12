# CLAUDE.md — Tsuburaya Intelligence Brief 開発ガイド

AI 開発セッション(Claude Code 等)向けの必読コンテキスト。詳細設計は `docs/ARCHITECTURE.md`、今後の機能仕様は `docs/ROADMAP.md` を参照。

## このプロダクトは何か

外部ニュース・規制動向・技術トレンドを、円谷の**経営論点・打ち手・KPI・実行計画**に翻訳する情報基盤。「読むためのニュース」ではなく「動くためのインテリジェンス」。

- リポジトリ名 `kessho-lens` は歴史的経緯(旧・投資シミュレーションアプリ)。現在は Intelligence Brief 専用。
- 中核データは **IntelCard**(事実+解釈+円谷への示唆+次アクション)。カード → Daily Brief → AI Council → 改革アクション/週次アジェンダ、と経営判断に近づけていく設計。

## 構成

| 層 | 技術 | デプロイ先 | 場所 |
|---|---|---|---|
| Frontend | Next.js 14 App Router | Vercel (Root Directory: `frontend`) | `frontend/` |
| Backend | FastAPI + Python 3.11 | Render (starter, 常時起動) | `backend/` |
| データ | JSON ファイル(原子的書き込み) | Render ローカル + Notion 永続化 | `data/` + `backend/src/data/storage.py` |
| AI | Anthropic API `claude-sonnet-4-6` | — | `card_generator.py` / `council.py` |

## 絶対に守ること

1. **本番 AI モデルは `claude-sonnet-4-6`**(`backend/src/intel/card_generator.py` / `council.py`)。変更は明示指示があった時だけ。
2. **`ANTHROPIC_API_KEY` なしでも全機能がテンプレ/ルールベースで動く**こと(フォールバック維持)。API キー必須のコードパスを増やさない。
3. **暴走課金ガードを外さない**: `/api/intel/cron/daily-brief` は 24h で `DAILY_BRIEF_MAX_RUNS_PER_DAY`(既定 5)回まで。フロント「今すぐ更新」ボタンは window.confirm で明示確認。
4. **cron エンドポイントは `Authorization: Bearer <CRON_SECRET>` 必須**(`_verify_cron_auth`)。認証なしの書き込み系 cron を追加しない。
5. **Render のディスクは揮発性前提**: 真のデータ永続先は Notion。起動時に `notion_sync.restore_local_from_notion()` でカード/ブリーフを復元する(`backend/main.py` の startup)。ローカル JSON はキャッシュと考える。
6. **型は 2 箇所で同期**: バックエンドの dict 構造と `frontend/lib/intel-types.ts` / `reform-types.ts`。API レスポンスの形を変えたら両方直す。

## スケジューラ(三重構成、意図的な冗長)

毎朝 7:00 JST (= 22:00 UTC) に daily-brief を実行:
1. **GitHub Actions** `.github/workflows/daily-brief.yml` — **一次スケジューラ**(Secrets: `BACKEND_URL`, `CRON_SECRET`)
2. **Vercel Cron** `vercel.json` → `frontend/app/api/cron/daily-brief` — 保険(Hobby プラン制約で信頼性低)
3. 手動: ダッシュボード「今すぐ更新」ボタン / `POST /api/intel/cron/daily-brief`

パイプライン(`_run_daily_brief_pipeline`): ニュース取得(Google News RSS、無料) → カード生成 → Brief 生成 → Resend メール配信 → Notion 同期。非同期 202 + `/api/intel/cron/status` ポーリング方式(Vercel 10 秒制限回避)。

## 開発コマンド

```bash
# Backend (port 8000)
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000

# Backend テスト
cd backend && pip install -r requirements-dev.txt && python -m pytest

# Frontend (port 3000)
cd frontend && npm install && npm run dev

# 検証(コミット前に必ず)
cd frontend && npx tsc --noEmit && npm run build
cd backend && python -m pytest
```

## テストの注意

- pytest は `storage.DATA_DIR` を tmp_path に monkeypatch すること。**素で走らせるとリポジトリの `data/*.json`(シードデータ)を汚す**。`backend/tests/conftest.py` 参照。
- Anthropic / Notion / Resend は環境変数未設定ならフォールバックするので、テストは外部 API なしで動く。

## ディレクトリの読み方

- `backend/api/intel.py` — 全 API エンドポイント(1 ファイル集約)。cards / briefs / council / notion / email / cron / reform
- `backend/src/intel/` — ドメインロジック(card_generator, brief_generator, council, news_ingest, notion_sync, email_sender)
- `backend/src/data/storage.py` — `Storage` クラス。将来 DB 移行時はここだけ差し替え
- `frontend/app/intel/` — 画面(page=ダッシュボード, cards, brief, council, actions, agenda, kpi, themes, watchlist, delivery, notion)
- `frontend/lib/` — API クライアント(`intel-api.ts`, `reform-api.ts`)、型(`intel-types.ts`, `reform-types.ts`)、経営インパクトスコア(`impact-score.ts`: ルールベース・純粋関数、LLM 置換前提の設計)
- `data/*.json` — シード兼ローカルストア。reform_* はコミットされたシードが初期表示を担う

## コミュニケーション

- コミットメッセージ・UI 文言・ドキュメントは日本語ベース(コミット summary は英語 prefix `feat:`/`fix:` 等 + 日英どちらも可)
- ユーザー(開発者)は非エンジニアの経営企画視点。説明は結論から、専門用語は最小限に
