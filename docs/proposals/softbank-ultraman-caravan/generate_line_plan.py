# -*- coding: utf-8 -*-
"""SB様提示用 月別ライン供給計画ドラフト(2027年1月〜2028年12月)"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

NAVY = "232278"
PALE = "F2F4F6"
RED = "C00000"
WHITE = "FFFFFF"
F = "Meiryo"

months = [f"2027年{m}月" for m in range(1, 13)] + [f"2028年{m}月" for m in range(1, 13)]
lines = [12, 12, 14, 17, 17, 18, 19, 17, 17, 19, 20, 20,
         20, 18, 20, 20, 20, 20, 20, 18, 19, 20, 20, 20]
days = [10, 8, 8, 8, 10, 8, 9, 9, 8, 10, 8, 8] * 2
notes = ["立ち上げ期(体制整備・会場選定)", "立ち上げ期/当社主催行事との調整月", "立ち上げ期",
         "フル稼働開始", "", "増強第1弾完了(+2ライン)", "", "当社主催行事との調整月",
         "当社主催行事との調整月", "", "増強第2弾完了=20ライン体制", "",
         "", "当社主催行事との調整月", "", "", "", "", "", "当社主催行事との調整月(想定)",
         "当社主催行事との調整月(想定)", "", "", ""]

wb = Workbook()
ws = wb.active
ws.title = "月別ライン供給計画"

thin = Side(style="thin", color="BBBBBB")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def put(r, c, v, bold=False, fill=None, color="1A1A1A", size=10.5, align="center", num_fmt=None):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font = Font(name=F, bold=bold, color=color, size=size)
    cell.alignment = Alignment(horizontal=align, vertical="center", wrap_text=True)
    cell.border = border
    if fill:
        cell.fill = PatternFill("solid", fgColor=fill)
    if num_fmt:
        cell.number_format = num_fmt
    return cell


put(1, 1, "ウルトラマンIP 店頭イベント 月別ライン供給計画(ドラフト)", bold=True, size=14, align="left")
ws.cell(row=1, column=1).border = Border()
put(2, 1, "円谷プロダクション作成/単価:50万円(税別)/ライン・日(土日開催・7名体制・MC込み)/交通運搬費・スーツ送料等の実費別途", size=9.5, align="left")
ws.cell(row=2, column=1).border = Border()

headers = ["年月", "同時稼働ライン数\n(週あたり)", "開催日数\n(土日)", "開催数\n(ライン×日)", "月額(税別)", "備考"]
for j, h in enumerate(headers, start=1):
    put(4, j, h, bold=True, fill=NAVY, color=WHITE, size=10.5)

r = 5
for i, m in enumerate(months):
    fill = PALE if i % 2 else None
    hi = "FBEAEB" if lines[i] >= 20 else fill
    put(r, 1, m, fill=fill)
    put(r, 2, lines[i], bold=lines[i] >= 20, fill=hi)
    put(r, 3, days[i], fill=fill)
    put(r, 4, lines[i] * days[i], fill=fill, num_fmt="#,##0")
    put(r, 5, lines[i] * days[i] * 500000, fill=fill, num_fmt="#,##0")
    put(r, 6, notes[i], fill=fill, align="left", size=9.5)
    r += 1

total_kai_27 = sum(lines[i] * days[i] for i in range(12))
total_kai_28 = sum(lines[i] * days[i] for i in range(12, 24))
put(r, 1, "2027年 小計", bold=True, fill=PALE)
put(r, 2, round(sum(lines[:12]) / 12, 1), bold=True, fill=PALE)
put(r, 3, sum(days[:12]), bold=True, fill=PALE)
put(r, 4, total_kai_27, bold=True, fill=PALE, num_fmt="#,##0")
put(r, 5, total_kai_27 * 500000, bold=True, fill=PALE, num_fmt="#,##0")
put(r, 6, f"平均{sum(lines[:12]) / 12:.1f}ライン/週", fill=PALE, align="left", size=9.5)
r += 1
put(r, 1, "2028年 小計", bold=True, fill=PALE)
put(r, 2, round(sum(lines[12:]) / 12, 1), bold=True, fill=PALE)
put(r, 3, sum(days[12:]), bold=True, fill=PALE)
put(r, 4, total_kai_28, bold=True, fill=PALE, num_fmt="#,##0")
put(r, 5, total_kai_28 * 500000, bold=True, fill=PALE, num_fmt="#,##0")
put(r, 6, f"平均{sum(lines[12:]) / 12:.1f}ライン/週", fill=PALE, align="left", size=9.5)
r += 1
put(r, 1, "2年間 合計", bold=True, fill=NAVY, color=WHITE)
put(r, 2, "", fill=NAVY)
put(r, 3, sum(days), bold=True, fill=NAVY, color=WHITE)
put(r, 4, total_kai_27 + total_kai_28, bold=True, fill=NAVY, color=WHITE, num_fmt="#,##0")
put(r, 5, (total_kai_27 + total_kai_28) * 500000, bold=True, fill=NAVY, color=WHITE, num_fmt="#,##0")
put(r, 6, "", fill=NAVY)
r += 2

conds = [
    "【前提条件】",
    "・ライン数は週あたりの同時稼働数。段階増強により2027年11月に20ライン体制が完成します。",
    "・繁忙月(当社主催行事との調整月)はライン数を抑え、閑散月の増枠で年間総量を確保する設計です。",
    "・年間最低開催数保証(計画開催数の8割)を前提とします。未達月も保証分を申し受けます。",
    "・開催会場は前月1日までに確定(専用フォーム申請→当社可否確認→確認書取り交わし)。",
    "・2028年の月別配分は当社主催行事の確定に応じて半期ごとに見直します(総量は維持)。",
    "・単価に含むもの:ヒーロー1体・7名体制(ディレクター/アクター/専任MC/キャラ補助2/運営スタッフ2)・音響機材・スタッフ昼食。",
    "・別途実費:交通運搬費・スーツ送料・宿泊費。JASRAC申請・費用は主催者様にてお願いします。",
    "・現地でのご準備:施錠可能な専用控室・関係車両用駐車場。",
    "・イベントキット・ノベルティは貴社にて事前作成・運用(当社は監修+作成許諾料20%)。",
]
for c in conds:
    cell = ws.cell(row=r, column=1, value=c)
    cell.font = Font(name=F, size=9.5, bold=(c.startswith("【")))
    cell.alignment = Alignment(horizontal="left", vertical="center")
    r += 1

ws.column_dimensions["A"].width = 14
ws.column_dimensions["B"].width = 16
ws.column_dimensions["C"].width = 10
ws.column_dimensions["D"].width = 12
ws.column_dimensions["E"].width = 16
ws.column_dimensions["F"].width = 40
ws.row_dimensions[4].height = 30
ws.freeze_panes = "A5"

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SB様提示用_月別ライン供給計画ドラフト.xlsx")
wb.save(OUT)
print("saved:", OUT)
print("2027:", total_kai_27, "回 /", total_kai_27 * 500000)
print("2028:", total_kai_28, "回 /", total_kai_28 * 500000)
print("total:", total_kai_27 + total_kai_28, "回 /", (total_kai_27 + total_kai_28) * 500000)
