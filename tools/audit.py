#!/usr/bin/env python3
"""Audit the built remake against the UK feature inventory and write REMAKE_REPORT.md.

The report ends with "REMAKE COMPLETE" only when every check passes:
  1. every UK feature in spec/uk_features.json is present in the built page it belongs to
  2. every UK menu group has a working equivalent (spec/uk_nav.json)
  3. every NZ product, collection, page, article, blog and policy has a page
  4. every spare-part collection is mapped into the spares finder
  5. no broken internal links or asset references, and no links to the UK site
  6. page quality: title, description, viewport, noindex, language, one h1, alt text, unique ids
  7. size budgets
  8. quiz and comparison engine tests pass (every quiz answer combination)
  9. browser self-test (reports/runtime.json) passes for the current build
 10. the deployed GitHub Pages site serves the current build (skipped with --no-deploy-check)

    python3 tools/audit.py [--no-deploy-check]
"""
import argparse, glob, hashlib, json, os, re, shutil, subprocess, sys, time
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
sys.path.insert(0, ROOT)
from remake import config as C  # noqa: E402
from remake.data import Store  # noqa: E402

LIVE_URL = "https://micro-nz.github.io/micro-uk/"
JSC = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
ALLOWED_HOSTS = ("microscooters.co.nz", "cdn.shopify.com", "api.okendo.io", "fonts.googleapis.com", "fonts.gstatic.com",
                 "instagram.com", "facebook.com", "youtube.com", "youtu.be", "vimeo.com", "schema.org", "order.microscooters.co.nz",
                 "account.microscooters.co.nz", "afterpay.com", "google.com", "goo.gl", "maps.app.goo.gl")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.h1, self.imgs_no_alt, self.features = [], [], 0, 0, set()
        self.title = self.desc = self.viewport = self.robots = self.lang = None
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if "data-feature" in a:
            self.features.add(a["data-feature"])
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            if a.get("name") == "description":
                self.desc = a.get("content")
            elif a.get("name") == "viewport":
                self.viewport = a.get("content")
            elif a.get("name") == "robots":
                self.robots = a.get("content")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "img" and "alt" not in a:
            self.imgs_no_alt += 1
        for k in ("href", "src"):
            if a.get(k) and tag in ("a", "link", "script", "img", "iframe", "form", "source"):
                self.links.append((tag, a[k]))
        if tag == "form" and a.get("action"):
            self.links.append(("form", a["action"]))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, d):
        if self._in_title:
            self.title = (self.title or "") + d


def check(name, ok, detail, items=None):
    return {"name": name, "ok": bool(ok), "detail": detail, "items": items or []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-deploy-check", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "REMAKE_REPORT.md"))
    args = ap.parse_args()
    if not os.path.exists(os.path.join(DIST, "build-manifest.json")):
        sys.exit("Run build.py first.")
    manifest = json.load(open(os.path.join(DIST, "build-manifest.json")))
    base = manifest["base"]
    store = Store(os.path.join(ROOT, ".cache", "nz"))
    results = []

    # parse every page once
    pages = {}
    for f in glob.glob(os.path.join(DIST, "**", "*.html"), recursive=True):
        p = Page()
        p.feed(open(f, encoding="utf-8").read())
        pages[os.path.relpath(f, DIST)] = p

    # 1. features
    spec = json.load(open(os.path.join(ROOT, "spec", "uk_features.json")))["features"]
    art = store.articles[0]
    missing = []
    for ft in spec:
        page = ft["page"].replace("ARTICLE", f"blogs/{art['blog']['handle']}/{art['handle']}/index.html")
        if page not in pages or ft["marker"] not in pages[page].features:
            missing.append(f"{ft['id']} {ft['name']} — `{ft['marker']}` not in {page}")
    results.append(check("UK feature inventory", not missing, f"{len(spec) - len(missing)} of {len(spec)} UK features present", missing))

    # 2. navigation parity
    nav = json.load(open(os.path.join(ROOT, "spec", "uk_nav.json")))["groups"]
    home = open(os.path.join(DIST, "index.html"), encoding="utf-8").read()
    bad = []
    for g in nav:
        href = f'href="{base}{g["remake"].rstrip("/")}/"' if not g["remake"].startswith("http") else f'href="{g["remake"]}"'
        rel = g["remake"].strip("/")
        exists = g["remake"].startswith("http") or os.path.exists(os.path.join(DIST, rel, "index.html"))
        if not exists or href not in home:
            bad.append(f"{g['uk']} → {g['remake']} ({'missing page' if not exists else 'not linked from the header'})")
    results.append(check("UK menu parity", not bad, f"{len(nav) - len(bad)} of {len(nav)} UK menu entries have a working equivalent in the header", bad))

    # 3. coverage
    routes = set(manifest["routes"])
    need = ({f"/products/{p['handle']}" for p in store.products} | {f"/collections/{c['handle']}" for c in store.collections}
            | {f"/pages/{p['handle']}" for p in store.pages if p["handle"] not in ("spares-and-repairs", "spares-finder", "your-best-micro-scooter", "compare-scooters")}
            | {f"/blogs/{b['handle']}" for b in store.blogs} | {f"/blogs/{a['blog']['handle']}/{a['handle']}" for a in store.articles}
            | {f"/policies/{v['handle']}" for k, v in store.shop.items() if k.endswith(("Policy", "Service")) and v}
            | {"/", "/search", "/cart", "/blogs", "/collections", "/pages/spares-finder", "/pages/spares-and-repairs", "/pages/your-best-micro-scooter", "/pages/compare-scooters"})
    gaps = sorted(r for r in need if r not in routes or not os.path.exists(os.path.join(DIST, r.strip("/"), "index.html")))
    c = manifest["counts"]
    results.append(check("NZ content coverage", not gaps,
                         f"{len(need) - len(gaps)} of {len(need)} routes built ({c['products']} products, {c['collections']} collections, {c['pages']} pages, "
                         f"{c['articles']} articles, {c['blogs']} blogs, {c['policies']} policies)", gaps[:50]))

    # 4. spares mapping
    unmapped = [c["title"] for c in store.spare_collections if store.collection_products(c["handle"]) and c["handle"] not in C.SPARES_MODELS]
    stale = [h for h in C.SPARES_MODELS if h not in store.collection_by_handle or not store.collection_products(h)]
    finder = open(os.path.join(DIST, "pages", "spares-finder", "index.html"), encoding="utf-8").read()
    tiles = len(re.findall(r'class="model-tile"', finder))
    mapped = sum(1 for h in C.SPARES_MODELS if h in store.collection_by_handle and store.collection_products(h))
    no_help = [h for h in C.SPARES_MODELS if h in store.collection_by_handle and store.collection_products(h)
               and "parts-help" not in pages.get(f"collections/{h}/index.html", Page()).features]
    results.append(check("Spares finder mapping", not unmapped and tiles == mapped and not no_help,
                         f"{tiles} model tiles for {mapped} mapped spare-part collections; {len(stale)} mapped collections currently empty",
                         [f"unmapped: {t}" for t in unmapped] + [f"no parts help: {h}" for h in no_help]))

    # 5. links
    broken, uk_links, bad_hosts = [], [], set()
    for rel, p in pages.items():
        for tag, url in p.links:
            if url.startswith(("mailto:", "tel:", "#", "data:", "javascript:")):
                continue
            if "micro-scooters.co.uk" in url:
                uk_links.append(f"{rel}: {url}")
                continue
            m = re.match(r"https?://([^/]+)", url) or re.match(r"//([^/]+)", url)
            if m:
                host = m.group(1).lower()
                if not any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS):
                    bad_hosts.add(host)
                continue
            path = url.split("#")[0].split("?")[0]
            if not path:
                continue
            if not path.startswith(base + "/"):
                broken.append(f"{rel}: {url} (outside {base})")
                continue
            local = os.path.join(DIST, path[len(base) + 1:])
            if not (os.path.isfile(local) or os.path.isfile(os.path.join(local, "index.html"))):
                broken.append(f"{rel}: {url}")
    total_links = sum(len(p.links) for p in pages.values())
    results.append(check("Links", not broken and not uk_links,
                         f"{total_links} links and asset references in {len(pages)} pages; {len(broken)} broken internal, {len(uk_links)} to the UK site; "
                         f"external hosts outside the allow-list (CMS content, informational): {', '.join(sorted(bad_hosts)) or 'none'}",
                         sorted(set(broken))[:40] + uk_links[:10]))

    # 6. page quality
    problems = []
    for rel, p in pages.items():
        issues = []
        if not (p.title or "").strip():
            issues.append("no title")
        if not (p.desc or "").strip():
            issues.append("no meta description")
        if not p.viewport:
            issues.append("no viewport")
        if not p.robots or "noindex" not in p.robots:
            issues.append("not noindex")
        if p.lang != "en-NZ":
            issues.append("lang")
        if p.h1 != 1:
            issues.append(f"{p.h1} h1")
        if p.imgs_no_alt:
            issues.append(f"{p.imgs_no_alt} img without alt")
        dup = {i for i in p.ids if p.ids.count(i) > 1}
        if dup:
            issues.append("duplicate ids: " + ", ".join(sorted(dup)[:3]))
        if issues:
            problems.append(f"{rel}: {'; '.join(issues)}")
    results.append(check("Page quality", not problems, f"{len(pages) - len(problems)} of {len(pages)} pages pass", problems[:40]))

    # 7. budgets
    sizes = {n: os.path.getsize(os.path.join(DIST, "assets", n)) for n in ("site.css", "app.js", "catalogue.json", "content-index.json")}
    biggest = max(((os.path.getsize(os.path.join(DIST, r)), r) for r in pages))
    limits = {"site.css": 90_000, "app.js": 90_000, "catalogue.json": 700_000, "content-index.json": 200_000}
    over = [f"{n}: {sizes[n]:,} bytes > {limits[n]:,}" for n in limits if sizes[n] > limits[n]]
    if biggest[0] > 500_000:
        over.append(f"{biggest[1]}: {biggest[0]:,} bytes > 500,000")
    results.append(check("Size budgets", not over, ", ".join(f"{n} {v / 1000:.0f} kB" for n, v in sizes.items()) + f"; largest page {biggest[0] / 1000:.0f} kB ({biggest[1]})", over))

    # 8. engine tests
    quiz_json = os.path.join(ROOT, "tests", ".quiz.json")
    json.dump(C.QUIZ, open(quiz_json, "w"))
    cmd_tail = [os.path.join(ROOT, f) for f in ("tests/stub.js", "assets/app.js", "tests/engine_test.js")]
    data = [os.path.join(DIST, "assets", "catalogue.json"), quiz_json]
    if os.path.exists(JSC):
        cmd = [JSC] + cmd_tail + ["--"] + data
    elif shutil.which("node"):
        cmd = ["node", os.path.join(ROOT, "tests", "node_runner.js")] + cmd_tail + ["--"] + data
    else:
        cmd = None
    if cmd:
        out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()
        try:
            summary = json.loads(out[0])
        except (IndexError, json.JSONDecodeError):
            summary = {"failures": -1}
        fails = [l[5:] for l in out[1:] if l.startswith("FAIL ")]
        results.append(check("Quiz and comparison engines", summary.get("failures") == 0,
                             f"{summary.get('quiz_combinations', 0):,} quiz answer combinations and {summary.get('compare_tables', 0)} comparison tables tested; "
                             f"{summary.get('failures')} failures", fails[:20]))
    else:
        results.append(check("Quiz and comparison engines", False, "no JavaScript engine (jsc or node) available to run tests/engine_test.js"))

    # 9. browser self-test
    rt_path = os.path.join(ROOT, "reports", "runtime.json")
    app_hash = hashlib.sha1(open(os.path.join(DIST, "assets", "app.js"), "rb").read()).hexdigest()[:10]
    css_hash = hashlib.sha1(open(os.path.join(DIST, "assets", "site.css"), "rb").read()).hexdigest()[:10]
    if os.path.exists(rt_path):
        rt = json.load(open(rt_path))
        failed = [f"{t['id']}: {t.get('detail', '')}" for t in rt.get("tests", []) if not t.get("ok")]
        wanted = {ft["runtime"] for ft in spec if ft.get("runtime")}
        ran = {t["id"] for t in rt.get("tests", [])}
        not_run = sorted(wanted - ran)
        fresh = rt.get("app") == app_hash
        results.append(check("Browser self-test", not failed and not not_run and fresh,
                             f"{len(ran)} behaviours tested in a real browser on {rt.get('when', '?')} ({rt.get('where', '?')}); "
                             f"{len(failed)} failed; {'matches' if fresh else 'does NOT match'} the current app.js",
                             failed + [f"not tested: {n}" for n in not_run]))
    else:
        results.append(check("Browser self-test", False, "reports/runtime.json missing — run tests/selftest.js in a browser against the build"))

    # 10. deployment
    if args.no_deploy_check:
        results.append(check("Deployed to GitHub Pages", False, "skipped (--no-deploy-check)"))
    else:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "30", LIVE_URL], capture_output=True, text=True)
        live = r.stdout
        ok = f"app.js?v={app_hash}" in live and f"site.css?v={css_hash}" in live
        results.append(check("Deployed to GitHub Pages", ok,
                             f"{LIVE_URL} {'serves' if ok else 'does not serve'} the current build (app.js {app_hash}, site.css {css_hash})"))

    # snapshot freshness (informational)
    snap_age = (time.time() - os.path.getmtime(os.path.join(ROOT, ".cache", "nz", "products.json"))) / 86400

    # report
    passed = sum(r["ok"] for r in results)
    complete = passed == len(results)
    lines = ["# Remake report: micro-scooters.co.uk → micro-nz/micro-uk", "",
             f"Generated {time.strftime('%d %B %Y, %H:%M %Z')} by `tools/audit.py` from build of {manifest['built']}.", "",
             "The remake rebuilds the UK site's design, structure and features as original code, filled with Micro NZ's catalogue "
             "and content (loaded from the NZ store's Storefront API). Checkout happens on microscooters.co.nz.", "",
             f"NZ data snapshot is {snap_age:.1f} days old.", "",
             "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, r in enumerate(results, 1):
        lines.append(f"| {i} | {r['name']} | {'PASS' if r['ok'] else 'FAIL'} | {r['detail'].replace('|', '/')} |")
    for r in results:
        if r["items"]:
            lines += ["", f"## {r['name']}: {'notes' if r['ok'] else 'failures'}", ""] + [f"- {x}" for x in r["items"]]
    lines += ["", "## UK features covered", "", "| ID | Area | Feature | Runtime test |", "|---|---|---|---|"]
    lines += [f"| {f['id']} | {f['area']} | {f['name']} | {f.get('runtime', '—')} |" for f in spec]
    lines += ["", "## Deliberate differences from the UK site", "",
              "- Products, prices, copy and images are Micro NZ's, in NZD; the UK's own text and photography are not copied.",
              "- Pay-later box shows Afterpay (NZ) where the UK shows Klarna; reviews come from the NZ store's Okendo account.",
              "- Spec rows the NZ listings don't state show \"Not listed\" rather than guessed values.",
              "- A prototype banner and noindex tag are added so the remake can't be mistaken for, or outrank, a live store.", "",
              f"**{passed} of {len(results)} checks pass.**", "",
              "REMAKE COMPLETE" if complete else f"REMAKE INCOMPLETE — {len(results) - passed} check(s) failing"]
    open(args.out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[-1:]))
    for r in results:
        print(f"  {'PASS' if r['ok'] else 'FAIL'}  {r['name']}: {r['detail']}")
        for x in r["items"][:5]:
            print(f"        - {x}")
    sys.exit(0 if complete else 1)


if __name__ == "__main__":
    main()
