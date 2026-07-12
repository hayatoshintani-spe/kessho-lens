# ROADMAP — 次期機能の実装仕様

各仕様は「このドキュメント + CLAUDE.md + ARCHITECTURE.md を読めば、追加の設計判断なしで実装に入れる」粒度で書いてある。実装時は 1 機能 = 1 ブランチ = 1 PR とし、必ず backend pytest / frontend build を通すこと。

優先順は上から。

---

## 1. reform データの Notion 永続化(優先度: 高)

### 背景
`data/reform_actions.json` / `reform_kpis.json` / `reform_agendas.json` は Render の揮発性ディスク上にあり、**再デプロイでユーザーの編集が消えてシードに戻る**(ARCHITECTURE.md「既知の制限」1)。カード/ブリーフと同じく Notion を真の永続層にする。

### スコープ
- Actions のみ対象(KPI・アジェンダは編集頻度が低く、次段階でよい)
- `notion_sync.py` に追加: `sync_action(action)` / `restore_local_actions_from_notion()`
- 環境変数: `NOTION_ACTIONS_DB_ID`(未設定なら全て no-op、既存動作を壊さない)
- DB プロパティ: Title(title), ActionID(rich_text), Owner(rich_text), Deadline(date), Status(select), Priority(select), UpdatedAt(date), **ActionJSON(rich_text: アクション全体の JSON)**
- 復元はカードと同じ方式: ActionJSON をパースして dict を再構築(プロパティ逆変換はしない)
- 書き込みタイミング: `POST/PATCH/DELETE /api/intel/reform/actions*` の成功後に同期(失敗しても API 自体は成功を返し、エラーはレスポンスの `notion` フィールドに載せる — カード作成と同じパターン)
- `backend/main.py` startup の復元処理に actions を追加
- `POST /api/intel/notion/setup-actions` で DB 自動作成(setup-briefs と同じパターン)

### 受け入れ条件
- [ ] NOTION_ACTIONS_DB_ID 未設定で全 API が現状どおり動く(pytest 既存 21 件がパスし続ける)
- [ ] 設定済み環境で: アクション作成 → Notion にページが出来る → ローカル JSON を消して再起動 → アクションが復元される
- [ ] 削除はアーカイブ(Notion ページの archived=true)として同期される
- [ ] pytest: notion 無効時に sync_action が no-op を返すテストを追加

---

## 2. 週次 Brief(優先度: 高)

### 背景
`brief_generator.py` に `build_weekly_brief` が既に存在する(未配線)。経営会議は週次なので、週の振り返り + 週次アジェンダとの連結が価値になる。

### スコープ
- `POST /api/intel/briefs/weekly/build` — body: `{ "week_of": "YYYY-MM-DD" }`(月曜)。その週 7 日分のカードから週次 Brief を生成・保存(brief_type="weekly"、date=week_of で upsert)
- `GET /api/intel/briefs/weekly/{week_of}` — 詳細取得
- 生成内容に「今週の保存済みアジェンダ(`Storage.get_reform_agenda(week_of)`)との対応」セクションを含める: アジェンダ論点ごとに、関連カードが今週何件増えたか
- フロント: `/intel/brief/[date]` は brief_type を見て週次表示に対応。`/intel/agenda` に「週次ブリーフを見る」導線
- メール配信: 金曜 17:00 JST に GitHub Actions で cron 追加(`/api/intel/cron/weekly-brief`、CRON_SECRET 認証、日次と同じ 202+status 方式・同じ実行回数ガードを別カウンタで)

### 受け入れ条件
- [ ] カード 0 件の週は skipped(日次と同じ挙動)
- [ ] 同じ week_of で再生成すると上書き(重複しない)
- [ ] API キーなしでもテンプレ生成で動く
- [ ] pytest: build → get → 再 build 上書き、cron 認証、の 3 テスト以上

---

## 3. 経営インパクトスコア v2(LLM 算出、優先度: 中)

### 背景
現行はフロントのルールベース(`frontend/lib/impact-score.ts`)。キーワード正規表現なので精度が頭打ち。LLM でスコアリングし、ルールベースはフォールバックに降格する。

### スコープ
- カード生成時(`card_generator.build_intel_card`)に、同じ Claude 呼び出しの出力へ `management_impact` を追加させる(**追加 API コールはしない**。既存プロンプトの JSON スキーマに impact フィールドを足す)
- スキーマは `frontend/lib/reform-types.ts` の `ManagementImpact` と同一: `{ score, components{8軸}, recommendation, rationale }`
- カード dict に `management_impact` フィールドを保存。API キーなし時は付けない(フロントでルールベース計算にフォールバック)
- フロント `enrichCards`: `card.management_impact` があればそれを使い、なければ現行 `computeImpact(card)`
- **`impact-score.ts` は削除しない**(フォールバック + 過去カード用)

### 受け入れ条件
- [ ] 新規カード(API キーあり)に management_impact が入り、ダッシュボード並び順に反映される
- [ ] 過去カード・キーなし環境は現状と同一表示
- [ ] rationale が日本語 1 行で入る(経営陣への説明性の維持)
- [ ] pytest: フォールバックカードに management_impact が無いこと、フロントは tsc が通ること

---

## 4. アクション自動提案(カード → ReformAction、優先度: 中)

### 背景
IntelCard には既に `actions[]`(who/what/priority)が入っているが、アクション管理(`/intel/actions`)とは切れている。「シグナル → 打ち手」の接続がこのプロダクトの本懐。

### スコープ
- `POST /api/intel/reform/actions/from-card` — body: `{ "card_id": "..." }`。カードの `actions[]` を ReformAction のドラフトに変換して返す(**保存はしない**。フロントで編集して既存 POST で保存)
- 変換規則: who→owner、what→title、priority: urgent→urgent / this_week→high(期限=今日+7日) / this_month→medium(期限=今日+30日) / watch→low(期限=今日+30日)。card_id をセット
- フロント: カード詳細ページ(`/intel/cards/[id]`)に「アクション化」ボタン → 変換結果をプレフィルした作成フォーム(モーダルか /intel/actions への遷移)

### 受け入れ条件
- [ ] 既に同じ card_id + title のアクションが存在する場合は draft に `duplicate: true` を付ける
- [ ] カードに actions が無い場合は空配列を返す(エラーにしない)
- [ ] pytest: 変換規則(priority→期限)のテスト

---

## 5. KPI 実績の半自動更新(優先度: 低)

### スコープ(最小版)
- `/intel/kpi` ページに手動編集 UI: KPI カードクリック → value / target / period / status を編集 → 既存 `PUT /api/intel/reform/kpis/{kpi_id}` で保存
- status は「value/target 比で自動提案、手動上書き可」: >=95% on_track / >=70% at_risk / <70% off_track
- Sheets / Notion 自動取得は、手動運用が回り始めてから別仕様として起こす(作り込まない)

### 受け入れ条件
- [ ] 編集 → リロードで値が保持される(Render 再起動では消える。制限は仕様 1 で解消)
- [ ] 不正値(負の target 等)はフロントでバリデーション

---

## 6. 閲覧保護(優先度: 状況次第)

社外公開が視野に入ったら着手。方式は「アプリに実装しない」を第一候補とする:
- Vercel: Password Protection(Pro)または Cloudflare Access を前段に
- Render API: `ALLOWED_ORIGINS` を本番ドメインのみに絞る + 簡易 API キー(`X-App-Key` ヘッダ、環境変数照合)をフロントの fetch ラッパー(`intel-api.ts` / `reform-api.ts` の request 関数)に足す
- 実装するなら受け入れ条件: キー無し閲覧 API 呼び出しが 401 / フロント経由は透過的に成功 / cron・health は現状維持

---

## 実装しないと決めたこと(蒸し返さない)

- **インパクトスコアの Python 移植**: フロント/バックの二重管理になる。移すなら「API に一本化してフロントから削除」のみ可(ARCHITECTURE.md 3)
- **JSON → RDB 移行**: 現ボリュームでは不要。Notion 永続化で足りる。移行条件は「複数ユーザー同時編集が必要になった時」
- **マルチ worker 化**: `_DAILY_BRIEF_STATE` がプロセス内メモリである限り不可(uvicorn 1 worker 前提)
