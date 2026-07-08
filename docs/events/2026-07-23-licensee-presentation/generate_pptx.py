#!/usr/bin/env python3
"""7/23 ULTRAMAN LICENSEE PRESENTATION — 28枚デッキ(.pptx)生成スクリプト.

08-slide-draft.md の内容を PowerPoint に落とす。素材が届いたら該当スライドの
プレースホルダーを差し替えて再エクスポートするか、このスクリプトを更新して再生成する。

    python3 generate_pptx.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.lang import MSO_LANGUAGE_ID
from pptx.oxml.ns import qn
import copy

# ---- palette (deck.html と同一の設計言語) ----
BG    = RGBColor(0x0A, 0x0F, 0x21)
PANEL = RGBColor(0x17, 0x20, 0x3F)
LINE  = RGBColor(0x2A, 0x36, 0x60)
INK   = RGBColor(0xF0, 0xF3, 0xFC)
SUB   = RGBColor(0xAA, 0xB4, 0xD0)
DIM   = RGBColor(0x75, 0x80, 0xA0)
RED   = RGBColor(0xFF, 0x3B, 0x34)
RED2  = RGBColor(0xFF, 0x6A, 0x52)
CYAN  = RGBColor(0x37, 0xC6, 0xEC)
GOLD  = RGBColor(0xF4, 0xC0, 0x4E)

JP_FONT = "Yu Gothic"          # 游ゴシック(無ければ各環境の既定JPフォントへフォールバック)
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
ML = Inches(0.9)               # left margin
CW = Inches(11.53)             # content width

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


def style_run(run, size, color=INK, bold=False, spacing=None, mono=False):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    name = "Consolas" if mono else JP_FONT
    f.name = name
    f.language_id = MSO_LANGUAGE_ID.JAPANESE
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.append(el)
        el.set("typeface", JP_FONT)
    if spacing is not None:
        rPr.set("spc", str(spacing))


def add_text(slide, x, y, w, h, lines, anchor=MSO_ANCHOR.TOP):
    """lines: list of (text, size, color, bold, dict-options)."""
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    first = True
    for spec in lines:
        text, size, color, bold = spec[0], spec[1], spec[2], spec[3]
        opts = spec[4] if len(spec) > 4 else {}
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = opts.get("align", PP_ALIGN.LEFT)
        p.space_before = Pt(opts.get("before", 0))
        p.space_after = Pt(opts.get("after", 4))
        p.line_spacing = opts.get("line", 1.15)
        run = p.add_run()
        run.text = text
        style_run(run, size, color, bold,
                  spacing=opts.get("spc"), mono=opts.get("mono", False))
    return box


def new_slide(part, notes=""):
    slide = prs.slides.add_slide(BLANK)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG
    # top accent bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Pt(3))
    bar.fill.solid(); bar.fill.fore_color.rgb = RED; bar.line.fill.background()
    bar.shadow.inherit = False
    # footer
    n = len(prs.slides.__iter__.__self__._sldIdLst)  # current count
    add_text(slide, ML, Inches(7.06), Inches(6), Inches(0.35),
             [(part.upper(), 9, DIM, False, {"mono": True, "spc": 200})])
    add_text(slide, Inches(11.6), Inches(7.06), Inches(0.9), Inches(0.35),
             [(f"{n:02d} / 28", 9, DIM, False,
               {"mono": True, "align": PP_ALIGN.RIGHT})])
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide


def eyebrow(slide, text, y=Inches(0.55)):
    add_text(slide, ML, y, CW, Inches(0.4),
             [(text.upper(), 12, CYAN, False, {"mono": True, "spc": 300})])


def heading(slide, text, y=Inches(1.0), size=34):
    add_text(slide, ML, y, CW, Inches(1.2), [(text, size, INK, True)])


def bullets(slide, items, y, w=CW, size=17):
    """items: list of (text, is_cyan)."""
    box = slide.shapes.add_textbox(ML + Inches(0.05), y, w, Inches(3.6))
    tf = box.text_frame
    tf.word_wrap = True
    for i, (text, cyan) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(10)
        p.line_spacing = 1.2
        r1 = p.add_run(); r1.text = "●  "
        style_run(r1, size - 5, CYAN if cyan else RED)
        r2 = p.add_run(); r2.text = text
        style_run(r2, size, INK)
    return box


def placeholder(slide, text, y, w=CW, h=Inches(0.85)):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, ML, y, w, h)
    shp.adjustments[0] = 0.12
    shp.fill.solid(); shp.fill.fore_color.rgb = PANEL
    shp.line.color.rgb = GOLD; shp.line.width = Pt(1.2)
    shp.line.dash_style = 4  # dashed
    shp.shadow.inherit = False
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.22); tf.margin_right = Inches(0.22)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = text
    style_run(r, 13, GOLD)


def quote_block(slide, text, y, color=RED, size=24, w=Inches(10.5)):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, ML, y, Pt(5), Inches(1.5))
    bar.fill.solid(); bar.fill.fore_color.rgb = color; bar.line.fill.background()
    bar.shadow.inherit = False
    box = add_text(slide, ML + Inches(0.3), y, w, Inches(1.6),
                   [(text, size, INK, True, {"line": 1.35})],
                   anchor=MSO_ANCHOR.MIDDLE)
    # match bar height to text later renders fine at fixed height
    return box


def card_row(slide, cards, y, h=Inches(1.55), size_t=15, size_b=11.5):
    """cards: list of (kicker, title, body)."""
    n = len(cards)
    gap = Inches(0.25)
    w = Emu(int((CW - gap * (n - 1)) / n))
    for i, (kick, title, body) in enumerate(cards):
        x = ML + Emu(int((w + gap) * i))
        shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        shp.adjustments[0] = 0.08
        shp.fill.solid(); shp.fill.fore_color.rgb = PANEL
        shp.line.color.rgb = LINE; shp.line.width = Pt(1)
        shp.shadow.inherit = False
        tf = shp.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2); tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.14)
        p = tf.paragraphs[0]; p.space_after = Pt(3)
        r = p.add_run(); r.text = kick.upper()
        style_run(r, 9, CYAN, spacing=200, mono=True)
        p2 = tf.add_paragraph(); p2.space_after = Pt(3)
        r2 = p2.add_run(); r2.text = title
        style_run(r2, size_t, INK, bold=True)
        p3 = tf.add_paragraph(); p3.line_spacing = 1.15
        r3 = p3.add_run(); r3.text = body
        style_run(r3, size_b, SUB)


def table_block(slide, headers, rows, y, col_w, size=13):
    n_rows, n_cols = len(rows) + 1, len(headers)
    total_w = Emu(sum(int(c) for c in col_w))
    gfx = slide.shapes.add_table(n_rows, n_cols, ML, y, total_w,
                                 Inches(0.42 * n_rows))
    tbl = gfx.table
    tbl.first_row = False; tbl.horz_banding = False
    for i, w in enumerate(col_w):
        tbl.columns[i].width = Emu(int(w))
    for c, htxt in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.fill.solid(); cell.fill.fore_color.rgb = PANEL
        p = cell.text_frame.paragraphs[0]
        r = p.add_run(); r.text = htxt
        style_run(r, size - 1, CYAN, bold=True)
    for ri, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = tbl.cell(ri, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = BG if ri % 2 else RGBColor(0x0E, 0x14, 0x2C)
            p = cell.text_frame.paragraphs[0]
            r = p.add_run(); r.text = val
            style_run(r, size, GOLD if c == 0 else SUB, bold=(c == 0))


def lamp(slide, x=ML, y=Inches(0.55), d=Inches(0.5)):
    glow = slide.shapes.add_shape(MSO_SHAPE.OVAL, x - Inches(0.08), y - Inches(0.08),
                                  d + Inches(0.16), d + Inches(0.16))
    glow.fill.solid(); glow.fill.fore_color.rgb = RGBColor(0x66, 0x1A, 0x18)
    glow.line.fill.background(); glow.shadow.inherit = False
    core = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, d, d)
    core.fill.solid(); core.fill.fore_color.rgb = RED
    core.line.color.rgb = RED2; core.line.width = Pt(1.5)
    core.shadow.inherit = False


def category_slide(part, kicker, headline, shoki, kikaku, message, notes):
    s = new_slide(part, notes)
    eyebrow(s, kicker)
    heading(s, headline, size=30)
    y = Inches(2.15)
    for label, val in (("商機", shoki), ("企画例", kikaku)):
        add_text(s, ML, y, Inches(1.5), Inches(0.5),
                 [(label, 15, CYAN, True)])
        add_text(s, ML + Inches(1.6), y, Inches(9.9), Inches(0.9),
                 [(val, 15, SUB, False, {"line": 1.25})])
        y += Inches(0.85)
    quote_block(s, message, Inches(4.35), color=CYAN, size=21)
    return s


# =====================================================================
# 1. タイトル
s = new_slide("Opening", "(タイトル表示のみ。MCオープニングへ)")
lamp(s, ML, Inches(0.85))
add_text(s, ML, Inches(1.75), CW, Inches(0.5),
         [("TSUBURAYA PRODUCTIONS · 60TH ANNIVERSARY", 13, CYAN, False,
           {"mono": True, "spc": 350})])
add_text(s, ML, Inches(2.3), CW, Inches(2.9),
         [("ULTRAMAN", 54, INK, True, {"line": 1.05, "after": 0}),
          ("LICENSEE", 54, INK, True, {"line": 1.05, "after": 0}),
          ("PRESENTATION", 54, INK, True, {"line": 1.05})])
add_text(s, ML, Inches(5.75), CW, Inches(0.8),
         [("2027年度以降の商機を、いま一緒につくる。", 25, RED2, True)])

# 2. 今日の目的
s = new_slide("Opening",
              "本日は、単なる作品紹介ではありません。2027年度以降、ウルトラマンを皆さまの商品・売場・"
              "キャンペーンにどう活用いただけるか、その商機を共有する場です。最後に個別商談のご案内も"
              "ありますので、ぜひ「自社ならこう使える」という視点でお聞きください。")
eyebrow(s, "Purpose")
heading(s, "本日は「作品発表会」ではありません")
bullets(s, [
    ("2027年度以降のウルトラマン展開を、パートナーの皆さまに共有する場", False),
    ("商品化・販促・広告タイアップ・流通施策の 商機を持ち帰っていただく場", False),
    ("本日の終わりに:個別商談のご予約・企画のご相談を受け付けます", True),
], Inches(2.5), size=19)

# 3. オープニングからの接続
s = new_slide("Opening",
              "いまご覧いただいた熱量は、ステージの中だけで終わるものではありません。商品に、売場に、"
              "キャンペーンに、そして生活者との毎日の接点に変わっていきます。")
eyebrow(s, "From the Stage")
heading(s, "いまの熱量が、商品と売場に変わる")
quote_block(s, "ステージの熱量 → 商品 → 売場 → キャンペーン\n→ 生活者との毎日の接点へ",
            Inches(3.0), size=26)

# 4. 60周年の現在地
s = new_slide("Now",
              "60周年はすでに動き出しています。イベント、商品化、コラボ、流通。この盛り上がりは今年で"
              "終わるものではなく、2027年度以降につながっていきます。")
eyebrow(s, "60th Anniversary")
heading(s, "60周年は、もう始まっている")
card_row(s, [
    ("Events", "国内外イベント", "ウルサマ/ライブ/展覧会/ヒーローショー/グリーティング"),
    ("Products", "商品化", "食品・アパレル・雑貨・玩具・文具・コレクション"),
], Inches(2.2))
card_row(s, [
    ("Collabs", "IPコラボ", "モフサンド、ベイブレード ほか"),
    ("Retail", "流通", "ウルトラマート、POPUP、量販・専門店"),
], Inches(3.95))
placeholder(s, "📷【素材8待ち】実績写真グリッド(8〜12点)に差し替え。数字より「動いている感」重視。",
            Inches(5.75))

# 5. なぜ今ウルトラマンなのか
s = new_slide("Now",
              "ウルトラマンの強みは、単なるリーチの広さではありません。年間約70万〜100万人規模のリアル"
              "接点を通じて、“直接会いに来るファン”との濃い関係を持っていることです。"
              "※注意:「100万人に届きます」という単独リーチ表現は使わない。")
eyebrow(s, "Why Ultraman, Why Now")
heading(s, "熱量あるリアル接点を持つIP")
table_block(s,
            ["レイヤー", "役割", "例"],
            [["マス接点", "認知を広げる", "テレビ、映画、YouTube、SNS、PR"],
             ["熱量接点", "ファン化する", "ウルサマ、ライブ、ショー、グリーティング"],
             ["購買接点", "商品化につなげる", "店頭、POPUP、ウルトラマート、EC"],
             ["継続接点", "次の商品・作品へ戻す", "新シリーズ、映画、イベント、限定商品"]],
            Inches(2.2), [Inches(2.2), Inches(3.2), Inches(6.1)])
placeholder(s, "📊【補強データ待ち】年間約70万〜100万人規模のリアル接点 — 満席率・稼働率の確定後に表現調整",
            Inches(5.75))

# 6. 全体戦略
s = new_slide("Content Strategy",
              "2027年度以降、ウルトラマンは単発の作品展開ではなく、テレビ、映画、イベント、YouTube、"
              "流通、IPコラボを連動させた“面の展開”に入ります。")
eyebrow(s, "Strategy 2027+")
heading(s, "単発の作品展開から、“面の展開”へ")
quote_block(s, "テレビ・映画・イベント・YouTube・流通・IPコラボが\n連動して動く「年間型IP」へ",
            Inches(3.0), size=24)

# 7. 3つの柱
s = new_slide("Content Strategy", "ここからは、2027年度以降のコンテンツ展開を3つの柱でご説明します。")
eyebrow(s, "Content Pillars")
heading(s, "3つの柱")
card_row(s, [
    ("Pillar 1", "新テレビシリーズ", "継続性を重視した世界観・キャラクター展開"),
    ("Pillar 2", "映画・特別編・ゼロ関連", "公開タイミング=販促・店頭の商機"),
    ("Pillar 3", "YouTube/ギャラファイ", "歴代ヒーロー・怪獣を横断活用"),
], Inches(2.4), h=Inches(1.9))
placeholder(s, "🎬【素材1待ち — 本編の核】2027年以降のコンテンツ全体像。7/14までに必ず回収。",
            Inches(4.7))

# 8. 新テレビシリーズ
s = new_slide("Content Strategy",
              "2027年度以降のテレビシリーズでは、キャラクターや世界観の継続性をより重視し、ファンが次の"
              "展開を追い続けたくなる構造を強化していきます。"
              "【NG】「3年連続で同じ世界線」「テレビ局が変わるかも」には一切触れない。")
eyebrow(s, "Pillar 1 — TV Series")
heading(s, "追い続けたくなる構造へ")
bullets(s, [
    ("キャラクターや世界観の 継続性をより重視", False),
    ("ファンが次の展開を追い続けたくなる構造を強化", False),
], Inches(2.4), size=19)
placeholder(s, "🖼【素材2・3・13待ち/開示確認】制作部の開示可能コピー・世界観イメージ・シルエット等で差し替え",
            Inches(4.4))

# 9. 映画・ゼロ関連
s = new_slide("Content Strategy",
              "映画館、配信、イベント、商品化を連動させ、作品接点を売場・キャンペーンに接続していきます。"
              "特に食品、外食、流通、アパレル、広告の皆さまには、映画のタイミングでご一緒できる企画を"
              "ご用意していきます。")
eyebrow(s, "Pillar 2 — Films")
heading(s, "映画の熱量を、売場とキャンペーンへ")
bullets(s, [
    ("ゼロ関連映画・特別編・スピンオフ(開示可能範囲で)", False),
    ("映画館 × 配信 × イベント × 商品化の連動", False),
    ("公開タイミング=販促・店頭キャンペーンの商機", True),
], Inches(2.4), size=19)
placeholder(s, "🎬【素材4・5待ち/開示確認】ゼロ映画・特別編の開示可能情報", Inches(4.9))

# 10. YouTube/ギャラファイ
s = new_slide("Content Strategy",
              "YouTube・配信領域では、幅広いヒーローとキャラクターを活用し、コアファンにも新規層にも届く"
              "接点を再強化します。ライセンシーの皆さまにとっては、歴代ヒーローや怪獣まで横断的に使える、"
              "企画自由度の高い領域です。")
eyebrow(s, "Pillar 3 — YouTube / Galaxy Fight")
heading(s, "歴代ヒーロー・怪獣を横断的に使える領域", size=30)
bullets(s, [
    ("YouTube・配信で、コアファンにも新規層にも届く接点を再強化", False),
    ("単独ヒーローに限らず、歴代ヒーロー・怪獣・人気キャラを横断活用", False),
    ("コレクション系・大人向け・怪獣デザイン商品との相性", False),
], Inches(2.4), size=19)
placeholder(s, "📺【素材6待ち/開示確認】ギャラファイ/YouTube系の開示可能情報", Inches(4.9))

# 11. イベント・リアル接点
s = new_slide("Content Strategy",
              "ウルトラマンには“直接会いに来るファン”がいます。この熱量あるリアル接点が、商品購買や"
              "店舗送客に直結します。")
eyebrow(s, "Real Touchpoints")
heading(s, "会いに来るファンがいる")
bullets(s, [
    ("ウルサマ、ライブ、展覧会、ヒーローショー、グリーティング", False),
    ("リアル接点 → 物販・店舗送客・キャンペーン参加への転換実績", False),
], Inches(2.4), size=19)
placeholder(s, "📊【補強データ待ち】満席率・稼働率・リピート率が強ければ「キャパ上限に近い」ことを示す",
            Inches(4.4))

# 12. マーケティングカレンダー
s = new_slide("Content Strategy",
              "ご覧の通り、2027年度以降は年間を通じて山場が続きます。商品開発のリードタイムを考えると、"
              "2027年度の山場に間に合わせるには、今から企画に入っていただくのがベストタイミングです。")
eyebrow(s, "Marketing Calendar")
heading(s, "2027年度以降の商機カレンダー")
bullets(s, [
    ("年間の山場(テレビ・映画・イベント・流通施策)を時系列で提示", False),
    ("「いつ盛り上がるか」「いつ企画に入れば間に合うか」が読み取れることが絶対条件", False),
    ("商品開発リードタイムから逆算した「企画開始の目安」を明記", True),
], Inches(2.4), size=18)
placeholder(s, "📅【素材7待ち】60周年マーケティングカレンダー+2027年以降版のビジュアルに差し替え",
            Inches(4.9))

# 13. 営業パート導入
s = new_slide("Sales",
              "ここからは、各カテゴリーの皆さまと一緒に、具体的な商品化・販促企画を作っていきたいと"
              "考えています。「うちならこう作れる」という目線でご覧ください。")
lamp(s, ML, Inches(0.85))
add_text(s, ML, Inches(1.75), CW, Inches(0.45),
         [("BUSINESS OPPORTUNITIES", 12, CYAN, False, {"mono": True, "spc": 300})])
add_text(s, ML, Inches(2.25), CW, Inches(1.1),
         [("ここからは「皆さまの企画」の話です", 36, INK, True)])
bullets(s, [
    ("過去実績のご紹介ではなく、今後ご一緒したい企画の募集です", False),
    ("7カテゴリー別に、商機と企画例をご提案します", False),
], Inches(3.7), size=19)

# 14-20. カテゴリー
category_slide("Sales", "Category 1 / 7 — 食品・飲料",
               "夏のウルトラマン接点を、親子向けキャンペーンに",
               "夏映画、ウルサマ、親子需要、店頭キャンペーン",
               "限定パッケージ/購入特典/親子キャンペーン/映画半券連動/夏休み販促",
               "夏のウルトラマン接点を、親子向け食品・飲料キャンペーンに変えられます。",
               "映画・イベントの山場と店頭を連動させる企画を、ぜひご一緒させてください。")
category_slide("Sales", "Category 2 / 7 — 外食・カフェ",
               "来場・視聴の熱量を、店舗送客に",
               "イベント来場前後、映画公開期、ファミリー来店",
               "コラボメニュー/ノベルティ/来店特典/ヒーローグリーティング連動",
               "来場・視聴の熱量を、店舗送客に接続できます。",
               "イベント会場の周辺送客や、映画公開期のファミリー需要の取り込みにご活用いただけます。")
category_slide("Sales", "Category 3 / 7 — アパレル",
               "大人が着られるデザインIP",
               "大人ファン、親子リンク、女性向け、ストリート、怪獣デザイン",
               "Tシャツ/スウェット/バッグ/キャップ/親子コーデ/限定コレクション",
               "ウルトラマンは子ども向けだけでなく、大人が着られるデザインIPとして展開できます。",
               "怪獣デザインやストリート系まで展開できます。")
category_slide("Sales", "Category 4 / 7 — 雑貨・生活用品",
               "“毎日使う商品”に落とし込む",
               "日常接点、ギフト、オフィス、家庭用品",
               "タンブラー/タオル/ステーショナリー/インテリア/ガジェット小物",
               "ウルトラマンを“毎日使う商品”に落とし込めます。",
               "ファンの日常に入り込む雑貨・生活用品は、継続的な売上を作れる領域です。")
category_slide("Sales", "Category 5 / 7 — 文具・教育・出版",
               "勇気・成長・仲間・正義を、学びの領域へ",
               "キッズ、親子、学習、読書、夏休み",
               "学習帳/絵本/図鑑/ワークブック/読書キャンペーン",
               "勇気、成長、仲間、正義というテーマを教育・文具領域に広げられます。",
               "ウルトラマンのテーマは、教育・文具領域と本質的に相性が良いものです。")
category_slide("Sales", "Category 6 / 7 — 流通・小売",
               "商品だけでなく、売場をつくる",
               "ウルトラマート、POPUP、量販店、専門店、売場ジャック",
               "専用棚/期間限定売場/購入特典/スタンプラリー/限定商品",
               "商品を作るだけでなく、売場を作る準備があります。",
               "ウルトラマートやPOPUPと連動した売場企画を、流通・小売の皆さまとご一緒したいと考えています。")
category_slide("Sales", "Category 7 / 7 — 広告代理店・SP",
               "ウルトラマンを、広告・販促装置として",
               "企業キャンペーン、地域創生、ファミリー向け販促、周年施策",
               "企業タイアップ/店頭キャンペーン/交通広告/SNSキャンペーン/イベント協賛",
               "クライアント課題に合わせて、ウルトラマンを広告・販促装置として活用できます。",
               "ファミリー、地域、周年など、課題起点でのご相談を歓迎します。")

# 21. IPコラボ実績
s = new_slide("Collabs & Retail",
              "60周年では、異なるファン層・異なる売場に向けて、すでに多様なコラボが動いています。"
              "※実績(このスライド)と今後の機会(次)を必ず分ける。")
eyebrow(s, "IP Collaborations — Now")
heading(s, "60周年、多様なコラボがすでに動いている", size=30)
card_row(s, [
    ("Collab", "モフサンド", "【素材8待ち】実績ビジュアル"),
    ("Collab", "ベイブレード", "【素材8待ち】実績ビジュアル"),
    ("Collab", "その他既存コラボ", "商品化・イベント・流通施策"),
], Inches(2.5), h=Inches(1.9))

# 22. 今後のIPコラボ機会
s = new_slide("Collabs & Retail",
              "ここからは、皆さまと一緒に商品化・売場化していきたい領域です。(サンリオ開示可の場合)"
              "サンリオコラボ実現時には、両IPの魅力を活かした商品化・売場展開をライセンシーの皆さまと"
              "広げていきます。")
eyebrow(s, "IP Collaborations — Next")
heading(s, "ここからは、一緒に商品化・売場化したい領域", size=30)
bullets(s, [
    ("サンリオコラボ 【開示確認後に表現確定】", False),
    ("ゼロ映画連動/新テレビシリーズ連動", False),
    ("YouTube・ギャラファイ系", False),
    ("ウルトラマート・流通展開", True),
], Inches(2.5), size=19)

# 23. ウルトラマート
s = new_slide("Collabs & Retail",
              "ウルトラマンの商品を売る場所を、円谷側でも増やしていきます。だから、商品化したものを展開"
              "できる場が広がっています。「作っても売る場所があるのか」という不安には、売場ごとお応えします。")
eyebrow(s, "Ultra Mart & Retail")
heading(s, "売る場所は、円谷側でも増やしていく", size=30)
bullets(s, [
    ("ウルトラマートの方向性/POPUP展開", False),
    ("量販店・専門店での売場展開/映画・イベント期の店頭施策", False),
    ("既存商品の売場事例/今後募集したい商品カテゴリー", False),
], Inches(2.4), size=18)
placeholder(s, "🏬【素材10待ち】ウルトラマート素材・売場事例写真", Inches(4.9))

# 24. スタイルガイド
s = new_slide("Style Guide",
              "今回のコンテンツ展開に合わせて、ライセンシーの皆さまがすぐ企画化できるよう、カテゴリー別の"
              "スタイルガイドと素材提供体制を整えていきます。「素材がある」ではなく「企画しやすいように、"
              "カテゴリー別に使える形にしてある」——ここを目指しています。")
eyebrow(s, "Style Guide Strategy")
heading(s, "「作りたい」を「作れる」に")
table_block(s,
            ["ガイド", "内容"],
            [["ブランドガイド", "ロゴ、世界観、コピー、NG表現"],
             ["キャラクターガイド", "ヒーロー、怪獣、歴代キャラ、新作関連キャラ"],
             ["カテゴリー別ガイド", "食品、アパレル、雑貨、文具、広告、流通"],
             ["シーズン別ガイド", "映画期、夏休み、年末年始、周年施策"]],
            Inches(2.3), [Inches(3.4), Inches(8.1)])

# 25. 素材提供・監修フロー
s = new_slide("Style Guide",
              "企画提出から承認までの流れを標準化しています。個別商談では、NDAのうえでさらに詳細な素材を"
              "ご覧いただけます。")
eyebrow(s, "Materials & Approval Flow")
heading(s, "企画から承認まで、迷わない")
bullets(s, [
    ("商品化テンプレート:パッケージ例/POP例/販促例/SNS例", False),
    ("監修フロー:企画提出 → 初稿確認 → 修正 → 承認(標準リードタイム明記)", False),
    ("開示区分:当日開示/NDA後開示/個別商談時開示", True),
], Inches(2.4), size=18)
placeholder(s, "📄【素材11・12待ち】スタイルガイド進捗・監修フロー資料", Inches(4.9))

# 26. 企画募集テーマ
s = new_slide("Closing",
              "以上のテーマで、いま企画を募集しています。「この枠に自社が入れるか」という段階からのご相談で"
              "構いません。")
eyebrow(s, "Open Call")
heading(s, "いま、募集しています")
card_row(s, [
    ("食品・飲料", "夏の親子キャンペーン", "映画連動販促"),
    ("外食・カフェ", "コラボメニュー", "送客連動企画"),
    ("アパレル", "大人向けコレクション", "親子リンク"),
], Inches(2.3), h=Inches(1.5), size_t=14, size_b=11)
card_row(s, [
    ("文具・教育・出版", "学び×ウルトラマン", "読書・夏休み企画"),
    ("流通・小売", "売場ジャック", "限定売場企画"),
    ("広告・SP", "企業タイアップ", "地域・周年施策"),
], Inches(4.0), h=Inches(1.5), size_t=14, size_b=11)

# 27. 個別商談・相談導線
s = new_slide("Closing",
              "お手元の資料とこちらのQRコードから、個別商談をご予約いただけます。カテゴリーごとに担当が"
              "ついてご相談を承ります。【運営】QRは後方からも読めるサイズで最低30秒表示。次スライドでも"
              "画面隅に残す。")
eyebrow(s, "Next Step")
heading(s, "今日から動けます")
qr = slide_qr = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, ML, Inches(2.3),
                                   Inches(3.2), Inches(3.2))
qr.adjustments[0] = 0.06
qr.fill.solid(); qr.fill.fore_color.rgb = PANEL
qr.line.color.rgb = GOLD; qr.line.width = Pt(1.2); qr.line.dash_style = 4
qr.shadow.inherit = False
tfq = qr.text_frame; tfq.word_wrap = True
tfq.vertical_anchor = MSO_ANCHOR.MIDDLE
for qi, qline in enumerate(["【QRコード】", "個別商談予約", "(希望カテゴリー選択式)"]):
    pq = tfq.paragraphs[0] if qi == 0 else tfq.add_paragraph()
    pq.alignment = PP_ALIGN.CENTER
    rq = pq.add_run(); rq.text = qline
    style_run(rq, 15 if qi < 2 else 12, GOLD, bold=(qi < 2))
bullets(s, [
    ("配布資料に相談窓口・連絡先を記載", False),
    ("NDA締結後、開示可能な詳細素材あり", False),
    ("カテゴリーごとに担当がついてご相談を承ります", True),
], Inches(2.6), w=Inches(6.9), size=17)
# shift bullets right of QR box
for shp in s.shapes:
    if shp.has_text_frame and shp.left == ML + Inches(0.05) and shp.top == Inches(2.6):
        shp.left = Inches(4.6)

# 28. クロージング
s = new_slide("Closing",
              "今、企画に入る企業が、2027年度以降のウルトラマンの売場とキャンペーンを先に作ることが"
              "できます。ぜひ本日を起点に、個別にご相談ください。本日はありがとうございました。")
lamp(s, ML, Inches(0.85))
add_text(s, ML, Inches(1.85), CW, Inches(0.45),
         [("CLOSING", 12, CYAN, False, {"mono": True, "spc": 300})])
add_text(s, ML, Inches(2.35), Inches(11.3), Inches(2.4),
         [("今、企画に入る企業が、", 34, INK, True, {"line": 1.25, "after": 0}),
          ("2027年度以降のウルトラマンの", 34, INK, True, {"line": 1.25, "after": 0}),
          ("売場とキャンペーンを先に作る。", 34, INK, True, {"line": 1.25})])
add_text(s, ML, Inches(5.35), CW, Inches(0.7),
         [("次の売場を、いま一緒につくる。", 24, RED2, True)])

OUT = "ULTRAMAN_LICENSEE_PRESENTATION_draft_v1.pptx"
prs.save(OUT)
print(f"saved {OUT} with {len(prs.slides._sldIdLst)} slides")
