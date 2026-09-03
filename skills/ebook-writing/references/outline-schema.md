# outline.json schema

The manuscript lives in one JSON file so writing, review and typesetting never drift.
`scripts/build_from_outline.py` consumes exactly this shape.

```jsonc
{
  "meta": {
    "title": "The … Playbook",          // serif display title
    "title_accent": "STEP BY STEP",      // cover kicker line
    "subtitle": "One-sentence promise.",
    "author": "Name",
    "identity": "Book name  ·  © 2026 Author",   // running footer
    "price_line": "₦3,500   (was ₦10,000)",       // optional on cover
    "terms": "One-time payment · Instant download · 7-day money-back guarantee",
    "cta_url": "https://…/checkout",
    "cta_label": "GET THE FULL BOOK",
    "disclaimer": "Educational only … results vary …"
  },
  "orientation": {
    "is":      ["A step-by-step system …", "Written for complete beginners …"],
    "is_not":  ["A get-rich-quick scheme", "For people unwilling to work"],
    "audience": ["Students", "Workers", "Side-hustlers"],
    "how_to_use": "Tasks matter more than reading. …"
  },
  "chapters": [
    {
      "title": "The System",
      "promise": "What this chapter gives you: …",
      "outcomes": ["bullet", "bullet"],
      "sections": [
        {"head": "Why …", "paras": ["…", "…"], "bullets": ["✓ item"]},
        {"head": "The 7 steps", "paras": ["…"], "numbered": ["step", "step"]}
      ],
      "myths": ["Wrong belief one", "Wrong belief two"],
      "script": "Optional word-for-word template text …",
      "task": "Do this now: 1) … 2) …",
      "refs": [["@handle — description", "https://…"]]
    }
  ],
  "plan": {
    "title": "Your 30-Day Action Plan",
    "weeks": [
      {"label": "Week 1 — Foundations",
       "days": ["Day 1 — …", "Day 2 — …", "Day 3 — rest & review"]}
    ]
  },
  "worksheets": [
    {"title": "Worksheet 1 — Idea Filter", "chapter": 2,
     "prompts": ["The problem I'm solving:", "Who has it:"]}
  ],
  "tracker_rows": 30,
  "appendix_note": "Every source, grouped by chapter."
}
```

Rules:

- `chapters` order IS the arc order (see `arc-and-anatomy.md`); the builder numbers them.
- `sections[].numbered` renders as 1./2./3. steps; `bullets` render with ✓.
- `myths` render with ✗ in red; `script` renders as an indented template block.
- `refs` appear both in-chapter and auto-grouped into the appendix.
- Sample build always takes `chapters[0]` plus a generated CTA page from `meta`.
- Keep paragraph strings ≤ ~45 words; the builder wraps, you pace.
