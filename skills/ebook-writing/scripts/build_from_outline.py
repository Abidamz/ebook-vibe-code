#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Typeset an ebook from outline.json — see ../SKILL.md and ../references/outline-schema.md.

Usage:
    python build_from_outline.py outline.json --out DIR [--paid-only|--sample-only]

Produces DIR/book.pdf (full) and DIR/sample.pdf (chapter 1 + CTA page).
Topic-agnostic: everything comes from the outline. fpdf2 + DejaVu (system fonts).
"""
import json
import os
import re
import sys

from fpdf import FPDF

_EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\uFE0F\u26EA\u2705\u274C\u26A0\u26A1\u2611]")
_REPL = {"❤": "♥", "❌": "", "⚠": "!", "⚡": "", "☐": "[ ]", "…": "..."}

DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DJB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DJSB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

INK = (28, 24, 18); BODY = (30, 41, 59); AMBER = (180, 83, 9)
GREEN = (22, 101, 52); RED = (220, 38, 38); MUTED = (133, 117, 95)
CREAM = (247, 241, 227); AMBER_L = (249, 240, 214); GREEN_L = (236, 246, 236)
RED_L = (254, 242, 242); COBALT = (29, 78, 216); COBALT_L = (239, 246, 255)

PAGE_W, PAGE_H = 210, 297
M = 18
W = PAGE_W - 2 * M


def clean(t):
    for k, v in _REPL.items():
        t = t.replace(k, v)
    t = _EMOJI_RE.sub("", t)
    return re.sub(r"\s+", " ", t).strip()


class Book(FPDF):
    def __init__(self, meta):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.meta = meta
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
        self.cell(0, 5, self.meta.get("identity", ""), new_x="LMARGIN", new_y="NEXT", align="L")
        self.cell(0, 5, f"Page {self.page_no()}", align="R")

    # ── primitives ──
    def para(self, t, size=10.8, lh=6.3, space=3.2):
        self.set_font("DJ", "", size)
        self.set_text_color(*BODY)
        self.multi_cell(W, lh, clean(t), new_x="LMARGIN", new_y="NEXT")
        self.ln(space)

    def bullets(self, items, marker="✓", color=GREEN, size=10.8):
        for it in items:
            y = self.get_y()
            self.set_font("DJ", "B", size - 1)
            self.set_text_color(*color)
            self.set_xy(M, y)
            self.cell(7, 6.2, marker)
            self.set_font("DJ", "", size)
            self.set_text_color(*BODY)
            self.multi_cell(W - 7, 6.2, clean(it), new_x="LMARGIN", new_y="NEXT")
            self.ln(1.4)

    def numbered(self, items, size=10.8):
        for i, it in enumerate(items, 1):
            y = self.get_y()
            self.set_font("DJ", "B", size)
            self.set_text_color(*AMBER)
            self.set_xy(M, y)
            self.cell(9, 6.2, f"{i}.")
            self.set_font("DJ", "", size)
            self.set_text_color(*BODY)
            self.multi_cell(W - 9, 6.2, clean(it), new_x="LMARGIN", new_y="NEXT")
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

    def _box(self, lines_fn, label, bg, fg, h):
        y = self.get_y()
        if y + h > PAGE_H - 24:
            self.add_page()
            y = self.get_y()
        self.set_fill_color(*bg)
        self.rect(M, y, W, h, "F")
        self.set_xy(M + 6, y + 4)
        self.set_font("DJ", "B", 8.5)
        self.set_text_color(*fg)
        self.cell(0, 5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_xy(M + 6, y + 10)
        lines_fn()
        self.set_y(y + h + 4)

    def _height(self, text, lh, size, width):
        self.set_font("DJ", "", size)
        lines = self.multi_cell(width, lh, clean(text), dry_run=True, output="LINES")
        return len(lines) * lh + 16

    def task_box(self, text):
        h = self._height(text, 6, 10.5, W - 12)
        def draw():
            self.set_font("DJ", "", 10.5)
            self.set_text_color(*INK)
            self.multi_cell(W - 12, 6, clean(text), new_x="LMARGIN", new_y="NEXT")
        self._box(draw, "DO THIS NOW", AMBER_L, AMBER, h)

    def myth_box(self, items):
        text = "\n".join(items)
        h = len(items) * 6.5 + 16
        def draw():
            self.set_font("DJ", "", 10.5)
            for it in items:
                self.set_text_color(*RED)
                self.set_font("DJ", "B", 10)
                self.cell(6, 6.2, "✗")
                self.set_font("DJ", "", 10.5)
                self.set_text_color(*INK)
                self.multi_cell(W - 18, 6.2, clean(it), new_x="LMARGIN", new_y="NEXT")
                self.ln(0.6)
        self._box(draw, "WHAT THIS IS NOT", RED_L, RED, h)

    def script_block(self, text):
        h = self._height(text, 5.6, 9.8, W - 16)
        def draw():
            self.set_font("DJ", "", 9.8)
            self.set_text_color(*COBALT)
            self.multi_cell(W - 16, 5.6, clean(text), new_x="LMARGIN", new_y="NEXT")
        self._box(draw, "WORD-FOR-WORD TEMPLATE", COBALT_L, COBALT, h)

    def callout(self, text, label, link=None):
        h = self._height(text, 6, 10.5, W - 12)
        def draw():
            self.set_font("DJ", "", 10.5)
            self.set_text_color(*COBALT if link else INK)
            self.multi_cell(W - 12, 6, clean(text), new_x="LMARGIN", new_y="NEXT", link=link)
        self._box(draw, label, GREEN_L, GREEN, h)

    def references(self, refs):
        if not refs:
            return
        self.h2("Sources & References")
        for label, url in refs:
            self.set_font("DJ", "", 9.5)
            self.set_text_color(*COBALT)
            self.multi_cell(W, 5.5, f"{label} — {url}", new_x="LMARGIN", new_y="NEXT", link=url)
        self.ln(2)

    # ── structural pages ──
    def cover(self):
        m = self.meta
        self.add_page()
        self.set_fill_color(*INK)
        self.rect(0, 0, PAGE_W, PAGE_H, "F")
        self.set_font("DJ", "B", 11)
        self.set_text_color(255, 176, 32)
        self.cell(0, 10, m.get("title_accent", ""), new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(30)
        self.set_font("DJS", "B", 38)
        self.set_text_color(*CREAM)
        self.multi_cell(0, 17, clean(m["title"]), align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        self.set_font("DJ", "", 13)
        self.set_text_color(*MUTED)
        self.multi_cell(0, 8, clean(m.get("subtitle", "")), align="C", new_x="LMARGIN", new_y="NEXT")
        if m.get("price_line"):
            self.ln(8)
            self.set_font("DJ", "B", 15)
            self.set_text_color(255, 176, 32)
            self.cell(0, 10, m["price_line"], new_x="LMARGIN", new_y="NEXT", align="C")
            self.set_font("DJ", "", 10)
            self.set_text_color(*MUTED)
            self.cell(0, 6, m.get("terms", ""), new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(8)
        self.set_font("DJ", "", 10)
        self.set_text_color(*CREAM)
        self.cell(0, 6, f"by {m.get('author', '')}", new_x="LMARGIN", new_y="NEXT", align="C")

    def orientation(self, o):
        self.add_page()
        self.h1("What this book IS")
        self.bullets(o.get("is", []))
        self.ln(2)
        self.h1("What this book is NOT")
        self.bullets(o.get("is_not", []), marker="✗", color=RED)
        if o.get("audience"):
            self.ln(2)
            self.h2("Who this is for")
            self.bullets(o["audience"])
        if o.get("how_to_use"):
            self.ln(2)
            self.task_box(o["how_to_use"])

    def contents(self, chapters):
        self.add_page()
        self.h1("Contents")
        for i, ch in enumerate(chapters, 1):
            self.set_font("DJ", "B", 12)
            self.set_text_color(*INK)
            self.cell(0, 8, f"{i}.  {ch['title']}", new_x="LMARGIN", new_y="NEXT")

    def chapter(self, n, ch):
        self.add_page()
        self.h2(f"CHAPTER {n}")
        self.h1(ch["title"])
        if ch.get("promise"):
            self.para(ch["promise"])
        if ch.get("outcomes"):
            self.bullets(ch["outcomes"])
        for sec in ch.get("sections", []):
            self.h2(sec["head"])
            for p in sec.get("paras", []):
                self.para(p)
            if sec.get("bullets"):
                self.bullets(sec["bullets"])
            if sec.get("numbered"):
                self.numbered(sec["numbered"])
        if ch.get("myths"):
            self.myth_box(ch["myths"])
        if ch.get("script"):
            self.script_block(ch["script"])
        if ch.get("task"):
            self.task_box(ch["task"])
        self.references(ch.get("refs", []))

    def plan(self, plan):
        self.add_page()
        self.h1(plan.get("title", "Your 30-Day Action Plan"))
        for wk in plan.get("weeks", []):
            self.h2(wk["label"])
            for day in wk.get("days", []):
                self.set_font("DJ", "", 10.5)
                self.set_text_color(*BODY)
                self.multi_cell(W, 6, clean(day), new_x="LMARGIN", new_y="NEXT")
                self.ln(0.8)

    def worksheets(self, sheets):
        for ws in sheets:
            self.add_page()
            self.h2(f"FROM CHAPTER {ws.get('chapter', 1)}")
            self.h1(ws["title"])
            for prompt in ws.get("prompts", []):
                self.set_font("DJ", "B", 11)
                self.set_text_color(*INK)
                self.multi_cell(W, 7, clean(prompt), new_x="LMARGIN", new_y="NEXT")
                for _ in range(2):
                    y = self.get_y()
                    self.set_draw_color(214, 205, 186)
                    self.line(M, y + 5, PAGE_W - M, y + 5)
                    self.ln(8)
                self.ln(2)

    def tracker(self, rows):
        self.add_page()
        self.h1("Daily Tracker")
        cols = [28, 60, 30, 30, 26]
        heads = ["Date", "Action done", "In", "Out", "Lesson"]
        def head():
            self.set_font("DJ", "B", 9)
            self.set_text_color(*INK)
            x = M
            for w_, t in zip(cols, heads):
                self.set_xy(x, self.get_y())
                self.cell(w_, 7, t)
                x += w_
            self.ln(7)
        head()
        self.set_draw_color(214, 205, 186)
        for i in range(rows):
            if self.get_y() > PAGE_H - 26:
                self.add_page()
                head()
            y = self.get_y()
            x = M
            for w_ in cols:
                self.rect(x, y, w_, 8)
                x += w_
            self.ln(8)

    def appendix(self, chapters):
        self.add_page()
        self.h1("Appendix — Every Source, By Chapter")
        for i, ch in enumerate(chapters, 1):
            if not ch.get("refs"):
                continue
            self.h2(f"Chapter {i} — {ch['title']}")
            for label, url in ch["refs"]:
                self.set_font("DJ", "", 9.5)
                self.set_text_color(*COBALT)
                self.multi_cell(W, 5.5, f"{label} — {url}", new_x="LMARGIN", new_y="NEXT", link=url)

    def copyright_page(self):
        self.add_page()
        self.h2("Copyright & Disclaimer")
        self.para(self.meta.get("disclaimer",
                                "Educational only. Results depend on your work, market and timing."),
                  size=9.5)
        self.para(f"© {self.meta.get('identity', '')}", size=9.5)


def build(outline, out, paid=True, sample=True):
    meta = outline["meta"]
    chapters = outline["chapters"]
    os.makedirs(out, exist_ok=True)
    if paid:
        pdf = Book(meta)
        pdf.cover()
        pdf.contents(chapters)
        if outline.get("orientation"):
            pdf.orientation(outline["orientation"])
        for i, ch in enumerate(chapters, 1):
            pdf.chapter(i, ch)
        if outline.get("plan"):
            pdf.plan(outline["plan"])
        for ws in outline.get("worksheets", []):
            pdf.worksheets([ws])
        if outline.get("tracker_rows"):
            pdf.tracker(outline["tracker_rows"])
        pdf.appendix(chapters)
        pdf.copyright_page()
        p = os.path.join(out, "book.pdf")
        pdf.output(p)
        print(f"book: {p} ({os.path.getsize(p)//1024} KB, {pdf.pages_count} pages)")
    if sample:
        pdf = Book(meta)
        pdf.add_page()
        pdf.h2("FREE SAMPLE — CHAPTER 1")
        ch = chapters[0]
        pdf.h1(ch["title"])
        if ch.get("promise"):
            pdf.para(ch["promise"])
        for sec in ch.get("sections", []):
            pdf.h2(sec["head"])
            for p_ in sec.get("paras", []):
                pdf.para(p_)
            if sec.get("bullets"):
                pdf.bullets(sec["bullets"])
        pdf.add_page()
        pdf.ln(18)
        pdf.set_font("DJS", "B", 22)
        pdf.set_text_color(*INK)
        pdf.multi_cell(0, 11, f"This was Chapter 1 of {len(chapters)}.", align="C",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.callout(f"Get the complete book at {meta.get('cta_url', '')}",
                    meta.get("cta_label", "GET THE FULL BOOK"), link=meta.get("cta_url"))
        p = os.path.join(out, "sample.pdf")
        pdf.output(p)
        print(f"sample: {p} ({os.path.getsize(p)//1024} KB, {pdf.pages_count} pages)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    if not args:
        print(__doc__)
        sys.exit(1)
    path = args[0]
    out = "/tmp/ebook-out"
    if "--out" in args:
        out = args[args.index("--out") + 1]
    with open(path) as f:
        outline = json.load(f)
    build(outline, out,
          paid="--sample-only" not in args,
          sample="--paid-only" not in args)
