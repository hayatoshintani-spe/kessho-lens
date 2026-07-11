#!/usr/bin/env python3
"""Google Driveフォルダから素材を一括取得し、要件(12-asset-requirements.md)に対して検品する。

30MB以上のファイルにも対応(ディスクへ直接ストリーミングし、コンテキストを経由しない)。

使い方:
    python3 fetch_and_verify_assets.py <DriveフォルダURLまたはID> [--out assets_incoming]
    python3 fetch_and_verify_assets.py --verify-only assets_incoming   # 取得済みフォルダの検品のみ

前提:
    - pip install gdown pillow
    - 対象フォルダは「リンクを知っている全員(閲覧者)」で共有されていること
    - 実行環境のネットワークポリシーで drive.google.com /
      drive.usercontent.google.com が許可されていること
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

MIN_LONG_EDGE = 1600      # 推奨最低ライン
HARD_MIN_LONG_EDGE = 1200 # これ未満は投影不可
BG_SIZE = (3840, 2160)    # 全面背景用
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".mts", ".mxf"}
OTHER_OK_EXT = {".pdf", ".pptx", ".key", ".ai", ".psd", ".zip", ".xlsx", ".docx"}

# 依頼リスト13(素材番号→用途)。ファイル名先頭の数字で突合する
ITEM_LABELS = {
    1: "親子がヒーローを見上げる", 2: "スマホ撮影の手元", 3: "売場で子どもが手を伸ばす",
    4: "SNS投稿画面", 5: "グリーティング握手", 6: "ウルサマ客席引き画",
    7: "ショー決め場面+観客", 8: "物販の行列", 9: "会場限定商品+購入者",
    10: "撮影会", 11: "館内スタンプラリー", 12: "商業施設・観光地の賑わい",
    13: "地域イベントのヒーロー登場", 14: "モフサンドコラボ", 15: "ベイブレードコラボ",
    16: "コラボ売場・棚", 17: "商品化事例:アパレル", 18: "商品化事例:ホビー・カード",
    19: "商品化事例:プレミアム", 20: "広告タイアップ掲出", 21: "海外イベント・展開",
    22: "ウルトラマート外観", 23: "店内の賑わい", 24: "商品棚クローズアップ",
    25: "限定商品コーナー", 26: "POPUP売場", 27: "EC特集ページ",
    28: "SG:ロゴ・カラー", 29: "SG:配置・OK/NG", 30: "SG:商品展開例",
    31: "監修フロー図", 32: "監修期間・チェックリスト", 33: "ヒーロー集合ビジュアル",
    34: "2027新作関連", 35: "ゼロ・映画関連", 36: "配信・YouTube",
    37: "歴代シリーズ", 38: "Tシャツ・アパレルモック", 39: "アクスタ・カード集合",
    40: "プレミアムフィギュア", 41: "限定パッケージ", 42: "購入特典カード",
    43: "映画公開記念棚", 44: "POPUP売場モック", 45: "スタンプラリー台紙",
    46: "交通広告", 47: "SNSキャンペーン投稿", 48: "ゲーム内コラボ画面",
    49: "YouTubeサムネ・配信画面",
}


def fetch(folder: str, out_dir: Path) -> bool:
    """gdownでフォルダを丸ごとダウンロード(サイズ無制限・ディスク直行)。"""
    os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
    url = folder if folder.startswith("http") else f"https://drive.google.com/drive/folders/{folder}"
    cmd = ["gdown", "--folder", url, "-O", str(out_dir), "--remaining-ok", "--continue"]
    print(f"$ {' '.join(cmd)}")
    res = subprocess.run(cmd)
    return res.returncode == 0


def guess_item(name: str):
    m = re.match(r"^\s*(\d{1,2})[\s_\-.]", name)
    if m and int(m.group(1)) in ITEM_LABELS:
        return int(m.group(1))
    return None


def verify(out_dir: Path) -> str:
    try:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None  # 高解像度素材でDecompressionBomb警告を出さない
    except ImportError:
        print("pip install pillow が必要です", file=sys.stderr)
        sys.exit(1)

    rows, problems, covered = [], [], set()
    files = sorted(p for p in out_dir.rglob("*") if p.is_file())
    for p in files:
        ext = p.suffix.lower()
        size_mb = p.stat().st_size / 1024 / 1024
        item = guess_item(p.name)
        if item:
            covered.add(item)
        status, note = "OK", ""
        if ext in IMAGE_EXT:
            try:
                with Image.open(p) as im:
                    w, h = im.size
                long_edge = max(w, h)
                dims = f"{w}×{h}"
                if long_edge < HARD_MIN_LONG_EDGE:
                    status, note = "×", f"長辺{long_edge}px — 投影基準(最低{HARD_MIN_LONG_EDGE}px)未満。元データ再送を依頼"
                elif long_edge < MIN_LONG_EDGE:
                    status, note = "△", f"長辺{long_edge}px — 使用可だが推奨{MIN_LONG_EDGE}px未満(小さめ配置に限定)"
            except Exception as e:
                dims, status, note = "-", "×", f"画像として開けない: {e}"
        elif ext in VIDEO_EXT:
            dims, note = "-", "動画 — 投影用静止画切り出しは不可。映像班へ引き渡し"
        elif ext in OTHER_OK_EXT:
            dims, note = "-", "ドキュメント/デザインデータ — 内容確認へ"
        else:
            dims, status, note = "-", "△", f"想定外の形式({ext})"
        label = f"{item} {ITEM_LABELS[item]}" if item else "(番号なし)"
        rows.append((p.relative_to(out_dir), label, dims, f"{size_mb:.1f}MB", status, note))
        if status != "OK":
            problems.append(rows[-1])

    missing = sorted(set(ITEM_LABELS) - covered)
    lines = ["# 素材検品レポート", "", f"対象: `{out_dir}`|ファイル数: {len(files)}", ""]
    lines += ["| ファイル | 素材番号 | 画素 | 容量 | 判定 | 備考 |", "| --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |" for r in rows]
    lines += ["", f"## 要対応 {len(problems)}件" if problems else "## 要対応なし(全点基準クリア)"]
    lines += [f"- {r[0]}: {r[5]}" for r in problems]
    if missing:
        lines += ["", f"## 未着の素材番号({len(missing)}点)",
                  ", ".join(f"{n}({ITEM_LABELS[n]})" for n in missing)]
    report = "\n".join(lines) + "\n"
    (out_dir / "検品レポート.md").write_text(report, encoding="utf-8")
    print(f"→ {out_dir / '検品レポート.md'}")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="DriveフォルダURL/ID、--verify-only時はローカルフォルダ")
    ap.add_argument("--out", default="assets_incoming")
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args()
    out = Path(a.target if a.verify_only else a.out)
    if not a.verify_only:
        out.mkdir(parents=True, exist_ok=True)
        if not fetch(a.target, out):
            print("ダウンロード失敗。フォルダの共有設定(リンクを知っている全員)と"
                  "ネットワーク許可(drive.google.com)を確認してください", file=sys.stderr)
            sys.exit(1)
    verify(out)


if __name__ == "__main__":
    main()
