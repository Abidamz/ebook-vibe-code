#!/usr/bin/env python3
"""Create the primary and alternate square cover images for the Selar listing.

Usage:
    .venv/bin/python scripts/make_selar_cover.py

Outputs:
    assets/img/selar-cover.png
    assets/img/selar-cover-b.png

The source artwork remains in ``assets/img/cover-art.png``. Keeping this
composition in code makes it easy to regenerate a crisp listing image whenever
the price, title, or author line changes.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "img"
SOURCE_ART = ASSET_DIR / "cover-art.png"
PRIMARY_OUTPUT = ASSET_DIR / "selar-cover.png"
ALTERNATE_OUTPUT = ASSET_DIR / "selar-cover-b.png"

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
SERIF = FONT_DIR / "DejaVuSerif.ttf"
SERIF_BOLD = FONT_DIR / "DejaVuSerif-Bold.ttf"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    """Load a bundled system font with a clear failure if the build host lacks it."""
    if not path.exists():
        raise FileNotFoundError(f"Required font was not found: {path}")
    return ImageFont.truetype(str(path), size)


def fit_font(draw: ImageDraw.ImageDraw, text: str, face: Path, max_size: int,
             max_width: int, min_size: int = 18) -> ImageFont.FreeTypeFont:
    """Return the largest font size that keeps a single text line within max_width."""
    for size in range(max_size, min_size - 1, -1):
        candidate = font(face, size)
        left, _, right, _ = draw.textbbox((0, 0), text, font=candidate)
        if right - left <= max_width:
            return candidate
    return font(face, min_size)


def center_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                face: Path, size: int, fill: str, *, anchor: str = "mm") -> None:
    draw.text(xy, text, font=font(face, size), fill=fill, anchor=anchor)


def add_grain(image: Image.Image, opacity: int = 13) -> Image.Image:
    """Add restrained paper grain so flat colour blocks match the source artwork."""
    noise = Image.effect_noise(image.size, 22).convert("L")
    noise = ImageOps.colorize(noise, black="#7B6847", white="#FFFBEF").convert("RGBA")
    noise.putalpha(opacity)
    return Image.alpha_composite(image.convert("RGBA"), noise).convert("RGB")


def art_on_card(source: Image.Image, card_size: tuple[int, int],
                border: int = 14, radius: int = 32) -> Image.Image:
    """Place the portrait source artwork on a framed, rounded card without distortion."""
    card_w, card_h = card_size
    card = Image.new("RGBA", (card_w, card_h), PAPER)
    target_w = card_w - 2 * border
    target_h = card_h - 2 * border
    contained = ImageOps.contain(source.convert("RGB"), (target_w, target_h), Image.Resampling.LANCZOS)
    x = (card_w - contained.width) // 2
    y = (card_h - contained.height) // 2
    card.paste(contained, (x, y))

    rounded = Image.new("L", (card_w, card_h), 0)
    ImageDraw.Draw(rounded).rounded_rectangle(
        (0, 0, card_w - 1, card_h - 1), radius=radius, fill=255
    )
    card.putalpha(rounded)
    return card


def add_card_shadow(canvas: Image.Image, position: tuple[int, int], card: Image.Image,
                    shadow_offset: tuple[int, int] = (18, 25)) -> None:
    """Paste a softly lifted card at position."""
    x, y = position
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    alpha = card.getchannel("A")
    shadow_mask = Image.new("L", canvas.size, 0)
    shadow_mask.paste(alpha, (x + shadow_offset[0], y + shadow_offset[1]))
    shadow.putalpha(shadow_mask.filter(ImageFilter.GaussianBlur(20)))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(card, position)


def pill(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str,
         fill: str, text_fill: str, face: Path, text_size: int) -> None:
    draw.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=fill)
    x = (box[0] + box[2]) // 2
    y = (box[1] + box[3]) // 2 + 1
    draw.text((x, y), text, font=font(face, text_size), fill=text_fill, anchor="mm")


def build_primary(source: Image.Image) -> Image.Image:
    """Warm, editorial primary cover — the recommended Selar upload."""
    canvas = Image.new("RGBA", (SIZE, SIZE), PARCHMENT)
    draw = ImageDraw.Draw(canvas)

    # Brand header and subtle rule.
    draw.rectangle((0, 0, SIZE, 184), fill=NAVY)
    center_text(draw, (SIZE // 2, 88), "THE NO-HYPE BLUEPRINT", SANS_BOLD, 34, GOLD_LIGHT)
    draw.line((310, 137, 1290, 137), fill="#776035", width=2)

    # Left-side sales copy.
    left = 102
    draw.text((left, 280), "THE", font=font(SANS_BOLD, 34), fill=GOLD)
    title_1 = "₦5K–₦10K"
    draw.text((left, 323), title_1,
              font=fit_font(draw, title_1, SERIF_BOLD, 112, 690), fill=INK)
    draw.text((left, 456), "DIGITAL PRODUCT", font=fit_font(draw, "DIGITAL PRODUCT", SANS_BOLD, 76, 690),
              fill=COBALT)
    draw.text((left, 550), "PLAYBOOK", font=fit_font(draw, "PLAYBOOK", SERIF_BOLD, 111, 690), fill=INK)
    draw.line((left, 685, 716, 685), fill=GOLD, width=7)

    draw.multiline_text(
        (left, 733),
        "Make ₦5,000–₦10,000 daily\nselling digital products.",
        font=font(SANS_BOLD, 39), fill=INK, spacing=12,
    )
    draw.multiline_text(
        (left, 870),
        "Create. Sell. Scale.\nA practical beginner roadmap for Nigeria.",
        font=font(SANS, 26), fill=MUTED, spacing=10,
    )
    pill(draw, (left, 1052, 628, 1136), "INSTANT DOWNLOAD  ·  ₦3,500", NAVY, PAPER, SANS_BOLD, 23)
    draw.text((left, 1182), "by Oluwadarasimi Oluwadamilola", font=font(SANS_BOLD, 25), fill=COBALT_DARK)

    # A full-length framed version of the existing book artwork adds a tangible product cue.
    card = art_on_card(source, (560, 1014), border=16, radius=32)
    card_x, card_y = 852, 267
    add_card_shadow(canvas, (card_x, card_y), card)
    outline = ImageDraw.Draw(canvas)
    outline.rounded_rectangle((card_x - 2, card_y - 2, card_x + 561, card_y + 1015),
                              radius=34, outline=COBALT, width=5)

    # Footer gives the listing image a crisp, recognizable edge at thumbnail scale.
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 1370, SIZE, SIZE), fill=NAVY)
    center_text(draw, (SIZE // 2, 1452), "10 CHAPTERS  ·  STEP-BY-STEP  ·  PHONE-FRIENDLY", SANS_BOLD, 24, GOLD_LIGHT)
    center_text(draw, (SIZE // 2, 1520), "Digital products. Real work. A system you can follow.", SANS, 23, PAPER)
    return add_grain(canvas)


def build_alternate(source: Image.Image) -> Image.Image:
    """High-contrast navy/cobalt alternate cover for listing A/B selection."""
    canvas = Image.new("RGBA", (SIZE, SIZE), NAVY)
    draw = ImageDraw.Draw(canvas)

    # Branded geometry behind the product art.
    draw.ellipse((-330, -455, 1040, 915), fill=COBALT_DARK)
    draw.ellipse((1100, 968, 1760, 1628), fill="#8C470B")
    draw.rectangle((0, 0, SIZE, 22), fill=GOLD)
    draw.line((86, 184, 1514, 184), fill="#605535", width=2)
    draw.text((90, 100), "THE NO-HYPE BLUEPRINT", font=font(SANS_BOLD, 30), fill=GOLD_LIGHT)
    draw.text((1510, 100), "EBOOK", font=font(SANS_BOLD, 30), fill=PARCHMENT, anchor="ra")

    # Artwork card on the left.
    card = art_on_card(source, (652, 1052), border=18, radius=38)
    add_card_shadow(canvas, (86, 290), card, shadow_offset=(20, 30))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((84, 288, 739, 1343), radius=40, outline=GOLD_LIGHT, width=5)

    # Direct, easily readable title on the right.
    x = 816
    draw.text((x, 337), "MAKE", font=font(SANS_BOLD, 37), fill=GOLD_LIGHT)
    money = "₦5K–₦10K"
    draw.text((x, 389), money, font=fit_font(draw, money, SERIF_BOLD, 98, 688), fill=WHITE)
    draw.text((x, 507), "DAILY", font=font(SERIF_BOLD, 112), fill=GOLD_LIGHT)
    draw.line((x, 649, 1486, 649), fill=COBALT, width=8)
    draw.text((x, 706), "THE DIGITAL", font=font(SANS_BOLD, 67), fill=WHITE)
    draw.text((x, 791), "PRODUCT", font=font(SANS_BOLD, 82), fill=WHITE)
    draw.text((x, 889), "PLAYBOOK", font=font(SERIF_BOLD, 83), fill=COBALT)
    draw.multiline_text(
        (x, 1035),
        "A clear, practical guide to creating\nand selling digital products in Nigeria.",
        font=font(SANS, 27), fill="#DDD2BC", spacing=12,
    )
    pill(draw, (x, 1193, 1452, 1275), "₦3,500  ·  INSTANT DOWNLOAD", GOLD, NAVY, SANS_BOLD, 22)
    draw.text((x, 1324), "Oluwadarasimi Oluwadamilola", font=font(SANS_BOLD, 24), fill=GOLD_LIGHT)

    draw.rectangle((0, 1450, SIZE, SIZE), fill="#100D09")
    center_text(draw, (SIZE // 2, 1529), "CREATE  ·  SELL  ·  SCALE", SANS_BOLD, 31, PARCHMENT)
    return add_grain(canvas, opacity=10)


def save(image: Image.Image, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, "PNG", optimize=True)
    print(f"Wrote {output.relative_to(ROOT)} ({output.stat().st_size / 1024:.0f} KB)")


def main() -> None:
    if not SOURCE_ART.exists():
        raise FileNotFoundError(f"Source artwork was not found: {SOURCE_ART}")
    with Image.open(SOURCE_ART) as source:
        source.load()
        save(build_primary(source), PRIMARY_OUTPUT)
        save(build_alternate(source), ALTERNATE_OUTPUT)


if __name__ == "__main__":
    main()
