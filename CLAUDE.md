# kessho-lens プロジェクトルール

## クリエイティブルール（必読）

スライド・提案書・報告書・HTML レポート・図解など、**ビジュアル資料を作成・生成する際は必ず `docs/CREATIVE_RULES.md` に従うこと**。
主要ポイント:

- 1スライド1メッセージ。結論を上部に太字1〜2行（50〜60文字以内）で明記
- メインカラー1色＋無彩色。区分は同系色の濃淡、重要でない要素はグレー
- 数字は大きく太くアクセント色、単位は小さく添える
- グラフには必ずメッセージ行とデータラベル。注記は※で右下
- 強調は最小限（重要箇所のみ太字/色）
- フッターに © 表記、ヘッダーは「英語ラベル＋日本語タイトル＋罫線」

詳細・レイアウトパターン集は `docs/CREATIVE_RULES.md` を参照。

## リポジトリ構成

- `frontend/` — Next.js (App Router) + Tailwind。ダッシュボード UI
- `backend/` — FastAPI。インテルカード生成・Notion 同期・メール配信
- 共有 UI コンポーネントは `frontend/components/ui/`（Button / Alert / BackLink / PageHeader / NoticeCard / Badge など）を使用し、ページ内での独自スタイル重複を避ける
