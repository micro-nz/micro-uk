"""Load the NZ Storefront snapshot and derive what the UK-style templates need."""
import json, os, re
from . import config

HIDDEN_TAGS = {"Admin Only"}
HIDDEN_TYPES = ("8 Miscellaneous",)
FEATURE_TAGS = {  # NZ tag -> (code, label) used for filters and feature pills
    "LED Wheels": ("led", "Light-up wheels"),
    "Foldable": ("foldable", "Foldable"),
    "Lightweight": ("lightweight", "Lightweight"),
    "Large Wheels": ("large-wheels", "Large wheels"),
    "Suspension": ("suspension", "Suspension"),
    "Personalised": ("personalised", "Personalised"),
    "Eco Material": ("eco", "Eco material"),
}
AGE_TAGS = {"Scooters : Preschoolers": "toddler", "Ride-on": "toddler", "Scooters : Kids": "kids",
            "Scooters : Adults": "adult", "Scooters : Freestyle": "adult"}
AGE_LABELS = {"toddler": "Toddlers & preschool", "kids": "Kids", "adult": "Teens & adults"}
CATEGORY_BY_TYPE = [("1 Scooters", "scooters"), ("3 Ride-Ons", "ride-ons"), ("4 Luggage", "luggage"),
                    ("5 Helmets", "helmets"), ("6 Accessories", "accessories"), ("7 Parts", "parts")]
PART_TYPES = [  # (code, label, title keywords) — first match wins, so order matters
    ("wheels", "Wheels & bearings", ["wheel", "bearing", "axle", "tyre", "tire"]),
    ("deck", "Decks & grip tape", ["grip tape", "griptape", "deck", "footplate", "board"]),
    ("grips", "Grips & handlebars", ["grip", "handlebar", "handle bar", "t-bar", "tbar", "bar end", "bar-end", "handle", "one piece bar", "one peice bar", "bar"]),
    ("brakes", "Brakes & mudguards", ["brake", "fender", "mudguard"]),
    ("folding", "Folding & clamps", ["fold", "clamp", "lever", "lock", "latch", "trigger", "push-button", "push button", "button", "block"]),
    ("steering", "Steering & frame", ["stem", "steering", "fork", "tube", "column", "headset", "joystick", "lean", "holder", "shank", "head", "frame", "bend", "linkage", "suspension"]),
    ("helmet", "Helmet parts", ["helmet", "padding", "visor", "buckle", "strap"]),
    ("seats", "Seats & ride-on parts", ["seat", "saddle", "rocker", "base", "hopper", "pump"]),
    ("fixings", "Screws & fixings", ["screw", "bolt", "nut", "washer", "spring", "pin", "spacer", "bush", "rivet", "cap", "plug", "clip"]),
]
QUIZ_COLLECTIONS = {"toddler-preschool-scooters", "kids-scooters", "adult-scooters", "scooter-for-teenager", "freestyle-scooters",
                    "micro-ride-on-range", "balance-bikes", "micro-trike-collection", "luggage", "bestselling-scooters",
                    "personalised-scooters", "led-range", "all-scooters"}
PRICE_BANDS = [("0-50", "Under $50", 0, 50), ("50-100", "$50 to $100", 50, 100), ("100-200", "$100 to $200", 100, 200),
               ("200-300", "$200 to $300", 200, 300), ("300+", "$300 and over", 300, 10 ** 9)]


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def fix_text(t):
    """Repair double-encoded UTF-8 in NZ titles (e.g. "180Ã‚Â°" -> "180°")."""
    for _ in range(3):
        if "Ã" not in t and "Â" not in t:
            break
        try:
            t = t.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
    return t.replace("Â", "")


def numeric_id(gid):
    return gid.rsplit("/", 1)[-1] if gid else ""


class Store:
    def __init__(self, cache_dir):
        load = lambda n: json.load(open(os.path.join(cache_dir, f"{n}.json")))
        self.shop = load("shop")
        self.products = load("products")
        self.collections = load("collections")
        self.pages = load("pages")
        self.articles = load("articles")
        self.blogs = self.shop.get("blogs", [])
        self.product_by_handle = {p["handle"]: p for p in self.products}
        self.collection_by_handle = {c["handle"]: c for c in self.collections}
        self.page_by_handle = {p["handle"]: p for p in self.pages}
        self.articles.sort(key=lambda a: a.get("publishedAt") or "", reverse=True)
        best = set(self.collection_by_handle.get("bestselling-scooters", {}).get("products", []))
        new = set(self.collection_by_handle.get("new-in-store", {}).get("products", []))
        for p in self.products:
            p["title"] = fix_text(p["title"])
            self._derive(p, best, new)
        self.spare_collections = [c for c in self.collections if "spare" in c["handle"] or c["handle"].endswith("-parts")]
        for p in self.products:
            p["_spares"] = self._spares_for(p)
            p["_specs"] = self._specs(p)
            p["_cols"] = [c["handle"] for c in p["collections"]["nodes"] if c["handle"] in QUIZ_COLLECTIONS]

    # ---- products -------------------------------------------------------
    def _derive(self, p, best, new):
        tags = set(p["tags"])
        variants = p["variants"]["nodes"]
        price = _f(p["priceRange"]["minVariantPrice"]["amount"])
        compare = max([_f((v.get("compareAtPrice") or {}).get("amount")) for v in variants] + [0])
        p["_price"] = price
        p["_compare"] = compare if compare > price else 0
        p["_hidden"] = bool(tags & HIDDEN_TAGS) or p["productType"].startswith(HIDDEN_TYPES)
        p["_category"] = next((c for t, c in CATEGORY_BY_TYPE if p["productType"].startswith(t)), "other")
        p["_features"] = [FEATURE_TAGS[t] for t in p["tags"] if t in FEATURE_TAGS]
        p["_wheels"] = "3" if "3-Wheel Scooter" in tags else "2" if "2-Wheel Scooter" in tags else ""
        age = next((AGE_TAGS[t] for t in p["tags"] if t in AGE_TAGS), "")
        if not age and p["_category"] == "scooters":
            age = "toddler" if ": 1 Mini" in p["productType"] else "adult" if (": 6 Adult" in p["productType"] or ": 5 Freestyle" in p["productType"]) else "kids"
        p["_age"] = age
        title = p["title"].lower()
        p["_part"] = ""
        if p["_category"] == "parts":
            p["_part"] = next((code for code, _, kws in PART_TYPES if any(k in title for k in kws)), "other")
        badge = ""
        if not p["availableForSale"]:
            badge = "Sold out"
        elif p["_compare"]:
            badge = "Offer"
        elif p["handle"] in new or "New" in tags:
            badge = "New"
        elif p["handle"] in best or "Best selling scooter" in tags:
            badge = "Best seller"
        elif "Personalised" in tags:
            badge = "Personalise me"
        p["_badge"] = badge
        imgs = p["images"]["nodes"] or ([p["featuredImage"]] if p.get("featuredImage") else [])
        p["_images"] = imgs
        p["_colour_option"] = next((o["name"] for o in p["options"] if o["name"].lower() == "colour"), None)
        sw, seen = [], set()
        if p["_colour_option"]:
            for v in variants:
                val = next((o["value"] for o in v["selectedOptions"] if o["name"] == p["_colour_option"]), None)
                if val and val not in seen:
                    seen.add(val)
                    sw.append({"name": val, "img": (v.get("image") or {}).get("url", ""), "variant": numeric_id(v["id"])})
        p["_swatches"] = sw

    def _specs(self, p):
        """Facts for the comparison table and key specs, from tags, title and description. None = not listed."""
        title = p["title"].lower()
        tags = set(p["tags"])
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", p.get("descriptionHtml") or "")).replace("–", "-").replace("—", "-")
        low = text.lower()
        s = {}
        if p["_wheels"]:
            s["wheels"] = p["_wheels"] + " wheels"
        elif re.search(r"\b3[ -]wheel|mini micro|maxi micro|kickboard|mini2go|mini2grow|rock & go", title):
            s["wheels"] = "3 wheels"
        elif re.search(r"\b2[ -]wheel|sprite|cruiser|speed|classic|rocket|suspension|suburb|stunt|ramp|downtown|flex", title):
            s["wheels"] = "2 wheels"
        elif "balance bike" in title:
            s["wheels"] = "Balance bike"
        elif "tricycle" in title or "trike" in title:
            s["wheels"] = "Tricycle"
        if re.search(r"ride[ -]?on|mini2go|mini2grow|rock & go|tricycle|7-in-1", title):
            s["rideon"] = True
        m = re.search(r"\bages?\s*(?:from\s*)?(\d{1,2})\s*(?:\+|-|to)\s*(\d{1,2}|adults?|teens?)\b", low) or \
            re.search(r"\b(\d{1,2})\s*-\s*(\d{1,2})\s*(?:years|yrs)\b", low)
        if m:
            lo, hi = m.group(1), m.group(2)
            hi = "adult" if hi.startswith("adult") else "teens" if hi.startswith("teen") else hi
            s["ages"] = f"{lo} to {hi}" + (" years" if hi.isdigit() else "")
        m = re.search(r"(?:weight limit(?: is tested to| of)?|weight of up to|max(?:imum)?\.? (?:rider |user )?(?:load|weight)(?: of)?)\D{0,12}(\d{2,3})\s*kg", low)
        if m:
            s["max_weight"] = f"{m.group(1)} kg"
        m = re.search(r"(?<!rider )(?<!user )(?<!max )(?<!load )\bweight\s*:?\s*(\d(?:\.\d{1,2})?)\s*kg", low)
        if m:
            s["weight"] = f"{m.group(1)} kg"
        m = re.search(r"wheel size\s*(\d{2,3})\s*mm", low) or re.search(r"(\d{2,3})\s*mm\s*(?:pu\s*)?wheels", low) or re.search(r"wheels[^.]{0,20}?(\d{2,3})\s*mm", low)
        if m:
            s["wheel_mm"] = f"{m.group(1)} mm"
        m = re.search(r"handlebar height\s*(\d{2,3}\s*-\s*\d{2,3}|\d{2,3})\s*cm", low)
        if m:
            s["handlebar"] = m.group(1).replace(" ", "").replace("-", " to ") + " cm"
        m = re.search(r"\bfoldable\s*:?\s*(yes|no)\b", low)
        if m:
            s["folds"] = m.group(1) == "yes"
        elif "Foldable" in tags or "foldable" in title:
            s["folds"] = True
        elif re.search(r"non[- ]fold|does not fold|doesn't fold|not foldable", low):
            s["folds"] = False
        elif re.search(r"\b(?:easy[- ]?)?fold(?:s|ing|able)?\b", low):
            s["folds"] = True
        s["led"] = bool("LED Wheels" in tags or re.search(r"\bled\b|light[- ]up|glow", title))
        s["lightweight"] = "Lightweight" in tags
        mm = int(s["wheel_mm"].split()[0]) if "wheel_mm" in s else 0
        s["large_wheels"] = "Large Wheels" in tags or mm >= 180
        s["suspension"] = "Suspension" in tags or "suspension" in title
        s["personalised"] = "Personalised" in tags or "personalis" in title
        s["eco"] = "Eco Material" in tags or re.search(r"\beco\b", title) is not None
        return s

    def _spares_for(self, p):
        if p["_category"] not in ("scooters", "ride-ons", "luggage", "helmets"):
            return None
        title = re.sub(r"[^a-z0-9+ ]", " ", p["title"].lower())
        words = set(title.split())
        best, best_len = None, 0
        for c in self.spare_collections:
            if not c["products"]:
                continue
            key = re.sub(r"\b(spare|spares|parts?|scooter|scoooter|online|micro|kids|and)\b", " ", c["title"].lower())
            key = re.sub(r"[^a-z0-9+ ]", " ", key).split()
            if key and all(k in words for k in key) and len(" ".join(key)) > best_len:
                best, best_len = c["handle"], len(" ".join(key))
        return best

    def visible_products(self, handles=None):
        src = [self.product_by_handle[h] for h in handles if h in self.product_by_handle] if handles is not None else self.products
        return [p for p in src if not p["_hidden"]]

    def collection_products(self, handle):
        c = self.collection_by_handle.get(handle)
        return self.visible_products(c["products"]) if c else []

    def primary_collection(self, p):
        """The most specific browse collection a product belongs to, for breadcrumbs."""
        prefer = ["mini-micro-deluxe-scooters", "micro-sprite-range", "micro-cruiser-scooters", "maxi-micro-deluxe-scooter-range",
                  "micro-ride-on-range", "freestyle-scooters", "balance-bikes", "luggage", "toddler-preschool-scooters", "kids-scooters",
                  "adult-scooters", "all-helmets-safety-gear", "kids-scooter-accessories", "adult-scooter-accessories"]
        mine = [c["handle"] for c in p["collections"]["nodes"]]
        for h in prefer:
            if h in mine:
                return self.collection_by_handle[h]
        if p["_spares"] is None:
            for h in mine:
                c = self.collection_by_handle.get(h)
                if c and ("spare" in h or h.endswith("-parts")):
                    return c
        return None

    def compact(self, p):
        """Small record used by client-side filtering, search and the quiz."""
        imgs = p["_images"]
        return {
            "h": p["handle"], "t": p["title"], "p": p["_price"], "c": p["_compare"],
            "i": imgs[0]["url"] if imgs else "", "i2": imgs[1]["url"] if len(imgs) > 1 else "",
            "a": 1 if p["availableForSale"] else 0, "b": p["_badge"], "cat": p["_category"], "age": p["_age"],
            "w": p["_wheels"], "f": [code for code, _ in p["_features"]], "pt": p["_part"],
            "sw": [[s["name"], s["img"]] for s in p["_swatches"]][:8], "id": numeric_id(p["id"]),
            "d": (p.get("publishedAt") or "")[:10], "v": numeric_id(p["variants"]["nodes"][0]["id"]) if p["variants"]["nodes"] else "",
            "multi": 1 if len(p["variants"]["nodes"]) > 1 else 0,
            "s": p["_specs"] if p["_category"] in ("scooters", "ride-ons", "luggage") or p["_cols"] else None,
            "col": p["_cols"],
            "vg": p["variants"]["nodes"][0]["id"] if p["variants"]["nodes"] else "",
        }
