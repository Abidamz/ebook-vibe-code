# Brand & copy system

Everything visual and verbal derives from one small set of decisions. Lock these before
touching any artifact; every script in this skill reads them from a config block.

## Palette (this project's worked example)

Semantic role → hex (web) / rgb (print & video):

| Role | Hex | RGB | Use |
|---|---|---|---|
| ink | `#1C1812` | (28,24,18) | headlines, body on light, footer bands |
| parchment | `#F7F1E3` | (247,241,227) | page background, light sections |
| cobalt | `#1D4ED8` | (29,78,216) | primary action / links on light |
| amber | `#B45309` / `#D97706` | (180,83,9) | rules, kickers, secondary accents |
| gold (bright) | `#FFB020` | (255,176,32) | price + highlights on DARK only |
| light link | `#93C5FD` | (147,197,253) | links on dark (plain cobalt is unreadable there) |
| green | `#166534` | (22,101,52) | ✓ marks, guarantee, money-positive |
| red | `#DC2626` | (220,38,38) | ✗ marks, strike-through on anchor price |
| muted | `#85755F` | (133,117,95) | footers, captions, struck anchor price |

Rule: dark sections get gold + light-link; light sections get cobalt + amber. Never mix.

## Fonts

- **Web:** Fraunces (serif display, 600–900) + Inter (sans body) via Google Fonts.
- **Print/video (no network):** DejaVu Serif Bold for display numerals/titles,
  DejaVu Sans / Sans-Bold for body and kickers, at `/usr/share/fonts/truetype/dejavu/`.
- Display = serif, everything actionable = sans. Kickers are sans-bold, letterspaced, uppercase.

## Tone rules (no-hype doctrine)

- Promise a system, not an outcome guarantee. "₦5K–₦10K daily" is framed as what the
  system targets, always next to "real work".
- Include an explicit "what this is NOT" list (not get-rich-quick, not MLM, not for
  people unwilling to work).
- Name the audience plainly (beginners, students, workers, parents, side-hustlers).
- Repeat honesty markers: "no tech skills needed" ≠ "no effort needed".
- Guarantee stated as fact near price: e.g. "7-day money-back guarantee".

## Price & CTA copy patterns

- Launch price + struck compare-at: `₦3,500  (was ₦10,000)`.
- Terms line under price: "One-time payment · Instant download · 7-day money-back guarantee".
- Primary CTA verb pairs: "Get Instant Access", "Buy Now", "Tap the link · Get the book".
- Secondary CTA is always the free sample: "Download Free Sample (PDF)".
- Checkout URL appears as a literal `href` on every paid CTA (no-JS fallback) AND in JS config.
- WhatsApp fallback link with a prefilled order message is acceptable as a secondary channel.

## Copy skeleton reused across artifacts

kicker → big claim → punchline → objection kills ("Not X. Not Y.") → pivot ("Just a
system.") → numbered steps → reassurance checks → guarantee → title reveal → price
anchor → CTA + URL → footer identity line. The site, the ebook intro, and the video ads
all run this same arc in their own medium.
