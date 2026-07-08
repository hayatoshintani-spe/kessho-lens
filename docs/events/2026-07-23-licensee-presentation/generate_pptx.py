#!/usr/bin/env python3
"""7/23 ULTRAMAN LICENSEE PRESENTATION — デッキ(.pptx)生成スクリプト v4.

コンセプト:「発表会」ではなく「2027商機の募集開始イベント」。
聞かせる会ではなく、手を挙げさせる会。全27枚+カテゴリー別企画10本。
社内標準フォーマット(白背景・ネイビー基調・ステートメント型タイトル)準拠。

    python3 generate_pptx.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.lang import MSO_LANGUAGE_ID
from pptx.oxml.ns import qn

# ---- design tokens(ネイビー基調)----
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
INK    = RGBColor(0x28, 0x2D, 0x38)
BODY   = RGBColor(0x49, 0x51, 0x60)
MUTED  = RGBColor(0x97, 0x9E, 0xAC)
ACCENT = RGBColor(0x1F, 0x4E, 0x96)   # ロイヤルネイビー
DK     = RGBColor(0x12, 0x24, 0x4B)   # 濃紺
PALE   = RGBColor(0xEB, 0xF0, 0xF8)   # 薄青
GRAYF  = RGBColor(0xF4, 0xF5, 0xF7)
LINEC  = RGBColor(0xE0, 0xE5, 0xEE)

JP_FONT = "Yu Gothic"
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
ML = Inches(0.55)
CW = Inches(12.23)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]

FOOTER_DOC = "円谷プロダクション|ULTRAMAN LICENSEE PRESENTATION 2026(ドラフト)"


def style_run(run, size, color=BODY, bold=False, spacing=None):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    f.name = JP_FONT
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
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = 0; tf.margin_bottom = 0
    first = True
    for spec in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        runs = spec if isinstance(spec, list) else [spec]
        opts = {}
        for rs in runs:
            text, size, color, bold = rs[0], rs[1], rs[2], rs[3]
            opts = rs[4] if len(rs) > 4 else opts
            run = p.add_run()
            run.text = text
            style_run(run, size, color, bold, spacing=opts.get("spc"))
        p.alignment = opts.get("align", PP_ALIGN.LEFT)
        p.space_before = Pt(opts.get("before", 0))
        p.space_after = Pt(opts.get("after", 3))
        p.line_spacing = opts.get("line", 1.25)
    return box


def rect(slide, x, y, w, h, fill, line_color=None, line_w=None, dash=False,
         shape=MSO_SHAPE.RECTANGLE, radius=None):
    shp = slide.shapes.add_shape(shape, x, y, w, h)
    if radius is not None:
        shp.adjustments[0] = radius
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line_color is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line_color
        shp.line.width = line_w or Pt(1)
        if dash:
            shp.line.dash_style = 4
    shp.shadow.inherit = False
    return shp


def new_slide(section, eyebrow_txt, notes=""):
    slide = prs.slides.add_slide(BLANK)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    n = len(prs.slides._sldIdLst)
    add_text(slide, ML, Inches(0.28), CW, Inches(0.3),
             [(eyebrow_txt, 11, ACCENT, True, {"spc": 60})])
    rect(slide, ML, Inches(7.14), CW, Pt(0.8), LINEC)
    add_text(slide, ML, Inches(7.2), Inches(10.5), Inches(0.25),
             [(f"{FOOTER_DOC}|{section}", 7.5, MUTED, False)])
    add_text(slide, Inches(12.3), Inches(7.2), Inches(0.48), Inches(0.25),
             [(str(n), 8, MUTED, False, {"align": PP_ALIGN.RIGHT})])
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide


def title(slide, text, size=21):
    add_text(slide, ML, Inches(0.58), CW, Inches(0.95),
             [(text, size, INK, True, {"line": 1.2})])


def rule(slide, y=1.52):
    rect(slide, ML, Inches(y), Inches(1.2), Pt(3.2), ACCENT)


def lead(slide, text, y=1.72):
    add_text(slide, ML, Inches(y), CW, Inches(0.4),
             [(text, 12.5, DK, True)])


def sections(slide, blocks, y=2.25, x=ML, w=CW, size=11.5):
    box = slide.shapes.add_textbox(x, Inches(y), w, Inches(3.9))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0
    first = True
    for subhead, items in blocks:
        if subhead:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            p.space_before = Pt(0 if first else 8)
            p.space_after = Pt(2)
            first = False
            r = p.add_run(); r.text = subhead
            style_run(r, size + 0.5, ACCENT, bold=True)
        for it in items:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.space_after = Pt(2); p.line_spacing = 1.3
            r = p.add_run(); r.text = "■ " + it
            style_run(r, size, BODY)
    return box


def callout(slide, label, text, y=6.42):
    band_h = Inches(0.52)
    rect(slide, ML, Inches(y), CW, band_h, PALE)
    rect(slide, ML, Inches(y), Pt(3.2), band_h, ACCENT)
    box = slide.shapes.add_textbox(ML + Inches(0.2), Inches(y), CW - Inches(0.4), band_h)
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = 0; tf.margin_right = 0
    p = tf.paragraphs[0]
    r1 = p.add_run(); r1.text = label + "　"
    style_run(r1, 11, ACCENT, bold=True)
    r2 = p.add_run(); r2.text = text
    style_run(r2, 11, INK, bold=True)


def note(slide, text, y=5.9):
    add_text(slide, ML, Inches(y), CW, Inches(0.4),
             [("※ " + text, 9, MUTED, False)])


def placeholder(slide, text, y, w=CW, h=Inches(0.5)):
    rect(slide, ML, Inches(y), w, h, PALE, ACCENT, Pt(1), dash=True,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.18)
    box = slide.shapes.add_textbox(ML + Inches(0.2), Inches(y), w - Inches(0.4), h)
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = 0; tf.margin_right = 0
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = text
    style_run(r, 10, ACCENT, bold=True)


def cards(slide, items, y, h=1.55, n_cols=None, title_size=13, body_size=10,
          gap_in=0.22):
    n = n_cols or len(items)
    gap = Inches(gap_in)
    w = Emu(int((CW - gap * (n - 1)) / n))
    for i, (t, b, variant) in enumerate(items):
        col = i % n
        row = i // n
        x = ML + Emu(int((w + gap) * col))
        yy = Inches(y) + Emu(int((Inches(h) + gap) * row))
        if variant == "dark":
            fill, border, tc, bc = DK, None, WHITE, RGBColor(0xC6, 0xD4, 0xEA)
        elif variant == "gray":
            fill, border, tc, bc = GRAYF, LINEC, INK, BODY
        else:
            fill, border, tc, bc = PALE, ACCENT, DK, BODY
        shp = rect(slide, x, yy, w, Inches(h), fill, border,
                   Pt(1.1) if border else None,
                   shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.10)
        tf = shp.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.15); tf.margin_right = Inches(0.15)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.space_after = Pt(3)
        r = p.add_run(); r.text = t
        style_run(r, title_size, tc, bold=True)
        if b:
            p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER; p2.line_spacing = 1.2
            r2 = p2.add_run(); r2.text = b
            style_run(r2, body_size, bc)


def table_block(slide, headers, rows, y, col_w, size=10.5, row_h=0.42,
                header_size=None):
    n_rows, n_cols = len(rows) + 1, len(headers)
    total_w = Emu(sum(int(c) for c in col_w))
    gfx = slide.shapes.add_table(n_rows, n_cols, ML, Inches(y), total_w,
                                 Inches(row_h * n_rows))
    tbl = gfx.table
    tbl.first_row = False; tbl.horz_banding = False
    for i, w in enumerate(col_w):
        tbl.columns[i].width = Emu(int(w))
    for c, htxt in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.fill.solid(); cell.fill.fore_color.rgb = DK
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        r = p.add_run(); r.text = htxt
        style_run(r, header_size or size, WHITE, bold=True)
    for ri, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = tbl.cell(ri, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if ri % 2 else GRAYF
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.line_spacing = 1.1
            r = p.add_run(); r.text = val
            style_run(r, size, DK if c == 0 else BODY, bold=(c == 0))


def statement(slide, lines, y=2.5, size=19):
    box = slide.shapes.add_textbox(ML + Inches(0.3), Inches(y), Inches(11.4), Inches(3.6))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0
    for i, (text, st) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(24); p.line_spacing = 1.3
        color, bold = {"gray": (BODY, False), "ink": (DK, True),
                       "accent": (ACCENT, True)}[st]
        r = p.add_run(); r.text = text
        style_run(r, size, color, bold)


def numbered_rows(slide, items, y=2.1, row_h=0.5, gap=0.11, size=11.5):
    for i, (num, text, sub) in enumerate(items):
        yy = Inches(y) + Emu(int((Inches(row_h) + Inches(gap)) * i))
        rect(slide, ML, yy, CW, Inches(row_h), GRAYF, LINEC, Pt(0.8),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.22)
        d = min(0.32, row_h - 0.08)
        circ = rect(slide, ML + Inches(0.13), yy + Inches((row_h - d) / 2),
                    Inches(d), Inches(d), DK, shape=MSO_SHAPE.OVAL)
        tfc = circ.text_frame
        tfc.margin_left = 0; tfc.margin_right = 0
        tfc.vertical_anchor = MSO_ANCHOR.MIDDLE
        pc = tfc.paragraphs[0]; pc.alignment = PP_ALIGN.CENTER
        rc = pc.add_run(); rc.text = num
        style_run(rc, 10, WHITE, bold=True)
        box = slide.shapes.add_textbox(ML + Inches(0.58), yy, CW - Inches(0.75), Inches(row_h))
        tf = box.text_frame; tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = 0; tf.margin_right = 0
        p = tf.paragraphs[0]
        r = p.add_run(); r.text = text
        style_run(r, size, INK, bold=True)
        if sub:
            r2 = p.add_run(); r2.text = "　" + sub
            style_run(r2, size - 1.5, BODY)


def category_slide(no, idx, cat, plan_name, headline, yobikake,
                   left_blocks, right_blocks, notes):
    s = new_slide("カテゴリー別企画募集",
                  f"SLIDE {no:02d}|カテゴリー別企画募集|企画 {idx} / 10", notes)
    title(s, f"{cat}|{plan_name}――{headline}", size=20)
    rule(s)
    lead(s, yobikake)
    sections(s, left_blocks, y=2.3, x=ML, w=Inches(5.9))
    sections(s, right_blocks, y=2.3, x=Inches(6.85), w=Inches(5.9))
    callout(s, "ご相談の入口",
            "このカテゴリーの企業様は、本日ぜひ個別相談にお申し込みください")
    return s


# =====================================================================
# 1. タイトル
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = WHITE
rect(s, 0, 0, Inches(0.28), SLIDE_H, ACCENT)
rect(s, Inches(0.9), Inches(1.12), Inches(2.2), Pt(3.2), ACCENT)
add_text(s, Inches(0.9), Inches(1.38), Inches(11.5), Inches(0.35),
         [("ライセンシー・パートナー企業の皆さまへ", 13, BODY, True)])
add_text(s, Inches(0.9), Inches(1.95), Inches(11.9), Inches(1.7),
         [("ULTRAMAN LICENSEE", 40, INK, True, {"line": 1.08, "after": 0}),
          ("PRESENTATION 2026", 40, INK, True, {"line": 1.08})])
add_text(s, Inches(0.9), Inches(3.62), Inches(11.9), Inches(0.55),
         [("2027年度以降の商機を、いま一緒につくる。", 20, ACCENT, True)])
add_text(s, Inches(0.9), Inches(4.2), Inches(11.9), Inches(0.4),
         [("― 商品化・売場・販促・広告タイアップ・IPコラボに参加する企業を、今日から募集します ―",
           13, DK, True)])
add_text(s, Inches(0.9), Inches(5.0), Inches(11.9), Inches(0.35),
         [("円谷プロダクション", 12, INK, True)])
add_text(s, Inches(0.9), Inches(5.32), Inches(11.9), Inches(0.3),
         [("2026年7月23日|ウルサマ イベントステージ", 10.5, MUTED, False)])
add_text(s, Inches(0.9), Inches(5.62), Inches(11.6), Inches(0.7),
         [("本資料は当日投影用ドラフトです。2027年度以降の展開に関する記述は、開示可能範囲の確定(7/14構成確認会)後に最終化します。未確定情報・NDA対象情報は含みません。",
           8.5, MUTED, False, {"line": 1.4})])
s.notes_slide.notes_text_frame.text = (
    "(タイトル表示のみ)本日の位置づけ:聞かせる会ではなく、手を挙げさせる会。"
    "参加者に持ち帰らせる感情は「盛り上がってるね」ではなく"
    "「うちのカテゴリーでも企画できる」「今動けば2027年の売場・キャンペーンに間に合う」「早く個別相談したい」。")

# 2. 本日の目的
s = new_slide("オープニング", "SLIDE 02|オープニング",
              "本日は、単なる作品紹介ではありません。2027年度以降のウルトラマン展開を、皆さまの商品・"
              "売場・キャンペーンにどう接続できるかをご説明する場です。")
title(s, "本日は「発表会」ではない――2027年度以降の商機に参加する企業を、今日から募集する")
rule(s)
lead(s, "聞いていただく会ではなく、手を挙げていただく会")
sections(s, [
    ("本日の位置づけ", [
        "2027年度以降のウルトラマン展開に向けて、商品化・売場・販促・広告タイアップ・IPコラボに参加する企業を募集する場",
        "各カテゴリーの具体企画案と、参加方法・相談導線までご案内する",
    ]),
    ("持ち帰っていただきたいこと", [
        "「うちのカテゴリーでも企画できる」という具体的なイメージ",
        "「今動けば、2027年の売場・キャンペーンに間に合う」というタイミング感",
    ]),
])
callout(s, "本日の背骨",
        "ウルトラマンは年間を通じて生活者との接点を作り続ける――その接点を、皆さまの商品・売場・キャンペーンに変えていく")

# 3. 今日お伝えしたいこと
s = new_slide("オープニング", "SLIDE 03|オープニング",
              "本日お伝えしたいことは5つです。この順番でご説明します。")
title(s, "今日お伝えしたいこと――5つ")
rule(s)
numbered_rows(s, [
    ("1", "60周年の熱量は、2027年度以降の商機につながっている", ""),
    ("2", "ウルトラマンは、年間を通じて生活者接点を作るIPになる", ""),
    ("3", "各カテゴリーで、具体的な商品化・販促機会がある", "本日、企画案を10本ご提案します"),
    ("4", "スタイルガイドと監修体制を整え、企画化を進めやすくする", ""),
    ("5", "本日から、個別商談・企画相談を開始する", ""),
], y=1.95, row_h=0.62, gap=0.16, size=12.5)
callout(s, "キーメッセージ", "本日は、そのための商機と参加方法をご説明します")

# 4. 60周年は、もう始まっている
s = new_slide("60周年の現在地", "SLIDE 04|60周年の現在地",
              "60周年はすでに動き出しています。イベント、商品化、コラボ、流通。"
              "(直前の動画と連動して、一枚で「動いている感」を見せる)")
title(s, "60周年は、もう始まっている――イベント・商品・広告・流通・コラボが動いている")
rule(s)
lead(s, "異なるファン層・異なる売場に向けた展開が、同時並行で進行中")
cards(s, [
    ("国内外イベント", "ウルサマ/ライブ/展覧会/ヒーローショー/グリーティング", "pale"),
    ("商品化", "食品・アパレル・雑貨・玩具・文具・コレクション", "pale"),
    ("IPコラボ", "モフサンド、ベイブレード ほか", "gray"),
    ("流通", "ウルトラマート、POPUP、量販・専門店", "dark"),
], y=2.35, h=1.5, n_cols=2)
note(s, "【素材8待ち】実績写真グリッド(8〜12点)に差し替え予定。数字より「動いている感」を重視", y=5.75)
callout(s, "キーメッセージ", "この熱量は、一過性の盛り上がりでは終わらない")

# 5. でも、商機はここからが本番
s = new_slide("60周年の現在地", "SLIDE 05|60周年の現在地",
              "60周年は一過性の盛り上がりではありません。2027年度以降の映像・映画・配信・イベント・"
              "流通施策に接続していきます。")
title(s, "でも、商機はここからが本番")
rule(s)
statement(s, [
    ("60周年は、一過性の盛り上がりではありません。", "gray"),
    ("2027年度以降の映像・映画・配信・イベント・流通施策に、接続していきます。", "ink"),
    ("――2027年のウルトラマン売場は、今日ここから始まります。", "accent"),
])

# 6. 2027年度以降の全体像
s = new_slide("2027年度以降の全体像", "SLIDE 06|2027年度以降の全体像",
              "2027年度以降、ウルトラマンは単発の作品展開ではなく、年間を通じて接点を作る設計に"
              "変わります。点ではなく、面で展開します。")
title(s, "2027年度以降の全体像――点ではなく、面で展開する")
rule(s)
lead(s, "9つの展開が連動して動く「年間型IP」へ")
cards(s, [
    ("テレビシリーズ", "継続接点", "pale"),
    ("映画", "大型話題化", "pale"),
    ("配信・YouTube", "コアファン接点", "pale"),
    ("ウルサマ・ライブイベント", "熱量づくり", "pale"),
    ("IPコラボ", "新ファン層開拓", "pale"),
    ("ウルトラマート", "売場づくり", "pale"),
    ("流通展開", "販路拡大", "pale"),
    ("商品化", "購買接点", "dark"),
    ("広告キャンペーン", "企業活用", "pale"),
], y=2.3, h=1.05, n_cols=3, title_size=12, body_size=9.5, gap_in=0.18)
callout(s, "キーメッセージ", "それぞれの接点を、皆さまの商品・売場・キャンペーンに変えていく")

# 7. 映像展開が、商品化の理由を作る
s = new_slide("2027年度以降の全体像", "SLIDE 07|2027年度以降の全体像",
              "テレビで継続接点を作り、映画で大型の話題化を作り、配信でコアファン接点を広げ、"
              "イベントで熱量を高め、流通・商品化で購買につなげます。"
              "TVの安全表現:「キャラクターや世界観の継続性をより重視し、ファンが次の展開を追い続けたく"
              "なる構造を強化」。【NG】3年連続・同一世界線・テレビ局変更には触れない。")
title(s, "映像展開が、商品化の理由を作る――テレビは継続、映画は話題化、配信は横断")
rule(s)
lead(s, "作品の羅列ではなく、「商品をいつ・なぜ出すか」の設計としてお伝えする")
cards(s, [
    ("商機① テレビシリーズ", "継続接点:世界観の継続性を重視し、商品もシリーズ展開・第2弾・第3弾を設計しやすくなる", "pale"),
    ("商機② 映画・ゼロ関連", "大型話題化:商品化・販促・流通施策を集中させる最大の山。生活者が「買う理由」を作れるタイミング", "pale"),
    ("商機③ 配信・ギャラファイ", "キャラ横断:歴代ヒーロー・怪獣を横断活用でき、コレクション性の高い商品・ファン向けMDと相性が良い", "pale"),
], y=2.35, h=2.0, title_size=12.5, body_size=10)
placeholder(s, "【素材1・2・4・6待ち/開示確認】2027年以降のコンテンツ全体像・各柱の開示可能情報", 4.7)
callout(s, "キーメッセージ", "単発の商品化で終わらせない――年間の接点設計が、商品の売れるタイミングを作る")

# 8. イベントが、熱量を作る
s = new_slide("2027年度以降の全体像", "SLIDE 08|2027年度以降の全体像",
              "広い認知はテレビ、映画、配信、SNS、PRで作ります。一方で、ウルトラマンには、イベント、"
              "ショー、グリーティングを通じて、実際に会いに来るファンとの濃い接点があります。"
              "このリアルな熱量を、商品・売場・キャンペーンに接続できることが、ウルトラマンの強みです。"
              "※「100万人に届きます」という単独リーチ表現は使わない。")
title(s, "イベントが、熱量を作る――広い認知と深いリアル接点の両方を持つIP")
rule(s)
lead(s, "「広さ」は映像・SNSで、「濃さ」はイベントで、「購買」は売場・商品化で語る")
table_block(s,
            ["指標", "役割", "例"],
            [["テレビ・映画・配信・SNS", "広く知ってもらう", "認知・話題化・PR"],
             ["イベント・ショー・グリーティング", "熱量を高める", "年間約70万〜100万人規模のリアル接点"],
             ["物販・POPUP・流通", "買う場所を作る", "店頭・ウルトラマート・EC"],
             ["商品化・キャンペーン", "企業の売上につなげる", "皆さまの商品・売場・販促"]],
            2.25, [Inches(3.6), Inches(2.7), Inches(5.9)])
note(s, "単なる広告リーチではなく、実際に足を運び、体験し、購買に近い場所にいるファンとの接点(補強データ確定後に表現最終化)", y=4.6)
callout(s, "キーメッセージ", "“会いに来るファン”の熱量を、皆さまの商品・売場・キャンペーンに接続できる")

# 9. 流通が、売る場所を作る
s = new_slide("2027年度以降の全体像", "SLIDE 09|2027年度以降の全体像",
              "商品を作って終わりではなく、売場・POPUP・EC・イベント物販に接続していきます。"
              "ライセンシーの最大の不安「作った商品はどこで売れるのか?」に応えるパートです。")
title(s, "流通が、売る場所を作る――「作っても売る場所があるのか」に応える")
rule(s)
lead(s, "商品化だけでなく、売場化・販促化まで一緒に設計できることが、今後のライセンス戦略のポイント")
sections(s, [
    ("円谷側でも「売る場所・見せる場所・出会う場所」を増やしていく", [
        "ウルトラマートのコンセプト/売場・商品展開イメージ",
        "POPUP展開/限定商品枠/先行販売枠",
        "映画連動棚/ウルサマ連動棚/IPコラボ棚/EC連動",
    ]),
])
placeholder(s, "【素材10待ち】ウルトラマート素材・売場写真・商品展開イメージ", 4.35)
callout(s, "キーメッセージ", "商品を作っていただくだけでなく、どこで・どう見せ・どう売るかまで一緒に設計していく")

# 10. 商機カレンダー
s = new_slide("商機カレンダー", "SLIDE 10|商機カレンダー",
              "ライセンシーの皆さまが一番知りたいのは「いつ何を仕込めばいいか」。作品スケジュールでは"
              "なく、商品化タイミングとしてお見せします。商品開発リードタイムから逆算すると、2027年の"
              "山場に間に合わせるには今から企画に入るのがベストタイミングです。")
title(s, "2026-2027 ULTRAMAN BUSINESS CALENDAR――いつ仕込めば、間に合うか")
rule(s)
lead(s, "作品スケジュールではなく、「商品化タイミング」としてお見せする")
table_block(s,
            ["時期", "円谷側の動き", "ライセンシーの商機", "作るべき商品・企画"],
            [["2026年夏", "ウルサマ、60周年施策", "熱量の可視化", "イベント連動商品、先行企画相談"],
             ["2026年秋", "IPコラボ、流通施策", "年末商戦・話題化", "雑貨、アパレル、ギフト商材"],
             ["2026年冬", "2027展開の仕込み", "来期商品企画", "スタイルガイド確認、企画提出"],
             ["2027年春", "新展開ティザー", "新生活・入学・春販促", "文具、アパレル、生活雑貨"],
             ["2027年夏", "映画・イベント・大型露出", "最大商戦期", "食品、外食、流通、キャンペーン"],
             ["2027年秋", "配信・YouTube・コアファン施策", "継続購買", "コレクション、EC限定、プレミアム商品"],
             ["2027年冬", "年末商戦", "ギフト・限定品", "高単価商品、福袋、限定コラボ"]],
            2.2, [Inches(1.5), Inches(3.3), Inches(2.5), Inches(4.9)],
            size=10, row_h=0.44)
callout(s, "キーメッセージ", "2027年夏の最大商戦に間に合わせるなら、企画開始は「いま」")

# 11. 募集カテゴリー一覧
s = new_slide("カテゴリー別企画募集", "SLIDE 11|カテゴリー別企画募集",
              "ここからが本日の中心です。2027年度以降の展開に向けて、10のカテゴリーで商品化・販促企画を"
              "募集します。それぞれ具体的な企画案をご用意しました。「うちならこう作れる」という目線で"
              "ご覧ください。")
title(s, "ライセンシーの皆さまにお願いしたいこと――10カテゴリーで企画を募集します")
rule(s)
numbered_rows(s, [
    ("1", "食品・飲料", "ULTRA ENERGY PACK"),
    ("2", "外食・カフェ", "親子ヒーローメニュー"),
    ("3", "アパレル", "ULTRA STREET / ULTRA FAMILY"),
    ("4", "生活雑貨", "毎日のウルトラマン"),
    ("5", "文具・教育", "ウルトラヒーローズ新学期"),
    ("6", "玩具・ホビー", "ULTRA CROSS COLLECTION"),
    ("7", "流通・小売", "ULTRA MARKET IN STORE"),
    ("8", "広告代理店・SP", "ULTRAMAN BRAND CAMPAIGN PACKAGE"),
    ("9", "プレミアム商品", "ULTRA PREMIUM LINE"),
    ("10", "女性・ライト層", "ULTRA KAWAII / CHARACTER MIX"),
], y=1.82, row_h=0.38, gap=0.075, size=10.5)
callout(s, "キーメッセージ", "過去実績のご紹介ではなく、これからご一緒したい企画のご提案です")

# 12-21. カテゴリー別企画(10本)
category_slide(12, 1, "企画① 食品・飲料", "ULTRA ENERGY PACK",
               "映画・イベント期の親子キャンペーンを募集",
               "食品・飲料の皆さまとは、映画・イベント期に合わせた親子向けキャンペーンを作りたい",
               [("ターゲット", ["親子、キッズ、夏休み需要"]),
                ("商品例", ["菓子/飲料/ゼリー/アイス/レトルト食品/シリアル/弁当商材"])],
               [("企画内容", ["「光」「エネルギー」「変身」をテーマにした限定パッケージ展開",
                          "購入特典:ステッカー、カード、映画・イベント連動キャンペーン"]),
                ("連動先", ["映画/ウルサマ/店頭キャンペーン/親子向け販促/夏休み企画"])],
               "食品・飲料カテゴリーの皆さまとは、映画・イベント期に合わせた親子向けキャンペーンを作りたいと考えています。")
category_slide(13, 2, "企画② 外食・カフェ", "親子ヒーローメニュー",
               "熱量を店舗送客につなげる企画を募集",
               "外食・カフェ業態の皆さまとは、ウルトラマンの熱量を店舗送客につなげる企画を作りたい",
               [("ターゲット", ["ファミリー、映画来場者、イベント来場者"]),
                ("商品例", ["キッズメニュー/コラボドリンク/デザート/テイクアウト商品/ノベルティ付きセット"])],
               [("企画内容", ["映画・ウルサマのタイミングに合わせた親子コラボメニュー",
                          "来店特典:限定コースター、ステッカー、ランチョンマット、撮影用カード"]),
                ("連動先", ["映画公開/イベント会場周辺/商業施設/SNS投稿キャンペーン"])],
               "外食・カフェ業態の皆さまとは、ウルトラマンの熱量を店舗送客につなげる企画を作りたいです。")
category_slide(14, 3, "企画③ アパレル", "ULTRA STREET / ULTRA FAMILY",
               "大人・女性・親子リンクまで広げる",
               "子ども向けだけでなく、大人・女性・親子リンクまで広げていきたい",
               [("ターゲット", ["大人ファン、若年層、親子"]),
                ("商品例", ["Tシャツ/スウェット/キャップ/トートバッグ/親子リンクウェア/靴下/ルームウェア"])],
               [("デザイン方向性", ["キッズ向け:ヒーロービジュアル中心",
                             "大人向け:ロゴ、シンボル、怪獣、タイポグラフィ",
                             "女性向け:柔らかい色、キャラクターコラボ、雑貨寄り",
                             "プレミアム:ブラック、シルバー、刺繍、限定感"])],
               "アパレルカテゴリーでは、子ども向けだけでなく、大人・女性・親子リンクまで広げていきたいと考えています。")
category_slide(15, 4, "企画④ 生活雑貨", "毎日のウルトラマン",
               "ファンが毎日使える商品を増やす",
               "生活雑貨カテゴリーでは、ファンが毎日使える商品を増やしていきたい",
               [("ターゲット", ["ファミリー、大人ファン、ギフト需要"]),
                ("商品例", ["タオル/マグカップ/タンブラー/ランチボックス/ポーチ/ルーム雑貨/インテリア小物/スマホアクセサリー"])],
               [("企画内容", ["ウルトラマンを日常生活の中に置く",
                          "「変身」「光」「防衛隊」「怪獣」を生活雑貨に落とし込む"]),
                ("連動先", ["ギフト商戦/ウルトラマート/POPUP/EC"])],
               "生活雑貨カテゴリーでは、ファンが毎日使える商品を増やしていきたいです。")
category_slide(16, 5, "企画⑤ 文具・教育", "ウルトラヒーローズ新学期",
               "物語性を子どもの成長文脈に接続する",
               "ウルトラマンの物語性を、子どもの成長文脈に接続した商品を作りたい",
               [("ターゲット", ["小学生、親、入学・新学期需要"]),
                ("商品例", ["ノート/鉛筆/ペンケース/下敷き/シール/学習帳/図鑑/ワークブック/絵本"])],
               [("企画内容", ["「勇気」「仲間」「成長」「正義」をテーマに文具・教育商材へ展開",
                          "春の新生活、夏休み、自由研究と相性が良い"]),
                ("連動先", ["新学期商戦/夏休み/読書キャンペーン"])],
               "文具・教育カテゴリーでは、ウルトラマンの物語性を子どもの成長文脈に接続した商品を作りたいです。")
category_slide(17, 6, "企画⑥ 玩具・ホビー", "ULTRA CROSS COLLECTION",
               "キャラクター資産を横断するコレクション展開",
               "単独作品ではなく、ウルトラマン全体のキャラクター資産を活かしたコレクション展開を強化したい",
               [("ターゲット", ["キッズ、コアファン、コレクター"]),
                ("商品例", ["フィギュア/カード/アクリルスタンド/カプセルトイ/食玩/ブラインド商品/ジオラマ商材"])],
               [("企画内容", ["ギャラファイ、ゼロ、歴代ヒーロー、怪獣を横断したコレクション企画",
                          "ランダム性、シークレット、シリーズ継続で購買を作る"]),
                ("連動先", ["配信・YouTube展開/EC限定/イベント物販"])],
               "ホビー領域では、ウルトラマン全体のキャラクター資産を活かしたコレクション展開を強化していきたいです。")
category_slide(18, 7, "企画⑦ 流通・小売", "ULTRA MARKET IN STORE",
               "商品を「売場」として見せる",
               "ウルトラマン商品を“売る場所”そのものから一緒に作っていきたい",
               [("ターゲット", ["量販店、専門店、商業施設、EC"]),
                ("売場例", ["映画公開記念棚/ウルサマ連動棚/親子向け夏休み棚/怪獣特集棚/ゼロ特集棚/大人ファン向けプレミアム棚"])],
               [("企画内容", ["商品を単品で置くのではなく、売場として見せる",
                          "映画、イベント、60周年、IPコラボに合わせた期間限定棚・POPUP・店頭キャンペーン"]),
                ("連動先", ["ウルトラマート/映画・イベント期の店頭施策"])],
               "流通・小売の皆さまとは、ウルトラマン商品を“売る場所”そのものから一緒に作っていきたいです。"
               "(サンリオコラボ棚は開示可能なら言及)")
category_slide(19, 8, "企画⑧ 広告代理店・SP会社", "ULTRAMAN BRAND CAMPAIGN PACKAGE",
               "クライアント課題に合わせた活用メニュー",
               "クライアント課題に合わせた、ウルトラマン活用メニューを作っていきたい",
               [("ターゲット", ["企業広告、販促、地域施策、ファミリー向けキャンペーン"]),
                ("活用テーマ", ["親子集客/夏休み販促/防災/交通安全/環境/地域創生/スポーツ/未来・テクノロジー/勇気・挑戦"])],
               [("企画内容", ["ウルトラマンを企業キャンペーンの装置として活用",
                          "単なるキャラクター使用ではなく、企業の課題に合わせて文脈を作る"]),
                ("連動先", ["映画・イベント期のタイアップ/交通広告/SNSキャンペーン"])],
               "広告代理店・SP会社の皆さまとは、クライアント課題に合わせたウルトラマン活用メニューを作っていきたいです。")
category_slide(20, 9, "企画⑨ プレミアム商品", "ULTRA PREMIUM LINE",
               "大人が所有したくなる高付加価値商品",
               "キャラクターをそのまま載せるのではなく、世界観やシンボルを活かした高付加価値商品を広げたい",
               [("ターゲット", ["大人ファン、ギフト、高単価商材"]),
                ("商品例", ["時計/革小物/アート/フィギュア/インテリア/ジュエリー/ゴルフ用品/高級アパレル"])],
               [("企画内容", ["ゼロ、セブン、怪獣、ロゴ、メカ、世界観を使い、大人が所有したくなる商品を作る"]),
                ("連動先", ["ゼロ映画/周年施策/ギフト商戦/EC限定"])],
               "大人ファン向けには、世界観やシンボルを活かした高付加価値商品を広げたいです。")
category_slide(21, 10, "企画⑩ 女性・ライト層", "ULTRA KAWAII / CHARACTER MIX",
               "従来のヒーロー商品とは違う入口を作る",
               "これまでウルトラマンに触れてこなかった層にも、雑貨・キャラクター文脈で接点を広げたい",
               [("ターゲット", ["女性、ライトファン、キャラクター雑貨層"]),
                ("商品例", ["ポーチ/キーホルダー/ぬいぐるみ/コスメ雑貨/ステーショナリー/バッグ/ルーム雑貨"])],
               [("企画内容", ["IPコラボやデフォルメ表現を活用し、従来のヒーロー商品とは違う入口を作る",
                          "サンリオ等のコラボが出せる場合は、ここで強く見せる【開示確認】"]),
                ("連動先", ["IPコラボ/キャラクター雑貨売場/ギフト"])],
               "これまでウルトラマンに触れてこなかった層にも、雑貨・キャラクター文脈で接点を広げたいです。")

# 22. IPコラボ
s = new_slide("IPコラボ・流通", "SLIDE 22|IPコラボ・流通",
              "ウルトラマンは、IPコラボによって新しいファン層・新しい売場・新しい商品カテゴリーに"
              "広がっています。今後は、コラボIPを起点に、ライセンシーの皆さまと共同で商品化・売場化"
              "していきたいと考えています。※「やりました」の実績紹介ではなく、役割と商品化機会で見せる。")
title(s, "IPコラボで、新しいファン層へ――コラボを起点に、共同で商品化・売場化する")
rule(s)
lead(s, "コラボごとに「役割・狙う層・商品化機会」が異なる――ここに皆さまの企画の入口がある")
table_block(s,
            ["コラボ", "役割", "狙う層", "商品化機会"],
            [["モフサンド", "かわいい文脈", "女性・ライト層", "雑貨、アパレル、小物"],
             ["ベイブレード", "キッズ・ホビー文脈", "男児・玩具層", "玩具、ホビー、イベント"],
             ["サンリオ【開示確認】", "キャラクター雑貨文脈", "女性、ファミリー、ギフト", "雑貨、文具、アパレル、流通棚"],
             ["ゼロ関連", "ヒーロー・大人ファン文脈", "コアファン、親世代", "プレミアム、アパレル、ホビー"],
             ["ギャラファイ系", "キャラ横断文脈", "コレクター", "ランダム、EC、限定商品"]],
            2.25, [Inches(2.5), Inches(2.7), Inches(2.9), Inches(4.1)],
            size=10, row_h=0.44)
callout(s, "キーメッセージ", "コラボIPを起点に、新しいファン層・新しい売場をライセンシーの皆さまと共同で開拓していく")

# 23. ウルトラマートと流通展開
s = new_slide("IPコラボ・流通", "SLIDE 23|IPコラボ・流通",
              "円谷側でも、ウルトラマン商品を売る場所、見せる場所、出会う場所を増やしていきます。"
              "商品化だけでなく、売場化・販促化まで一緒に設計できることが、今後のライセンス戦略の"
              "大きなポイントです。")
title(s, "ウルトラマートと流通展開――作った商品の「売場の出口」を用意する")
rule(s)
lead(s, "円谷側でも「売る場所・見せる場所・出会う場所」を増やしていく")
sections(s, [
    ("見せるもの", [
        "ウルトラマートのコンセプト/売場写真/商品展開イメージ",
        "POPUP展開/限定商品枠/先行販売枠",
        "映画連動棚/ウルサマ連動棚/IPコラボ棚/EC連動",
    ]),
])
placeholder(s, "【素材10待ち】ウルトラマート売場写真・展開イメージに差し替え", 4.35)
callout(s, "キーメッセージ", "商品を作っていただくだけでなく、どこで・どう見せ・どう売るかまで一緒に設計していく")

# 24. スタイルガイド戦略
s = new_slide("スタイルガイド・監修", "SLIDE 24|スタイルガイド・監修",
              "2027年度以降の展開に向けて、ライセンシーの皆さまが企画しやすいよう、カテゴリー別・"
              "ターゲット別に使える素材とデザインガイドを整備していきます。"
              "完成感を無理に出すのではなく「使える形にする方針」を打ち出す。")
title(s, "商品化を加速するスタイルガイド戦略――カテゴリー別・ターゲット別に「使える形」で")
rule(s)
lead(s, "“素材をお渡しします”ではなく、“商品化しやすい形にしてお渡しします”")
table_block(s,
            ["ガイド", "使う企業"],
            [["キッズ向けガイド", "食品、玩具、文具、子ども服"],
             ["大人ファン向けガイド", "アパレル、雑貨、プレミアム商品"],
             ["女性・ライト層向けガイド", "雑貨、文具、キャラクターコラボ"],
             ["怪獣・ヴィランガイド", "アパレル、ホビー、雑貨"],
             ["映画連動ガイド", "食品、外食、流通、広告"],
             ["流通販促ガイド", "小売、量販店、商業施設"],
             ["広告キャンペーンガイド", "代理店、SP、企業タイアップ"]],
            2.25, [Inches(3.6), Inches(8.6)], size=10, row_h=0.42)
callout(s, "キーメッセージ", "これが今後のライセンス営業の大きな方針です")

# 25. 監修・商品化フロー
s = new_slide("スタイルガイド・監修", "SLIDE 25|スタイルガイド・監修",
              "企画提出から商品化までの流れを標準化しています。個別商談では、NDAのうえでさらに詳細な"
              "素材をご覧いただけます。")
title(s, "監修・商品化フロー――企画提出から商品化まで、迷わない")
rule(s)
lead(s, "「作りたい」と思った後、すぐ動ける体制を用意する")
cards(s, [
    ("① 企画提出", "カテゴリー別ガイド・テンプレートを利用", "pale"),
    ("② 初稿確認", "標準リードタイムを明記", "pale"),
    ("③ 修正", "差し戻し理由を明確に共有", "pale"),
    ("④ 承認・商品化", "売場・販促の設計まで並走", "dark"),
], y=2.3, h=1.35, n_cols=4, title_size=12, body_size=9.5)
sections(s, [
    ("開示区分", ["当日開示/NDA後開示/個別商談時開示――商談の段階に応じて詳細素材をご覧いただけます"]),
], y=4.0)
placeholder(s, "【素材11・12待ち】スタイルガイド抜粋・監修フロー資料", 4.75)
callout(s, "キーメッセージ", "企画のご相談から商品化まで、止まらない導線を用意しています")

# 26. 本日から受付開始
s = new_slide("クロージング", "SLIDE 26|クロージング",
              "本日ご紹介した各カテゴリー企画について、個別相談の受付を開始します。会場内のQRより、"
              "関心カテゴリーとご希望の相談テーマをご登録ください。2027年度以降の展開に向けて、早期に"
              "ご相談いただいた企業様から、優先的に企画検討を進めてまいります。"
              "【運営】QRは後方からも読めるサイズで最低30秒表示。次スライドでも画面隅に残す。")
title(s, "本日から受付開始――個別商談・企画相談・NDA説明会・スタイルガイド")
rule(s)
lead(s, "会場内のQRから、関心カテゴリーとご希望の相談テーマをご登録ください")
qr = rect(s, ML, Inches(2.3), Inches(2.7), Inches(2.7), PALE, ACCENT, Pt(1.2),
          dash=True, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
tfq = qr.text_frame; tfq.word_wrap = True
tfq.vertical_anchor = MSO_ANCHOR.MIDDLE
for qi, qline in enumerate(["【QRコード】", "個別商談・企画相談", "受付フォーム"]):
    pq = tfq.paragraphs[0] if qi == 0 else tfq.add_paragraph()
    pq.alignment = PP_ALIGN.CENTER
    rq = pq.add_run(); rq.text = qline
    style_run(rq, 13 if qi != 2 else 11, DK, bold=True)
sections(s, [
    ("フォームでご登録いただくこと", [
        "検討したい領域(商品化/広告タイアップ/流通展開/イベント協賛/IPコラボ/海外展開)",
        "検討カテゴリー(食品/飲料/外食/アパレル/雑貨/文具/玩具/ホビー/流通/広告 ほか)",
        "関心のある展開(2027テレビ/映画/ゼロ関連/ギャラファイ/IPコラボ/ウルトラマート/イベント連動)",
        "個別商談希望/NDA説明会希望/スタイルガイド資料希望/企画提出予定時期",
    ]),
], y=2.35, x=Inches(3.6), w=Inches(9.2), size=10.5)
callout(s, "優先案内", "早期にご相談いただいた企業様から、優先的に企画検討を進めてまいります")

# 27. クロージング
s = new_slide("クロージング", "SLIDE 27|クロージング",
              "本日ご紹介した2027年度以降の展開は、円谷プロだけで完結するものではありません。"
              "映像で生まれる話題、イベントで生まれる熱量、流通で生まれる売場、そして皆さまの商品・"
              "キャンペーンがつながることで、ウルトラマンの次の市場が作られていきます。"
              "だからこそ、今日を起点に、ぜひ具体的なご相談を始めさせてください。食品、アパレル、雑貨、"
              "文具、流通、広告、IPコラボ、プレミアム商品。それぞれのカテゴリーで、まだまだ一緒に作れる"
              "余地があります。2027年度以降のウルトラマンの売場は、今日ここから始まります。"
              "皆さまと一緒に、次の商機を作っていきたいと思います。")
title(s, "2027年のウルトラマン売場は、今日ここから始まります。")
rule(s)
statement(s, [
    ("映像で生まれる話題。イベントで生まれる熱量。流通で生まれる売場。", "gray"),
    ("そこに皆さまの商品・キャンペーンがつながることで、次の市場が作られる。", "ink"),
    ("――今日を起点に、具体的なご相談を始めさせてください。", "accent"),
], y=2.6)

OUT = "ULTRAMAN_LICENSEE_PRESENTATION_draft_v4.pptx"
prs.save(OUT)
print(f"saved {OUT} with {len(prs.slides._sldIdLst)} slides")
