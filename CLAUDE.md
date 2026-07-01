# CLAUDE.md — このリポジトリで Claude が守る規約

このリポジトリには2つのものが同居している。

1. **Tsuburaya Intelligence Brief**（`backend/` `frontend/` `shared/` `data/`）
   外部ニュースを円谷の経営示唆に翻訳する情報基盤アプリ（既存プロダクト）。詳細は `README.md`。
2. **AI経営参謀システム / 参謀本部**（`.claude/` `advisory/`）
   新任役員のための個人向けAI参謀群。詳細は `advisory/README.md`。

---

## 参謀本部（AI経営参謀システム）の使い方

### エージェント（`.claude/agents/`）
| エージェント | 役割 |
|---|---|
| `sanbo-cho` | 参謀長。毎朝ブリーフ・交通整理・統合 |
| `ip-strategist` | ウルトラマンIP成長戦略 |
| `d2c-crm-strategist` | D2C・CRM・体験事業の戦略仮説 |
| `b2b-dealmaker` | 大企業向け提案（ソフトバンク等） |
| `bizdev-evaluator` | 事業開発案件の評価（GO/NO-GO） |
| `cfo-analyst` | ファイナンス・ROE・株価・競合比較 |
| `org-talent-advisor` | 組織・人材・採用・評価 |
| `board-memo-writer` | 会長/社長/役員向け論点メモの清書 |
| `red-team` | 悪魔の代弁者（重い判断の前に必ず通す） |
| `decision-logger` | 意思決定ログの記録 |

### スラッシュコマンド（`.claude/commands/`）
`/morning-brief` `/issue-map` `/board-memo` `/deal-eval` `/proposal` `/ip-strategy` `/finance-check` `/org-review` `/decision-log`

### 参謀本部で作業するときの原則
- **必ず最初に `advisory/knowledge/` を読む**（特に `my-mandate.md`）。上司の立ち位置を外すと全出力が的外れになる。
- **事実 / 仮説 / 未確認を必ず区別する。** 数値は一次情報で裏取りし、出典と確認日を書く。**財務・市場数値を捏造しない。** 未確認は「要確認」と明記。
- **結論・推奨を先に。** 冗長さは上司の時間を奪う敵。出力はそのまま貼れる Markdown。
- 重い意思決定（投資・提携・組織変更・対外提案）は **red-team を通してから** 結論を出す。
- 成果物は `advisory/` の該当番号フォルダに保存する（各コマンドが保存先を指定）。
- 機密情報（人物評価・未公表数値・提携交渉）は `advisory/` 配下に置き、外部送信しない。git にコミットする前に機密性を確認する。

### 既存プロダクト側を触るときの原則
- `backend/` は FastAPI + JSON ストレージ（`backend/src/data/storage.py`）。データは原子的書き込み。
- `frontend/` は Next.js 14 App Router。
- 詳細な起動・デプロイ手順は `README.md` を参照。
