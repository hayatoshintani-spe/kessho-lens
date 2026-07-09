#!/usr/bin/env python3
"""12-asset-requirements.md の全素材をプレースホルダーカンプとして生成する.

実写・実商品素材が届くまでの位置・サイズ・トーン確認用。ブランドカラー
(濃紺×ウルトラマンレッド)のフラットイラスト調で統一。各画像は
デッキ上の配置枠と同じアスペクト比・要件定義のピクセルクラスで出力する。

    python3 generate_assets.py   # → assets/ に出力
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter

random.seed(60)  # 再現性(60周年)

OUT = "assets"
for sub in ("photo", "mock", "kv", "qr"):
    os.makedirs(f"{OUT}/{sub}", exist_ok=True)

# ---- palette ----
NAVY   = (0, 7, 20)
NAVY2  = (10, 20, 43)
NAVY3  = (17, 31, 62)
LINE   = (37, 54, 94)
WHITE  = (244, 247, 253)
SUB    = (169, 182, 210)
DIM    = (106, 119, 148)
RED    = (232, 56, 47)
REDDK  = (168, 28, 24)
CYAN   = (127, 200, 232)
GOLD   = (244, 192, 78)
SILVER = (200, 210, 228)
INKSIL = (5, 10, 24)     # シルエット色


def canvas(w, h, top=NAVY, bottom=NAVY2):
    """縦グラデーションの下地."""
    img = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    return img


def glow(img, cx, cy, r, color, strength=110):
    """柔らかい光."""
    layer = Image.new("RGB", img.size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              fill=tuple(int(c * strength / 255) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.55))
    return Image.blend(img, Image.composite(layer, Image.new("RGB", img.size, (0,0,0)),
                       Image.new("L", img.size, 255)), 0) if False else \
           Image.blend(img, add(img, layer), 1.0)


def add(a, b):
    """加算合成."""
    import numpy  # Pillowのみで済ますため簡易実装に切替
    raise RuntimeError


def add_glow(img, cx, cy, r, color, alpha=90):
    """加算風の光(合成で近似)."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    steps = 6
    for i in range(steps, 0, -1):
        rr = int(r * i / steps)
        a = int(alpha * (1 - i / (steps + 1)))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def person(d, x, y, h, color=INKSIL, arms="down"):
    """人物シルエット(x=中心, y=足元, h=身長)."""
    hw = h * 0.16
    head_r = h * 0.11
    d.ellipse([x - head_r, y - h, x + head_r, y - h + head_r * 2], fill=color)
    d.rounded_rectangle([x - hw, y - h + head_r * 2.1, x + hw, y - h * 0.28],
                        radius=hw * 0.7, fill=color)
    d.rectangle([x - hw * 0.85, y - h * 0.32, x - hw * 0.15, y], fill=color)
    d.rectangle([x + hw * 0.15, y - h * 0.32, x + hw * 0.85, y], fill=color)
    aw = hw * 0.5
    if arms == "up":
        d.rectangle([x - hw - aw, y - h * 0.95, x - hw, y - h * 0.55], fill=color)
        d.rectangle([x + hw, y - h * 0.95, x + hw + aw, y - h * 0.55], fill=color)
    elif arms == "raise":  # 片手上げ
        d.rectangle([x + hw, y - h * 1.0, x + hw + aw, y - h * 0.6], fill=color)
        d.rectangle([x - hw - aw, y - h * 0.72, x - hw, y - h * 0.4], fill=color)
    else:
        d.rectangle([x - hw - aw, y - h * 0.72, x - hw, y - h * 0.35], fill=color)
        d.rectangle([x + hw, y - h * 0.72, x + hw + aw, y - h * 0.35], fill=color)


def hero(d, x, y, h, body=SILVER, accent=RED, arms="raise"):
    """ヒーロー風シルエット(体シルバー・胸に赤いタイマー・頭部クレスト)."""
    person(d, x, y, h, color=body, arms=arms)
    head_r = h * 0.11
    d.polygon([(x - head_r * 0.18, y - h - head_r * 0.55),
               (x + head_r * 0.18, y - h - head_r * 0.55),
               (x, y - h + head_r * 0.4)], fill=body)
    tr = h * 0.05
    cy = y - h * 0.62
    d.ellipse([x - tr, cy - tr, x + tr, cy + tr], fill=accent)


def crowd(d, w, y, n, hmin, hmax, color=INKSIL, arms_up_ratio=0.4):
    xs = sorted(random.uniform(0.02, 0.98) for _ in range(n))
    for fx in xs:
        hh = random.uniform(hmin, hmax)
        arms = "up" if random.random() < arms_up_ratio else "down"
        person(d, fx * w, y + random.uniform(-hh*0.05, hh*0.05), hh, color, arms)


def label(img, text, sub=""):
    """左下の内容ラベル(カンプ識別用・小さく)."""
    d = ImageDraw.Draw(img)
    w, h = img.size
    pad = int(h * 0.028)
    bh = int(h * 0.075)
    d.rectangle([0, h - bh - pad * 2, int(w * 0.55), h], fill=(0, 0, 0))
    d.rectangle([0, h - bh - pad * 2, int(h * 0.012), h], fill=RED)
    fs = max(int(bh * 0.52), 14)
    try:
        from PIL import ImageFont
        JP = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
        font = ImageFont.truetype(JP, fs)
        font2 = ImageFont.truetype(JP, int(fs * 0.72))
    except Exception:
        font = font2 = None
    d.text((pad * 2, h - bh - pad), text, fill=WHITE, font=font)
    if sub:
        d.text((pad * 2 + (font.getlength(text) if font else len(text) * fs * 0.6) + pad * 2,
                h - bh - pad + fs * 0.18), sub, fill=DIM, font=font2)
    return img


def save(img, path, text, sub="IMAGE COMP"):
    label(img, text, sub)
    img.save(path, quality=90)
    print("saved", path, img.size)


def box3d(d, x, y, w, h, face=RED, side=REDDK, top_c=(255, 120, 110)):
    """商品箱."""
    dep = w * 0.22
    d.polygon([(x, y), (x + dep, y - dep * 0.6), (x + w + dep, y - dep * 0.6),
               (x + w, y)], fill=top_c)
    d.rectangle([x, y, x + w, y + h], fill=face)
    d.polygon([(x + w, y), (x + w + dep, y - dep * 0.6),
               (x + w + dep, y + h - dep * 0.6), (x + w, y + h)], fill=side)
    tr = w * 0.13
    d.ellipse([x + w/2 - tr, y + h*0.3 - tr, x + w/2 + tr, y + h*0.3 + tr], fill=WHITE)


def bottle(d, x, y, w, h, body=CYAN):
    d.rounded_rectangle([x, y + h*0.22, x + w, y + h], radius=w*0.25, fill=body)
    d.rectangle([x + w*0.3, y, x + w*0.7, y + h*0.25], fill=body)
    d.rectangle([x + w*0.28, y, x + w*0.72, y + h*0.08], fill=SILVER)
    d.rectangle([x + w*0.08, y + h*0.45, x + w*0.92, y + h*0.75], fill=WHITE)
    tr = w * 0.14
    d.ellipse([x + w/2 - tr, y + h*0.6 - tr, x + w/2 + tr, y + h*0.6 + tr], fill=RED)


def shelf(d, x, y, w, h, rows=3, header=None, hdr_color=RED):
    """棚(ヘッダーボード+段+商品)."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY3, outline=LINE, width=3)
    if header:
        d.rectangle([x, y - h*0.18, x + w, y], fill=hdr_color)
    rh = h / rows
    for r in range(rows):
        ry = y + rh * (r + 1) - rh * 0.08
        d.rectangle([x, ry - rh*0.06, x + w, ry], fill=LINE)
        n = random.randint(5, 7)
        bw = w / (n + 2)
        for i in range(n):
            bx = x + bw * (i + 0.7) + random.uniform(-2, 2)
            bh = rh * random.uniform(0.5, 0.72)
            c = random.choice([RED, CYAN, SILVER, GOLD])
            d.rectangle([bx, ry - rh*0.06 - bh, bx + bw*0.8, ry - rh*0.06], fill=c)


def phone(d, x, y, w, h, screen=NAVY2):
    d.rounded_rectangle([x, y, x + w, y + h], radius=w*0.12, fill=(8, 12, 24),
                        outline=SILVER, width=4)
    d.rounded_rectangle([x + w*0.05, y + h*0.03, x + w*0.95, y + h*0.97],
                        radius=w*0.08, fill=screen)


def browser(d, x, y, w, h, page=NAVY2):
    d.rounded_rectangle([x, y, x + w, y + h], radius=w*0.02, fill=(8, 12, 24),
                        outline=LINE, width=3)
    d.rectangle([x, y, x + w, y + h*0.1], fill=NAVY3)
    for i in range(3):
        r = h * 0.022
        d.ellipse([x + w*0.02 + i * r * 3, y + h*0.05 - r,
                   x + w*0.02 + i * r * 3 + r*2, y + h*0.05 + r],
                  fill=[RED, GOLD, CYAN][i])
    d.rectangle([x + w*0.02, y + h*0.12, x + w*0.98, y + h*0.98], fill=page)


def tshirt(d, x, y, w, color, mark=RED):
    """Tシャツ(x,y=左上, w=幅)."""
    h = w * 1.05
    d.polygon([(x + w*0.32, y), (x + w*0.68, y), (x + w, y + w*0.22),
               (x + w*0.86, y + w*0.38), (x + w*0.78, y + w*0.3),
               (x + w*0.78, y + h), (x + w*0.22, y + h),
               (x + w*0.22, y + w*0.3), (x + w*0.14, y + w*0.38),
               (x, y + w*0.22)], fill=color)
    d.ellipse([x + w*0.44, y - w*0.03, x + w*0.56, y + w*0.07], fill=NAVY)
    tr = w * 0.1
    d.ellipse([x + w/2 - tr, y + h*0.42 - tr, x + w/2 + tr, y + h*0.42 + tr], fill=mark)
    d.rectangle([x + w*0.36, y + h*0.62, x + w*0.64, y + h*0.66], fill=mark)


def spotlights(img, w, h, n=3):
    o = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(o)
    for i in range(n):
        cx = w * (0.2 + 0.3 * i)
        d.polygon([(cx, 0), (cx - w*0.09 + w*0.14, h*0.85), (cx + w*0.2, h*0.85)],
                  fill=(140, 190, 240, 26))
    return Image.alpha_composite(img.convert("RGBA"), o).convert("RGB")


# =====================================================================
def photo(path, w, h, scene, text):
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    scene(img, d, w, h)
    # scene関数がimgを返す場合の再取得は各sceneで処理済み
    save(Image.open(path) if False else img, path, text, "PHOTO COMP")


# --- scene builders(共通シーン) ---
def scene_stage_crowd(w, h, hero_pose="raise", crowd_n=26):
    img = canvas(w, h, NAVY, NAVY3)
    img = add_glow(img, w*0.5, h*0.32, int(h*0.5), (60, 120, 200), 70)
    img = spotlights(img, w, h)
    d = ImageDraw.Draw(img)
    d.rectangle([0, h*0.72, w, h*0.78], fill=NAVY3)          # ステージ
    hero(d, w*0.5, h*0.72, h*0.42, arms=hero_pose)
    img2 = add_glow(img, w*0.5, h*0.5, int(h*0.09), RED, 120)
    d = ImageDraw.Draw(img2)
    crowd(d, w, h*1.02, crowd_n, h*0.22, h*0.3, arms_up_ratio=0.55)
    return img2


def scene_queue(w, h):
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    d.rectangle([w*0.05, h*0.25, w*0.4, h*0.75], fill=NAVY3, outline=LINE, width=3)
    d.rectangle([w*0.05, h*0.25, w*0.4, h*0.33], fill=RED)   # 物販ブース
    shelf(d, w*0.08, h*0.4, w*0.28, h*0.3, rows=2)
    for i in range(9):
        person(d, w*(0.48 + i*0.055), h*0.88, h*0.32 * random.uniform(0.9, 1.05))
    return img


def scene_family_lookup(w, h):
    img = canvas(w, h)
    img = add_glow(img, w*0.72, h*0.3, int(h*0.42), (70, 130, 210), 80)
    d = ImageDraw.Draw(img)
    hero(d, w*0.72, h*0.62, h*0.5, arms="up")
    img = add_glow(img, w*0.72, h*0.31, int(h*0.06), RED, 130)
    d = ImageDraw.Draw(img)
    person(d, w*0.22, h*0.98, h*0.42)
    person(d, w*0.34, h*0.98, h*0.26, arms="up")   # 子ども
    return img


# =====================================================================
# ここから各素材の生成
# =====================================================================

# ---- s01 タイトル背景 BG 3840x2160 ----
w, h = 3840, 2160
img = canvas(w, h, (0, 4, 14), NAVY2)
img = add_glow(img, w*0.78, h*0.35, 700, (50, 110, 190), 60)
d = ImageDraw.Draw(img)
for i in range(40):                                   # 星
    x, y = random.uniform(0, w), random.uniform(0, h*0.5)
    r = random.uniform(1.5, 4)
    d.ellipse([x-r, y-r, x+r, y+r], fill=(200, 215, 240))
bx = 0                                                # スカイライン
while bx < w:
    bw_ = random.uniform(90, 220); bh_ = random.uniform(90, 320)
    d.rectangle([bx, h - bh_, bx + bw_, h], fill=(4, 10, 26))
    bx += bw_ + random.uniform(4, 30)
hero(d, w*0.855, h*0.99, h*0.74, arms="raise")
img = add_glow(img, w*0.855, h*0.53, 85, RED, 150)
img.save(f"{OUT}/kv/s01_01_bg-keyvisual_BG.png")   # タイトル背景はラベルなし
print("saved", f"{OUT}/kv/s01_01_bg-keyvisual_BG.png", img.size)

# ---- s03 熱量ビジュアル 5点(1600x1500相当) ----
w, h = 1600, 1500
img = scene_family_lookup(w, h)
save(img, f"{OUT}/photo/s03_01_arrive_M.png", "ARRIVE  会場に来る")

img = canvas(w, h)
d = ImageDraw.Draw(img)
phone(d, w*0.3, h*0.18, w*0.4, h*0.62)
d2 = ImageDraw.Draw(img)
hero(d2, w*0.5, h*0.7, h*0.36, arms="raise")          # 画面内ヒーロー
img = add_glow(img, w*0.5, h*0.47, 40, RED, 120)
d = ImageDraw.Draw(img)
person(d, w*0.14, h*1.05, h*0.5)                      # 撮影者
d.ellipse([w*0.44, h*0.86, w*0.56, h*0.9], fill=WHITE) # シャッターUI
save(img, f"{OUT}/photo/s03_02_shoot_M.png", "SHOOT  写真を撮る")

img = canvas(w, h)
d = ImageDraw.Draw(img)
shelf(d, w*0.15, h*0.2, w*0.7, h*0.5, rows=3, header="1")
person(d, w*0.3, h*0.95, h*0.32, arms="raise")        # 手を伸ばす子ども
save(img, f"{OUT}/photo/s03_03_pickup_M.png", "PICK UP  商品を手に取る")

img = canvas(w, h)
d = ImageDraw.Draw(img)
phone(d, w*0.28, h*0.12, w*0.44, h*0.72)
d.rectangle([w*0.33, h*0.2, w*0.67, h*0.5], fill=NAVY3)   # 投稿画像
hero(d, w*0.5, h*0.47, h*0.2, arms="up")
d.ellipse([w*0.35, h*0.56, w*0.39, h*0.585], fill=RED)     # ハート
d.rectangle([w*0.42, h*0.56, w*0.62, h*0.575], fill=LINE)
d.rectangle([w*0.35, h*0.62, w*0.65, h*0.635], fill=LINE)
save(img, f"{OUT}/photo/s03_04_share_M.png", "SHARE  誰かに共有する")

img = canvas(w, h)
img = add_glow(img, w*0.62, h*0.4, 300, (70, 130, 210), 70)
d = ImageDraw.Draw(img)
hero(d, w*0.62, h*0.9, h*0.55, arms="down")
person(d, w*0.33, h*0.92, h*0.28, arms="raise")
save(img, f"{OUT}/photo/s03_05_greeting_M.png", "GREETING  ヒーローと握手")

# ---- s04 モメンタム 8点(1200x1650 縦) ----
w, h = 1200, 1650
scenes4 = [
    ("s04_01_ulsama_M", "ULSAMA  会場の熱量", lambda: scene_stage_crowd(w, h)),
    ("s04_02_heroshow_M", "HERO SHOW", lambda: scene_stage_crowd(w, h, hero_pose="up")),
]
for name, text, fn in scenes4:
    save(fn(), f"{OUT}/photo/{name}.png", text)

img = canvas(w, h)                                     # 商品化
d = ImageDraw.Draw(img)
for i, bx in enumerate([0.12, 0.42, 0.68]):
    box3d(d, w*bx, h*(0.35 + 0.12*i % 0.2), w*0.2, h*0.16,
          face=[RED, CYAN, GOLD][i], side=REDDK)
tshirt(d, w*0.3, h*0.62, w*0.36, NAVY3)
save(img, f"{OUT}/photo/s04_03_products_M.png", "PRODUCTS  商品化")

img = canvas(w, h)                                     # IPコラボ
d = ImageDraw.Draw(img)
d.ellipse([w*0.14, h*0.3, w*0.5, h*0.55], fill=SILVER)          # まるいマスコット
d.ellipse([w*0.22, h*0.36, w*0.28, h*0.42], fill=NAVY)
d.ellipse([w*0.36, h*0.36, w*0.42, h*0.42], fill=NAVY)
hero(d, w*0.68, h*0.62, h*0.28, arms="up")
d.text((w*0.47, h*0.42), "x", fill=WHITE)
save(img, f"{OUT}/photo/s04_04_collab_M.png", "IP COLLAB")

img = canvas(w, h)                                     # ウルトラマート
d = ImageDraw.Draw(img)
d.rectangle([w*0.1, h*0.3, w*0.9, h*0.8], fill=NAVY3, outline=LINE, width=4)
d.rectangle([w*0.1, h*0.3, w*0.9, h*0.4], fill=RED)
d.rectangle([w*0.38, h*0.52, w*0.62, h*0.8], fill=NAVY2)        # 入口
person(d, w*0.3, h*0.92, h*0.24); person(d, w*0.7, h*0.92, h*0.22, arms="up")
save(img, f"{OUT}/photo/s04_05_ultramart_M.png", "ULTRA MART")

img = canvas(w, h)
d = ImageDraw.Draw(img)
shelf(d, w*0.12, h*0.28, w*0.76, h*0.5, rows=4, header="1")
save(img, f"{OUT}/photo/s04_06_retail_M.png", "RETAIL  流通展開")

img = canvas(w, h)                                     # 広告
d = ImageDraw.Draw(img)
d.rectangle([w*0.14, h*0.22, w*0.86, h*0.66], fill=NAVY3, outline=SILVER, width=6)
hero(d, w*0.38, h*0.6, h*0.28, arms="raise")
d.rectangle([w*0.55, h*0.36, w*0.8, h*0.4], fill=WHITE)
d.rectangle([w*0.55, h*0.45, w*0.74, h*0.48], fill=RED)
person(d, w*0.3, h*0.9, h*0.2); person(d, w*0.6, h*0.9, h*0.22)
save(img, f"{OUT}/photo/s04_07_ad_M.png", "AD TIE-UP  広告タイアップ")

img = canvas(w, h)                                     # 海外
d = ImageDraw.Draw(img)
d.ellipse([w*0.2, h*0.25, w*0.8, h*0.7], outline=CYAN, width=8)
d.arc([w*0.2, h*0.35, w*0.8, h*0.6], 0, 360, fill=CYAN, width=4)
d.line([w*0.5, h*0.25, w*0.5, h*0.7], fill=CYAN, width=4)
hero(d, w*0.5, h*0.93, h*0.25, arms="up")
save(img, f"{OUT}/photo/s04_08_global_M.png", "GLOBAL  海外展開")

# ---- s07-s11 カテゴリーゾーン(メイン1600x705+サブ800x527) ----
def cat_main(path, text, draw_fn):
    w, h = 1600, 705
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    draw_fn(img, d, w, h)
    save(img, path, text, "MOCK COMP")

def cat_thumb(path, text, draw_fn):
    w, h = 800, 527
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    draw_fn(img, d, w, h)
    save(img, path, text, "MOCK COMP")

# s07 MD
def f(img, d, w, h):
    tshirt(d, w*0.05, h*0.18, w*0.22, NAVY3)
    tshirt(d, w*0.3, h*0.18, w*0.22, (30, 30, 36), mark=SILVER)
    d.rounded_rectangle([w*0.58, h*0.3, w*0.75, h*0.52], radius=20, fill=RED)   # キャップ
    d.rectangle([w*0.58, h*0.5, w*0.79, h*0.56], fill=REDDK)
    box3d(d, w*0.82, h*0.35, w*0.12, h*0.35, face=CYAN, side=(60, 120, 160))
cat_main(f"{OUT}/mock/s07_01_apparel-main_M.png", "APPAREL LINE  大人向け2ライン", f)
def f(img, d, w, h):
    for i in range(4):
        d.rounded_rectangle([w*(0.08+i*0.23), h*0.25, w*(0.08+i*0.23)+w*0.16, h*0.75],
                            radius=12, fill=NAVY3, outline=LINE, width=3)
        hero(d, w*(0.16+i*0.23), h*0.68, h*0.3, arms=["raise","up","down","raise"][i])
cat_thumb(f"{OUT}/mock/s07_02_acsta-cards_S.png", "アクスタ・カード集合", f)
def f(img, d, w, h):
    img2 = add_glow(img, w*0.5, h*0.4, 160, GOLD, 60)
    img.paste(img2)
    d.rectangle([w*0.3, h*0.75, w*0.7, h*0.85], fill=(20, 20, 24))
    hero(d, w*0.5, h*0.76, h*0.52, body=(220, 225, 235), arms="raise")
cat_thumb(f"{OUT}/mock/s07_03_premium-figure_S.png", "プレミアムフィギュア", f)
def f(img, d, w, h):
    shelf(d, w*0.1, h*0.2, w*0.8, h*0.55, rows=3, header="1")
cat_thumb(f"{OUT}/mock/s07_04_shelf_S.png", "売場イメージ", f)

# s08 食品
def f(img, d, w, h):
    box3d(d, w*0.08, h*0.3, w*0.2, h*0.45, face=RED, side=REDDK)
    for i in range(8):                                  # 光バースト
        ang = i * math.pi / 4
        x0, y0 = w*0.18, h*0.45
        d.line([x0, y0, x0 + math.cos(ang)*w*0.05, y0 + math.sin(ang)*w*0.05],
               fill=GOLD, width=6)
    bottle(d, w*0.42, h*0.15, w*0.09, h*0.68)
    bottle(d, w*0.55, h*0.15, w*0.09, h*0.68, body=RED)
    d.ellipse([w*0.72, h*0.3, w*0.95, h*0.75], fill=SILVER)      # キッズプレート
    d.ellipse([w*0.76, h*0.38, w*0.85, h*0.55], fill=GOLD)
    d.ellipse([w*0.85, h*0.5, w*0.92, h*0.64], fill=RED)
cat_main(f"{OUT}/mock/s08_01_package-main_M.png", "限定パッケージ+コラボメニュー", f)
def f(img, d, w, h):
    for i in range(5):
        x = w*0.12 + i*w*0.14
        d.rounded_rectangle([x, h*0.22 + i*h*0.06, x + w*0.16, h*0.75],
                            radius=10, fill=NAVY3, outline=GOLD, width=3)
        hero(d, x + w*0.08, h*(0.62 + i*0.05), h*0.26, arms="raise")
cat_thumb(f"{OUT}/mock/s08_02_bonus-cards_S.png", "購入特典カード(扇形)", f)
def f(img, d, w, h):
    d.rectangle([w*0.15, h*0.2, w*0.85, h*0.62], fill=NAVY3, outline=RED, width=5)
    d.rectangle([w*0.15, h*0.2, w*0.85, h*0.32], fill=RED)
    d.polygon([(w*0.3, h*0.62), (w*0.42, h*0.62), (w*0.36, h*0.78)], fill=SILVER)  # 半券
cat_thumb(f"{OUT}/mock/s08_03_ticket-campaign_S.png", "映画半券キャンペーン", f)
def f(img, d, w, h):
    d.rectangle([w*0.1, h*0.55, w*0.9, h*0.62], fill=NAVY3)     # カウンター
    person(d, w*0.3, h*0.92, h*0.34); person(d, w*0.42, h*0.92, h*0.22, arms="up")
    box3d(d, w*0.6, h*0.35, w*0.14, h*0.18, face=RED, side=REDDK)
cat_thumb(f"{OUT}/mock/s08_04_parent-child_S.png", "親子が店頭で選ぶ", f)

# s09 流通
def f(img, d, w, h):
    shelf(d, w*0.06, h*0.28, w*0.55, h*0.55, rows=3, header="1")
    d.rectangle([w*0.06, h*0.06, w*0.61, h*0.24], fill=RED)     # 大型ヘッダー
    hero(d, w*0.13, h*0.23, h*0.14, arms="raise")
    d.rectangle([w*0.2, h*0.12, w*0.5, h*0.16], fill=WHITE)
    browser(d, w*0.66, h*0.1, w*0.3, h*0.72)
    hero(d, w*0.81, h*0.5, h*0.22, arms="up")
    d.rectangle([w*0.69, h*0.6, w*0.93, h*0.64], fill=RED)
cat_main(f"{OUT}/mock/s09_01_shelf-ec-main_M.png", "映画公開記念棚+EC特集", f)
def f(img, d, w, h):
    d.polygon([(w*0.2, h*0.75), (w*0.5, h*0.2), (w*0.8, h*0.75)], fill=NAVY3)   # POPUPテント風
    d.rectangle([w*0.28, h*0.55, w*0.72, h*0.75], fill=RED)
    person(d, w*0.2, h*0.92, h*0.22); person(d, w*0.82, h*0.92, h*0.2)
cat_thumb(f"{OUT}/mock/s09_02_popup_S.png", "POPUP売場", f)
def f(img, d, w, h):
    d.rounded_rectangle([w*0.15, h*0.15, w*0.85, h*0.85], radius=14,
                        fill=NAVY3, outline=GOLD, width=4)
    for i in range(3):
        for j in range(2):
            cx, cy = w*(0.28 + i*0.22), h*(0.38 + j*0.28)
            d.ellipse([cx-32, cy-32, cx+32, cy+32],
                      outline=RED, width=5, fill=NAVY2 if (i+j) % 2 else REDDK)
cat_thumb(f"{OUT}/mock/s09_03_stamp-rally_S.png", "スタンプラリー台紙", f)

# s10 広告
def f(img, d, w, h):
    d.rectangle([0, h*0.75, w, h], fill=(6, 12, 28))            # 駅ホーム床
    d.rectangle([w*0.12, h*0.1, w*0.66, h*0.72], fill=NAVY3, outline=SILVER, width=8)
    hero(d, w*0.28, h*0.66, h*0.4, arms="raise")
    d.rectangle([w*0.42, h*0.26, w*0.6, h*0.3], fill=WHITE)
    d.rectangle([w*0.42, h*0.36, w*0.56, h*0.4], fill=RED)
    person(d, w*0.78, h*0.98, h*0.32); person(d, w*0.88, h*0.98, h*0.3)
cat_main(f"{OUT}/mock/s10_01_station-ad-main_M.png", "交通広告(駅貼りB0)", f)
def f(img, d, w, h):
    phone(d, w*0.32, h*0.08, w*0.36, h*0.84)
    d.rectangle([w*0.36, h*0.16, w*0.64, h*0.42], fill=NAVY3)
    hero(d, w*0.5, h*0.4, h*0.18, arms="up")
    d.ellipse([w*0.38, h*0.47, w*0.41, h*0.5], fill=RED)
    d.rectangle([w*0.44, h*0.47, w*0.6, h*0.49], fill=LINE)
cat_thumb(f"{OUT}/mock/s10_02_sns_S.png", "SNSキャンペーン投稿", f)
def f(img, d, w, h):
    hero(d, w*0.6, h*0.85, h*0.5, arms="down")
    for i, fx in enumerate([0.2, 0.32, 0.44]):
        person(d, w*fx, h*0.92, h*(0.2 + i*0.02), arms="up")
cat_thumb(f"{OUT}/mock/s10_03_greeting-crowd_S.png", "グリーティング集客", f)

# s11 デジタル
def f(img, d, w, h):
    d.rectangle([w*0.03, h*0.06, w*0.97, h*0.94], fill=NAVY2, outline=CYAN, width=4)
    d.rectangle([w*0.05, h*0.1, w*0.3, h*0.16], fill=NAVY3)          # HPバー
    d.rectangle([w*0.05, h*0.1, w*0.22, h*0.16], fill=RED)
    d.rectangle([w*0.7, h*0.1, w*0.95, h*0.16], fill=NAVY3)
    d.rectangle([w*0.7, h*0.1, w*0.86, h*0.16], fill=CYAN)
    hero(d, w*0.35, h*0.82, h*0.5, arms="raise")
    hero(d, w*0.68, h*0.84, h*0.44, body=(90, 60, 70), accent=GOLD, arms="up")
    for i in range(4):                                                # スキルUI
        d.ellipse([w*(0.4+i*0.06), h*0.84, w*(0.4+i*0.06)+w*0.045, h*0.84+w*0.045],
                  outline=CYAN, width=3)
cat_main(f"{OUT}/mock/s11_01_game-main_M.png", "ゲーム内コラボ画面", f)
def f(img, d, w, h):
    phone(d, w*0.32, h*0.06, w*0.36, h*0.88)
    img2 = add_glow(img, w*0.5, h*0.42, 90, GOLD, 110)
    img.paste(img2)
    hero(ImageDraw.Draw(img), w*0.5, h*0.62, h*0.3, arms="raise")
    ImageDraw.Draw(img).rectangle([w*0.4, h*0.75, w*0.6, h*0.8], fill=RED)
cat_thumb(f"{OUT}/mock/s11_02_gacha_S.png", "ガチャ・限定アバター", f)
def f(img, d, w, h):
    d.rectangle([w*0.08, h*0.12, w*0.92, h*0.7], fill=NAVY3)
    d.polygon([(w*0.44, h*0.3), (w*0.44, h*0.52), (w*0.6, h*0.41)], fill=RED)   # 再生
    d.rectangle([w*0.08, h*0.76, w*0.7, h*0.8], fill=LINE)
    d.rectangle([w*0.08, h*0.84, w*0.5, h*0.87], fill=LINE)
cat_thumb(f"{OUT}/mock/s11_03_youtube_S.png", "YouTubeサムネイル風", f)
def f(img, d, w, h):
    d.rectangle([w*0.05, h*0.1, w*0.68, h*0.9], fill=NAVY3)
    hero(d, w*0.36, h*0.78, h*0.44, arms="up")
    d.ellipse([w*0.08, h*0.13, w*0.12, h*0.17], fill=RED)            # LIVE
    for i in range(6):                                               # チャット欄
        d.rectangle([w*0.72, h*(0.14+i*0.13), w*0.95, h*(0.14+i*0.13)+h*0.05],
                    fill=NAVY2, outline=LINE)
cat_thumb(f"{OUT}/mock/s11_04_livestream_S.png", "ライブ配信画面", f)

# ---- s12 イベント・施設 4点(1600x1065) ----
w, h = 1600, 1065
save(scene_stage_crowd(w, h), f"{OUT}/photo/s12_01_heroshow_M.png", "HERO SHOW+観客")
img = canvas(w, h)
img = add_glow(img, w*0.6, h*0.35, 260, (70, 130, 210), 70)
d = ImageDraw.Draw(img)
hero(d, w*0.6, h*0.88, h*0.6, arms="down")
person(d, w*0.38, h*0.9, h*0.3, arms="raise")
save(img, f"{OUT}/photo/s12_02_greeting_M.png", "グリーティング(握手)")
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.rounded_rectangle([w*0.12, h*0.12, w*0.88, h*0.82], radius=18, fill=NAVY3,
                    outline=GOLD, width=5)
d.rectangle([w*0.12, h*0.12, w*0.88, h*0.26], fill=RED)
pts = [(0.25, 0.45), (0.45, 0.6), (0.62, 0.4), (0.78, 0.62)]
for i in range(len(pts) - 1):
    d.line([w*pts[i][0], h*pts[i][1], w*pts[i+1][0], h*pts[i+1][1]],
           fill=CYAN, width=6)
for fx, fy in pts:
    d.ellipse([w*fx-26, h*fy-26, w*fx+26, h*fy+26], fill=RED)
save(img, f"{OUT}/photo/s12_03_stamprally_M.png", "館内スタンプラリーマップ")
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.rectangle([w*0.1, h*0.2, w*0.9, h*0.55], fill=NAVY3, outline=LINE, width=4)   # 商業施設
d.rectangle([w*0.42, h*0.35, w*0.58, h*0.55], fill=NAVY2)
crowd(d, w, h*0.98, 16, h*0.2, h*0.28, arms_up_ratio=0.3)
save(img, f"{OUT}/photo/s12_04_mall-event_M.png", "商業施設イベントの賑わい")

# ---- s13 コラボ 5点(800x800) ----
w, h = 800, 800
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.ellipse([w*0.22, h*0.3, w*0.78, h*0.75], fill=SILVER)          # まるいマスコット
d.ellipse([w*0.34, h*0.42, w*0.42, h*0.5], fill=NAVY)
d.ellipse([w*0.58, h*0.42, w*0.66, h*0.5], fill=NAVY)
d.ellipse([w*0.44, h*0.28, w*0.56, h*0.4], fill=RED)             # 頭にタイマー
save(img, f"{OUT}/photo/s13_01_cute-collab_S.png", "かわいい文脈コラボ")
img = canvas(w, h)
d = ImageDraw.Draw(img)
for i in range(3):                                               # コマ玩具
    cx, cy = w*(0.3 + i*0.2), h*0.5
    d.ellipse([cx-70, cy-70, cx+70, cy+70], fill=[RED, CYAN, GOLD][i])
    d.ellipse([cx-30, cy-30, cx+30, cy+30], fill=NAVY2)
    d.polygon([(cx-14, cy+64), (cx+14, cy+64), (cx, cy+110)], fill=SILVER)
save(img, f"{OUT}/photo/s13_02_hobby-collab_S.png", "ホビー文脈コラボ")
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.ellipse([w*0.3, h*0.32, w*0.7, h*0.66], fill=WHITE)            # リボンキャラ風
d.polygon([(w*0.3, h*0.34), (w*0.2, h*0.22), (w*0.34, h*0.3)], fill=WHITE)
d.polygon([(w*0.7, h*0.34), (w*0.8, h*0.22), (w*0.66, h*0.3)], fill=WHITE)
d.ellipse([w*0.62, h*0.3, w*0.74, h*0.42], fill=RED)             # リボン
d.ellipse([w*0.4, h*0.45, w*0.45, h*0.5], fill=NAVY)
d.ellipse([w*0.55, h*0.45, w*0.6, h*0.5], fill=NAVY)
save(img, f"{OUT}/photo/s13_03_character-collab_S.png", "キャラクター文脈【開示確認】")
img = canvas(w, h)
d = ImageDraw.Draw(img)
hero(d, w*0.5, h*0.85, h*0.6, arms="raise")
img = add_glow(img, w*0.5, h*0.47, 44, RED, 140)
save(img, f"{OUT}/photo/s13_04_hero-collab_S.png", "ヒーロー文脈コラボ")
img = canvas(w, h)
d = ImageDraw.Draw(img)
shelf(d, w*0.12, h*0.25, w*0.76, h*0.5, rows=3, header="1")
save(img, f"{OUT}/photo/s13_05_collab-shelf_S.png", "コラボ棚")

# ---- s14 ULTRA MART 4点(1600x943) ----
w, h = 1600, 943
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.rectangle([w*0.08, h*0.24, w*0.92, h*0.85], fill=NAVY3, outline=LINE, width=5)
d.rectangle([w*0.08, h*0.24, w*0.92, h*0.4], fill=RED)
d.rectangle([w*0.4, h*0.52, w*0.6, h*0.85], fill=NAVY2)
d.rectangle([w*0.14, h*0.5, w*0.34, h*0.78], fill=NAVY2)         # ウィンドウ
d.rectangle([w*0.66, h*0.5, w*0.86, h*0.78], fill=NAVY2)
hero(d, w*0.24, h*0.76, h*0.2, arms="raise")
person(d, w*0.5, h*0.94, h*0.22)
save(img, f"{OUT}/photo/s14_01_storefront_M.png", "ULTRA MART 外観")
img = canvas(w, h)
d = ImageDraw.Draw(img)
shelf(d, w*0.06, h*0.2, w*0.4, h*0.6, rows=3)
shelf(d, w*0.54, h*0.2, w*0.4, h*0.6, rows=3)
person(d, w*0.5, h*0.95, h*0.3); person(d, w*0.62, h*0.95, h*0.2, arms="up")
save(img, f"{OUT}/photo/s14_02_interior_M.png", "店内の賑わい")
img = canvas(w, h)
d = ImageDraw.Draw(img)
shelf(d, w*0.15, h*0.15, w*0.7, h*0.6, rows=3, header="1", hdr_color=GOLD)
save(img, f"{OUT}/photo/s14_03_limited-corner_M.png", "限定商品コーナー")
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.polygon([(w*0.25, h*0.72), (w*0.5, h*0.2), (w*0.75, h*0.72)], fill=NAVY3)
d.rectangle([w*0.33, h*0.5, w*0.67, h*0.72], fill=RED)
crowd(d, w, h*0.98, 8, h*0.18, h*0.24, arms_up_ratio=0.2)
save(img, f"{OUT}/photo/s14_04_popup_M.png", "POPUP展開")

# ---- s15 スタイルガイド見開き 3点(1600x726) ----
def spread(path, text, page_fn):
    w, h = 1600, 726
    img = canvas(w, h, NAVY2, NAVY2)
    d = ImageDraw.Draw(img)
    d.rectangle([w*0.05, h*0.08, w*0.95, h*0.92], fill=WHITE)
    d.line([w*0.5, h*0.08, w*0.5, h*0.92], fill=(200, 205, 215), width=3)
    page_fn(d, w, h)
    save(img, path, text, "STYLE GUIDE COMP")

def f(d, w, h):
    d.rectangle([w*0.09, h*0.16, w*0.2, h*0.3], fill=RED)             # ロゴ枠
    d.rectangle([w*0.24, h*0.16, w*0.35, h*0.3], fill=NAVY)
    d.rectangle([w*0.09, h*0.4, w*0.44, h*0.44], fill=(60, 60, 70))
    for i, c in enumerate([RED, NAVY, CYAN, GOLD, SILVER]):           # パレット
        d.rectangle([w*(0.09+i*0.073), h*0.55, w*(0.09+i*0.073)+w*0.06, h*0.72], fill=c)
    d.rectangle([w*0.55, h*0.16, w*0.91, h*0.72], outline=(200,205,215), width=3)
    hero(d, w*0.73, h*0.62, h*0.36, body=(90, 100, 120), arms="raise")
spread(f"{OUT}/mock/s15_01_guide-logo_M.png", "ロゴ使用例+カラーパレット", f)
def f(d, w, h):
    d.rectangle([w*0.09, h*0.16, w*0.44, h*0.72], outline=(200,205,215), width=3)
    for gx in range(4):
        d.line([w*(0.09+gx*0.0875), h*0.16, w*(0.09+gx*0.0875), h*0.72],
               fill=(225,228,235), width=2)
    hero(d, w*0.265, h*0.62, h*0.34, body=(90,100,120), arms="raise")
    d.ellipse([w*0.56, h*0.2, w*0.61, h*0.3], outline=(30,150,80), width=6)     # OK
    d.line([w*0.56, h*0.45, w*0.61, h*0.55], fill=RED, width=6)                 # NG
    d.line([w*0.61, h*0.45, w*0.56, h*0.55], fill=RED, width=6)
    d.rectangle([w*0.64, h*0.2, w*0.91, h*0.3], fill=(240,242,246))
    d.rectangle([w*0.64, h*0.45, w*0.91, h*0.55], fill=(240,242,246))
spread(f"{OUT}/mock/s15_02_guide-okng_M.png", "キャラクター配置+OK/NG例", f)
def f(d, w, h):
    tshirt(d, w*0.09, h*0.2, w*0.13, (40, 45, 60))
    box3d(d, w*0.28, h*0.34, w*0.1, h*0.3, face=RED, side=REDDK)
    d.rectangle([w*0.55, h*0.18, w*0.91, h*0.4], fill=RED)                      # POP
    d.rectangle([w*0.58, h*0.24, w*0.83, h*0.28], fill=WHITE)
    d.rectangle([w*0.55, h*0.5, w*0.75, h*0.72], fill=(240,242,246))
spread(f"{OUT}/mock/s15_03_guide-products_M.png", "商品・POP展開例", f)

# ---- s17/s21 QR(1100x1100・ダミー) ----
import qrcode
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=4)
qr.add_data("https://example.com/ubpm2026-registration-DUMMY")
qr.make(fit=True)
qimg = qr.make_image(fill_color="black", back_color="white").convert("RGB")
qimg = qimg.resize((900, 900), Image.NEAREST)
tile = Image.new("RGB", (1100, 1100), "white")
tile.paste(qimg, (100, 60))
d = ImageDraw.Draw(tile)
try:
    from PIL import ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
except Exception:
    font = None
d.text((160, 990), "DUMMY QR - REPLACE WITH PROD URL", fill=(168, 28, 24), font=font)
tile.save(f"{OUT}/qr/s17_01_qr-dummy_QR.png")
print("saved", f"{OUT}/qr/s17_01_qr-dummy_QR.png", tile.size)

# ---- s18 コンテンツパノラマ(3520x1108) ----
w, h = 3520, 1108
img = canvas(w, h, (0, 4, 14), NAVY2)
img = add_glow(img, w*0.5, h*0.15, 500, (50, 110, 190), 45)
d = ImageDraw.Draw(img)
# 4接点セクション
sec_w = w / 4
labels_x = []
# TV
d.rounded_rectangle([sec_w*0.14, h*0.22, sec_w*0.86, h*0.66], radius=16,
                    fill=NAVY3, outline=SILVER, width=5)
hero(d, sec_w*0.5, h*0.62, h*0.3, arms="raise")
d.rectangle([sec_w*0.42, h*0.66, sec_w*0.58, h*0.72], fill=SILVER)
# 映画
x0 = sec_w
d.rectangle([x0+sec_w*0.12, h*0.2, x0+sec_w*0.88, h*0.55], fill=NAVY3)
hero(d, x0+sec_w*0.5, h*0.52, h*0.24, arms="up")
for i in range(6):
    d.rounded_rectangle([x0+sec_w*(0.14+i*0.125), h*0.66, x0+sec_w*(0.14+i*0.125)+sec_w*0.09,
                         h*0.78], radius=10, fill=(20, 32, 60))
# 配信
x0 = sec_w*2
d.rounded_rectangle([x0+sec_w*0.14, h*0.22, x0+sec_w*0.86, h*0.66], radius=16, fill=NAVY3)
d.polygon([(x0+sec_w*0.42, h*0.34), (x0+sec_w*0.42, h*0.54), (x0+sec_w*0.62, h*0.44)],
          fill=RED)
d.rectangle([x0+sec_w*0.18, h*0.72, x0+sec_w*0.7, h*0.76], fill=LINE)
# イベント
x0 = sec_w*3
img2 = img
d2 = d
hero(d2, x0+sec_w*0.5, h*0.6, h*0.34, arms="raise")
crowd(d2, sec_w, h*0.92, 10, h*0.14, h*0.2, arms_up_ratio=0.6)  # ローカル座標→補正
# crowd はimg全体x基準のため個別に描き直し
for fx in [0.06, 0.16, 0.3, 0.44, 0.58, 0.72, 0.86]:
    person(d2, x0 + sec_w*fx + sec_w*0.06, h*0.95, h*random.uniform(0.14, 0.2),
           arms="up" if random.random() < 0.6 else "down")
img = add_glow(img, x0+sec_w*0.5, h*0.31, 40, RED, 120)
# ヒーローラインナップ(全幅・下部)
d = ImageDraw.Draw(img)
save(img, f"{OUT}/kv/s18_01_content-panorama_L.png",
     "TV  /  MOVIE  /  STREAMING  /  EVENT", "3520x1108 / KV COMP")

# ---- s19 3接点(1600x504) ----
w, h = 1600, 504
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.rounded_rectangle([w*0.2, h*0.14, w*0.8, h*0.78], radius=14, fill=NAVY3,
                    outline=SILVER, width=5)
hero(d, w*0.5, h*0.72, h*0.4, arms="raise")
d.rectangle([w*0.42, h*0.78, w*0.58, h*0.86], fill=SILVER)
save(img, f"{OUT}/photo/s19_01_tv_M.png", "TVシリーズ(継続接点)")
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.rectangle([w*0.15, h*0.12, w*0.85, h*0.6], fill=NAVY3)
hero(d, w*0.5, h*0.56, h*0.3, arms="up")
for i in range(8):
    d.rounded_rectangle([w*(0.16+i*0.09), h*0.7, w*(0.16+i*0.09)+w*0.06, h*0.86],
                        radius=8, fill=(20, 32, 60))
save(img, f"{OUT}/photo/s19_02_movie_M.png", "映画・大型映像(話題化)")
img = canvas(w, h)
d = ImageDraw.Draw(img)
d.rounded_rectangle([w*0.22, h*0.12, w*0.78, h*0.74], radius=14, fill=NAVY3)
d.polygon([(w*0.44, h*0.3), (w*0.44, h*0.56), (w*0.6, h*0.43)], fill=RED)
d.rectangle([w*0.22, h*0.8, w*0.6, h*0.85], fill=LINE)
save(img, f"{OUT}/photo/s19_03_streaming_M.png", "配信・YouTube(コアファン)")

# ---- s21 クロージング(2390x634) ----
w, h = 2390, 634
img = canvas(w, h, NAVY, (26, 20, 44))
img = add_glow(img, w*0.5, h*0.95, 420, (230, 120, 60), 60)      # 夜明け
d = ImageDraw.Draw(img)
d.rectangle([0, h*0.88, w, h], fill=(4, 8, 20))
for i, fx in enumerate([0.16, 0.3, 0.44, 0.58, 0.72, 0.86]):
    hero(d, w*fx, h*0.88, h*random.uniform(0.5, 0.62),
         arms=["raise", "up", "down"][i % 3])
img = add_glow(img, w*0.5, h*0.5, 120, RED, 60)
save(img, f"{OUT}/kv/s21_01_closing_L.png", "HEROES TOWARD 2027", "2390x634 / KV COMP")

print("\nDONE — all assets generated under ./assets/")
