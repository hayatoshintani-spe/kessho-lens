# CLAUDE.md

## ビジュアルアウトプットのデザイン統一

スライド（pptx）・HTML アーティファクト・レポート・図版など、
**視覚的なアウトプットはすべて `docs/design/DESIGN_SYSTEM.md`
（デザインシステム「HENSHIN」）に従うこと。**

- 漆黒ベース（`0A0C11`）×ウルトラレッド（`C8102E`）×カラータイマー青（`2EA8E0`）のシネマティック・ダーク
- 和文 Yu Gothic / 英字 Arial・Arial Black、ゴーストタイポとガラスカード、赤グローの発光表現
- 再利用アセット・生成スクリプトは `tools/design-kit/`
- スライドの基準実装は `tools/design-kit/decks/rokid-ultraman-pitch.js`（新デッキはこれを複製して作る）

## リポジトリ概要

Tsuburaya Intelligence Brief — 外部ニュースを円谷の事業機会・リスクに翻訳する情報基盤。
- `frontend/` Next.js 14 / `backend/` FastAPI / `data/` JSON ストア
- `docs/proposals/` 提案書類（Rokid×ウルトラマン案件など）
- 提案・分析のアウトプットは `data/intel_cards.json`（IntelCard）・`data/intel_council.json`（AI Council）とも整合させる
