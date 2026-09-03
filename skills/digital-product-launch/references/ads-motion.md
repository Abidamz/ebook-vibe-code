# Motion-graphic video ads

Full detail lives in the renderer's config; this is the method + the traps.
Runnable template: `../scripts/render_ad.py`.

## Pipeline

1. Mine brand (palette/fonts/art/copy) — same source as site & ebook.
2. Agree brief: formats, duration, audio, hook angle. Defaults: 3 formats, 45s, VO+text,
   outcome hook.
3. Write VO to a char budget (English ≈ 800–900 chars/min → 45s ≈ 600–680 chars); spell
   money as words; end VO ~5s before the end so the CTA card breathes.
4. Generate VO, probe its REAL duration, build the timeline around it.
5. Edit `CONFIG` (copy/assets/palette/timing), render single stills per scene per format
   and LOOK at them, then full render.
6. Verify: probe each MP4 (duration, h264/yuv420p, dims, aac stream); extract frames and
   view them; confirm seeking works (Range-capable server or local player).

## The 7-beat arc (CONFIG["timing"])

hook (count-up → big claim + underline swipe + staggered punchline + particles) →
objection kills (red ✗) → pivot to light ("Just a system.") → numbered steps as Ken Burns
cards with progress dots → reassurance ✓ checks + guarantee badge → product-cover reveal
with glare sweep → price anchor struck + pulsing CTA + checkout URL.

## Formats

vertical 1080×1920 (Reels/TikTok/Stories) · square 1080×1080 (feed) ·
landscape 1920×1080 (YouTube). Landscape = split composition (text column left, art right,
text column width-fitted to the gap); vertical uses spare height for a footer tagline.

## Encode

`-f rawvideo -pix_fmt rgb24 -s WxH -r 30 -i -` piped from Pillow (no PNG frames on disk);
`-c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p`; `-c:a aac -b:a 192k -ar 48000 -ac 2`;
`-movflags +faststart`. ffmpeg via `imageio-ffmpeg` when system ffmpeg is unavailable.

## Traps (each cost a re-render)

- Width-fit ALL display strings (`fit_font`); fixed px clips on narrow formats.
- `anchor="ma"` y = ascender TOP → underline at `y + bbox_height + pad`.
- Size type by WIDTH across formats, not height.
- Preview stills first; a 45s×3 render is minutes, a still is milliseconds.
- Regional TTS accents (e.g. `en-NG`) often don't exist → fall back to bare language tag
  and disclose it. No licensed music: ship VO-only with end head-room.
- Muted autoplay is the norm: offer a burned-captions variant as follow-up.
- Ad creatives are publishable; the paid PDF they sell is not.
