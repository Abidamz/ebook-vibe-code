#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal, config-driven ebook builder (fpdf2) — see ../SKILL.md and
../references/ebook-pdf.md. Produces a PAID book and a FREE sample from one source so
they cannot drift.

Usage:
    python ebook_skeleton.py            # paid only
    python ebook_skeleton.py --all      # paid + free sample
    python ebook_skeleton.py --sample   # sample only

Edit CONFIG for your book. Paid output goes to an IGNORED directory by convention
(see ../references/paywall-and-git.md); the sample goes where your repo tracks it.
"""
import os
import re
import sys

from fpdf import FPDF

CONFIG = {
    "paid_out": "/tmp/skilltest/paid.pdf",        # point at your ignored dir, e.g. <repo>/delivery/book.pdf
    "sample_out": "/tmp/skilltest/sample.pdf",    # point at your tracked dir, e.g. <repo>/assets/ebook/free-sample.pdf
    "title": "Your Product Playbook",
    "title_accent": "STEP BY STEP",
    "subtitle": "A practical, no-hype roadmap for beginners.",
    "author": "Your Name",
    "identity": "Your Playbook  ·  © 2026 Your Name",
    "price_line": "₦3,500   (was ₦10,000)",
    "terms": "One-time payment · Instant download · 7-day money-back guarantee",
    "cta_url": "https://example.com/checkout",
    "cta_label": "GET THE FULL BOOK",
    "chapters": [
        {
            "title": "The System",
            "promise": "Why this works and what it asks of you.",
            "paras": [
                "This is a system, not a lottery ticket. You create something useful, "
                "put it in front of the right people, and improve every week.",
                "No tech skills required. Effort required. That trade is the whole book.",
            ],
            "bullets": ["Create a simple product", "Raise small seed money", "Run ads that sell", "Scale what works"],
            "task": "Write down: 1) the problem people around you complain about, 2) who has it, 3) what you can build this week.",
            "refs": [("Source thread", "https://example.com/thread-1")],
        },
        {
            "title": "Create",
            "promise": "Your first product in seven steps.",
            "paras": [
                "Start smaller than feels respectable. A checklist that solves one problem "
                "beats a course that promises everything.",
            ],
            "bullets": ["Pick one promise", "Outline ten sections", "Draft ugly, edit kind"],
            "task": "Draft your table of contents today. Ten lines maximum.",
            "refs": [],
        },
    ],
}

# ── glyph safety: DejaVu has no colour emoji ────────────────────────
_EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\uFE0F\u26EA\u2705\u274C\u26A0\u26A1\u2611]")
_REPL = {"❤": "♥", "❌": "", "⚠": "!", "⚡": "", "☐": "[ ]", "…": "..."}

DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DJB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DJSB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

INK = (28, 24, 18); BODY = (30, 41, 59); AMBER = (180, 83, 9)
GREEN = (22, 101, 52); MUTED = (133, 117, 95); CREAM = (247, 241, 227)
AMBER_L = (249, 240, 214); GREEN_L = (236, 246, 236); COBALT = (29, 78, 216)

PAGE_W, PAGE_H = 210, 297
M = 18
W = PAGE_W - 2 * M


def clean(t):
    for k, v in _REPL.items():
        t = t.replace(k, v)
    t = _EMOJI_RE.sub("", t)
    return re.sub(r"\s+", " ", t).strip()


class Book(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("DJ", "", DJ)
        self.add_font("DJ", "B", DJB)
        self.add_font("DJS", "B", DJSB)
        self.set_margins(M, 18, M)

    def footer(self):
        if self.page_no() <= 1:
            return
        self.set_y(-14)
        self.set_font("DJ", "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 5, CONFIG["identity"], new_x="LMARGIN", new_y="NEXT", align="L")
        self.cell(0, 5, f"Page {self.page_no()}", align="R")

    def para(self, t, size=10.8, lh=6.3, space=3.2):
        self.set_font("DJ", "", size)
        self.set_text_color(*BODY)
        self.multi_cell(W, lh, clean(t), new_x="LMARGIN", new_y="NEXT")
        self.ln(space)

    def bullets(self, items, size=10.8, lh=6.2, marker="✓", color=GREEN):
        for it in items:
            y = self.get_y()
            self.set_font("DJ", "B", size - 1)
            self.set_text_color(*color)
            self.set_xy(M, y)
            self.cell(7, lh, marker)
            self.set_font("DJ", "", size)
            self.set_text_color(*BODY)
            self.multi_cell(W - 7, lh, clean(it), new_x="LMARGIN", new_y="NEXT")
            self.ln(1.4)

    def h1(self, t):
        self.set_font("DJS", "B", 26)
        self.set_text_color(*INK)
        self.multi_cell(W, 12, clean(t), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def h2(self, t):
        self.set_font("DJ", "B", 14)
        self.set_text_color(*AMBER)
        self.multi_cell(W, 8, clean(t), new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def box(self, text, label, bg, fg):
        self.ln(1)
        y = self.get_y()
        self.set_font("DJ", "", 10.5)
        lines = self.multi_cell(W - 12, 6, clean(text), dry_run=True, output="LINES")
        h = len(lines) * 6 + 16
        self.set_fill_color(*bg)
        self.rect(M, y, W, h, "F")
        self.set_xy(M + 6, y + 4)
        self.set_font("DJ", "B", 8.5)
        self.set_text_color(*fg)
        self.cell(0, 5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_xy(M + 6, y + 10)
        self.set_font("DJ", "", 10.5)
        self.set_text_color(*INK)
        self.multi_cell(W - 12, 6, clean(text), new_x="LMARGIN", new_y="NEXT")
        self.set_y(y + h + 4)

    def task_box(self, text):
        self.box(text, "DO THIS NOW", AMBER_L, AMBER)

    def callout(self, text, label, link=None):
        self.ln(1)
        y = self.get_y()
        self.set_font("DJ", "", 10.5)
        lines = self.multi_cell(W - 12, 6, clean(text), dry_run=True, output="LINES")
        h = len(lines) * 6 + 16
        self.set_fill_color(*GREEN_L)
        self.rect(M, y, W, h, "F")
        self.set_xy(M + 6, y + 4)
        self.set_font("DJ", "B", 8.5)
        self.set_text_color(*GREEN)
        self.cell(0, 5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_xy(M + 6, y + 10)
        self.set_font("DJ", "", 10.5)
        self.set_text_color(*INK)
        if link:
            self.set_text_color(*COBALT)
        self.multi_cell(W - 12, 6, clean(text), new_x="LMARGIN", new_y="NEXT",
                        link=link)
        self.set_y(y + h + 4)

    def references(self, refs):
        if not refs:
            return
        self.h2("Sources & References")
        for label, url in refs:
            self.set_font("DJ", "", 9.5)
            self.set_text_color(*COBALT)
            self.multi_cell(W, 5.5, f"{label} — {url}", new_x="LMARGIN", new_y="NEXT", link=url)
        self.ln(2)

    def cover(self):
        self.add_page()
        self.set_fill_color(*INK)
        self.rect(0, 0, PAGE_W, PAGE_H, "F")
        self.set_font("DJ", "B", 11)
        self.set_text_color(255, 176, 32)
        self.cell(0, 10, CONFIG["title_accent"], new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(30)
        self.set_font("DJS", "B", 40)
        self.set_text_color(*CREAM)
        self.multi_cell(0, 18, clean(CONFIG["title"]), align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)
        self.set_font("DJ", "", 13)
        self.set_text_color(*MUTED)
        self.multi_cell(0, 8, clean(CONFIG["subtitle"]), align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)
        self.set_font("DJ", "B", 15)
        self.set_text_color(255, 176, 32)
        self.cell(0, 10, CONFIG["price_line"], new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("DJ", "", 10)
        self.set_text_color(*MUTED)
        self.cell(0, 6, CONFIG["terms"], new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(8)
        self.set_font("DJ", "", 10)
        self.set_text_color(*CREAM)
        self.cell(0, 6, f"by {CONFIG['author']}", new_x="LMARGIN", new_y="NEXT", align="C")


def build_paid():
    pdf = Book()
    pdf.cover()
    pdf.add_page()
    pdf.h1("Contents")
    for i, ch in enumerate(CONFIG["chapters"], 1):
        pdf.set_font("DJ", "B", 12)
        pdf.set_text_color(*INK)
        pdf.cell(0, 8, f"{i}.  {ch['title']}", new_x="LMARGIN", new_y="NEXT")
    for i, ch in enumerate(CONFIG["chapters"], 1):
        pdf.add_page()
        pdf.h2(f"CHAPTER {i}")
        pdf.h1(ch["title"])
        pdf.para(ch["promise"])
        for p in ch["paras"]:
            pdf.para(p)
        if ch.get("bullets"):
            pdf.bullets(ch["bullets"])
        if ch.get("task"):
            pdf.task_box(ch["task"])
        pdf.references(ch.get("refs", []))
    os.makedirs(os.path.dirname(CONFIG["paid_out"]), exist_ok=True)
    pdf.output(CONFIG["paid_out"])
    print(f"paid: {CONFIG['paid_out']} ({os.path.getsize(CONFIG['paid_out'])//1024} KB, {pdf.pages_count} pages)")


def build_sample():
    pdf = Book()
    ch = CONFIG["chapters"][0]
    pdf.add_page()
    pdf.h2("FREE SAMPLE — CHAPTER 1")
    pdf.h1(ch["title"])
    pdf.para(ch["promise"])
    for p in ch["paras"]:
        pdf.para(p)
    pdf.add_page()
    pdf.ln(20)
    pdf.set_font("DJS", "B", 22)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 11, "This was Chapter 1.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.callout(f"Get the complete book at {CONFIG['cta_url']}", CONFIG["cta_label"],
                link=CONFIG["cta_url"])
    os.makedirs(os.path.dirname(CONFIG["sample_out"]), exist_ok=True)
    pdf.output(CONFIG["sample_out"])
    print(f"sample: {CONFIG['sample_out']} ({os.path.getsize(CONFIG['sample_out'])//1024} KB, {pdf.pages_count} pages)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--all" in a:
        build_paid(); build_sample()
    elif "--sample" in a:
        build_sample()
    else:
        build_paid()
