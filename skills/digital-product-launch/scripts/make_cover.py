#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Square marketplace listing-cover generator (Pillow) — see ../references/listing-covers.md.

Usage:
    python make_cover.py [out.png] [art.png]

If no source art is given (or it is missing), a parchment placeholder panel is drawn so
the script runs anywhere. Edit CONFIG for your product.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

CONFIG = {
    "size": 1600,
    "out": "/tmp/skilltest/selar-cover.png",
    "art": None,                      # e.g. <repo>/assets/img/cover-art.png
    "kicker_top": "THE NO-HYPE BLUEPRINT",
    "kicker": "THE",
    "title_lines": [("₦5K–₦10K", "serif"), ("DIGITAL PRODUCT", "sans"), ("PLAYBOOK", "serif")],
    "promise": "Make ₦5,000–₦10,000 daily selling digital products.",
    "support": ["Create. Sell. Scale.", "A practical beginner roadmap."],
    "pill": "INSTANT DOWNLOAD  ·  ₦3,500",
    "byline": "by Your Name",
    "features": "10 CHAPTERS  ·  STEP-BY-STEP  ·  PHONE-FRIENDLY",
    "reassure": "Digital products. Real work. A system you can follow.",
    "palette": {
        "ink": "#17130D", "parchment": "#F7F1E3", "paper": "#FFF9E9",
        "cobalt": "#1D4ED8", "gold": "#D97706", "gold_light": "#F7C65D",
        "muted": "#766A56", "white": "#FFFFFF",
    },
    "fonts": {
        "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "sansb": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "serifb": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    },
}

P = CONFIG["palette"]
F = CONFIG["fonts"]
S = CONFIG["size"]


def font(path, size):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required font not found: {path}")
    return ImageFont.truetype(path, size)


def fit(d, text, face, max_size, max_width, min_size=18):
    for size in range(max_size, min_size - 1, -1):
        f = font(face, size)
        l, _, r, _ = d.textbbox((0, 0), text, font=f)
        if r - l <= max_width:
            return f
    return font(face, min_size)


def wrap(d, text, fnt, max_width):
    """Word-wrap to max_width at a given font; never slice mid-word."""
    lines, cur = [], ""
    for word in text.split():
        cand = f"{cur} {word}".strip()
        if d.textlength(cand, font=fnt) <= max_width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def grain(im, opacity=13):
    noise = Image.effect_noise(im.size, 22).convert("L")
    noise = noise.point(lambda v: 255 if v > 255 - opacity else 0)
    return Image.composite(Image.new("RGB", im.size, "#000000"), im, noise)


def art_panel():
    """Placeholder product art when no source artwork is supplied."""
    w, h = int(S * 0.42), int(S * 0.56)
    im = Image.new("RGB", (w, h), P["paper"])
    d = ImageDraw.Draw(im)
    for x in range(0, w, 40):
        d.line([(x, 0), (x, h)], fill="#EDE5D2", width=1)
    for y in range(0, h, 40):
        d.line([(0, y), (w, y)], fill="#EDE5D2", width=1)
    d.rounded_rectangle([w * 0.2, h * 0.25, w * 0.8, h * 0.7], radius=24,
                        outline=P["cobalt"], width=8)
    d.line([(w * 0.32, h * 0.47), (w * 0.68, h * 0.47)], fill=P["gold"], width=10)
    return im


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else CONFIG["out"]
    art_path = sys.argv[2] if len(sys.argv) > 2 else CONFIG["art"]

    im = Image.new("RGB", (S, S), P["parchment"])
    d = ImageDraw.Draw(im)

    band = int(S * 0.115)
    d.rectangle([0, 0, S, band], fill=P["ink"])
    d.rectangle([0, S - band, S, S], fill=P["ink"])

    f = fit(d, CONFIG["kicker_top"], F["sansb"], 46, S * 0.7)
    d.text((S / 2, band / 2), CONFIG["kicker_top"], font=f, fill=P["gold_light"], anchor="mm")
    d.line([(S * 0.2, band * 0.82), (S * 0.8, band * 0.82)], fill=P["gold"], width=3)

    lx = int(S * 0.065)
    lw = int(S * 0.44)
    y = int(S * 0.185)
    d.text((lx, y), CONFIG["kicker"], font=font(F["sansb"], 40), fill=P["gold"])
    y += 62
    for text, kind in CONFIG["title_lines"]:
        face = F["serifb"] if kind == "serif" else F["sansb"]
        fill = P["ink"] if kind == "serif" else P["cobalt"]
        fnt = fit(d, text, face, 128, lw)
        d.text((lx, y), text, font=fnt, fill=fill)
        y += int(fnt.size * 1.16)
    d.line([(lx, y + 8), (lx + int(lw * 0.85), y + 8)], fill=P["gold"], width=6)
    y += 40
    f = fit(d, CONFIG["promise"], F["sansb"], 52, lw)
    for line in wrap(d, CONFIG["promise"], f, lw):
        d.text((lx, y), line, font=f, fill=P["ink"])
        y += int(f.size * 1.3)
    y += 12
    for s in CONFIG["support"]:
        d.text((lx, y), s, font=font(F["sans"], 36), fill=P["muted"])
        y += 48

    y += int(S * 0.03)
    pf = fit(d, CONFIG["pill"], F["sansb"], 40, lw - 90)
    pw = min(lw, d.textlength(CONFIG["pill"], font=pf) + 90)
    d.rounded_rectangle([lx, y, lx + pw, y + 96], radius=48, fill=P["ink"])
    d.text((lx + pw / 2, y + 48), CONFIG["pill"], font=pf, fill=P["white"], anchor="mm")
    y += 130
    d.text((lx, y), CONFIG["byline"], font=font(F["sansb"], 40), fill=P["cobalt"])

    aw, ah = int(S * 0.42), int(S * 0.56)
    ax, ay = int(S * 0.545), int(S * 0.175)
    if art_path and os.path.isfile(art_path):
        src = Image.open(art_path).convert("RGB")
        sf = max(aw / src.width, ah / src.height)
        src = src.resize((int(src.width * sf), int(src.height * sf)), Image.LANCZOS)
        cx, cy = (src.width - aw) // 2, (src.height - ah) // 2
        src = src.crop((cx, cy, cx + aw, cy + ah))
    else:
        src = art_panel()
    card = Image.new("RGB", (aw + 80, ah + 80), P["paper"])
    card.paste(src, (40, 40))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([8, 8, aw + 72, ah + 72], radius=36, outline=P["cobalt"], width=8)
    shadow = Image.new("RGBA", (aw + 140, ah + 140), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([40, 48, aw + 100, ah + 108], radius=36,
                                             fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    im.paste(shadow, (ax - 70, ay - 70), shadow)
    im.paste(card, (ax - 40, ay - 40))
    d = ImageDraw.Draw(im)

    ff = fit(d, CONFIG["features"], F["sansb"], 42, S * 0.8)
    d.text((S / 2, S - band * 0.42), CONFIG["features"], font=ff, fill=P["gold_light"], anchor="mm")
    d.text((S / 2, S - band * 0.16), CONFIG["reassure"], font=font(F["sans"], 32),
           fill=P["white"], anchor="mm")

    im = grain(im)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    im.save(out)
    print(f"cover: {out} ({os.path.getsize(out)//1024} KB, {S}x{S})")


if __name__ == "__main__":
    main()
