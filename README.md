# micro-uk

A remake of [micro-scooters.co.uk](https://www.micro-scooters.co.uk/)'s design, structure and features, filled with **Micro NZ's** products, prices and content. Orders go through the real checkout on [microscooters.co.nz](https://www.microscooters.co.nz).

Live prototype: **https://micro-nz.github.io/micro-uk/** (hidden from search engines, with a prototype banner).

## What it is

- **Static site, no build tooling beyond Python.** `build.py` turns a snapshot of the NZ store into ~850 pages: home, collections, products, spares, blog, content pages, policies.
- **Data:** `tools/fetch_nz.py` reads the NZ store through Shopify's public Storefront API (products, collections, pages, articles, policies). GitHub Actions refreshes it daily at 04:17 NZDT and redeploys.
- **Live in the browser:** cart and checkout (Storefront API cart → NZ checkout), price and stock refresh on product pages, "complete the set" recommendations, and star ratings and reviews from the NZ store's Okendo account.
- **The UK's own copy and photography are not used.** Layout and behaviour follow the UK site; words and images are Micro NZ's.

## Features worth knowing about

- **Scooter finder quiz** (`/pages/your-best-micro-scooter/`): five questions that adapt to the rider's age, with ranked picks, a tick/cross explanation for each, honest notes when it has to widen the search, shareable result URLs and a one-click comparison.
- **Product comparison** (`/pages/compare-scooters/`, plus on collection and product pages): any three scooters side by side; picking one already shown swaps columns; "highlight differences"; specs the NZ listings don't state show as "Not listed" rather than guesses.
- **Spare parts finder** (`/pages/spares-finder/`): search or browse 54 models by category, jump straight to a part type (wheels, grips, brakes…), see which scooters each parts page fits and the matching repair guides.

## Run it locally

```bash
python3 tools/fetch_nz.py      # snapshot the NZ store into .cache/nz/
python3 build.py               # write dist/
python3 tools/serve.py         # http://localhost:8123/micro-uk/
python3 tools/audit.py         # write REMAKE_REPORT.md
```

The browser self-test drives every interactive feature in real pages. With the preview server running, open any page and run this in the console; it saves `reports/runtime.json`, which the audit checks:

```js
await (await import('/__selftest.js')).run()
```

The cart test creates and then empties a real cart on the NZ store; no order is placed.

## Layout

| Path | What |
|---|---|
| `remake/config.py` | Menus, homepage sections, quiz questions, spares finder model map — the UK structure mapped to NZ handles |
| `remake/data.py` | Loads the snapshot; derives filters, badges, swatches, spare-part links and comparison specs |
| `remake/pages.py`, `remake/html.py` | Page templates and shared components |
| `assets/site.css`, `assets/app.js` | Styles and behaviour (no dependencies) |
| `spec/` | The UK feature inventory and menu map the audit checks against |
| `tests/` | Quiz and comparison engine tests (every answer combination), browser self-test |
| `tools/audit.py` | Writes `REMAKE_REPORT.md`; it says `REMAKE COMPLETE` only when every check passes |
