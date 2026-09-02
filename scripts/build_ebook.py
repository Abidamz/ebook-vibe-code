#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds "Digital Product Cash Machine" ebook PDFs (A4, portrait).
Run:  .venv/bin/python scripts/build_ebook.py --all
Outputs:
  delivery/digital-product-cash-machine.pdf   (paid book - local only, gitignored, upload to Selar)
  assets/ebook/free-sample-chapter1.pdf       (free sample - published on the site)
"""
import os
import re
from fpdf import FPDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELIVERY_DIR = os.path.join(ROOT, "delivery")
OUT = os.path.join(DELIVERY_DIR, "digital-product-cash-machine.pdf")
IMG = os.path.join(ROOT, "assets", "img")
OPT = os.path.join(ROOT, "assets", "img", "opt")
LIVE_SITE_URL = "https://how-to-make-5k-10k-daily.pages.dev/"
DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DJB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ── strip emoji / unsupported glyphs (DejaVu has no colour emoji) ──
_EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\uFE0F\u26EA\u2705\u274C\u26A0\u26A1\u2611]")
_REPLACEMENTS = {
    "❤": "♥", "❌": "✗", "⚠": "!", "⚡": "", "☐": "[ ]",
    "…": "...", "—": "—",
}


def clean(text):
    for k, v in _REPLACEMENTS.items():
        text = text.replace(k, v)
    text = _EMOJI_RE.sub("", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def opt_image(name, max_w=1100, quality=82):
    """Return a compressed JPEG path for embedding in the PDF."""
    from PIL import Image
    src = os.path.join(IMG, name)
    out = os.path.join(OPT, name.replace(".png", ".jpg"))
    os.makedirs(OPT, exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(out, quality=quality, optimize=True)
    return out

NAVY = (28, 24, 18)       # ink
GOLD = (180, 83, 9)       # amber
GOLD_D = (146, 64, 14)    # dark amber
GREEN = (22, 101, 52)
GREEN_L = (236, 246, 236)
AMBER_L = (249, 240, 214)
MUTED = (133, 117, 95)
LIGHT = (247, 241, 227)
BORDER = (214, 205, 186)
COBALT = (29, 78, 216)
COBALT_D = (30, 58, 138)

PAGE_W, PAGE_H = 210, 297
M = 18          # margin mm
W = PAGE_W - 2 * M  # 174 mm text width
LH = 6.3        # body line height


def prepare_cover_art():
    """Bake semi-transparent parchment bands into the cover art so title text stays readable."""
    from PIL import Image, ImageDraw
    src = os.path.join(IMG, "cover-art.png")
    out = os.path.join(IMG, "cover-bands.png")
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle([0, int(h * 0.08), w, int(h * 0.30)], fill=(247, 241, 227, 186))
    d.rectangle([0, int(h * 0.68), w, int(h * 0.93)], fill=(247, 241, 227, 186))
    Image.alpha_composite(im, overlay).convert("RGB").save(out, quality=92)
    return opt_image("cover-bands.png", max_w=896, quality=86)


class Book(FPDF):

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("DJ", "", DJ)
        self.add_font("DJ", "B", DJB)
        self.set_margins(M, 18, M)
        self.chapter_pages = {}

    def footer(self):
        if self.page_no() <= 1:
            return
        self.set_y(-14)
        self.set_font("DJ", "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 5, "The ₦5K–₦10K Digital Product Playbook  ·  © 2026 Oluwadarasimi Oluwadamilola",
                  new_x="LMARGIN", new_y="NEXT", align="L")
        self.cell(0, 5, f"Page {self.page_no()}", align="R")

    # ── helpers ──────────────────────────────────────────────
    def para(self, text, size=10.8, lh=6.3, space=3.2):
        text = clean(text)
        self.set_font("DJ", "", size)
        self.set_text_color(30, 41, 59)
        self.multi_cell(W, lh, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(space)

    def bullets(self, items, size=10.8, lh=6.2, marker="✓", mcolor=GREEN):
        for it in items:
            it = clean(it)
            y = self.get_y()
            self.set_font("DJ", "B", size - 1)
            self.set_text_color(*mcolor)
            self.set_xy(M, y)
            self.cell(7, lh, marker)
            self.set_font("DJ", "", size)
            self.set_text_color(30, 41, 59)
            self.set_xy(M + 7, y)
            self.multi_cell(W - 7, lh, it, new_x="LMARGIN", new_y="NEXT")
            self.ln(1.2)
        self.ln(2)

    def chapter_header(self, num, title, subtitle=None):
        title, subtitle = clean(title), clean(subtitle) if subtitle else None
        if self.get_y() > 235:
            self.add_page()
        self.set_font("DJ", "B", 11)
        self.set_text_color(*GOLD_D)
        self.cell(0, 8, f"CHAPTER {num}", new_x="LMARGIN", new_y="NEXT")
        self.set_font("DJ", "B", 21)
        self.set_text_color(*NAVY)
        self.multi_cell(W, 10, title, new_x="LMARGIN", new_y="NEXT")
        if subtitle:
            self.set_font("DJ", "", 11)
            self.set_text_color(*MUTED)
            self.multi_cell(W, 6, subtitle, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        y = self.get_y()
        self.set_draw_color(*GOLD)
        self.set_line_width(1.1)
        self.line(M, y, PAGE_W - M, y)
        self.ln(7)
        self.chapter_pages[num] = self.page_no()

    def h2(self, text):
        text = clean(text)
        if self.get_y() > 250:
            self.add_page()
        self.ln(2)
        self.set_font("DJ", "B", 13.5)
        self.set_text_color(*NAVY)
        self.multi_cell(W, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2.5)

    def h3(self, text):
        text = clean(text)
        self.set_font("DJ", "B", 11.5)
        self.set_text_color(*GOLD_D)
        self.multi_cell(W, 6.5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def callout(self, text, label=None, kind="amber", link=None):
        text, label = clean(text), clean(label) if label else None
        bg = AMBER_L if kind == "amber" else GREEN_L
        border = GOLD if kind == "amber" else GREEN
        self.ln(1)
        lines = self._estimate_lines(text, kind == "amber")
        h = lines * 6.0 + 10 + (6 if label else 0)
        y = self.get_y()
        if y + h > PAGE_H - 20:
            self.add_page()
            y = self.get_y()
        self.set_fill_color(*bg)
        self.set_draw_color(*border)
        self.set_line_width(0.5)
        self.rect(M, y, W, h, style="FD")
        self.set_xy(M + 5, y + 4)
        if label:
            self.set_font("DJ", "B", 9.5)
            self.set_text_color(*border)
            self.cell(W - 10, 5.5, label, new_x="LMARGIN", new_y="NEXT")
            self.set_xy(M + 5, self.get_y() + 1)
        self.set_font("DJ", "", 10.3)
        self.set_text_color(60, 50, 20)
        self.multi_cell(W - 10, 5.9, text, new_x="LMARGIN", new_y="NEXT", link=link)
        self.set_y(y + h + 5)

    def task_box(self, text):
        text = clean(text)
        lines = self._estimate_lines(text, True, 10.3)
        h = lines * 6.0 + 14
        y = self.get_y()
        if y + h > PAGE_H - 20:
            self.add_page()
            y = self.get_y()
        self.set_fill_color(*NAVY)
        self.rect(M, y, W, h, style="F")
        self.set_draw_color(*GOLD)
        self.set_line_width(0.6)
        self.rect(M, y, 2.4, h, style="F")
        self.set_xy(M + 7, y + 4)
        self.set_font("DJ", "B", 10)
        self.set_text_color(*GOLD)
        self.cell(0, 5.5, "YOUR TASK TODAY", new_x="LMARGIN", new_y="NEXT")
        self.set_xy(M + 7, self.get_y() + 1.5)
        self.set_font("DJ", "", 10.3)
        self.set_text_color(*LIGHT)
        self.multi_cell(W - 14, 5.9, text, new_x="LMARGIN", new_y="NEXT")
        self.set_y(y + h + 5)

    def references(self, items, note=None):
        """Sources & references box at the end of each chapter (clickable X/Twitter links)."""
        if self.get_y() > 235:
            self.add_page()
        self.ln(1)
        self.set_font("DJ", "B", 9)
        self.set_text_color(*GOLD_D)
        self.cell(0, 5.5, "SOURCES & REFERENCES FOR THIS CHAPTER", new_x="LMARGIN", new_y="NEXT")
        self.set_font("DJ", "", 8.6)
        self.set_text_color(*MUTED)
        for label, url in items:
            self.set_font("DJ", "", 8.6)
            self.set_text_color(71, 85, 105)
            self.multi_cell(W, 5.2, f"• {label}:", new_x="LMARGIN", new_y="NEXT")
            self.set_font("DJ", "U", 8.6)
            self.set_text_color(37, 99, 235)
            self.multi_cell(W, 5.2, "   " + url, new_x="LMARGIN", new_y="NEXT", link=url)
        if note:
            self.ln(0.5)
            self.set_text_color(100, 116, 139)
            self.set_font("DJ", "", 8.6)
            self.multi_cell(W, 5.2, note, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        y = self.get_y()
        self.set_draw_color(*BORDER)
        self.set_line_width(0.3)
        self.line(M, y, PAGE_W - M, y)
        self.ln(4)

    def photo(self, path, caption=None, width=140):
        if caption:
            caption = clean(caption)
        if self.get_y() > 210:
            self.add_page()
        x = (PAGE_W - width) / 2
        h = width * 768 / 1408
        self.image(path, x=x, y=self.get_y(), w=width)
        self.set_y(self.get_y() + h + 1.5)
        if caption:
            self.set_font("DJ", "", 8.8)
            self.set_text_color(*MUTED)
            self.multi_cell(W, 5, caption, new_x="LMARGIN", new_y="NEXT", align="C")
            self.ln(4)
        else:
            self.ln(4)

    def _estimate_lines(self, text, gold_border=False, size=10.3):
        # rough estimator: chars per line ≈ width_mm / (size_pt * 0.5)
        cpl = max(10, int(W / (size * 0.5)))
        import math
        return max(1, math.ceil(len(text) / cpl))

    def page_gutter(self):
        self.add_page()


def build():
    pdf = Book()

    # ─────────────── COVER ───────────────
    cover_with_bands = prepare_cover_art()
    pdf.add_page()
    pdf.set_margins(0, 0, 0)
    img_h = PAGE_W * 1200 / 896
    pdf.image(cover_with_bands, x=0, y=(PAGE_H - img_h) / 2, w=PAGE_W)
    pdf.set_font("DJ", "B", 11)
    pdf.set_text_color(*COBALT)
    pdf.set_xy(0, 40)
    pdf.cell(PAGE_W, 8, "THE NO-HYPE BLUEPRINT", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 24)
    pdf.set_text_color(*NAVY)
    pdf.cell(PAGE_W, 11, "THE ₦5K–₦10K", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 26)
    pdf.set_text_color(*COBALT)
    pdf.cell(PAGE_W, 12, "DIGITAL PRODUCT", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 28)
    pdf.set_text_color(*GOLD)
    pdf.cell(PAGE_W, 12, "PLAYBOOK", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "", 11)
    pdf.set_text_color(75, 66, 51)
    pdf.cell(PAGE_W, 9, "Make ₦5,000 – ₦10,000 Daily Selling Digital Products", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 10)
    pdf.set_text_color(*NAVY)
    pdf.ln(2)
    pdf.cell(PAGE_W, 8, "10 CHAPTERS  ·  30-DAY ACTION PLAN  ·  PRO TARGETING BONUS", align="C", new_x="LMARGIN", new_y="NEXT")
    # author + price band (bottom)
    pdf.set_font("DJ", "B", 12)
    pdf.set_text_color(*COBALT_D)
    pdf.set_xy(0, 222)
    pdf.cell(PAGE_W, 8, "BY OLUWADARASIMI OLUWADAMILOLA", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 18)
    pdf.set_text_color(*GOLD)
    pdf.cell(PAGE_W, 10, "₦3,500   (was ₦10,000)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "", 9.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(PAGE_W, 7, "Instant download · Read on any device", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_margins(M, 18, M)

    # ─────────────── TITLE PAGE ───────────────
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("DJ", "B", 23)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(W, 12, "THE ₦5K–₦10K DIGITAL PRODUCT PLAYBOOK", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(3)
    pdf.set_font("DJ", "", 13.5)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(W, 8, "The No-Hype Blueprint to Make ₦5,000 – ₦10,000 Daily\nSelling Digital Products in Nigeria",
                   new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(14)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.8)
    y = pdf.get_y()
    pdf.line(M + 55, y, PAGE_W - M - 55, y)
    pdf.ln(16)
    pdf.set_font("DJ", "", 12)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(W, 8, "by  Oluwadarasimi Oluwadamilola", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(18)
    pdf.set_font("DJ", "B", 11)
    pdf.set_text_color(*GOLD_D)
    pdf.multi_cell(W, 7, "10 Chapters  ·  30-Day Action Plan  ·  Tracking Sheets  ·  Pro Targeting Bonus",
                   new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("DJ", "", 11)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(W, 7, "Price: ₦3,500 (Launch)   ·   One-time payment   ·   Instant download",
                   new_x="LMARGIN", new_y="NEXT", align="C")

    # ─────────────── COPYRIGHT / CREDITS ───────────────
    pdf.add_page()
    pdf.ln(10)
    pdf.h2("Copyright & Credits")
    pdf.para("© 2026 Oluwadarasimi Oluwadamilola. All rights reserved. This ebook may not be reproduced, "
             "redistributed, or resold without the author's written permission. You may print one personal copy "
             "for your own use.")
    pdf.para("This book distills a practical business system that is currently working in the Nigerian and African "
             "digital-product space. The core process (create product → raise ₦30,000 with talking flyers → run "
             "Facebook ads → rinse and repeat), the pro-geo-targeting tips, the digital-product system checklist, "
             "and the Reddit content-engine method are inspired by free public educational threads by @iamrichygold, "
             "@egbokavictory_ and @dotsokt on X (Twitter), expanded and re-written with additional actionable detail, "
             "worksheets, and a 30-day plan. Full links are listed at the end of each chapter and in the appendix.")
    pdf.para("While every effort has been made to keep the information accurate and up to date, results are never "
             "guaranteed. Your income depends on your effort, consistency, and market conditions. This ebook is "
             "for educational purposes only and is not financial advice. Ad platforms (including Meta) can change "
             "their policies at any time — always follow the platform's current advertising guidelines.")

    # ─────────────── TOC ───────────────
    pdf.add_page()
    pdf.ln(8)
    pdf.set_font("DJ", "B", 22)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "What's Inside", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    y = pdf.get_y()
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.1)
    pdf.line(M, y, PAGE_W - M, y)
    pdf.ln(7)
    toc = [
        ("01", "The ₦5K–₦10K Daily Promise — the honest math, who this is for, what you need"),
        ("02", "Digital Products 101 — what sells, why it sells, how to pick your niche"),
        ("03", "Step 1: Create Your First Digital Product — the 7-step creation process"),
        ("04", "Shortcut: Resell Ready-Made Products (PLR) — sell without creating from scratch"),
        ("05", "Step 2: Raise ₦30,000 With Talking Flyers — the pitch script & client hunt"),
        ("06", "Step 3: Facebook Ads That Sell — full system setup, Advantage+, creatives & the Reddit content engine"),
        ("07", "PRO BONUS: Target the Big Buyers — Kenya, Zambia, Ghana & Nigeria"),
        ("08", "Step 4: Rinse, Repeat & Scale — from ₦5K daily to bigger numbers"),
        ("09", "Your 30-Day Action Plan — day-by-day roadmap, routine & tracking sheet"),
        ("10", "FAQ & Final Words — answers to the questions everyone asks"),
        ("+", "Bonus Worksheets — pitch script, checklists & daily tracker"),
        ("+", "Appendix — Sources & Further Reading (all reference links)"),
    ]
    for num, txt in toc:
        y = pdf.get_y()
        pdf.set_font("DJ", "B", 12)
        pdf.set_text_color(*GOLD_D)
        pdf.set_xy(M, y)
        pdf.cell(10, 7, num)
        pdf.set_font("DJ", "", 11)
        pdf.set_text_color(30, 41, 59)
        pdf.set_xy(M + 12, y)
        pdf.multi_cell(W - 12, 6.6, txt, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)
    pdf.ln(6)
    pdf.set_font("DJ", "", 10)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(W, 6, "Pro tip: don't read this book like a novel. Read one chapter, do the task at the end, "
                         "then move to the next. Action is what turns pages into naira.",
                   new_x="LMARGIN", new_y="NEXT")

    # ══════════════════════════════════════════════════════════
    # CHAPTER 1
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.chapter_header("1", "The ₦5K–₦10K Daily Promise",
                       "An honest chapter about what this system is, what it isn't, and why ₦5,000–₦10,000 a day is a realistic goal.")
    pdf.para("Let's start with honesty, because that's the whole point of this book.")
    pdf.para("I am not going to promise you ₦100,000 or ₦200,000 every single day. Anyone who promises that on the "
             "internet is selling you dreams, not a system. What I am showing you is a simple process — the same "
             "process real digital-product sellers are using right now. If you put in the work, ₦5,000 – ₦10,000 "
             "daily is possible. And once you have that consistency, you scale.")
    pdf.callout("₦5,000/day × 30 days = ₦150,000 per month\n"
                "₦10,000/day × 30 days = ₦300,000 per month\n\n"
                "That's ₦150K–₦300K monthly — more than many Nigerian salaries — from a business you can run on your phone.",
                label="📊 THE MATH", kind="amber")
    pdf.h2("What this book IS")
    pdf.bullets([
        "A step-by-step system: create a product → raise ₦30,000 → run ads → scale",
        "Written for complete beginners — no tech skills, no followers, no big budget required",
        "Phone-friendly — everything in here works from a smartphone",
        "Honest — it shows you the work involved and never hides the effort",
    ])
    pdf.h2("What this book is NOT")
    pdf.bullets([
        "A get-rich-in-24-hours scheme",
        "An MLM, referral trick, or 'quick money' app",
        "A promise that money falls from the sky while you sleep on night one",
        "For lazy people — if you don't want to work, put this book down now",
    ], marker="✗", mcolor=(220, 38, 38))
    pdf.h2("Why digital products?")
    pdf.para("Digital products are things you create once and sell many times: a PDF guide, a template, an ebook, a "
             "checklist. There is no inventory to store, no shipping to pay, and delivery is instant. Every sale is "
             "almost pure profit. People across Africa buy them every single day — relationship guides, pregnancy and "
             "baby-care books, recipe books, finance templates, business checklists, church and event materials. "
             "The list is endless.")
    pdf.para("The best part? You don't need to be an expert or an influencer. You need a product people want, a way "
             "to put it in front of them, and a system to do it repeatedly. That is exactly what this book gives you.")
    pdf.h2("Who this book is for")
    pdf.para("Students who need an extra ₦50K–₦100K per month. 9–5 workers who want a side income that grows. "
             "Stay-at-home parents, NYSC members, fresh graduates, and anyone who has ever felt: 'I'm ready to work, "
             "I just don't know the steps.' If you can give 2–3 focused hours a day on your phone, this system is "
             "within your reach. The public threads that inspired this book were created for exactly these people — "
             "the creators said it plainly: 'We need to make money. Even an extra 50k or 100k per month can go a "
             "long way.'")
    pdf.para("This book is a full expansion of those free public threads: structured into chapters, with worksheets, "
             "checklists, a 30-day action plan, and clear source references at the end of every chapter — so you can "
             "watch the original content yourself and verify every claim before you invest a single naira.")
    pdf.task_box("Answer these three questions in your notes:\n"
                 "1) How much money do I need per month to change my life? (Be honest.)\n"
                 "2) What problem do people around me always complain about? (That's a product idea.)\n"
                 "3) What will I do with my first ₦5,000 day? (Visualize it — it matters.)")
    pdf.references([
        ("@iamrichygold — 'What I'll do to earn 5k–10k daily if I had to start over again'",
         "https://x.com/iamrichygold/status/2092708000414761351"),
        ("@iamrichygold — 'Let's talk about how to create a digital product' (series kick-off)",
         "https://x.com/iamrichygold/status/2084258170944270469"),
    ], note="Both are free public threads on X (Twitter). This ebook is an original, expanded guide built from them.")

    # ══════════════════════════════════════════════════════════
    # CHAPTER 2
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.chapter_header("2", "Digital Products 101",
                       "What digital products are, why they sell, and how to pick the niche that pays.")
    pdf.h2("What is a digital product?")
    pdf.para("A digital product is any product that is delivered electronically instead of physically. The customer "
             "pays, and within seconds the product lands in their inbox or WhatsApp. No printing, no delivery rider, "
             "no warehouse.")
    pdf.h2("Why people buy them (and why you should sell them)")
    pdf.bullets([
        "Infinite inventory — you can sell the same file to 1 customer or 10,000 customers",
        "Instant delivery — buyers love getting value immediately after paying",
        "Zero shipping cost — no courier fees eating your profit",
        "High margins — after creation, every sale is 80–100% profit",
        "Global buyers — with ads, you can sell to Kenya, Zambia, Ghana, and beyond",
    ])
    pdf.h2("Types of digital products that sell")
    pdf.bullets([
        "Ebooks & guides — relationship guides, baby care, recipes, money management",
        "Templates — CV/resume templates, budget trackers, Notion templates, flyer templates",
        "Checklists & printables — wedding planners, pregnancy trackers, prayer journals",
        "Presets — Lightroom presets for photos (huge with content creators)",
        "Video courses & tutorials — short, practical, solve one problem",
        "PLR/resell-rights packages — ready-made products you can rebrand and sell",
    ])
    pdf.h2("The hottest niches right now")
    pdf.para("The system in this book focuses on niches that are proven to spend money. Top sellers focus here first:")
    pdf.bullets([
        "❤️ Love, relationship & marriage — relationship advice guides, marriage prep, date ideas, 'first date' scripts. This is one of the best-selling niches on Meta right now.",
        "🤱 Mothers & nursing mothers — pregnancy guides, baby feeding schedules, newborn care, sleep training. New mothers buy constantly.",
        "💰 Money & finance — budgeting templates, saving challenges, side-hustle guides, crypto & investment basics for beginners.",
        "🏥 Health & wellness — natural remedies, fitness plans, meal plans, home remedy books.",
        "📈 Business & career — CV templates, interview guides, freelancing guides, small business checklists.",
        "⛪ Faith & lifestyle — prayer journals, devotional guides, event planning printables.",
    ])
    pdf.h2("How to pick YOUR niche")
    pdf.callout("Pick a niche where you can easily understand the customer's problem. You don't need to be a "
                "professional — you need to be one step ahead of your buyer. Ask: Do I know this problem? Can I "
                "research it in a weekend? Would this audience pay ₦1,000–₦5,000 for a simple solution?",
                label="THE 3-QUESTION NICHE TEST", kind="green")
    pdf.h2("The 10-minute mental model")
    pdf.para("If you have ten minutes, this is the whole business model: people are searching for answers to "
             "problems every single day. Create a simple PDF, ebook, template or video that solves ONE of those "
             "problems clearly. Put it somewhere buyers can pay (Selar, WhatsApp). Tell people about it with ads and "
             "content. Deliver it instantly. Repeat with the next problem. That's it — everything else in this book "
             "is detail on how to do each of those steps well.")
    pdf.para("When @iamrichygold was asked 'what are digital products and how can I create one to sell?', he "
             "answered in a 10-minute practical session, promising to make it simple enough for a five-year-old to "
             "follow, with no long stories and no long talks. That is the spirit of this chapter — and this whole "
             "book: practical steps you can act on the same day you read them.")
    pdf.task_box("Write down 3 product ideas using the format: NICHE + PROBLEM + FORMAT.\n"
                 "Example: Relationship + 'couples fight over money' + PDF guide with 20 practical rules.\n"
                 "Pick the one you'd be excited to create this week.")
    pdf.references([
        ("@iamrichygold — 'Digital products in 10 minutes: understand them and create one' (series part 1)",
         "https://x.com/iamrichygold/status/2084258170944270469"),
    ])

    # ══════════════════════════════════════════════════════════
    # CHAPTER 3
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.chapter_header("3", "Step 1: Create Your First Digital Product",
                       "Don't start with ads. Start with something ready to sell — a PDF, guide, or template.")
    pdf.photo(opt_image("step1-create.png"), "Create once. Sell forever. This is the foundation of the whole system.")
    pdf.para("The number-one mistake beginners make is starting with ads before they have anything to sell. Ads send "
             "traffic to a dead end — and you waste money. So Step 1 is simple: get a product ready. It doesn't need "
             "to be perfect. It needs to be useful, clear, and priced fairly.")
    pdf.h2("The 7-step product creation process")
    pdf.bullets([
        "1) Choose one specific problem — narrow beats broad. ('How to stop fighting about money' beats 'relationship advice'.)",
        "2) Outline 5–10 short sections that solve that problem step by step.",
        "3) Write 10–20 pages in simple language — as if talking to a friend. Short sentences. Real examples.",
        "4) Design it in Canva (free) — pick a clean template, add your headings and images.",
        "5) Create an attractive cover page — your product is judged by its cover first.",
        "6) Export to PDF and check it on your phone — it must look good on a phone.",
        "7) Add a final page: 'Thank you + what to do next' with your WhatsApp or store link.",
    ])
    pdf.h2("Tools you already have (all free)")
    pdf.bullets([
        "Canva (app or web) — design pages, covers, and flyer templates",
        "Google Docs / Word — write your content",
        "ChatGPT — help with outlines, titles, and first drafts (edit and personalize everything!)",
        "Selar or Paystack Storefront — host your product and collect payments automatically",
    ])
    pdf.h2("Pricing your product")
    pdf.bullets([
        "Entry product (first-time buyers): ₦1,000 – ₦2,000",
        "Standard guide (10–20 pages, nicely designed): ₦2,500 – ₦5,000",
        "Premium bundle (guide + templates + checklist): ₦7,000+",
        "Raise the price after reviews and sales — never lower it to chase buyers",
    ])
    pdf.h2("Where to sell it")
    pdf.para("The simplest way in Nigeria is Selar: create a free account, upload your PDF, set your price, and get a "
             "checkout link. Selar delivers the file to the buyer automatically and sends the money to your bank "
             "account. You can also sell directly on WhatsApp — receive payment, send the file, done. Many top sellers "
             "use both: Selar for ad traffic, WhatsApp for personal orders.")
    pdf.task_box("This week: create your first product. Use the free tools above. When it's done, upload it to Selar "
                 "and get your checkout link ready. A finished product in your hand changes everything.")

    # ══════════════════════════════════════════════════════════
    # CHAPTER 4
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.chapter_header("4", "Shortcut: Resell Ready-Made Products (PLR)",
                       "Don't want to create from scratch? Here's how to get ready-made digital products to resell.")
    pdf.para("Not everyone wants to write. And that's fine — there is a legal shortcut: products with resell or "
             "private-label rights (PLR). These are products the creator allows you to rebrand, edit, and sell as "
             "your own, keeping 100% of the profit.")
    pdf.h2("Where to get ready-made products")
    pdf.bullets([
        "PLR marketplaces — sites that sell resell-rights bundles (search 'PLR digital products')",
        "Creators selling resell rights — many Nigerian and foreign creators sell their ebooks with resell rights",
        "Your own old work — repurpose content you already created",
        "Always read the licence: some allow selling only, some allow rebranding too",
    ])
    pdf.h2("Where the 'sure plug' actually is")
    pdf.para("A question every beginner asks is: 'How can I get ready-made, valuable digital products for any niche "
             "to sell?' The honest answer: ready-made products you can resell legitimately are available once you "
             "know where to look. Here is the practical map:")
    pdf.bullets([
        "Resell-rights bundles from creators — buy a product once with resell rights and keep 100% of your sales",
        "PLR marketplaces — private-label-rights packs for almost every niche imaginable (health, relationships, finance, parenting)",
        "Digital marketplaces — study what already sells (guides, planners, templates) on global platforms for product ideas, then license or build your own version",
        "Google Trends research — see what people are searching for this week, then find or build a product around the rising trend",
    ])
    pdf.para("The original thread that introduced this shortcut put it plainly: not everyone has the time to do "
             "research or check Google Trends to find what's trending and build a PDF or video around it. So smart "
             "sellers plug into sources of ready-made products they can resell legitimately. This chapter is your "
             "map to those sources — with the safety rules that keep you out of trouble.")
    pdf.h2("Rules that keep you safe")
    pdf.bullets([
        "Check the resell rights before paying — no rights, no sale",
        "Rebrand it: your cover, your name, minor edits. Never sell a raw copy of someone's product",
        "Add value: rewrite sections in your own words, add extra pages, make it better",
        "Don't sell into a market the original owner already saturated — find a fresh angle or country",
    ], marker="⚠", mcolor=(217, 119, 6))
    pdf.callout("Important: quality is your reputation. A cheap, ugly product gets refunds and bad reviews. Even if "
                "you're reselling, spend time making it look premium — good cover, clean pages, clear language. Your "
                "buyers don't care where the product came from; they care whether it helps them.",
                label="🚨 QUALITY FIRST", kind="amber")
    pdf.task_box("Find ONE ready-made product you could resell (or one of your old pieces of content). Check its "
                 "resell rights. If allowed, plan the rebrand: new title, new cover, 2–3 pages of added value. That "
                 "will be your backup product while you build your own.")
    pdf.references([
        ("@iamrichygold — 'How to get ready-made valuable digital products to resell legitimately'",
         "https://x.com/iamrichygold/status/2084383065682375038"),
    ])

    # ══════════════════════════════════════════════════════════
    # CHAPTER 5
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.chapter_header("5", "Step 2: Raise ₦30,000 With Talking Flyers",
                       "You need seed money for ads. Here's the fastest honest way to get it — ₦5,000–₦10,000 per flyer.")
    pdf.photo(opt_image("step2-flyers.png"), "One talking flyer can pay ₦5,000–₦10,000. Five clients = your ad budget.")
    pdf.para("You need about ₦30,000 to run meaningful ads. Where does that money come from if you're broke? "
             "Talking flyers. A talking flyer is a short video advertisement for a business — pictures or video clips, "
             "a voiceover, text on screen, delivered to customers on WhatsApp and social media. Small online "
             "businesses around you pay ₦5,000–₦10,000 for one because it brings them customers.")
    pdf.h2("The math")
    pdf.callout("Charge ₦5,000 – ₦10,000 per talking flyer.\n5 clients × ₦6,000 = ₦30,000.\n\n"
                "That's your full ad budget — raised in days, not months.",
                label="💰 5 CLIENTS = ₦30,000", kind="green")
    pdf.h2("How to make a talking flyer (no experience needed)")
    pdf.bullets([
        "Collect the business's photos or short clips (they almost always have them)",
        "Add them to CapCut (free) with music and your voiceover",
        "Voiceover script: what they sell → why it's good → where to order (their WhatsApp)",
        "Keep it 30–60 seconds. Add text captions so it works on mute",
        "Practice once or twice — your first one doesn't need to be perfect",
    ])
    pdf.h2("Who to pitch")
    pdf.bullets([
        "Hair salons & barbershops, boutiques, restaurants, phone & gadget stores",
        "Event planners, small online brands on Instagram selling clothes, skin care, food",
        "Real estate agents, gyms, tutors, churches and event centres",
        "Anyone who advertises at all — they already know ads matter",
    ])
    pdf.h2("The pitch script (copy, edit, send)")
    pdf.callout("WhatsApp message:\n\n"
                "'Hello [Name], I noticed you sell [product/service] and you're doing well. I make short video ads "
                "('talking flyers') for businesses like yours — 30–60 seconds, with your photos, your voice or mine, "
                "and your WhatsApp number so customers can reach you directly. It costs ₦6,000 and takes 24 hours. "
                "Can I make one for you today? I'll show you a sample first.'\n\n"
                "Face-to-face: same message, shorter. Show one sample on your phone. Ask for the sale.",
                label="📋 THE SCRIPT", kind="amber")
    pdf.h2("Be shameless (the right way)")
    pdf.para("Don't hide. Walk into shops. Send WhatsApp messages. Post your samples on your status and social pages. "
             "Bill your friends and family — they know someone who owns a business. One of the most powerful lines "
             "you'll ever hear in this business: You can't be broke and shy at the same time. Rejection is part of "
             "the process — every no brings you closer to the yes that pays ₦6,000.")
    pdf.task_box("Today: make ONE sample talking flyer for a business you admire (you don't need their permission to "
                 "practice). Then message 10 businesses with the script. Track replies. Aim for 5 clients this week.")

    # ══════════════════════════════════════════════════════════
    # CHAPTER 6
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.chapter_header("6", "Step 3: Facebook Ads That Sell",
                       "Take your ₦30K, promote your digital product with Facebook Ads, and let the buyers come to you.")
    pdf.photo(opt_image("step3-ads.png"), "Advantage+ audience + wide targeting + a clean creative = sales.")
    pdf.para("This is where the system turns money into customers. You don't need followers — the ads put your "
             "product in front of people who are already interested in the problem you solve.")
    pdf.h2("Set up the campaign (simplified)")
    pdf.bullets([
        "Create a Facebook Page for your product (free) and a Business account at business.facebook.com",
        "Open Ads Manager → Create campaign → choose Sales (or Traffic while you're learning)",
        "Pick Advantage+ (Advantage+ audience) — Meta does the targeting for you",
        "Keep targeting WIDE — broad age and interest targeting wins for digital products",
        "Link your Selar checkout page as the destination and add the Meta pixel (Selar shows you how) so you can track sales",
    ])
    pdf.h2("The full system you need to set up (the 10K-daily checklist)")
    pdf.photo(opt_image("step5-system.png"), "Five connected pieces: accounts, page, store, pixel, product. Set them up once, reuse forever.")
    pdf.para("One of the clearest breakdowns in the source material (@egbokavictory_) lists exactly what you need to "
             "set up a digital-product system that makes at least ₦10K daily. Put these five pieces together once, "
             "in one afternoon:")
    pdf.bullets([
        "Facebook account + Instagram account — your personal identity for managing everything",
        "Facebook Page — the public face of your product; required for running ads and posting organic content",
        "Meta Business Suite / Business Manager — where your ad account, pixel and page live",
        "Selar store with your product uploaded — where the money lands and the file is delivered",
        "Meta pixel connected to Selar — so you can see exactly which ad produced each sale",
    ])
    pdf.para("Notice the order: set up the store and product BEFORE you touch ads. That way, every naira you spend "
             "points at something ready to buy — the same 'product first' principle from Chapter 3.")
    pdf.h2("The content engine: free traffic from Reddit Custom Feeds")
    pdf.photo(opt_image("step6-content.png"), "Curate proven viral ideas daily — content for your page, hooks for your ads.")
    pdf.para("Ads bring buyers, but you also need content that keeps your Facebook Page alive, builds trust, and "
             "gives you free reach. The smartest free trick comes from @dotsokt: use Reddit Custom Feeds to find "
             "viral content for your niche.")
    pdf.bullets([
        "Create a private Custom Feed for each niche you're in and add all your niche subreddits",
        "Every 24 hours, open each feed, sort by 'Top', and select 'Today'",
        "You now have a list of the most upvoted posts in your niche — content that has already proven people care",
        "Use those posts as inspiration and curate the best ideas for your Facebook Page",
        "Sometimes you can literally take images as they are and post them on your page with an engaging caption",
        "It's one of the easiest free ways to consistently find content with proven demand",
    ])
    pdf.para("Why this matters for your ads too: the hooks and angles that go viral in your niche are the same "
             "hooks that stop thumbs on your ad creatives. Your Custom Feeds become your idea factory — for organic "
             "posts AND for ad copy.")
    pdf.h2("Organic + paid: how the best sellers combine both")
    pdf.para("When readers asked one top seller whether their 10K-daily sales come from ads or organic content, the "
             "answer was: both. The pros run a hybrid loop — organic content on the page builds authority, trust and "
             "free reach, while paid ads bring the buyers who convert. Organic posts also feed your retargeting "
             "audiences: people who watched your page's content become warm prospects for your ads.")
    pdf.callout("The hybrid loop: Reddit feeds → page content → warm audience → ads → sales → reviews → better "
                "content. Each piece makes the next one cheaper and stronger.",
                label="THE HYBRID LOOP", kind="green")
    pdf.h2("The two niches that sell best")
    pdf.bullets([
        "Love, relationship & marriage — 'fix your relationship' guides sell like crazy",
        "Mothers & nursing mothers — new mothers search for help every single day",
    ])
    pdf.h2("Creatives that convert (and don't get rejected)")
    pdf.para("Meta rejects ads that look explicit or make outrageous claims. Keep your ad clean and sell the RESULT, "
             "not the product:")
    pdf.bullets([
        "Use video (15–30 seconds, 9:16 for Stories/Reels, 1:1 for Feed) — your talking-flyer skills transfer here",
        "First 3 seconds must hook: 'Are you tired of fighting with your partner about money?'",
        "Show the benefit: a better relationship, a calmer baby, a clearer budget",
        "Never promise guaranteed income or medical cures — Meta will reject it",
        "Add a clear call to action: 'Get the guide — link in comments' or 'Order now'",
    ])
    pdf.h2("Budgeting like a pro")
    pdf.bullets([
        "Start at ₦2,000 – ₦5,000 per day, run 3–5 days before judging",
        "Don't touch the ad every hour — let it learn",
        "One product + one niche + one creative at a time; scale the winner",
        "When an ad makes sales, increase its budget gradually (20–30% every 2 days)",
    ])
    pdf.callout("Common beginner mistakes: targeting too narrow (let Advantage+ work), making the ad about the PDF "
                "instead of the result, switching creatives every few hours, and advertising without a sales-tracking "
                "pixel. Avoid these and you're already ahead of 90% of beginners.",
                label="AVOID THESE", kind="amber")
    pdf.task_box("This week: 1) Set up all five system pieces (accounts, page, Business Manager, Selar, pixel). "
                 "2) Build your Reddit Custom Feeds and check them once a day. 3) Launch ONE ad at ₦2,000/day for 3 "
                 "days and change nothing for 72 hours.")
    pdf.references([
        ("@egbokavictory_ — 'The things you need to setup a digital product system that makes you at least 10K daily'",
         "https://x.com/egbokavictory_/status/2091154409786884148"),
        ("@egbokavictory_ — 'How I make at least 10K daily' (organic + paid answer)",
         "https://x.com/egbokavictory_/status/2089711208832057499"),
        ("@dotsokt — 'Use Reddit Custom Feeds to find viral content for your Facebook page'",
         "https://x.com/dotsokt/status/2092346283302457636"),
        ("@iamrichygold — the original 5k–10k daily system (ads with ₦30K)",
         "https://x.com/iamrichygold/status/2092708000414761351"),
    ])

    # ══════════════════════════════════════════════════════════
    # CHAPTER 7
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.chapter_header("7", "PRO BONUS: Target the Big Buyers",
                       "The geo-targeting secret top sellers use: Kenya, Zambia, Ghana & Nigeria.")
    pdf.para("Most beginners target only Nigeria, then wonder why sales are slow. Smart sellers know that the biggest "
             "buyers of digital products right now are in specific African countries — and they target those "
             "countries directly in their ads.")
    pdf.h2("The winning countries")
    pdf.bullets([
        "🇰🇪 Kenya — the biggest buyers of digital products at the moment (your first sale may come in KSH!)",
        "🇿🇲 Zambia — high-converting market with low competition",
        "🇬🇭 Ghana — strong buyers of guides, templates and relationship content",
        "🇳🇬 Nigeria — your home ground; a huge market you can also sell to in naira",
    ])
    pdf.h2("The ChatGPT city trick")
    pdf.callout("1) Open ChatGPT and type:\n\n"
                "'Give me the top 5 cities in Kenya, the top 5 cities in Zambia, the top 5 cities in Ghana, and the "
                "top 5 cities in Nigeria.'\n\n"
                "2) Copy the cities and paste them into your ad set's locations.\n\n"
                "3) Run your ads as normal.\n\n"
                "Sellers who use this trick say their first sale often arrives within days — and in Kenyan Shillings.",
                label="🤖 THE TRICK", kind="green")
    pdf.h2("Why this works")
    pdf.para("City-level targeting keeps your ads in the wealthiest, most connected parts of each country — exactly "
             "where digital-product buyers live. It also keeps your cost per click lower than country-wide targeting, "
             "so your ₦30K budget goes further. The product and the ad stay the same — only the location changes.")
    pdf.task_box("Open ChatGPT right now and get your city lists. Save them in your notes. You'll paste them into "
                 "your ad set when you set up your campaign.")
    pdf.references([
        ("@egbokavictory_ — 'Pro Targeting Tip: Kenya, Zambia, Ghana & Nigeria'",
         "https://x.com/egbokavictory_/status/2016424347422867473"),
    ])

    # ══════════════════════════════════════════════════════════
    # CHAPTER 8
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.chapter_header("8", "Step 4: Rinse, Repeat & Scale",
                       "One sale is not the goal. The system is: sell, improve, scale. Forever.")
    pdf.photo(opt_image("step4-scale.png"), "Consistency first. Scaling later.")
    pdf.para("A single sale proves nothing. A single day of sales proves nothing. The goal is a repeatable loop that "
             "produces ₦5K–₦10K daily, then more. Here is the loop:")
    pdf.h2("The repeat loop")
    pdf.bullets([
        "Sell — keep your product live and your ads running",
        "Get more talking-flyer clients — this refills your ad budget without touching your savings",
        "Run more ads — scale budgets on winning creatives, cut losers",
        "Improve the product — ask buyers what they loved and what they wanted more of; update the PDF",
        "Repeat — this cycle is the business. It compounds",
    ])
    pdf.h2("How to move past ₦10K/day")
    pdf.bullets([
        "Raise your price as social proof grows (reviews, sales count, before/after stories)",
        "Create a second product in a related niche and cross-sell it to your buyers",
        "Build an email/WhatsApp list of buyers — they buy again and again",
        "Test new creatives weekly; scale the ones with the lowest cost per sale",
        "Add a bundle: guide + templates + checklist at a higher price",
    ])
    pdf.callout("Consistency first. Scaling later. Most people quit at week two, right before the system starts "
                "working. The sellers earning ₦5K+ daily are not geniuses — they simply showed up longer than "
                "everyone else.",
                label="💯 THE ONLY SECRET", kind="amber")
    pdf.task_box("Look at your product, ads and flyer pipeline. Pick ONE thing to improve this week — a better "
                 "creative, a higher price, or a second product outline. Small improvements, repeated, become big "
                 "numbers.")
    pdf.references([
        ("@iamrichygold — 'Here's a summary of my post...' (the 4-step system recap)",
         "https://x.com/iamrichygold/status/2092953828328952091"),
    ])

    # ══════════════════════════════════════════════════════════
    # CHAPTER 9
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.chapter_header("9", "Your 30-Day Action Plan",
                       "A day-by-day roadmap so you never wake up wondering 'what do I do today?'")
    pdf.h2("Week 1 — Build your product (Days 1–7)")
    pdf.bullets([
        "Day 1: Pick your niche with the 3-question test. Write down 3 product ideas.",
        "Day 2: Outline your product — 5–10 sections solving one specific problem.",
        "Day 3: Write the first half of your content (simple language, real examples).",
        "Day 4: Finish writing. Let it rest for a few hours, then edit.",
        "Day 5: Design it in Canva — clean template, headings, images, cover page.",
        "Day 6: Export to PDF, check on your phone, fix anything ugly.",
        "Day 7: Upload to Selar. Set your price. Get your checkout link. 🎉 You have a product!",
    ])
    pdf.h2("Week 2 — Raise ₦30,000 with talking flyers (Days 8–14)")
    pdf.bullets([
        "Day 8: Make one sample talking flyer (CapCut + voiceover).",
        "Day 9: Pitch 10 businesses with the script. Track every reply.",
        "Day 10: Follow up everyone who didn't reply. Pitch 10 more.",
        "Day 11: Deliver your first flyer. Ask for a referral.",
        "Day 12: Pitch 10 more businesses. Bill friends and family.",
        "Day 13: Deliver flyer #2–3. Post samples on your status.",
        "Day 14: Close your 5th client. You should now have ₦30,000+. 🎉",
    ])
    pdf.h2("Week 3 — Launch your ads (Days 15–21)")
    pdf.bullets([
        "Day 15: Create your Facebook Page + Business account.",
        "Day 16: Build your ad creative (video, 15–30s, hook in the first 3 seconds).",
        "Day 17: Connect your Selar page and Meta pixel.",
        "Day 18: Create the Advantage+ campaign. Paste your ChatGPT city lists (Chapter 7).",
        "Day 19: Launch at ₦2,000–₦3,000/day. Hands off the keyboard.",
        "Day 20: Do NOT change anything. Watch and learn.",
        "Day 21: Review results: cost per result, sales, messages. Adjust ONE thing.",
    ])
    pdf.h2("Week 4 — Optimize & scale (Days 22–30)")
    pdf.bullets([
        "Day 22: If an ad is selling — increase its budget by 20–30%.",
        "Day 23: If nothing sells — change the creative or the offer, not the targeting.",
        "Day 24: Make a second creative (different hook, same product).",
        "Day 25: Run flyer pitches in your spare time to refill the ad fund.",
        "Day 26: Message your buyers for reviews and feedback. Improve the PDF.",
        "Day 27: Test a second country from your list (e.g., Kenya alone).",
        "Day 28: Double down on whatever made money. Cut what didn't.",
        "Day 29: Outline your second product (cross-sell to buyers).",
        "Day 30: Review the whole month. Celebrate. Plan month two. 🚀",
    ])
    pdf.h2("Your daily routine (from Day 15 onward)")
    pdf.bullets([
        "Morning (30 min): check ads, reply to customers, post one flyer sample",
        "Afternoon (1–2 hrs): pitch 5–10 flyer clients, make deliveries",
        "Evening (30 min): improve the product, plan tomorrow's creative",
        "Total: about 2–3 focused hours a day. The system runs the rest of the time.",
    ])
    pdf.task_box("Print or copy this chapter into your notes. Tick off every day. Miss a day? Don't restart — just "
                 "continue the next day. Perfection is not the goal; progress is.")

    # ══════════════════════════════════════════════════════════
    # CHAPTER 10
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.chapter_header("10", "FAQ & Final Words",
                       "The questions everyone asks — and the no-gatekeeping closing message.")
    pdf.h2("Frequently asked questions")
    pdf.h3("How much money do I need to start?")
    pdf.para("You can create your first product with ₦0 using free tools. The only real money needed is the ₦30,000 "
             "ad budget — and Chapter 5 shows you how to raise it with talking flyers, so you're not spending your "
             "own money.")
    pdf.h3("Do I need followers?")
    pdf.para("No. This system uses paid ads, not your personal page. People with zero followers have made first sales "
             "in days because the ads bring buyers to them.")
    pdf.h3("I've never run ads. Can I follow this?")
    pdf.para("Yes — the book walks you through it step by step, and Meta's Advantage+ does most of the work. Start "
             "small (₦2,000/day) while you learn.")
    pdf.h3("Can I really do this on my phone?")
    pdf.para("Yes. Canva, CapCut, Selar, and Meta Ads Manager all work on smartphones. That's how many sellers run "
             "this exact business.")
    pdf.h3("What if Meta rejects my ad?")
    pdf.para("Keep your ad clean: no explicit content, no outrageous income claims, no medical promises. Sell the "
             "result, not the product. If an ad is rejected, fix the text and resubmit — it happens to everyone.")
    pdf.h3("How long until my first sale?")
    pdf.para("With a good product, clean creative and the right countries, first sales often come within the first "
             "few days of ads — but it is not guaranteed. Consistency, not speed, is what creates the ₦5K–₦10K daily "
             "reality.")
    pdf.h3("Is this a get-rich-quick scheme?")
    pdf.para("No. It's a work-based system with honest math. If you put in the work, ₦5K–₦10K daily is possible, "
             "then you scale. No ₦100K-per-day fairy tales. Not for lazy people.")
    pdf.h3("What about refunds?")
    pdf.para("The ebook comes with a 7-day money-back guarantee from the author: if it doesn't deliver value, message "
             "and get a full refund — no stories.")
    pdf.h2("Final words — no gatekeeping")
    pdf.para("Everything in this book was once someone else's 'secret'. The difference between you and the sellers "
             "earning ₦5K–₦10K daily is not talent, connections, or luck. It's that they did the work — the product, "
             "the flyers, the ads, the repeat — while others scrolled.")
    pdf.callout("Create the product. Raise the ₦30,000. Run the ads. Rinse and repeat.\n\n"
                "Consistency first. Scaling later.\n\n"
                "Do the work. 💯",
                label="💯 NO GATEKEEPING ZONE", kind="green")
    pdf.task_box("Start today. Read the bonus worksheets, make your plan, and take your first action within 24 "
                 "hours. In 30 days, you'll thank yourself.")

    # ══════════════════════════════════════════════════════════
    # BONUS WORKSHEETS
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("DJ", "B", 22)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "Bonus Worksheets", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    y = pdf.get_y()
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.1)
    pdf.line(M, y, PAGE_W - M, y)
    pdf.ln(7)

    pdf.h2("Worksheet A — Talking Flyer Pitch Script (copy & paste)")
    pdf.para("WhatsApp version:", size=10.8)
    pdf.callout("Hello [Name]! I noticed you sell [product/service] — great work. I create short video ads called "
                "talking flyers for businesses like yours: 30–60 seconds with your photos, a voiceover, and your "
                "WhatsApp number so customers can reach you directly. It's ₦6,000 and delivery takes 24 hours. I'll "
                "send a sample first. Can I make one for you?", label="📱 WHATSAPP PITCH", kind="amber")
    pdf.para("Face-to-face version:", size=10.8)
    pdf.callout("'Good afternoon, boss. I love what you do here. I make talking flyers — short video ads — for "
                "businesses like this. It's ₦6,000, takes 24 hours, and I'll send it to you to post on WhatsApp. "
                "This is a sample of my work. Should I make one for you today?'", label="🚶 IN-PERSON PITCH", kind="green")
    pdf.h3("Follow-up message (day 2)")
    pdf.para("'Hello [Name], just checking in on the talking flyer — I have two slots left this week. Should I "
             "reserve one for you?'")

    pdf.add_page()
    pdf.h2("Worksheet B — Product Creation Checklist")
    pdf.bullets([
        "☐ One specific problem chosen (niche test passed)",
        "☐ 5–10 section outline written",
        "☐ Content written in simple language (10–20 pages)",
        "☐ Designed in Canva with a clean, consistent template",
        "☐ Attractive cover page created",
        "☐ Exported as PDF and checked on a phone",
        "☐ Thank-you page with your WhatsApp/store link included",
        "☐ Uploaded to Selar with a clear title and description",
        "☐ Price set (₦1,000–₦5,000 for your first product)",
        "☐ Checkout link tested with a real payment flow",
    ])
    pdf.h2("Worksheet C — Ad Setup Checklist")
    pdf.bullets([
        "☐ Facebook Page created for your product",
        "☐ Business account created at business.facebook.com",
        "☐ Campaign objective: Sales (or Traffic while learning)",
        "☐ Advantage+ audience selected — targeting kept wide",
        "☐ ChatGPT city lists pasted into locations (Chapter 7)",
        "☐ Video creative 15–30s, hook in the first 3 seconds",
        "☐ Ad copy sells the RESULT, no explicit claims",
        "☐ Selar checkout link in the ad destination",
        "☐ Meta pixel connected to track sales",
        "☐ Budget: ₦2,000–₦5,000/day, scheduled for 3+ days",
    ])
    pdf.h2("Worksheet D — Daily Tracker")
    pdf.para("Copy this into your notes and tick daily:", size=10.8)
    track = [
        ("Day", "Product work", "Flyer pitches", "Ads running", "Sales (₦)"),
        ("1", "", "", "", ""),
        ("2", "", "", "", ""),
        ("3", "", "", "", ""),
        ("4", "", "", "", ""),
        ("5", "", "", "", ""),
        ("6", "", "", "", ""),
        ("7", "", "", "", ""),
    ]
    col_w = [26, 40, 38, 38, 32]
    pdf.set_font("DJ", "B", 9.5)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*LIGHT)
    x = M
    for i, c in enumerate(track[0]):
        pdf.set_xy(x, pdf.get_y())
        pdf.cell(col_w[i], 8, c, border=1, align="C", fill=True)
        x += col_w[i]
    pdf.ln(8)
    pdf.set_font("DJ", "", 9.5)
    pdf.set_text_color(30, 41, 59)
    for row in track[1:]:
        x = M
        for i, c in enumerate(row):
            pdf.set_xy(x, pdf.get_y())
            pdf.cell(col_w[i], 8, c, border=1, align="C")
            x += col_w[i]
        pdf.ln(8)
    pdf.ln(3)
    pdf.para("Weekly review questions: What sold? What didn't? What will I improve next week? Write three lines "
             "every Sunday.")

    # ─────────────── APPENDIX: SOURCES ───────────────
    pdf.add_page()
    pdf.set_font("DJ", "B", 22)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "Appendix — Sources & Further Reading", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    y = pdf.get_y()
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.1)
    pdf.line(M, y, PAGE_W - M, y)
    pdf.ln(7)
    pdf.para("Every claim in this book traces back to free, public educational posts by Nigerian and African "
             "digital-product creators. Watch the originals yourself — each link below notes which chapters it "
             "supports. All content in this ebook is an original expansion of these ideas, written for beginners.")
    pdf.h2("The references by chapter")
    refs = [
        ("@iamrichygold — 'What I'll do to earn 5k–10k daily if I had to start over again'",
         "https://x.com/iamrichygold/status/2092708000414761351", "Chapters 1, 6, 8"),
        ("@iamrichygold — 'Here's a summary of my post...' (system recap)",
         "https://x.com/iamrichygold/status/2092953828328952091", "Chapters 1, 8"),
        ("@iamrichygold — 'Digital products in 10 minutes' (series part 1)",
         "https://x.com/iamrichygold/status/2084258170944270469", "Chapters 1, 2, 3"),
        ("@iamrichygold — 'How to get ready-made valuable digital products to resell legitimately'",
         "https://x.com/iamrichygold/status/2084383065682375038", "Chapter 4"),
        ("@egbokavictory_ — 'Pro Targeting Tip: Kenya, Zambia, Ghana & Nigeria'",
         "https://x.com/egbokavictory_/status/2016424347422867473", "Chapter 7"),
        ("@egbokavictory_ — 'The things you need to setup a digital product system that makes you at least 10K daily'",
         "https://x.com/egbokavictory_/status/2091154409786884148", "Chapter 6"),
        ("@egbokavictory_ — 'How I make at least 10K daily'",
         "https://x.com/egbokavictory_/status/2089711208832057499", "Chapter 6"),
        ("@dotsokt — 'Use Reddit Custom Feeds to find viral content for your Facebook page'",
         "https://x.com/dotsokt/status/2092346283302457636", "Chapter 6"),
    ]
    for title, url, ch in refs:
        y0 = pdf.get_y()
        if y0 > 235:
            pdf.add_page()
        pdf.set_font("DJ", "B", 9.6)
        pdf.set_text_color(30, 41, 59)
        pdf.multi_cell(W, 5.6, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DJ", "U", 8.8)
        pdf.set_text_color(37, 99, 235)
        pdf.multi_cell(W, 5.2, f"   {url}", new_x="LMARGIN", new_y="NEXT", link=url)
        pdf.set_font("DJ", "B", 8.8)
        pdf.set_text_color(*GOLD_D)
        pdf.multi_cell(W, 5.2, f"   Used in: {ch}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2.5)
    pdf.ln(3)
    pdf.callout("Links may change or be taken down — that is the nature of social media. The methods in this book "
                "are timeless: create a product, raise seed money, run clean ads, target the right countries, "
                "repeat. Verify, learn, and make it your own.",
                label="A NOTE ON LINKS", kind="amber")

    # ─────────────── BACK PAGE ───────────────
    pdf.add_page()
    pdf.set_margins(0, 0, 0)
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, PAGE_W, PAGE_H, style="F")
    # small cover thumbnail
    thumb_w = 60
    thumb_h = thumb_w * 1200 / 896
    pdf.image(cover_with_bands, x=(PAGE_W - thumb_w) / 2, y=40, w=thumb_w)
    pdf.set_font("DJ", "B", 22)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 140)
    pdf.cell(PAGE_W, 12, "Now go and do the work.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "", 12)
    pdf.set_text_color(255, 213, 122)
    pdf.cell(PAGE_W, 9, "Create the product. Raise the ₦30,000. Run the ads. Rinse and repeat.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(26)
    pdf.set_font("DJ", "", 10)
    pdf.set_text_color(133, 117, 95)
    pdf.cell(PAGE_W, 7, "The ₦5K–₦10K Digital Product Playbook — by Oluwadarasimi Oluwadamilola", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(PAGE_W, 7, "© 2026 All rights reserved", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_margins(M, 18, M)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    os.makedirs(DELIVERY_DIR, exist_ok=True)
    pdf.output(OUT)
    print(f"✅ Ebook written: {OUT} ({os.path.getsize(OUT)/1024:.0f} KB, {pdf.pages_count} pages)")


def build_sample():
    """Build a free downloadable sample: Chapter 1 + CTA (assets/ebook/free-sample-chapter1.pdf)."""
    pdf = Book()
    SAMPLE_OUT = os.path.join(ROOT, "assets", "ebook", "free-sample-chapter1.pdf")

    # Cover-style opening
    cover_with_bands = prepare_cover_art()
    pdf.add_page()
    pdf.set_margins(0, 0, 0)
    img_h = PAGE_W * 1200 / 896
    pdf.image(cover_with_bands, x=0, y=(PAGE_H - img_h) / 2, w=PAGE_W)
    pdf.set_font("DJ", "B", 11)
    pdf.set_text_color(*COBALT)
    pdf.set_xy(0, 40)
    pdf.cell(PAGE_W, 8, "FREE SAMPLE · CHAPTER 1 OF 10", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 24)
    pdf.set_text_color(*NAVY)
    pdf.cell(PAGE_W, 11, "THE ₦5K–₦10K", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 26)
    pdf.set_text_color(*COBALT)
    pdf.cell(PAGE_W, 12, "DIGITAL PRODUCT", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 28)
    pdf.set_text_color(*GOLD)
    pdf.cell(PAGE_W, 12, "PLAYBOOK", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "", 11)
    pdf.set_text_color(75, 66, 51)
    pdf.cell(PAGE_W, 9, "Make ₦5,000 – ₦10,000 Daily Selling Digital Products", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 12)
    pdf.set_text_color(*COBALT_D)
    pdf.set_xy(0, 224)
    pdf.cell(PAGE_W, 8, "BY OLUWADARASIMI OLUWADAMILOLA", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 17)
    pdf.set_text_color(*GOLD)
    pdf.cell(PAGE_W, 10, "Full book: ₦3,500   (was ₦10,000)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_margins(M, 18, M)

    # Chapter 1 content
    pdf.add_page()
    pdf.chapter_header("1", "The ₦5K–₦10K Daily Promise",
                       "An honest chapter about what this system is, what it isn't, and why ₦5,000–₦10,000 a day is a realistic goal.")
    pdf.para("Let's start with honesty, because that's the whole point of this book.")
    pdf.para("I am not going to promise you ₦100,000 or ₦200,000 every single day. Anyone who promises that on the "
             "internet is selling you dreams, not a system. What I am showing you is a simple process — the same "
             "process real digital-product sellers are using right now. If you put in the work, ₦5,000 – ₦10,000 "
             "daily is possible. And once you have that consistency, you scale.")
    pdf.callout("₦5,000/day × 30 days = ₦150,000 per month\n"
                "₦10,000/day × 30 days = ₦300,000 per month\n\n"
                "That's ₦150K–₦300K monthly — more than many Nigerian salaries — from a business you can run on your phone.",
                label="THE MATH", kind="amber")
    pdf.h2("What this book IS")
    pdf.bullets([
        "A step-by-step system: create a product → raise ₦30,000 → run ads → scale",
        "Written for complete beginners — no tech skills, no followers, no big budget required",
        "Phone-friendly — everything in here works from a smartphone",
        "Honest — it shows you the work involved and never hides the effort",
    ])
    pdf.h2("What this book is NOT")
    pdf.bullets([
        "A get-rich-in-24-hours scheme",
        "An MLM, referral trick, or 'quick money' app",
        "A promise that money falls from the sky while you sleep on night one",
        "For lazy people — if you don't want to work, put this book down now",
    ], marker="✗", mcolor=(220, 38, 38))
    pdf.h2("Why digital products?")
    pdf.para("Digital products are things you create once and sell many times: a PDF guide, a template, an ebook, a "
             "checklist. There is no inventory to store, no shipping to pay, and delivery is instant. Every sale is "
             "almost pure profit. People across Africa buy them every single day — relationship guides, pregnancy and "
             "baby-care books, recipe books, finance templates, business checklists, church and event materials. "
             "The list is endless.")
    pdf.task_box("Answer these three questions in your notes:\n"
                 "1) How much money do I need per month to change my life? (Be honest.)\n"
                 "2) What problem do people around me always complain about? (That's a product idea.)\n"
                 "3) What will I do with my first ₦5,000 day? (Visualize it — it matters.)")
    pdf.references([
        ("@iamrichygold — 'What I'll do to earn 5k–10k daily if I had to start over again'",
         "https://x.com/iamrichygold/status/2092708000414761351"),
        ("@iamrichygold — 'Let's talk about how to create a digital product' (series kick-off)",
         "https://x.com/iamrichygold/status/2084258170944270469"),
    ])

    # CTA page
    pdf.add_page()
    pdf.ln(24)
    pdf.set_font("DJ", "B", 24)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(W, 12, "This was Chapter 1 of 10.", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(2)
    pdf.set_font("DJ", "", 12.5)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(W, 8, "Get the complete ebook and unlock:", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)
    pdf.bullets([
        "Digital Products 101 + the hottest niches",
        "Step 1: create your first product (7-step process)",
        "Shortcut: resell ready-made products (PLR)",
        "Step 2: raise ₦30,000 with talking flyers (pitch script included)",
        "Step 3: Facebook Ads that sell + the full 10K-daily system checklist",
        "PRO BONUS: target Kenya, Zambia, Ghana & Nigeria (the ChatGPT city trick)",
        "Step 4: rinse, repeat & scale",
        "Your 30-Day Action Plan + worksheets & daily tracker",
        "Every chapter's source links (X/Twitter references)",
    ])
    pdf.ln(8)
    pdf.set_font("DJ", "B", 19)
    pdf.set_text_color(255, 176, 32)
    pdf.multi_cell(W, 10, "₦3,500   (was ₦10,000)", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("DJ", "", 11)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(W, 7, "One-time payment · Instant download · 7-day money-back guarantee",
                   new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)
    pdf.callout(f"Get instant access at {LIVE_SITE_URL} — or message the author on WhatsApp. "
                "Consistency first. Scaling later. Do the work.",
                label="GET THE FULL BOOK", kind="green", link=LIVE_SITE_URL)

    os.makedirs(os.path.dirname(SAMPLE_OUT), exist_ok=True)
    pdf.output(SAMPLE_OUT)
    print(f"✅ Sample written: {SAMPLE_OUT} ({os.path.getsize(SAMPLE_OUT)/1024:.0f} KB, {pdf.pages_count} pages)")


if __name__ == "__main__":
    import sys
    if "--all" in sys.argv:
        build()
        build_sample()
    elif "--sample" in sys.argv:
        build_sample()
    else:
        build()
