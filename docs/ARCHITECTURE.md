# アーキテクチャ設計メモ

このドキュメントは「なぜこの形になっているか」を残すためのもの。コードを読めば分かる「何をしているか」は書かない。

## 全体像

```
Google News RSS ──┐
手動カード入力 ────┤
                  ▼
       card_generator (claude-sonnet-4-6 / テンプレfallback)
                  │  IntelCard = 事実 + 解釈 + 円谷への示唆 + 次アクション
                  ▼
        data/intel_cards.json ⇄ Notion Cards DB (真の永続層)
                  │
                  ▼
       brief_generator → Daily Brief ⇄ Notion Briefs DB
                  │                └─ Resend で毎朝 7:00 JST メール配信
                  ▼
       council (6 AIエキスパート討議) / 改革ダッシュボード(actions・agenda・KPI)
```

## 主要な設計判断と理由

### 1. ストレージが「JSON ファイル + Notion」である理由

- **JSON**: 個人〜小規模チーム利用でスキーマ変更が頻繁なため、マイグレーション不要の JSON が開発速度で勝つ。書き込みは temp → rename の原子的書き込み + ファイル単位の threading.Lock。
- **Notion が真の永続層**: Render のファイルシステムはデプロイ/再起動で消える。Notion は (a) 永続化、(b) 社内共有 UI、(c) 手動編集の受け皿を 1 つで兼ねる。起動時に `restore_local_from_notion()` で JSON を再構築する(= JSON はキャッシュ)。
- Notion ページの `CardJSON` プロパティに **カード全体の JSON を丸ごと格納**しておき、復元時はそれをパースする(プロパティ→構造体の逆変換の劣化を防ぐ)。
- 将来 DB 化する場合は `Storage` クラスの差し替えのみで済む構造(呼び出し側は dict しか見ない)。

### 2. reform 系(actions / kpis / agendas)のストレージ

- 2026-07 時点では **JSON のみで Notion 同期なし**。つまり Render 再デプロイでユーザー編集分は消え、コミット済みシード(`data/reform_*.json`)に戻る。既知の制限であり、対応は ROADMAP の「reform データの Notion 永続化」参照。
- KPI スナップショットは kpi_id ごとに**最新 1 件のみ**保持(upsert)。履歴が必要になったら追記型に変える。
- 週次アジェンダは week_of(月曜日付)ごとに 1 件 upsert。
- KPI の「定義」(`KPI_DEFS`)はフロント `reform-taxonomies.ts` のハードコード、バックエンドは「実績値スナップショット」だけ持つ。定義とデータの分離は意図的(定義変更はデプロイで良い)。

### 3. 経営インパクトスコアがフロントエンド実装である理由

`frontend/lib/impact-score.ts` はルールベースの純粋関数。理由:
- 算出根拠を rationale で経営陣に説明できる(LLM だとブラックボックス化)
- カード一覧を取得するだけでダッシュボードが組めて、バックエンド往復もトークン費用もゼロ
- 将来 LLM 算出に置き換える時は、同じ `ManagementImpact` 型を返すバックエンド API を生やして差し替える設計(ROADMAP 参照)

テーマ分類(`KEYWORD_TO_THEMES`)・レンズ分類も同様に正規表現ベース。**Python 側に移植しないこと** — 二重管理になる。移す時は「フロントから削除して API に一本化」が条件。

### 4. cron が三重になっている理由(歴史的経緯)

1. 最初 Vercel Cron のみ → Hobby プランは実行保証が弱く、環境変数の伝播も不安定
2. Render Cron を追加検討 → 無料プランでは cron サービス不可で Blueprint から削除(commit 1428864)
3. **GitHub Actions を一次スケジューラに**(commit 4b01823)。Vercel Cron は保険として残置

daily-brief 実行は**即 202 を返して BackgroundTask で処理**する。Vercel の 10 秒タイムアウト、Render の リクエストタイムアウトの両方を回避するため。進捗はプロセス内メモリの `_DAILY_BRIEF_STATE` を `/api/intel/cron/status` で公開し、フロントが 4 秒間隔ポーリング。マルチワーカーにすると壊れる(uvicorn 1 worker 前提)。

### 5. コスト暴走ガード

Anthropic API の従量課金事故を防ぐ多層防御:
- `DAILY_BRIEF_MAX_RUNS_PER_DAY`(既定 5)— 24h スライディングウィンドウでの実行回数制限(プロセス内メモリ。再起動でリセットされるのは許容)
- `running` 中の二重起動拒否
- news_ingest の 1 回あたりカード生成数上限
- フロント「今すぐ更新」は window.confirm で費用目安(¥10〜30)を明示
- `INTEL_AUTO_INGEST=0` で自動ニュース取得を殺せる

### 6. API キーなしフォールバック

`ANTHROPIC_API_KEY` 未設定でも全機能がテンプレ/ルールベースで動く。これは (a) デモ・開発の摩擦をなくす、(b) API 障害時にアプリ全体が死なない、(c) テストが外部依存なしで書ける、の 3 点で意図的に維持している。**新機能も必ずフォールバックを実装すること。**

### 7. CORS / 認証

- CORS: localhost + `FRONTEND_URL` + `ALLOWED_ORIGINS` + `*.vercel.app` 等の正規表現。閲覧系 API は認証なし(社内限定利用前提の割り切り)。
- 書き込み系で費用が発生する cron 系のみ `CRON_SECRET` Bearer 認証。
- 認証強化(Basic 認証 / Vercel Password / IP 制限)は必要になったら Vercel/Render 側の機能で被せる方針。

## デプロイ

- Frontend: Vercel(`frontend/` を Root Directory に。リポジトリ直下の `vercel.json` は rewrite + cron 用)
- Backend: Render Web Service starter プラン(常時起動。free だとスリープ→毎朝の cron が cold start でタイムアウトするため有料化した。commit 2bef782)
- 環境変数一覧は README 参照。`CRON_SECRET` は GitHub Secrets / Vercel / Render の 3 箇所で同一値。

## 既知の制限(2026-07-12 時点)

1. reform 系データは Notion 永続化なし(再デプロイでシードに戻る)
2. `_DAILY_BRIEF_STATE` / 実行回数カウンタはプロセス内メモリ(再起動で消える。単一 worker 前提)
3. KPI 実績は手動入力/シードのみ(Sheets/Notion 自動取得は未実装)
4. 認証は cron 系のみ。閲覧 API は URL を知っていれば誰でも見られる
5. インパクトスコアはルールベース v1(キーワード正規表現。精度は限定的)
