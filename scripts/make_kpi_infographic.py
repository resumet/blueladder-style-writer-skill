#!/usr/bin/env python3
"""Render source-grounded Korean KPI infographic to a 2000x1125 PNG.

Only draws data passed in JSON; it does not obtain, infer or verify statistics.
"""
import argparse
from functools import lru_cache
import json
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageColor

W, H = 2000, 1125
WHITE = "#F5F7FA"
MUTED = "#A9B8C6"
BASE = (9, 16, 28)
CARD = "#142335"
FONT_PATHS = {False: None, True: None}


def supports_korean(path):
    """Reject unreadable fonts and the missing-glyph boxes used for Hangul."""
    try:
        font = ImageFont.truetype(str(path), 32)
        missing = font.getmask("\U0010ffff")
        missing_signature = (missing.size, bytes(missing))
        for character in "한글가":
            glyph = font.getmask(character)
            if not glyph.getbbox() or (glyph.size, bytes(glyph)) == missing_signature:
                return False
        return True
    except (OSError, ValueError):
        return False


@lru_cache(maxsize=2)
def font_file(bold=False):
    explicit = FONT_PATHS[bold]
    if explicit is not None:
        path = Path(explicit).expanduser()
        if not path.is_file() or not supports_korean(path):
            raise ValueError(f"Font is missing, unreadable, or lacks Korean glyphs: {path}")
        return str(path)

    candidates = []
    family = "Noto Sans CJK KR:lang=ko:style=Bold" if bold else "Noto Sans CJK KR:lang=ko"
    try:
        result = subprocess.check_output(
            ["fc-match", "-f", "%{file}", family], text=True, stderr=subprocess.DEVNULL,
        ).strip()
        if result:
            candidates.append(Path(result))
    except (OSError, subprocess.CalledProcessError):
        pass

    windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    candidates.extend(Path(file) for file in [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        windows_fonts / ("malgunbd.ttf" if bold else "malgun.ttf"),
        windows_fonts / "malgun.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/NotoSansKR-Bold.ttf" if bold else "/Library/Fonts/NotoSansKR-Regular.ttf",
    ])
    for path in candidates:
        if path.is_file() and supports_korean(path):
            return str(path)
    raise RuntimeError(
        "No readable Korean font found. Install Noto Sans CJK KR, or pass "
        "--font /path/to/korean-font.ttf and optionally --bold-font /path/to/bold.ttf."
    )


@lru_cache(maxsize=128)
def ft(px, bold=False):
    return ImageFont.truetype(font_file(bold), px)


def fit(d, text, width, start=64, minimum=22, bold=True):
    for size in range(start, minimum - 1, -2):
        font = ft(size, bold)
        if d.textbbox((0, 0), str(text), font=font)[2] <= width:
            return font
    return ft(minimum, bold)


def as_rgb(value):
    if not isinstance(value, str) or not value.startswith("#"):
        raise ValueError("accent must be a CSS hex color like '#76B900'")
    return ImageColor.getrgb(value)


def load_data(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    for key in ["title", "subtitle", "source", "kpis"]:
        if not d.get(key):
            raise ValueError(f"required field missing: {key}")
    if not 3 <= len(d["kpis"]) <= 4:
        raise ValueError("kpis must contain 3 or 4 items")
    for k in d["kpis"]:
        for key in ["label", "value", "change"]:
            if not str(k.get(key, "")).strip():
                raise ValueError(f"KPI item requires {key}")
    if "bars" in d:
        bars = d["bars"]
        if not bars.get("title") or not 2 <= len(bars.get("items", [])) <= 4:
            raise ValueError("bars requires title and 2..4 items")
        for b in bars["items"]:
            if not isinstance(b.get("value"), (int, float)) or b["value"] < 0 or not b.get("label"):
                raise ValueError("each bar needs non-negative numeric value and label")
    as_rgb(d.get("accent", "#76B900"))
    return d


def background():
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            shift = int(13 * (x / W) + 10 * (1 - y / H))
            px[x, y] = tuple(min(c + shift, 255) for c in BASE)
    return im


def render(data, path, font=None, bold_font=None):
    FONT_PATHS[False] = font
    FONT_PATHS[True] = bold_font if bold_font is not None else font
    font_file.cache_clear()
    ft.cache_clear()
    # Check both weights before doing the expensive image work.
    font_file(False)
    font_file(True)
    accent = as_rgb(data.get("accent", "#76B900"))
    im = background()
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((85, 80, 100, 172), radius=7, fill=accent)
    title = str(data["title"])
    d.text((132, 74), title, font=fit(d, title, 1740, 76, 44), fill=WHITE)
    d.text((135, 175), str(data["subtitle"]), font=fit(d, data["subtitle"], 1670, 35, 24, False), fill=MUTED)

    cards = data["kpis"]
    gap = 24
    total = 1830
    cw = (total - gap * (len(cards)-1)) / len(cards)
    start_x = 85
    top, bottom = 278, 559
    for i, k in enumerate(cards):
        x0 = round(start_x + i * (cw + gap))
        x1 = round(x0 + cw)
        d.rounded_rectangle((x0, top, x1, bottom), radius=28, fill=CARD, outline="#2B4355", width=2)
        d.rounded_rectangle((x0, top, x1, top + 13), radius=6, fill=accent)
        d.text((x0 + 27, top + 49), str(k["label"]), font=fit(d, k["label"], cw-55, 36, 26), fill=MUTED)
        d.text((x0 + 27, top + 113), str(k["value"]), font=fit(d, k["value"], cw-55, 61, 33), fill=WHITE)
        change = str(k["change"])
        d.text((x0 + 27, top + 219), change, font=fit(d, change, cw-55, 28, 19), fill=accent)

    d.line((85, 606, 1915, 606), fill="#375063", width=2)
    left_x, left_w = 85, 1195
    d.text((left_x, 628), str(data.get("section_title", "핵심 수치 비교")), font=ft(38, True), fill=WHITE)
    bars = data.get("bars")
    if bars:
        items = bars["items"]
        max_val = max(item["value"] for item in items) or 1
        chart_x, maxbar = 370, 710
        top_y, interval = 704, min(78, int(275 / max(1, len(items))))
        for i, b in enumerate(items):
            y = top_y + i * interval
            label = str(b["label"])
            d.text((left_x, y-5), label, font=fit(d, label, 240, 32, 22, False), fill=WHITE)
            width = max(8, int(maxbar * float(b["value"]) / max_val))
            d.rounded_rectangle((chart_x, y, chart_x + width, y+42), radius=10, fill=accent if i == len(items)-1 else "#6E8596")
            txt = f"{b['value']:g}{bars.get('unit', '')}"
            d.text((chart_x + width + 14, y-3), txt, font=fit(d, txt, 185, 29, 22), fill=WHITE)
        d.text((left_x, 1025), str(bars.get("note", "")), font=fit(d, bars.get("note", ""), 1120, 24, 18, False), fill=MUTED)
    else:
        summary = str(data.get("summary", "수치를 해석한 핵심 포인트를 여기에 정리합니다."))
        d.multiline_text((left_x, 715), summary, font=fit(d, summary, 1080, 48, 26, False), fill=WHITE, spacing=15)

    right_x, right_y, right_w, right_h = 1310, 645, 605, 352
    d.rounded_rectangle((right_x, right_y, right_x + right_w, right_y + right_h), radius=28, fill="#1A3040", outline="#36586B", width=2)
    d.text((right_x+34, right_y+32), "핵심 포인트", font=ft(36, True), fill=accent)
    takeaway = str(data.get("takeaway", "사업 성장과 수익성을 함께 확인해야 합니다."))
    # Text wrapping based on actual rendered width.
    words = takeaway.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if d.textbbox((0, 0), test, font=ft(38, False))[2] > 525 and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    if len(lines) > 5:
        lines = lines[:4] + ["…"]
    for i, line in enumerate(lines):
        d.text((right_x+34, right_y+117+i*50), line, font=ft(37, False), fill=WHITE)

    src = f"자료: {data['source']}"
    d.text((90, 1083), src, font=fit(d, src, 1810, 23, 16, False), fill="#9AABBA")
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG", optimize=True)
    return im.size


def main():
    ap = argparse.ArgumentParser(description="Render 16:9 Korean KPI infographic with verified user-supplied numbers")
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--font", type=Path, help="Korean-capable TTF/OTF/TTC font; auto-detect when omitted")
    ap.add_argument("--bold-font", type=Path, help="Bold font; uses --font when only --font is supplied")
    args = ap.parse_args()
    try:
        data = load_data(args.input)
        w, h = render(data, args.output, args.font, args.bold_font)
    except (OSError, ValueError, RuntimeError) as error:
        ap.exit(1, f"Cannot render infographic: {error}\n")
    print(f"Created {args.output} ({w}x{h})")


if __name__ == "__main__":
    main()
