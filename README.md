# AI投資ファンド — kessho-lens

**4体のAI投資家が毎日議論し、思考し、学習する投資シミュレーションプラットフォーム**

> 「投資成績よりも、AIの思考・葛藤・反論・判断変更・学習が見えることを重視する」

---

## AIエージェント

| エージェント | 投資スタイル | 個性 |
|------|------|------|
| **BuffettAI** | 長期バリュー投資 | 配当・堀・割安を重視。「20年持てる株か？」が口癖 |
| **SorosAI** | マクロ投資・再帰性理論 | 政策・為替・市場の反射性を重視。「市場は常に間違っている」 |
| **LynchAI** | テンバガーハンター | 日常観察・PEGレシオ重視。「自分が理解できる株を買え」 |
| **FlatAI** | インデックス運用 | 効率的市場仮説信者。他3人を批判する役回り |

---

## 機能

- **AIダッシュボード** — 4エージェントのリアルタイム成績・損益・ランキング
- **AI投資会議ログ** — チャット形式で4人の議論・反論・決定を可視化
- **日次レポート** — AIが生成するMarkdownレポート（市場概況・判断根拠）
- **銘柄探索ログ** — 各AIがどのテーマ・銘柄を発見・検討したか
- **エージェント詳細** — 各AIの哲学・ポートフォリオ・過去の学びと失敗

---

## 技術構成

```
ai-investment-fund/
├── frontend/          # Next.js 14 (Vercel)
├── backend/           # FastAPI (Railway / Render)
├── shared/            # 共通型定義 (TypeScript / Python)
├── data/              # JSONデータ保存
├── vercel.json        # Vercel Cron設定
└── .env.example       # 環境変数テンプレート
```

---

## ローカル起動

### 前提条件
- Node.js 18+
- Python 3.11+

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/kessho-lens.git
cd kessho-lens
```

### 2. 環境変数の設定

```bash
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY などを設定
```

### 3. バックエンド起動

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

バックエンドAPI: `http://localhost:8000`  
APIドキュメント: `http://localhost:8000/docs`

### 4. フロントエンド起動

```bash
cd frontend
npm install
npm run dev
```

フロントエンド: `http://localhost:3000`

### 5. 日次シミュレーション手動実行

```bash
# APIエンドポイント経由
curl -X POST http://localhost:8000/api/run-daily

# または直接実行
cd backend
python src/simulation/daily_runner.py --mode daily
```

---

## 本番デプロイ

### Frontend: Vercel

1. [vercel.com](https://vercel.com) でアカウント作成
2. GitHubリポジトリを接続
3. 設定:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`（自動検出）
4. 環境変数を設定:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-backend.railway.app
   CRON_SECRET=your-secret-here
   ```
5. デプロイ → URLを取得

**Vercel Cron Jobs**（`vercel.json` で設定済み）:
- 毎日 01:00 UTC に `/api/trigger-daily` を呼び出し
- `CRON_SECRET` でバックエンドを保護

### Backend: Railway

1. [railway.app](https://railway.app) でアカウント作成
2. 「New Project」→「Deploy from GitHub repo」
3. 設定:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. 環境変数を設定:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   CRON_SECRET=your-secret-here
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```
5. デプロイ → バックエンドURLを取得
6. VercelのNEXT_PUBLIC_API_BASE_URLに設定

### Backend: Render (代替)

1. [render.com](https://render.com) でアカウント作成
2. 「New Web Service」→ GitHubリポジトリを接続
3. 設定:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - `render.yaml` で自動設定可能
4. 環境変数を設定（同上）

---

## GitHub連携と自動デプロイ

1. GitHubリポジトリを作成:
   ```bash
   git remote add origin https://github.com/your-username/kessho-lens.git
   git push -u origin main
   ```

2. Vercelにfrontendを接続（上記参照）

3. RailwayまたはRenderにbackendを接続（上記参照）

4. **自動デプロイ**: `main` ブランチにpushすると両サービスが自動でデプロイ

---

## 環境変数一覧

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `ANTHROPIC_API_KEY` | Claude API キー | 推奨（なしでもモックで動作） |
| `CRON_SECRET` | Cronエンドポイント保護 | 本番必須 |
| `NEXT_PUBLIC_API_BASE_URL` | バックエンドURL | 本番必須 |
| `ALPHA_VANTAGE_API_KEY` | 株価データAPI | オプション |
| `FINNHUB_API_KEY` | 追加市場データ | オプション |
| `DATABASE_URL` | Supabase接続URL | オプション（拡張時） |

---

## APIリファレンス

```
GET  /api/health              # ヘルスチェック
GET  /api/dashboard           # ダッシュボードデータ（全エージェント成績）
GET  /api/agents              # エージェント一覧
GET  /api/agents/{id}         # エージェント詳細 (buffett/soros/lynch/flat)
GET  /api/meetings            # 会議ログ一覧
GET  /api/meetings/{date}     # 指定日の会議ログ (YYYY-MM-DD)
GET  /api/reports             # 日次レポート一覧
GET  /api/reports/{date}      # 指定日のレポート (YYYY-MM-DD)
GET  /api/discovery           # 銘柄探索ログ
POST /api/run-daily           # 日次シミュレーション手動実行
POST /api/cron/run-daily      # Cron実行（CRON_SECRETで保護）
```

APIドキュメント（Swagger UI）: `http://localhost:8000/docs`

---

## 日次シミュレーション仕様

毎日1回（デフォルト: 01:00 UTC）以下を自動実行:

1. **市場環境取得** — Alpha Vantage / Finnhub からデータ取得（なければモックデータ）
2. **各AIの銘柄探索** — 4エージェントが独立して市場を分析
3. **AI投資会議** — Claude APIで4人の議論を生成（個性・反論・意見変更あり）
4. **最終売買判断** — 会議の結論に基づきトレード決定
5. **ポートフォリオ更新** — `data/portfolios.json` を更新
6. **会議ログ保存** — `data/meetings.json` に追加
7. **日次レポート生成** — Markdown形式で `data/daily_reports.json` に保存
8. **ダッシュボードデータ更新** — フロントエンドに反映

---

## APIキーなしでのデモ動作

`ANTHROPIC_API_KEY` がない場合、システムは自動的に以下にフォールバック:

- **会議生成**: 各エージェントの個性に基づくルールベース応答（日本語）
- **レポート生成**: テンプレートベースのMarkdownレポート
- **市場データ**: モックデータ（`data/` ディレクトリの初期データ）

---

## データ構造

```
data/
├── portfolios.json    # 4エージェントの現在ポートフォリオ
├── trades.json        # 売買履歴
├── meetings.json      # 会議ログ（チャット形式）
├── daily_reports.json # 日次レポート（Markdown）
├── discovery.json     # 銘柄探索ログ
└── memories.json      # エージェントの学習・記憶
```

---

## 開発

```bash
# バックエンドのテスト
cd backend
pytest

# フロントエンドのLint
cd frontend
npm run lint

# 型チェック
cd frontend
npx tsc --noEmit
```

---

## ライセンス

MIT License

---

*本プロダクトはAI投資シミュレーション用のフィクションです。実際の投資判断には使用しないでください。*
