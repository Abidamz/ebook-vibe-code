#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config-driven motion-graphics ad renderer (see ../SKILL.md).

Renders ONE timeline into several aspect ratios by drawing frames with Pillow
and piping raw RGB into ffmpeg (H.264 + AAC), muxed with a voiceover WAV.

Usage:
    python render_ad.py all                 # render every format in CONFIG["formats"]
    python render_ad.py square              # render one format
    python render_ad.py preview 3.0 square  # write ONE still frame to ./preview_<fmt>_<t>.png

Edit CONFIG below for a new project: palette, fonts, assets, copy, timing, vo path.
"""
import os
import math
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

HERE = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────────
# CONFIG — edit per project. Paths for images are relative to IMG_ROOT;
# prefix "web/" to resolve from IMG_ROOT/web.
# ─────────────────────────────────────────────────────────────────────
CONFIG = {
    # repo root three levels up when this file lives in <repo>/skills/<name>/scripts/
    "root": os.path.dirname(os.path.dirname(os.path.dirname(HERE))),
    "img_root": None,            # defaults to <root>/assets/img
    "out_dir": None,             # defaults to <root>/delivery/ads
    "vo": None,                  # defaults to <out_dir>/vo.wav
    "fps": 30,
    "duration": 45.0,
    "formats": {
        "vertical": (1080, 1920),
        "square": (1080, 1080),
        "landscape": (1920, 1080),
    },
    "palette": {
        "ink": (28, 24, 18), "ink2": (40, 34, 26),
        "cream": (247, 241, 227), "cream2": (238, 230, 211),
        "gold": (255, 176, 32), "amber": (180, 83, 9),
        "cobalt": (29, 78, 216), "llink": (147, 197, 253),
        "green": (22, 101, 52), "red": (220, 38, 38),
        "muted": (133, 117, 95),
    },
    "fonts": {
        "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "sansb": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "serifb": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    },
    "assets": {
        "cover": "selar-cover.png",
        "steps": [
            ["web/step1-create.jpg", "1. CREATE", "a digital product"],
            ["web/step2-flyers.jpg", "2. RAISE", "your first ₦30,000"],
            ["web/step3-ads.jpg", "3. RUN ADS", "that actually sell"],
            ["web/step4-scale.jpg", "4. SCALE", "rinse. repeat. scale."],
        ],
    },
    "copy": {
        "kicker": "MAKE",
        "big": "₦5K–₦10K",
        "punch": "EVERY. SINGLE. DAY.",
        "tag": "THE ₦5K–₦10K DIGITAL PRODUCT PLAYBOOK",
        "objections": ["NOT LUCK.", "NOT A GET-RICH-QUICK SCHEME.", "NOT FOLLOWERS YOU DON'T HAVE."],
        "pivot_head": "JUST A SYSTEM.",
        "pivot_l1": "One you can run entirely",
        "pivot_l2": "from your phone.",
        "ease_head1": "WRITTEN FOR",
        "ease_head2": "COMPLETE BEGINNERS.",
        "checks": ["No tech skills.", "No big budget.", "No followers needed."],
        "guarantee": "7-DAY MONEY-BACK GUARANTEE",
        "title1": "THE DIGITAL PRODUCT",
        "title2": "CASH MACHINE",
        "price_old": "₦10,000",
        "price_new": "₦3,500",
        "terms": "One-time payment · Instant download",
        "cta": "TAP THE LINK · GET THE BOOK",
        "url": "selar.com/27778q2k78",
        "footer": "The ₦5K–₦10K Digital Product Playbook",
    },
    "timing": [
        (0.0, 4.6, "hook"),
        (4.6, 10.2, "objections"),
        (10.2, 15.0, "pivot"),
        (15.0, 27.0, "system"),
        (27.0, 33.0, "ease"),
        (33.0, 39.3, "reveal"),
        (39.3, 45.0, "cta"),
    ],
}

P = CONFIG["palette"]
F = CONFIG["fonts"]
C = CONFIG["copy"]
IMG_ROOT = CONFIG["img_root"] or os.path.join(CONFIG["root"], "assets", "img")
OUT = CONFIG["out_dir"] or os.path.join(CONFIG["root"], "delivery", "ads")
VO = CONFIG["vo"] or os.path.join(OUT, "vo.wav")
FPS = CONFIG["fps"]
DUR = CONFIG["duration"]
N_FRAMES = int(FPS * DUR)


# ── easing ──────────────────────────────────────────────────────────
def c01(x):
    return max(0.0, min(1.0, x))

def eo(x):
    x = c01(x); return 1 - (1 - x) ** 3

def eob(x):
    x = c01(x); c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def eio(x):
    x = c01(x)
    return 2 * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 2 / 2

def pr(t, start, dur):
    return c01((t - start) / dur)

def lerp(a, b, x):
    return a + (b - a) * x


class FontCache:
    _c = {}

    @classmethod
    def get(cls, path, size):
        k = (path, int(size))
        if k not in cls._c:
            cls._c[k] = ImageFont.truetype(path, int(size))
        return cls._c[k]


def fnt(kind, px):
    return FontCache.get(F[kind], px)


class Ctx:
    def __init__(self, name, W, H):
        self.name, self.W, self.H = name, W, H
        self.wide, self.tall = W > H, H > W
        self._imgs = {}
        self._build()

    def img(self, rel):
        if rel not in self._imgs:
            base = IMG_ROOT if not rel.startswith("web/") else os.path.join(IMG_ROOT, "web")
            self._imgs[rel] = Image.open(os.path.join(base, rel.split("web/")[-1])).convert("RGB")
        return self._imgs[rel]

    def _build(self):
        W, H = self.W, self.H

        def grad(top, bot):
            im = Image.new("RGB", (1, H))
            d = ImageDraw.Draw(im)
            for y in range(H):
                f = y / max(1, H - 1)
                d.point((0, y), tuple(int(lerp(top[i], bot[i], f)) for i in range(3)))
            return im.resize((W, H))
        self.grad_dark = grad(P["ink2"], (16, 13, 10))
        self.grad_cream = grad(P["cream"], P["cream2"])

        g = Image.new("L", (512, 512), 0)
        gd = ImageDraw.Draw(g)
        for r in range(256, 0, -8):
            gd.ellipse([256 - r, 256 - r, 256 + r, 256 + r], fill=int(90 * (1 - r / 256.0) ** 2))
        tint = Image.new("RGBA", (512, 512), tuple(P["gold"]) + (0,))
        tint.putalpha(g)
        self.glow_gold = tint

        vig = Image.new("L", (W, H), 0)
        vd = ImageDraw.Draw(vig)
        vd.rectangle([0, 0, W, H], fill=70)
        m = min(W, H) * 0.42
        vd.ellipse([-m, -m, W + m, H + m], fill=0)
        vig = vig.filter(ImageFilter.GaussianBlur(min(W, H) * 0.10))
        self.vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.vignette.putalpha(vig)

        rnd = random.Random(7)
        grain = Image.new("L", (W, H))
        grain.putdata([rnd.randrange(0, 26) for _ in range(W * H)])
        self.grain = Image.new("RGBA", (W, H), (255, 255, 255, 0))
        self.grain.putalpha(grain)

    def new(self, dark=True):
        self.im = (self.grad_dark if dark else self.grad_cream).copy()
        self.d = ImageDraw.Draw(self.im, "RGBA")
        return self

    def glow(self, x, y, scale=1.0, alpha=1.0):
        s = int(900 * scale)
        sp = self.glow_gold.resize((s, s))
        if alpha < 1.0:
            sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
        self.im.paste(sp, (int(x - s / 2), int(y - s / 2)), sp)
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def finish(self, t=None):
        self.im.paste(self.vignette, (0, 0), self.vignette)
        self.im.paste(self.grain, (0, 0), self.grain)
        return self.im

    # ── text ─
    def tw(self, s, font):
        b = self.d.textbbox((0, 0), s, font=font)
        return b[2] - b[0], b[3] - b[1]

    def text(self, x, y, s, font, fill, anchor="la", alpha=1.0, shadow=None):
        if alpha <= 0:
            return
        col = fill if alpha >= 1 else tuple(list(fill) + [int(255 * alpha)])
        if shadow:
            ox, oy, scol = shadow
            self.d.text((x + ox, y + oy), s, font=font, fill=scol, anchor=anchor)
        self.d.text((x, y), s, font=font, fill=col, anchor=anchor)

    def text_c(self, cx, y, s, font, fill, alpha=1.0, shadow=None):
        self.text(cx, y, s, font, fill, anchor="ma", alpha=alpha, shadow=shadow)

    def stagger(self, cx, y, s, font, fill, k, gap=0.045):
        n = len(s)
        w, h = self.tw(s, font)
        x = cx - w / 2
        for i, ch in enumerate(s):
            p = eo((k - i * gap) / 0.35) if k > i * gap else 0.0
            if p <= 0:
                continue
            self.text(x, y + (1 - p) * h * 0.9, ch, font, fill, alpha=p)
            x += self.d.textlength(ch, font=font)

    def fit(self, kind, text, maxw, start):
        """Largest font (<= start px) whose width fits maxw. ALWAYS use for display type."""
        px = int(start)
        f = fnt(kind, px)
        while px > 20:
            f = fnt(kind, px)
            if self.tw(text, f)[0] <= maxw:
                return f
            px -= 4
        return f

    # ── shapes / images ──
    def rrect(self, box, r, fill=None, outline=None, width=1, alpha=1.0):
        if fill and alpha < 1:
            fill = tuple(list(fill) + [int(255 * alpha)])
        self.d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

    def bar(self, x, y, w, h, fill, frac=1.0, r=None):
        r = r if r is not None else h / 2
        if frac <= 0:
            return
        self.d.rounded_rectangle([x, y, x + w * c01(frac), y + h], radius=r, fill=fill)

    def card(self, im, box, radius=24, shadow=True, scale=1.0):
        x0, y0, x1, y1 = [int(v) for v in box]
        bw, bh = x1 - x0, y1 - y0
        if bw <= 0 or bh <= 0:
            return
        if scale != 1.0:
            cw, ch = int(bw * scale), int(bh * scale)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            x0, y0 = int(cx - cw / 2), int(cy - ch / 2)
            bw, bh = cw, ch
        src = im.convert("RGB")
        sw, sh = src.size
        sf = max(bw / sw, bh / sh)
        src = src.resize((int(sw * sf), int(sh * sf)), Image.LANCZOS)
        nw, nh = src.size
        lx, ly = (nw - bw) // 2, (nh - bh) // 2
        src = src.crop((lx, ly, lx + bw, ly + bh))
        mask = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw, bh], radius=radius, fill=255)
        if shadow:
            shim = Image.new("RGBA", (bw + 60, bh + 60), (0, 0, 0, 0))
            ImageDraw.Draw(shim).rounded_rectangle([30, 34, bw + 30, bh + 34], radius=radius,
                                                   fill=(0, 0, 0, 130))
            shim = shim.filter(ImageFilter.GaussianBlur(18))
            self.im.paste(shim, (x0 - 30, y0 - 34), shim)
        self.im.paste(src, (x0, y0), mask)
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def shine(self, box, k):
        if k <= 0 or k >= 1:
            return
        x0, y0, x1, y1 = [int(v) for v in box]
        bw, bh = x1 - x0, y1 - y0
        layer = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        w = int(bw * 0.22)
        px = int(lerp(-w * 2, bw + w, k))
        for i in range(w):
            a = int(70 * math.sin(math.pi * i / w))
            ld.line([(px + i, -10), (px + i - int(bh * 0.35), bh + 10)],
                    fill=(255, 255, 255, a), width=1)
        self.im.paste(layer, (x0, y0), layer)
        self.d = ImageDraw.Draw(self.im, "RGBA")


# ── scenes (7-beat arc; read strings from CONFIG["copy"]) ────────────
def sc_hook(c, t):
    c.new(dark=True)
    W, H = c.W, c.H
    c.glow(W * 0.5, H * 0.42, scale=1.5, alpha=0.9 + 0.1 * math.sin(t * 3))
    cy = H * 0.45 if c.tall else H * 0.42
    c.text_c(W / 2, cy - H * 0.11, C["kicker"], fnt("sansb", H * 0.035), P["cream"],
             alpha=eo(pr(t, 0.2, 0.5)))
    lock = pr(t, 1.5, 0.5)
    if lock < 1:
        val = int(lerp(500, 10000, eo(pr(t, 0.15, 1.35))))
        s = f"₦{val:,}"
        f = c.fit("serifb", s, W * 0.88, H * 0.16)
        c.text_c(W / 2, cy, s, f, P["gold"], shadow=(0, 6, (0, 0, 0, 160)))
        tw_, th_ = c.tw(s, f)
    else:
        k = eob(pr(t, 1.5, 0.6))
        fitted = c.fit("serifb", C["big"], W * 0.88, H * 0.17)
        f = fnt("serifb", int(fitted.size * lerp(0.8, 1.0, c01(k))))
        c.text_c(W / 2, cy, C["big"], f, P["gold"], alpha=c01(k * 1.4),
                 shadow=(0, 6, (0, 0, 0, 160)))
        tw_, th_ = c.tw(C["big"], fitted)
    uw = min(W * 0.42, tw_ * 0.8)
    uy = cy + th_ + H * 0.015
    c.bar(W / 2 - uw / 2, uy, uw, max(4, H * 0.006), P["amber"], frac=eo(pr(t, 1.9, 0.6)))
    pf = c.fit("sansb", C["punch"], W * 0.90, H * 0.052)
    c.stagger(W / 2, uy + H * 0.03, C["punch"], pf, P["cream"], eo(pr(t, 2.5, 0.9)))
    if c.tall:
        tf = c.fit("sansb", C["tag"], W * 0.84, H * 0.022)
        c.text_c(W / 2, H * 0.86, C["tag"], tf, P["muted"], alpha=eo(pr(t, 2.8, 0.6)))
    rnd = random.Random(3)
    for i in range(14):
        sp = 0.25 + rnd.random() * 0.5
        ph = rnd.random()
        px_ = W * (0.12 + 0.76 * ((ph + t * sp * 0.12) % 1))
        py_ = H * (1.05 - ((t * sp * 0.22 + ph) % 1.15))
        a = int(120 * c01(math.sin(math.pi * c01(py_ / H))))
        c.text(px_, py_, "₦", fnt("sansb", H * 0.02), P["gold"], alpha=a / 255)


def sc_objections(c, t):
    c.new(dark=True)
    W, H = c.W, c.H
    c.glow(W * 0.5, H * 0.5, scale=1.2, alpha=0.5)
    fs = H * 0.045 if not c.wide else H * 0.052
    y0 = H * (0.34 if c.tall else 0.38)
    for i, ln in enumerate(C["objections"]):
        k = eo(pr(t, 0.3 + i * 1.5, 0.55))
        if k <= 0:
            continue
        y = y0 + i * fs * 2.1
        x = W * 0.5 - (c.tw(ln, fnt("sansb", fs))[0] + fs * 1.6) / 2 + (1 - k) * W * 0.06
        mx, my = x, y + fs * 0.5
        r = fs * 0.42 * eob(pr(t, 0.3 + i * 1.5 + 0.1, 0.4))
        c.d.line([mx - r, my - r, mx + r, my + r], fill=P["red"], width=int(fs * 0.16))
        c.d.line([mx - r, my + r, mx + r, my - r], fill=P["red"], width=int(fs * 0.16))
        c.text(x + fs * 0.9, y, ln, fnt("sansb", fs), P["cream"], alpha=k)


def sc_pivot(c, t):
    c.new(dark=False)
    W, H = c.W, c.H
    c.glow(W * 0.5, H * 0.4, scale=1.3, alpha=0.25)
    k = eob(pr(t, 0.2, 0.6))
    c.text_c(W / 2, H * 0.36, C["pivot_head"],
             fnt("serifb", H * 0.085 * lerp(0.7, 1, k)), P["ink"], alpha=c01(k * 1.3))
    uw = W * 0.30
    c.bar(W / 2 - uw / 2, H * 0.50, uw, max(4, H * 0.006), P["amber"], frac=eo(pr(t, 0.8, 0.5)))
    k2 = eo(pr(t, 1.4, 0.6))
    c.text_c(W / 2, H * 0.56, C["pivot_l1"], fnt("sans", H * 0.036), P["ink2"], alpha=k2)
    c.text_c(W / 2, H * 0.615, C["pivot_l2"], fnt("sansb", H * 0.040), P["cobalt"], alpha=k2)
    pw, ph = H * 0.05, H * 0.09
    px, py = W / 2 - pw / 2, H * 0.70
    k3 = eob(pr(t, 2.2, 0.5))
    c.rrect([px, py, px + pw, py + ph], pw * 0.22, fill=P["ink"], alpha=c01(k3))
    c.rrect([px + pw * 0.14, py + ph * 0.10, px + pw * 0.86, py + ph * 0.80],
            pw * 0.10, fill=P["cream"], alpha=c01(k3))


def sc_system(c, t):
    c.new(dark=False)
    W, H = c.W, c.H
    beats = C["steps"]
    n = len(beats)
    seg = 12.0 / n
    idx = min(n - 1, int(t / seg))
    lt = t - idx * seg
    rel, head, sub = beats[idx]
    im = c.img(rel)
    enter = eo(pr(lt, 0.0, 0.5))
    exitk = eo(pr(lt, seg - 0.35, 0.35))
    label = f"STEP {idx + 1}/{n}"
    if c.wide:
        iw = W * 0.46
        bx = [W * 0.50, H * 0.20, W * 0.50 + iw, H * 0.20 + iw * 0.56]
        c.card(im, bx, radius=28, scale=lerp(0.92, 1.0, enter) * lerp(1, 1.05, exitk))
        tx, hy = W * 0.08, H * 0.36
        c.text(tx, hy - H * 0.10, label, fnt("sansb", H * 0.026), P["amber"], alpha=enter)
        c.text(tx, hy, head, fnt("serifb", H * 0.075), P["ink"], alpha=enter)
        c.text(tx, hy + H * 0.10, sub, fnt("sans", H * 0.040), P["ink2"], alpha=eo(pr(lt, 0.25, 0.5)))
        c.bar(tx, hy + H * 0.17, W * 0.30, H * 0.006, P["amber"], frac=eo(pr(lt, 0.3, 0.6)))
    else:
        iw = W * 0.74
        ih = iw * 0.56
        bx = [W / 2 - iw / 2, H * 0.14, W / 2 + iw / 2, H * 0.14 + ih]
        c.card(im, bx, radius=28, scale=lerp(0.92, 1.0, enter) * lerp(1, 1.05, exitk))
        c.text_c(W / 2, H * 0.14 + ih + H * 0.05, label, fnt("sansb", H * 0.026), P["amber"], alpha=enter)
        c.text_c(W / 2, H * 0.14 + ih + H * 0.09, head, fnt("serifb", H * 0.070), P["ink"], alpha=enter)
        c.text_c(W / 2, H * 0.14 + ih + H * 0.185, sub, fnt("sans", H * 0.036), P["ink2"],
                 alpha=eo(pr(lt, 0.25, 0.5)))
        c.bar(W / 2 - W * 0.2, H * 0.14 + ih + H * 0.245, W * 0.40, H * 0.006, P["amber"],
              frac=eo(pr(lt, 0.3, 0.6)))
    dy = H * 0.93
    for i in range(n):
        cx = W / 2 + (i - (n - 1) / 2) * W * 0.045
        fill = P["amber"] if i <= idx else (200, 190, 170)
        r = W * 0.008 * (1.4 if i == idx else 1.0)
        c.d.ellipse([cx - r, dy - r, cx + r, dy + r], fill=fill)


def sc_ease(c, t):
    c.new(dark=True)
    W, H = c.W, c.H
    c.glow(W * 0.5, H * 0.45, scale=1.2, alpha=0.45)
    c.text_c(W / 2, H * 0.22, C["ease_head1"], fnt("sansb", H * 0.032), P["muted"],
             alpha=eo(pr(t, 0.1, 0.5)))
    c.text_c(W / 2, H * 0.27, C["ease_head2"], fnt("serifb", H * 0.062), P["cream"],
             alpha=eo(pr(t, 0.2, 0.6)))
    fs = H * 0.036
    y = H * 0.42
    for i, ln in enumerate(C["checks"]):
        k = eo(pr(t, 1.0 + i * 0.7, 0.5))
        if k <= 0:
            continue
        w = c.tw(ln, fnt("sans", fs))[0]
        x = W / 2 - (w + fs * 1.8) / 2
        yy = y + i * fs * 1.9
        r = fs * 0.45 * eob(pr(t, 1.0 + i * 0.7 + 0.08, 0.4))
        c.d.ellipse([x, yy, x + 2 * r, yy + 2 * r], fill=P["green"])
        c.d.line([x + r * 0.5, yy + r, x + r * 0.9, yy + r * 1.4], fill=(255, 255, 255), width=int(fs * 0.12))
        c.d.line([x + r * 0.9, yy + r * 1.4, x + r * 1.55, yy + r * 0.55], fill=(255, 255, 255), width=int(fs * 0.12))
        c.text(x + fs * 1.2, yy - fs * 0.12, ln, fnt("sans", fs), P["cream"], alpha=k)
    k = eob(pr(t, 3.6, 0.6))
    if k > 0:
        bw, bh = W * 0.62, H * 0.075
        bx, by = W / 2 - bw / 2, H * 0.72
        c.rrect([bx, by, bx + bw, by + bh], bh / 2, outline=P["gold"],
                width=max(2, int(H * 0.003)), alpha=c01(k))
        c.text_c(W / 2, by + bh / 2 - fs * 0.42, C["guarantee"], fnt("sansb", fs * 0.8),
                 P["gold"], alpha=c01(k))


def sc_reveal(c, t):
    c.new(dark=True)
    W, H = c.W, c.H
    cover = c.img(C["assets_cover"] if "assets_cover" in C else CONFIG["assets"]["cover"])
    leftw = None
    if c.wide:
        side = H * 0.62
        cx = W * 0.70
        bx = [cx - side / 2, H * 0.5 - side / 2, cx + side / 2, H * 0.5 + side / 2]
        tx = W * 0.06
        leftw = (cx - side / 2) - tx - W * 0.03
    elif c.tall:
        side = W * 0.66
        bx = [W / 2 - side / 2, H * 0.24 - side / 2, W / 2 + side / 2, H * 0.24 + side / 2]
        tx = None
    else:
        side = H * 0.60
        bx = [W / 2 - side / 2, H * 0.42 - side / 2, W / 2 + side / 2, H * 0.42 + side / 2]
        tx = None
    k = eob(pr(t, 0.2, 0.9))
    c.card(cover, bx, radius=30, scale=lerp(0.75, 1.0, k))
    c.shine(bx, pr(t, 1.2, 1.0))
    c.glow((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2, scale=1.6, alpha=0.35)
    if tx is None:
        ty = H * 0.62 if c.tall else H * 0.80
        c.text_c(W / 2, ty, C["title1"], fnt("serifb", H * 0.050), P["cream"], alpha=eo(pr(t, 1.4, 0.6)))
        c.text_c(W / 2, ty + H * 0.062, C["title2"], fnt("serifb", H * 0.062), P["gold"],
                 alpha=eo(pr(t, 1.6, 0.6)))
    else:
        f1 = c.fit("serifb", C["title1"], leftw, H * 0.052)
        f2 = c.fit("serifb", C["title2"], leftw, H * 0.070)
        c.text(tx, H * 0.34, C["title1"], f1, P["cream"], alpha=eo(pr(t, 1.4, 0.6)))
        c.text(tx, H * 0.43, C["title2"], f2, P["gold"], alpha=eo(pr(t, 1.6, 0.6)))
        c.bar(tx, H * 0.56, leftw * 0.55, H * 0.006, P["amber"], frac=eo(pr(t, 1.9, 0.6)))


def sc_cta(c, t):
    c.new(dark=True)
    W, H = c.W, c.H
    c.glow(W * 0.5, H * 0.5, scale=1.6, alpha=0.7 + 0.15 * math.sin(t * 4))
    y = H * 0.16 if c.tall else H * 0.20
    fo = fnt("sansb", H * 0.040)
    wo, ho = c.tw(C["price_old"], fo)
    c.text_c(W / 2, y, C["price_old"], fo, P["muted"])
    c.d.line([W / 2 - wo / 2, y + ho / 2, W / 2 + wo / 2, y + ho / 2], fill=P["red"],
             width=max(3, int(H * 0.004)))
    k = eob(pr(t, 0.4, 0.7))
    c.text_c(W / 2, y + H * 0.075, C["price_new"], fnt("serifb", H * 0.13 * lerp(0.7, 1, k)),
             P["gold"], alpha=c01(k * 1.4), shadow=(0, 8, (0, 0, 0, 160)))
    c.text_c(W / 2, y + H * 0.235, C["terms"], fnt("sans", H * 0.028), P["cream"],
             alpha=eo(pr(t, 1.0, 0.6)))
    pulse = 1.0 + 0.03 * math.sin((t - 1.4) * 6)
    bw, bh = W * 0.62 * pulse, H * 0.085 * pulse
    bx, by = W / 2 - bw / 2, H * (0.60 if c.tall else 0.62)
    kb = eob(pr(t, 1.4, 0.6))
    if kb > 0:
        c.rrect([bx, by, bx + bw, by + bh], bh / 2, fill=P["gold"], alpha=c01(kb))
        c.text_c(W / 2, by + bh / 2 - H * 0.020, C["cta"], fnt("sansb", H * 0.030), P["ink"],
                 alpha=c01(kb))
    c.text_c(W / 2, by + bh + H * 0.035, C["url"], fnt("sansb", H * 0.026), P["llink"],
             alpha=eo(pr(t, 1.9, 0.6)))
    c.text_c(W / 2, H * 0.93, C["footer"], fnt("sans", H * 0.022), P["muted"],
             alpha=eo(pr(t, 2.2, 0.6)))


SCENE_FN = {"hook": sc_hook, "objections": sc_objections, "pivot": sc_pivot,
            "system": sc_system, "ease": sc_ease, "reveal": sc_reveal, "cta": sc_cta}


def frame(ctx_cache, name, t):
    if name not in ctx_cache:
        ctx_cache[name] = Ctx(name, *CONFIG["formats"][name])
    c = ctx_cache[name]
    fn, lt = CONFIG["timing"][0][2], t
    for (s0, s1, nm) in CONFIG["timing"]:
        if s0 <= t < s1:
            fn, lt = nm, t - s0
            break
    SCENE_FN[fn](c, lt)
    return c.finish(t)


def render(name):
    W, H = CONFIG["formats"][name]
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"ad-{name}.mp4")
    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", VO, "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-t", str(DUR), "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cache = {}
    for f in range(N_FRAMES):
        img = frame(cache, name, f / FPS)
        proc.stdin.write(img.tobytes())
        if f % 150 == 0:
            print(f"[{name}] frame {f}/{N_FRAMES}", flush=True)
    proc.stdin.close()
    proc.wait()
    print(f"[{name}] DONE -> {out}", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "preview":
        t = float(args[1]) if len(args) > 1 else 2.0
        fmt = args[2] if len(args) > 2 else "square"
        img = frame({}, fmt, t)
        p = os.path.join(os.getcwd(), f"preview_{fmt}_{t:.0f}.png")
        img.save(p)
        print(p)
    else:
        which = args[0] if args else "all"
        for nm in (list(CONFIG["formats"]) if which == "all" else [which]):
            render(nm)
        print("ALL FORMATS COMPLETE", flush=True)
