# Marketplace listing covers (Pillow)

Square (1600×1600) product images generated in code so price/title edits are re-runs.
Produce one PRIMARY plus 1–2 approved alternates for later listing-image tests.

## Composition (primary)

- **Top band** (ink): letterspaced kicker, e.g. "THE NO-HYPE BLUEPRINT", thin gold rule.
- **Body** (parchment): two columns.
  - Left: tiny amber kicker ("THE"), serif display title in 2–3 lines with one line
    swapped to cobalt sans for contrast, amber rule, bold sans promise line
    ("Make ₦5,000–₦10,000 daily selling digital products."), muted support lines,
    ink price pill ("INSTANT DOWNLOAD · ₦3,500"), cobalt author byline.
  - Right: the product art inside a phone/book card — parchment panel, cobalt rounded
    border, soft drop shadow (blur ~18px, offset y+4).
- **Bottom band** (ink): feature line ("10 CHAPTERS · STEP-BY-STEP · PHONE-FRIENDLY")
  + one muted reassurance sentence.

## Techniques that make it look designed

- `fit_font(draw, text, face, max_size, max_width)` — largest size that fits; use for
  every display line so copy changes never overflow.
- `add_grain(image, opacity≈13)` via `Image.effect_noise` → flat colour blocks match the
  paper texture of the source artwork.
- Drop shadows = separate RGBA layer, rounded rect, GaussianBlur, paste with mask.
- Consistent corner radii (cards ~24–30px at 1600px) and one shadow direction.
- Letter-spacing done manually (draw char-by-char) for kickers if the font lacks it.

## Variants

- **B:** rearrange (art left / text right, or full-bleed art with band overlay).
- **C:** different crop/emphasis (price-led, or audience-led).
- Keep the same palette + fonts across variants; only composition changes.
- Never upload all variants as product files — primary only; alternates are for tests.

## Contract with the rest of the project

- Source art stays `assets/img/cover-art.png`; covers are DERIVED, committed outputs.
- The same cover art (compressed) feeds the ebook cover page and the video-ad reveal,
  so regenerating art means re-running cover + ebook + ads.
- Listing doc records which file is primary and which are alternates.
