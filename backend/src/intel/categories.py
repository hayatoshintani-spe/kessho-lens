"""
重点カテゴリ定義（プロジェクト指示§4に対応）
7カテゴリ × 監視対象 × 観点
"""

from typing import Dict, List

CATEGORIES = [
    "ip_content",
    "ai_agent",
    "device_telecom",
    "global_region",
    "retail_md_license",
    "regulation_ip_law",
    "competitor_capital",
]

CATEGORY_META: Dict[str, Dict] = {
    "ip_content": {
        "id": "ip_content",
        "label": "IP・キャラクター・コンテンツ市場",
        "label_short": "IP / Content",
        "icon": "🎭",
        "color": "#E91E63",
        "targets": [
            "Disney", "Pokémon", "Sanrio", "Nintendo", "Netflix", "YouTube",
            "Roblox", "TikTok", "Marvel/DC", "Godzilla",
            "Anime/Manga/VTuber", "中国・韓国・東南アジアのIP企業",
        ],
        "watch_angles": [
            "どのIPがどの国で伸びているか",
            "映像・ゲーム・MD・イベント・ライセンスのどこで稼いでいるか",
            "ファンコミュニティをどう作っているか",
            "若年層接点をどう獲得しているか",
        ],
        "responsible_experts": ["ip_strategist", "global_expansion", "md_licensing"],
    },
    "ai_agent": {
        "id": "ai_agent",
        "label": "AI・生成AI・エージェント",
        "label_short": "AI / Agent",
        "icon": "🤖",
        "color": "#2196F3",
        "targets": [
            "OpenAI", "Google", "Anthropic", "Meta", "Perplexity",
            "Apple Intelligence", "Character.AI",
            "Midjourney", "Runway", "Suno", "ElevenLabs",
        ],
        "watch_angles": [
            "IPキャラクターをAI化できるか",
            "AI音声・動画・翻訳で海外展開コストが下がるか",
            "ファンとの会話体験を作れるか",
            "制作工程をどこまで効率化できるか",
            "権利侵害・学習データ問題にどう対応するか",
        ],
        "responsible_experts": ["ai_trend", "risk_manager", "ip_strategist"],
    },
    "device_telecom": {
        "id": "device_telecom",
        "label": "スマホ・通信・デバイス",
        "label_short": "Device / Telecom",
        "icon": "📱",
        "color": "#9C27B0",
        "targets": [
            "Apple", "Google Pixel", "Xperia", "Samsung",
            "Meta Quest", "RCS", "キャリア各社",
            "ARグラス", "スマートTV", "ゲーム機",
        ],
        "watch_angles": [
            "ユーザー接点はどのデバイスに移るか",
            "IP体験はスマホ/TV/AR/ゲーム/SNSのどこで起きるか",
            "キャリアとの協業可能性はあるか",
            "ウルトラマン公式アプリやファンCRMに何を活かせるか",
        ],
        "responsible_experts": ["ai_trend", "ip_strategist", "global_expansion"],
    },
    "global_region": {
        "id": "global_region",
        "label": "グローバル市場・地域別トレンド",
        "label_short": "Global / Region",
        "icon": "🌏",
        "color": "#FF9800",
        "targets": [
            "北米", "中国", "東南アジア", "インド",
            "中東", "欧州", "韓国", "台湾",
        ],
        "watch_angles": [
            "ウルトラマンが伸びる国はどこか",
            "配信・玩具・イベント・MDの勝ち筋は地域ごとに違うか",
            "現地パートナー候補はどこか",
            "海外ファンの熱量はどこにあるか",
        ],
        "responsible_experts": ["global_expansion", "md_licensing", "cfo"],
    },
    "retail_md_license": {
        "id": "retail_md_license",
        "label": "小売・MD・ライセンス・コマース",
        "label_short": "Retail / MD",
        "icon": "🛍️",
        "color": "#4CAF50",
        "targets": [
            "Bandai", "TOMY", "LEGO", "Funko", "Pop Mart",
            "Miniso", "ユニクロ", "ZOZO", "Amazon",
            "Shopify", "TikTok Shop", "中国ライブコマース",
        ],
        "watch_angles": [
            "グッズはどの価格帯が伸びているか",
            "大人向け・キダルト市場は拡大しているか",
            "D2Cで取れる余地はあるか",
            "限定商品・コラボ商品の勝ち筋は何か",
            "ライセンス収益を最大化する構造は何か",
        ],
        "responsible_experts": ["md_licensing", "global_expansion", "cfo"],
    },
    "regulation_ip_law": {
        "id": "regulation_ip_law",
        "label": "規制・著作権・プラットフォーム政策",
        "label_short": "Regulation / Law",
        "icon": "⚖️",
        "color": "#607D8B",
        "targets": [
            "AI著作権", "子どものSNS規制", "プラットフォーム規制",
            "中国・米国・EUのコンテンツ規制",
            "データ保護", "景表法・広告規制", "ガチャ規制",
        ],
        "watch_angles": [
            "子ども向けIPの展開に影響はあるか",
            "AIキャラクター展開の法的リスクは何か",
            "海外展開時の規制リスクは何か",
            "ファンデータ活用に制約はあるか",
        ],
        "responsible_experts": ["risk_manager", "global_expansion", "ip_strategist"],
    },
    "competitor_capital": {
        "id": "competitor_capital",
        "label": "競合・決算・資本市場",
        "label_short": "Competitor / Capital",
        "icon": "📊",
        "color": "#C8860A",
        "targets": [
            "円谷フィールズ", "東映アニメーション", "サンリオ", "バンダイナムコ",
            "東宝", "任天堂", "ソニー", "Netflix",
            "Disney", "Roblox", "Tencent", "Bilibili",
        ],
        "watch_angles": [
            "どの会社がIP収益を伸ばしているか",
            "映像・MD・ゲーム・ライセンスの利益率はどう違うか",
            "市場はどの事業モデルを評価しているか",
            "円谷の企業価値向上に何が必要か",
        ],
        "responsible_experts": ["cfo", "ip_strategist", "md_licensing"],
    },
}


def get_category_meta(category_id: str) -> Dict:
    """カテゴリIDからメタ情報を取得"""
    return CATEGORY_META.get(category_id, {})


def list_categories() -> List[Dict]:
    """全カテゴリのメタ情報リストを返す"""
    return [CATEGORY_META[c] for c in CATEGORIES]
