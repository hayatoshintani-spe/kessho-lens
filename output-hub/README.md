# アウトプット一覧 (PERSONAL-OUTPUT-HUB)

Claude Code で作った公開サイト・プロジェクト・資料を一覧で管理するためのハブサイト。
**静的HTML 1ファイル + JSON データ**だけで動くので、ビルド不要・どこにでも置けます。

## 構成

```
output-hub/
├── index.html   # サイト本体（CSS/JSインライン・編集不要）
├── sites.json   # 表示データ（ここだけ編集すればOK）
└── README.md
```

## サイトを追加する

`sites.json` の `sites` 配列に1件追記するだけです。

```json
{
  "name": "新しいサイト名",
  "icon": "🚀",
  "status": "公開中",
  "category": "カテゴリ名",
  "description": "このサイトが何かの説明。",
  "url": "https://example.com/",
  "repoPath": "フォルダ/プロジェクト名",
  "tags": ["Cloudflare Pages", "Next.js"]
}
```

| フィールド    | 必須 | 説明 |
|--------------|:--:|------|
| `name`        | ◯ | サイト名（カード見出し） |
| `icon`        |    | 絵文字アイコン（省略時 📄） |
| `status`      |    | `公開中` / `開発中` / `停止中` / `非公開`（バッジ色が変わる） |
| `category`    |    | 上部の絞り込みチップに自動で並ぶ |
| `description` |    | 説明文 |
| `url`         |    | 公開URL（クリックで別タブ） |
| `repoPath`    |    | リポジトリ内のパスなどメモ表示 |
| `tags`        |    | 技術タグ（配列） |

ヘッダーの文言は `sites.json` の `meta` で変更できます。

## ローカルで確認する

`index.html` は `sites.json` を fetch するため、**簡易サーバー経由**で開いてください。

```bash
cd output-hub
python3 -m http.server 8000
# → http://localhost:8000 を開く
```

## デプロイ

ビルド不要の静的サイトなので、`output-hub/` をそのまま公開できます。

- **Cloudflare Pages**: ルートディレクトリに `output-hub` を指定（ビルドコマンドなし）
- **Vercel / Netlify**: 同上、フレームワークプリセットは「Other / 静的」
- **GitHub Pages**: `output-hub/` を公開ディレクトリに

## 機能

- 名前・説明・タグ・パス横断のインクリメンタル検索
- カテゴリ絞り込みチップ（データから自動生成）
- 件数 / 公開中数 / カテゴリ数の集計サマリー
- ステータス別バッジ色・レスポンシブ対応
