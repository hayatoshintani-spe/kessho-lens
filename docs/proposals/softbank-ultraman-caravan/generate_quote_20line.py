# -*- coding: utf-8 -*-
"""週20ライン×2年間のお見積り(SB提示用・円谷フォーマット)"""
import os

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

INK = RGBColor(0x1A, 0x1A, 0x1A)
SUB = RGBColor(0x5A, 0x62, 0x6B)
RED = RGBColor(0xC0, 0x00, 0x00)
NAVY = RGBColor(0x23, 0x22, 0x78)
SILVER = RGBColor(0x8E, 0x94, 0x9B)
PALE = RGBColor(0xF2, 0xF4, 0xF6)
PALE_RED = RGBColor(0xFB, 0xEA, 0xEB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TSUB_NAVY = RGBColor(0x1F, 0x33, 0x8C)
FONT = "Meiryo"
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
BAND_IMG = os.path.join(ASSETS, "band_header.png")
COVER_IMG = os.path.join(ASSETS, "band_cover.png")

SW, SH = Inches(13.333), Inches(7.5)
prs = Presentation()
prs.slide_width, prs.slide_height = SW, SH
BLANK = prs.slide_layouts[6]
page_no = [0]


def set_font(run, size, color=INK, bold=False):
    f = run.font
    f.name = FONT
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ea')
    if ea is None:
        from lxml import etree
        ea = etree.SubElement(rPr, '{http://schemas.openxmlformats.org/drawingml/2006/main}ea')
    ea.set('typeface', FONT)


def add_slide():
    page_no[0] += 1
    return prs.slides.add_slide(BLANK)


def textbox(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, gap=5):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, item in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(gap)
        for (t, sz, c, b) in (item if isinstance(item, list) else [item]):
            r = p.add_run()
            r.text = t
            set_font(r, sz, c, b)
    return box


def rect(slide, x, y, w, h, fill=None, shape=MSO_SHAPE.RECTANGLE):
    sp = slide.shapes.add_shape(shape, x, y, w, h)
    sp.shadow.inherit = False
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    sp.line.fill.background()
    return sp


def footer(slide):
    textbox(slide, Inches(5.17), Inches(7.16), Inches(3.0), Inches(0.28),
            [("© TSUBURAYA PRODUCTIONS", 8, SILVER, False)], align=PP_ALIGN.CENTER)
    textbox(slide, Inches(10.25), Inches(7.1), Inches(2.2), Inches(0.3),
            [("Strictly Confidential", 10, RED, True)], align=PP_ALIGN.RIGHT)
    textbox(slide, Inches(12.6), Inches(7.1), Inches(0.5), Inches(0.3),
            [(str(page_no[0]), 10, SILVER, False)], align=PP_ALIGN.RIGHT)


def header(slide, title, sub=None):
    slide.shapes.add_picture(BAND_IMG, 0, 0, width=SW, height=Inches(0.86))
    textbox(slide, Inches(0.5), Inches(0.08), Inches(11.2), Inches(0.7),
            [(title, 21, WHITE, True)], anchor=MSO_ANCHOR.MIDDLE)
    if sub:
        textbox(slide, Inches(0.55), Inches(0.98), Inches(12.2), Inches(0.4),
                [(sub, 12.5, SUB, False)])
    footer(slide)


def add_table(slide, x, y, w, headers, rows, col_widths=None, font_size=11.5, row_h=0.5):
    n_rows = len(rows) + 1
    tbl = slide.shapes.add_table(n_rows, len(headers), x, y, w, Inches(row_h * n_rows)).table
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = int(w * cw / total)
    for j, htxt in enumerate(headers):
        c = tbl.cell(0, j)
        c.fill.solid(); c.fill.fore_color.rgb = NAVY
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.margin_left = c.margin_right = Inches(0.08)
        p = c.text_frame.paragraphs[0]
        r = p.add_run(); r.text = htxt
        set_font(r, font_size, WHITE, True)
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            c = tbl.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = WHITE if i % 2 == 1 else PALE
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_left = c.margin_right = Inches(0.08)
            text, bold, color = val, False, INK
            if isinstance(val, tuple):
                text, bold = val[0], val[1]
                color = val[2] if len(val) > 2 else INK
            for k, line in enumerate(str(text).split("\n")):
                p = c.text_frame.paragraphs[0] if k == 0 else c.text_frame.add_paragraph()
                r = p.add_run(); r.text = line
                set_font(r, font_size, color, bold)
    return tbl


# =============================================================================
# 1. 表紙
# =============================================================================
s = add_slide()
s.shapes.add_picture(COVER_IMG, 0, 0, width=Inches(4.09), height=SH)
textbox(s, Inches(4.5), Inches(1.25), Inches(8.4), Inches(0.5),
        [("ソフトバンク株式会社 御中", 14, SUB, False)], align=PP_ALIGN.CENTER)
textbox(s, Inches(4.5), Inches(2.25), Inches(8.4), Inches(2.0), [
    ("ウルトラマンIP 店頭イベント展開", 30, INK, True),
    ("お見積り(週20ライン・2年間)", 26, INK, True),
], align=PP_ALIGN.CENTER, gap=10)
textbox(s, Inches(4.5), Inches(4.2), Inches(8.4), Inches(0.9), [
    ("週20ライン(月80開催)× 2年間の継続展開に関する", 13.5, INK, False),
    ("概算お見積りのご提示", 13.5, INK, False),
], align=PP_ALIGN.CENTER, gap=4)
textbox(s, Inches(4.5), Inches(5.7), Inches(8.4), Inches(1.0), [
    ("2026年10月", 15, TSUB_NAVY, True),
    ("(株)円谷プロダクション", 15, TSUB_NAVY, True),
    ("金額はすべて税別・概算", 10.5, SILVER, False),
], align=PP_ALIGN.CENTER, gap=3)
textbox(s, Inches(5.17), Inches(7.16), Inches(3.0), Inches(0.28),
        [("© TSUBURAYA PRODUCTIONS", 8, SILVER, False)], align=PP_ALIGN.CENTER)
textbox(s, Inches(10.25), Inches(7.1), Inches(2.5), Inches(0.3),
        [("Strictly Confidential", 10, RED, True)], align=PP_ALIGN.RIGHT)

# =============================================================================
# 2. ご相談内容の整理(お見積りの前提)
# =============================================================================
s = add_slide()
header(s, "お見積りの前提:ご相談いただいた実施規模",
       "現在実施中のテスト(神奈川7会場)と同一のパッケージ形式を、週20ラインで2年間継続する想定で試算しています")
add_table(s, Inches(0.7), Inches(1.6), Inches(11.9),
          ["項目", "前提条件"],
          [
              [("実施規模", True), "週20ライン(20会場で同時開催)× 月4週 = 月80開催"],
              [("年間開催数", True), "960開催/年(月80開催 × 12ヶ月)"],
              [("契約期間", True), "2027年1月 〜 2028年12月の2年間(計1,920開催)"],
              [("実施形式", True), "写真撮影会型(現在のテストと同一のパッケージ:キャラクター出演・運営スタッフ・演出込み)\n※ステージショー型への変更は該当開催を200万円/開催で読み替え"],
              [("1開催の単位", True), "土日2日間・1会場での実施(1回30分×1日最大5回・1回あたり約50組対応)"],
          ],
          col_widths=[1.0, 3.6], row_h=0.62, font_size=12)
b = rect(s, Inches(0.7), Inches(5.3), Inches(11.9), Inches(1.15), fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
b.adjustments[0] = 0.07
textbox(s, Inches(1.0), Inches(5.45), Inches(11.3), Inches(0.95), [
    ("体制についてのご案内", 12.5, RED, True),
    ("週20ラインの同時稼働は、現行体制からの増強(スーツ・アクター・ディレクターの拡充)を伴います。増強には約3ヶ月の準備期間を要する"
     "ため、2027年1月開始の場合は2026年10月末までの契約締結をお願いしております。", 11.5, INK, False),
], gap=4)

# =============================================================================
# 3. お見積り(本体)
# =============================================================================
s = add_slide()
header(s, "お見積り:2年間合計 25億4,000万円(税別)+従量精算分",
       "固定・従量の構成はテストと同一です。ノベルティは貴社制作に切り替え、当社は下代の20%を許諾料として申し受けます")
add_table(s, Inches(0.7), Inches(1.6), Inches(11.9),
          ["費目", "単価・条件", "1年目", "2年目", "2年間合計"],
          [
              [("① 年間IP利用料", True), "年間包括ライセンス\n初年度特別価格を適用", "2,000万円\n(通常2,400万円)", "2,400万円", "4,400万円"],
              [("② ライブ費(イベント実施)", True), "100万円/開催 × 960開催\n(出演・運営・演出込み)", "9億6,000万円", "9億6,000万円", "19億2,000万円"],
              [("③ イベントキット利用料", True), "30万円/開催 × 960開催", "2億8,800万円", "2億8,800万円", "5億7,600万円"],
              [("小計(固定)", True), "", ("12億6,800万円", True), ("12億7,200万円", True), ("25億4,000万円", True, RED)],
              [("④ ノベルティ作成許諾料", True), "貴社制作ノベルティの\n下代(卸価格)の20%", "従量精算", "従量精算", "従量精算"],
          ],
          col_widths=[1.5, 1.9, 1.1, 1.0, 1.2], row_h=0.66, font_size=11.5)
textbox(s, Inches(0.7), Inches(5.68), Inches(11.9), Inches(0.4), [
    ("月額換算:約1億580万円/月(固定分)。実施されなかった開催分は請求いたしません(最低開催数のお約束は次頁)。", 11.5, NAVY, True),
])
textbox(s, Inches(0.7), Inches(6.08), Inches(11.9), Inches(0.85), [
    ("※ 着ぐるみ運搬・交通・宿泊費、スタッフ昼食費等の実費を全開催で別途申し受けます(会場確定後にお見積り)。", 10.5, SUB, False),
    ("※ 店頭訴求ツール(ポスター・チラシ等)の作成許諾料(作成費用の20%)は本見積りの対象外で、従来ご提示のとおり別途精算です。", 10.5, SUB, False),
    ("※ 連休等で3日間開催とする場合:ライブ費+50万円/日・キット+10万円/日を追加で申し受けます。", 10.5, SUB, False),
], gap=3)

# =============================================================================
# 4. 費目のご説明
# =============================================================================
s = add_slide()
header(s, "費目のご説明:お支払いいただく内容",
       "テストでは開催ごとの単価に内包していたIP利用の対価を、年間契約では包括ライセンスとして明確化しています")

def fee_block(x, y, w, h, title, lines):
    bb = rect(s, x, y, w, h, fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    bb.adjustments[0] = 0.06
    textbox(s, x + Inches(0.25), y + Inches(0.14), w - Inches(0.5), h - Inches(0.28),
            [(title, 13, RED, True)] + [(t, 11, INK, False) for t in lines], gap=4)

fee_block(Inches(0.7), Inches(1.6), Inches(5.8), Inches(2.3), "① 年間IP利用料(固定)", [
    "・店頭イベント・告知物・LP/Web・SNSでのIP利用を年間で包括",
    "・週20ライン同時稼働枠の優先確保(体制の専属化)",
    "・作成物の監修対応(KV3営業日・チラシ等1〜2営業日)",
    "・8ヒーローのキャラクター選択・切替(店舗・時期ごと)",
])
fee_block(Inches(6.8), Inches(1.6), Inches(5.8), Inches(2.3), "② ライブ費 100万円/開催", [
    "・キャラクター出演(着ぐるみ)・専属アクター・ディレクター",
    "・運営スタッフ・演出・BGM音素材・音響機材",
    "・現在のテストと同一内容・同一単価(実績ベース)",
    "・ステージショー型は200万円/開催で読み替え可能",
])
fee_block(Inches(0.7), Inches(4.1), Inches(5.8), Inches(2.3), "③ イベントキット利用料 30万円/開催", [
    "・バックパネル・装飾ツール等の会場設営一式",
    "・テストと同一の提供内容",
    "・長期契約に伴うキット保有形態の最適化(ご相談可能)",
])
fee_block(Inches(6.8), Inches(4.1), Inches(5.8), Inches(2.3), "④ ノベルティ作成許諾料(下代の20%)", [
    "・貴社にてノベルティを制作いただく方式に切り替え",
    "・当社は商品企画の監修と作成許諾を提供し、",
    "  下代(卸価格)の20%を許諾料として申し受けます",
    "・大量供給の安定化とコスト最適化が見込めます",
])

# =============================================================================
# 5. ご契約条件・ご留意事項
# =============================================================================
s = add_slide()
header(s, "ご契約条件・ご留意事項",
       "本見積りは以下の条件を前提としています。詳細は契約協議にて調整させてください")
add_table(s, Inches(0.7), Inches(1.6), Inches(11.9),
          ["項目", "条件"],
          [
              [("最低開催数のお約束", True), "年間770開催(計画数の8割)を最低開催数として設定させてください。体制増強の前提となるため、未達の場合も当該数量分を申し受けます"],
              [("ご契約期限", True), "2027年1月開始の場合、体制増強の準備期間(約3ヶ月)のため2026年10月末までの締結をお願いします"],
              [("キャンセル料", True), "個別開催の中止:開催30日前まで30%/14日前まで50%/13日前以降100%(ライブ費に適用)"],
              [("キャラクター", True), "8ヒーロー(初代ウルトラマン/タロウ/ティガ/ダイナ/ゼロ/アーク/オメガ/テオ)。権利調整の状況により一部変動の場合があります"],
              [("開催エリア", True), "会場リストを頂戴し次第、当社にて開催可否を確認します(一部実施できないエリアがあります)"],
              [("IP利用の範囲", True), "本契約に基づくイベント・告知目的に限ります。非公式商品の使用・販売はできません"],
              [("金額の前提", True), "すべて税別。本見積りは概算であり、正式見積書は条件確定後に発行します(有効期限:発行日より30日)"],
          ],
          col_widths=[1.1, 3.9], row_h=0.62, font_size=11)
textbox(s, Inches(0.7), Inches(6.68), Inches(11.9), Inches(0.4), [
    ("次のステップ:本見積りをたたき台に、開催エリア計画・最低開催数・お支払い条件を協議のうえ、正式見積書とご契約手続き(EDI発注)へ進めさせてください。", 11, NAVY, True),
])

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SB様提示用_お見積り_週20ライン2年間.pptx")
prs.save(OUT)
print("saved:", OUT)
