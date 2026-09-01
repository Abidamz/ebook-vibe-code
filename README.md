# The ₦5K–₦10K Digital Product Playbook — Sales Website + Ebook

The sales website for **"The ₦5K–₦10K Digital Product Playbook"** — the no-hype ebook that shows you how to
make **₦5,000 – ₦10,000 daily (₦150K–₦300K monthly)** selling digital products in Nigeria.

- **Price:** ₦3,500 (launch, anchored against ₦10,000)
- **Design:** "Lagos Market Notebook" — warm parchment, ink-black type, cobalt action accents, tactile editorial details
- **Author:** Oluwadarasimi Oluwadamilola
- **Content source:** inspired by free public educational threads by
  [@iamrichygold](https://x.com/iamrichygold), [@egbokavictory_](https://x.com/egbokavictory_) and
  [@dotsokt](https://x.com/dotsokt) on X (Twitter), expanded into a full 10-chapter ebook (38 pages)
  with worksheets, a 30-day plan, illustrations, and chapter-by-chapter source links inside the PDF.

## What's in the repo

| Path | Description |
|---|---|
| `index.html` | The main sales page (hero, system, TOC, steps, bonuses, pricing, FAQ, author, sticky Buy Now bar) |
| `preview.html` | Free sample chapter (Chapter 1) — links back to the sales page |
| `assets/css/styles.css` | All styling (dark fintech look, gold/green naira theme) |
| `assets/js/main.js` | Buy-button wiring, sticky Buy Now bar, FAQ accordion, mobile nav, scroll reveal |
| `assets/img/` | Cover art + 6 illustrations (AI-generated; web-optimized copies in `assets/img/web/`) |
| `assets/ebook/digital-product-cash-machine.pdf` | The finished 38-page ebook (PDF) |
| `scripts/build_ebook.py` | Rebuilds the ebook PDF (Python + fpdf2) |

## Reference links used inside the ebook

Every chapter ends with a **Sources & References** box, and the appendix lists all links by chapter:

- @iamrichygold — [the 5k–10k daily system](https://x.com/iamrichygold/status/2092708000414761351)
- @iamrichygold — [system recap](https://x.com/iamrichygold/status/2092953828328952091)
- @iamrichygold — [digital products in 10 minutes](https://x.com/iamrichygold/status/2084258170944270469)
- @iamrichygold — [ready-made products to resell](https://x.com/iamrichygold/status/2084383065682375038)
- @egbokavictory_ — [pro targeting: Kenya, Zambia, Ghana & Nigeria](https://x.com/egbokavictory_/status/2016424347422867473)
- @egbokavictory_ — [10K-daily system setup](https://x.com/egbokavictory_/status/2091154409786884148)
- @egbokavictory_ — [how I make at least 10K daily](https://x.com/egbokavictory_/status/2089711208832057499)
- @dotsokt — [Reddit Custom Feeds content engine](https://x.com/dotsokt/status/2092346283302457636)

## ⚠️ Before going live — 2 things to edit

1. **Your checkout link** — open `assets/js/main.js` and replace:

   ```js
   const BUY_URL = "https://selar.co/your-digital-product-cash-machine"; // ← your Selar checkout link
   const WHATSAPP_NUMBER = "234XXXXXXXXXX";                             // ← your WhatsApp number
   ```

2. **Your domain** — in `index.html`, replace `YOUR-DOMAIN.pages.dev` in the
   `link rel="canonical"` and JSON-LD blocks (search for `YOUR-DOMAIN`).

Also update the email in the footer (`mailto:hello@yourdomain.com`).

## Deploy to Cloudflare Pages (free)

This is a **static site** — no build step needed.

### Option A — Drag & drop
1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages → Create → Pages → Upload assets**.
2. Upload the repo folder (everything except `.venv`, `.git`, and `scripts`).
3. Your site is live at `<project-name>.pages.dev`.

### Option B — Connect to GitHub (recommended)
1. Push this repo to GitHub.
2. In Cloudflare Pages, **Create a project** → connect the repo.
3. Build settings: **Framework preset: None** · Build command: *(leave empty)* · Build output directory: `/` .
4. Deploy. Every push to `main` auto-redeploys.

### Add your own domain (optional)
In the Pages project → **Custom domains** → add your domain and follow the DNS instructions.

## Rebuilding the ebook PDF

```bash
python3 -m venv .venv
.venv/bin/pip install fpdf2 pillow
.venv/bin/python scripts/build_ebook.py   # → assets/ebook/digital-product-cash-machine.pdf
```

## License

© 2026 Oluwadarasimi Oluwadamilola. All rights reserved. Do not redistribute or resell without permission.
