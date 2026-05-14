require('dotenv').config();
const express   = require('express');
const cors      = require('cors');
const yf        = require('yahoo-finance2').default;
const Anthropic = require('@anthropic-ai/sdk');
const fs        = require('fs');
const path      = require('path');

const app  = express();
const PORT = process.env.PORT || 3000;

// Vercel サーバーレス環境かどうか
const IS_VERCEL = !!process.env.VERCEL;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ── 対象銘柄定義 ──────────────────────────────────────────────────
const COMPANY_DEFS = [
  { id: 1, code: '2413', symbol: '2413.T', name: 'エムスリー',  nameEn: 'M3, Inc.',           sector: '医療DX',       exchange: '東証プライム' },
  { id: 2, code: '4478', symbol: '4478.T', name: 'freee',       nameEn: 'freee K.K.',         sector: '会計SaaS',     exchange: '東証グロース' },
  { id: 3, code: '4443', symbol: '4443.T', name: 'Sansan',      nameEn: 'Sansan, Inc.',       sector: '営業DX',       exchange: '東証プライム' },
  { id: 4, code: '3923', symbol: '3923.T', name: 'ラクス',       nameEn: 'Rakus Co., Ltd.',    sector: '経費精算SaaS', exchange: '東証プライム' },
  { id: 5, code: '6594', symbol: '6594.T', name: '日本電産',     nameEn: 'Nidec Corporation',  sector: '電気機器',     exchange: '東証プライム' },
];

const STATIC = {
  '2413': {
    description: '医療従事者向け総合プラットフォーム。医師の約95%が登録するネットワーク効果を持つ医療DXリーダー。AIを活用した製薬向けマーケティングも急成長。',
    fallback: { score: 91, rating: 'beat',   revenueGrowth: 28.4, operatingMargin: 32.1, grossMargin: 72.4 },
  },
  '4478': {
    description: '中小企業向けクラウド会計・人事労務SaaS。ARR高成長を維持しながら赤字を縮小中。フリーミアムからの有料転換率が改善傾向。',
    fallback: { score: 88, rating: 'beat',   revenueGrowth: 34.0, operatingMargin: -8.2, grossMargin: 69.8 },
  },
  '4443': {
    description: '法人向け名刺管理・営業DXクラウド。NRR 116%という高い顧客拡張率が継続成長を支える。Bill Oneの急成長が次の柱として期待される。',
    fallback: { score: 82, rating: 'beat',   revenueGrowth: 29.0, operatingMargin: 14.2, grossMargin: 65.1 },
  },
  '3923': {
    description: '経費精算・勤怠管理SaaSのリーディングカンパニー。主力の楽楽精算はARRが高成長を維持。中小から大企業への顧客層拡大が収益性改善に貢献。',
    fallback: { score: 79, rating: 'inline', revenueGrowth: 22.1, operatingMargin: 18.4, grossMargin: 62.3 },
  },
  '6594': {
    description: '精密モーター世界最大手。EV向け事業の回復遅れと中国景気減速を注視。構造改革とコスト削減の進捗が株価回復の鍵となる。',
    fallback: { score: 52, rating: 'miss',   revenueGrowth:  3.2, operatingMargin:  8.1, grossMargin: 28.4 },
  },
};

// ── キャッシュ（メモリ + ローカルファイル） ────────────────────────
const DATA_DIR   = path.join(__dirname, 'data');
const CACHE_FILE = path.join(DATA_DIR, 'companies_cache.json');

let companiesCache = [];
let lastUpdated    = null;

function loadCache() {
  if (IS_VERCEL) return; // Vercel ではファイルキャッシュ不可
  try {
    if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
    if (fs.existsSync(CACHE_FILE)) {
      const { companies, lastUpdated: lu } = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf-8'));
      companiesCache = companies || [];
      lastUpdated    = lu || null;
      console.log(`[Cache] ${companiesCache.length}社 読み込み完了 (${lastUpdated})`);
    }
  } catch (e) {
    console.error('[Cache] 読み込み失敗:', e.message);
  }
}

function saveCache(companies) {
  if (IS_VERCEL) return; // Vercel ではファイルキャッシュ不可
  try {
    if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
    lastUpdated = new Date().toISOString();
    fs.writeFileSync(CACHE_FILE, JSON.stringify({ companies, lastUpdated }, null, 2), 'utf-8');
  } catch (e) {
    console.error('[Cache] 保存失敗:', e.message);
  }
}

// ── Yahoo Finance データ取得 ──────────────────────────────────────
function pct(v) { return v != null ? +(v * 100).toFixed(1) : null; }
function num(v) { return v != null ? +(v).toFixed(2)       : null; }

function buildKPIs(code, { revenueGrowth, grossMargin, operatingMargin, price, changePercent, high52w }) {
  const ratio52w     = price && high52w ? Math.round(price / high52w * 100) : null;
  const growthLabel  = revenueGrowth == null ? 'N/A'
    : revenueGrowth > 25 ? '高成長' : revenueGrowth > 10 ? '安定成長' : revenueGrowth > 0 ? '低成長' : '減収';

  return [
    { label: '売上成長率', value: revenueGrowth != null ? `${revenueGrowth > 0 ? '+' : ''}${revenueGrowth}%` : 'N/A', change: growthLabel,                                                up: (revenueGrowth || 0) > 5  },
    { label: '営業利益率', value: operatingMargin != null ? `${operatingMargin}%` : 'N/A',                           change: operatingMargin > 15 ? '高収益' : operatingMargin > 0 ? '黒字' : '投資フェーズ', up: (operatingMargin || 0) > 0 },
    { label: '粗利率',     value: grossMargin != null ? `${grossMargin}%` : 'N/A',                                   change: grossMargin > 60 ? '高水準' : grossMargin > 40 ? '標準' : '改善余地',          up: (grossMargin || 0) > 40   },
    { label: '当日変動',   value: changePercent != null ? `${changePercent > 0 ? '+' : ''}${changePercent}%` : 'N/A', change: ratio52w ? `52週高値比 ${ratio52w}%` : '---',                               up: (changePercent || 0) >= 0  },
  ];
}

function scoreFromMetrics(rg, gm, om) {
  let s = 55;
  if (rg > 30) s += 20; else if (rg > 20) s += 14; else if (rg > 10) s += 7; else if (rg < 0) s -= 8;
  if (gm > 65) s += 12; else if (gm > 50) s += 7;  else if (gm > 35) s += 3;
  if (om > 20) s += 12; else if (om > 10) s += 7;  else if (om > 0)  s += 3; else if (om < -10) s -= 8;
  return Math.min(99, Math.max(20, s));
}

async function fetchLiveData() {
  console.log('[Yahoo Finance] データ取得開始...');
  const results = await Promise.all(
    COMPANY_DEFS.map(async def => {
      const st = STATIC[def.code] || { description: '', fallback: {} };
      try {
        const [quote, summary] = await Promise.all([
          yf.quote(def.symbol),
          yf.quoteSummary(def.symbol, { modules: ['financialData', 'defaultKeyStatistics'] }).catch(() => null),
        ]);
        const fd = summary?.financialData        || {};
        const ks = summary?.defaultKeyStatistics || {};

        const revenueGrowth   = pct(fd.revenueGrowth);
        const grossMargin     = pct(fd.grossMargins);
        const operatingMargin = pct(fd.operatingMargins);
        const price           = num(quote.regularMarketPrice);
        const changePercent   = num(quote.regularMarketChangePercent);
        const high52w         = num(quote.fiftyTwoWeekHigh);

        const surprise = ks.earningsSurprise?.raw;
        const rating   = surprise != null
          ? (surprise > 0.05 ? 'beat' : surprise < -0.05 ? 'miss' : 'inline')
          : st.fallback.rating || 'inline';

        const score = (revenueGrowth != null && grossMargin != null && operatingMargin != null)
          ? scoreFromMetrics(revenueGrowth, grossMargin, operatingMargin)
          : st.fallback.score || 60;

        console.log(`  ✓ ${def.name}: ¥${price?.toLocaleString('ja-JP') ?? '---'}`);
        return {
          ...def,
          price, priceChange: num(quote.regularMarketChange), changePercent,
          marketCap: quote.marketCap || null,
          peRatio:   num(quote.trailingPE) || null,
          high52w,   low52w: num(quote.fiftyTwoWeekLow),
          revenueGrowth:   revenueGrowth   ?? st.fallback.revenueGrowth   ?? 0,
          grossMargin:     grossMargin     ?? st.fallback.grossMargin     ?? 0,
          operatingMargin: operatingMargin ?? st.fallback.operatingMargin ?? 0,
          score, rating, description: st.description,
          kpis: buildKPIs(def.code, { revenueGrowth, grossMargin, operatingMargin, price, changePercent, high52w }),
          liveData: true, fetchedAt: new Date().toISOString(),
        };
      } catch (e) {
        console.error(`  ✗ ${def.name}: ${e.message}`);
        const fb = st.fallback;
        return {
          ...def,
          price: null, priceChange: null, changePercent: null, marketCap: null, peRatio: null, high52w: null, low52w: null,
          revenueGrowth: fb.revenueGrowth ?? 0, grossMargin: fb.grossMargin ?? 0, operatingMargin: fb.operatingMargin ?? 0,
          score: fb.score ?? 60, rating: fb.rating ?? 'inline', description: st.description,
          kpis: buildKPIs(def.code, { revenueGrowth: fb.revenueGrowth, grossMargin: fb.grossMargin, operatingMargin: fb.operatingMargin, price: null, changePercent: null, high52w: null }),
          liveData: false, fetchedAt: new Date().toISOString(),
        };
      }
    })
  );
  console.log(`[Yahoo Finance] 完了: ${results.length}社`);
  return results;
}

function makeFallbackCache() {
  return COMPANY_DEFS.map(def => {
    const st = STATIC[def.code] || { description: '', fallback: {} };
    const fb = st.fallback;
    return {
      ...def,
      price: null, priceChange: null, changePercent: null, marketCap: null, peRatio: null, high52w: null, low52w: null,
      revenueGrowth: fb.revenueGrowth ?? 0, grossMargin: fb.grossMargin ?? 0, operatingMargin: fb.operatingMargin ?? 0,
      score: fb.score ?? 60, rating: fb.rating ?? 'inline', description: st.description,
      kpis: buildKPIs(def.code, { revenueGrowth: fb.revenueGrowth, grossMargin: fb.grossMargin, operatingMargin: fb.operatingMargin, price: null, changePercent: null, high52w: null }),
      liveData: false, fetchedAt: new Date().toISOString(),
    };
  });
}

// ── API ルート ────────────────────────────────────────────────────

app.get('/api/companies', async (_req, res) => {
  // Vercel: キャッシュが空なら毎回フェッチ（ウォームインスタンスはキャッシュ使用）
  if (companiesCache.length === 0) {
    try {
      companiesCache = await fetchLiveData();
      lastUpdated    = new Date().toISOString();
      saveCache(companiesCache);
    } catch (e) {
      companiesCache = makeFallbackCache();
      lastUpdated    = new Date().toISOString();
    }
  }
  res.json({ companies: companiesCache, lastUpdated, count: companiesCache.length });
});

app.get('/api/refresh', async (_req, res) => {
  try {
    companiesCache = await fetchLiveData();
    lastUpdated    = new Date().toISOString();
    saveCache(companiesCache);
    res.json({ success: true, lastUpdated, count: companiesCache.length });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/api/chat', async (req, res) => {
  const { messages, systemPrompt, apiKey } = req.body;
  const key = apiKey || process.env.ANTHROPIC_API_KEY;

  if (!key) {
    return res.status(400).json({ error: 'Claude API キーが未設定です。⚙️ 設定から入力してください。' });
  }

  res.setHeader('Content-Type',  'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection',    'keep-alive');
  res.flushHeaders();

  try {
    const client = new Anthropic({ apiKey: key });
    const stream = client.messages.stream({
      model: 'claude-sonnet-4-20250514', max_tokens: 1200,
      system: systemPrompt, messages,
    });
    for await (const chunk of stream) {
      if (chunk.type === 'content_block_delta' && chunk.delta?.text) {
        res.write(`data: ${JSON.stringify({ text: chunk.delta.text })}\n\n`);
      }
    }
    res.write('data: [DONE]\n\n');
  } catch (e) {
    const msg = e.status === 401 ? 'APIキーが無効です。正しいキーを設定してください。' : e.message;
    res.write(`data: ${JSON.stringify({ error: msg })}\n\n`);
  }
  res.end();
});

// ── ローカル起動 / Cron（Vercel以外のみ） ────────────────────────
if (!IS_VERCEL) {
  const cron = require('node-cron');
  cron.schedule('30 9 * * 1-5', async () => {
    console.log(`[Cron] 定時更新開始`);
    try {
      companiesCache = await fetchLiveData();
      lastUpdated    = new Date().toISOString();
      saveCache(companiesCache);
      console.log('[Cron] 完了:', lastUpdated);
    } catch (e) {
      console.error('[Cron] 失敗:', e.message);
    }
  }, { timezone: 'UTC' });

  loadCache();

  app.listen(PORT, async () => {
    console.log('');
    console.log('╔══════════════════════════════════════════╗');
    console.log('║  #決密レンズ  AI アナリスト               ║');
    console.log(`║   http://localhost:${PORT}                    ║`);
    console.log('╚══════════════════════════════════════════╝');
    console.log(`  Claude API : ${process.env.ANTHROPIC_API_KEY ? '✓ .env 読み込み済み' : '⚠️  未設嚚（アプリ内で入力可）'}`);
    console.log(`  自動更新   : 毎営業日 18:30 JST`);
    console.log('');

    if (companiesCache.length === 0) {
      console.log('初回データ取得を開始します...');
      try {
        companiesCache = await fetchLiveData();
        lastUpdated    = new Date().toISOString();
        saveCache(companiesCache);
      } catch (e) {
        console.error('初回取得失敗 → フォールバc��クで起動:', e.message);
        companiesCache = makeFallbackCache();
        lastUpdated    = new Date().toISOString();
      }
    }
  });
}

// Vercel 用エクスポート
module.exports = app;
