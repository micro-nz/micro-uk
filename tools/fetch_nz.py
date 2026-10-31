#!/usr/bin/env python3
"""Snapshot the Micro NZ catalogue and content from Shopify's Storefront API.

Writes .cache/nz/{products,collections,pages,articles,shop}.json. Uses curl for
HTTPS (the python.org build on Jeremy's Mac has no CA bundle). Stdlib only.
"""
import json, os, subprocess, sys, time

STORE = os.environ.get("NZ_STORE", "https://www.microscooters.co.nz")
API = f"{STORE}/api/2026-01/graphql.json"
TOKEN = os.environ.get("NZ_STOREFRONT_TOKEN", "")  # optional; tokenless works for these queries
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cache", "nz")


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}})
    cmd = ["curl", "-sS", "--max-time", "60", "-X", "POST", API,
           "-H", "Content-Type: application/json", "--data-binary", "@-"]
    if TOKEN:
        cmd += ["-H", f"X-Shopify-Storefront-Access-Token: {TOKEN}"]
    for attempt in range(5):
        r = subprocess.run(cmd, input=body, capture_output=True, text=True)
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            time.sleep(5 * (attempt + 1)); continue
        errs = data.get("errors")
        if errs and any("THROTTLED" in json.dumps(e) for e in errs):
            time.sleep(5 * (attempt + 1)); continue
        if errs:
            sys.exit(f"GraphQL error: {json.dumps(errs)[:500]}")
        time.sleep(0.4)
        return data["data"]
    sys.exit("Storefront API kept failing")


def paged(field, fragment, first=25, extra_args=""):
    q = f"""query($after: String) {{ {field}(first: {first}, after: $after{extra_args}) {{
        pageInfo {{ hasNextPage endCursor }} nodes {{ {fragment} }} }} }}"""
    out, after = [], None
    while True:
        d = gql(q, {"after": after})[field]
        out += d["nodes"]
        print(f"  {field}: {len(out)}", file=sys.stderr)
        if not d["pageInfo"]["hasNextPage"]:
            return out
        after = d["pageInfo"]["endCursor"]


PRODUCT = """id handle title vendor productType tags createdAt updatedAt publishedAt
  descriptionHtml description availableForSale
  seo { title description }
  options { name optionValues { name swatch { color image { previewImage { url } } } } }
  priceRange { minVariantPrice { amount currencyCode } maxVariantPrice { amount } }
  compareAtPriceRange { maxVariantPrice { amount } }
  featuredImage { url altText width height }
  images(first: 20) { nodes { url altText width height } }
  variants(first: 60) { nodes { id title sku availableForSale
    price { amount } compareAtPrice { amount }
    selectedOptions { name value } image { url altText width height } } }
  collections(first: 20) { nodes { handle } }"""

COLLECTION = """id handle title description descriptionHtml updatedAt
  seo { title description } image { url altText width height }"""

PAGE = """id handle title body bodySummary createdAt updatedAt seo { title description }"""

ARTICLE = """id handle title publishedAt excerpt contentHtml tags
  authorV2 { name } image { url altText width height } blog { handle title }
  seo { title description }"""


def main():
    os.makedirs(OUT, exist_ok=True)
    shop = gql("""{ shop { name description primaryDomain { url }
        paymentSettings { currencyCode countryCode acceptedCardBrands }
        shippingPolicy { title handle body } refundPolicy { title handle body }
        privacyPolicy { title handle body } termsOfService { title handle body } } }""")["shop"]
    products = paged("products", PRODUCT, first=20)
    collections = paged("collections", COLLECTION, first=50)
    # collection membership, in the store's own sort order
    for c in collections:
        handles, after = [], None
        while True:
            d = gql("""query($h: String!, $after: String) { collection(handle: $h) {
                products(first: 250, after: $after) { pageInfo { hasNextPage endCursor } nodes { handle } } } }""",
                    {"h": c["handle"], "after": after})["collection"]["products"]
            handles += [n["handle"] for n in d["nodes"]]
            if not d["pageInfo"]["hasNextPage"]:
                break
            after = d["pageInfo"]["endCursor"]
        c["products"] = handles
    pages = paged("pages", PAGE, first=50)
    articles = paged("articles", ARTICLE, first=50)
    shop["blogs"] = paged("blogs", "handle title seo { title description }", first=50)
    for name, data in [("shop", shop), ("products", products), ("collections", collections),
                       ("pages", pages), ("articles", articles)]:
        with open(os.path.join(OUT, f"{name}.json"), "w") as f:
            json.dump(data, f, indent=1)
    print(f"products {len(products)}, collections {len(collections)}, pages {len(pages)}, "
          f"articles {len(articles)}", file=sys.stderr)


if __name__ == "__main__":
    main()
