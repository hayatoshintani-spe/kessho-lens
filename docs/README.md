# ドキュメント索引（プロジェクト別）

このアカウント（`hayatoshintani-spe`）の GitHub 上にある Markdown ドキュメントを、
プロジェクト（PJ）ごとに整理した索引です。

## 構成ルール

- プロジェクトごとに `docs/projects/<プロジェクト名>/` フォルダを作る
- リポジトリ全体の概要はルートの `README.md` に置く
- 新しいプロジェクトのドキュメントを追加するときは、下の一覧にも追記する

```
docs/
├── README.md                              # この索引
└── projects/
    └── <プロジェクト名>/                   # PJ ごとのドキュメント一式
```

---

## プロジェクト一覧

### 1. Tsuburaya Intelligence Brief（本リポジトリ / kessho-lens）

外部ニュース・規制動向・技術トレンドを、円谷の事業機会・リスク・経営論点に翻訳する情報基盤。

| ドキュメント | 内容 |
|---|---|
| [`../README.md`](../README.md) | アプリ概要・主要機能・技術構成・ローカル起動・本番デプロイ・API リファレンス |
| [`projects/tsuburaya-intelligence-brief/DEPLOY_JA.md`](projects/tsuburaya-intelligence-brief/DEPLOY_JA.md) | デプロイ手順（スマホ・初心者向け、Render + Vercel） |

---

## 備考

- 2026-08-03 時点で、このアカウントの GitHub リポジトリは `kessho-lens` の 1 つのみで、
  Markdown ファイルは上記 2 件がすべてです。
- 他プロジェクトの資料（提案書・マニュアル等）は GitHub 外（Claude アーティファクト / Notion）で
  管理されています。公開リポジトリのため、社外秘資料はここには置かないでください。
