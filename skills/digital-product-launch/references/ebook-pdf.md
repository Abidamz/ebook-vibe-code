# Paid ebook + free sample (fpdf2)

One script builds BOTH artifacts so they can never drift:

```
build_ebook.py --all      → paid book (ignored dir) + free sample (tracked)
build_ebook.py            → paid only
build_ebook.py --sample   → sample only
```

## Architecture that works

- `ROOT` derived from `__file__`; outputs: `delivery/<paid>.pdf`, `assets/ebook/free-sample-*.pdf`.
- A4 portrait, mm units, margins ~18mm, auto page break margin 20mm.
- Subclass `FPDF` once (`Book`): register DejaVu Sans + Sans-Bold in `__init__`,
  override `footer()` for the running footer (skip page 1): identity line + `Page N`.
- Helper methods on the subclass keep chapter code declarative:
  `para()`, `bullets(marker, color)`, `h1/h2`, `callout(label, kind, link)`,
  `task_box()` (worksheet prompts), `references()` (per-chapter source links),
  `image_card()` for illustrations.
- Track `chapter_pages` for a trustworthy TOC.
- Free sample = a subset build: cover-ish opener + chapter 1 + a final CTA page whose
  callout links to the LIVE sales page (clickable in the PDF).

## Glyph safety table (DejaVu)

| Safe | Unsafe |
|---|---|
| `₦` `✓` `✗` `·` `—` `…` (replaced to `...`) | colour emoji (🔥✅⚡ etc.) |

Keep a `clean(text)` preprocessor: replacement map + regex strip of emoji ranges +
whitespace collapse. Run EVERY string through it; one stray emoji crashes or tofu-prints.

## Composition targets

- ~38 pages / 10 chapters is the tested shape: chapter opener (number + title + promise),
  body paras at ~10.8pt / 6.3mm leading, bullet lists, one task box per chapter,
  references box, occasional full-width illustration.
- Cover page: cover art baked with semi-transparent parchment bands behind the title zone
  (composite once with Pillow, cache to an ignored path, embed the compressed JPEG).
- Images: compress to JPEG via Pillow (`opt_image()`), max width ~1100px q82 — keeps the
  book near ~1 MB instead of ~10 MB.

## Verification (do not trust stdout)

```python
import re; d = open(pdf,'rb').read()
pages = len(re.findall(rb'/Type\s*/Page[^s]', d))   # expect the target count
assert re.search(rb'/Count\s+%d' % pages, d)        # page tree agrees
assert b'%%EOF' in d[-1024:]
```
Also `ls -l` for size sanity and confirm the paid path is gitignored afterwards.

## Rebuild churn is expected

The sample PDF is TRACKED, so `--all` dirties the tree: byte-identical content except
`/CreationDate` and the trailer `/ID` hash (~66 bytes). Decide per session: restore
(`git checkout -- <path>`) or commit. Never present this churn as a content change.

## Environment

`python3 -m venv .venv && .venv/bin/pip install fpdf2 pillow`. Venvs do not survive
ephemeral restarts — recreate before rebuilding. Fonts come from the OS
(`/usr/share/fonts/truetype/dejavu/`); install `fonts-dejavu` only if missing.
