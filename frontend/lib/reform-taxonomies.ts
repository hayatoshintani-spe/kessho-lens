// 経営課題マップ / IPビジネスレンズ / KPI のマスタデータ
// AI 連携 / Notion 連携時はこの定義をシードとして同期する想定

import type {
  ThemeGroupId,
  ThemeGroupMeta,
  ThemeId,
  ThemeMeta,
  IPLensId,
  IPLensMeta,
  KPIDefinition,
} from './reform-types';

// ─── 経営課題マップ ───────────────────────────────────────────────────

export const THEME_GROUPS: Record<ThemeGroupId, ThemeGroupMeta> = {
  revenue_growth: {
    id: 'revenue_growth',
    label: '売上成長',
    color: '#1D9E75',
    icon: '📈',
  },
  profit_improvement: {
    id: 'profit_improvement',
    label: '利益改善',
    color: '#C8860A',
    icon: '💰',
  },
  org_reform: {
    id: 'org_reform',
    label: '組織改革',
    color: '#2196F3',
    icon: '🏗️',
  },
  finance_ir: {
    id: 'finance_ir',
    label: '財務・株価',
    color: '#9C27B0',
    icon: '📊',
  },
  risk: {
    id: 'risk',
    label: 'リスク',
    color: '#D85A30',
    icon: '⚠️',
  },
};

export const THEMES: Record<ThemeId, ThemeMeta> = {
  // ─── 売上成長 ────────────────────────────
  global_ip: {
    id: 'global_ip',
    group: 'revenue_growth',
    label: '海外IP展開',
    short: '海外IP',
    description: 'ウルトラマンIPの海外ライセンス・配給・パートナリング',
  },
  d2c: {
    id: 'd2c',
    group: 'revenue_growth',
    label: 'D2C強化',
    short: 'D2C',
    description: '自社EC・直販・会員プログラムの強化',
  },
  md_reform: {
    id: 'md_reform',
    group: 'revenue_growth',
    label: '商品MD改革',
    short: 'MD改革',
    description: 'SKU構成・価格帯・ターゲット顧客の見直し',
  },
  experience: {
    id: 'experience',
    group: 'revenue_growth',
    label: '体験事業',
    short: '体験',
    description: 'イベント・テーマパーク・コラボ施設',
  },
  collab: {
    id: 'collab',
    group: 'revenue_growth',
    label: '新規コラボ',
    short: 'コラボ',
    description: '他社IP・ブランド・アーティストとの共同企画',
  },

  // ─── 利益改善 ────────────────────────────
  royalty_design: {
    id: 'royalty_design',
    group: 'profit_improvement',
    label: 'ロイヤリティ設計',
    short: 'ロイヤリティ',
    description: '最低保証/料率/契約期間の設計改善',
  },
  cogs: {
    id: 'cogs',
    group: 'profit_improvement',
    label: '原価率改善',
    short: '原価率',
    description: '製造原価・物流費・在庫の最適化',
  },
  sga_opt: {
    id: 'sga_opt',
    group: 'profit_improvement',
    label: '販管費最適化',
    short: '販管費',
    description: '人件費・広告宣伝費・販促費の構造改革',
  },
  high_margin_products: {
    id: 'high_margin_products',
    group: 'profit_improvement',
    label: '高粗利商品の開発',
    short: '高粗利',
    description: '大人向け・コレクター向け・限定商品の拡充',
  },

  // ─── 組織改革 ────────────────────────────
  sales_org: {
    id: 'sales_org',
    group: 'org_reform',
    label: '営業体制',
    short: '営業',
    description: 'チャネル別営業組織の再設計',
  },
  product_org: {
    id: 'product_org',
    group: 'org_reform',
    label: '商品企画体制',
    short: '商品企画',
    description: 'SNS起点企画・スピード意思決定組織',
  },
  crm_org: {
    id: 'crm_org',
    group: 'org_reform',
    label: 'CRM体制',
    short: 'CRM',
    description: 'ファン分析・施策実行・ロイヤリティ運用組織',
  },
  data_org: {
    id: 'data_org',
    group: 'org_reform',
    label: 'データ活用体制',
    short: 'データ',
    description: 'BI/データ基盤・データドリブン意思決定',
  },

  // ─── 財務・株価 ──────────────────────────
  ir_story: {
    id: 'ir_story',
    group: 'finance_ir',
    label: 'IRストーリー',
    short: 'IR',
    description: '投資家への成長ストーリー提示',
  },
  capital_efficiency: {
    id: 'capital_efficiency',
    group: 'finance_ir',
    label: '資本効率',
    short: '資本効率',
    description: 'ROE/ROIC/在庫回転の改善',
  },
  midterm_plan: {
    id: 'midterm_plan',
    group: 'finance_ir',
    label: '中期経営計画',
    short: '中計',
    description: '3〜5年の経営方針・数値目標の再設計',
  },

  // ─── リスク ──────────────────────────────
  china_dependence: {
    id: 'china_dependence',
    group: 'risk',
    label: '中国依存',
    short: '中国依存',
    description: '中国売上比率・代替市場開拓',
  },
  contract_risk: {
    id: 'contract_risk',
    group: 'risk',
    label: '契約リスク',
    short: '契約',
    description: 'ライセンス契約条件・更新リスク',
  },
  counterfeit: {
    id: 'counterfeit',
    group: 'risk',
    label: '模倣品',
    short: '模倣品',
    description: '海賊版・コピー品の流通対策',
  },
  ip_damage: {
    id: 'ip_damage',
    group: 'risk',
    label: 'IP毀損',
    short: 'IP毀損',
    description: '炎上・不適切な二次利用・ブランド低下',
  },
  regulation: {
    id: 'regulation',
    group: 'risk',
    label: '規制変化',
    short: '規制',
    description: '著作権法・輸出規制・各国の表現規制',
  },
};

export const THEMES_BY_GROUP: Record<ThemeGroupId, ThemeId[]> = (() => {
  const out: Record<ThemeGroupId, ThemeId[]> = {
    revenue_growth: [],
    profit_improvement: [],
    org_reform: [],
    finance_ir: [],
    risk: [],
  };
  for (const t of Object.values(THEMES)) {
    out[t.group].push(t.id);
  }
  return out;
})();

// ─── IPビジネスレンズ ─────────────────────────────────────────────────

export const IP_LENSES: Record<IPLensId, IPLensMeta> = {
  ip_monetization: {
    id: 'ip_monetization',
    label: 'IP収益化',
    short: 'IP収益化',
    icon: '💎',
    description: 'IP価値を売上・利益にどう換金するか',
  },
  china: {
    id: 'china',
    label: '中国事業',
    short: '中国',
    icon: '🇨🇳',
    description: '中国市場における展開・リスク・機会',
  },
  product_planning: {
    id: 'product_planning',
    label: '商品企画',
    short: '商品企画',
    icon: '🎨',
    description: '商品ラインナップ・SKU設計・トレンド対応',
  },
  harajuku: {
    id: 'harajuku',
    label: '原宿プロジェクト',
    short: '原宿',
    icon: '🏬',
    description: '原宿旗艦店・直営拠点の戦略',
  },
  d2c_crm: {
    id: 'd2c_crm',
    label: 'D2C/CRM',
    short: 'D2C/CRM',
    icon: '🛒',
    description: '直販・会員・ファンエンゲージメント',
  },
  license_contract: {
    id: 'license_contract',
    label: 'ライセンス契約',
    short: 'ライセンス',
    icon: '📜',
    description: '契約条件・最低保証・料率・期間',
  },
  global_expansion: {
    id: 'global_expansion',
    label: '海外展開',
    short: '海外',
    icon: '🌐',
    description: 'グローバル市場開拓・地域別戦略',
  },
  fan_community: {
    id: 'fan_community',
    label: 'ファンコミュニティ',
    short: 'ファン',
    icon: '👥',
    description: 'コアファン育成・UGC・コミュニティ運営',
  },
};

// ─── KPI 定義 ─────────────────────────────────────────────────────────

export const KPI_DEFS: KPIDefinition[] = [
  // 売上系
  { id: 'kpi_revenue', label: '売上', unit: 'jpy', category: 'revenue',
    description: '連結売上高(月次/四半期)' },
  { id: 'kpi_overseas_ratio', label: '海外売上比率', unit: 'pct', category: 'global',
    description: '海外売上 / 全社売上' },
  { id: 'kpi_d2c_revenue', label: 'D2C売上', unit: 'jpy', category: 'revenue',
    description: '自社EC + 直営店の売上' },
  // 利益系
  { id: 'kpi_gross_profit', label: '粗利', unit: 'jpy', category: 'profit',
    description: '売上高 - 売上原価' },
  { id: 'kpi_gross_margin', label: '粗利率', unit: 'pct', category: 'profit',
    description: '粗利 / 売上高' },
  { id: 'kpi_royalty_rate', label: 'ロイヤリティ率', unit: 'pct', category: 'license',
    description: '平均ロイヤリティ料率' },
  // 商品系
  { id: 'kpi_sku_count', label: 'SKU数', unit: 'count', category: 'product',
    description: '販売中商品の総 SKU 数' },
  // 顧客系
  { id: 'kpi_ec_conversion', label: 'EC転換率', unit: 'pct', category: 'customer',
    description: '自社 EC の購入転換率' },
  { id: 'kpi_member_count', label: '会員登録数', unit: 'people', category: 'customer',
    description: '累計会員登録者数' },
  { id: 'kpi_store_visitors', label: '来店者数', unit: 'people', category: 'customer',
    description: '原宿店ほか直営店の月次来店数' },
  { id: 'kpi_avg_basket', label: '客単価', unit: 'jpy', category: 'customer',
    description: '1顧客あたり平均購入額' },
  { id: 'kpi_purchase_rate', label: '購入率', unit: 'pct', category: 'customer',
    description: '会員あたり購入率' },
  // ソーシャル系
  { id: 'kpi_sns_posts', label: 'SNS投稿数', unit: 'count', category: 'social',
    description: '公式アカウント月次投稿数' },
  // ライセンス
  { id: 'kpi_contract_renewal', label: '契約更新数', unit: 'count', category: 'license',
    description: 'ライセンス契約の年次更新数' },
  { id: 'kpi_new_licensee', label: '新規ライセンシー数', unit: 'count', category: 'license',
    description: '新規契約獲得数' },
];

// ─── キーワード → テーマ/レンズ 推定マップ ─────────────────────────
// スコア推定 / 自動分類で使う。実運用では LLM 判定に置き換える想定。

export const KEYWORD_TO_THEMES: Array<{ kw: RegExp; themes: ThemeId[] }> = [
  { kw: /中国|china|中華|抖音|tiktok/i, themes: ['china_dependence', 'global_ip'] },
  { kw: /原宿|harajuku|旗艦店|flagship/i, themes: ['d2c', 'experience'] },
  { kw: /d2c|直販|ec|オンライン|オムニチャネル/i, themes: ['d2c', 'crm_org'] },
  { kw: /ライセンス|licens|許諾|ロイヤリ/i,
    themes: ['royalty_design', 'contract_risk'] },
  { kw: /模倣|海賊|コピー品|偽物/i, themes: ['counterfeit', 'ip_damage'] },
  { kw: /規制|法律|著作権|copyright|gdpr/i, themes: ['regulation', 'contract_risk'] },
  { kw: /株価|投資家|ir|決算|市場/i, themes: ['ir_story', 'capital_efficiency'] },
  { kw: /中期経営|中計|midterm/i, themes: ['midterm_plan'] },
  { kw: /sns|tiktok|instagram|x\b|twitter|youtube|ugc/i,
    themes: ['product_org', 'd2c'] },
  { kw: /高単価|プレミアム|大人|コレクター/i,
    themes: ['high_margin_products', 'md_reform'] },
  { kw: /原価|物流|在庫|サプライ/i, themes: ['cogs'] },
  { kw: /人件費|採用|組織|hr/i, themes: ['sga_opt', 'sales_org'] },
  { kw: /コラボ|collab|共同/i, themes: ['collab', 'md_reform'] },
  { kw: /テーマパーク|イベント|exhibition|expo/i, themes: ['experience'] },
  { kw: /会員|ファン|crm|ロイヤリティプログラム/i,
    themes: ['crm_org', 'd2c'] },
  { kw: /データ|bi|dashboard|analytics/i, themes: ['data_org'] },
  { kw: /炎上|批判|不祥事/i, themes: ['ip_damage'] },
  { kw: /海外|グローバル|global|overseas|アメリカ|欧州|韓国|台湾|東南アジア/i,
    themes: ['global_ip'] },
];

export const KEYWORD_TO_LENSES: Array<{ kw: RegExp; lenses: IPLensId[] }> = [
  { kw: /中国|china|抖音|tiktok|wechat|bilibili|微博/i, lenses: ['china'] },
  { kw: /原宿|harajuku|旗艦店|flagship store/i, lenses: ['harajuku'] },
  { kw: /ライセンス|licens|許諾|ロイヤリ|契約/i, lenses: ['license_contract'] },
  { kw: /d2c|ec|直販|会員|crm|ロイヤリティ/i, lenses: ['d2c_crm'] },
  { kw: /商品|sku|md|merchandis|プロダクト|フィギュア|グッズ/i,
    lenses: ['product_planning'] },
  { kw: /海外|グローバル|global|overseas|アメリカ|欧州|韓国|台湾|東南アジア/i,
    lenses: ['global_expansion'] },
  { kw: /ファン|fan community|コミュニティ|ugc|二次創作/i,
    lenses: ['fan_community'] },
  { kw: /収益化|monetiz|配信収益|ip価値|ip ip収益/i, lenses: ['ip_monetization'] },
];

// 全カードに最低 1 つは IP収益化レンズを当てる(円谷は IP 会社のため)
export const DEFAULT_LENS: IPLensId = 'ip_monetization';
