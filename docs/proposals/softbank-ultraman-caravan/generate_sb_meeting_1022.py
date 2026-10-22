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
    ("本格実施に向けたお打ち合わせ資料", 26, INK, True),
], align=PP_ALIGN.CENTER, gap=10)
textbox(s, Inches(4.5), Inches(4.2), Inches(8.4), Inches(0.9), [
    ("テストイベントの振り返りと、本格実施の運営・条件のご確認", 13.5, INK, False),
], align=PP_ALIGN.CENTER, gap=4)
textbox(s, Inches(4.5), Inches(5.7), Inches(8.4), Inches(1.0), [
    ("2026年10月22日", 15, TSUB_NAVY, True),
    ("株式会社円谷プロダクション", 15, TSUB_NAVY, True),
    ("金額はすべて税別", 10.5, SILVER, False),
], align=PP_ALIGN.CENTER, gap=3)
textbox(s, Inches(5.17), Inches(7.16), Inches(3.0), Inches(0.28),
        [("© TSUBURAYA PRODUCTIONS", 8, SILVER, False)], align=PP_ALIGN.CENTER)
textbox(s, Inches(10.25), Inches(7.1), Inches(2.5), Inches(0.3),
        [("Strictly Confidential", 10, RED, True)], align=PP_ALIGN.RIGHT)

# 2. 本日の進め方 --------------------------------------------------------------
s = add_slide()
header(s, "本日の進め方")
add_table(s, Inches(0.7), Inches(1.4), Inches(11.9),
          ["", "内容", "目安"],
          [
              [("1. テストイベントの振り返り", True), "7会場の実施結果と、本格実施に向けて改善したい点", "10分"],
              [("2. 本格実施の役割分担", True), "当日運営の分担、連絡体制、申請と確認書の流れ", "20分"],
              [("3. ご提供条件", True), "価格、最低開催数保証、ライン供給計画、実施条件", "20分"],
              [("4. 今後の進め方", True), "キャンペーン名称・ビジュアルの策定、契約手続き、スケジュール", "10分"],
          ],
          col_widths=[1.6, 3.4, 0.6], row_h=0.72, font_size=12.5)
b = rect(s, Inches(0.7), Inches(5.1), Inches(11.9), Inches(1.3), fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
b.adjustments[0] = 0.07
textbox(s, Inches(1.0), Inches(5.25), Inches(11.3), Inches(1.1), [
    ("本日決めていただきたいこと", 13, RED, True),
    ("本格実施の可否／役割分担／11月末締結までの進め方／キャンペーン名称・ビジュアル策定打ち合わせの日程", 12, INK, False),
], gap=5)

# 3. テスト振り返り ---------------------------------------------------------
s = add_slide()
header(s, "1. テストイベントの振り返り", "2026年9〜10月、神奈川県内7会場(写真撮影会5・ステージショー2)")
block(s, Inches(0.7), Inches(1.6), Inches(5.8), Inches(2.4), "実績", [
    "・7会場14日間を予定どおり実施",
    "・ステージショーは1回150〜227名。ヤマダ横浜で単日227名、古淵は開店前から50名の行列、整理券200枚が完売",
    "・撮影会は1回の上限を30〜35組にすると安定。港南台は2日間とも滞りなく進行",
    "・ヨドバシ横浜はノベルティの受け取りを店舗内にしたところ、見積の取得が増加",
])
block(s, Inches(6.8), Inches(1.6), Inches(5.8), Inches(2.4), "改善したい点", [
    "・MCがいない会場で撮影ルールが伝わらず、場の盛り上がりが弱い",
    "・スタッフの服装がまちまちでお客様から見分けがつかない。集合時間・接客にもばらつき",
    "・撮影後の商談・アンケート案内が事前に伝わっておらず、不満の声",
    "・監修前のPOP、非公式グッズ、AI生成画像の使用",
    "・会場ごとの個別配送で物流が煩雑。EDIの検収時期と書類発行のずれ",
])
block(s, Inches(0.7), Inches(4.25), Inches(11.9), Inches(2.3), "本格実施での運用ルール(案)", [
    "・公演は1日4回(1回30分、各50組まで)。間に休憩とスーツメンテの時間を1時間半",
    "・MC役を全会場に置く(ルール案内と進行アナウンス)。スタッフTシャツ着用、集合時間厳守、接客マナーの事前共有",
    "・「商談・アンケートのご案内がある」ことを告知物と受付で明記",
    "・制作物は監修済みの規定デザインのみ。他キャラクターとの混在は不可(貴社キャラクター〔おとうさん犬など〕は可。同一盤面でのデザイン混在は応相談)",
    "・ノベルティは貴社製造となるため当社からの納品は原則なし。発生する場合は指定倉庫に一括納品、5営業日前に数量確定",
    "・全会場の情報をまとめた告知ページを開設し、当社公式サイトから誘導。EDIの検収と書類発行の時期を契約で整理",
], size=10.5)

# 4. 会場別実績 ---------------------------------------------------------------
s = add_slide()
header(s, "1. 会場別の実績", "2026年9月12日〜10月18日")
add_table(s, Inches(0.7), Inches(1.45), Inches(11.9),
          ["会場", "日程・形式", "出演", "動員", "備考"],
          [
              ["イトーヨーカドー古淵", "9/12-13 ショー", "テオ&オメガ／ゼット&ジード", "664名(各日2回)", "開店前50名の行列、整理券200枚完売。抽選会の流れに混乱"],
              ["イトーヨーカドー川崎", "9/19-20 撮影会", "ウルトラマン／オメガ", "216組(各日5回)", "監修前POPと非公式品の装飾使用。入り時間に店舗担当者が不在"],
              ["ビックカメラ ラゾーナ川崎", "9/19-20 撮影会", "ゼロ／ティガ", "225組(各日3回)", "整理券45〜50枚/回がほぼ完売。景品に他IP品が混在"],
              ["ヤマダデンキ横浜本店", "9/26-27 ショー", "テオ&オメガ／ゼット&ジード", "622名(27日は227名)", "当日朝にレイアウト変更"],
              ["イトーヨーカドー上永谷", "9/26-27 撮影会", "ゼロ／ティガ", "234組(各日5回)", "初回の上限を30組にして人の偏りを解消"],
              ["港南台バーズ", "10/17-18 撮影会", "ゼロ／ティガ", "313名(各日5回)", "上限35名/回。2日間とも滞りなく進行"],
              ["ヨドバシカメラ横浜", "10/17-18 撮影会", "ゼロ／ティガ", "344名(各日5回)", "MCなしでルールが伝わらず。特典受け取りを店舗内に変更し見積取得増"],
          ],
          col_widths=[1.6, 1.2, 1.6, 1.3, 3.1], row_h=0.6, font_size=10.5)
textbox(s, Inches(0.7), Inches(6.35), Inches(11.9), Inches(0.5), [
    ("会場に合わせた枠数(30〜35名/回)と事前の会場ブリーフィングで運営が安定する。MCの配置と商談・アンケート案内の事前告知は全店共通にしたい", 11, NAVY, True),
])

# 5. 役割分担 ----------------------------------------------------------------
s = add_slide()
header(s, "2. 本格実施の役割分担", "当社はキャラクター稼働(2名)、貴社は会場運営(運営ディレクター1名+運営スタッフ4名)")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["役割", "撮影会中", "合間・開始前"],
          [
              [("当社:担当(チーフスタッフ)", True, NAVY), "キャラクター稼働の統括。着脱補助、スーツメンテ、ヒーロー前のお客様対応", "スーツメンテ。貴社ディレクターと進行確認"],
              [("当社:スーツアクター", True, NAVY), "キャラクター出演(1回30分、1日最大5回)", "スーツの準備・休憩"],
              [("貴社:運営ディレクター", True), "全体管理。音響の設置と音出し、館管理者との対応、周辺のお客様誘導", "会場づくり、お客様対応"],
              [("貴社:スタッフ1", True), "待機列の先頭", "会場づくり、整理券配布"],
              [("貴社:スタッフ2", True), "出口の送り出し", "会場づくり、整理券配布"],
              [("貴社:スタッフ3", True), "撮影補助(荷物運搬など)", "会場づくり、列づくり"],
              [("貴社:スタッフ4", True), "待機列の最後尾(参加者管理)", "会場づくり、列づくり"],
          ],
          col_widths=[1.5, 2.6, 2.0], row_h=0.52, font_size=11)
textbox(s, Inches(0.7), Inches(5.85), Inches(11.9), Inches(1.1), [
    ("・運営スタッフ4名は、撮影会中と合間で持ち場が入れ替わるために必要な人数です", 11, INK, False),
    ("・スタッフと分かる服装(Tシャツ・ベスト等)でお願いします。初回はレクチャーを当社が行い、運営マニュアルをお渡しします", 11, INK, False),
    ("・MC役は運営スタッフの兼務、または当社のMCオプション(+3万円/日)。運営一式を当社で行うフル運営オプション(+22万円/日)も会場単位で選べます", 11, INK, False),
], gap=4)

# 6. 連絡体制 ------------------------------------------------------------------
s = add_slide()
header(s, "2. 連絡体制と回答日数", "貴社の取りまとめ窓口と当社の総合窓口を1対1でつなぎ、当社内で用件ごとに振り分けます")
rect(s, Inches(4.4), Inches(1.6), Inches(4.5), Inches(0.7), fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
textbox(s, Inches(4.4), Inches(1.6), Inches(4.5), Inches(0.7), [("貴社 取りまとめ窓口(1部署)", 13, WHITE, True)], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
textbox(s, Inches(4.4), Inches(2.35), Inches(4.5), Inches(0.35), [("連絡 ↓　↑ 回答", 12, SUB, True)], align=PP_ALIGN.CENTER)
rect(s, Inches(4.4), Inches(2.7), Inches(4.5), Inches(0.7), fill=TSUB_NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
textbox(s, Inches(4.4), Inches(2.7), Inches(4.5), Inches(0.7), [("当社 総合窓口(専用メーリングリスト)", 13, WHITE, True)], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_table(s, Inches(0.7), Inches(3.75), Inches(11.9),
          ["窓口", "用件", "回答日数"],
          [
              [("① イベント実施", True), "開催申請(エリア・会場・日程)のバッティング確認、実施確認書の確認", "5営業日。前月1日までに確定"],
              [("② 告知物", True), "KV・Web・チラシ等の監修", "KV 3営業日、Web流用 1〜2営業日、チラシ+色校 1〜2営業日"],
              [("③ 制作物", True), "仮申請(制作可否)、ノベルティ・キット等のデザイン監修", "仮申請 約15営業日、デザイン監修 5営業日"],
              [("④ 契約・精算", True), "発注、請求、最低保証の精算、実績報告", "随時"],
          ],
          col_widths=[1.3, 3.5, 2.2], row_h=0.55, font_size=11)
textbox(s, Inches(0.7), Inches(6.6), Inches(11.9), Inches(0.4), [
    ("当社側のメーリングリストは契約後にご案内します。開催当日の連絡は、当社現場担当と貴社運営ディレクターの間で直接行います", 10.5, SUB, False),
])

# 7. お願いする体制 ----------------------------------------------------------
s = add_slide()
header(s, "2. 貴社にお願いしたいこと")
add_table(s, Inches(0.7), Inches(1.4), Inches(11.9),
          ["区分", "内容", "テストでの対応"],
          [
              [("取りまとめ窓口", True), "全国の実施を取りまとめる部署を1つ決め、各会場への展開と当社との連絡を一本化", "新規"],
              [("開催申請", True), "専用フォームで申請、前月1日に可否確定、確認書を取り交わし。会場は1ヶ月前までに確定", "新規"],
              [("運営計画・実施確認書", True), "会場ごとに貴社で作成。様式は当社のものをお渡しします", "新規(テストは当社作成)"],
              [("制作物の仮申請", True), "イベントキット・ノベルティ等を品目ごとに申請。備品か配布用かを明記。申請窓口は担当者1名", "新規"],
              [("運営サイン・音響・設営", True), "会場内サイン、音響の手配と操作、イベントキットの設営と撤去", "新規(テストは当社対応)"],
              [("整理券・告知素材・実施報告", True), "整理券と列づくりの備品、HP掲載用の文章と画像(当社監修)、参加人数の報告", "対応済(一部新規)"],
              [("会場要件ほか", True), "施錠できる非公開の控室、関係車両の駐車場。JASRAC申請とイベント保険は主催者様で", "対応済"],
          ],
          col_widths=[1.4, 3.6, 1.0], row_h=0.6, font_size=11)

# 8. ご提供価格 --------------------------------------------------------------
s = add_slide()
header(s, "3. ご提供価格(ソフトバンク様特別価格)", "年間契約と最低開催数保証を前提とした、本件限りの価格です")
add_table(s, Inches(0.7), Inches(1.55), Inches(6.9),
          ["キャラクターイベント稼働費", "通常販売価格", "特別価格"],
          [
              [("1日(1日最大5回公演)", True), "225,000円", ("100,000円(▲55.6%)", True, RED)],
              [("土日2日間", True), "450,000円", ("200,000円", True, RED)],
              [("3連休", True), "675,000円", ("300,000円", True, RED)],
          ],
          col_widths=[2.0, 1.3, 1.6], row_h=0.6, font_size=11.5)
textbox(s, Inches(0.7), Inches(4.05), Inches(6.9), Inches(1.2), [
    ("特別価格の内訳(1日):キャラクター使用料 40,000円、担当 35,000円、スーツアクター 25,000円", 10.5, SUB, False),
    ("通常販売価格は同じ内容(キャラクター使用料+担当+アクター、5回公演対応)での当社標準価格", 10.5, SUB, False),
], gap=3)
add_table(s, Inches(7.9), Inches(1.55), Inches(4.7),
          ["その他", "金額"],
          [
              [("年間IP使用料", True), "2,000万円/年"],
              [("作成許諾ロイヤリティ", True), "作成費用の20%"],
              [("MCオプション", True), "+30,000円/日"],
              [("フル運営オプション", True), "+220,000円/日"],
              [("現場諸経費", True), "20,000円/日"],
              [("実費", True), "交通運搬・宿泊・スーツ送料(基準料金表)"],
          ],
          col_widths=[1.5, 1.6], row_h=0.55, font_size=11)
b = rect(s, Inches(0.7), Inches(5.35), Inches(11.9), Inches(1.3), fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
b.adjustments[0] = 0.07
textbox(s, Inches(1.0), Inches(5.5), Inches(11.3), Inches(1.1), [
    ("年間IP使用料に含まれるもの", 12.5, RED, True),
    ("店頭イベント・イベントキット・店頭訴求ツール・LP/Web・SNSでのIP利用、作成物の監修、8ヒーローの選択と切替、キャラクター素材と運営マニュアルの提供", 11.5, INK, False),
], gap=4)

# 9. 実施条件 ----------------------------------------------------------------
s = add_slide()
header(s, "3. 実施の条件", "特別価格の前提となる条件です。詳細は契約協議で調整します")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["#", "条件", "内容"],
          [
              ["1", ("契約期間・締結", True), "2027年1月〜2029年3月(2年3ヶ月)。2026年11月末までに締結(1月開始に必要な体制準備のため)"],
              ["2", ("最低開催数保証", True), "基準15ライン分の開催数を保証。未実施の場合も当該数量分を申し受け、各年度末に精算"],
              ["3", ("開催確定とキャンセル", True), "会場・日程は開催1ヶ月前までに確定。確定後のキャンセル料は1ヶ月前〜14日前30%、13日前〜7日前50%、6日前〜当日100%"],
              ["4", ("ライン供給", True), "基準15ライン。余裕のある月(1・4・6・11・12月)は最大20ラインまで(次頁)"],
              ["5", ("お支払い", True), "貴社EDIで発注。IP使用料は契約時に27ヶ月分(4,500万円)を一括前払い、保証分は四半期前払い(ご相談)。最低保証契約のため、期間一括の発注形態をご相談したい"],
              ["6", ("エリア・キャラクター", True), "関信越エリア(埼玉・茨城・群馬・栃木・山梨・長野・新潟)は2027年1〜3月は実施不可(4月以降は可)。ウルトラセブンは対象外。出演は8ヒーロー"],
              ["7", ("排他条件", True), "契約期間中、当社は国内の他の携帯キャリア(3社)と店頭イベントの契約を行わない"],
          ],
          col_widths=[0.3, 1.5, 4.2], row_h=0.62, font_size=11)
textbox(s, Inches(0.7), Inches(6.5), Inches(11.9), Inches(0.5), [
    ("キャンセル料は7月ご提案時のスポット向け規定から、本契約向けの規定に変更しています", 10.5, SUB, False),
])

# 10. ライン供給計画 ----------------------------------------------------------
s = add_slide()
header(s, "3. ライン供給計画(2027年1月〜2029年3月)", "基準15ラインを最低保証の対象とし、余裕のある月は最大20ラインまで。月別の詳細は別紙")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["", "1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
          [
              [("開催日数(土日)", True), "10", "8", "8", "8", "10", "8", "9", "9", "8", "10", "8", "8"],
              [("基準ライン数", True), "15", "15", "15", "15", "15", "15", "15", "15", "15", "15", "15", "15"],
              [("最大ライン数", True), ("20", True, RED), "15", "15", ("20", True, RED), "15", ("20", True, RED), "15", "15", "15", "15", ("20", True, RED), ("20", True, RED)],
          ],
          col_widths=[1.6] + [0.55] * 12, row_h=0.5, font_size=11)
textbox(s, Inches(0.7), Inches(3.75), Inches(11.9), Inches(0.4), [
    ("上表は2027年(104日)。2028年は106日、2029年1〜3月は25日。ライン数の考え方は同じ", 10.5, SUB, False),
])
add_table(s, Inches(0.7), Inches(4.3), Inches(11.9),
          ["27ヶ月合計", "開催日数", "開催数(ライン×日)", "稼働費"],
          [
              [("基準(15ライン)", True), "235日", "3,525現場", ("3億5,250万円", True)],
              [("最大(余裕月は20ライン)", True), "235日", "4,005現場", ("4億50万円", True, RED)],
          ],
          col_widths=[2.0, 1.0, 1.5, 1.5], row_h=0.55, font_size=11.5)
textbox(s, Inches(0.7), Inches(6.1), Inches(11.9), Inches(0.8), [
    ("・2月・3月・8月・9月は当社の主催行事と重なるため基準15ラインでの運用。増枠分は前月1日の開催確定時に確定", 11, INK, False),
    ("・上記は稼働費のみ。年間IP使用料、現場諸経費、実費は別途", 11, INK, False),
], gap=4)

# 10b. エリア別ライン配分 --------------------------------------------------------
s = add_slide()
header(s, "3. エリア別のライン配分", "基準15ラインのエリア配分と、余裕のある月の最大ライン数。月別の詳細は別紙")
add_table(s, Inches(0.7), Inches(1.5), Inches(11.9),
          ["エリア", "基準", "余裕月の最大", "27ヶ月の現場数(基準〜最大)", "展開の考え方", "主な出演候補"],
          [
              [("関東", True), "6", ("8", True, RED), "1,410〜1,602", "東京・神奈川・千葉を中心に通年固定", "初代ウルトラマン、ティガ、ゼロ、テオ、オメガ、ゼット、ジード"],
              [("関西", True), "2", ("3", True, RED), "470〜566", "大阪・兵庫・京都を中心に展開", "ゼロ、ゼット、テオ、ジード、オメガ"],
              [("東海", True), "2", ("3", True, RED), "470〜566", "愛知を中心に岐阜・三重・静岡", "アーク、テオ、オメガ、ゼット、ジード"],
              [("九州", True), "2", ("3", True, RED), "470〜566", "福岡を拠点に各県", "ゼロ、ゼット、テオ、オメガ、ジード、ティガ"],
              [("北海道", True), "1", "1", "235", "札幌近郊は日帰り、函館・釧路は宿泊", "アーク、テオ、オメガ"],
              [("東北・信越", True), "1", "1", "235", "仙台・新潟を拠点に交互に配分", "初代ウルトラマン、テオ、オメガ、ジード"],
              [("中国・四国・沖縄", True), "1", "1", "235", "広島を拠点に各県、沖縄は本島中心", "アーク、テオ、オメガ、ジード、ゼロ、ゼット"],
              [("合計", True), ("15", True), ("20", True, RED), ("3,525〜4,005", True), "", ""],
          ],
          col_widths=[1.3, 0.6, 0.9, 1.6, 2.6, 3.0], row_h=0.52, font_size=10.5)
textbox(s, Inches(0.7), Inches(6.3), Inches(11.9), Inches(0.7), [
    ("・エリア配分は目安。会場リストをいただいた段階で、バッティング基準(半径8km・前後8日/5日)に照らして調整", 10.5, INK, False),
    ("・出演キャラクターは月別シフト表でご案内。関信越エリアは2027年1〜3月は実施不可(4月以降は可)", 10.5, INK, False),
], gap=3)

# 11. 制作・権利 --------------------------------------------------------------
s = add_slide()
header(s, "4. 制作物と権利の進め方", "キャンペーンビジュアルを決めてから、品目ごとに仮申請で制作物を確定していきます")
block(s, Inches(0.7), Inches(1.6), Inches(5.8), Inches(2.5), "キャンペーン名称・KVの策定(11月中)", [
    "・KVは貴社で制作(当社で受託することも可能)",
    "・撮影会の背景バナーは、キャラクターなしの背景素材(青空・宇宙)を当社から提供",
    "・会場装飾には集合ビジュアル(調整版)、告知素材にはヒーローの個体素材を当社から提供。ブランドロゴも提供",
    "・監修は当社の制作物窓口へ。春節前の量産(1月末)から逆算し、11月中に確定",
])
block(s, Inches(6.8), Inches(1.6), Inches(5.8), Inches(2.5), "仮申請の流れ(別紙「仮申請のご案内」)", [
    "・貴社担当者1名を事前登録し、品目ごとに申請。約15営業日で可否を回答",
    "・入力項目は企画商品名(「ノベルティ ○○」の表記)、キャラクター、商品カテゴリー、製造原価単価、予定数量、材質・サイズなど",
    "・配布物は商品カテゴリー1〜16、会場装飾は店舗備品として申請",
    "・作成許諾ロイヤリティは作成費用の20%(製造原価単価×数量)",
])
block(s, Inches(0.7), Inches(4.3), Inches(5.8), Inches(2.3), "ノベルティのカテゴリー", [
    "・制作できるもの:トートバッグ、タオル、BOXティッシュなど(キャンペーンデザイン使用)",
    "・制作できないもの:お子様向け玩具(フィギュア・ソフビ等)、菓子類、ランチボックスなど",
    "・タオルは一般的な仕様で(ループタオル・ミニタオルは避ける)",
])
block(s, Inches(6.8), Inches(4.3), Inches(5.8), Inches(2.3), "修了証・配布物", [
    "・既存の修了証は当社の別イベント用のため、本件では使わない",
    "・案A:貴社のミッション(クイズ等)と連動したオリジナル修了証を貴社で制作",
    "・案B:キャンペーンビジュアルのステッカーを貴社で制作し、来場者全員に配布",
    "・体験型か告知型か、配布の目的に合わせて選択",
])

# 11b. 素材提供の進め方 ---------------------------------------------------------
s = add_slide()
header(s, "4. 素材提供の進め方", "キャンペーンビジュアルの方向性を決めてから、使用する素材を選定してお渡しします")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["手順", "内容", "時期"],
          [
              [("1. 事前ヒアリング", True), "用途(KV・会場装飾・ノベルティ・告知物)、媒体サイズ、トーン、使いたいヒーロー、必要点数を簡単なシートでお伺い", "打ち合わせ前"],
              [("2. 候補の絞り込み", True), "ヒアリング内容をもとに当社で候補を選定", "打ち合わせ前"],
              [("3. 方向性の決定", True), "キャンペーン名称・KVの策定打ち合わせで、候補を見ながら使用素材を決定", "11月上旬"],
              [("4. 素材のお渡し", True), "決定した素材のみをGoogleドライブで共有(データ量が大きい場合はHDDでのお渡し)", "決定後"],
              [("5. 制作・監修", True), "貴社でデザイン制作、当社監修(5営業日)、仮申請・製造へ", "11月中〜12月"],
          ],
          col_widths=[1.5, 4.2, 1.1], row_h=0.6, font_size=11.5)
b = rect(s, Inches(0.7), Inches(5.3), Inches(11.9), Inches(1.4), fill=PALE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
b.adjustments[0] = 0.06
textbox(s, Inches(1.0), Inches(5.45), Inches(11.3), Inches(1.2), [
    ("ご提供の考え方", 12.5, RED, True),
    ("・テストではイベント告知用の素材のみお渡ししました。本契約向けのKV・ノベルティ用素材はこれからのご提供です", 11.5, INK, False),
    ("・素材は使用する分のみお渡しします(用途ごとに選定することで、監修の手戻りを減らします)", 11.5, INK, False),
    ("・撮影会の背景バナーはキャラクターなしの背景素材、会場装飾・告知物は集合ビジュアル・個体素材・ロゴ。クレジットは「©円谷プロ」左下", 11.5, INK, False),
], gap=4)

# 12. スケジュール ------------------------------------------------------------
s = add_slide()
header(s, "4. スケジュール", "2027年1月開始からの逆算")
add_table(s, Inches(0.7), Inches(1.55), Inches(11.9),
          ["時期", "内容", "担当"],
          [
              [("10月22日(本日)", True), "本格実施の可否、役割分担の確定", "両社"],
              [("10月下旬〜11月上旬", True), "キャンペーン名称・KVの策定打ち合わせ。契約書ドラフトの提示。ノベルティ品目の仮申請(回答に約15営業日)", "両社"],
              [("11月中", True), "KV確定、取りまとめ窓口の設置", "貴社"],
              [("11月末", True), "契約締結", "両社"],
              [("12月", True), "デザイン監修完了、量産開始(春節前)。1月開催分の会場確定(12月1日)。運営レクチャー", "両社"],
              [("2027年1月", True), "開始(基準15ライン。1月は最大20ライン)", "両社"],
          ],
          col_widths=[1.4, 3.8, 0.8], row_h=0.58, font_size=11.5)
b = rect(s, Inches(0.7), Inches(5.75), Inches(11.9), Inches(1.0), fill=PALE_RED, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
b.adjustments[0] = 0.08
textbox(s, Inches(1.0), Inches(5.88), Inches(11.3), Inches(0.8), [
    ("本日ご確認いただきたいこと", 12.5, RED, True),
    ("本格実施の可否／役割分担(運営体制・取りまとめ窓口)／11月末締結までの進め方／KV策定打ち合わせの日程", 12, INK, False),
], gap=4)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SB様提示用_1022ミーティング資料.pptx")
prs.save(OUT)
print("saved:", OUT)
