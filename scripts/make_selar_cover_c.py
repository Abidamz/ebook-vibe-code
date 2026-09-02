#!/usr/bin/env python3
"""Create the third, wide-artwork Selar cover variation.

Usage:
    .venv/bin/python scripts/make_selar_cover_c.py

Output:
    assets/img/selar-cover-c.png
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "img"
SOURCE_ART = ASSET_DIR / "cover-art.png"
OUTPUT = ASSET_DIR / "selar-cover-c.png"

SIZE = 1600
NAVY = "#17130D"
INK = "#201B14"
PARCHMENT = "#F7F1E3"
PAPER = "#FFF9E9"
COBALT = "#1D4ED8"
COBALT_DARK = "#173B9F"
GOLD = "#D97706"
GOLD_LIGHT = "#F7C65D"
MUTED = "#766A56"
WHITE = "#FFFFFF"

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SANS = FONT_DIR / "DejaVuSans.ttf"
SANS_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
SERIF_BOLD = FONT_DIR / "DejaVuSerif-Bold.ttf"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.exists():
        raise FileNotFoundError(f"Required font was not found: {path}")
    return ImageFont.truetype(str(path), size)


def fit_font(draw: ImageDraw.ImageDraw, text: str, face: Path, max_size: int,
             max_width: int, min_size: int = 18) -> ImageFont.FreeTypeFont:
    for size in range(max_size, min_size - 1, -1):
        candidate = font(face, size)
        bbox = draw.textbbox((0, 0), text, font=candidate)
        if bbox[2] - bbox[0] <= max_width:
            return candidate
    return font(face, min_size)


def grain(image: Image.Image) -> Image.Image:
    noise = Image.effect_noise(image.size, 22).convert("L")
    noise = ImageOps.colorize(noise, black="#796747", white="#FFFBEF").convert("RGBA")
    noise.putalpha(11)
    return Image.alpha_composite(image.convert("RGBA"), noise).convert("RGB")


def wide_art_panel(source: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Crop the source's notebook illustration into a landscape, listing-ready panel."""
    # Removing the source's large empty upper area keeps the illustration legible in a square thumbnail.
    source = source.convert("RGB").crop((0, 270, source.width, source.height))
    art = ImageOps.fit(source, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    panel = Image.new("RGBA", (size[0] + 28, size[1] + 28), PAPER)
    panel.paste(art, (14, 14))
    mask = Image.new("L", panel.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, panel.width - 1, panel.height - 1), radius=34, fill=255)
    panel.putalpha(mask)
    return panel


def add_shadow(canvas: Image.Image, panel: Image.Image, xy: tuple[int, int]) -> None:
    x, y = xy
    mask = Image.new("L", canvas.size, 0)
    mask.paste(panel.getchannel("A"), (x + 18, y + 23))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(20)))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(panel, xy)


def pill(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str) -> None:
    draw.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=GOLD)
    draw.text(((box[0] + box[2]) // 2, (box[1] + box[3]) // 2 + 2), text,
              font=font(SANS_BOLD, 25), fill=NAVY, anchor="mm")


def build(source: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", (SIZE, SIZE), COBALT)
    draw = ImageDraw.Draw(canvas)

    # A paper sheet on cobalt gives this option a brighter, editorial profile than covers A and B.
    draw.rounded_rectangle((64, 58, 1536, 1542), radius=54, fill=PARCHMENT)
    draw.rectangle((64, 58, 1536, 157), fill=NAVY)
    draw.text((112, 107), "THE NO-HYPE BLUEPRINT", font=font(SANS_BOLD, 27), fill=GOLD_LIGHT, anchor="lm")
    draw.text((1488, 107), "DIGITAL PRODUCT EBOOK", font=font(SANS_BOLD, 24), fill=PARCHMENT, anchor="rm")

    # Crisp product title.
    draw.text((800, 253), "THE", font=font(SANS_BOLD, 34), fill=GOLD, anchor="mm")
    money = "₦5K–₦10K"
    draw.text((800, 349), money, font=fit_font(draw, money, SERIF_BOLD, 116, 1210), fill=INK, anchor="mm")
    draw.text((800, 475), "DIGITAL PRODUCT", font=fit_font(draw, "DIGITAL PRODUCT", SANS_BOLD, 90, 1210),
              fill=COBALT_DARK, anchor="mm")
    draw.text((800, 590), "PLAYBOOK", font=fit_font(draw, "PLAYBOOK", SERIF_BOLD, 115, 1210), fill=INK, anchor="mm")
    draw.line((323, 684, 1277, 684), fill=GOLD, width=8)
    draw.text((800, 744), "Make ₦5,000–₦10,000 daily selling digital products.",
              font=font(SANS_BOLD, 32), fill=INK, anchor="mm")
    draw.text((800, 794), "A practical, phone-friendly system for beginners in Nigeria.",
              font=font(SANS, 24), fill=MUTED, anchor="mm")

    # The landscape crop puts the notebook, naira coin, phone, and growth arrow front and centre.
    panel = wide_art_panel(source, (1268, 474))
    panel_x, panel_y = 166, 859
    add_shadow(canvas, panel, (panel_x, panel_y))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((panel_x - 3, panel_y - 3, panel_x + panel.width + 2, panel_y + panel.height + 2),
                           radius=37, outline=COBALT, width=5)

    pill(draw, (555, 1380, 1045, 1462), "₦3,500  ·  INSTANT DOWNLOAD")
    draw.text((800, 1505), "by Oluwadarasimi Oluwadamilola", font=font(SANS_BOLD, 24), fill=NAVY, anchor="mm")
    return grain(canvas)


def main() -> None:
    if not SOURCE_ART.exists():
        raise FileNotFoundError(f"Source artwork was not found: {SOURCE_ART}")
    with Image.open(SOURCE_ART) as source:
        source.load()
        image = build(source)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUTPUT, "PNG", optimize=True)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
