#!/usr/bin/env python3
"""Build the static site into dist/ from the NZ Storefront snapshot in .cache/nz/.

    python3 tools/fetch_nz.py          # refresh the snapshot
    python3 build.py --base /micro-uk  # GitHub Pages project path ("" for a root domain)
"""
import argparse, hashlib, json, os, shutil, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from remake import html as H, pages as P, config as C  # noqa: E402
from remake.data import Store  # noqa: E402


def write(dist, path, doc):
    """path is a site path like /products/x -> dist/products/x/index.html"""
    rel = path.strip("/")
    target = os.path.join(dist, rel, "index.html") if rel else os.path.join(dist, "index.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w") as f:
        f.write(doc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("SITE_BASE", "/micro-uk"))
    ap.add_argument("--cache", default=os.path.join(ROOT, ".cache", "nz"))
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    a = ap.parse_args()
    t0 = time.time()
    store = Store(a.cache)
    H.BASE = a.base.rstrip("/")
    dist = a.out
    shutil.rmtree(dist, ignore_errors=True)
    os.makedirs(os.path.join(dist, "assets"))

    # ---- client data
    visible = store.visible_products()
    catalogue = [store.compact(p) for p in visible]
    content = ([{"t": pg["title"], "u": f"/pages/{pg['handle']}", "x": P.strip_tags(pg.get("bodySummary") or pg.get("body"), 160), "k": "page"}
                for pg in store.pages]
               + [{"t": ar["title"], "u": f"/blogs/{ar['blog']['handle']}/{ar['handle']}", "x": P.strip_tags(ar.get("excerpt") or ar.get("contentHtml"), 160),
                   "k": "article", "b": ar["blog"]["title"], "i": (ar.get("image") or {}).get("url", ""), "d": (ar.get("publishedAt") or "")[:10]}
                  for ar in store.articles]
               + [{"t": c["title"], "u": f"/collections/{c['handle']}", "x": P.first_sentences(c.get("description"), 140), "k": "collection",
                   "i": (c.get("image") or {}).get("url", "")} for c in store.collections if store.collection_products(c["handle"])])
    assets = {
        "catalogue.json": json.dumps(catalogue, separators=(",", ":")),
        "content-index.json": json.dumps(content, separators=(",", ":")),
        "site.css": open(os.path.join(ROOT, "assets", "site.css")).read(),
        "app.js": open(os.path.join(ROOT, "assets", "app.js")).read(),
    }
    for name, text in assets.items():
        H.ASSET_VER[name] = hashlib.sha1(text.encode()).hexdigest()[:10]
        with open(os.path.join(dist, "assets", name), "w") as f:
            f.write(text)

    # ---- routes (known before rendering so CMS links can be pointed at remake pages)
    policies = {k: v for k, v in store.shop.items() if k in ("shippingPolicy", "refundPolicy", "privacyPolicy", "termsOfService") and v}
    feature_pages = {"/pages/spares-and-repairs": P.spares_landing, "/pages/spares-finder": P.spares_finder,
                     "/pages/your-best-micro-scooter": P.quiz, "/pages/compare-scooters": P.compare_page,
                     "/search": P.search_page, "/cart": P.cart_page, "/collections": P.collections_index}
    routes = {"/"} | set(feature_pages) | {"/blogs"}
    routes |= {f"/products/{p['handle']}" for p in store.products}
    routes |= {f"/collections/{c['handle']}" for c in store.collections}
    routes |= {f"/pages/{pg['handle']}" for pg in store.pages if f"/pages/{pg['handle']}" not in feature_pages}
    routes |= {f"/blogs/{b['handle']}" for b in store.blogs}
    routes |= {f"/blogs/{ar['blog']['handle']}/{ar['handle']}" for ar in store.articles}
    routes |= {f"/policies/{v['handle']}" for v in policies.values()}
    H.ROUTES.clear()
    H.ROUTES.update(routes)

    def emit(path, page):
        write(dist, path, H.layout(store, **page))

    emit("/", P.home(store))
    for path, fn in feature_pages.items():
        emit(path, fn(store))
    for p in store.products:
        emit(f"/products/{p['handle']}", P.product(store, p))
    for c in store.collections:
        emit(f"/collections/{c['handle']}", P.collection(store, c))
    for pg in store.pages:
        if f"/pages/{pg['handle']}" not in feature_pages:
            emit(f"/pages/{pg['handle']}", P.content_page(store, pg))
    emit("/blogs", P.blog_list(store))
    for b in store.blogs:
        emit(f"/blogs/{b['handle']}", P.blog_list(store, b))
    for ar in store.articles:
        emit(f"/blogs/{ar['blog']['handle']}/{ar['handle']}", P.article(store, ar))
    for key, pol in policies.items():
        emit(f"/policies/{pol['handle']}", P.policy(store, key, pol))
    with open(os.path.join(dist, "404.html"), "w") as f:
        f.write(H.layout(store, **P.not_found(store)))
    with open(os.path.join(dist, ".nojekyll"), "w") as f:
        f.write("")
    with open(os.path.join(dist, "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /\n")
    manifest = {"built": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "base": H.BASE, "routes": sorted(routes),
                "counts": {"products": len(store.products), "visible_products": len(visible), "collections": len(store.collections),
                           "pages": len(store.pages), "articles": len(store.articles), "blogs": len(store.blogs), "policies": len(policies)}}
    with open(os.path.join(dist, "build-manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"built {len(routes) + 1} pages into {os.path.relpath(dist, ROOT)} in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
