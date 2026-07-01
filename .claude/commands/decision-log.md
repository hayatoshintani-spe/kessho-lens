---
description: 意思決定を記録（文脈・選ばなかった案・前提・確信度・成否指標）
argument-hint: <決定内容の要約>
allowed-tools: Read, Write, Edit, Grep, Glob
model: sonnet
---

decision-logger として、次の意思決定を記録せよ: $ARGUMENTS

手順:
1. `advisory/10_decision-log/` を確認し、本日のID連番を採番（`D-YYYYMMDD-nn`）。
2. `advisory/templates/decision-log-entry.md` の型で構造化。特に:
   - 選ばなかった案と理由（後の学びの源泉、省略しない）
   - 判断の前提（崩れたら見直すトリガー）
   - 確信度、成否を測る指標と時期
3. 詳細を `advisory/10_decision-log/<ID>.md` に保存。
4. `advisory/10_decision-log/decision-log.md` のインデックス表に1行追記（新しいものを上に）。
5. 事後レビューの時期を提案（四半期後など）。

上司の迷いや不確実性も美化せず記録せよ。「あえてやらないと決めたこと」も記録価値が高い。
