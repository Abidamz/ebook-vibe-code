---
name: motion-graphics-ad
description: >
  Build brand-matched motion-graphic video ads (H.264 MP4 in vertical/square/landscape)
  from a repository's EXISTING assets, palette and copy, using Pillow frame rendering
  piped into ffmpeg, with an AI voiceover. Use whenever a user asks for "motion graphics",
  "a video ad", "ad creative", "reels/tiktok/stories ad", or "animate this for ads" for a
  product or brand that already has visual identity in the repo.
---

# Motion-Graphics Ad Builder

Turns a repo's existing brand (palette, fonts, illustrations, price, CTA) into a
timed motion-graphics ad, rendered as real MP4 video — no video-generation model,
no external SaaS. Fully reproducible from a script.

## When to use

- "Make motion graphics / a video ad / ad creative for this product."
- "Cut this for Reels / TikTok / Stories / Facebook / YouTube."
- You have brand assets in-repo (covers, step illustrations, a palette in code) and
  want animated ad variants instead of static images.

## Prerequisites

- Python venv with `pillow` and `imageio-ffmpeg`.
  - `imageio-ffmpeg` bundles a static ffmpeg binary with `libx264` + `aac`.
    Use it when `apt`/system ffmpeg is unavailable or network-blocked:
    `python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`.
- TTF fonts with the glyphs your copy needs. DejaVu ships with most Linux images at
  `/usr/share/fonts/truetype/dejavu/`. It has `₦` and `✓`/`✗` but NO colour emoji —
  strip or replace emoji before drawing (see gotchas).
- A TTS voice for the voiceover (register/audition first; see gotchas on accents).

## Workflow

1. **Mine the brand from the repo before designing anything.**
   - Palette: look for colour constants in existing build/render scripts.
   - Fonts: whatever the product PDF/site uses (serif display + sans body reads premium).
   - Artwork: covers, step/feature illustrations. Prefer web-optimised JPGs for speed.
   - Copy: headline, price + anchor price, guarantee, CTA URL, footer line.
   Never invent brand values; lift them.
2. **Agree the brief** (ask if not given): format(s), duration, audio treatment, hook angle.
   Default sane set: all three aspect ratios, 30–45 s, voiceover + on-screen text,
   outcome/benefit hook.
3. **Write the VO script to a character budget.** English TTS ≈ 800–900 chars/min,
   so ~45 s ≈ 600–680 chars. Spell money as words ("three thousand five hundred naira")
   for natural reading. End the VO a few seconds before the end so the CTA card breathes.
4. **Generate the VO first** and probe its real duration; build the timeline around the
   measured length, not the estimated one.
5. **Edit `scripts/render_ad.py`'s `CONFIG`** (copy, asset paths, palette, timing).
   The scene structure (hook → objections → pivot → steps → reassurance → reveal → CTA)
   is a proven 7-beat arc; reorder or drop beats by editing `CONFIG["timing"]`.
6. **PREVIEW BEFORE YOU RENDER.** Render single still frames per scene per format and
   actually LOOK at them. This catches 90% of layout bugs in seconds instead of after a
   1350-frame encode:
   `python scripts/render_ad.py preview 3.0 square`
7. **Full render**, piping raw RGB frames straight into ffmpeg stdin (never write PNGs
   to disk): `python scripts/render_ad.py all`
8. **Verify the outputs**, don't trust the render log:
   - probe each MP4 for duration, `h264`/`yuv420p`, dimensions, and an `aac` audio stream;
   - extract 2–3 frames with ffmpeg and view them;
   - confirm audio is muxed and the file plays/seek (Range-capable server or local player).
9. **Publish per the project's conventions.** Keep gated/paid assets OUT of git
   (`git check-ignore -v` to confirm). Ad creatives are usually safe to publish;
   the paid product they sell usually is not.

## Hard-won gotchas (each of these cost a re-render)

- **Width-fit every display string.** Fixed pixel sizes overflow on narrow formats.
  Use `fit_font()` (shrink until measured width ≤ max). Apply to headlines AND punchlines.
- **Pillow text anchors are not centre.** With `anchor="ma"` the y you pass is the
  ASCENDER TOP, so an underline belongs at `y + bbox_height + pad`, never `y + h*0.75`
  (that draws a line through the glyphs).
- **Size type by width, not height, across formats.** Scaling fonts by H makes 9:16
  punchlines clip. Fit to `W * 0.9` instead; let vertical use its spare height for an
  extra footer tagline.
- **Landscape needs a different composition**, not just a squeeze: split layout
  (text column left, artwork right) and fit the text column to the space left of the art.
- **Render stills and view them first.** A 45 s × 3-format encode is minutes; a preview
  frame is milliseconds.
- **Emoji will silently break DejaVu.** Strip/replace unsupported glyphs up front.
- **Regional TTS accents often don't exist.** `en-NG` failed outright; the tool contract
  is to retry with the bare language tag (`en`). Tell the user the accent limitation.
- **No licensed music available.** Ship VO-only and leave head-room at the end so the
  user can drop a bed under it. Say so explicitly.
- **Ephemeral sandboxes delete ignored/untracked dirs.** Re-verify outputs exist with
  `ls` immediately before reporting success; a restart can silently wipe `delivery/`.
  Venvs do not survive either — recreate and reinstall.
- **GitHub release uploads can be network-blocked** (`uploads.github.com` EOF), as can
  `raw.githubusercontent.com` from inside a sandbox. Fallback that always works:
  `git add` + `commit` + `push` the binaries to a branch; verify with the GitHub
  *contents API* (`gh api repos/…/contents/…?ref=…`), not with curl from the sandbox.
- **Autoplay is muted on social.** If the client picks voiceover, offer a burned-captions
  variant as a follow-up.

## Config schema (`scripts/render_ad.py` → `CONFIG`)

- `formats`: name → (W, H). Ship vertical 1080×1920, square 1080×1080, landscape 1920×1080.
- `fps`, `duration`: 30 and ~45 are the tested defaults.
- `palette`: ink / cream / gold / amber / cobalt / green / red / muted + light-link colour
  for dark backgrounds (plain cobalt is unreadable on ink).
- `fonts`: paths for sans, sans-bold, serif, serif-bold.
- `assets`: `cover` (packaged product shot) + `steps` list of `[image, head, sub]`.
  Prefix `web/` to resolve from the web-optimised folder.
- `copy`: every on-screen string (kicker, big, punch, tag, objections, pivot lines,
  ease lines, checks, guarantee, titles, prices, terms, cta, url, footer).
- `timing`: list of `(start, end, scene_name)`; scene names map to renderers.
- `vo`: path to the voiceover WAV to mux.

## Encode flags that matter

`-c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30` for compatibility,
`-c:a aac -b:a 192k -ar 48000 -ac 2` for the VO, and `-movflags +faststart` so the
moov atom leads and web players start instantly. Feed frames as
`-f rawvideo -pix_fmt rgb24 -s WxH -r 30 -i -`.
