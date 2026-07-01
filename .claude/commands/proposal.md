---
description: 大企業向けの提案書を作成（ソフトバンク等、相手主語で刺さる提案）
argument-hint: <提案先企業> <提案の狙い>
allowed-tools: Read, Write, Grep, Glob, WebSearch, WebFetch
model: opus
---

b2b-dealmaker として、次の相手への提案を作成せよ: $ARGUMENTS

手順:
1. `advisory/knowledge/ultraman-ip.md`（持ち込めるIP資産）と `my-mandate.md` を読む。
2. WebSearch で提案先の最新の中期戦略・課題・直近の打ち手を調べ、相手の文脈を把握。
3. `advisory/templates/proposal.md` の型で作成:
   - エグゼクティブサマリ（相手の経営会議で1枚で通る水準、相手主語）
   - Why you（相手の便益・数値イメージ）/ Why us（我々の便益）
   - 座組（役割・レベニューシェア・権利）/ 入り口を軽く（PoCから）
   - 相手の懸念を先回りしたQ&A
4. 過大約束をしない。効果・リーチは前提を明示し確実に守れる範囲で。
5. `advisory/05_b2b-proposals/YYYY-MM-DD-<相手>.md` に保存。

我々が売りたいものでなく、相手が欲しいものから逆算して書け。
