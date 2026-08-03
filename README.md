# Tsuburaya Intelligence Brief

**外部ニュース・規制動向・技術トレンドを、円谷の事業機会・リスク・経営論点に翻訳する情報基盤**

> 「読むためのニュース」ではなく「動くためのインテリジェンス」

---

## 何をするアプリか

毎日大量に流れる業界ニュース・規制動向・技術トレンドは、そのままではただの情報でしかありません。
このアプリは AI が以下の7カテゴリで監視・要約・解釈し、円谷の経営層・事業部長・経営企画に
「Daily Intelligence Brief」として届けます。

| カテゴリ | 監視対象 |
|---|---|
| IP・コンテンツ | 競合IP動向、配信プラットフォーム、コンテンツ消費トレンド |
| AI・エージェント | 生成AI、AIエージェント技術、コンテンツ生成への影響 |
| デバイス・通信 | XR/AR、5G/6G、新型デバイス |
| グローバル・地域 | 海外市場動向、地域別IP戦略 |
| 小売・MD・ライセンス | グッズ市場、ライセンス契約、リテール動向 |
| 規制・著作権 | 著作権法改正、AI生成物の法的扱い、肖像権 |
| 競合・資本市場 | エンタメ業界M&A、競合資金調達、評価額 |

各情報は **IntelCard**（事実 + 解釈 + 円谷への示唆 + 次アクション）として保存され、
6 種類の AI エキスパート（IP戦略家・グローバル展開・MD/ライセンス・AI技術トレンド・CFO・リスク管理）が
**AI Council Session** で論点を議論し、採用・保留・要調査の結論を出します。

---

## 主要機能

- **Daily Brief** — 経営層向け要約 + 重要トピックス + 次アクション + 識別リスク
- **IntelCard DB** — 重要度A〜D（経営アジェンダ / 事業部検討 / 共有 / 参考）で分類された記事カード
- **AI Council Session** — 6エキスパートによる戦略議論と編集者の結論
- **Watchlist** — カテゴリ別の監視キーワード・対象企業
- **Notion 連携** — IntelCard を社内 Notion DB に自動同期
- **Daily Brief 自動配信** — 毎朝 7:00 JST に Brief を経営層へ自動メール配信 (Resend)

---

## 技術構成

```
tsuburaya-intelligence-brief/
├── frontend/          # Next.js 14 (App Router)
├── backend/           # FastAPI (Python 3.11)
├── shared/            # 共通型定義 (TypeScript / Python)
├── data/              # JSON データ保存（intel_cards / briefs / council / watchlist）
├── render.yaml        # Render 用 Blueprint
└── .env.example       # 環境変数テンプレート
```

---

## ドキュメント

プロジェクト別のドキュメント索引は [`docs/README.md`](docs/README.md) を参照してください。
デプロイ手順（初心者向け）は [`docs/projects/tsuburaya-intelligence-brief/DEPLOY_JA.md`](docs/projects/tsuburaya-intelligence-brief/DEPLOY_JA.md) にあります。

---

## ローカル起動

### 前提条件
- Node.js 18+
- Python 3.11+

### 1. 環境変数

```bash
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY、Notion 連携を使うなら NOTION_API_KEY を設定
```

### 2. バックエンド

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- API: `http://localhost:8000`
- ドキュメント: `http://localhost:8000/docs`

### 3. フロントエンド

```bash
cd frontend
npm install
npm run dev
```

- 画面: `http://localhost:3000` → `/intel` に自動リダイレクト

---

## 本番デプロイ

### Frontend: Vercel

1. GitHub リポジトリを接続
2. 設定:
   - Framework Preset: **Next.js**
   - Root Directory: **`frontend`**
3. 環境変数: `NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com`

### Backend: Render

1. New Web Service → GitHub リポジトリを接続
2. 設定（または同梱の `render.yaml` で自動設定）:
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. 環境変数:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   NOTION_API_KEY=secret_...        # 任意
   NOTION_CARDS_DB_ID=...           # 任意
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

---

## 環境変数一覧

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `ANTHROPIC_API_KEY` | Claude API キー（カード・ブリーフ・AI会議生成） | 推奨（なしでもテンプレで動作） |
| `NOTION_API_KEY` | Notion Integration Token | 任意（Notion 連携時） |
| `NOTION_CARDS_DB_ID` | IntelCards DB の ID | 任意（Notion 連携時） |
| `RESEND_API_KEY` | Resend API キー（メール配信） | 任意（メール配信時） |
| `BRIEF_EMAIL_FROM` | メール差出人 (`"Name <addr>"` 形式可) | 任意（メール配信時） |
| `BRIEF_EMAIL_RECIPIENTS` | カンマ区切り宛先 | 任意（メール配信時） |
| `BRIEF_TIMEZONE` | Brief 生成タイムゾーン (既定: `Asia/Tokyo`) | 任意 |
| `CRON_SECRET` | クロンエンドポイント認証用シークレット | 自動配信時必須 |
| `NEXT_PUBLIC_API_BASE_URL` | バックエンド URL | 本番必須 |
| `ALLOWED_ORIGINS` | CORS 許可オリジン（カンマ区切り） | 本番推奨 |
| `FRONTEND_URL` | フロントエンド URL（メール本文リンクに使用） | メール配信時推奨 |

---

## API リファレンス

```
GET  /api/health                         # ヘルスチェック
GET  /api/intel/cards                    # IntelCard 一覧 (?category, ?importance, ?limit)
GET  /api/intel/cards/{card_id}          # 詳細
POST /api/intel/cards                    # 新規カード生成（記事タイトル/URL から）
GET  /api/intel/briefs                   # ブリーフ一覧（軽量サマリ）
GET  /api/intel/briefs/daily/{date}      # Daily Brief 詳細 + トップカード + 関連 Council
POST /api/intel/briefs/daily/build       # 指定日のカードから Daily Brief 生成
GET  /api/intel/council                  # AI 会議セッション一覧
GET  /api/intel/council/{session_id}     # 会議詳細
POST /api/intel/council                  # 新規 AI 会議生成
GET  /api/intel/meta                     # カテゴリ・エキスパート・重要度メタ
GET  /api/intel/watchlist                # ウォッチリスト
GET  /api/intel/notion/status            # Notion 接続状況
POST /api/intel/notion/sync              # カードを Notion に同期
POST /api/intel/notion/setup             # Notion DB を新規作成
GET  /api/intel/email/status             # メール配信設定の状況
POST /api/intel/email/test               # Brief をテスト送信 (dry_run=true でプレビューのみ)
POST /api/intel/cron/daily-brief         # 日次自動配信 (Bearer CRON_SECRET 認証)
```

OpenAPI 仕様: `http://localhost:8000/docs`

---

## データ構造

```
data/
├── intel_cards.json     # IntelCard（記事カード）
├── intel_briefs.json    # Daily / Weekly Brief
├── intel_council.json   # AI 会議セッション
└── intel_watchlist.json # カテゴリ別ウォッチリスト
```

JSON ファイルは原子的書き込み（temp → rename）で同時書き込みを防いでいます。
将来 Supabase / PostgreSQL に移行する場合は `backend/src/data/storage.py` の `Storage` クラスを差し替えるだけで済む構造です。

---

## Daily Brief 自動メール配信

### 仕組み

```
┌─────────────┐     ┌─────────────────────┐     ┌───────────────────┐
│ Vercel Cron │ ──→ │ /api/cron/daily-brief│ ──→ │ Backend /intel/cron│
│ 22:00 UTC   │     │ (Bearer CRON_SECRET) │     │ /daily-brief       │
└─────────────┘     └─────────────────────┘     └────────┬──────────┘
                                                          │
                          ┌───────────────────────────────┼─────────────────┐
                          ↓                               ↓                 ↓
                  Brief 生成 / 取得              Resend API 送信       配信ログ
                  (intel_briefs.json)         (BRIEF_EMAIL_RECIPIENTS)
```

毎朝 7:00 JST (=22:00 UTC 前日) に:
1. その日付の IntelCard を集めて Daily Brief を生成（既存なら再利用）
2. Brief を HTML/text 整形して Resend で配信
3. 当日カードが 0 件なら配信スキップ

### セットアップ

1. **Resend** で API キー取得 + 送信ドメイン認証 → https://resend.com/api-keys
2. バックエンドに環境変数を設定:
   ```
   RESEND_API_KEY=re_...
   BRIEF_EMAIL_FROM="Tsuburaya Intel <intel@yourdomain.com>"
   BRIEF_EMAIL_RECIPIENTS=ceo@example.com,strategy@example.com
   CRON_SECRET=$(openssl rand -hex 32)
   FRONTEND_URL=https://your-frontend.vercel.app
   ```
3. **Vercel Cron を使う場合**: Vercel プロジェクトに同じ `CRON_SECRET` を設定。`vercel.json` の crons が自動で `/api/cron/daily-brief` を毎朝呼び出す。
4. **Render Cron を使う場合**: `render.yaml` の `tsuburaya-intel-daily-brief` サービスに `BACKEND_URL` と `CRON_SECRET` を設定。
5. アプリの `/intel/delivery` ページでテスト送信して動作確認。

### 手動トリガ

```bash
# 今日の Brief をテスト送信
curl -X POST http://localhost:8000/api/intel/email/test \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'

# クロンを手で叩く
curl -X POST http://localhost:8000/api/intel/cron/daily-brief \
  -H "Authorization: Bearer $CRON_SECRET"
```

---

## API キーなしのフォールバック動作

`ANTHROPIC_API_KEY` がない場合:

- **カード生成**: テンプレートベースで `fact` / `interpretation` / `insight` を構造化
- **ブリーフ生成**: その日のカード重要度を集計してテンプレ要約を出力
- **AI 会議**: 各エキスパートのキー質問に基づくルールベース発言

UI とデータ構造は同じなので、まず API キーなしで全機能を試せます。

---

## ライセンス

MIT License
