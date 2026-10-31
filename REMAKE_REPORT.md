# Remake report: micro-scooters.co.uk → micro-nz/micro-uk

Generated 01 November 2026, 11:36 NZDT by `tools/audit.py` from build of 2026-11-01T11:35:31+1300.

The remake rebuilds the UK site's design, structure and features as original code, filled with Micro NZ's catalogue and content (loaded from the NZ store's Storefront API). Checkout happens on microscooters.co.nz.

NZ data snapshot is 0.0 days old.

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | UK feature inventory | PASS | 73 of 73 UK features present |
| 2 | UK menu parity | PASS | 44 of 44 UK menu entries have a working equivalent in the header |
| 3 | NZ content coverage | PASS | 852 of 852 routes built (605 products, 91 collections, 49 pages, 88 articles, 6 blogs, 4 policies) |
| 4 | Spares finder mapping | PASS | 54 model tiles for 54 mapped spare-part collections; 0 mapped collections currently empty |
| 5 | Links | PASS | 247174 links and asset references in 853 pages; 0 broken internal, 0 to the UK site; external hosts outside the allow-list (CMS content, informational): indd.adobe.com, isin-wheel.com, micro-scooters-au.myshopify.com, micro-scooters.myshopify.com, online-store-web.shopifyapps.com, stockist.co, www.micro-mobility.com, www.microscooters.com.au, www.pinterest.nz, www.stuff.co.nz, www1.health.gov.au |
| 6 | Page quality | PASS | 853 of 853 pages pass |
| 7 | Size budgets | PASS | site.css 49 kB, app.js 59 kB, catalogue.json 314 kB, content-index.json 70 kB; largest page 363 kB (index.html) |
| 8 | Quiz and comparison engines | PASS | 5,024 quiz answer combinations and 49 comparison tables tested; 0 failures |
| 9 | Browser self-test | PASS | 19 behaviours tested in a real browser on 2026-10-31T22:34:52.934Z (http://localhost:8123/micro-uk (Chrome/152.0.7977.167)); 0 failed; matches the current app.js |
| 10 | Deployed to GitHub Pages | FAIL | skipped (--no-deploy-check) |

## UK features covered

| ID | Area | Feature | Runtime test |
|---|---|---|---|
| G01 | Global | Rotating announcement bar | — |
| G02 | Global | Floating sticky header with centred logo | — |
| G03 | Global | Shop mega menu: tabbed categories, age columns, promo tiles | mega-menu |
| G04 | Global | Best sellers top-level link | — |
| G05 | Global | Help & Support dropdown (before / after purchase) | — |
| G06 | Global | About Micro dropdown (about / initiatives) | — |
| G07 | Global | Search overlay with predictive results | predictive-search |
| G08 | Global | Account link | — |
| G09 | Global | Cart drawer: lines, quantity, remove, subtotal, free-delivery bar, checkout | cart |
| G10 | Global | Mobile menu drawer with nested panels | mobile-menu |
| G11 | Global | USP bar (four promises with icons) | — |
| G12 | Global | Footer brand pillars | — |
| G13 | Global | Footer newsletter sign-up | — |
| G14 | Global | Footer link columns | — |
| G15 | Global | Footer social links | — |
| G16 | Global | Footer legal links and copyright | — |
| G17 | Global | Delivery location statement | — |
| G18 | Global | Floating help / chat button | — |
| G19 | Global | Breadcrumbs | — |
| H01 | Home | Hero: image, gradient, headline, two pill CTAs | — |
| H02 | Home | Shop-by-age colour cards | — |
| H03 | Home | Scooter adviser banner | — |
| H04 | Home | Tabbed product carousel ('Don't forget your…') | carousel-tabs |
| H05 | Home | Personalise banner | — |
| H06 | Home | Featured looks tiles | — |
| H07 | Home | Brand statement with quick links | — |
| H08 | Home | Ambassador feature carousel | — |
| H09 | Home | Heading and text grid | — |
| H10 | Home | Latest blog stories | — |
| H11 | Home | SEO intro text | — |
| C01 | Collection | Collection banner with icon badges | — |
| C02 | Collection | Sub-collection quick-link strip | — |
| C03 | Collection | Facet filters (pill dropdowns and filter drawer) | filters |
| C04 | Collection | Sort | sort |
| C05 | Collection | Product count | — |
| C06 | Collection | Product card: grey tile, hover image, badge, swatches, Now/Was price, feature pills | — |
| C07 | Collection | Load more | load-more |
| C08 | Collection | Editorial content below the grid | — |
| C09 | Collection | Compare-the-range table | compare |
| C10 | Collection | Scooter adviser call to action | — |
| P01 | Product | Media gallery | — |
| P02 | Product | Image lightbox | lightbox |
| P03 | Product | Sticky buy box: title, price, save badge | — |
| P04 | Product | Star rating summary | rating |
| P05 | Product | Colour swatches / variant picker | variant |
| P06 | Product | Add to cart | cart |
| P07 | Product | Pay-later instalments box (Klarna in UK, Afterpay in NZ) | — |
| P08 | Product | Delivery / returns / warranty promises | — |
| P09 | Product | Complete the set | complete-set |
| P10 | Product | Key specs (ages, wheels, features) | — |
| P11 | Product | Accordions: description, features, delivery, spares, FAQs | — |
| P12 | Product | Why buy from Micro | — |
| P13 | Product | Reviews | reviews |
| P14 | Product | Compare products | — |
| P15 | Product | Related products | — |
| P16 | Product | Spare parts finder call to action | — |
| P17 | Product | Live price and stock | live-price |
| S01 | Spares | Spares & repairs landing (four steps) | — |
| S02 | Spares | Spares finder: model search, category tabs, model tiles with part shortcuts | spares-finder |
| S03 | Spares | Model spares page: part-type filter, fits-these-scooters, repair guides | parts-filter |
| S04 | Spares | Part-type filter | — |
| Q01 | Tools | Scooter finder quiz | quiz |
| Q02 | Tools | Compare the full range page | compare |
| B01 | Content | Blog hub with category tabs | — |
| B02 | Content | Blog category listing | — |
| B03 | Content | Article page with share links and related stories | — |
| I01 | Content | Information page template | — |
| I02 | Content | FAQs as accordions | — |
| I03 | Content | Contact form | — |
| I04 | Content | Search results page with tabs | search-page |
| I05 | Content | Cart page | — |
| I06 | Content | Not-found page | — |
| I07 | Content | Policy pages | — |

## Deliberate differences from the UK site

- Products, prices, copy and images are Micro NZ's, in NZD; the UK's own text and photography are not copied.
- Pay-later box shows Afterpay (NZ) where the UK shows Klarna; reviews come from the NZ store's Okendo account.
- Spec rows the NZ listings don't state show "Not listed" rather than guessed values.
- A prototype banner and noindex tag are added so the remake can't be mistaken for, or outrank, a live store.

**9 of 10 checks pass.**

REMAKE INCOMPLETE — 1 check(s) failing
