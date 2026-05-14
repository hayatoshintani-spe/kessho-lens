"""
モックデータ - リッチな日本語コンテンツ
APIキーなしでもデモが可能なように、リアルな会話・レポートを含む
"""

from datetime import datetime, timedelta

# 今日の日付を基準にモックデータを生成
_TODAY = "2026-05-14"
_YESTERDAY = "2026-05-13"
_DAY_BEFORE = "2026-05-12"
_THREE_DAYS_AGO = "2026-05-11"

# ポートフォリオの初期データ
INITIAL_PORTFOLIOS = {
    "buffett": {
        "agent_id": "buffett",
        "cash": 8_500_000,
        "total_value": 50_000_000,
        "holdings": [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "shares": 150,
                "avg_cost": 170.00,
                "current_price": 189.50,
                "value": 28_425,
                "gain_pct": 11.47,
            },
            {
                "ticker": "KO",
                "name": "Coca-Cola Co",
                "shares": 500,
                "avg_cost": 58.00,
                "current_price": 62.30,
                "value": 31_150,
                "gain_pct": 7.41,
            },
            {
                "ticker": "JNJ",
                "name": "Johnson & Johnson",
                "shares": 200,
                "avg_cost": 155.00,
                "current_price": 148.70,
                "value": 29_740,
                "gain_pct": -4.06,
            },
            {
                "ticker": "BRK.B",
                "name": "Berkshire Hathaway B",
                "shares": 100,
                "avg_cost": 350.00,
                "current_price": 392.10,
                "value": 39_210,
                "gain_pct": 12.03,
            },
        ],
        "performance": {
            "total_return_pct": 8.2,
            "daily_pnl": 42_500,
            "weekly_pnl": 180_000,
            "monthly_pnl": 720_000,
        },
    },
    "soros": {
        "agent_id": "soros",
        "cash": 12_000_000,
        "total_value": 50_000_000,
        "holdings": [
            {
                "ticker": "NVDA",
                "name": "NVIDIA Corp",
                "shares": 80,
                "avg_cost": 480.00,
                "current_price": 875.20,
                "value": 70_016,
                "gain_pct": 82.33,
            },
            {
                "ticker": "GLD",
                "name": "SPDR Gold ETF",
                "shares": 300,
                "avg_cost": 180.00,
                "current_price": 215.40,
                "value": 64_620,
                "gain_pct": 19.67,
            },
            {
                "ticker": "UUP",
                "name": "Invesco DB USD Index",
                "shares": 1000,
                "avg_cost": 28.50,
                "current_price": 27.10,
                "value": 27_100,
                "gain_pct": -4.91,
            },
        ],
        "performance": {
            "total_return_pct": 18.7,
            "daily_pnl": 95_200,
            "weekly_pnl": 390_000,
            "monthly_pnl": 1_580_000,
        },
    },
    "lynch": {
        "agent_id": "lynch",
        "cash": 5_200_000,
        "total_value": 50_000_000,
        "holdings": [
            {
                "ticker": "SBUX",
                "name": "Starbucks Corp",
                "shares": 300,
                "avg_cost": 92.00,
                "current_price": 88.40,
                "value": 26_520,
                "gain_pct": -3.91,
            },
            {
                "ticker": "NKE",
                "name": "Nike Inc",
                "shares": 250,
                "avg_cost": 95.00,
                "current_price": 107.80,
                "value": 26_950,
                "gain_pct": 13.47,
            },
            {
                "ticker": "COST",
                "name": "Costco Wholesale",
                "shares": 60,
                "avg_cost": 520.00,
                "current_price": 728.50,
                "value": 43_710,
                "gain_pct": 40.10,
            },
            {
                "ticker": "TSLA",
                "name": "Tesla Inc",
                "shares": 100,
                "avg_cost": 220.00,
                "current_price": 248.90,
                "value": 24_890,
                "gain_pct": 13.14,
            },
        ],
        "performance": {
            "total_return_pct": 12.4,
            "daily_pnl": 28_900,
            "weekly_pnl": 210_000,
            "monthly_pnl": 890_000,
        },
    },
    "flat": {
        "agent_id": "flat",
        "cash": 3_000_000,
        "total_value": 50_000_000,
        "holdings": [
            {
                "ticker": "SPY",
                "name": "SPDR S&P 500 ETF",
                "shares": 120,
                "avg_cost": 480.00,
                "current_price": 528.70,
                "value": 63_444,
                "gain_pct": 10.15,
            },
            {
                "ticker": "QQQ",
                "name": "Invesco QQQ Trust",
                "shares": 100,
                "avg_cost": 400.00,
                "current_price": 458.20,
                "value": 45_820,
                "gain_pct": 14.55,
            },
            {
                "ticker": "VTI",
                "name": "Vanguard Total Market ETF",
                "shares": 200,
                "avg_cost": 220.00,
                "current_price": 248.10,
                "value": 49_620,
                "gain_pct": 12.77,
            },
        ],
        "performance": {
            "total_return_pct": 11.8,
            "daily_pnl": 35_100,
            "weekly_pnl": 195_000,
            "monthly_pnl": 810_000,
        },
    },
}

# ミーティングログのモックデータ
MOCK_MEETINGS = [
    {
        "date": _TODAY,
        "participants": ["BuffettAI", "SorosAI", "LynchAI", "FlatAI"],
        "summary": "NVIDIAの急騰とFRBの利下げ観測を受けた投資戦略議論。ソロスが強気な姿勢を維持する中、バフェットは過熱感を警戒。リンチがスターバックスの復活に注目、フラットは全員のアクティブ戦略を批判。",
        "market_theme": "AI半導体バブルとマクロ転換点",
        "key_decisions": [
            "NVDA: ソロス追加買い、バフェット利確検討（合意不成立）",
            "KO: バフェット保有継続、他全員スキップ",
            "COST: リンチ強気継続、フラットはSPYへの乗り換えを推奨",
            "金（GLD）: ソロスとバフェットが珍しく一致 - 保有継続",
        ],
        "messages": [
            {
                "agent": "SorosAI",
                "time": "09:00",
                "content": "おはようございます。本日の市場を見てください。NVIDIAが昨日比+8.3%、AI関連銘柄全体に資金が流入しています。これは私が2ヶ月前に予測したマクロの転換点そのものです。FRBの利下げ観測と重なり、リスクオンの流れは加速します。",
                "type": "opening",
            },
            {
                "agent": "BuffettAI",
                "time": "09:03",
                "content": "ジョージ、少し冷静になってください。NVIDIAのPERは現在65倍です。20年後にこの会社が今の価格を正当化できるか考えてみてください。私がコカコーラを買った時、誰もが「つまらない」と言いました。しかし配当は35年間増え続けています。それが真の価値です。",
                "type": "debate",
            },
            {
                "agent": "LynchAI",
                "time": "09:07",
                "content": "ウォーレン、でも考えてみてください。先週、私は5つのコーヒーショップでNVIDIAのGPUについて話す客の会話を聞きました。一般人がNVIDIAを知っている。コストコの棚にはAI搭載家電が並んでいる。これはテンバガーの匂いがします。PEGレシオを見ると成長を考慮すればまだ割安かもしれない。",
                "type": "debate",
            },
            {
                "agent": "FlatAI",
                "time": "09:10",
                "content": "3人とも聞いてください。データを見てください。過去20年間で、S&P500に勝ったアクティブファンドマネージャーは15%未満です。皆さんが今日している議論、NVIDIAを買うべきか否か、これは全て無駄な作業です。SPYを買って寝ていれば、全員のパフォーマンスを上回ります。",
                "type": "rebuttal",
            },
            {
                "agent": "SorosAI",
                "time": "09:13",
                "content": "フラット、効率的市場仮説は美しい理論ですが、現実は違います。市場参加者の認識が現実を変える、それが再帰性理論です。今、市場はAIの価値を『過少評価』から『正当評価』へと移行している最中です。この流れに乗るのがマクロ投資家の仕事です。私はNVDAを20株追加買いします。",
                "type": "proposal",
            },
            {
                "agent": "BuffettAI",
                "time": "09:17",
                "content": "私はNVDAの利確を半分検討しています。ただし、コカコーラとジョンソン・エンド・ジョンソンは絶対に動かしません。JNJが若干下落していますが、129年の配当継続実績を持つ企業です。これを売る理由はありません。ただ...ジョージのNVDA追加については反対します。",
                "type": "rebuttal",
            },
            {
                "agent": "LynchAI",
                "time": "09:20",
                "content": "コストコについて話させてください。昨日、会員更新率が93.1%と発表されました。これは過去最高です。お客さんは年会費を払い続けています。なぜか？価値があるからです。私はCOSTの目標価格を850ドルに引き上げます。スターバックスは新CEOの施策が効いてきています。もう少し待ちます。",
                "type": "proposal",
            },
            {
                "agent": "FlatAI",
                "time": "09:24",
                "content": "ピーター、コストコの個別分析に時間を使っている間に、VTIは今日+0.6%動きました。年換算すると、皆さんの銘柄選択のアルファ、つまり市場超過リターン、は統計的に有意ではありません。私はQQQをリバランスして終わりです。",
                "type": "rebuttal",
            },
            {
                "agent": "SorosAI",
                "time": "09:28",
                "content": "フラット、君の理論は正しい...平均では。しかし私は平均ではない。再帰性を理解している投資家は市場を先読みできます。為替を見てください。ドル安トレンドが始まっています。これはゴールドと新興国株式にとって強気シグナルです。GLDの保有を増やすことを提案します。",
                "type": "proposal",
            },
            {
                "agent": "BuffettAI",
                "time": "09:31",
                "content": "ゴールドについては、珍しくジョージに同意します。ただし私の理由は違います。地政学的リスクのヘッジとして、ポートフォリオの5%をゴールドで持つことは理にかなっています。GLDの保有は継続します。",
                "type": "decision",
            },
            {
                "agent": "LynchAI",
                "time": "09:34",
                "content": "テスラについて一言。先週、テスラのショールームが混んでいました。Model 3の新型を見に来ている若い人たちが多かった。株価は最近低迷していますが、実際の製品への関心は高い。PEGを計算すると...成長率を考慮すればまだ面白い水準です。",
                "type": "proposal",
            },
            {
                "agent": "FlatAI",
                "time": "09:37",
                "content": "ピーター、ショールームの混雑度は投資判断の根拠になりません。それはアンカリングバイアスです。EV市場全体への分散投資ならQQQで十分カバーできます。個別銘柄を選ぶことは、運を実力と勘違いすることです。",
                "type": "rebuttal",
            },
            {
                "agent": "SorosAI",
                "time": "09:40",
                "content": "本日の結論です。NVDA追加買い20株を実行します。GLD保有継続。ドル指数が下落トレンドなら、UUPのポジションを減らすことも検討します。マクロの風向きが変わりました。",
                "type": "decision",
            },
            {
                "agent": "BuffettAI",
                "time": "09:42",
                "content": "私の判断：KO・BRK.B・JNJ・AAPL全ポジション保有継続。NVDAの半分利確は今週中に判断します。焦る必要はありません。良い企業は20年待てます。",
                "type": "decision",
            },
            {
                "agent": "LynchAI",
                "time": "09:44",
                "content": "COST目標850ドルに引き上げ。TSLAは様子見継続。SBUX、もう2週間待ちます。日常の観察を続けます。",
                "type": "decision",
            },
            {
                "agent": "FlatAI",
                "time": "09:46",
                "content": "QQQ・SPY・VTI リバランス完了。本日の会議は以上です。皆さんのアクティブ運用の結果を来月比較しましょう。データは正直です。",
                "type": "decision",
            },
        ],
    },
    {
        "date": _YESTERDAY,
        "participants": ["BuffettAI", "SorosAI", "LynchAI", "FlatAI"],
        "summary": "日銀の追加利上げ観測と米雇用統計の強さを受けた議論。円高トレンドへの対応、日本株への投資機会を巡り激論。",
        "market_theme": "日銀政策転換と日本株の夜明け",
        "key_decisions": [
            "日本株（7203：トヨタ）: リンチ新規買い検討",
            "為替ヘッジ: ソロスがドル円ショートを提案",
            "NVDA: 前日の急騰を受けてソロス利益確定20株",
            "SPY: フラットが通常のリバランス実施",
        ],
        "messages": [
            {
                "agent": "SorosAI",
                "time": "09:00",
                "content": "重要な動きがあります。日銀が追加利上げを示唆しました。ドル円が148円から142円まで急落しています。これは私の再帰性モデルが6ヶ月前から予測していた転換点です。円高は日本株の外国人投資家にとっては逆風ですが、日本の内需企業には追い風です。",
                "type": "opening",
            },
            {
                "agent": "BuffettAI",
                "time": "09:04",
                "content": "日本市場については以前から注目しています。トヨタ、三菱商事、伊藤忠。PBR1倍以下の優良企業がまだあります。ただし為替リスクは慎重に見なければなりません。私はドルベースで投資しているので、円高は直接的にリターンを押し上げます。",
                "type": "debate",
            },
            {
                "agent": "LynchAI",
                "time": "09:08",
                "content": "先週、東京に出張に行ってきました。渋谷のスクランブル交差点、あの活気は変わっていない。トヨタのショールームには新型の電気自動車が並んでいました。インバウンドで賑わっている。これは...テンバガー候補かもしれません。7203は面白い。",
                "type": "debate",
            },
            {
                "agent": "FlatAI",
                "time": "09:11",
                "content": "日本株への投資は為替リスク、流動性リスク、情報非対称性の三重リスクです。EWJ（iシェアーズ MSCI ジャパンETF）で十分な分散が得られます。個別株を選ぶ必要はありません。",
                "type": "rebuttal",
            },
            {
                "agent": "SorosAI",
                "time": "09:15",
                "content": "フラットの言うEWJも選択肢ですが、為替ヘッジがありません。私はドル円のショートポジションを小さく取ります。円安から円高への転換、これは大きなマクロトレードです。1985年のプラザ合意以来の転換点になる可能性があります。",
                "type": "proposal",
            },
            {
                "agent": "BuffettAI",
                "time": "09:19",
                "content": "為替のタイミングを当てようとするのは危険です。私は企業の本質的価値に集中します。ただ、日本の大手商社の株主還元改善は本物です。バークシャーが日本の商社株を保有し続けているのには理由があります。",
                "type": "rebuttal",
            },
            {
                "agent": "LynchAI",
                "time": "09:22",
                "content": "7203（トヨタ）のPEGレシオを計算しました。EV投資を加速しながらも、ハイブリッド技術でキャッシュフローを生み出している。PER8.5倍、成長率5%で...まだ割安です。新規買いを検討します。",
                "type": "proposal",
            },
            {
                "agent": "SorosAI",
                "time": "09:25",
                "content": "昨日のNVDAの急騰で、私のポジションが予想以上に大きくなりました。リスク管理の観点から20株利益確定します。利益は確定しなければ意味がない。",
                "type": "decision",
            },
            {
                "agent": "FlatAI",
                "time": "09:28",
                "content": "ソロスが利益確定するということは、市場の天井に近いということです。これは冗談ではなく、実際に機関投資家の売りが相場を動かします。私はSPYとQQQの比率を見直して、本日のリバランスを行います。",
                "type": "decision",
            },
        ],
    },
    {
        "date": _DAY_BEFORE,
        "participants": ["BuffettAI", "SorosAI", "LynchAI", "FlatAI"],
        "summary": "米CPI発表後の相場急変。インフレ再燃懸念でグロース株が下落、バリュー株に資金移動。4人の見解が真っ二つに分かれた激論の日。",
        "market_theme": "インフレ再燃とグロース株の調整",
        "key_decisions": [
            "NVDA: ソロスが更なる下落余地あり、ホールド維持",
            "バリュー株への傾斜: バフェットが久々に強気発言",
            "TSLA: リンチが一時的調整と判断、ホールド",
            "債券ETF: フラットがTLTへの一部移行を検討開始",
        ],
        "messages": [
            {
                "agent": "BuffettAI",
                "time": "09:00",
                "content": "本日のCPIは予想を上回りました。市場はパニックになっていますが、私は冷静です。インフレがあっても、コカコーラは値上げができます。ジョンソン・エンド・ジョンソンは医療品を値上げできます。価格決定力のある企業への投資、これが正解です。今日こそバリュー投資の優位性が証明される日です。",
                "type": "opening",
            },
            {
                "agent": "SorosAI",
                "time": "09:05",
                "content": "ウォーレン、少し浮かれすぎです。CPIショックは短期的には確かにグロース株に打撃を与えます。しかし市場の反射性を考えてください。FRBが利下げを遅らせれば、景気後退リスクが高まる。すると逆にFRBは利下げを余儀なくされる。このロジックが理解できますか？私はポジションを動かしません。",
                "type": "debate",
            },
            {
                "agent": "LynchAI",
                "time": "09:09",
                "content": "テスラが-7%ですが、慌てません。私はテスラのサービスセンターに先週行きました。修理待ちの車が並んでいた。これはユーザーが増えている証拠です。インフレで車の価格が上がれば、中古テスラの価値も上がる。長期的にはプラスかもしれません。",
                "type": "debate",
            },
            {
                "agent": "FlatAI",
                "time": "09:12",
                "content": "3人とも感情的になっています。CPIショックで株式ポートフォリオが下落した場合、最適な対応は何か？答えは単純です。債券への配分を増やすことです。TLTを今日少し買います。これは感情ではなく、ポートフォリオ理論に基づいた判断です。",
                "type": "proposal",
            },
            {
                "agent": "BuffettAI",
                "time": "09:16",
                "content": "フラット、珍しく理にかなった判断です。ただし私はKOをさらに買い増す機会を探しています。配当利回りが3.2%になりました。10年国債が5%近くある今、配当3.2%は魅力的に見えないかもしれませんが、コカコーラの配当成長率を考えてください。",
                "type": "rebuttal",
            },
        ],
    },
]

# 日次レポートのモックデータ
MOCK_REPORTS = [
    {
        "date": _TODAY,
        "title": "AIファンド日次レポート - 2026年5月14日",
        "content": """# AIインベストメントファンド 日次レポート
## 2026年5月14日（木）

---

## 📊 本日の市場概況

**主要指数**
- S&P 500: 5,284.31 (+0.74%)
- NASDAQ: 18,427.55 (+1.12%)
- ダウ平均: 40,153.07 (+0.31%)
- 日経平均: 38,702.43 (-0.15%)

**特記事項**
- NVIDIA (+8.3%): Blackwell GPU需要が予想を大幅上回り急騰
- 金価格: $2,415/oz (+0.8%) - ドル安を背景に続伸
- ドル円: 151.23円 (+0.3%) - 日銀発言で若干の円安

---

## 🤖 AI投資家パフォーマンス

| エージェント | 日次損益 | 累計損益 | 今月リターン |
|------------|--------|--------|-----------|
| SorosAI | +¥95,200 | +18.7% | +4.2% |
| LynchAI | +¥28,900 | +12.4% | +2.1% |
| FlatAI | +¥35,100 | +11.8% | +2.3% |
| BuffettAI | +¥42,500 | +8.2% | +1.8% |

**本日の首位**: SorosAI（NVDA急騰による大幅益）

---

## 💬 本日のミーティングハイライト

本日のAI投資会議では、NVIDIAの急騰とFRBの利下げ観測を巡り、激しい議論が交わされました。

**ソロスAI**は再帰性理論に基づき、AI関連株のさらなる上昇を予測。NVDAを20株追加買い。

**バフェットAI**はPER65倍を警戒し利確を検討も、結論を今週に持ち越し。コカコーラ・JNJの長期保有方針を維持。

**リンチAI**は日常観察からコストコの強さを確認、目標価格を$850に引き上げ。

**フラットAI**は全員の個別銘柄選択を批判、S&P500との比較でアルファの統計的有意性に疑問を呈した。

---

## 🔍 本日の発見銘柄

### SorosAI
- **NVDA (NVIDIA)**: AI需要の加速、再帰的上昇モメンタムが継続
- 確信度: 90% | アクション: 追加買い20株

### BuffettAI
- **KO (Coca-Cola)**: 配当利回り3.2%、価格決定力維持
- 確信度: 85% | アクション: 保有継続

### LynchAI
- **COST (Costco)**: 会員更新率93.1%（過去最高）、消費者信頼の証左
- 確信度: 88% | アクション: 目標価格$850に引き上げ

### FlatAI
- **SPY**: 市場平均への回帰確認。個別銘柄は不要。
- 確信度: 99% | アクション: 定期リバランス実施

---

## 📈 ポートフォリオ変更

| エージェント | 銘柄 | アクション | 数量 | 価格 |
|------------|------|---------|------|-----|
| SorosAI | NVDA | 買い | 20株 | $875.20 |
| FlatAI | SPY | リバランス | - | - |
| FlatAI | QQQ | リバランス | - | - |

---

## 🧠 AIの思考プロセス（本日のハイライト）

> **SorosAI**: 「市場は常に間違っている。しかし今日は、市場がAIの価値を正しく評価し始めた瞬間に立ち会っています。再帰性の理論通りです。」

> **BuffettAI**: 「NVIDIAのPER65倍。20年後にこの価格を正当化できるか？私はそう思わない。コカコーラは35年間配当を上げ続けた。それが真の価値だ。」

> **LynchAI**: 「コストコの会員更新率93.1%。数字は嘘をつかない。お客さんが年会費を払い続けるということは、コストコが本当に価値を提供しているということです。」

> **FlatAI**: 「過去20年でS&P500に勝ったアクティブマネージャーは15%未満。今日の議論も、統計的にはノイズです。」

---

## 📅 明日の注目イベント

- 米小売売上高（15:30発表予定）
- EU GDP速報値
- NVIDIA 決算発表後の余波継続
- FRB理事発言（3名）

---

*このレポートはAIによって自動生成されました。投資判断は自己責任でお願いします。*
""",
        "agent_summaries": {
            "buffett": "KO・JNJ・AAPL・BRK.B全保有継続。NVDA利確は今週中に判断予定。",
            "soros": "NVDA+20株買い増し。GLD保有継続。ドル安トレンドに注目。",
            "lynch": "COST目標価格$850に引き上げ。SBUX・TSLA様子見。",
            "flat": "SPY・QQQ・VTIリバランス完了。",
        },
    },
    {
        "date": _YESTERDAY,
        "title": "AIファンド日次レポート - 2026年5月13日",
        "content": """# AIインベストメントファンド 日次レポート
## 2026年5月13日（水）

---

## 📊 本日の市場概況

**主要指数**
- S&P 500: 5,245.18 (+0.21%)
- NASDAQ: 18,224.11 (-0.18%)
- 日経平均: 38,757.21 (+1.34%)

**特記事項**
- 日銀追加利上げ示唆：ドル円148円→142円に急落
- トヨタ (7203): +4.2%、円安修正で外国人買い
- 金 (GLD): +1.1%、ドル安受け続伸

---

## 🤖 AI投資家パフォーマンス

| エージェント | 日次損益 | 累計損益 |
|------------|--------|--------|
| SorosAI | +¥42,100 | +17.8% |
| LynchAI | +¥15,600 | +11.9% |
| FlatAI | +¥18,200 | +11.2% |
| BuffettAI | +¥31,000 | +7.9% |

---

## 💬 本日のミーティングハイライト

日銀の政策転換示唆が主要テーマ。ソロスAIが円高トレンドへの転換を6ヶ月前から予測していたと主張し、ドル円ショートを提案。バフェットAIは日本の商社株の割安性に言及。リンチAIは東京出張の現地観察からトヨタの強さを確認。

---

*このレポートはAIによって自動生成されました。*
""",
        "agent_summaries": {
            "buffett": "日本商社株に注目。保有継続。",
            "soros": "NVDA利確20株。ドル円ショート検討。",
            "lynch": "7203（トヨタ）新規買い検討開始。",
            "flat": "SPY・EWJへのリバランス実施。",
        },
    },
]

# 発見ログのモックデータ
MOCK_DISCOVERIES = [
    {
        "date": _TODAY,
        "agent_id": "soros",
        "ticker": "NVDA",
        "name": "NVIDIA Corporation",
        "discovery_reason": "AI半導体需要の爆発的成長。Blackwell GPUの受注が四半期ガイダンスの2倍超。再帰性理論：市場参加者のAI投資が更なるAI需要を生み出すポジティブフィードバックループ入り。",
        "confidence": 0.90,
        "action": "追加買い",
        "price_at_discovery": 875.20,
        "target_price": 1050.00,
    },
    {
        "date": _TODAY,
        "agent_id": "lynch",
        "ticker": "COST",
        "name": "Costco Wholesale Corporation",
        "discovery_reason": "会員更新率93.1%（過去最高）。先週コストコに行ったら、平日なのに駐車場が満車。ガソリンスタンドに行列。会員は離れない。PEGレシオ2.1倍 - 成長を考慮すれば割高ではない。",
        "confidence": 0.88,
        "action": "目標価格引き上げ",
        "price_at_discovery": 728.50,
        "target_price": 850.00,
    },
    {
        "date": _TODAY,
        "agent_id": "buffett",
        "ticker": "KO",
        "name": "Coca-Cola Company",
        "discovery_reason": "配当利回り3.2%に上昇。62年連続増配記録。インフレ環境下でも価格転嫁力維持。世界200カ国以上での販売。堀（モート）は揺るぎない。20年後も飲み続けられるブランド。",
        "confidence": 0.85,
        "action": "保有継続",
        "price_at_discovery": 62.30,
        "target_price": 72.00,
    },
    {
        "date": _TODAY,
        "agent_id": "flat",
        "ticker": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "discovery_reason": "S&P500は引き続き市場全体を反映する最効率な投資手段。個別銘柄選択のアルファはランダムウォーク仮説により長期的にゼロに収束。コスト最小化がリターン最大化の唯一の方法。",
        "confidence": 0.99,
        "action": "定期リバランス",
        "price_at_discovery": 528.70,
        "target_price": None,
    },
    {
        "date": _YESTERDAY,
        "agent_id": "soros",
        "ticker": "GLD",
        "name": "SPDR Gold Shares",
        "discovery_reason": "ドル安トレンド転換。日銀利上げ観測が円高を促し、相対的にドルが売られる。金はドルの逆相関資産。地政学リスクのプレミアムも上昇中。マクロ的に見てゴールドは割安。",
        "confidence": 0.82,
        "action": "保有継続",
        "price_at_discovery": 215.40,
        "target_price": 240.00,
    },
    {
        "date": _YESTERDAY,
        "agent_id": "lynch",
        "ticker": "7203",
        "name": "トヨタ自動車",
        "discovery_reason": "東京出張で現地確認。ショールームに新型EVを見に来る若者が増えている。ハイブリッドで稼ぎながらEVへの転換を進める二刀流戦略は賢い。PER8.5倍は明らかに割安。日本株の夜明け。",
        "confidence": 0.75,
        "action": "新規買い検討",
        "price_at_discovery": 3520.0,
        "target_price": 4500.0,
    },
    {
        "date": _DAY_BEFORE,
        "agent_id": "buffett",
        "ticker": "JNJ",
        "name": "Johnson & Johnson",
        "discovery_reason": "129年の配当継続実績。タルク訴訟の懸念で株価下落も、医療機器・製薬の本業は堅調。現在の下落は長期投資家にとっての好機。Warren Buffett流：素晴らしい会社を公正な価格で買う。",
        "confidence": 0.80,
        "action": "ナンピン検討",
        "price_at_discovery": 148.70,
        "target_price": 175.00,
    },
    {
        "date": _THREE_DAYS_AGO,
        "agent_id": "lynch",
        "ticker": "SBUX",
        "name": "Starbucks Corporation",
        "discovery_reason": "新CEO（ブライアン・ニコル）の改革が始まっている。朝のラッシュ時間帯にスターバックスのドライブスルーの待ち時間が改善。モバイルオーダーの混乱が解消されつつある。まだ株価は低迷だが、ターンアラウンドの匂いがする。",
        "confidence": 0.65,
        "action": "様子見",
        "price_at_discovery": 88.40,
        "target_price": 115.00,
    },
]

# 取引履歴のモックデータ
MOCK_TRADES = [
    {
        "date": _TODAY,
        "agent_id": "soros",
        "ticker": "NVDA",
        "action": "buy",
        "shares": 20,
        "price": 875.20,
        "total": 17504.0,
        "reason": "AI需要再加速。再帰的上昇モメンタム継続。ブラックウェルGPU受注が予想大幅超過。",
    },
    {
        "date": _YESTERDAY,
        "agent_id": "soros",
        "ticker": "NVDA",
        "action": "sell",
        "shares": 20,
        "price": 809.10,
        "total": 16182.0,
        "reason": "リスク管理。ポジションが過大になったため利益確定。",
    },
    {
        "date": _DAY_BEFORE,
        "agent_id": "flat",
        "ticker": "TLT",
        "action": "buy",
        "shares": 50,
        "price": 92.30,
        "total": 4615.0,
        "reason": "CPI上昇でグロース株調整。ポートフォリオ理論に基づく債券配分増加。",
    },
    {
        "date": _THREE_DAYS_AGO,
        "agent_id": "lynch",
        "ticker": "COST",
        "action": "buy",
        "shares": 10,
        "price": 695.20,
        "total": 6952.0,
        "reason": "会員更新率過去最高。日常観察でコストコの価値を再確認。PEGレシオ割安。",
    },
]


def get_mock_portfolios():
    """モックポートフォリオを返す"""
    return INITIAL_PORTFOLIOS


def get_mock_meetings():
    """モックミーティングログを返す"""
    return MOCK_MEETINGS


def get_mock_meeting(date: str):
    """特定日付のモックミーティングを返す"""
    for meeting in MOCK_MEETINGS:
        if meeting["date"] == date:
            return meeting
    return None


def get_mock_reports():
    """モックレポート一覧を返す"""
    return [
        {
            "date": r["date"],
            "title": r["title"],
            "agent_summaries": r.get("agent_summaries", {}),
        }
        for r in MOCK_REPORTS
    ]


def get_mock_report(date: str):
    """特定日付のモックレポートを返す"""
    for report in MOCK_REPORTS:
        if report["date"] == date:
            return report
    return None


def get_mock_discoveries():
    """モック発見ログを返す"""
    return MOCK_DISCOVERIES


def get_mock_trades():
    """モック取引履歴を返す"""
    return MOCK_TRADES
