# -*- coding: utf-8 -*-
"""最低開催数保証(MG)を組み込んだお見積り(27ヶ月・基準15ライン)"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
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
ASSETS = os.path.join(HERE, "assets")
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


# ---- 数値(月別ライン供給計画27ヶ月版と同一前提) ----
# 期別:立ち上げ期 2027/1-3=26日、FY27 2027/4-2028/3=104日、FY28 2028/4-2029/3=104日
P = [
    ("第1期 2027年1月〜3月", 26, 500),
    ("第2期 2027年4月〜2028年3月", 104, 2000),
    ("第3期 2028年4月〜2029年3月", 105, 2000),
]
UNIT = 100000
LINES = 15
rows_p = []
tot_days = tot_sites = tot_live = tot_ip = tot_exp = 0
for name, days, ip in P:
    sites = days * LINES
    live = sites * UNIT
    exp = sites * 20000
    rows_p.append((name, days, sites, live, ip * 10000, exp))
    tot_days += days; tot_sites += sites; tot_live += live; tot_ip += ip * 10000; tot_exp += exp


def man(v):
    return f"{v // 10000:,}万円"


def oku(v):
    o = v / 100000000
    return f"{o:.2f}億円".replace(".00億", "億")


# 1. 表紙 --------------------------------------------------------------------
s = add_slide()
s.shapes.add_picture(COVER_IMG, 0, 0, width=Inches(4.09), height=SH)
textbox(s, Inches(4.5), Inches(1.25), Inches(8.4), Inches(0.5),
        [("ソフトバンク株式会社 御中", 14, SUB, False)], align=PP_ALIGN.CENTER)
textbox(s, Inches(4.5), Inches(2.25), Inches(8.4), Inches(2.0), [
    ("ウルトラソフトバンクフェス", 30, INK, True),
    ("お見積り(最低開催数保証プラン)", 26, INK, True),
], align=PP_ALIGN.CENTER, gap=10)
textbox(s, Inches(4.5), Inches(4.2), Inches(8.4), Inches(0.9), [
    ("2027年1月〜2029年3月(2年3ヶ月)・基準15ライン", 13.5, INK, False),
    ("ソフトバンク様特別プランによる概算お見積り", 13.5, INK, False),
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

# 2. 総括 ----------------------------------------------------------------------
s = add_slide()
header(s, f"お見積り総括:27ヶ月 合計 {oku(tot_live + tot_ip)}(税別)+従量精算分",
       "固定分(最低開催数保証と年間IP使用料)と、従量分(増枠・諸経費・許諾料・実費)に分けて記載しています")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["区分", "費目", "単価・条件", "27ヶ月合計"],
          [
              [("固定(最低保証)", True), "キャラクターイベント稼働費(最低開催数保証)", f"10万円/日 × 基準15ライン × {tot_days}日 = {tot_sites:,}現場", (oku(tot_live), True, RED)],
              [("固定", True), "IP使用料", "2,000万円/年×27ヶ月分。契約時に一括前払い", (man(tot_ip), True)],
              [("固定分 小計", True), "", "", (oku(tot_live + tot_ip), True, RED)],
              [("従量", True), "余裕月の増枠分(最大20ライン)", "10万円/日 × 増枠現場数(最大+470現場)", "最大 +4,700万円"],
              [("従量", True), "現場諸経費", "2万円/日 × 実施現場数", f"基準で {man(tot_exp)}"],
              [("従量", True), "作成許諾ロイヤリティ(最低保証付き)", "作成費用の20%(製造数量ベースで契約年度ごとに最低保証を設定)", "次頁参照"],
              [("従量", True), "3連休等の3日目/フル運営オプション", "+10万円/日/+22万円/日(会場単位)", "実施分"],
              [("実費", True), "交通運搬費・宿泊費・スーツ送料", "全国基準料金表により会場確定時に算定", "実費精算"],
          ],
          col_widths=[1.2, 2.6, 3.2, 1.4], row_h=0.56, font_size=11)
textbox(s, Inches(0.7), Inches(6.65), Inches(11.9), Inches(0.4), [
    ("※ 最低保証分は未実施の場合も申し受けます。増枠分・諸経費・許諾料・実費は実施・製造の実績に基づき精算します。", 10.5, SUB, False),
])

# 3. 期別内訳 ------------------------------------------------------------------
s = add_slide()
header(s, "期別の最低保証額と精算スケジュール",
       "最低保証は3つの精算期間に区切り、各期末に実績との差額(未達分・増枠分)を精算します")
rows = []
for i, (name, days, sites, live, ip, exp) in enumerate(rows_p):
    ip_txt = f"{man(tot_ip)}\n(27ヶ月分を契約時一括)" if i == 0 else "—"
    ip_val = tot_ip if i == 0 else 0
    rows.append([(name, True), f"{days}日", f"{sites:,}現場", (man(live), True), ip_txt, (man(live + ip_val), True, RED), f"{man(exp)}"])
rows.append([("合計(27ヶ月)", True), f"{tot_days}日", f"{tot_sites:,}現場", (man(tot_live), True), man(tot_ip), (oku(tot_live + tot_ip), True, RED), man(tot_exp)])
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["精算期間", "開催日数", "最低保証現場数", "稼働費(最低保証)", "IP使用料", "固定分 計", "現場諸経費(参考)"],
          rows, col_widths=[2.2, 0.9, 1.2, 1.4, 1.4, 1.3, 1.2], row_h=0.6, font_size=11)
b = rect(s, Inches(0.7), Inches(4.7), Inches(11.9), Inches(2.0), fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
b.adjustments[0] = 0.06
textbox(s, Inches(1.0), Inches(4.85), Inches(11.3), Inches(1.8), [
    ("精算の考え方", 13, RED, True),
    ("・各期の最低保証額は期初(第1期は契約時)に確定。四半期ごとの前払い(お支払い条件はご相談)", 11.5, INK, False),
    ("・期末に実績を集計。余裕月の増枠分は追加精算、最低保証を下回った場合も保証額をお支払いいただく", 11.5, INK, False),
    ("・第1期(2027年1〜3月)は立ち上げ期として、会場の確定状況にかかわらず15ライン体制を貴社専属で確保する定額期間", 11.5, INK, False),
    ("・IP使用料は27ヶ月分(4,500万円)を契約時に一括前払い", 11.5, INK, False),
], gap=4)

# 4. 許諾料MG ------------------------------------------------------------------
s = add_slide()
header(s, "作成許諾ロイヤリティ(最低保証付き)の考え方",
       "貴社制作のイベントキット・ノベルティ・店頭訴求ツールが対象。製造数量をもとに契約年度ごとに最低保証を設定")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["項目", "内容"],
          [
              [("対象", True), "貴社が制作するイベントキット(バックバナー等の備品を含む)・ノベルティ・店頭訴求ツール"],
              [("料率", True), "作成費用(製造原価)の20%"],
              [("最低保証", True), "契約年度ごとに想定製造数量に基づく最低保証額を設定(第1期+第2期で1年3ヶ月分、第3期で1年分)。実績が上回る場合は差額を精算"],
              [("想定数量(仮置き)", True), "撮影会1開催あたり約400個 × 1,755開催(27ヶ月・基準)= 約70万個。作成単価は品目構成により確定"],
              [("参考:最低保証額の目安", True), "平均作成単価30円台の構成なら27ヶ月で約450〜500万円、高単価品(タオル・トート等)中心の構成なら数千万円規模。貴社の数量・品目確定後に確定"],
              [("手続き", True), "品目ごとの仮申請→当社監修→製造。製造数量は四半期ごとにご報告いただき精算"],
          ],
          col_widths=[1.4, 4.6], row_h=0.66, font_size=11)
textbox(s, Inches(0.7), Inches(6.3), Inches(11.9), Inches(0.6), [
    ("※ 修了証ステッカー等を当社既存商品でご購入いただく場合は、本許諾料とは別に商品代金(卸価格)でのお取引となります。", 10.5, SUB, False),
])

# 5. 条件・備考 ----------------------------------------------------------------
s = add_slide()
header(s, "お見積り条件(備考)", "本見積りは以下の条件を前提としています。正式見積書・契約書に同内容を記載します")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["項目", "条件"],
          [
              [("契約期間・締結", True), "2027年1月〜2029年3月。2026年11月末までのご締結を前提"],
              [("特別価格の適用", True), "本件限りの条件(年間契約+最低開催数保証が前提)。単発・スポットは通常価格(225,000円/日)"],
              [("開催確定・キャンセル", True), "会場・日程は開催1ヶ月前までに確定。確定後のキャンセル料:1ヶ月前〜14日前30%/13日前〜7日前50%/6日前〜当日100%"],
              [("中途解約", True), "残期間の最低保証額を精算"],
              [("ライン供給", True), "基準15ライン。余裕月(1・4・6・11・12月)は最大20ライン。2・3・8・9月は当社主催行事との調整月"],
              [("エリア・キャラクター", True), "関信越エリア(埼玉・茨城・群馬・栃木・山梨・長野・新潟)は2027年1〜3月は実施不可。ウルトラセブンは対象外。出演は8ヒーロー(権利調整により一部変動の場合あり)"],
              [("排他", True), "契約期間中、当社は国内の他の携帯キャリア(3社)との店頭イベント契約を行いません"],
              [("お支払い", True), "貴社EDI発注・翌月末振込。IP使用料は契約時に27ヶ月分を一括前払い、最低保証分は四半期前払い(ご相談)。期間一括の発注形態をご相談。すべて税別"],
              [("有効期限", True), "本見積りの有効期限は発行日より30日"],
          ],
          col_widths=[1.4, 4.6], row_h=0.52, font_size=10.5)

OUT = os.path.join(HERE, "SB様提示用_お見積り_最低保証プラン.pptx")
prs.save(OUT)
print("saved:", OUT)
print("days", tot_days, "sites", tot_sites, "live", tot_live, "ip", tot_ip, "exp", tot_exp)
