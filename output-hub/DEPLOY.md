# デプロイ手順 — 限定公開（自分だけ）

このサイトは**自分だけが見られる限定公開**を前提にしています。
静的サイト単体に認証は持たせず、ホスティング側の機能で「自分以外は閲覧不可」を実現します。

多層防御の構成：
1. **認証**（本命）… Cloudflare Access もしくは Vercel パスワード保護で第三者を遮断
2. **検索エンジン除外**（保険）… `meta robots` / `robots.txt` / `_headers` の3点で noindex

> リポジトリには既に `robots.txt`・`_headers`・`<meta name="robots">` を同梱済みです。
> あなたの作業は「ホスティングに繋いで認証をONにする」だけです。

---

## 方式A（推奨）: Cloudflare Pages + Cloudflare Access

既存サイトが Cloudflare 系で揃っており、**個人利用は無料**。メール認証で自分だけ通せます。

### A-1. Cloudflare Pages でデプロイ
1. Cloudflare ダッシュボード → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
2. リポジトリ `hayatoshintani-spe/kessho-lens` を選択
3. ビルド設定：
   - **Production branch**: `claude/nifty-rubin-y2ezzs`（または main にマージ後 `main`）
   - **Framework preset**: `None`
   - **Build command**: （空欄）
   - **Build output directory**: `output-hub`
   - **Root directory (Advanced)**: `output-hub`
4. **Save and Deploy** → `https://<project>.pages.dev` が発行される

> ビルド不要の静的サイトなので、コマンドは不要です。

### A-2. Cloudflare Access で「自分だけ」に制限
1. Cloudflare ダッシュボード → **Zero Trust**（初回はチーム名を設定、Freeプランを選択）
2. **Access** → **Applications** → **Add an application** → **Self-hosted**
3. アプリ設定：
   - **Application name**: `output-hub`
   - **Session Duration**: 任意（例: 24h / 1週間）
   - **Application domain**: 上で発行された `*.pages.dev`（カスタムドメインを当てる場合はそれ）
4. **Policies** で1つ追加：
   - **Policy name**: `me-only`
   - **Action**: `Allow`
   - **Include**: `Emails` → `hayatoshintani@gmail.com`
5. 保存。以後このサイトを開くとメール宛のワンタイムコード（または Google ログイン）が要求され、**自分以外は弾かれます**。

---

## 方式B（代替）: Vercel + パスワード保護

Vercel をすでに使っているなら、こちらが最短です（Deployment Protection は Pro 機能の点に注意）。

1. Vercel → **Add New** → **Project** → リポジトリをインポート
2. 設定：
   - **Framework Preset**: `Other`
   - **Root Directory**: `output-hub`
   - **Build Command / Output**: 空欄（静的のためそのまま配信）
3. Deploy
4. **Settings** → **Deployment Protection** → **Password Protection**（または Vercel Authentication）を有効化し、パスワードを設定

> 無料枠で確実に隠したい場合は方式A（Cloudflare Access）を推奨します。

---

## 方式C（最小・保険のみ）: 認証なし＋推測困難URL

アカウント設定をしたくない場合の最低ライン。**強度は低い**ので機微情報は載せないこと。
- どこにデプロイしても可。URL を共有しない＋本リポジトリ同梱の `robots.txt`/`noindex` で検索流入を防ぐ。
- ただし URL を知っている人は閲覧できるため、「自分だけ」を厳密に満たすなら A か B を選ぶ。

---

## デプロイ後チェックリスト

- [ ] サイトが表示され、6件のカードが出る
- [ ] シークレットウィンドウ（未ログイン）でアクセスすると**認証画面で止まる**（方式A/B）
- [ ] 自分のメール/パスワードで通すと閲覧できる
- [ ] `https://<site>/robots.txt` が `Disallow: /` を返す
- [ ] ページソースに `<meta name="robots" content="noindex, nofollow">` がある
- [ ] `sites.json` に1件追記 → push → 自動再デプロイで反映される

---

## メモ：本番ブランチについて
今は作業ブランチ `claude/nifty-rubin-y2ezzs` にあります。運用を安定させるなら、
このブランチを `main` にマージし、Pages/Vercel の Production branch を `main` に設定するのがおすすめです（マージはご指示があれば対応します）。
