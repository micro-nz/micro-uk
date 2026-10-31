"""Page templates, one function per UK page type."""
import json, re
from . import config as C
from . import data as D
from .html import U, esc, img, icon, money, price_html, product_card, breadcrumbs, usp_bar, stars_slot, sized
from . import html as H

STORE_HOSTS = r"https?://(?:www\.)?microscooters\.co\.nz"


# ---------------------------------------------------------------- rich text
def rich(body):
    """Clean NZ CMS HTML: drop scripts/styles, absolutise images, point links at remake pages where they exist."""
    if not body:
        return ""
    body = re.sub(r"<(script|style|noscript)\b.*?</\1\s*>", "", body, flags=re.S | re.I)
    body = re.sub(r"<link\b[^>]*>", "", body, flags=re.I)
    body = re.sub(r'(src|srcset)="//', r'\1="https://', body)
    body = re.sub(r'(src|srcset)="/(?!/)', rf'\1="{C.STORE_URL}/', body)

    def fix(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith("www."):
            url = "https://" + url
        path = re.sub(STORE_HOSTS, "", url)
        if path.startswith("/") and not path.startswith("//"):
            bare = path.split("?")[0].split("#")[0].rstrip("/") or "/"
            if bare in H.ROUTES:
                return f'{attr}="{U(path)}"'
            return f'{attr}="{C.STORE_URL}{path}"'
        return f'{attr}="{url}"'
    body = re.sub(r'(href)="([^"]+)"', fix, body)
    body = re.sub(r"<h1\b", "<h2", body, flags=re.I).replace("</h1>", "</h2>")
    body = re.sub(r"<img\b(?![^>]*\balt=)", '<img alt=""', body, flags=re.I)
    body = re.sub(r"<img\b(?![^>]*\bloading=)", '<img loading="lazy"', body, flags=re.I)
    return body


def strip_tags(s, n=None):
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()
    if n and len(t) > n:
        t = t[:n].rsplit(" ", 1)[0] + "…"
    return t


def first_sentences(text, n=200):
    t = strip_tags(text)
    out = ""
    for s in re.split(r"(?<=[.!?])\s+", t):
        if len(out) + len(s) > n:
            break
        out += s + " "
    return (out or strip_tags(text, n)).strip()


def coll_img(store, handle):
    c = store.collection_by_handle.get(handle) or {}
    return (c.get("image") or {}).get("url", "")


def section(inner, cls="", feature="", sid=""):
    f = f' data-feature="{feature}"' if feature else ""
    i = f' id="{sid}"' if sid else ""
    return f'<section class="section {cls}"{f}{i}>{inner}</section>'


def carousel(cards, label):
    return (f'<div class="carousel" data-carousel aria-label="{esc(label)}"><button class="carousel__btn carousel__btn--prev" data-prev aria-label="Previous">{icon("left")}</button>'
            f'<div class="carousel__track">{"".join(cards)}</div>'
            f'<button class="carousel__btn carousel__btn--next" data-next aria-label="Next">{icon("right")}</button></div>')


def tabbed_carousel(store, title, tabs, feature):
    btns, panels = "", ""
    for i, (label, handle) in enumerate(tabs):
        prods = store.collection_products(handle)[:12]
        btns += f'<button class="tab{" is-active" if i == 0 else ""}" role="tab" aria-selected="{"true" if i == 0 else "false"}" data-tab="{feature}-{i}">{esc(label)}</button>'
        lead = (f'<a class="card card--lead" href="{U("/collections/" + handle)}">{img(coll_img(store, handle), "", "(min-width: 990px) 22vw, 60vw", cls="card__img")}'
                f'<span class="card--lead__text"><b>{esc(label)}</b><span class="btn btn--light btn--sm">Shop the range</span></span></a>')
        panels += (f'<div class="tabpanel{" is-active" if i == 0 else ""}" role="tabpanel" id="{feature}-{i}"{"" if i == 0 else " hidden"}>'
                   f'{carousel([lead] + [product_card(p) for p in prods], label)}</div>')
    return section(f'<div class="container"><div class="section__head"><h2>{esc(title)}</h2><div class="tabs" role="tablist">{btns}</div></div>{panels}</div>',
                   feature="tabbed-carousel" if feature == "c1" else feature)


def media_banner(store, cfg, feature, tone="teal"):
    image = coll_img(store, cfg["collection"])
    t, link = cfg["cta"]
    return section(f'<div class="container"><div class="media-banner media-banner--{tone}">{img(image, "", "(min-width: 990px) 1200px, 100vw", cls="media-banner__img")}'
                   f'<div class="media-banner__text"><p class="eyebrow">{esc(cfg["eyebrow"])}</p><h2 class="display">{esc(cfg["title"])}</h2>'
                   f'<p>{esc(cfg["text"])}</p><a class="btn btn--light" href="{esc(U(link))}">{esc(t)}</a></div></div></div>', feature=feature)


def article_card(a):
    url = U(f"/blogs/{a['blog']['handle']}/{a['handle']}")
    im = (a.get("image") or {}).get("url", "")
    date = (a.get("publishedAt") or "")[:10]
    return (f'<article class="post-card" data-blog="{esc(a["blog"]["handle"])}"><a href="{url}" class="post-card__media">{img(im, a["title"], "(min-width: 990px) 30vw, 90vw")}</a>'
            f'<div class="post-card__body"><p class="eyebrow">{esc(a["blog"]["title"])}</p><h3><a href="{url}">{esc(a["title"])}</a></h3>'
            f'<p>{esc(strip_tags(a.get("excerpt") or a.get("contentHtml"), 140))}</p><time datetime="{date}">{nz_date(date)}</time></div></article>')


MONTHS = "January February March April May June July August September October November December".split()


def nz_date(iso):
    if not iso or len(iso) < 10:
        return ""
    y, m, d = iso[:10].split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


# ---------------------------------------------------------------- home
def home(store):
    h = C.HOME
    hero = h["hero"]
    ctas = "".join(f'<a class="btn {"btn--light" if i == 0 else "btn--outline-light"}" href="{esc(U(l))}">{esc(t)}</a>' for i, (t, l) in enumerate(hero["ctas"]))
    out = [f'<section class="hero" data-feature="home-hero">{img(hero["image"], "Children riding Micro scooters", "100vw", eager=True, cls="hero__img")}'
           f'<div class="hero__text container"><h1 class="display">{esc(hero["title"])}</h1><p>{esc(hero["text"])}</p><div class="btn-row">{ctas}</div></div></section>',
           usp_bar()]
    cards = "".join(f'<a class="age-card age-card--{tone}" href="{esc(U(link))}"><span class="age-card__text"><small>{esc(sub)}</small><b>{esc(title)}</b></span>'
                    f'{img(coll_img(store, coll), "", "(min-width: 990px) 25vw, 70vw", cls="age-card__img")}</a>'
                    for sub, title, link, coll, tone in h["age_cards"])
    out.append(section(f'<div class="container"><h2 class="sr-only">Shop by age</h2><div class="age-cards">{cards}</div></div>', "section--grey", "age-cards"))
    out.append(media_banner(store, h["adviser"], "adviser-banner", "slate"))
    out.append(tabbed_carousel(store, h["carousel_1"]["title"], h["carousel_1"]["tabs"], "c1"))
    out.append(media_banner(store, h["personalise"], "personalise-banner", "plum"))
    out.append(tabbed_carousel(store, h["carousel_2"]["title"], h["carousel_2"]["tabs"], "c2"))
    fp = h["featured_pages"]
    tiles = "".join(f'<a class="look-tile" href="{esc(U(link))}">{img(coll_img(store, coll), "", "(min-width: 990px) 25vw, 45vw")}<span>{esc(t)} ›</span></a>'
                    for t, link, coll in fp["tiles"])
    out.append(section(f'<div class="container"><h2 class="section__title">{esc(fp["title"])}</h2><div class="look-grid">{tiles}</div></div>', feature="featured-pages"))
    ql = h["quick_links"]
    links = "".join(f'<li><a href="{esc(U(l))}">{esc(t)} {icon("right", "icon icon--sm")}</a></li>' for t, l in ql["links"])
    out.append(section(f'<div class="container quick-links"><div class="quick-links__media">{img(coll_img(store, ql["collection"]), "", "(min-width: 990px) 45vw, 100vw")}</div>'
                       f'<div class="quick-links__text"><h2>{esc(ql["title"])}</h2><ul>{links}</ul></div></div>', "section--grey", "quick-links"))
    am = h["ambassadors"]
    acards = "".join(f'<div class="feature-card">{img(coll_img(store, coll), "", "(min-width: 990px) 25vw, 70vw")}<p>{esc(t)}</p></div>' for t, coll in am["cards"])
    out.append(section(f'<div class="container ambassadors"><div class="ambassadors__text"><h2>{esc(am["title"])}</h2><p>{esc(am["text"])}</p>'
                       f'<a class="btn btn--dark" href="{esc(U(am["cta"][1]))}">{esc(am["cta"][0])}</a></div>'
                       f'{carousel(acards and [acards], "Ambassador perks")}</div>', feature="ambassadors"))
    grid = "".join(f'<div><h3>{esc(t)}</h3><p>{esc(s)}</p></div>' for t, s in h["text_grid"])
    out.append(section(f'<div class="container"><div class="text-grid">{grid}</div></div>', "section--tight", "text-grid"))
    posts = "".join(article_card(a) for a in store.articles[:3])
    out.append(section(f'<div class="container"><div class="section__head"><h2>Stories from the Micro blog</h2><a class="link-arrow" href="{U("/blogs")}">Explore the blog ›</a></div>'
                       f'<div class="post-grid">{posts}</div></div>', feature="latest-news"))
    out.append(section(f'<div class="container seo-text"><h2>{esc(h["seo"][0])}</h2><p>{esc(h["seo"][1])}</p></div>', "section--tight", "seo-text"))
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": C.STORE_NAME, "url": C.STORE_URL, "logo": C.LOGO}
    return dict(title="Scooters for kids & adults", description=C.HOME["seo"][1], body="\n".join(out), canonical=C.STORE_URL + "/",
                page_class="page-home", hero_first=True, json_ld=ld)


# ---------------------------------------------------------------- collections
def menu_siblings(handle):
    """Sub-collections shown in the UK 'which … to choose' strip: the menu column containing this collection."""
    for _, _, cols, _ in C.MEGA_MENU:
        for heading, hlink, links in cols:
            paths = [l for _, l in links]
            if f"/collections/{handle}" in paths or hlink == f"/collections/{handle}":
                return [(t, l) for t, l in links if l.startswith("/collections/") and l != f"/collections/{handle}" and t != "View all"]
    return [("Kids scooters", "/collections/kids-scooters"), ("Toddler scooters", "/collections/toddler-preschool-scooters"),
            ("Adult scooters", "/collections/adult-scooters"), ("Helmets & safety gear", "/collections/all-helmets-safety-gear")]


def facet_defs(prods):
    """Only facets that actually split this collection's products."""
    defs = []
    wheels = sorted({p["_wheels"] for p in prods if p["_wheels"]})
    if len(wheels) > 1:
        defs.append(("w", "No. of wheels", [(w, f"{w} wheels") for w in wheels]))
    feats = {}
    for p in prods:
        for code, label in p["_features"]:
            feats[code] = label
    if feats:
        defs.append(("f", "Feature", sorted(feats.items(), key=lambda x: x[1])))
    ages = [a for a in ("toddler", "kids", "adult") if any(p["_age"] == a for p in prods)]
    if len(ages) > 1:
        defs.append(("age", "Age", [(a, D.AGE_LABELS[a]) for a in ages]))
    parts = [(code, label) for code, label, _ in D.PART_TYPES + [("other", "Other parts", [])] if any(p["_part"] == code for p in prods)]
    if len(parts) > 1:
        defs.append(("pt", "Part type", parts))
    bands = [(code, label) for code, label, lo, hi in D.PRICE_BANDS if any(lo <= p["_price"] < hi for p in prods)]
    if len(bands) > 1:
        defs.append(("price", "Price", bands))
    if any(not p["availableForSale"] for p in prods):
        defs.append(("a", "Availability", [("1", "In stock")]))
    return defs


def facet_ui(defs):
    pills, drawer = "", ""
    for key, label, opts in defs:
        boxes = "".join(f'<label class="check"><input type="checkbox" name="{key}" value="{esc(v)}"> <span>{esc(l)}</span></label>' for v, l in opts)
        feat = ' data-feature="part-type-filter"' if key == "pt" else ""
        pills += (f'<div class="facet"{feat}><button class="pill pill--select" aria-expanded="false" data-facet-toggle>{esc(label)} {icon("down", "icon icon--xs")}</button>'
                  f'<div class="facet__menu" hidden>{boxes}</div></div>')
        drawer += f'<fieldset class="facet-group"><legend>{esc(label)}</legend>{boxes}</fieldset>'
    return pills, drawer


def comparable(p):
    return not p["_hidden"] and p["_category"] in ("scooters", "ride-ons") and bool(p["_specs"].get("wheels"))


def compare_block(store, prods, title="Compare the range", defaults=None, full_page=False, cid="cmp"):
    """UK 'Compare the range' table: three product pickers, spec rows, highlight-differences toggle. Rendered by app.js."""
    items = [p for p in prods if comparable(p)]
    if len(items) < 2:
        return ""
    handles = [p["handle"] for p in items]
    defaults = [h for h in (defaults or []) if h in handles] or handles[:3]
    link = "" if full_page else f'<p class="compare__more"><a class="link-arrow" href="{U("/pages/compare-scooters")}">Compare the full range ›</a></p>'
    inner = (f'<div class="container"><div class="section__head"><h2 id="{cid}-title">{esc(title)}</h2>'
             f'<label class="switch"><input type="checkbox" data-compare-diff><span class="switch__track" aria-hidden="true"></span>Highlight differences</label></div>'
             f'<div class="compare" id="{cid}" data-compare data-url-sync="{"1" if full_page else ""}" aria-labelledby="{cid}-title" '
             f'data-handles=\'{esc(json.dumps(handles))}\' data-defaults=\'{esc(json.dumps(defaults[:3]))}\'>'
             f'<p class="muted compare__loading">Loading comparison…</p></div>'
             f'<p class="small muted compare__note">Specs are taken from each product\'s listing on microscooters.co.nz. '
             f'"Not listed" means the listing doesn\'t state it.</p>{link}</div>')
    return section(inner, "section--grey", "compare")


def compare_page(store):
    items = [p for p in store.products if comparable(p)]
    best = [h for h in store.collection_by_handle["bestselling-scooters"]["products"] if any(p["handle"] == h for p in items)]
    body = (f'{page_hero("Compare scooters", "Pick any three Micro scooters, ride-ons or balance bikes and see how they stack up.")}'
            f'{breadcrumbs([("Compare scooters", "")])}{compare_block(store, items, "Compare the Micro range", best[:3], full_page=True)}{quiz_cta()}')
    return dict(title="Compare scooters", description="Compare Micro scooters side by side: ages, wheels, folding, light-up wheels, rider weight and price.",
                body=body, canonical=f"{C.STORE_URL}/collections/all-scooters", page_class="page-compare")


def quiz_cta():
    return section(f'<div class="container"><div class="cta-split" data-feature="quiz-cta"><div><p class="eyebrow">Scooter adviser</p>'
                   f'<h2>Need help choosing the right Micro?</h2><p>Five quick questions and we\'ll suggest the scooters that suit them best.</p>'
                   f'<a class="btn btn--dark" href="{U("/pages/your-best-micro-scooter")}">Find your perfect scooter</a></div>'
                   f'<div class="cta-split__icon">{icon("spark", "icon icon--xl")}</div></div></div>')


def collection(store, c, page_size=24):
    prods = store.collection_products(c["handle"])
    is_parts = c in store.spare_collections
    banner_img = (c.get("image") or {}).get("url", "")
    lead = first_sentences(c.get("description"), 180)
    badges = (f'<li>{icon("truck")} Free shipping over $100</li><li>{icon("shield")} 2 year warranty</li>' if not is_parts else
              f'<li>{icon("wrench")} Genuine Micro parts</li><li>{icon("truck")} Fast NZ dispatch</li>')
    out = [f'<section class="coll-banner{" coll-banner--plain" if not banner_img else ""}" data-feature="collection-banner">'
           f'{img(banner_img, "", "100vw", eager=True, cls="coll-banner__img") if banner_img else ""}'
           f'<div class="container coll-banner__text">{"<p class=eyebrow>Spare parts</p>" if is_parts else ""}<h1 class="display">{esc(c["title"])}</h1>{f"<p>{esc(lead)}</p>" if lead else ""}'
           f'<ul class="icon-badges">{badges}</ul></div></section>']
    out.append(breadcrumbs([("Spares and repairs", "/pages/spares-and-repairs"), ("Spares finder", "/pages/spares-finder"), (c["title"], "")] if is_parts else [(c["title"], "")]))
    guides_after = ""
    if is_parts and prods:
        help_html, guides_after = parts_extras(store, c, prods)
        out.append(help_html)
    sibs = [(t, l) for t, l in (menu_siblings(c["handle"]) if not is_parts else [])][:4]
    if sibs:
        tiles = "".join(f'<a class="sub-tile" href="{esc(U(l))}"><span><b>{esc(t)}</b><small>Shop now</small></span>'
                        f'{img(coll_img(store, l.rsplit("/", 1)[-1]), "", "120px", widths=(120, 240))}</a>' for t, l in sibs)
        out.append(f'<section class="sub-strip" data-feature="subcollection-strip"><div class="container"><p class="eyebrow">Explore the range</p><div class="sub-strip__grid">{tiles}</div></div></section>')
    defs = facet_defs(prods)
    pills, drawer = facet_ui(defs)
    sort = ('<label class="sr-only" for="sort">Sort by</label><select id="sort" class="pill pill--select" data-sort data-feature="sort">'
            '<option value="featured">Featured</option><option value="price-asc">Price, low to high</option><option value="price-desc">Price, high to low</option>'
            '<option value="title-asc">Alphabetically, A–Z</option><option value="title-desc">Alphabetically, Z–A</option><option value="date-desc">Newest</option></select>')
    cards = "".join(product_card(p) for p in prods[:page_size])
    more = (f'<div class="load-more" data-feature="load-more"><p class="small muted" data-shown>Showing {min(page_size, len(prods))} of {len(prods)}</p>'
            f'<button class="btn btn--outline" data-load-more{" hidden" if len(prods) <= page_size else ""}>Load more</button></div>')
    empty = '<p class="empty" data-empty hidden>No products match those filters. <button class="link" data-clear>Clear filters</button></p>'
    if not prods:
        empty = '<p class="empty">There are no products in this collection right now.</p>'
    out.append(f'''<section class="section section--tight" id="products">
<div class="container" data-collection='{esc(json.dumps([p["handle"] for p in prods]))}' data-page-size="{page_size}">
  <div class="toolbar" data-feature="facets">
    <button class="pill pill--icon" data-open="filters">{icon("filter")} Filter</button>
    <div class="toolbar__facets">{pills}</div>
    <div class="toolbar__right">{sort}<span class="count" data-feature="product-count" data-count>{len(prods)} products</span></div>
  </div>
  <div class="active-filters" data-active-filters></div>
  <div class="grid" data-grid>{cards}</div>{empty}{more}
</div>
<div class="drawer drawer--left" id="filters" hidden role="dialog" aria-modal="true" aria-label="Filters">
  <div class="drawer__head"><span>Filter</span><button class="icon-btn" data-close aria-label="Close filters">{icon("close")}</button></div>
  <div class="drawer__body">{drawer or '<p class="muted">No filters for this collection.</p>'}</div>
  <div class="drawer__foot"><button class="btn btn--outline" data-clear>Clear all</button><button class="btn btn--dark" data-close>Show results</button></div>
</div></section>''')
    if c.get("descriptionHtml"):
        out.append(section(f'<div class="container rte rte--narrow">{rich(c["descriptionHtml"])}</div>', "section--grey", "collection-content"))
    if not is_parts:
        out.append(compare_block(store, prods))
        out.append(quiz_cta())
    else:
        out.append(guides_after)
        out.append(spares_help_cta())
    seo = c.get("seo") or {}
    return dict(title=seo.get("title") or c["title"], description=seo.get("description") or lead or c["title"], body="\n".join(out),
                canonical=f"{C.STORE_URL}/collections/{c['handle']}", page_class="page-collection", hero_first=bool(banner_img))


def collections_index(store):
    tiles = "".join(f'<a class="look-tile" href="{U("/collections/" + c["handle"])}">{img((c.get("image") or {}).get("url", ""), "", "(min-width: 990px) 25vw, 45vw")}'
                    f'<span>{esc(c["title"])} ›</span></a>' for c in store.collections if c not in store.spare_collections and store.collection_products(c["handle"]))
    body = (f'<section class="page-hero"><div class="container"><h1 class="display">Shop all</h1></div></section>{breadcrumbs([("Collections", "")])}'
            f'<section class="section"><div class="container"><div class="look-grid">{tiles}</div></div></section>')
    return dict(title="All collections", description="Every Micro range: scooters, ride-ons, helmets, accessories and spare parts.", body=body,
                canonical=C.STORE_URL + "/collections", page_class="page-collections")


# ---------------------------------------------------------------- product
WHY_MICRO = [("shield", "2 year warranty", "Every scooter is covered for two years as standard.", "/pages/warranty"),
             ("wrench", "Spares and repairs", "Every part is replaceable, so a Micro can be repaired, not binned.", "/pages/spares-and-repairs"),
             ("tag", "Price match promise", "Found it cheaper at an NZ retailer? We'll match it.", "/pages/price-match-promise"),
             ("truck", "Free NZ shipping", "Free delivery on orders over $100.", "/pages/delivery")]


def why_micro():
    cards = "".join(f'<a class="why-card" href="{esc(U(l))}">{icon(ic, "icon icon--lg")}<h3>{esc(t)}</h3><p>{esc(s)}</p></a>' for ic, t, s, l in WHY_MICRO)
    return section(f'<div class="container"><p class="eyebrow">Made for adventure, built to last</p><h2 class="section__title">Why buy from Micro?</h2>'
                   f'<div class="why-grid">{cards}</div></div>', "section--grey", "why-micro")


def spares_help_cta():
    return section(f'<div class="container"><div class="cta-split" data-feature="spares-cta"><div><p class="eyebrow">Spare parts finder</p>'
                   f'<h2>Keep it rolling</h2><p>We stock parts for current and past Micro models, with repair guides to help you fit them.</p>'
                   f'<div class="btn-row"><a class="btn btn--dark" href="{U("/pages/spares-finder")}">Find a spare part</a>'
                   f'<a class="btn btn--outline" href="{U("/blogs/how-tos")}">Repair guides</a></div></div>'
                   f'<div class="cta-split__icon">{icon("wrench", "icon icon--xl")}</div></div></div>')


def product(store, p):
    imgs = p["_images"]
    pc = store.primary_collection(p)
    crumbs = ([(pc["title"], "/collections/" + pc["handle"])] if pc else []) + [(p["title"], "")]
    gallery = "".join(f'<button class="gallery__item" data-lightbox="{i}" aria-label="Open image {i + 1} of {len(imgs)}">'
                      f'{img(im["url"], im.get("altText") or p["title"], "(min-width: 990px) 30vw, 100vw", eager=i == 0, w=im.get("width"), h=im.get("height"))}'
                      f'{icon("expand", "icon gallery__zoom")}</button>' for i, im in enumerate(imgs[:12]))
    if not imgs:
        gallery = '<div class="img-placeholder"></div>'
    variants = p["variants"]["nodes"]
    vjson = [{"id": D.numeric_id(v["id"]), "gid": v["id"], "title": v["title"], "price": D._f(v["price"]["amount"]),
              "compare": D._f((v.get("compareAtPrice") or {}).get("amount")), "available": v["availableForSale"],
              "options": {o["name"]: o["value"] for o in v["selectedOptions"]}, "image": (v.get("image") or {}).get("url", ""), "sku": v.get("sku")}
             for v in variants]
    pickers = ""
    for o in p["options"]:
        if o["name"] == "Title" and len(o["optionValues"]) <= 1:
            continue
        is_colour = o["name"].lower() == "colour"
        btns = ""
        for j, ov in enumerate(o["optionValues"]):
            val = ov["name"]
            vimg = next((v["image"] for v in vjson if v["options"].get(o["name"]) == val and v["image"]), "")
            inner = img(vimg, val, "56px", widths=(60, 120)) if is_colour and vimg else esc(val)
            btns += (f'<button type="button" class="opt{" opt--swatch" if is_colour and vimg else ""}{" is-selected" if j == 0 else ""}" data-option="{esc(o["name"])}" '
                     f'data-value="{esc(val)}" aria-pressed="{"true" if j == 0 else "false"}" title="{esc(val)}">{inner}</button>')
        pickers += (f'<div class="opt-group"><p class="opt-group__label">{esc(o["name"])}: <b data-option-label="{esc(o["name"])}">{esc(o["optionValues"][0]["name"])}</b></p>'
                    f'<div class="opt-group__values">{btns}</div></div>')
    first = vjson[0] if vjson else {"price": p["_price"], "compare": 0, "available": False, "gid": ""}
    save = (f'<span class="save-badge" data-save>Save {money(first["compare"] - first["price"])} ({round(100 * (first["compare"] - first["price"]) / first["compare"])}%)</span>'
            if first["compare"] > first["price"] else '<span class="save-badge" data-save hidden></span>')
    instal = first["price"] / 4
    specs = []
    if p["_age"]:
        specs.append(("age", "Suits", D.AGE_LABELS[p["_age"]]))
    if p["_wheels"]:
        specs.append(("wheel", "Wheels", f'{p["_wheels"]} wheels'))
    if p["_features"]:
        specs.append(("spark", "Why we love it", ", ".join(l for _, l in p["_features"])))
    spec_html = "".join(f'<li>{icon(ic)}<span><b>{esc(t)}</b>{esc(v)}</span></li>' for ic, t, v in specs)
    spec_html = f'<ul class="key-specs" data-feature="key-specs">{spec_html}</ul>' if specs else '<ul class="key-specs" data-feature="key-specs"><li>' + icon("shield") + '<span><b>Genuine Micro</b>Designed in Switzerland</span></li></ul>'
    feats = "".join(f"<li>{esc(l)}</li>" for _, l in p["_features"]) or "<li>Genuine Micro product</li><li>Backed by our two-year warranty</li>"
    spares_link = (f'<p>Parts for this model are in stock: <a href="{U("/collections/" + p["_spares"])}">shop {esc(store.collection_by_handle[p["_spares"]]["title"].lower())}</a>.</p>'
                   if p["_spares"] else "")
    acc = [
        ("Product description", f'<div class="rte">{rich(p["descriptionHtml"]) or "<p>" + esc(p["title"]) + "</p>"}</div>', True),
        ("Features", f'<ul class="ticks">{feats}</ul>', False),
        ("Delivery & returns", f'<p>Free shipping on NZ orders over $100. Orders are dispatched from our Wellington warehouse.</p>'
                               f'<p><a href="{U("/pages/delivery")}">Shipping &amp; delivery</a> · <a href="{U("/pages/returns-refunds")}">Returns &amp; refunds</a></p>', False),
        ("Spares & repairs", f'{spares_link}<p>Every Micro is built to be repaired. <a href="{U("/pages/spares-finder")}">Find a spare part</a> or read our '
                             f'<a href="{U("/blogs/how-tos")}">repair guides</a>.</p>', False),
        ("FAQs", f'<p>Answers on sizing, assembly, warranty and more in our <a href="{U("/pages/scooter-faq-help-desk")}">help centre</a>.</p>', False),
    ]
    accordions = "".join(f'<details class="acc"{" open" if op else ""}><summary>{esc(t)}{icon("plus", "icon acc__icon")}</summary><div class="acc__body">{b}</div></details>'
                         for t, b, op in acc)
    usps = "".join(f'<li>{icon(ic)}<span><b>{esc(t)}</b> {esc(s)}</span></li>' for ic, t, s, _ in WHY_MICRO)
    siblings = [x for x in (store.collection_products(pc["handle"]) if pc else []) if x["handle"] != p["handle"]]
    related = carousel([product_card(x) for x in siblings[:12]], "Related products") if siblings else ""
    numeric = D.numeric_id(p["id"])
    buy = f'''
<div class="buy-box" data-feature="buy-box">
  <h1 class="buy-box__title">{esc(p["title"])}</h1>
  {stars_slot(numeric)}
  <div class="buy-box__price" data-feature="live-price"><div data-price>{price_html(first["price"], first["compare"] if first["compare"] > first["price"] else 0)}</div>{save}</div>
  <div data-feature="variant-picker">{pickers}</div>
  <p class="stock" data-stock>{"In stock" if first["available"] else "Sold out"}</p>
  <button class="btn btn--dark btn--block btn--lg" data-feature="add-to-cart" data-add-to-cart data-variant="{esc(first["gid"])}"{"" if first["available"] else " disabled"}>{"Add to cart" if first["available"] else "Sold out"}</button>
  <div class="instalments" data-feature="instalments">or 4 interest-free payments of <b data-instalment>{money(instal)}</b> with <b>Afterpay</b> <a href="{U("/pages/pay-with-afterpay")}">Learn more</a></div>
  <ul class="pdp-usps" data-feature="pdp-usps">{usps}</ul>
  <div class="complete-set" data-feature="complete-set" data-product-gid="{esc(p["id"])}" hidden><h2>Complete the set</h2><div class="complete-set__items" data-complete-items></div></div>
  {spec_html}
  <div class="accordions" data-feature="accordions">{accordions}</div>
</div>'''
    body = f'''
{breadcrumbs(crumbs)}
<section class="pdp" data-product='{esc(json.dumps({"handle": p["handle"], "id": numeric, "gid": p["id"], "variants": vjson}))}'>
  <div class="container pdp__grid">
    <div class="gallery" data-feature="gallery">{gallery}</div>
    <div class="pdp__info">{buy}</div>
  </div>
</section>
<div class="lightbox" id="lightbox" data-feature="lightbox" hidden role="dialog" aria-modal="true" aria-label="Image viewer">
  <button class="icon-btn lightbox__close" data-close aria-label="Close">{icon("close")}</button>
  <button class="icon-btn lightbox__prev" data-lb-prev aria-label="Previous image">{icon("left")}</button>
  <img alt="" data-lb-img><button class="icon-btn lightbox__next" data-lb-next aria-label="Next image">{icon("right")}</button>
  <script type="application/json" data-lb-src>{json.dumps([sized(i["url"], 1600) for i in imgs[:12]])}</script>
</div>
{why_micro()}
{section(f'<div class="container"><div class="section__head"><h2>Reviews</h2>{stars_slot(numeric, "rating--lg")}</div><div class="reviews" data-reviews="{numeric}"><p class="muted">Loading reviews…</p></div></div>', "", "reviews")}
{compare_block(store, ([p] + siblings) if comparable(p) else [], "Compare products", [p["handle"]] + [x["handle"] for x in siblings if comparable(x)][:2])}
{quiz_cta() if p["_category"] in ("scooters", "ride-ons") else ""}
{spares_help_cta()}
{section(f'<div class="container"><h2 class="section__title">You may also like</h2>{related}</div>', "", "related") if related else ""}'''
    seo = p.get("seo") or {}
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["title"], "image": [i["url"] for i in imgs[:5]],
          "description": strip_tags(p.get("description"), 300), "brand": {"@type": "Brand", "name": p.get("vendor") or "Micro"},
          "offers": {"@type": "Offer", "priceCurrency": "NZD", "price": f'{first["price"]:.2f}',
                     "availability": "https://schema.org/InStock" if first["available"] else "https://schema.org/OutOfStock",
                     "url": f"{C.STORE_URL}/products/{p['handle']}"}}
    return dict(title=seo.get("title") or p["title"], description=seo.get("description") or strip_tags(p.get("description"), 160) or p["title"],
                body=body, canonical=f"{C.STORE_URL}/products/{p['handle']}", page_class="page-product", json_ld=ld)


# ---------------------------------------------------------------- content pages
def page_hero(title, sub=""):
    return f'<section class="page-hero"><div class="container"><h1 class="display">{esc(title)}</h1>{f"<p>{esc(sub)}</p>" if sub else ""}</div></section>'


FAQ_HANDLES = {"scooter-faq-help-desk"}
CONTACT_HANDLES = {"contact"}


def faq_body(body):
    """Turn heading-led sections into accordions, the way the UK FAQ page works."""
    parts = re.split(r"(<h[2-4][^>]*>.*?</h[2-4]>)", body, flags=re.S | re.I)
    if len(parts) < 3:
        return f'<div class="rte">{body}</div>'
    out = f'<div class="rte">{parts[0]}</div>'
    for i in range(1, len(parts) - 1, 2):
        q = strip_tags(parts[i])
        out += f'<details class="acc"><summary>{esc(q)}{icon("plus", "icon acc__icon")}</summary><div class="acc__body rte">{parts[i + 1]}</div></details>'
    return out


def content_page(store, pg):
    body_html = rich(pg.get("body"))
    feature = "info-page"
    if pg["handle"] in FAQ_HANDLES:
        inner, feature = faq_body(body_html), "faq"
    else:
        inner = f'<div class="rte">{body_html}</div>'
    extra = ""
    if pg["handle"] in CONTACT_HANDLES:
        extra = contact_form()
    seo = pg.get("seo") or {}
    body = (f'{page_hero(pg["title"])}{breadcrumbs([(pg["title"], "")])}'
            f'<section class="section section--tight" data-feature="{feature}"><div class="container rte-wrap">{inner}{extra}</div></section>{usp_bar()}')
    return dict(title=seo.get("title") or pg["title"], description=seo.get("description") or pg.get("bodySummary") or pg["title"], body=body,
                canonical=f"{C.STORE_URL}/pages/{pg['handle']}", page_class="page-content")


def contact_form():
    return f'''
<div class="contact-grid" data-feature="contact-form">
  <form class="form" method="post" action="{C.STORE_URL}/contact#contact_form" accept-charset="UTF-8">
    <h2>Send us a message</h2>
    <input type="hidden" name="form_type" value="contact"><input type="hidden" name="utf8" value="✓">
    <label>Name<input type="text" name="contact[name]" autocomplete="name" required></label>
    <label>Email<input type="email" name="contact[email]" autocomplete="email" required></label>
    <label>Phone (optional)<input type="tel" name="contact[phone]" autocomplete="tel"></label>
    <label>Order number (optional)<input type="text" name="contact[order]"></label>
    <label>Message<textarea name="contact[body]" rows="5" required></textarea></label>
    <button class="btn btn--dark" type="submit">Send message</button>
    <p class="small muted">Messages go to the Micro NZ customer service team.</p>
  </form>
  <aside class="contact-card"><h2>Other ways to reach us</h2>
    <p>{icon("phone")} <a href="tel:{C.CONTACT["phone"].replace(" ", "")}">{esc(C.CONTACT["phone"])}</a></p>
    <p>{icon("mail")} Use the form and we'll reply by email.</p>
    <p>{esc(C.CONTACT["address"])}</p>
    <p><a href="{U("/pages/scooter-faq-help-desk")}">Browse our FAQs ›</a></p></aside>
</div>'''


def policy(store, key, pol):
    body = (f'{page_hero(pol["title"])}{breadcrumbs([(pol["title"], "")])}'
            f'<section class="section section--tight" data-feature="policy"><div class="container rte-wrap"><div class="rte">{rich(pol.get("body"))}</div></div></section>')
    return dict(title=pol["title"], description=f'{C.STORE_NAME} {pol["title"].lower()}', body=body,
                canonical=f"{C.STORE_URL}/policies/{pol['handle']}", page_class="page-content")


# ---------------------------------------------------------------- spares
def spares_landing(store):
    steps = [("Step 1: Spares finder", "Choose your scooter and find the part you need.", "Spares finder", "/pages/spares-finder", "micro-sprite-scooter-spare-parts"),
             ("Step 2: Repair guides", "Follow our how-to guides to fit the part yourself.", "How-to guides", "/blogs/how-tos", "maxi-micro-scooter-spare-parts"),
             ("Step 3: Ask an expert", "Not sure which part you need? Our Wellington team can help identify it.", "Contact us", "/pages/contact", "mini-micro-deluxe-spare-parts"),
             ("Step 4: Book a repair", "Prefer to leave it to us? We service scooters in our workshop.", "Scooter repairs", "/pages/scooter-repairs", "micro-flex-scooter-spare-parts")]
    rows = "".join(f'<div class="step-row{" step-row--flip" if i % 2 else ""}"><div class="step-row__media">{img(coll_img(store, coll), "", "(min-width: 990px) 45vw, 100vw")}</div>'
                   f'<div class="step-row__text"><h2>{esc(t)}</h2><p>{esc(s)}</p><a class="btn btn--dark" href="{U(l)}">{esc(cta)}</a></div></div>'
                   for i, (t, s, cta, l, coll) in enumerate(steps))
    body = (f'{page_hero("Spares and repairs", "We stock replacement parts for current and past Micro models, so most scooters can be repaired rather than thrown away.")}'
            f'{breadcrumbs([("Spares and repairs", "")])}'
            f'<section class="section" data-feature="spares-steps"><div class="container"><h2 class="section__title">Repair, revamp or refurbish your scooter in 4 easy steps</h2>{rows}</div></section>'
            f'{section(f"""<div class="container media-pair"><a class="look-tile" href="{U("/pages/scooter-maintenance")}">{img(coll_img(store, "kids-scooters"), "", "45vw")}<span>Scooter maintenance ›</span></a><a class="look-tile" href="{U("/collections/micro-helmets-spare-parts")}">{img(coll_img(store, "all-helmets-safety-gear"), "", "45vw")}<span>Helmet spare parts ›</span></a></div>""", "section--grey")}')
    return dict(title="Spares and repairs", description="Spare parts, repair guides and servicing for Micro scooters in New Zealand.", body=body,
                canonical=f"{C.STORE_URL}/pages/micro-parts", page_class="page-spares")


def spare_model(store, c):
    """(tab, model name, image url) for a spare-part collection."""
    tab, name = C.SPARES_MODELS.get(c["handle"], ("other", re.sub(r"(?i)\s*(scooter\s*)?(spare\s*)?parts?(\s*online)?$", "", c["title"])))
    image = (c.get("image") or {}).get("url", "")
    if not image:
        fits = [p for p in store.products if p.get("_spares") == c["handle"] and p["_images"]]
        parts = store.collection_products(c["handle"])
        image = fits[0]["_images"][0]["url"] if fits else next((p["_images"][0]["url"] for p in parts if p["_images"]), "")
    return tab, name, image


def part_counts(prods):
    labels = {code: label for code, label, _ in D.PART_TYPES}
    labels["other"] = "Other parts"
    counts = {}
    for p in prods:
        counts[p["_part"]] = counts.get(p["_part"], 0) + 1
    order = [code for code, _, _ in D.PART_TYPES] + ["other"]
    return [(code, labels[code], counts[code]) for code in order if counts.get(code)]


def spares_finder(store):
    models = []
    for c in store.spare_collections:
        prods = store.collection_products(c["handle"])
        if prods:
            tab, name, image = spare_model(store, c)
            models.append((tab, name, image, c, prods))
    tabs, panels = "", ""
    tab_list = C.SPARES_TABS + [("other", "Other")]
    first = True
    for key, label in tab_list:
        ms = sorted([m for m in models if m[0] == key], key=lambda m: m[1].lower())
        if not ms:
            continue
        tabs += (f'<button class="tab{" is-active" if first else ""}" role="tab" aria-selected="{"true" if first else "false"}" '
                 f'aria-controls="sf-{key}" data-tab="sf-{key}">{esc(label)} <span class="tab__n">{len(ms)}</span></button>')
        tiles = ""
        for _, name, image, c, prods in ms:
            chips = "".join(f'<li><a href="{U("/collections/" + c["handle"] + "?pt=" + code)}">{esc(lbl)} <span>{n}</span></a></li>'
                            for code, lbl, n in part_counts(prods)[:4])
            tiles += (f'<article class="model-tile" data-model="{esc(name.lower())}" data-tabkey="{key}">'
                      f'<a class="model-tile__media" href="{U("/collections/" + c["handle"])}" tabindex="-1" aria-hidden="true">'
                      f'{img(image, "", "(min-width: 990px) 16vw, 40vw", widths=(180, 360, 540))}</a>'
                      f'<div class="model-tile__body"><h3><a href="{U("/collections/" + c["handle"])}">{esc(name)}</a></h3>'
                      f'<p class="small muted">{len(prods)} part{"s" if len(prods) != 1 else ""}</p><ul class="chips">{chips}</ul></div></article>')
        panels += (f'<div class="tabpanel{" is-active" if first else ""}" role="tabpanel" id="sf-{key}"{"" if first else " hidden"}>'
                   f'<div class="model-grid">{tiles}</div></div>')
        first = False
    steps = (f'<ol class="finder-steps"><li class="is-active"><span>1</span>Choose your scooter</li><li><span>2</span>Choose the part</li>'
             f'<li><span>3</span>Fit it with our <a href="{U("/blogs/how-tos")}">repair guides</a></li></ol>')
    search = (f'<div class="finder-search"><label for="sf-q">Search for your model</label><div class="search-form search-form--page">{icon("search")}'
              f'<input id="sf-q" type="search" placeholder="e.g. Sprite, Mini Micro Deluxe, Flex" data-finder-search autocomplete="off"></div>'
              f'<p class="small muted" data-finder-status aria-live="polite"></p></div>')
    quick = "".join(f'<li><a class="pill" href="{U("/search?q=" + q)}">{esc(l)}</a></li>'
                    for l, q in [("Wheels", "wheel"), ("Grips", "grip"), ("Brakes", "brake"), ("Grip tape", "grip+tape"), ("Bearings", "bearing"), ("Handlebars", "handlebar")])
    body = (f'{page_hero("Spares finder", "Pick your scooter to see every replacement part we stock for it.")}'
            f'{breadcrumbs([("Spares and repairs", "/pages/spares-and-repairs"), ("Spares finder", "")])}'
            f'<section class="section" data-feature="spares-finder"><div class="container">{steps}{search}'
            f'<div class="section__head"><h2>Spare parts by model</h2><div class="tabs tabs--wrap" role="tablist" data-finder-tabs>{tabs}</div></div>'
            f'{panels}<div class="finder-empty" data-finder-empty hidden><p>No model matches that search.</p>'
            f'<p><a href="{U("/pages/contact")}">Send us a photo</a> and we will identify it for you.</p></div>'
            f'<div class="finder-quick"><p class="eyebrow">Looking for a type of part?</p><ul class="pill-row">{quick}</ul></div></div></section>'
            f'{section(f"""<div class="container"><div class="cta-split"><div><h2>Not sure which scooter you have?</h2><p>The model name is usually printed on the frame, under the deck or on the folding block. Still stuck? Send us a photo and we will identify it.</p><a class="btn btn--dark" href="{U("/pages/contact")}">Ask an expert</a></div><div class="cta-split__icon">{icon("wrench", "icon icon--xl")}</div></div></div>""", "section--grey")}')
    return dict(title="Spares finder", description="Find genuine Micro spare parts for your scooter model.", body=body,
                canonical=f"{C.STORE_URL}/pages/micro-parts", page_class="page-spares")


def parts_extras(store, c, prods):
    """Model spares page extras: which scooters it fits, part-type shortcuts, matching repair guides."""
    _, name, _ = spare_model(store, c)
    fits = [p for p in store.visible_products() if p.get("_spares") == c["handle"]]
    chips = "".join(f'<li><a class="pill" href="?pt={code}#products" data-pt-link="{code}">{esc(lbl)} <span>{n}</span></a></li>' for code, lbl, n in part_counts(prods))
    key = name.lower().replace("+", "").split()[-1] if name else ""
    words = [w for w in name.lower().replace("+", "").split() if w not in ("micro", "mini", "the")] or [key]
    guides = [a for a in store.articles if a["blog"]["handle"] in ("how-tos", "buying-guides") and all(w in a["title"].lower() for w in words)][:3]
    fits_html = "".join(f'<li><a href="{U("/products/" + p["handle"])}">{img(p["_images"][0]["url"] if p["_images"] else "", "", "64px", widths=(80, 160))}<span>{esc(p["title"])}</span></a></li>' for p in fits[:8])
    out = (f'<section class="parts-help" data-feature="parts-help"><div class="container parts-help__grid">'
           f'<div><p class="eyebrow">Step 2: choose the part</p><h2>Parts for the {esc(name)}</h2><ul class="pill-row">{chips}</ul>'
           f'<p class="small"><a href="{U("/pages/spares-finder")}">‹ Not your model? Back to the spares finder</a></p></div>')
    if fits_html:
        out += f'<div><p class="eyebrow">Fits these scooters</p><ul class="fits">{fits_html}</ul></div>'
    out += '</div></section>'
    guide_html = "".join(article_card(a) for a in guides)
    after = section(f'<div class="container"><h2 class="section__title">Repair guides for the {esc(name)}</h2><div class="post-grid">{guide_html}</div></div>', "", "repair-guides") if guides else ""
    return out, after


# ---------------------------------------------------------------- blog
def blog_tabs(store, active):
    links = [("All stories", "/blogs", active == "")] + [(b["title"], f"/blogs/{b['handle']}", active == b["handle"]) for b in store.blogs
                                                         if any(a["blog"]["handle"] == b["handle"] for a in store.articles)]
    return '<div class="tabs tabs--links">' + "".join(f'<a class="tab{" is-active" if on else ""}" href="{U(l)}"{" aria-current=page" if on else ""}>{esc(t)}</a>' for t, l, on in links) + "</div>"


def blog_list(store, blog=None, page_size=12):
    arts = [a for a in store.articles if not blog or a["blog"]["handle"] == blog["handle"]]
    title = blog["title"] if blog else "The Micro blog"
    cards = "".join(article_card(a) for a in arts)
    feature = "blog-list" if blog else "blog-hub"
    body = (f'{page_hero(title, "Buying guides, how-tos and stories from the Micro family.")}'
            f'{breadcrumbs([("Blog", "/blogs"), (title, "")] if blog else [("Blog", "")])}'
            f'<section class="section section--tight" data-feature="{feature}"><div class="container">{blog_tabs(store, blog["handle"] if blog else "")}'
            f'<div class="post-grid" data-paged="{page_size}">{cards}</div>'
            f'<div class="load-more"><button class="btn btn--outline" data-load-more-posts{"" if len(arts) > page_size else " hidden"}>Load more stories</button></div></div></section>')
    canon = f"{C.STORE_URL}/blogs/{blog['handle']}" if blog else f"{C.STORE_URL}/pages/blog"
    return dict(title=title, description=f"{title}: articles from Micro Scooters NZ.", body=body, canonical=canon, page_class="page-blog")


def article(store, a):
    im = (a.get("image") or {}).get("url", "")
    url = f"{C.STORE_URL}/blogs/{a['blog']['handle']}/{a['handle']}"
    related = [x for x in store.articles if x["blog"]["handle"] == a["blog"]["handle"] and x["handle"] != a["handle"]][:3]
    share = (f'<ul class="share" aria-label="Share"><li><a href="https://www.facebook.com/sharer/sharer.php?u={esc(url)}" rel="noopener" aria-label="Share on Facebook">{icon("facebook")}</a></li>'
             f'<li><a href="mailto:?subject={esc(a["title"])}&amp;body={esc(url)}" aria-label="Share by email">{icon("mail")}</a></li>'
             f'<li><button class="icon-btn" data-copy="{esc(url)}" aria-label="Copy link">{icon("link")}</button></li></ul>')
    author = (a.get("authorV2") or {}).get("name") or "Micro Scooters"
    date = (a.get("publishedAt") or "")[:10]
    body = f'''
<article class="article" data-feature="article">
  <header class="article__hero">{img(im, a["title"], "100vw", eager=True, cls="article__img") if im else ""}
    <div class="container article__head"><p class="eyebrow"><a href="{U("/blogs/" + a["blog"]["handle"])}">{esc(a["blog"]["title"])}</a></p><h1 class="display">{esc(a["title"])}</h1>
    <p class="article__meta"><time datetime="{date}">{nz_date(date)}</time> · {esc(author)}</p></div></header>
  {breadcrumbs([("Blog", "/blogs"), (a["blog"]["title"], "/blogs/" + a["blog"]["handle"]), (a["title"], "")])}
  <div class="container article__body"><div class="rte">{rich(a.get("contentHtml"))}</div>{share}</div>
</article>
{section(f'<div class="container"><h2 class="section__title">More from {esc(a["blog"]["title"])}</h2><div class="post-grid">{"".join(article_card(x) for x in related)}</div></div>', "section--grey") if related else ""}'''
    seo = a.get("seo") or {}
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": a["title"], "datePublished": a.get("publishedAt"),
          "author": {"@type": "Person", "name": author}, "image": im or None}
    return dict(title=seo.get("title") or a["title"], description=seo.get("description") or strip_tags(a.get("excerpt") or a.get("contentHtml"), 160),
                body=body, canonical=url, page_class="page-article", json_ld=ld)


# ---------------------------------------------------------------- tools
def quiz(store):
    steps = C.QUIZ["steps"]
    n = len(steps)
    html_steps = ""
    for i, st in enumerate(steps):
        multi = st.get("multi")
        kind = "checkbox" if multi else "radio"
        opts = ""
        for o in st["options"]:
            ages = " ".join(o.get("ages", []))
            opts += (f'<label class="quiz__opt" data-ages="{ages}"><input type="{kind}" name="{st["id"]}" value="{o["v"]}">'
                     f'<span class="quiz__opt-body"><b>{esc(o["l"])}</b>{f"<small>{esc(o["d"])}</small>" if o.get("d") else ""}</span>'
                     f'{icon("check", "icon quiz__tick")}</label>')
        back = '<button type="button" class="btn btn--outline" data-quiz-back>Back</button>' if i else ""
        skip = '<button type="button" class="btn btn--ghost" data-quiz-skip>Skip</button>' if multi else ""
        hint = f'<p class="small muted">{esc(st["hint"])}</p>' if st.get("hint") else ""
        html_steps += (f'<fieldset class="quiz__step" data-step="{i}" data-id="{st["id"]}"{f" data-multi={multi}" if multi else ""}{"" if i == 0 else " hidden"}>'
                       f'<legend tabindex="-1"><span class="eyebrow">Question {i + 1} of {n}</span><span class="quiz__q">{esc(st["q"])}</span></legend>{hint}'
                       f'<div class="quiz__opts">{opts}</div><div class="btn-row">{back}{skip}'
                       f'<button type="button" class="btn btn--dark" data-quiz-next disabled>{"See my matches" if i == n - 1 else "Next"}</button></div></fieldset>')
    progress = f'<div class="quiz__progress" aria-hidden="true"><span data-quiz-bar style="width:{100 // n}%"></span></div>'
    body = (f'{page_hero("Find their perfect scooter", f"Answer up to {n} quick questions and we will match them to the right Micro.")}'
            f'{breadcrumbs([("Scooter adviser", "")])}'
            f'<section class="section" data-feature="quiz"><div class="container quiz">{progress}'
            f'<form class="quiz__form" data-quiz data-pools=\'{esc(json.dumps(C.QUIZ["pools"]))}\' novalidate>{html_steps}</form>'
            f'<div class="quiz__results" data-quiz-results hidden tabindex="-1" aria-live="polite">'
            f'<div class="section__head"><h2 data-quiz-title>Our top picks</h2><div class="btn-row"><a class="btn btn--outline" data-quiz-compare href="{U("/pages/compare-scooters")}">Compare these</a>'
            f'<button type="button" class="btn btn--ghost" data-quiz-restart>Start again</button></div></div>'
            f'<p class="quiz__summary" data-quiz-summary></p><p class="quiz__note" data-quiz-note hidden></p>'
            f'<div class="quiz-picks" data-quiz-grid></div>'
            f'<div data-quiz-more-wrap hidden><h3 class="section__title" data-quiz-more-title>More good matches</h3><div class="grid" data-quiz-more></div></div></div>'
            f'<noscript><p>The scooter adviser needs JavaScript. Browse <a href="{U("/collections/all-scooters")}">all scooters</a> instead.</p></noscript>'
            f'</div></section>{usp_bar()}')
    return dict(title="Which scooter is right for you?", description="Answer up to five questions to find the right Micro scooter, ride-on or balance bike.", body=body,
                canonical=f"{C.STORE_URL}/pages/which-kids-scooter-should-i-buy-quiz", page_class="page-quiz")


def search_page(store):
    body = (f'{page_hero("Search")}{breadcrumbs([("Search", "")])}'
            f'<section class="section section--tight" data-feature="search-page"><div class="container">'
            f'<form class="search-form search-form--page" action="{U("/search")}" role="search">{icon("search")}<input type="search" name="q" aria-label="Search" placeholder="Search" data-search-input></form>'
            f'<div class="tabs" role="tablist" data-search-tabs><button class="tab is-active" data-tab="sr-products" role="tab" aria-selected="true">Products <span data-n="products"></span></button>'
            f'<button class="tab" data-tab="sr-articles" role="tab" aria-selected="false">Articles <span data-n="articles"></span></button>'
            f'<button class="tab" data-tab="sr-pages" role="tab" aria-selected="false">Pages <span data-n="pages"></span></button></div>'
            f'<div class="tabpanel is-active" id="sr-products" role="tabpanel"><div class="grid" data-search-products></div></div>'
            f'<div class="tabpanel" id="sr-articles" role="tabpanel" hidden><div class="post-grid" data-search-articles></div></div>'
            f'<div class="tabpanel" id="sr-pages" role="tabpanel" hidden><ul class="link-list" data-search-pages></ul></div>'
            f'<p class="muted" data-search-status>Type to search the full Micro range.</p></div></section>')
    return dict(title="Search", description="Search Micro scooters, helmets, accessories and spare parts.", body=body,
                canonical=C.STORE_URL + "/search", page_class="page-search")


def cart_page(store):
    body = (f'{page_hero("Your cart")}{breadcrumbs([("Cart", "")])}'
            f'<section class="section section--tight" data-feature="cart-page"><div class="container cart-page">'
            f'<div class="cart-page__lines" data-cart-page-lines><p class="muted">Loading your cart…</p></div>'
            f'<aside class="cart-page__summary"><div class="ship-progress" data-ship-progress><p data-ship-text></p><div class="ship-progress__bar"><span data-ship-bar></span></div></div>'
            f'<div class="cart-total"><span>Subtotal</span><b data-cart-subtotal>$0.00</b></div><p class="small muted">Shipping and discount codes are applied at checkout on microscooters.co.nz.</p>'
            f'<a class="btn btn--dark btn--block" data-checkout href="{C.STORE_URL}/cart">Checkout</a></aside></div></section>{usp_bar()}')
    return dict(title="Your cart", description="Your Micro Scooters cart.", body=body, canonical=C.STORE_URL + "/cart", page_class="page-cart")


def not_found(store):
    tiles = "".join(f'<a class="sub-tile" href="{U(l)}"><span><b>{esc(t)}</b><small>Shop now</small></span>{img(coll_img(store, l.rsplit("/", 1)[-1]), "", "120px", widths=(120, 240))}</a>'
                    for t, l in [("Toddler scooters", "/collections/toddler-preschool-scooters"), ("Kids scooters", "/collections/kids-scooters"),
                                 ("Adult scooters", "/collections/adult-scooters"), ("Helmets", "/collections/all-helmets-safety-gear")])
    body = (f'<section class="page-hero" data-feature="not-found"><div class="container"><h1 class="display">Page not found</h1><p>That page has scooted off. Try a search or one of these.</p>'
            f'<form class="search-form search-form--page" action="{U("/search")}" role="search">{icon("search")}<input type="search" name="q" aria-label="Search" placeholder="Search"></form></div></section>'
            f'<section class="section"><div class="container"><div class="sub-strip__grid">{tiles}</div></div></section>')
    return dict(title="Page not found", description="Page not found.", body=body, page_class="page-404")
