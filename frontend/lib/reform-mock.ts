// 改革カード / アクション / KPI / 週次アジェンダのモックデータ
// localStorage 永続化用のシード。将来的にバックエンド API に置き換え可能。

import type {
  ReformAction,
  KPISnapshot,
  WeeklyAgendaItem,
  ReformCardEnrichment,
} from './reform-types';

const today = () => new Date().toISOString().slice(0, 10);
const daysAgo = (n: number) => {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
};
const daysAhead = (n: number) => {
  const d = new Date();
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
};

// ─── アクション ───────────────────────────────────────────────────────

export const MOCK_ACTIONS: ReformAction[] = [
  {
    id: 'act_001',
    title: '中国MD自社企画比率を 30→50% に引き上げる施策案を立案',
    owner: '商品企画部',
    deadline: daysAgo(2),  // 遅延
    status: 'in_progress',
    priority: 'urgent',
    memo: '抖音・小紅書での反応分析を踏まえてSKU構成案を作る',
    linked_kpi_ids: ['kpi_sku_count', 'kpi_overseas_ratio'],
    next_review_date: today(),
    created_at: daysAgo(14),
    updated_at: daysAgo(3),
  },
  {
    id: 'act_002',
    title: '原宿店舗を D2C会員獲得拠点として再設計する素案作成',
    owner: '直営事業部',
    deadline: daysAhead(7),
    status: 'in_progress',
    priority: 'high',
    memo: 'QRコード会員登録動線+店舗体験設計の両軸で',
    linked_kpi_ids: ['kpi_member_count', 'kpi_store_visitors'],
    next_review_date: daysAhead(5),
    created_at: daysAgo(10),
    updated_at: daysAgo(1),
  },
  {
    id: 'act_003',
    title: '海外ライセンス契約 最低保証条件の見直し方針を経営承認',
    owner: 'ライセンス部',
    deadline: daysAhead(3),
    status: 'awaiting_review',  // 経営判断待ち
    priority: 'urgent',
    memo: '4契約について、現行最低保証 vs 想定実績の差分を可視化済み',
    linked_kpi_ids: ['kpi_royalty_rate', 'kpi_contract_renewal'],
    created_at: daysAgo(7),
    updated_at: daysAgo(1),
  },
  {
    id: 'act_004',
    title: '大人向け高単価商品ライン 第1弾コレクション企画',
    owner: '商品企画部',
    deadline: daysAhead(21),
    status: 'in_progress',
    priority: 'high',
    memo: '想定価格帯 ¥8,000-¥30,000、SKU 12点',
    linked_kpi_ids: ['kpi_avg_basket', 'kpi_gross_margin'],
    created_at: daysAgo(5),
    updated_at: today(),
  },
  {
    id: 'act_005',
    title: 'SNS起点の商品企画体制 立ち上げ案を提案',
    owner: '組織開発',
    deadline: daysAhead(14),
    status: 'not_started',
    priority: 'medium',
    memo: 'TikTok/Instagram の月次トレンドを商品企画に直結させる組織',
    created_at: daysAgo(2),
    updated_at: daysAgo(2),
  },
  {
    id: 'act_006',
    title: '模倣品流通対策の海外法務リソース確保',
    owner: '法務',
    deadline: daysAgo(5),  // 遅延
    status: 'on_hold',
    priority: 'high',
    memo: '対応国を絞り込み中。中国 + 東南アジア 3カ国を優先候補に',
    created_at: daysAgo(20),
    updated_at: daysAgo(10),
  },
  {
    id: 'act_007',
    title: 'IR向け中期成長ストーリー(IP収益化軸)のドラフト作成',
    owner: 'IR/経営企画',
    deadline: daysAhead(10),
    status: 'awaiting_review',  // 経営判断待ち
    priority: 'medium',
    memo: '海外IP・D2C・ライセンス改善の3本柱で構成',
    linked_kpi_ids: ['kpi_overseas_ratio', 'kpi_d2c_revenue'],
    created_at: daysAgo(15),
    updated_at: daysAgo(2),
  },
  {
    id: 'act_008',
    title: 'ファンコミュニティ運営 KPI と運営体制の定義',
    owner: 'CRM/マーケ',
    deadline: daysAhead(28),
    status: 'not_started',
    priority: 'low',
    linked_kpi_ids: ['kpi_member_count', 'kpi_purchase_rate'],
    created_at: daysAgo(3),
    updated_at: daysAgo(3),
  },
];

// ─── KPI スナップショット ──────────────────────────────────────────────

export const MOCK_KPI_SNAPSHOTS: KPISnapshot[] = [
  { kpi_id: 'kpi_revenue', value: 2_180_000_000, target: 2_400_000_000,
    period: '2026-Q1', delta_vs_prev: 0.07, status: 'at_risk', updated_at: today() },
  { kpi_id: 'kpi_overseas_ratio', value: 18.2, target: 30.0,
    period: '2026-Q1', delta_vs_prev: 0.03, status: 'off_track', updated_at: today() },
  { kpi_id: 'kpi_d2c_revenue', value: 320_000_000, target: 500_000_000,
    period: '2026-Q1', delta_vs_prev: 0.22, status: 'at_risk', updated_at: today() },
  { kpi_id: 'kpi_gross_margin', value: 42.5, target: 48.0,
    period: '2026-Q1', delta_vs_prev: 0.012, status: 'at_risk', updated_at: today() },
  { kpi_id: 'kpi_royalty_rate', value: 8.3, target: 10.0,
    period: '2026-Q1', delta_vs_prev: -0.005, status: 'off_track', updated_at: today() },
  { kpi_id: 'kpi_sku_count', value: 1240, target: 1500,
    period: '2026-Q1', delta_vs_prev: 0.05, status: 'at_risk', updated_at: today() },
  { kpi_id: 'kpi_ec_conversion', value: 2.8, target: 3.5,
    period: '2026-Q1', delta_vs_prev: 0.18, status: 'at_risk', updated_at: today() },
  { kpi_id: 'kpi_member_count', value: 84_000, target: 120_000,
    period: '2026-Q1', delta_vs_prev: 0.28, status: 'on_track', updated_at: today() },
  { kpi_id: 'kpi_store_visitors', value: 18_500, target: 25_000,
    period: '2026-05', delta_vs_prev: 0.12, status: 'at_risk', updated_at: today() },
  { kpi_id: 'kpi_avg_basket', value: 4_200, target: 5_500,
    period: '2026-Q1', delta_vs_prev: 0.08, status: 'at_risk', updated_at: today() },
  { kpi_id: 'kpi_purchase_rate', value: 12.4, target: 18.0,
    period: '2026-Q1', delta_vs_prev: 0.04, status: 'off_track', updated_at: today() },
  { kpi_id: 'kpi_sns_posts', value: 142, target: 180,
    period: '2026-05', delta_vs_prev: 0.15, status: 'on_track', updated_at: today() },
  { kpi_id: 'kpi_contract_renewal', value: 18, target: 22,
    period: '2026-Q1', delta_vs_prev: 0.0, status: 'at_risk', updated_at: today() },
  { kpi_id: 'kpi_new_licensee', value: 5, target: 8,
    period: '2026-Q1', delta_vs_prev: 0.25, status: 'at_risk', updated_at: today() },
];

// ─── 週次経営会議アジェンダ ──────────────────────────────────────────

export const MOCK_WEEKLY_AGENDA: WeeklyAgendaItem[] = [
  {
    id: 'agd_1',
    rank: 1,
    topic: '中国MDの自社企画比率を 30 → 50% に引き上げるべきか',
    background: '現状の中国向け商品は OEM/版権許諾主体で、ロイヤリティ収益が伸び悩んでいる。抖音・小紅書では自社限定企画への反応が高く、機会損失が大きい。',
    why_now: '抖音の D2C 機能拡張、海外 IP コラボ商品の市場成熟、競合の自社企画拡大により、今動かないと差を縮められなくなる。',
    related_card_ids: [],
    related_kpi_ids: ['kpi_overseas_ratio', 'kpi_royalty_rate', 'kpi_sku_count'],
    recommended_decision: '段階的に自社企画比率を 6 ヶ月で 30 → 40%、12 ヶ月で 50% へ。商品企画部に専任チームを新設。',
    next_action: '商品企画部:中国専任チーム編成案 / ロイヤリティ部:契約改定案を 2 週間以内に提出',
    week_of: today(),
  },
  {
    id: 'agd_2',
    rank: 2,
    topic: '原宿店舗を D2C 会員獲得拠点として再設計できるか',
    background: '現状の原宿店は「物販拠点」として機能しているが、来店者の会員化率は 4% にとどまる。D2C 会員 LTV は店頭購入客の 3 倍。',
    why_now: '会員ベースを倍増させる中期目標に対し、現在のオンライン施策だけでは到達難。直営店舗の動線改革は実行コストが小さい割に効果が大きい。',
    related_card_ids: [],
    related_kpi_ids: ['kpi_member_count', 'kpi_store_visitors', 'kpi_d2c_revenue'],
    recommended_decision: 'QRコード会員登録動線設置・店舗限定会員特典・スタッフ KPI への会員化指標組込みを Q3 までに実装。',
    next_action: '直営事業部:再設計案を 1 ヶ月以内に提出。投資概算は 5,000 万円以内目標。',
    week_of: today(),
  },
  {
    id: 'agd_3',
    rank: 3,
    topic: '海外ライセンス契約の最低保証条件を見直すべきか',
    background: '主要 4 契約のうち 3 件が最低保証を下回って終了見込み。一方で実績好調な 2 契約は料率改定の交渉余地あり。',
    why_now: '次年度更新のタイミングで一括見直さないと条件は固定化する。',
    related_card_ids: [],
    related_kpi_ids: ['kpi_royalty_rate', 'kpi_contract_renewal'],
    recommended_decision: '不振契約は最低保証を実勢に合わせて引下げ、好調契約は料率を 1-2% 引上げる方針で交渉開始。',
    next_action: 'ライセンス部:契約別の交渉方針シートを 1 週間以内に経営承認用にまとめる。',
    week_of: today(),
  },
  {
    id: 'agd_4',
    rank: 4,
    topic: '大人向け高単価商品のSKUを増やすべきか',
    background: 'ファン層の高年齢化に伴い、¥8,000-¥30,000 帯のコレクター需要が増加。現状 SKU は全体の 8% で、競合は 25% 超。',
    why_now: '原価率を維持したまま粗利率を引き上げる最短手段。来期 IR 数値にも効く。',
    related_card_ids: [],
    related_kpi_ids: ['kpi_gross_margin', 'kpi_avg_basket', 'kpi_sku_count'],
    recommended_decision: '6 ヶ月で高単価 SKU を倍増(現 8% → 16%)。原宿店 + D2C 限定先行販売で需要検証。',
    next_action: '商品企画部:第 1 弾コレクション 12 SKU の企画書を 3 週間以内に提出。',
    week_of: today(),
  },
  {
    id: 'agd_5',
    rank: 5,
    topic: 'SNS起点の商品企画体制を作るべきか',
    background: '現状は商品企画 → SNS 投稿の一方通行。トレンドが SNS 上で生まれてから商品化までに 6 ヶ月かかっており、機会損失が大きい。',
    why_now: 'TikTok 起点のヒット商品は競合各社で増加。意思決定スピードが競争力に直結する局面。',
    related_card_ids: [],
    related_kpi_ids: ['kpi_sns_posts', 'kpi_sku_count'],
    recommended_decision: '商品企画部内に「ソーシャルプロダクト」チーム(3 名)を新設。2 週間以内の企画化を可能にする決裁権限を付与。',
    next_action: '組織開発:体制案 + 決裁権限ルールを 1 ヶ月以内に提示。',
    week_of: today(),
  },
];

// ─── 改革カード Enrichment ─────────────────────────────────────────────
// 実カード ID と紐づくが、初期は空配列。ユーザー操作で蓄積される想定。
export const MOCK_REFORM_ENRICHMENTS: ReformCardEnrichment[] = [];
