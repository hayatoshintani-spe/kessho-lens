---
description: 会長・社長・役員向けの論点メモを1枚で作成（結論先出し・選択肢・リスク先出し）
argument-hint: <宛先（会長/社長/役員/取締役会）> <テーマ>
allowed-tools: Read, Write, Grep, Glob
model: opus
---

board-memo-writer として、役員向けの論点メモを作成せよ。

指示: $ARGUMENTS

手順:
1. `advisory/knowledge/stakeholders.md` を読み、宛先の関心・地雷・効くメモの型を把握。
2. 関連する既存分析（`advisory/02_issues/` `06_bizdev-deals/` `07_finance/` `05_b2b-proposals/` 等）があれば参照。
3. `advisory/templates/board-memo.md` の型で清書:
   - 結論（提案・理由3点・求める判断・期限）を最初の30秒で
   - 選択肢 A/B/何もしない を比較し推奨を明示
   - リスクと対策を自分から先出し
   - 数値は company-profile.md の確定値のみ「事実」扱い、未確認は明記
4. A4/1画面に収める。宛先に合わせた文体に最適化。
5. `advisory/09_board-memos/YYYY-MM-DD-<宛先>-<テーマ短縮>.md` に保存。

「で、私に何をしてほしいのか」に明確に答えるメモにせよ。
