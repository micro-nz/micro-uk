"""HTML helpers and shared components (layout, header, footer, product cards)."""
import html, json, re
from . import config as C

BASE = ""          # set by build.py, e.g. "/micro-uk"
ASSET_VER = {}     # file name -> short hash, set by build.py
ROUTES = set()     # every site path the build will write, set by build.py

esc = lambda s: html.escape(str(s or ""), quote=True)


def U(path):
    """Site path -> URL under BASE, with a trailing slash for page paths."""
    if not path or re.match(r"^(https?:|mailto:|tel:|#)", path):
        return path
    path, _, frag = path.partition("#")
    path, _, query = path.partition("?")
    if not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
        path += "/"
    out = BASE + path
    return out + (("?" + query) if query else "") + (("#" + frag) if frag else "")


def asset(name):
    return f"{BASE}/assets/{name}?v={ASSET_VER.get(name, '0')}"


def money(x):
    return f"{C.CURRENCY_SYMBOL}{x:,.2f}"


def sized(url, width):
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url
    if "cdn.shopify.com" in url or "/cdn/shop/" in url:
        url = re.sub(r"([?&])width=\d+&?", r"\1", url).rstrip("?&")
        return url + ("&" if "?" in url else "?") + f"width={width}"
    return url


def img(url, alt="", sizes="100vw", widths=(180, 360, 540, 720, 960, 1200, 1600), cls="", eager=False, w=None, h=None, extra=""):
    if not url:
        return f'<div class="img-placeholder {esc(cls)}" role="img" aria-label="{esc(alt)}"></div>'
    srcset = ", ".join(f"{sized(url, x)} {x}w" for x in widths)
    dims = f' width="{w}" height="{h}"' if w and h else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{sized(url, widths[min(3, len(widths) - 1)])}" srcset="{srcset}" sizes="{esc(sizes)}" alt="{esc(alt)}"'
            f'{dims} class="{esc(cls)}" {load} decoding="async"{extra}>')


def icon(name, cls="icon"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"></use></svg>'


ICONS = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "cart": '<path d="M3 4h2l2.4 11.2a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 2-1.5L21 8H6.2"/><circle cx="10" cy="20.5" r="1.2"/><circle cx="17" cy="20.5" r="1.2"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "close": '<path d="M5 5l14 14M19 5 5 19"/>',
    "down": '<path d="m6 9 6 6 6-6"/>',
    "right": '<path d="m9 6 6 6-6 6"/>',
    "left": '<path d="m15 6-6 6 6 6"/>',
    "truck": '<path d="M2 6h11v10H2zM13 10h4l4 4v2h-8z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "tag": '<path d="M3 12V3h9l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "shield": '<path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    "star": '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1 6.2L12 17.3 6.5 20.2l1-6.2L3 9.6l6.2-.9z"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "minus": '<path d="M5 12h14"/>',
    "filter": '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
    "check": '<path d="m5 12 5 5 9-10"/>',
    "edit": '<path d="M4 20h4L20 8l-4-4L4 16z"/>',
    "expand": '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6"/>',
    "facebook": '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8z"/>',
    "youtube": '<rect x="2" y="5" width="20" height="14" rx="4"/><path d="m10 9 5 3-5 3z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "phone": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
    "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    "age": '<circle cx="8" cy="6" r="2.5"/><circle cx="16" cy="8" r="2"/><path d="M4 21v-6a4 4 0 0 1 8 0v6M13 21v-4a3 3 0 0 1 6 0v4"/>',
    "wheel": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/>',
    "spark": '<path d="M12 2v5M12 17v5M2 12h5M17 12h5M5 5l3.5 3.5M15.5 15.5 19 19M5 19l3.5-3.5M15.5 8.5 19 5"/>',
}


def icon_sprite():
    syms = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" '
                   f'stroke-linecap="round" stroke-linejoin="round">{v}</symbol>' for k, v in ICONS.items())
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{syms}</svg>'


def stars_slot(product_id, cls=""):
    return f'<div class="rating {cls}" data-feature="rating" data-okendo="{esc(product_id)}" aria-live="polite"></div>'


# ---------------------------------------------------------------- product card
def price_html(price, compare):
    if compare:
        return (f'<div class="price price--sale"><span class="price__now">Now {money(price)}</span>'
                f'<span class="price__was">Was <s>{money(compare)}</s></span></div>')
    return f'<div class="price"><span class="price__now">{money(price)}</span></div>'


def product_card(p, sizes="(min-width: 990px) 22vw, (min-width: 750px) 30vw, 46vw"):
    imgs = p["_images"]
    url = U(f"/products/{p['handle']}")
    media = img(imgs[0]["url"] if imgs else "", imgs[0].get("altText") or p["title"] if imgs else p["title"], sizes, cls="card__img")
    hover = img(imgs[1]["url"], "", sizes, cls="card__img card__img--hover") if len(imgs) > 1 else ""
    badge = f'<span class="badge badge--{esc(p["_badge"].lower().replace(" ", "-"))}">{esc(p["_badge"])}</span>' if p["_badge"] else ""
    sw = p["_swatches"]
    swatches = ""
    if len(sw) > 1:
        items = "".join(f'<li title="{esc(s["name"])}">{img(s["img"], s["name"], "40px", widths=(60, 120), cls="swatch__img")}</li>' for s in sw[:6])
        more = f'<li class="swatch__more">+{len(sw) - 6}</li>' if len(sw) > 6 else ""
        swatches = f'<ul class="card__swatches" aria-label="{len(sw)} colours">{items}{more}</ul>'
    pills = "".join(f"<li>{esc(label)}</li>" for _, label in p["_features"][:2])
    pills = f'<ul class="pills">{pills}</ul>' if pills else ""
    return (f'<article class="card" data-feature="product-card" data-h="{esc(p["handle"])}">'
            f'<a class="card__media" href="{url}" tabindex="-1" aria-hidden="true">{media}{hover}{badge}</a>{swatches}'
            f'<div class="card__body"><h3 class="card__title"><a href="{url}">{esc(p["title"])}</a></h3>'
            f'{price_html(p["_price"], p["_compare"])}{pills}</div></article>')


# ---------------------------------------------------------------- header
def _menu_link(label, link, cls=""):
    return f'<a class="{cls}" href="{esc(U(link))}">{esc(label)}</a>'


def mega_menu(store):
    tabs, panels = [], []
    for i, (label, link, cols, promo_key) in enumerate(C.MEGA_MENU):
        tid = f"mega-{i}"
        tabs.append(f'<li><a class="mega__tab{" is-active" if i == 0 else ""}" href="{esc(U(link))}" data-panel="{tid}">'
                    f'{esc(label)}{icon("right", "icon icon--sm")}</a></li>')
        colhtml = ""
        for heading, hlink, links in cols:
            lis = "".join(f"<li>{_menu_link(l, h)}</li>" for l, h in links)
            colhtml += f'<div class="mega__col"><a class="mega__heading" href="{esc(U(hlink))}">{esc(heading)}</a><ul>{lis}</ul></div>'
        if not cols:
            colhtml = f'<div class="mega__col"><a class="mega__heading" href="{esc(U(link))}">{esc(label)}</a><p class="mega__lead">Shop the full {esc(label.lower())} range.</p></div>'
        promos = ""
        for eyebrow, cta, plink, coll in C.MEGA_PROMOS.get(promo_key or "", [])[:2]:
            cimg = (store.collection_by_handle.get(coll, {}).get("image") or {}).get("url", "")
            promos += (f'<a class="promo-tile" href="{esc(U(plink))}">{img(cimg, "", "260px", widths=(260, 520))}'
                       f'<span class="promo-tile__text"><span>{esc(eyebrow)}</span><b>{esc(cta)} ›</b></span></a>')
        panels.append(f'<div class="mega__panel{" is-active" if i == 0 else ""}" id="{tid}"><div class="mega__cols">{colhtml}</div>'
                      f'<div class="mega__promos">{promos}</div></div>')
    return (f'<div class="mega" id="mega-shop" data-feature="mega-menu" hidden><div class="mega__inner">'
            f'<ul class="mega__tabs">{"".join(tabs)}</ul>{"".join(panels)}</div></div>')


def dropdown(did, feature, groups):
    cols = ""
    for heading, links in groups:
        lis = "".join(f"<li>{_menu_link(l, h)}</li>" for l, h in links)
        cols += f'<div class="mega__col"><p class="mega__heading">{esc(heading)}</p><ul>{lis}</ul></div>'
    return f'<div class="mega mega--simple" id="{did}" data-feature="{feature}" hidden><div class="mega__inner"><div class="mega__cols">{cols}</div></div></div>'


def mobile_menu():
    def panel(pid, title, items, back=True):
        lis = ""
        for label, target in items:
            if target.startswith("panel:"):
                lis += f'<li><button class="mm__next" data-to="{target[6:]}">{esc(label)}{icon("right")}</button></li>'
            else:
                lis += f'<li><a href="{esc(U(target))}">{esc(label)}</a></li>'
        head = (f'<button class="mm__back" data-to="mm-root">{icon("left")} Back</button>' if back else "")
        return f'<div class="mm__panel" id="{pid}"{"" if not back else " hidden"}>{head}<p class="mm__title">{esc(title)}</p><ul>{lis}</ul></div>'
    panels = []
    root = [(label, f"panel:mm-{i}") if cols else (label, link) for i, (label, link, cols, _) in enumerate(C.MEGA_MENU)]
    root += [("Help & support", "panel:mm-help"), ("About Micro", "panel:mm-about"), ("My account", C.STORE_URL + "/account")]
    panels.append(panel("mm-root", "Shop", root, back=False))
    for i, (label, link, cols, _) in enumerate(C.MEGA_MENU):
        if not cols:
            continue
        items = []
        for heading, hlink, links in cols:
            items += [(f"{heading}: {l}" if len(cols) > 1 and l == "View all" else l, h) for l, h in links]
        panels.append(panel(f"mm-{i}", label, items))
    panels.append(panel("mm-help", "Help & support", [x for _, links in C.HELP_MENU for x in links]))
    panels.append(panel("mm-about", "About Micro", [x for _, links in C.ABOUT_MENU for x in links]))
    return (f'<div class="drawer drawer--left" id="mobile-menu" data-feature="mobile-menu" hidden aria-label="Menu" role="dialog" aria-modal="true">'
            f'<div class="drawer__head"><span>Menu</span><button class="icon-btn" data-close aria-label="Close menu">{icon("close")}</button></div>'
            f'<div class="mm">{"".join(panels)}</div></div>')


def header(store):
    ann = "".join(f'<a class="ann__msg{" is-active" if i == 0 else ""}" href="{esc(U(l))}">{esc(t)}</a>' for i, (t, l) in enumerate(C.ANNOUNCEMENTS))
    return f"""
<div class="proto-bar" data-feature="prototype-banner">Prototype: the micro-scooters.co.uk design, built with Micro NZ products. Orders are placed on <a href="{C.STORE_URL}">microscooters.co.nz</a>.</div>
<div class="ann" data-feature="announcement" role="region" aria-label="Announcements">{ann}</div>
<header class="site-header" data-feature="header">
  <div class="site-header__bar">
    <button class="icon-btn hide-desktop" data-open="mobile-menu" aria-label="Open menu">{icon("menu")}</button>
    <nav class="nav nav--left" aria-label="Primary">
      <button class="nav__item" data-mega="mega-shop" aria-expanded="false">Shop {icon("down", "icon icon--xs")}</button>
      <a class="nav__item" href="{esc(U('/collections/bestselling-scooters'))}" data-feature="nav-bestsellers">Best sellers</a>
    </nav>
    <a class="logo" href="{esc(U('/'))}" aria-label="Micro Scooters home"><img src="{C.LOGO}" alt="Micro" width="120" height="30"></a>
    <div class="header-right">
    <nav class="nav nav--right" aria-label="Support">
      <button class="nav__item" data-mega="mega-help" aria-expanded="false">Help &amp; support {icon("down", "icon icon--xs")}</button>
      <button class="nav__item" data-mega="mega-about" aria-expanded="false">About Micro {icon("down", "icon icon--xs")}</button>
    </nav>
    <div class="header-icons">
      <button class="icon-btn icon-btn--round" data-open="search" aria-label="Search">{icon("search")}</button>
      <a class="icon-btn icon-btn--round hide-mobile" data-feature="account-link" href="{C.STORE_URL}/account" aria-label="My account">{icon("user")}</a>
      <button class="icon-btn icon-btn--round cart-btn" data-open="cart" aria-label="Cart">{icon("cart")}<span class="cart-count" data-cart-count hidden>0</span></button>
    </div>
    </div>
  </div>
  {mega_menu(store)}
  {dropdown("mega-help", "menu-help", C.HELP_MENU)}
  {dropdown("mega-about", "menu-about", C.ABOUT_MENU)}
</header>"""


def search_overlay():
    return f"""
<div class="search-overlay" id="search" data-feature="search-overlay" hidden role="dialog" aria-modal="true" aria-label="Search">
  <div class="search-overlay__panel">
    <form class="search-form" action="{esc(U('/search'))}" role="search">
      {icon("search")}<input type="search" name="q" placeholder="Search scooters, helmets, spare parts…" autocomplete="off" aria-label="Search" data-predictive>
      <button type="button" class="icon-btn" data-close aria-label="Close search">{icon("close")}</button>
    </form>
    <div class="predictive" data-predictive-results>
      <p class="predictive__hint">Popular: <a href="{esc(U('/search?q=sprite'))}">Sprite</a> · <a href="{esc(U('/search?q=helmet'))}">Helmets</a> · <a href="{esc(U('/search?q=wheel'))}">Wheels</a> · <a href="{esc(U('/search?q=mini'))}">Mini Micro</a></p>
    </div>
  </div>
</div>"""


def cart_drawer():
    return f"""
<div class="drawer drawer--right" id="cart" data-feature="cart-drawer" hidden role="dialog" aria-modal="true" aria-label="Your cart">
  <div class="drawer__head"><span>Your cart <span data-cart-count-text></span></span><button class="icon-btn" data-close aria-label="Close cart">{icon("close")}</button></div>
  <div class="ship-progress" data-ship-progress><p data-ship-text>Spend {money(C.FREE_SHIPPING_FROM)} for free shipping</p><div class="ship-progress__bar"><span data-ship-bar></span></div></div>
  <div class="drawer__body" data-cart-lines><p class="cart-empty">Your cart is empty.</p></div>
  <div class="drawer__foot" data-cart-foot hidden>
    <div class="cart-total"><span>Subtotal</span><b data-cart-subtotal></b></div>
    <p class="small muted">Shipping calculated at checkout on microscooters.co.nz.</p>
    <a class="btn btn--dark btn--block" data-checkout href="{C.STORE_URL}/cart">Checkout</a>
    <a class="btn btn--ghost btn--block" href="{esc(U('/cart'))}">View cart</a>
  </div>
</div>"""


def usp_bar():
    items = "".join(f'<li><a href="{esc(U(l))}">{icon(ic, "icon icon--lg")}<span><b>{esc(t)}</b><small>{esc(s)}</small></span></a></li>'
                    for ic, t, s, l in C.USPS)
    return f'<section class="usp-bar" data-feature="usp-bar"><ul class="container usp-bar__list">{items}</ul></section>'


def footer():
    pillars = "".join(f'<div class="pillar"><h2>{esc(t)}</h2><p>{esc(s)}</p></div>' for t, s in C.FOOTER_PILLARS)
    cols = "".join(f'<div class="footer__col"><h2>{esc(h)}</h2><ul>{"".join(f"<li>{_menu_link(l, k)}</li>" for l, k in links)}</ul></div>'
                   for h, links in C.FOOTER_COLUMNS)
    social = "".join(f'<li><a href="{u}" aria-label="{n.title()}" rel="noopener">{icon(n)}</a></li>' for n, u in C.SOCIALS)
    legal = " ".join(f'<a href="{esc(U(u))}">{esc(t)}</a>' for t, u in C.LEGAL)
    return f"""
<footer class="footer">
  <div class="container">
    <div class="footer__pillars" data-feature="footer-pillars">{pillars}</div>
    <div class="footer__grid">
      <div class="footer__signup" data-feature="newsletter">
        <h2>Sign up for exclusive offers and news</h2>
        <form class="newsletter" method="post" action="{C.STORE_URL}/contact#newsletter" accept-charset="UTF-8">
          <input type="hidden" name="form_type" value="customer"><input type="hidden" name="utf8" value="✓">
          <input type="hidden" name="contact[tags]" value="newsletter">
          <label class="sr-only" for="nl-email">Email</label>
          <input id="nl-email" type="email" name="contact[email]" placeholder="Email" required autocomplete="email">
          <button class="btn btn--light" type="submit">Subscribe</button>
        </form>
        <p class="small">By subscribing you agree to our <a href="{esc(U('/policies/terms-of-service'))}">terms</a> and <a href="{esc(U('/policies/privacy-policy'))}">privacy policy</a>.</p>
      </div>
      <div class="footer__cols" data-feature="footer-links">{cols}
        <div class="footer__col"><h2>Get in touch</h2><ul class="footer__contact">
          <li>{icon("phone", "icon icon--sm")} <a href="tel:{C.CONTACT['phone'].replace(' ', '')}">{esc(C.CONTACT['phone'])}</a></li>
          <li>{icon("mail", "icon icon--sm")} <a href="{esc(U(C.CONTACT['page']))}">Email us</a></li>
          <li>{esc(C.CONTACT['address'])}</li></ul>
          <h2 class="mt">Follow us on social</h2><ul class="footer__social" data-feature="footer-social">{social}</ul>
        </div>
      </div>
    </div>
    <div class="footer__legal" data-feature="footer-legal">
      <p class="region" data-feature="region">Delivering to: New Zealand (NZD $)</p>
      <p>{legal}</p>
      <p>© 2026 Micro Scooters NZ · Design remake of micro-scooters.co.uk</p>
    </div>
  </div>
</footer>
<a class="help-fab" data-feature="help-fab" href="{esc(U('/pages/contact'))}" aria-label="Help and contact">{icon("chat")}</a>"""


def breadcrumbs(items):
    lis = "".join((f'<li><a href="{esc(U(l))}">{esc(t)}</a></li>' if l else f'<li aria-current="page">{esc(t)}</li>') for t, l in items)
    return f'<nav class="breadcrumbs container" aria-label="Breadcrumb" data-feature="breadcrumbs"><ol><li><a href="{esc(U("/"))}">Home</a></li>{lis}</ol></nav>'


def layout(store, *, title, description, body, canonical="", page_class="", hero_first=False, json_ld=None):
    cfg = {"base": BASE, "store": C.STORE_URL, "api": C.API_VERSION, "okendo": C.OKENDO_STORE,
           "freeShip": C.FREE_SHIPPING_FROM, "catalogue": asset("catalogue.json"), "content": asset("content-index.json")}
    ld = f'<script type="application/ld+json">{json.dumps(json_ld)}</script>' if json_ld else ""
    desc = re.sub(r"\s+", " ", description or "").strip()[:300]
    return f"""<!doctype html>
<html lang="en-NZ">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Micro Scooters</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
{f'<link rel="canonical" href="{esc(canonical)}">' if canonical else ""}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdn.shopify.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="{asset('site.css')}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='16' fill='%2328282b'/%3E%3Ctext x='16' y='22' font-size='17' text-anchor='middle' fill='white' font-family='Arial' font-weight='700'%3Em%3C/text%3E%3C/svg%3E">
<script>window.MICRO={json.dumps(cfg)}</script>
<script src="{asset('app.js')}" defer></script>
{ld}
</head>
<body class="{esc(page_class)}{' has-hero' if hero_first else ''}">
<a class="skip-link" href="#main">Skip to content</a>
{icon_sprite()}
{header(store)}
<main id="main" tabindex="-1">
{body}
</main>
{footer()}
{search_overlay()}
{cart_drawer()}
{mobile_menu()}
<div class="scrim" data-scrim hidden></div>
</body>
</html>
"""
