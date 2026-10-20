# -*- coding: utf-8 -*-
"""10/22 SBミーティング投影用デッキ(円谷フォーマット)"""
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


def block(slide, x, y, w, h, title, lines, size=11):
    bb = rect(slide, x, y, w, h, fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    bb.adjustments[0] = 0.06
    textbox(slide, x + Inches(0.25), y + Inches(0.14), w - Inches(0.5), h - Inches(0.28),
            [(title, 13, RED, True)] + [(t, size, INK, False) for t in lines], gap=4)


# 1. 表紙 --------------------------------------------------------------------
s = add_slide()
s.shapes.add_picture(COVER_IMG, 0, 0, width=Inches(4.09), height=SH)
textbox(s, Inches(4.5), Inches(1.25), Inches(8.4), Inches(0.5),
        [("ソフトバンク株式会社 御中", 14, SUB, False)], align=PP_ALIGN.CENTER)
textbox(s, Inches(4.5), Inches(2.25), Inches(8.4), Inches(2.0), [
    ("ウルトラソフトバンクフェス", 30, INK, True),
    ("本格実施に向けたご確認事項", 26, INK, True),
], align=PP_ALIGN.CENTER, gap=10)
textbox(s, Inches(4.5), Inches(4.2), Inches(8.4), Inches(0.9), [
    ("テストイベントの振り返り/役割分担/ご提供条件/今後の進め方", 13.5, INK, False),
], align=PP_ALIGN.CENTER, gap=4)
textbox(s, Inches(4.5), Inches(5.7), Inches(8.4), Inches(1.0), [
    ("2026年10月22日", 15, TSUB_NAVY, True),
    ("(株)円谷プロダクション", 15, TSUB_NAVY, True),
    ("金額はすべて税別", 10.5, SILVER, False),
], align=PP_ALIGN.CENTER, gap=3)
textbox(s, Inches(5.17), Inches(7.16), Inches(3.0), Inches(0.28),
        [("© TSUBURAYA PRODUCTIONS", 8, SILVER, False)], align=PP_ALIGN.CENTER)
textbox(s, Inches(10.25), Inches(7.1), Inches(2.5), Inches(0.3),
        [("Strictly Confidential", 10, RED, True)], align=PP_ALIGN.RIGHT)

# 2. アジェンダ ------------------------------------------------------------
s = add_slide()
header(s, "本日のアジェンダ", "本格実施のご判断に向けて、以下の4点を確認・確定させていただきたく存じます")
add_table(s, Inches(0.7), Inches(1.6), Inches(11.9),
          ["", "内容", "目安"],
          [
              [("1. テストイベントの振り返り", True), "7会場の実施結果と、本格実施に向けた改善ポイントの共有", "10分"],
              [("2. 本格実施の役割分担", True), "当日運営の分担(当社2名派遣/貴社運営体制)と、申請・確認書のフローの確定", "20分"],
              [("3. ご提供条件", True), "ソフトバンク様特別プランの価格、最低開催数保証、ライン供給計画、実施条件", "20分"],
              [("4. 今後の進め方", True), "キャンペーン名称・ビジュアルの策定、契約手続き、スケジュール", "10分"],
          ],
          col_widths=[1.6, 3.4, 0.6], row_h=0.72, font_size=12.5)
b = rect(s, Inches(0.7), Inches(5.3), Inches(11.9), Inches(1.2), fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
b.adjustments[0] = 0.07
textbox(s, Inches(1.0), Inches(5.45), Inches(11.3), Inches(1.0), [
    ("本日のゴール", 13, RED, True),
    ("・本格実施のご意思確認　・役割分担の確定　・11月末までのご契約スケジュールの合意　・キャンペーン名称・ビジュアル策定打ち合わせの日程確定", 12, INK, False),
], gap=5)

# 3. テスト振り返り ---------------------------------------------------------
s = add_slide()
header(s, "1. テストイベントの振り返り", "2026年9〜10月・神奈川県内7会場(写真撮影会型5・ステージショー型2)の実施を踏まえて")
block(s, Inches(0.7), Inches(1.6), Inches(5.8), Inches(2.4), "良かった点", [
    "・全7会場を予定どおり実施、各会場で安定した集客を確認",
    "・貴社側での会場設営・音響・整理券・告知素材の対応は本格実施でも活用可能",
    "・写真撮影会型(1回30分)の運用は、来場者の満足度・回転とも良好",
])
block(s, Inches(6.8), Inches(1.6), Inches(5.8), Inches(2.4), "改善をお願いしたい点", [
    "・各会場スタッフ様へのキャンペーン内容の事前共有(当日の問い合わせ対応のため)",
    "・当日ご担当者様の集合時間の厳守(搬入・設営の遅れ防止)",
    "・キャラクターグッズの扱い(販促物を展示装飾に転用しない等、使用ルールの徹底)",
    "・告知名称・ビジュアルの統一(会場ごとの表記ゆれの解消)",
])
block(s, Inches(0.7), Inches(4.25), Inches(11.9), Inches(2.3), "本格実施に向けた整理", [
    "・撮影会は1回30分×1日3〜4回(各50組)を基本とし、貴社店頭の来店動態に合わせて2案から選択",
    "・上記の改善点は、貴社内の取りまとめ窓口からの全会場一括展開(全店共通フォーマット)で解消可能と考えています",
    "・当社から運営マニュアル・初回レクチャーを提供し、全国どの会場でも同じ品質で実施できる体制を整えます",
], size=11.5)

# 4. 役割分担 ----------------------------------------------------------------
s = add_slide()
header(s, "2. 本格実施の役割分担", "当社はキャラクター稼働パート(2名)、貴社は会場運営パート(運営ディレクター1名+運営スタッフ4名)をご担当いただきます")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["役割", "撮影会中", "撮影会の合間・開始前"],
          [
              [("当社:担当(チーフスタッフ)", True, NAVY), "キャラクター稼働の統括、着脱補助・スーツメンテナンス、ヒーロー前のお客様対応", "スーツメンテナンス、貴社ディレクターとの進行確認"],
              [("当社:スーツアクター", True, NAVY), "キャラクター出演・ポージング(1回30分×最大5回)", "メンテナンス休憩"],
              [("貴社:運営ディレクター", True), "全体管理、音響機材のセット・音出し、館管理者との対応、会場周辺のお客様誘導", "会場づくり、お客様対応"],
              [("貴社:スタッフ1", True), "待機列の先頭", "会場づくり、整理券配布"],
              [("貴社:スタッフ2", True), "出口での送り出し", "会場づくり、整理券配布"],
              [("貴社:スタッフ3", True), "撮影補助(荷物運搬など)", "会場づくり、事前の列づくり"],
              [("貴社:スタッフ4", True), "待機列の最後尾(参加者管理)", "会場づくり、事前の列づくり"],
          ],
          col_widths=[1.5, 2.6, 2.0], row_h=0.52, font_size=11)
textbox(s, Inches(0.7), Inches(5.85), Inches(11.9), Inches(1.1), [
    ("・費用を抑えた体制で品質を担保するための最低人数です。撮影会中と合間で持ち場が切り替わるため、運営スタッフは4名が必要となります", 11, INK, False),
    ("・運営スタッフはスタッフと分かる服装(スタッフTシャツ・ベスト等)の着用をお願いします　・初回開催時は当社がレクチャーを実施し、運営マニュアルをご提供します", 11, INK, False),
    ("・貴社での運営が難しい会場向けに、当社が運営一式を手配するフル運営オプション(+22万円/日)を会場単位でご用意します", 11, INK, False),
], gap=4)

# 5. お願いする体制 ----------------------------------------------------------
s = add_slide()
header(s, "2. 貴社にお願いしたい体制・分担", "全国展開を円滑に進めるため、以下の体制・分担をお願いいたします")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["区分", "お願いしたい内容", "テストでの実績"],
          [
              [("取りまとめ窓口", True), "貴社内に全国の実施を取りまとめるご担当窓口(1部署)を設置。各会場への展開・情報共有・当社との一本化した連絡", "新規"],
              [("開催申請", True), "専用フォームで申請→前月1日に可否確定→確認書の取り交わし(会場は1ヶ月前までに確定)", "新規"],
              [("運営計画・実施確認書", True), "会場ごとの運営計画・実施確認書を貴社にて作成(当社テンプレートをご提供)", "新規(テストは当社作成)"],
              [("制作物の仮申請", True), "イベントキット・ノベルティ等は品目ごとに仮申請(備品/配布用の区分を明記)。申請窓口はご担当1名に集約", "新規"],
              [("運営サイン・音響・設営", True), "会場内サイン、音響機材の手配とオペレーション、イベントキット設営・会場復帰", "✓ 対応済み"],
              [("整理券・告知素材・実施報告", True), "整理券・列形成備品、HP掲載用テキスト・画像(当社監修)、参加人数等の実施報告", "✓ 対応済み"],
              [("会場要件・その他", True), "施錠可能な非公開控室・関係車両用駐車場/JASRAC申請・イベント保険(主催者様にて)", "✓ 対応済み"],
          ],
          col_widths=[1.4, 3.6, 1.0], row_h=0.6, font_size=11)

# 6. ご提供価格 --------------------------------------------------------------
s = add_slide()
header(s, "3. ご提供価格(ソフトバンク様特別プラン)", "通常販売価格から大幅な特別価格でご提供します。本特別価格は年間契約+最低開催数保証のご締結を前提とした本件限りの条件です")
add_table(s, Inches(0.7), Inches(1.55), Inches(6.9),
          ["キャラクターイベント稼働費", "通常販売価格", "SB様特別価格"],
          [
              [("1日稼働(1日最大5回公演)", True), "225,000円/日", ("100,000円/日(▲55.6%)", True, RED)],
              [("土日2日間(1開催)", True), "450,000円", ("200,000円", True, RED)],
              [("3連休通し(3日間)", True), "675,000円", ("300,000円", True, RED)],
          ],
          col_widths=[2.0, 1.3, 1.6], row_h=0.6, font_size=11.5)
textbox(s, Inches(0.7), Inches(4.05), Inches(6.9), Inches(1.2), [
    ("特別価格の内訳(1日):キャラクター使用料 40,000円/担当 35,000円/スーツアクター 25,000円", 10.5, SUB, False),
    ("通常販売価格は同一スコープ(キャラクター使用料+担当+アクター・5回公演対応)での当社標準価格です", 10.5, SUB, False),
], gap=3)
add_table(s, Inches(7.9), Inches(1.55), Inches(4.7),
          ["その他の費目", "金額"],
          [
              [("年間IP使用料", True), "2,000万円/年"],
              [("作成許諾ロイヤリティ", True), "作成費用の20%"],
              [("フル運営オプション", True), "+220,000円/日"],
              [("現場諸経費", True), "20,000円/日"],
              [("実費", True), "交通運搬・宿泊・スーツ送料(基準料金表)"],
          ],
          col_widths=[1.5, 1.6], row_h=0.6, font_size=11)
b = rect(s, Inches(0.7), Inches(5.35), Inches(11.9), Inches(1.3), fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
b.adjustments[0] = 0.07
textbox(s, Inches(1.0), Inches(5.5), Inches(11.3), Inches(1.1), [
    ("年間IP使用料に含まれるもの", 12.5, RED, True),
    ("店頭イベント・イベントキット・店頭訴求ツール・LP/Web・SNSでのIP利用、作成物の監修対応、8ヒーローの選択・切替、キャラクター素材・運営マニュアルの提供", 11.5, INK, False),
], gap=4)

# 7. 実施条件 ----------------------------------------------------------------
s = add_slide()
header(s, "3. 実施の成立条件", "特別価格の前提となる条件です。契約協議にて詳細を調整させてください")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["#", "条件", "内容"],
          [
              ["1", ("契約期間・締結期限", True), "2027年1月〜2029年3月(2年3ヶ月)。2026年11月末までのご締結(1月開始に必要な体制準備のため)"],
              ["2", ("最低開催数保証", True), "基準15ライン分の開催数を最低保証。未実施の場合も当該数量分を申し受け、各年度末に精算"],
              ["3", ("開催確定とキャンセル", True), "会場・日程は開催1ヶ月前までに確定。確定後のキャンセル料:1ヶ月前〜14日前30%/13日前〜7日前50%/6日前〜当日100%"],
              ["4", ("ライン供給", True), "基準15ライン。余裕月(1・4・6・11・12月)は最大20ラインまで増枠可(次頁)"],
              ["5", ("お支払い", True), "貴社EDI発注。IP使用料は年度前払い、保証分は四半期前払い(ご相談)。最低保証契約のため期間一括の発注形態をご相談"],
              ["6", ("エリア・キャラクター", True), "北関東エリアは2027年1〜3月は実施不可(4月以降可)。ウルトラセブンは対象外。出演は8ヒーロー"],
              ["7", ("排他条件", True), "契約期間中、当社は国内の他の携帯キャリア(3社)との店頭イベント契約を行いません"],
          ],
          col_widths=[0.3, 1.5, 4.2], row_h=0.62, font_size=11)
textbox(s, Inches(0.7), Inches(6.5), Inches(11.9), Inches(0.5), [
    ("※ キャンセル料は7月ご提案時のスポット向け規定から、本契約(最低保証・1ヶ月前確定フロー)向けの規定に更新しています", 10.5, SUB, False),
])

# 8. ライン供給計画 ----------------------------------------------------------
s = add_slide()
header(s, "3. ライン供給計画(2027年1月〜2029年3月)", "基準15ラインを最低保証の対象とし、余裕のある月は最大20ラインまで増枠できます。詳細は別紙(月別供給計画)をご参照ください")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["", "1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
          [
              [("開催日数(土日)", True), "10", "8", "8", "8", "10", "8", "9", "9", "8", "10", "8", "8"],
              [("基準ライン数", True), "15", "15", "15", "15", "15", "15", "15", "15", "15", "15", "15", "15"],
              [("最大ライン数", True), ("20", True, RED), "15", "15", ("20", True, RED), "15", ("20", True, RED), "15", "15", "15", "15", ("20", True, RED), ("20", True, RED)],
          ],
          col_widths=[1.6] + [0.55] * 12, row_h=0.5, font_size=11)
textbox(s, Inches(0.7), Inches(3.75), Inches(11.9), Inches(0.4), [
    ("※ 2027年・2028年とも同パターン。2029年1〜3月は1月が最大20ライン、2〜3月は基準15ライン", 10.5, SUB, False),
])
add_table(s, Inches(0.7), Inches(4.3), Inches(11.9),
          ["27ヶ月合計", "開催日数", "開催数(ライン×日)", "稼働費(税別)"],
          [
              [("基準(15ライン固定)", True), "234日", "3,510現場", ("3億5,100万円", True)],
              [("最大(余裕月20ライン)", True), "234日", "3,980現場", ("3億9,800万円", True, RED)],
          ],
          col_widths=[2.0, 1.0, 1.5, 1.5], row_h=0.55, font_size=11.5)
textbox(s, Inches(0.7), Inches(6.1), Inches(11.9), Inches(0.8), [
    ("・2月・3月・8月・9月は当社主催行事との調整月のため基準15ラインでの運用となります　・増枠分は前月1日の開催確定時に確定します", 11, INK, False),
    ("・上記は稼働費のみ。年間IP使用料・現場諸経費・実費は別途", 11, INK, False),
], gap=4)

# 9. 制作・権利 --------------------------------------------------------------
s = add_slide()
header(s, "4. 制作物・権利まわりの進め方", "キャンペーンビジュアルの確定を起点に、仮申請フローで各制作物を確定していきます")
block(s, Inches(0.7), Inches(1.6), Inches(5.8), Inches(2.5), "① キャンペーン名称・キービジュアルの策定(11月中)", [
    "・名称とKVを両社で確定(ノベルティ可否判定の基準になります)",
    "・素材:複数ヒーローの集合ビジュアル、色調の揃った個体素材、ブランドロゴ",
    "・貴社デザイン部門向けに素材の使い方をレクチャー(監修回数の最小化)",
    "・中国工場の春節前量産(1月末まで)から逆算し、11月中の確定が必要",
])
block(s, Inches(6.8), Inches(1.6), Inches(5.8), Inches(2.5), "② 仮申請フロー", [
    "・イベントキット・ノベルティ等は品目ごとに仮申請(備品/配布用を明記)",
    "・仮申請をもって正式回答(約1週間)",
    "・申請窓口はご担当1名に集約(通知が1名にのみ届くため)",
    "・作成許諾ロイヤリティ:作成費用の20%(製造数量ベース)",
])
block(s, Inches(0.7), Inches(4.3), Inches(5.8), Inches(2.3), "③ ノベルティのカテゴリー", [
    "・制作可能:トートバッグ・タオル・BOXティッシュ等(キャンペーンデザイン使用)",
    "・制作不可:お子様向け玩具(フィギュア・ソフビ等)・菓子類・ランチボックス等",
    "・タオルは一般仕様(ループタオル・ミニタオルは避ける)",
])
block(s, Inches(6.8), Inches(4.3), Inches(5.8), Inches(2.3), "④ 修了証・配布物", [
    "・既存の修了証は当社既存イベント専用のため本件では使用しません",
    "・案A:貴社のミッション(クイズ等)と連動したオリジナル修了証を貴社制作",
    "・案B:キャンペーンビジュアルのステッカーを貴社制作・全員配布",
    "・配布の目的(体験型か告知型か)に応じて選択",
])

# 10. スケジュール ------------------------------------------------------------
s = add_slide()
header(s, "4. スケジュールと次のステップ", "2027年1月開始に向けた逆算スケジュールです")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["時期", "マイルストーン", "担当"],
          [
              [("10月22日(本日)", True), "本格実施のご判断/役割分担の確定", "両社"],
              [("10月下旬〜11月上旬", True), "キャンペーン名称・KV策定打ち合わせ/契約書ドラフトのご提示", "両社/当社"],
              [("11月中", True), "KV確定/ノベルティ品目の仮申請/取りまとめ窓口の設置", "貴社"],
              [("11月末", True), "契約締結", "両社"],
              [("12月", True), "デザイン監修完了・量産開始/1月開催分の会場確定(12月1日)/運営レクチャー", "両社"],
              [("2027年1月", True), "開始(基準15ライン・1月は最大20ライン)", "両社"],
          ],
          col_widths=[1.4, 3.8, 0.8], row_h=0.58, font_size=11.5)
b = rect(s, Inches(0.7), Inches(5.75), Inches(11.9), Inches(1.0), fill=PALE_RED, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
b.adjustments[0] = 0.08
textbox(s, Inches(1.0), Inches(5.88), Inches(11.3), Inches(0.8), [
    ("本日ご確認いただきたいこと", 12.5, RED, True),
    ("① 本格実施のご意思　② 役割分担(運営体制・取りまとめ窓口)　③ 11月末締結のスケジュール　④ KV策定打ち合わせの日程", 12, INK, False),
], gap=4)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SB様提示用_1022ミーティング資料.pptx")
prs.save(OUT)
print("saved:", OUT)
