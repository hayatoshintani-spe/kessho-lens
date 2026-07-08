#!/usr/bin/env python3
"""7/23 ULTRAMAN LICENSEE PRESENTATION — 28枚デッキ(.pptx)生成スクリプト v2.

社内標準フォーマット(白背景・紫アクセント・ステートメント型タイトル)に準拠。
素材が届いたら該当スライドのプレースホルダーを差し替えるか、この
スクリプトを更新して再生成する。

    python3 generate_pptx.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.lang import MSO_LANGUAGE_ID
from pptx.oxml.ns import qn

# ---- design tokens(参考フォーマット準拠)----
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
INK    = RGBColor(0x2E, 0x2E, 0x38)   # 見出し・本文強調
BODY   = RGBColor(0x4E, 0x4E, 0x5A)   # 本文
MUTED  = RGBColor(0x9B, 0x9B, 0xA8)   # 注記・フッター
PURPLE = RGBColor(0x7B, 0x2F, 0xE0)   # アクセント(アイキャッチ・罫線・強調)
DK     = RGBColor(0x3B, 0x12, 0x73)   # 濃紫(リード・表ヘッダー・濃カード)
LILAC  = RGBColor(0xF1, 0xEC, 0xFA)   # 薄紫(コールアウト・カード)
GRAYF  = RGBColor(0xF5, 0xF5, 0xF7)   # 薄グレー(カード・表の縞)
LINEC  = RGBColor(0xE4, 0xE4, 0xEC)   # 罫線

JP_FONT = "Yu Gothic"
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
ML = Inches(0.55)
CW = Inches(12.23)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]

FOOTER_DOC = "円谷プロダクション|ULTRAMAN LICENSEE PRESENTATION 2027(ドラフト)"


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
    """lines: list of (text, size, color, bold, opts) or list-of-runs paragraphs."""
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


SECTION_PAGES = []  # (page_no, section)


def new_slide(section, eyebrow_txt, notes=""):
    slide = prs.slides.add_slide(BLANK)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    n = len(prs.slides._sldIdLst)
    # eyebrow
    add_text(slide, ML, Inches(0.28), CW, Inches(0.3),
             [(eyebrow_txt, 11, PURPLE, True, {"spc": 60})])
    # footer hairline + text
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
    rect(slide, ML, Inches(y), Inches(1.2), Pt(3.2), PURPLE)


def lead(slide, text, y=1.72):
    add_text(slide, ML, Inches(y), CW, Inches(0.4),
             [(text, 12.5, DK, True)])


def sections(slide, blocks, y=2.25, w=CW, size=11.5):
    """blocks: list of (subhead, [bullet strings])."""
    box = slide.shapes.add_textbox(ML, Inches(y), w, Inches(3.9))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0
    first = True
    for subhead, items in blocks:
        if subhead:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.space_before = Pt(0 if first else 8)
            p.space_after = Pt(2)
            r = p.add_run(); r.text = subhead
            style_run(r, size + 0.5, PURPLE, bold=True)
        for it in items:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.space_after = Pt(2); p.line_spacing = 1.3
            r = p.add_run(); r.text = "■ " + it
            style_run(r, size, BODY)
    return box


def callout(slide, label, text, y=6.42):
    band_h = Inches(0.52)
    rect(slide, ML, Inches(y), CW, band_h, LILAC)
    rect(slide, ML, Inches(y), Pt(3.2), band_h, PURPLE)
    box = slide.shapes.add_textbox(ML + Inches(0.2), Inches(y), CW - Inches(0.4), band_h)
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = 0; tf.margin_right = 0
    p = tf.paragraphs[0]
    r1 = p.add_run(); r1.text = label + "　"
    style_run(r1, 11, PURPLE, bold=True)
    r2 = p.add_run(); r2.text = text
    style_run(r2, 11, INK, bold=True)


def note(slide, text, y=5.9):
    add_text(slide, ML, Inches(y), CW, Inches(0.4),
             [("※ " + text, 9, MUTED, False)])


def placeholder(slide, text, y, w=CW, h=Inches(0.5)):
    rect(slide, ML, Inches(y), w, h, LILAC, PURPLE, Pt(1), dash=True,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.18)
    box = slide.shapes.add_textbox(ML + Inches(0.2), Inches(y), w - Inches(0.4), h)
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = 0; tf.margin_right = 0
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = text
    style_run(r, 10, PURPLE, bold=True)


def cards(slide, items, y, h=1.55, n_cols=None, title_size=13, body_size=10):
    """items: list of (title, body, variant) — variant: 'lilac'|'gray'|'dark'."""
    n = n_cols or len(items)
    gap = Inches(0.22)
    w = Emu(int((CW - gap * (n - 1)) / n))
    for i, (t, b, variant) in enumerate(items):
        col = i % n
        row = i // n
        x = ML + Emu(int((w + gap) * col))
        yy = Inches(y) + Emu(int((Inches(h) + gap) * row))
        if variant == "dark":
            fill, border, tc, bc = DK, None, WHITE, RGBColor(0xD8, 0xCB, 0xF2)
        elif variant == "gray":
            fill, border, tc, bc = GRAYF, LINEC, INK, BODY
        else:
            fill, border, tc, bc = LILAC, PURPLE, DK, BODY
        shp = rect(slide, x, yy, w, Inches(h), fill, border,
                   Pt(1.1) if border else None,
                   shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.10)
        tf = shp.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.18); tf.margin_right = Inches(0.18)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.space_after = Pt(4)
        r = p.add_run(); r.text = t
        style_run(r, title_size, tc, bold=True)
        if b:
            p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER; p2.line_spacing = 1.25
            r2 = p2.add_run(); r2.text = b
            style_run(r2, body_size, bc)


def table_block(slide, headers, rows, y, col_w, size=10.5, row_h=0.42):
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
        style_run(r, size, WHITE, bold=True)
    for ri, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = tbl.cell(ri, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if ri % 2 else GRAYF
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            r = p.add_run(); r.text = val
            style_run(r, size, DK if c == 0 else BODY, bold=(c == 0))


def statement(slide, lines, y=2.5):
    """lines: list of (text, style) — style: 'gray'|'ink'|'purple'."""
    box = slide.shapes.add_textbox(ML + Inches(0.3), Inches(y), Inches(11.4), Inches(3.6))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0
    for i, (text, st) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(26); p.line_spacing = 1.3
        color, bold = {"gray": (BODY, False), "ink": (DK, True),
                       "purple": (PURPLE, True)}[st]
        r = p.add_run(); r.text = text
        style_run(r, 19, color, bold)


def numbered_rows(slide, items, y=2.1, row_h=0.56, gap=0.14, size=12,
                  highlight_last=False):
    """items: list of (num_label, text, sub)."""
    for i, (num, text, sub) in enumerate(items):
        yy = Inches(y) + Emu(int((Inches(row_h) + Inches(gap)) * i))
        last = highlight_last and i == len(items) - 1
        rect(slide, ML, yy, CW, Inches(row_h),
             LILAC if last else GRAYF,
             PURPLE if last else LINEC, Pt(1.2 if last else 0.8),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.22)
        circ = rect(slide, ML + Inches(0.14), yy + Inches((row_h - 0.34) / 2),
                    Inches(0.34), Inches(0.34),
                    PURPLE if last else DK, shape=MSO_SHAPE.OVAL)
        tfc = circ.text_frame
        tfc.margin_left = 0; tfc.margin_right = 0
        tfc.vertical_anchor = MSO_ANCHOR.MIDDLE
        pc = tfc.paragraphs[0]; pc.alignment = PP_ALIGN.CENTER
        rc = pc.add_run(); rc.text = num
        style_run(rc, 11, WHITE, bold=True)
        box = slide.shapes.add_textbox(ML + Inches(0.62), yy, CW - Inches(0.8), Inches(row_h))
        tf = box.text_frame; tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = 0; tf.margin_right = 0
        p = tf.paragraphs[0]
        r = p.add_run(); r.text = text
        style_run(r, size, DK if last else INK, bold=True)
        if sub:
            r2 = p.add_run(); r2.text = "　" + sub
            style_run(r2, size - 2, BODY)


def category_slide(no, name, headline, message, shoki, kikaku, notes):
    s = new_slide("営業戦略", f"SLIDE {no:02d}|営業戦略|カテゴリー {no-13} / 7", notes)
    title(s, f"{name}――{headline}")
    rule(s)
    lead(s, message)
    sections(s, [
        ("商機", [shoki]),
        ("企画例", [kikaku]),
    ], y=2.35)
    callout(s, "ご相談の入口", "「この枠に自社が入れるか」という段階からのご相談で構いません――個別商談で貴社の売場・キャンペーンに合わせて企画をご一緒します")
    return s


# =====================================================================
# 1. タイトル
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = WHITE
rect(s, 0, 0, Inches(0.28), SLIDE_H, PURPLE)
rect(s, Inches(0.9), Inches(1.12), Inches(2.2), Pt(3.2), PURPLE)
add_text(s, Inches(0.9), Inches(1.38), Inches(11.5), Inches(0.35),
         [("ライセンシー・パートナー企業の皆さまへ", 13, BODY, True)])
add_text(s, Inches(0.9), Inches(1.95), Inches(11.9), Inches(1.1),
         [("ULTRAMAN LICENSEE PRESENTATION", 40, INK, True, {"line": 1.1})])
add_text(s, Inches(0.9), Inches(2.85), Inches(11.9), Inches(0.55),
         [("2027年度以降の商機を、いま一緒につくる。", 20, PURPLE, True)])
add_text(s, Inches(0.9), Inches(3.42), Inches(11.9), Inches(0.4),
         [("― 作品・イベント・流通・商品化が連動する「年間型IP」へ ―", 13, DK, True)])
add_text(s, Inches(0.9), Inches(5.0), Inches(11.9), Inches(0.35),
         [("円谷プロダクション", 12, INK, True)])
add_text(s, Inches(0.9), Inches(5.32), Inches(11.9), Inches(0.3),
         [("2026年7月23日|ウルサマ イベントステージ", 10.5, MUTED, False)])
add_text(s, Inches(0.9), Inches(5.62), Inches(11.6), Inches(0.7),
         [("本資料は当日投影用ドラフトです。2027年度以降の展開に関する記述は、開示可能範囲の確定(7/14構成確認会)後に最終化します。未確定情報・NDA対象情報は含みません。",
           8.5, MUTED, False, {"line": 1.4})])
s.notes_slide.notes_text_frame.text = "(タイトル表示のみ。MCオープニングへ)"

# 2. 今日の目的
s = new_slide("オープニング", "SLIDE 02|オープニング",
              "本日は、単なる作品紹介ではありません。2027年度以降、ウルトラマンを皆さまの商品・売場・"
              "キャンペーンにどう活用いただけるか、その商機を共有する場です。最後に個別商談のご案内も"
              "ありますので、ぜひ「自社ならこう使える」という視点でお聞きください。")
title(s, "本日は「作品発表会」ではない――2027年度以降の商機を、持ち帰っていただく場である")
rule(s)
lead(s, "担当者の皆さまが社内に持ち帰り、「これは商品化したい」と言える材料をお渡しする")
sections(s, [
    ("本日の位置づけ", [
        "2027年度以降のウルトラマン展開を、パートナー企業の皆さまに共有する",
        "商品化・販促・広告タイアップ・流通施策の商機を、具体的な企画例とともにご提案する",
    ]),
    ("本日のゴール", [
        "「すごかった」ではなく、「うちも作りたい。相談したい」で終わる",
        "本日の終わりに、個別商談のご予約・企画相談の導線をご案内する",
    ]),
])
callout(s, "お願い", "ぜひ「自社ならこう使える」という視点でお聞きください")

# 3. 接続(ステートメント)
s = new_slide("オープニング", "SLIDE 03|オープニング",
              "いまご覧いただいた熱量は、ステージの中だけで終わるものではありません。商品に、売場に、"
              "キャンペーンに、そして生活者との毎日の接点に変わっていきます。")
title(s, "いまの熱量が、商品と売場に変わる")
rule(s)
statement(s, [
    ("いまご覧いただいた熱量は、ステージの中だけで終わるものではありません。", "gray"),
    ("商品に、売場に、キャンペーンに変わっていきます。", "ink"),
    ("――生活者との毎日の接点へ。", "purple"),
])

# 4. 60周年の現在地
s = new_slide("60周年の現在地", "SLIDE 04|60周年の現在地",
              "60周年はすでに動き出しています。イベント、商品化、コラボ、流通。この盛り上がりは今年で"
              "終わるものではなく、2027年度以降につながっていきます。")
title(s, "60周年は、もう始まっている――イベント・商品化・コラボ・流通がすでに動いている")
rule(s)
lead(s, "異なるファン層・異なる売場に向けた展開が、同時並行で進行中")
cards(s, [
    ("国内外イベント", "ウルサマ/ライブ/展覧会/ヒーローショー/グリーティング", "lilac"),
    ("商品化", "食品・アパレル・雑貨・玩具・文具・コレクション", "lilac"),
    ("IPコラボ", "モフサンド、ベイブレード ほか", "gray"),
    ("流通", "ウルトラマート、POPUP、量販・専門店", "dark"),
], y=2.35, h=1.5, n_cols=2)
note(s, "【素材8待ち】実績写真グリッド(8〜12点)に差し替え予定。数字より「動いている感」を重視", y=5.75)
callout(s, "キーメッセージ", "この盛り上がりは今年で終わらない――2027年度以降につながっていく")

# 5. なぜ今ウルトラマンなのか
s = new_slide("60周年の現在地", "SLIDE 05|60周年の現在地",
              "ウルトラマンの強みは、単なるリーチの広さではありません。年間約70万〜100万人規模のリアル"
              "接点を通じて、“直接会いに来るファン”との濃い関係を持っていることです。"
              "※「100万人に届きます」という単独リーチ表現は使わない。")
title(s, "ウルトラマンの強みは、単純なリーチではなく“熱量あるリアル接点”である")
rule(s)
lead(s, "年間約70万〜100万人規模のリアル接点――“直接会いに来るファン”との濃い関係")
table_block(s,
            ["レイヤー", "役割", "例"],
            [["マス接点", "認知を広げる", "テレビ、映画、YouTube、SNS、PR"],
             ["熱量接点", "ファン化する", "ウルサマ、ライブ、ヒーローショー、グリーティング"],
             ["購買接点", "商品化につなげる", "店頭、POPUP、ウルトラマート、EC、キャンペーン"],
             ["継続接点", "次の商品・作品へ戻す", "新シリーズ、映画、イベント、限定商品"]],
            2.25, [Inches(2.0), Inches(3.0), Inches(7.2)])
note(s, "【補強データ待ち】満席率・稼働率・リピート率の確定後に表現を最終化(強ければ「キャパ上限に近い」訴求へ)", y=4.6)
callout(s, "キーメッセージ", "マスで広げ、リアルで熱量を高め、流通・商品化で購買につなげる――この一連の流れがウルトラマンの強み")

# 6. 全体戦略(ステートメント)
s = new_slide("コンテンツ戦略", "SLIDE 06|コンテンツ戦略",
              "2027年度以降、ウルトラマンは単発の作品展開ではなく、テレビ、映画、イベント、YouTube、"
              "流通、IPコラボを連動させた“面の展開”に入ります。")
title(s, "2027年度以降、単発の作品展開から“面の展開”へ")
rule(s)
statement(s, [
    ("テレビ、映画、イベント、YouTube、流通、IPコラボ。", "gray"),
    ("それぞれが連動して動く、「年間型IP」へ。", "ink"),
    ("――年間を通じて、生活者との接点を作り続けます。", "purple"),
])

# 7. 3つの柱
s = new_slide("コンテンツ戦略", "SLIDE 07|コンテンツ戦略",
              "ここからは、2027年度以降のコンテンツ展開を3つの柱でご説明します。")
title(s, "コンテンツ戦略は3つの柱――テレビ・映画・YouTubeが商機のタイミングをつくる")
rule(s)
lead(s, "3つの柱が連動し、商品化・販促のタイミングを一年中つくり出す")
cards(s, [
    ("① 新テレビシリーズ", "継続性を重視した世界観・キャラクター展開", "lilac"),
    ("② 映画・特別編・ゼロ関連", "公開タイミング=販促・店頭の商機", "lilac"),
    ("③ YouTube/ギャラファイ", "歴代ヒーロー・怪獣を横断活用", "lilac"),
], y=2.45, h=1.7)
placeholder(s, "【素材1待ち―本編の核】2027年以降のコンテンツ全体像(7/14確認会までに回収)", 4.55)
callout(s, "キーメッセージ", "単発の「点」ではなく、年間を通じた「面」で商機が生まれる")

# 8. 新テレビシリーズ
s = new_slide("コンテンツ戦略", "SLIDE 08|コンテンツ戦略|柱①",
              "2027年度以降のテレビシリーズでは、キャラクターや世界観の継続性をより重視し、ファンが次の"
              "展開を追い続けたくなる構造を強化していきます。"
              "【NG】「3年連続で同じ世界線」「テレビ局が変わるかも」には一切触れない。")
title(s, "新テレビシリーズ――ファンが「追い続けたくなる」構造へ")
rule(s)
lead(s, "キャラクターや世界観の継続性をより重視し、次の展開を追い続けたくなる構造を強化する")
sections(s, [
    ("ライセンシーの皆さまにとっての意味", [
        "世界観・キャラクターの継続性は、商品ラインの継続展開・シリーズ化のしやすさに直結する",
        "「次の展開」があることが、ファンの購買モチベーションを持続させる",
    ]),
])
placeholder(s, "【素材2・3・13待ち/開示確認】制作部の開示可能コピー・世界観イメージ・シルエット等で差し替え", 4.3)
callout(s, "キーメッセージ", "継続性ある展開が、商品も売場も「単発」から「シリーズ」に変える")

# 9. 映画・ゼロ関連
s = new_slide("コンテンツ戦略", "SLIDE 09|コンテンツ戦略|柱②",
              "映画館、配信、イベント、商品化を連動させ、作品接点を売場・キャンペーンに接続していきます。"
              "特に食品、外食、流通、アパレル、広告の皆さまには、映画のタイミングでご一緒できる企画を"
              "ご用意していきます。")
title(s, "映画・ゼロ関連――公開タイミングが、販促と店頭の商機になる")
rule(s)
lead(s, "映画館 × 配信 × イベント × 商品化を連動させ、作品接点を売場・キャンペーンに接続する")
sections(s, [
    ("展開の考え方", [
        "ゼロ関連映画・特別編・スピンオフ(開示可能範囲で)",
        "公開期は、店頭キャンペーン・タイアップ・限定商品の最大の山場になる",
    ]),
    ("特にご一緒したい業種", [
        "食品・外食・流通・アパレル・広告代理店――映画タイミングの連動企画",
    ]),
])
placeholder(s, "【素材4・5待ち/開示確認】ゼロ映画・特別編の開示可能情報", 4.55)
callout(s, "キーメッセージ", "映画の公開日は、皆さまのキャンペーンの開始日になる")

# 10. YouTube/ギャラファイ
s = new_slide("コンテンツ戦略", "SLIDE 10|コンテンツ戦略|柱③",
              "YouTube・配信領域では、幅広いヒーローとキャラクターを活用し、コアファンにも新規層にも届く"
              "接点を再強化します。ライセンシーの皆さまにとっては、歴代ヒーローや怪獣まで横断的に使える、"
              "企画自由度の高い領域です。")
title(s, "YouTube/ギャラファイ――歴代ヒーロー・怪獣を横断的に使える、企画自由度の高い領域")
rule(s)
lead(s, "コアファンにも新規層にも届く接点を、配信領域で再強化する")
sections(s, [
    ("この領域の特長", [
        "単独ヒーローに限らず、歴代ヒーロー・怪獣・人気キャラを横断的に活用できる",
        "コレクション系・大人向け・怪獣デザイン商品との相性が良い",
    ]),
])
placeholder(s, "【素材6待ち/開示確認】ギャラファイ/YouTube系の開示可能情報", 4.3)
callout(s, "キーメッセージ", "使えるキャラクターの幅が、企画の幅になる")

# 11. イベント・リアル接点
s = new_slide("コンテンツ戦略", "SLIDE 11|コンテンツ戦略",
              "ウルトラマンには“直接会いに来るファン”がいます。この熱量あるリアル接点が、商品購買や"
              "店舗送客に直結します。")
title(s, "会いに来るファンがいる――リアル接点は、購買と送客に直結する")
rule(s)
lead(s, "ウルサマ・ライブ・展覧会・ヒーローショー・グリーティングが、年間を通じて熱量を生む")
sections(s, [
    ("リアル接点の価値", [
        "“直接会いに来るファン”との接点は、物販・店舗送客・キャンペーン参加への転換率が高い",
        "イベント来場の前後は、周辺店舗・コラボ企画への送客機会になる",
    ]),
])
placeholder(s, "【補強データ待ち】満席率・稼働率・リピート率――強ければ「キャパ上限に近い」ことを示す", 4.3)
callout(s, "キーメッセージ", "会いに来るファンの熱量を、貴社の売場と店舗に接続できる")

# 12. マーケティングカレンダー
s = new_slide("コンテンツ戦略", "SLIDE 12|コンテンツ戦略",
              "ご覧の通り、2027年度以降は年間を通じて山場が続きます。商品開発のリードタイムを考えると、"
              "2027年度の山場に間に合わせるには、今から企画に入っていただくのがベストタイミングです。")
title(s, "2027年度以降の商機カレンダー――「いつ企画に入れば間に合うか」を示す")
rule(s)
lead(s, "年間の山場(テレビ・映画・イベント・流通施策)を時系列で提示し、企画開始の目安を明記する")
sections(s, [
    ("カレンダーの読み方", [
        "「いつ盛り上がるか」「いつ企画に入れば間に合うか」が読み取れることが絶対条件",
        "商品開発リードタイムから逆算した「企画開始の目安」を各山場に明記",
    ]),
])
placeholder(s, "【素材7待ち】60周年マーケティングカレンダー+2027年以降版のビジュアルに差し替え", 4.3)
callout(s, "キーメッセージ", "2027年度の山場に間に合わせるなら、企画開始は「いま」がベストタイミング")

# 13. 営業パート導入(ステートメント)
s = new_slide("営業戦略", "SLIDE 13|営業戦略",
              "ここからは、各カテゴリーの皆さまと一緒に、具体的な商品化・販促企画を作っていきたいと"
              "考えています。「うちならこう作れる」という目線でご覧ください。")
title(s, "ここからは「皆さまの企画」の話です")
rule(s)
statement(s, [
    ("過去実績のご紹介ではありません。", "gray"),
    ("今後ご一緒したい企画の、募集です。", "ink"),
    ("――7カテゴリー別に、商機と企画例をご提案します。", "purple"),
])

# 14-20. カテゴリー
category_slide(14, "食品・飲料", "夏のウルトラマン接点を、親子向けキャンペーンに",
               "夏のウルトラマン接点を、親子向け食品・飲料キャンペーンに変えられます。",
               "夏映画、ウルサマ、親子需要、店頭キャンペーン",
               "限定パッケージ/購入特典/親子キャンペーン/映画半券連動/夏休み販促",
               "映画・イベントの山場と店頭を連動させる企画を、ぜひご一緒させてください。")
category_slide(15, "外食・カフェ", "来場・視聴の熱量を、店舗送客に",
               "来場・視聴の熱量を、店舗送客に接続できます。",
               "イベント来場前後、映画公開期、ファミリー来店",
               "コラボメニュー/ノベルティ/来店特典/ヒーローグリーティング連動",
               "イベント会場の周辺送客や、映画公開期のファミリー需要の取り込みにご活用いただけます。")
category_slide(16, "アパレル", "大人が着られるデザインIPとして",
               "ウルトラマンは子ども向けだけでなく、大人が着られるデザインIPとして展開できます。",
               "大人ファン、親子リンク、女性向け、ストリート、怪獣デザイン",
               "Tシャツ/スウェット/バッグ/キャップ/親子コーデ/限定コレクション",
               "怪獣デザインやストリート系まで展開できます。")
category_slide(17, "雑貨・生活用品", "“毎日使う商品”に落とし込む",
               "ウルトラマンを“毎日使う商品”に落とし込めます。",
               "日常接点、ギフト、オフィス、家庭用品",
               "タンブラー/タオル/ステーショナリー/インテリア/ガジェット小物",
               "ファンの日常に入り込む雑貨・生活用品は、継続的な売上を作れる領域です。")
category_slide(18, "文具・教育・出版", "勇気・成長・仲間・正義を、学びの領域へ",
               "勇気、成長、仲間、正義というテーマを教育・文具領域に広げられます。",
               "キッズ、親子、学習、読書、夏休み",
               "学習帳/絵本/図鑑/ワークブック/読書キャンペーン",
               "ウルトラマンのテーマは、教育・文具領域と本質的に相性が良いものです。")
category_slide(19, "流通・小売", "商品だけでなく、売場をつくる",
               "商品を作るだけでなく、売場を作る準備があります。",
               "ウルトラマート、POPUP、量販店、専門店、売場ジャック",
               "専用棚/期間限定売場/購入特典/スタンプラリー/限定商品",
               "ウルトラマートやPOPUPと連動した売場企画を、流通・小売の皆さまとご一緒したいと考えています。")
category_slide(20, "広告代理店・SP会社", "ウルトラマンを、広告・販促装置として",
               "クライアント課題に合わせて、ウルトラマンを広告・販促装置として活用できます。",
               "企業キャンペーン、地域創生、ファミリー向け販促、周年施策",
               "企業タイアップ/店頭キャンペーン/交通広告/SNSキャンペーン/イベント協賛",
               "ファミリー、地域、周年など、課題起点でのご相談を歓迎します。")

# 21. IPコラボ実績
s = new_slide("IPコラボ・流通", "SLIDE 21|IPコラボ・流通",
              "60周年では、異なるファン層・異なる売場に向けて、すでに多様なコラボが動いています。"
              "※実績(このスライド)と今後の機会(次)を必ず分ける。")
title(s, "60周年、多様なIPコラボがすでに動いている")
rule(s)
lead(s, "異なるファン層・異なる売場に向けて、すでに実績が積み上がっている")
cards(s, [
    ("モフサンド", "【素材8待ち】実績ビジュアル", "lilac"),
    ("ベイブレード", "【素材8待ち】実績ビジュアル", "lilac"),
    ("その他既存コラボ", "商品化・イベント・流通施策", "gray"),
], y=2.45, h=1.7)
callout(s, "キーメッセージ", "コラボは「これから始める」のではなく、「すでに動いて成果が出ている」")

# 22. 今後のIPコラボ機会
s = new_slide("IPコラボ・流通", "SLIDE 22|IPコラボ・流通",
              "ここからは、皆さまと一緒に商品化・売場化していきたい領域です。(サンリオ開示可の場合)"
              "サンリオコラボ実現時には、両IPの魅力を活かした商品化・売場展開をライセンシーの皆さまと"
              "広げていきます。")
title(s, "ここからは、皆さまと一緒に商品化・売場化していきたい領域")
rule(s)
lead(s, "これからの大型機会に、企画の初期段階から入っていただきたい")
sections(s, [
    ("今後の大型機会", [
        "サンリオコラボ【開示確認後に表現確定】",
        "ゼロ映画連動/新テレビシリーズ連動",
        "YouTube・ギャラファイ系",
        "ウルトラマート・流通展開",
    ]),
])
note(s, "サンリオは「決定」ではなく、ライセンシー側の参加余地を見せる表現で(7/14に言及レベルを確定)", y=4.7)
callout(s, "キーメッセージ", "実現時には、両IPの魅力を活かした商品化・売場展開をライセンシーの皆さまと広げていく")

# 23. ウルトラマート
s = new_slide("IPコラボ・流通", "SLIDE 23|IPコラボ・流通",
              "ウルトラマンの商品を売る場所を、円谷側でも増やしていきます。だから、商品化したものを展開"
              "できる場が広がっています。「作っても売る場所があるのか」という不安には、売場ごとお応えします。")
title(s, "売る場所は、円谷側でも増やしていく――「作っても売る場所があるのか」に応える")
rule(s)
lead(s, "ウルトラマート・POPUP・売場展開が、ライセンシーが商品を作る理由になる")
sections(s, [
    ("売場の広がり", [
        "ウルトラマートの方向性/POPUP展開",
        "量販店・専門店での売場展開/映画・イベント期の店頭施策",
        "既存商品の売場事例/今後募集したい商品カテゴリー",
    ]),
])
placeholder(s, "【素材10待ち】ウルトラマート素材・売場事例写真", 4.55)
callout(s, "キーメッセージ", "商品を作っていただければ、展開できる売場を円谷側でも用意していく")

# 24. スタイルガイド
s = new_slide("スタイルガイド・監修", "SLIDE 24|スタイルガイド・監修",
              "今回のコンテンツ展開に合わせて、ライセンシーの皆さまがすぐ企画化できるよう、カテゴリー別の"
              "スタイルガイドと素材提供体制を整えていきます。「素材がある」ではなく「企画しやすいように、"
              "カテゴリー別に使える形にしてある」——ここを目指しています。")
title(s, "スタイルガイドが、「作りたい」を「作れる」に変える")
rule(s)
lead(s, "すぐ企画化できるよう、カテゴリー別のスタイルガイドと素材提供体制を整備する")
table_block(s,
            ["ガイド", "内容"],
            [["ブランドガイド", "ロゴ、世界観、コピー、NG表現"],
             ["キャラクターガイド", "ヒーロー、怪獣、歴代キャラ、新作関連キャラ"],
             ["カテゴリー別ガイド", "食品、アパレル、雑貨、文具、広告、流通"],
             ["シーズン別ガイド", "映画期、夏休み、年末年始、周年施策"]],
            2.3, [Inches(3.0), Inches(9.2)])
callout(s, "キーメッセージ", "「素材がある」ではなく、「企画しやすいように、カテゴリー別に使える形にしてある」")

# 25. 素材提供・監修フロー
s = new_slide("スタイルガイド・監修", "SLIDE 25|スタイルガイド・監修",
              "企画提出から承認までの流れを標準化しています。個別商談では、NDAのうえでさらに詳細な素材を"
              "ご覧いただけます。")
title(s, "企画から承認まで、迷わない――素材提供と監修フローを標準化する")
rule(s)
lead(s, "企画提出 → 初稿確認 → 修正 → 承認。標準リードタイムを明記し、進め方の不安をなくす")
sections(s, [
    ("提供するもの", [
        "商品化テンプレート:パッケージ例/POP例/販促例/SNS例",
        "監修フロー:企画提出 → 初稿確認 → 修正 → 承認(標準リードタイム明記)",
        "開示区分:当日開示/NDA後開示/個別商談時開示",
    ]),
])
placeholder(s, "【素材11・12待ち】スタイルガイド進捗・監修フロー資料", 4.55)
callout(s, "キーメッセージ", "個別商談では、NDAのうえでさらに詳細な素材をご覧いただける")

# 26. 企画募集テーマ
s = new_slide("クロージング", "SLIDE 26|クロージング",
              "以上のテーマで、いま企画を募集しています。「この枠に自社が入れるか」という段階からのご相談で"
              "構いません。")
title(s, "いま、7つのカテゴリーで企画を募集しています")
rule(s)
numbered_rows(s, [
    ("1", "食品・飲料", "夏の親子キャンペーン/映画連動販促"),
    ("2", "外食・カフェ", "コラボメニュー/送客連動企画"),
    ("3", "アパレル", "大人向け・親子リンクコレクション"),
    ("4", "雑貨・生活用品", "日常使いの定番商品"),
    ("5", "文具・教育・出版", "学び×ウルトラマン企画"),
    ("6", "流通・小売", "売場ジャック/限定売場企画"),
    ("7", "広告代理店・SP", "企業タイアップ/地域・周年施策"),
], y=1.85, row_h=0.5, gap=0.11, highlight_last=False)
callout(s, "ご相談の入口", "「この枠に自社が入れるか」という段階からのご相談で構いません")

# 27. 個別商談・相談導線
s = new_slide("クロージング", "SLIDE 27|クロージング",
              "お手元の資料とこちらのQRコードから、個別商談をご予約いただけます。カテゴリーごとに担当が"
              "ついてご相談を承ります。【運営】QRは後方からも読めるサイズで最低30秒表示。次スライドでも"
              "画面隅に残す。")
title(s, "今日から動けます――個別商談のご予約はこちら")
rule(s)
lead(s, "本日を起点に、カテゴリーごとの担当がご相談を承ります")
qr = rect(s, ML, Inches(2.35), Inches(2.9), Inches(2.9), LILAC, PURPLE, Pt(1.2),
          dash=True, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
tfq = qr.text_frame; tfq.word_wrap = True
tfq.vertical_anchor = MSO_ANCHOR.MIDDLE
for qi, qline in enumerate(["【QRコード】", "個別商談予約", "(希望カテゴリー選択式)"]):
    pq = tfq.paragraphs[0] if qi == 0 else tfq.add_paragraph()
    pq.alignment = PP_ALIGN.CENTER
    rq = pq.add_run(); rq.text = qline
    style_run(rq, 13 if qi < 2 else 10, DK, bold=(qi < 2))
box = slide_box = s.shapes.add_textbox(Inches(3.9), Inches(2.5), Inches(8.8), Inches(2.6))
tf = box.text_frame; tf.word_wrap = True
for i, it in enumerate([
    "配布資料に相談窓口・連絡先を記載しています",
    "NDA締結後、開示可能な詳細素材をご覧いただけます",
    "カテゴリーごとに担当がついて、ご相談を承ります",
]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(10); p.line_spacing = 1.3
    r = p.add_run(); r.text = "■ " + it
    style_run(r, 12.5, BODY)
callout(s, "次のアクション", "QRから個別商談をご予約ください――本日を起点に、企画のご相談を始めましょう")

# 28. クロージング(ステートメント)
s = new_slide("クロージング", "SLIDE 28|クロージング",
              "今、企画に入る企業が、2027年度以降のウルトラマンの売場とキャンペーンを先に作ることが"
              "できます。ぜひ本日を起点に、個別にご相談ください。本日はありがとうございました。")
title(s, "次の売場を、いま一緒につくる。")
rule(s)
statement(s, [
    ("2027年度以降のウルトラマンは、作品・イベント・流通・商品化が連動する「年間型IP」へ。", "gray"),
    ("今、企画に入る企業が、次の売場とキャンペーンを先に作る。", "ink"),
    ("――ぜひ本日を起点に、個別にご相談ください。", "purple"),
], y=2.7)

OUT = "ULTRAMAN_LICENSEE_PRESENTATION_draft_v2.pptx"
prs.save(OUT)
print(f"saved {OUT} with {len(prs.slides._sldIdLst)} slides")
