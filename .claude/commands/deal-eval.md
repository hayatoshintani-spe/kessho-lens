---
description: 事業開発案件を投資委員会目線で評価（GO/NO-GO・撤退基準つき）
argument-hint: <案件名と概要／資料へのパス>
allowed-tools: Read, Write, Grep, Glob, WebSearch, WebFetch
model: opus
---

bizdev-evaluator として、次の案件を評価せよ: $ARGUMENTS

手順:
1. `advisory/knowledge/my-mandate.md` `ultraman-ip.md` を読み、戦略適合の基準を把握。
2. `advisory/templates/deal-eval.md` の6軸で評価:
   戦略適合 / 市場・機会 / ユニットエコノミクス / リスク / レッドチーム所見 / 判定と条件。
3. **red-team を必ず起用**し、最も可能性の高い失敗シナリオを「6. レッドチーム所見」に反映。
4. ユニットエコノミクスは前提を明示、未確認は「要検証」。悲観ケースも試算。
5. 判定を1つに絞る（GO/条件付きGO/HOLD/NO-GO）。**KO基準（撤退ライン）を必ず明記**。
6. `advisory/06_bizdev-deals/YYYY-MM-DD-<案件名>.md` に保存。
7. 上司が判断したら `/decision-log` で記録するよう促す。

熱狂に流されず、しかし筋の良いリスクは取る規律で評価せよ。
