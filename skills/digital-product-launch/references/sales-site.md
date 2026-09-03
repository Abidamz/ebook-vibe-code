# Sales site (static, checkout-gated)

A single-page funnel plus a sample reader. No framework, no build step.

## Page anatomy (top → bottom)

1. **Sticky buy bar** (`#buyBar`, hidden until scroll > ~600px) — price + Buy Now.
2. **Nav** — brand mark, section links, Free Sample button, Get It Now button, burger.
3. **Hero** — kicker, serif headline with the income claim, sub, two CTAs
   (free sample = paper/cobalt, paid = amber), trust line, cover art.
4. **Problem** — mirror the reader's situation; agitate honestly, no shame.
5. **System** (dark) — the numbered framework at a glance.
6. **Inside / TOC** — chapter list so buyers see the volume of content.
7. **Steps** — one illustrated card per step (reuse the ebook's step art).
8. **Pro bonus** — a differentiated extra (e.g. country-targeting trick).
9. **Extras / bonuses** — worksheets, tracker, plan.
10. **Pricing** — anchor price struck, launch price big, terms line, guarantee badge,
    paid CTA + WhatsApp fallback.
11. **FAQ accordion** — objection handling (is this a scam? do I need a laptop? refunds?).
12. **Author** — credibility + photo/initials.
13. **Footer** — identity, canonical email placeholder, copyright, "no redistribution".

Plus `preview.html`: renders the free chapter in-page and links back to the sales page
and the sample PDF download.

## JS contract (`assets/js/main.js`)

- Config constants at top: `BUY_URL`, `WHATSAPP_NUMBER` (digits, no `+`).
- `document.querySelectorAll("[data-buy]")` → set href/target/rel from `BUY_URL`.
- WhatsApp links built from an encoded prefilled order message.
- Behaviours: nav scroll shadow, sticky buy bar toggle, FAQ accordion, mobile nav,
  scroll-reveal via IntersectionObserver.
- Everything enhancement-only: with JS off, literal hrefs still sell.

## CSS notes

- One stylesheet; CSS custom properties for the palette roles (see brand reference).
- Sections alternate light / `section-dark` for rhythm.
- Buttons: `.btn-amber` (paid), `.btn-cobalt` (action), `.btn-paper` (sample).
- Type scale: serif display 40–72px, body 16–18px, kickers 12–13px letterspaced.
- Mobile-first; burger nav under ~820px; buy bar always reachable on thumb.

## SEO / identity

- `<link rel="canonical">` = live pages URL; Product JSON-LD with same URL, price, currency.
- Data-URI SVG favicon (parchment rounded square + cobalt circle + ₦ glyph).
- Preconnect + single Google Fonts request (Fraunces + Inter, display=swap).
- Footer mailto is the accepted placeholder until a real inbox exists; note it in README.

## Deploy

Static host with zero build (Cloudflare Pages pattern): connect repo, framework None,
empty build command, output `/`; auto-redeploy on push to main. Exclude `.git`, `.venv`,
`scripts` from drag-and-drop uploads. Verify post-deploy: paid path 404s, sample path 200s,
checkout links resolve to the marketplace.
