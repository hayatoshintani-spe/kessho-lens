---
description: ファイナンス分析（ROE分解・セグメント収益性・競合比較・バリュエーション）
argument-hint: <分析テーマ（例：競合ROE比較／自社セグメント収益性）>
allowed-tools: Read, Write, Grep, Glob, WebSearch, WebFetch
model: opus
---

cfo-analyst として、次のファイナンス論点を分析せよ: $ARGUMENTS

手順:
1. `advisory/knowledge/company-profile.md`（自社の確定数値・要確認）と `competitors.md` を読む。
2. 必要な数値を WebSearch/WebFetch で一次情報（決算短信・有報・適時開示・IR）から取得し、**出典と確認日を併記**。記憶の数値を事実として出さない。
3. 該当フレームで分析:
   - ROE分解（純利益率 × 総資産回転率 × レバレッジ）
   - セグメント収益性 / 競合比較表（ROE・営業利益率・海外比率・ライセンス比率）
   - バリュエーション（PER/PBR/EV-EBITDA）
4. 「数字が語る示唆（So what）」を必ず添える。楽観/悲観/基本の3シナリオで幅を示す。
5. 確定できた数値は `company-profile.md` の更新を提案。
6. 分析を `advisory/07_finance/YYYY-MM-DD-<テーマ>.md` に表形式で保存。

数値の裏取りを最優先。未確認は必ず「要確認」と明記せよ。
