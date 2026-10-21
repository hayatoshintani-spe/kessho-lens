# -*- coding: utf-8 -*-
"""SB様提示用 エリア別ライン供給計画(2027年1月〜2029年3月)"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

NAVY = "232278"
PALE = "F2F4F6"
HI = "FBEAEB"
WHITE = "FFFFFF"
F = "Meiryo"

months = [f"2027年{m}月" for m in range(1, 13)] + [f"2028年{m}月" for m in range(1, 13)] + [f"2029年{m}月" for m in range(1, 4)]
days = [10, 8, 8, 8, 10, 8, 9, 9, 8, 10, 8, 8] + [10, 8, 8, 10, 8, 8, 10, 8, 9, 9, 8, 10] + [8, 8, 9]
BUFFER = {1, 4, 6, 11, 12}

# エリア別ライン配分(基準15/余裕月20)
AREAS = [
    ("関東", 6, 8, "東京・神奈川・千葉を中心に通年固定ライン", "初代ウルトラマン、ティガ、ゼロ、テオ、オメガ、ゼット、ジード"),
    ("関西", 2, 3, "大阪・兵庫・京都を中心に展開", "ゼロ、ゼット、テオ、ジード、オメガ"),
    ("東海", 2, 3, "愛知を中心に岐阜・三重・静岡", "アーク、テオ、オメガ、ゼット、ジード"),
    ("九州", 2, 3, "福岡を拠点に各県", "ゼロ、ゼット、テオ、オメガ、ジード、ティガ"),
    ("北海道", 1, 1, "札幌近郊は日帰り、函館・釧路は宿泊", "アーク、テオ、オメガ"),
    ("東北・信越", 1, 1, "仙台・新潟を拠点に交互に配分", "初代ウルトラマン、テオ、オメガ、ジード"),
    ("中国・四国・沖縄", 1, 1, "広島を拠点に各県、沖縄は本島中心", "アーク、テオ、オメガ、ジード、ゼロ、ゼット"),
]
assert sum(a[1] for a in AREAS) == 15 and sum(a[2] for a in AREAS) == 20

wb = Workbook()
thin = Side(style="thin", color="BBBBBB")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def put(ws, r, c, v, bold=False, fill=None, color="1A1A1A", size=10.5, align="center", num_fmt=None):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font = Font(name=F, bold=bold, color=color, size=size)
    cell.alignment = Alignment(horizontal=align, vertical="center", wrap_text=True)
    cell.border = border
    if fill:
        cell.fill = PatternFill("solid", fgColor=fill)
    if num_fmt:
        cell.number_format = num_fmt
    return cell


# ---- シート1:エリア×月 ライン数 ----
ws = wb.active
ws.title = "エリア別月別ライン数"
put(ws, 1, 1, "エリア別 月別ライン供給計画(2027年1月〜2029年3月)", bold=True, size=14, align="left")
ws.cell(row=1, column=1).border = Border()
put(ws, 2, 1, "円谷プロダクション作成/基準15ライン・余裕月(1・4・6・11・12月)は最大20ライン/単位:同時稼働ライン数", size=9.5, align="left")
ws.cell(row=2, column=1).border = Border()
put(ws, 4, 1, "エリア", bold=True, fill=NAVY, color=WHITE)
for j, m in enumerate(months, start=2):
    put(ws, 4, j, m.replace("年", "/").replace("月", ""), bold=True, fill=NAVY, color=WHITE, size=9.5)
put(ws, 4, len(months) + 2, "27ヶ月 現場数(基準)", bold=True, fill=NAVY, color=WHITE, size=9.5)
put(ws, 4, len(months) + 3, "27ヶ月 現場数(最大)", bold=True, fill=NAVY, color=WHITE, size=9.5)
put(ws, 5, 1, "開催日数(土日)", bold=True, fill=PALE)
for j, d in enumerate(days, start=2):
    put(ws, 5, j, d, fill=PALE)
put(ws, 5, len(months) + 2, sum(days), fill=PALE, bold=True)
put(ws, 5, len(months) + 3, sum(days), fill=PALE, bold=True)
r = 6
area_tot = []
for name, base, mx, _, _ in AREAS:
    put(ws, r, 1, name, bold=True, align="left")
    tb = tm = 0
    for j, m in enumerate(months, start=2):
        mm = int(m.split("年")[1].rstrip("月"))
        v = mx if mm in BUFFER else base
        put(ws, r, j, v, fill=HI if (v > base) else None, bold=(v > base))
        tb += base * days[j - 2]
        tm += v * days[j - 2]
    put(ws, r, len(months) + 2, tb, num_fmt="#,##0")
    put(ws, r, len(months) + 3, tm, num_fmt="#,##0")
    area_tot.append((name, tb, tm))
    r += 1
put(ws, r, 1, "合計", bold=True, fill=NAVY, color=WHITE, align="left")
for j, m in enumerate(months, start=2):
    mm = int(m.split("年")[1].rstrip("月"))
    put(ws, r, j, 20 if mm in BUFFER else 15, bold=True, fill=NAVY, color=WHITE)
put(ws, r, len(months) + 2, sum(t[1] for t in area_tot), bold=True, fill=NAVY, color=WHITE, num_fmt="#,##0")
put(ws, r, len(months) + 3, sum(t[2] for t in area_tot), bold=True, fill=NAVY, color=WHITE, num_fmt="#,##0")
ws.column_dimensions["A"].width = 18
for j in range(2, len(months) + 2):
    ws.column_dimensions[ws.cell(row=4, column=j).column_letter].width = 6.5
ws.column_dimensions[ws.cell(row=4, column=len(months) + 2).column_letter].width = 13
ws.column_dimensions[ws.cell(row=4, column=len(months) + 3).column_letter].width = 13
ws.freeze_panes = "B6"

# ---- シート2:エリア別サマリー ----
ws2 = wb.create_sheet("エリア別サマリー")
put(ws2, 1, 1, "エリア別 供給ラインのサマリー(27ヶ月)", bold=True, size=14, align="left")
ws2.cell(row=1, column=1).border = Border()
hdr = ["エリア", "基準ライン数", "余裕月の最大", "現場数(基準)", "稼働費(基準・税別)", "現場数(最大)", "稼働費(最大・税別)", "展開の考え方", "主な出演候補キャラクター"]
for j, h in enumerate(hdr, start=1):
    put(ws2, 3, j, h, bold=True, fill=NAVY, color=WHITE)
r = 4
for (name, base, mx, note, chars), (_, tb, tm) in zip(AREAS, area_tot):
    fill = PALE if r % 2 else None
    put(ws2, r, 1, name, bold=True, fill=fill, align="left")
    put(ws2, r, 2, base, fill=fill)
    put(ws2, r, 3, mx, fill=fill)
    put(ws2, r, 4, tb, fill=fill, num_fmt="#,##0")
    put(ws2, r, 5, tb * 100000, fill=fill, num_fmt="#,##0")
    put(ws2, r, 6, tm, fill=fill, num_fmt="#,##0")
    put(ws2, r, 7, tm * 100000, fill=fill, num_fmt="#,##0")
    put(ws2, r, 8, note, fill=fill, align="left", size=9.5)
    put(ws2, r, 9, chars, fill=fill, align="left", size=9.5)
    r += 1
TB = sum(t[1] for t in area_tot); TM = sum(t[2] for t in area_tot)
put(ws2, r, 1, "合計", bold=True, fill=NAVY, color=WHITE, align="left")
put(ws2, r, 2, 15, bold=True, fill=NAVY, color=WHITE)
put(ws2, r, 3, 20, bold=True, fill=NAVY, color=WHITE)
put(ws2, r, 4, TB, bold=True, fill=NAVY, color=WHITE, num_fmt="#,##0")
put(ws2, r, 5, TB * 100000, bold=True, fill=NAVY, color=WHITE, num_fmt="#,##0")
put(ws2, r, 6, TM, bold=True, fill=NAVY, color=WHITE, num_fmt="#,##0")
put(ws2, r, 7, TM * 100000, bold=True, fill=NAVY, color=WHITE, num_fmt="#,##0")
put(ws2, r, 8, "", fill=NAVY); put(ws2, r, 9, "", fill=NAVY)
r += 2
notes = [
    "【前提】",
    "・ライン数は同時稼働数。1ライン=1会場で土日2日間の実施(1日最大5回公演)。",
    "・エリア配分は目安です。会場リストをいただいた段階で、バッティング基準(半径8km・前後8日/5日)に照らして調整します。",
    "・出演キャラクターは月別のシフト表でご案内します(権利調整により一部変わる場合があります)。ウルトラセブンは対象外。",
    "・関信越エリア(埼玉・茨城・群馬・栃木・山梨・長野・新潟)は2027年1〜3月は実施できません(4月以降は可)。",
    "・交通運搬費・宿泊費は全国基準料金表によりエリアごとに算定(地方エリアは宿泊を伴う場合があります)。",
]
for n in notes:
    c = ws2.cell(row=r, column=1, value=n)
    c.font = Font(name=F, size=9.5, bold=n.startswith("【"))
    c.alignment = Alignment(horizontal="left", vertical="center")
    r += 1
for col, w in zip("ABCDEFGHI", [18, 11, 11, 12, 16, 12, 16, 34, 40]):
    ws2.column_dimensions[col].width = w
ws2.row_dimensions[3].height = 30

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SB様提示用_エリア別ライン供給計画.xlsx")
wb.save(OUT)
print("saved:", OUT)
for t in area_tot:
    print(t)
print("total", TB, TM)
