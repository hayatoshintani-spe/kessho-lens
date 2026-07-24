const pptxgen = require('pptxgenjs');
const path = require('path');

const ICONS = p => path.join(__dirname, '..', 'icons', p + '.png');
const ART = p => path.join(__dirname, '..', 'art', p + '.png');

// Cinematic palette
const RED = 'C8102E';
const RED_HI = 'E8354F';
const BLUE = '2EA8E0';
const WHITE = 'FFFFFF';
const SILVER = 'AEB6C4';
const FAINT = '78808F';
const GHOST = '181E2B';      // ghost display type on dark bg
const GLASS = '141926';      // card fill
const EDGE = '2A3140';       // card border
const JP = 'Yu Gothic';
const EN = 'Arial';
const ENBLK = 'Arial Black';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5

const glowRed = () => ({ size: 9, opacity: 0.45, color: RED });

function bg(s, name) { s.background = { path: ART(name) }; }

function kicker(s, label) {
  s.addShape('ellipse', { x: 0.74, y: 0.66, w: 0.1, h: 0.1, fill: { color: BLUE }, shadow: { type: 'outer', color: BLUE, blur: 8, offset: 0, angle: 0, opacity: 0.85 } });
  s.addText(label, {
    x: 0.98, y: 0.52, w: 10.5, h: 0.4, margin: 0, fontFace: EN, fontSize: 10.5, bold: true,
    charSpacing: 4, color: SILVER, valign: 'middle'
  });
}

function ghost(s, word, x, y, size, w) {
  s.addText(word, {
    x, y, w: w || 12.0, h: size / 50, margin: 0, fontFace: ENBLK, fontSize: size,
    bold: true, color: GHOST, charSpacing: 6, align: 'right', valign: 'middle'
  });
}

function slideTitle(s, text) {
  s.addText(text, {
    x: 0.7, y: 0.95, w: 11.95, h: 0.8, margin: 0, fontFace: JP, fontSize: 28, bold: true,
    color: WHITE, valign: 'middle'
  });
}

function glass(s, x, y, w, h, opts) {
  s.addShape('roundRect', {
    x, y, w, h, rectRadius: 0.1,
    fill: { color: GLASS, transparency: 14 },
    line: { color: (opts && opts.edge) || EDGE, width: (opts && opts.edgeW) || 1 },
    ...(opts && opts.glow ? { shadow: { type: 'outer', color: RED, blur: 22, offset: 0, angle: 0, opacity: 0.35 } } : {})
  });
}

function iconCircle(s, icon, x, y, d) {
  s.addShape('ellipse', { x, y, w: d, h: d, fill: { color: RED }, shadow: { type: 'outer', color: RED, blur: 12, offset: 0, angle: 0, opacity: 0.5 } });
  const inset = d * 0.27;
  s.addImage({ path: ICONS(icon), x: x + inset, y: y + inset, w: d - 2 * inset, h: d - 2 * inset });
}

function pageNo(s, n) {
  s.addText(String(n).padStart(2, '0'), {
    x: 12.5, y: 7.02, w: 0.6, h: 0.32, margin: 0, fontFace: EN, fontSize: 10, color: FAINT, align: 'right', valign: 'middle'
  });
}

// ================= S1 — TITLE =================
{
  const s = pres.addSlide();
  bg(s, 'bg_hero');
  s.addImage({ path: ART('ring'), x: 7.75, y: 0.85, w: 5.8, h: 5.8 });

  s.addShape('ellipse', { x: 0.74, y: 0.78, w: 0.1, h: 0.1, fill: { color: BLUE }, shadow: { type: 'outer', color: BLUE, blur: 8, offset: 0, angle: 0, opacity: 0.85 } });
  s.addText('TSUBURAYA PRODUCTIONS  ×  ROKID', {
    x: 0.98, y: 0.64, w: 10.0, h: 0.4, margin: 0, fontFace: EN, fontSize: 11, bold: true, charSpacing: 4, color: SILVER, valign: 'middle'
  });

  s.addText('ULTRAMAN SERIES 60TH ANNIVERSARY PROJECT', {
    x: 0.72, y: 2.0, w: 8.5, h: 0.35, margin: 0, fontFace: EN, fontSize: 12, bold: true, charSpacing: 3, color: RED_HI, valign: 'middle'
  });
  s.addText('視界に、\nヒーローを。', {
    x: 0.68, y: 2.4, w: 8.3, h: 2.6, margin: 0, fontFace: JP, fontSize: 60, bold: true, color: WHITE, lineSpacing: 78, valign: 'top'
  });
  s.addImage({ path: ART('beam'), x: 0.45, y: 4.95, w: 7.2, h: 1.08 });
  s.addText('ULTRAMAN × Rokid Glasses　共同プロモーションのご提案', {
    x: 0.72, y: 5.95, w: 8.5, h: 0.45, margin: 0, fontFace: JP, fontSize: 16, color: SILVER, valign: 'middle'
  });
  s.addText('円谷プロダクション ライセンス事業部　·　2026.07　·　CONFIDENTIAL', {
    x: 0.72, y: 6.85, w: 9.0, h: 0.35, margin: 0, fontFace: EN, fontSize: 10.5, charSpacing: 1, color: FAINT, valign: 'middle'
  });
}

// ================= S2 — STORY =================
{
  const s = pres.addSlide();
  bg(s, 'bg_dark');
  ghost(s, '1967', 4.6, 0.35, 130, 8.1);
  kicker(s, '01 / STORY');

  s.addText('「グラスをかけて変身する」物語を、\n60年前から持つIPは、世界にひとつ。', {
    x: 0.7, y: 1.75, w: 7.0, h: 1.7, margin: 0, fontFace: JP, fontSize: 25, bold: true, color: WHITE, lineSpacing: 40, valign: 'top'
  });
  s.addText('1967年、ウルトラセブンはメガネ型のデバイス「ウルトラアイ」を装着して変身しました。「グラスをかけると、世界が変わり、自分が変わる」——この物語を60年前から持っているのは、ウルトラマンだけです。', {
    x: 0.7, y: 3.6, w: 6.7, h: 1.6, margin: 0, fontFace: JP, fontSize: 13.5, color: SILVER, lineSpacing: 23, valign: 'top'
  });
  s.addText([
    { text: 'これは単なるキャラクターコラボではありません。', options: { color: SILVER } },
    { text: 'Rokid Glasses の装着体験そのものに「変身」という物語を与える', options: { color: WHITE, bold: true } },
    { text: 'ご提案です。', options: { color: SILVER } }
  ], { x: 0.7, y: 5.15, w: 6.7, h: 1.3, margin: 0, fontFace: JP, fontSize: 13.5, lineSpacing: 23, valign: 'top' });
  s.addText('※ ウルトラアイ = ウルトラセブンの変身アイテム（1967年放送開始）', {
    x: 0.7, y: 6.6, w: 6.7, h: 0.3, margin: 0, fontFace: JP, fontSize: 9.5, color: FAINT, valign: 'middle'
  });

  glass(s, 7.9, 1.55, 4.75, 5.35);
  s.addImage({ path: ART('ring'), x: 9.32, y: 1.75, w: 1.9, h: 1.9 });
  s.addText([
    { text: '1967', options: { bold: true, color: WHITE, fontSize: 19, fontFace: EN } },
    { text: '　ウルトラアイ', options: { color: SILVER, fontSize: 13 } }
  ], { x: 8.2, y: 3.75, w: 4.15, h: 0.4, margin: 0, fontFace: JP, align: 'center', valign: 'middle' });
  s.addText('↓', { x: 8.2, y: 4.14, w: 4.15, h: 0.3, margin: 0, fontFace: EN, fontSize: 14, bold: true, color: RED_HI, align: 'center', valign: 'middle' });
  s.addText([
    { text: '2026', options: { bold: true, color: WHITE, fontSize: 19, fontFace: EN } },
    { text: '　Rokid Glasses', options: { color: SILVER, fontSize: 13, fontFace: EN } }
  ], { x: 8.2, y: 4.45, w: 4.15, h: 0.4, margin: 0, fontFace: JP, align: 'center', valign: 'middle' });
  s.addShape('line', { x: 8.75, y: 5.15, w: 3.05, h: 0, line: { color: EDGE, width: 1 } });
  s.addText('KEY COPY', { x: 8.2, y: 5.3, w: 4.15, h: 0.3, margin: 0, fontFace: EN, fontSize: 9.5, bold: true, charSpacing: 3, color: FAINT, align: 'center', valign: 'middle' });
  s.addText('変身は、\n現実になった。', {
    x: 8.05, y: 5.6, w: 4.45, h: 1.15, margin: 0, fontFace: JP, fontSize: 22, bold: true, color: WHITE,
    glow: glowRed(), align: 'center', lineSpacing: 30, valign: 'top'
  });
  pageNo(s, 2);
}

// ================= S3 — WHERE ROKID STANDS =================
{
  const s = pres.addSlide();
  bg(s, 'bg_dark');
  ghost(s, 'ROKID', 3.6, 0.3, 110, 9.1);
  kicker(s, '02 / WHERE ROKID STANDS');
  slideTitle(s, '機能の戦いは、勝ちつつある。次は「物語」の戦い。');

  const mk = (x, head, headColor, items, mark, edge, edgeW) => {
    glass(s, x, 1.95, 5.94, 3.85, { edge, edgeW });
    s.addText(head, { x: x + 0.45, y: 2.25, w: 5.0, h: 0.45, margin: 0, fontFace: JP, fontSize: 16, bold: true, color: headColor, valign: 'middle' });
    let iy = 2.9;
    for (const it of items) {
      s.addText(mark, { x: x + 0.45, y: iy, w: 0.32, h: 0.4, margin: 0, fontFace: EN, fontSize: 12.5, bold: true, color: RED_HI, valign: 'top' });
      s.addText(it, { x: x + 0.8, y: iy, w: 4.8, h: 0.6, margin: 0, fontFace: JP, fontSize: 12.5, color: 'E7EAF0', lineSpacing: 17, valign: 'top' });
      iy += 0.68;
    }
  };
  mk(0.7, '獲得済みのもの', WHITE, [
    'Makuake 歴代応援購入額1位の話題性',
    '全国約75店舗 + 5都市ポップアップの販路',
    '翻訳・AIメモ・ARナビの機能的説得力',
    '109,890円に見合うスペック（49g・両眼表示）'
  ], '✓');
  mk(6.69, 'これからの課題', RED_HI, [
    '早期採用層の外側に届く「物語」',
    '店頭で足を止めさせ、装着させる引力',
    '「毎日かけたい」と思わせる情動的な理由',
    '年末商戦、競合スマートグラス攻勢前の差別化'
  ], '→', '5A2430', 1.25);

  s.addText([
    { text: '次に必要なのは、かける理由の', options: { color: WHITE } },
    { text: '「物語化」', options: { color: RED_HI } },
    { text: '。そこに最も構造的に噛み合うIPが、ウルトラマンです。', options: { color: WHITE } }
  ], { x: 0.7, y: 6.2, w: 11.9, h: 0.55, margin: 0, fontFace: JP, fontSize: 16.5, bold: true, valign: 'middle' });
  pageNo(s, 3);
}

// ================= S4 — WHY ULTRAMAN =================
{
  const s = pres.addSlide();
  bg(s, 'bg_dark');
  ghost(s, 'WHY', 5.6, 0.3, 110, 7.1);
  kicker(s, '03 / WHY ULTRAMAN');
  slideTitle(s, 'なぜ、ウルトラマンなのか');

  glass(s, 0.7, 1.9, 11.93, 1.62, { edge: '5A2430', edgeW: 1.25, glow: true });
  iconCircle(s, 'FaGlasses', 1.08, 2.24, 0.94);
  s.addText([
    { text: '01｜', options: { color: RED_HI, fontFace: EN } },
    { text: '「装着して変身する」物語を持つ、世界で唯一のIP', options: { color: WHITE } }
  ], { x: 2.35, y: 2.1, w: 10.0, h: 0.45, margin: 0, fontFace: JP, fontSize: 16.5, bold: true, valign: 'middle' });
  s.addText([
    { text: 'ウルトラアイ（1967年〜）以来、アイウェアの装着は変身の起点。装着デモがそのまま広告になります——', options: { color: SILVER } },
    { text: '「さあ、変身してください」', options: { color: WHITE, bold: true } }
  ], { x: 2.35, y: 2.6, w: 10.0, h: 0.75, margin: 0, fontFace: JP, fontSize: 12.5, lineSpacing: 18, valign: 'top' });

  const cards = [
    { icon: 'FaUsers', n: '02', head: '購買層とファン層の完全一致', desc: 'ガジェット感度の高い30〜50代は、ウルトラマン直撃世代。親子3世代へ体験が波及します。' },
    { icon: 'FaCogs', n: '03', head: '全機能にIP文脈を与えられる', desc: '通知・撮影・ナビ・空間表示のすべてが感情体験に変わる。機能デモが物語のデモになります。' },
    { icon: 'FaGlobeAsia', n: '04', head: '本国・中国での圧倒的地盤', desc: 'ウルトラマンは中国で世代を超えた人気IP。日本コラボの成功が、グローバル展開の「第1話」に。' },
    { icon: 'FaShieldAlt', n: '05', head: '円谷公式監修 + 3Dアセット供与', desc: '表現品質は円谷が公式監修で担保。「本物」であることが、ファンへの最大の品質保証です。' }
  ];
  const cw = 5.86, ch = 1.58, gx = 0.21, gy = 0.18;
  cards.forEach((c, i) => {
    const x = 0.7 + (i % 2) * (cw + gx);
    const y = 3.78 + Math.floor(i / 2) * (ch + gy);
    glass(s, x, y, cw, ch);
    iconCircle(s, c.icon, x + 0.3, y + 0.3, 0.6);
    s.addText([
      { text: c.n + '｜', options: { color: RED_HI, fontFace: EN } },
      { text: c.head, options: { color: WHITE } }
    ], { x: x + 1.1, y: y + 0.17, w: cw - 1.3, h: 0.4, margin: 0, fontFace: JP, fontSize: 13.5, bold: true, valign: 'middle' });
    s.addText(c.desc, { x: x + 1.1, y: y + 0.58, w: cw - 1.35, h: 0.9, margin: 0, fontFace: JP, fontSize: 11, color: SILVER, lineSpacing: 15.5, valign: 'top' });
  });
  pageNo(s, 4);
}

// ================= S5 — PRODUCT × IP =================
{
  const s = pres.addSlide();
  bg(s, 'bg_dark');
  ghost(s, 'MODE', 4.6, 0.3, 110, 8.1);
  kicker(s, '04 / PRODUCT × IP');
  slideTitle(s, '機能デモが、そのまま感情体験になる');

  const rows = [
    { icon: 'FaBell', fn: '通知・ステータス表示', ip: 'カラータイマー', desc: '残量・通知が、あの点滅と音でわかる' },
    { icon: 'FaCamera', fn: '12MPカメラ撮影', ip: '光線ポーズ撮影', desc: '光線を合成してSNSへ（UGC装置）' },
    { icon: 'FaRoute', fn: 'ARナビ', ip: '防衛隊HUDモード', desc: '毎日の移動がミッションになる' },
    { icon: 'FaExpandArrowsAlt', fn: '空間ディスプレイ', ip: '巨大ウルトラマン召喚', desc: '都市スケールの空間演出デモ' }
  ];
  let ry = 1.95;
  rows.forEach((r) => {
    glass(s, 0.7, ry, 11.93, 0.92);
    iconCircle(s, r.icon, 1.0, ry + 0.17, 0.58);
    s.addText(r.fn, { x: 1.82, y: ry, w: 3.3, h: 0.92, margin: 0, fontFace: JP, fontSize: 13.5, bold: true, color: 'E7EAF0', valign: 'middle' });
    s.addText('→', { x: 5.12, y: ry, w: 0.6, h: 0.92, margin: 0, fontFace: EN, fontSize: 17, bold: true, color: RED_HI, align: 'center', valign: 'middle' });
    s.addText(r.ip, { x: 5.82, y: ry, w: 3.3, h: 0.92, margin: 0, fontFace: JP, fontSize: 15.5, bold: true, color: RED_HI, valign: 'middle' });
    s.addText(r.desc, { x: 9.15, y: ry, w: 3.3, h: 0.92, margin: 0, fontFace: JP, fontSize: 11, color: SILVER, lineSpacing: 15, valign: 'middle' });
    ry += 1.04;
  });

  s.addText([
    { text: '店頭で人を立ち止まらせるのは、「翻訳できます」より ', options: { color: WHITE } },
    { text: '「変身できます」。', options: { color: RED_HI, glow: glowRed() } }
  ], { x: 0.7, y: 6.35, w: 11.9, h: 0.6, margin: 0, fontFace: JP, fontSize: 18.5, bold: true, valign: 'middle' });
  pageNo(s, 5);
}

// ================= S6 — PROMOTION CAMPAIGN =================
{
  const s = pres.addSlide();
  bg(s, 'bg_dark');
  ghost(s, '360', 5.6, 0.3, 120, 7.1);
  kicker(s, '05 / PROMOTION');
  slideTitle(s, '統合キャンペーン「さあ、変身してください。」');

  const cards = [
    {
      icon: 'FaBullhorn', head: 'TVCM・広告・OOH',
      desc: 'ウルトラマンが Rokid Glasses をかけて変身するTVCM / WEB CM。屋外は都心の巨大ウルトラマンAR演出と連動し、発売を「事件」として見せる。'
    },
    {
      icon: 'FaUsers', head: 'イベント・PR',
      desc: '共同発表会にウルトラマンが登壇。7月10日「変身の日」と60周年展のステージに連動させ、発表そのものをニュース化する。'
    },
    {
      icon: 'FaStore', head: '店頭・体験',
      desc: '5都市ポップアップ + 量販約75店舗で「変身体験」デモを標準化。フィナーレの巨大ウルトラマン召喚が購入転換の山場になる。'
    },
    {
      icon: 'FaHashtag', head: 'SNS・UGC',
      desc: '「#変身してみた」光線撮影チャレンジ。公式素材の提供とリポスト運用で、購入者自身がキャンペーンの広告塔になる。'
    }
  ];
  const cw = 5.86, ch = 1.98, gx = 0.21, gy = 0.2;
  cards.forEach((c, i) => {
    const x = 0.7 + (i % 2) * (cw + gx);
    const y = 1.95 + Math.floor(i / 2) * (ch + gy);
    glass(s, x, y, cw, ch);
    iconCircle(s, c.icon, x + 0.3, y + 0.3, 0.62);
    s.addText(c.head, { x: x + 1.12, y: y + 0.2, w: cw - 1.3, h: 0.4, margin: 0, fontFace: JP, fontSize: 14.5, bold: true, color: WHITE, valign: 'middle' });
    s.addText(c.desc, { x: x + 1.12, y: y + 0.62, w: cw - 1.4, h: 1.25, margin: 0, fontFace: JP, fontSize: 11, color: SILVER, lineSpacing: 16.5, valign: 'top' });
  });

  s.addText([
    { text: '限定モデルは「点」にすぎません。', options: { color: WHITE } },
    { text: '広告・イベント・店頭・SNSの全面で、ウルトラマンが「面」を張ります。', options: { color: RED_HI } }
  ], { x: 0.7, y: 6.5, w: 11.9, h: 0.55, margin: 0, fontFace: JP, fontSize: 16.5, bold: true, valign: 'middle' });
  pageNo(s, 6);
}

// ================= S7 — WHY NOW =================
{
  const s = pres.addSlide();
  bg(s, 'bg_dark');
  ghost(s, '2026', 4.6, 0.3, 120, 8.1);
  kicker(s, '06 / WHY NOW');
  slideTitle(s, 'なぜ、今なのか — 2026年にしかない3つの理由');

  const cards = [
    {
      num: '60th', head: 'シリーズ60周年イヤー',
      desc: '60周年プロジェクトが進行中。新シリーズ『ウルトラマンティオ』放送中、60周年展が全国巡回中。露出と熱量が60年間で最大の年。公式文脈に入れる枠は、今年だけ。'
    },
    {
      num: '7.10', head: '運命の発売日',
      desc: 'Rokid Glasses の日本発売日は「ウルトラマンの日」と同日。この偶然を必然に変え、毎年7月10日を「変身の日」として更新し続ける記念日設計ができる。'
    },
    {
      num: '1st', head: '最初のIP体験の定義権',
      desc: 'ARグラスは機能訴求から体験訴求へ移る直前。カテゴリ最初の代表的IP体験を作ったブランドが、以後数年の連想を独占する。年末商戦前が最後の窓。'
    }
  ];
  const cw = 3.84, gap = 0.2;
  cards.forEach((c, i) => {
    const x = 0.7 + i * (cw + gap);
    glass(s, x, 2.15, cw, 4.35);
    s.addText(c.num, {
      x: x + 0.35, y: 2.5, w: cw - 0.7, h: 0.95, margin: 0, fontFace: ENBLK, fontSize: 44, bold: true,
      color: RED_HI, glow: glowRed(), valign: 'middle'
    });
    s.addText(c.head, { x: x + 0.35, y: 3.6, w: cw - 0.7, h: 0.45, margin: 0, fontFace: JP, fontSize: 15.5, bold: true, color: WHITE, valign: 'middle' });
    s.addText(c.desc, { x: x + 0.35, y: 4.15, w: cw - 0.66, h: 2.2, margin: 0, fontFace: JP, fontSize: 11, color: SILVER, lineSpacing: 17, valign: 'top' });
  });
  pageNo(s, 7);
}

// ================= S8 — PLANS =================
{
  const s = pres.addSlide();
  bg(s, 'bg_dark');
  ghost(s, 'PLAN', 4.6, 0.3, 110, 8.1);
  kicker(s, '07 / PROPOSAL');
  slideTitle(s, 'ご提案 — 2つのプラン');

  // Plan S
  glass(s, 0.7, 1.85, 5.85, 4.8);
  iconCircle(s, 'FaBolt', 1.06, 2.16, 0.62);
  s.addText([
    { text: 'PLAN S', options: { color: FAINT, fontSize: 11, bold: true, fontFace: EN, charSpacing: 2 } },
    { text: '　SPARK', options: { color: WHITE, fontSize: 19, bold: true, fontFace: EN, charSpacing: 1 } }
  ], { x: 1.85, y: 2.16, w: 4.5, h: 0.62, margin: 0, valign: 'middle' });
  s.addText([
    { text: '3,000', options: { fontSize: 35, bold: true, color: WHITE, fontFace: EN } },
    { text: ' 万円', options: { fontSize: 15, bold: true, color: SILVER } },
    { text: '（税別）', options: { fontSize: 10, color: FAINT } }
  ], { x: 1.06, y: 2.95, w: 5.0, h: 0.6, margin: 0, fontFace: JP, valign: 'middle' });
  s.addText([
    { text: 'WEB CM・SNS広告へのキャラクター使用（「さあ、変身してください。」）', options: { bullet: { code: '25AA', indent: 12 }, breakLine: true } },
    { text: 'SNSキャンペーン「#変身してみた」設計 + 公式素材供与', options: { bullet: { code: '25AA', indent: 12 }, breakLine: true } },
    { text: 'AR体験パック「ULTRAMAN MODE」開発・供与（光線撮影／カラータイマー通知／防衛隊ナビ）', options: { bullet: { code: '25AA', indent: 12 }, breakLine: true } },
    { text: '5都市ポップアップ「変身体験」+ 7月10日共同PR', options: { bullet: { code: '25AA', indent: 12 }, breakLine: true } },
    { text: '円谷公式監修 + 3Dアセット供与', options: { bullet: { code: '25AA', indent: 12 }, breakLine: true } },
    { text: '許諾範囲: プロモ + デジタル／日本国内12ヶ月', options: { bullet: { code: '25AA', indent: 12 } } }
  ], { x: 1.06, y: 3.7, w: 5.15, h: 2.85, margin: 0, fontFace: JP, fontSize: 11, color: 'E7EAF0', paraSpaceAfter: 6, lineSpacing: 15.5, valign: 'top' });

  // Plan U — recommended
  glass(s, 6.78, 1.65, 5.85, 5.0, { edge: RED, edgeW: 1.5, glow: true });
  s.addShape('roundRect', { x: 11.42, y: 1.86, w: 0.95, h: 0.38, rectRadius: 0.19, fill: { color: RED } });
  s.addText('推奨', { x: 11.42, y: 1.86, w: 0.95, h: 0.38, margin: 0, fontFace: JP, fontSize: 11.5, bold: true, color: WHITE, align: 'center', valign: 'middle' });
  iconCircle(s, 'FaGem', 7.14, 2.36, 0.62);
  s.addText([
    { text: 'PLAN U', options: { color: FAINT, fontSize: 11, bold: true, fontFace: EN, charSpacing: 2 } },
    { text: '　ULTRAMAN EDITION', options: { color: WHITE, fontSize: 17, bold: true, fontFace: EN, charSpacing: 1 } }
  ], { x: 7.93, y: 2.36, w: 4.45, h: 0.62, margin: 0, valign: 'middle' });
  s.addText([
    { text: '8,000', options: { fontSize: 35, bold: true, color: RED_HI, fontFace: EN, glow: glowRed() } },
    { text: ' 万円', options: { fontSize: 15, bold: true, color: WHITE } },
    { text: '（税別）', options: { fontSize: 10, color: SILVER } }
  ], { x: 7.14, y: 3.12, w: 5.0, h: 0.6, margin: 0, fontFace: JP, valign: 'middle' });
  s.addText([
    { text: 'Plan S のすべて、に加えて——', options: { bullet: false, color: SILVER, italic: true, breakLine: true } },
    { text: 'TVCM・OOHへのキャラクター使用（都心での巨大ウルトラマンAR演出）', options: { bullet: { code: '25AA', indent: 12 }, breakLine: true } },
    { text: '共同発表会・店頭イベントへのウルトラマン登壇（ショー派遣）', options: { bullet: { code: '25AA', indent: 12 }, breakLine: true } },
    { text: '限定モデル「ULTRAMAN EDITION」3,000台（カラータイマー型ケース・変身音・シリアルNo.・60周年ロゴ）', options: { bullet: { code: '25AA', indent: 12 }, breakLine: true } },
    { text: '60周年展 出展枠・『ウルトラマンティオ』放送連動 ※', options: { bullet: { code: '25AA', indent: 12 }, breakLine: true } },
    { text: '中国・北米・欧州 Rokid 販路の優先交渉権', options: { bullet: { code: '25AA', indent: 12 } } }
  ], { x: 7.14, y: 3.85, w: 5.2, h: 2.7, margin: 0, fontFace: JP, fontSize: 11, color: 'E7EAF0', paraSpaceAfter: 6, lineSpacing: 15.5, valign: 'top' });

  s.addText('※ 60周年イベント・番組連動の実施形態は円谷社内の企画枠調整を経て確定。ハード製造原価・アプリ実装費は Rokid 様負担、売上ロイヤリティ設計は別途協議（MG充当方式も可）。', {
    x: 0.7, y: 6.9, w: 11.95, h: 0.42, margin: 0, fontFace: JP, fontSize: 9, color: FAINT, lineSpacing: 12.5, valign: 'top'
  });
  pageNo(s, 8);
}

// ================= S9 — IMPACT =================
{
  const s = pres.addSlide();
  bg(s, 'bg_dark');
  ghost(s, 'IMPACT', 3.6, 0.3, 105, 9.1);
  kicker(s, '08 / IMPACT');
  slideTitle(s, '期待効果（初年度目安）');

  const stats = [
    { icon: 'FaStore', num: '10万', unit: '人', label: '店頭・イベントでの\n装着体験' },
    { icon: 'FaHashtag', num: '1万', unit: '件', label: '光線撮影UGC\n（SNS投稿）' },
    { icon: 'FaYenSign', num: '3.3億', unit: '円', label: '限定モデル小売規模\n（3,000台完売時）' },
    { icon: 'FaBullhorn', num: '5億', unit: '円+', label: 'メディア露出換算\n（Plan U 実施時）' }
  ];
  const cw = 2.98;
  stats.forEach((st, i) => {
    const x = 0.7 + i * cw;
    if (i > 0) s.addShape('line', { x, y: 2.35, w: 0, h: 2.9, line: { color: EDGE, width: 1 } });
    iconCircle(s, st.icon, x + cw / 2 - 0.33, 2.35, 0.66);
    s.addText([
      { text: st.num, options: { fontSize: 38, bold: true, color: WHITE, fontFace: EN } },
      { text: ' ' + st.unit, options: { fontSize: 17, bold: true, color: RED_HI } }
    ], { x: x + 0.1, y: 3.25, w: cw - 0.2, h: 0.8, margin: 0, fontFace: JP, align: 'center', valign: 'middle' });
    s.addText(st.label, { x: x + 0.2, y: 4.15, w: cw - 0.4, h: 0.85, margin: 0, fontFace: JP, fontSize: 11.5, color: SILVER, align: 'center', lineSpacing: 16, valign: 'top' });
  });

  s.addShape('line', { x: 0.7, y: 5.7, w: 11.93, h: 0, line: { color: EDGE, width: 1 } });
  s.addText([
    { text: '収益は入口にすぎません。本質的な価値は、', options: { color: WHITE } },
    { text: '「ARグラスの最初のIP体験」という歴史的ポジション', options: { color: RED_HI, bold: true } },
    { text: ' を両社で独占することです。', options: { color: WHITE } }
  ], { x: 0.7, y: 5.95, w: 11.95, h: 0.95, margin: 0, fontFace: JP, fontSize: 15.5, bold: true, lineSpacing: 24, valign: 'top' });
  pageNo(s, 9);
}

// ================= S10 — TIMELINE =================
{
  const s = pres.addSlide();
  bg(s, 'bg_dark');
  ghost(s, 'Q4 2026', 3.1, 0.3, 100, 9.6);
  kicker(s, '09 / TIMELINE');
  slideTitle(s, '年末商戦から、逆算する');

  const nodes = [
    { m: '2026.8', t: '基本合意', d: '企画確定' },
    { m: '2026.9', t: '契約締結', d: '監修開始' },
    { m: '2026.10', t: '開発・製造', d: 'ULTRAMAN MODE /\n限定モデル着手' },
    { m: '2026.11', t: '発表', d: '年末商戦 ×\n60周年の頂点で' },
    { m: '2026.12', t: '発売・配信', d: '限定モデル /\n体験パック' },
    { m: '2027.7.10', t: '「変身の日」', d: '1周年施策 →\n継続契約へ', blue: true }
  ];
  const y = 3.75, x0 = 1.15, span = 10.9 / (nodes.length - 1);
  s.addShape('line', { x: x0, y: y + 0.13, w: 10.9, h: 0, line: { color: '3A4257', width: 1.5 } });
  nodes.forEach((n, i) => {
    const cx = x0 + i * span;
    const dotColor = n.blue ? BLUE : RED;
    s.addShape('ellipse', {
      x: cx - 0.13, y, w: 0.26, h: 0.26, fill: { color: dotColor },
      shadow: { type: 'outer', color: dotColor, blur: 12, offset: 0, angle: 0, opacity: 0.8 }
    });
    s.addText(n.m, { x: cx - 0.95, y: y - 0.88, w: 1.9, h: 0.35, margin: 0, fontFace: EN, fontSize: 12.5, bold: true, color: n.blue ? BLUE : RED_HI, align: 'center', valign: 'middle' });
    s.addText(n.t, { x: cx - 0.95, y: y - 0.53, w: 1.9, h: 0.35, margin: 0, fontFace: JP, fontSize: 13.5, bold: true, color: WHITE, align: 'center', valign: 'middle' });
    s.addText(n.d, { x: cx - 1.0, y: y + 0.48, w: 2.0, h: 0.8, margin: 0, fontFace: JP, fontSize: 10, color: SILVER, align: 'center', lineSpacing: 14, valign: 'top' });
  });

  glass(s, 0.7, 5.75, 11.93, 1.0, { edge: '5A2430', edgeW: 1.25 });
  s.addText([
    { text: '11月発表に間に合わせるには、8月中の基本合意が必要です。', options: { color: RED_HI, bold: true } },
    { text: '　意匠変更をカラー・テンプル・充電ケース・起動音に限定することで、この日程は実現可能です。', options: { color: 'E7EAF0' } }
  ], { x: 1.05, y: 5.75, w: 11.3, h: 1.0, margin: 0, fontFace: JP, fontSize: 13, lineSpacing: 19, valign: 'middle' });
  pageNo(s, 10);
}

// ================= S11 — CLOSING =================
{
  const s = pres.addSlide();
  bg(s, 'bg_hero');
  s.addImage({ path: ART('ring'), x: 9.7, y: -2.4, w: 5.4, h: 5.4 });

  s.addShape('ellipse', { x: 0.74, y: 0.78, w: 0.1, h: 0.1, fill: { color: BLUE }, shadow: { type: 'outer', color: BLUE, blur: 8, offset: 0, angle: 0, opacity: 0.85 } });
  s.addText('CLOSING', { x: 0.98, y: 0.64, w: 6.0, h: 0.4, margin: 0, fontFace: EN, fontSize: 11, bold: true, charSpacing: 4, color: SILVER, valign: 'middle' });

  s.addText('ウルトラアイを装着したかった少年たちは、\nいま、購買決定者になった。', {
    x: 0.7, y: 2.1, w: 11.9, h: 1.9, margin: 0, fontFace: JP, fontSize: 30, bold: true, color: WHITE, lineSpacing: 46, valign: 'top'
  });
  s.addText([
    { text: '7月10日生まれ同士、', options: { color: SILVER } },
    { text: '一緒に歴史を作りましょう。', options: { color: RED_HI, bold: true, glow: glowRed() } }
  ], { x: 0.7, y: 4.3, w: 11.9, h: 0.7, margin: 0, fontFace: JP, fontSize: 22, bold: true, valign: 'middle' });
  s.addImage({ path: ART('beam'), x: 0.45, y: 5.1, w: 7.2, h: 1.08 });

  s.addText('円谷プロダクション ライセンス事業部\n本提案の有効期限: 2026年8月31日（年末商戦・60周年展の日程逆算のため）', {
    x: 0.7, y: 6.35, w: 11.0, h: 0.8, margin: 0, fontFace: JP, fontSize: 11, color: FAINT, lineSpacing: 18, valign: 'top'
  });
}

pres.writeFile({ fileName: path.join(__dirname, '..', '..', '..', 'docs', 'proposals', 'rokid-ultraman-pitch.pptx') }).then(() => console.log('deck v2 written'));
