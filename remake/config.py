"""Site configuration: the UK site's structure, filled with Micro NZ links and copy.

Every link here is a site path ("/collections/x") that the build checks exists,
or an absolute URL. Copy is written for this remake; NZ store facts (free
shipping threshold, warranty, contact details) come from microscooters.co.nz.
"""

STORE_URL = "https://www.microscooters.co.nz"
STORE_NAME = "Micro Scooters NZ"
API_VERSION = "2026-01"
OKENDO_STORE = "c51de6f4-858a-4bb6-a2ab-9678248a3b2c"
LOGO = "https://www.microscooters.co.nz/cdn/shop/files/micro-scooters-nz.png"
FREE_SHIPPING_FROM = 100  # NZD
CURRENCY_SYMBOL = "$"

ANNOUNCEMENTS = [
    ("Free shipping on orders over $100", "/pages/delivery"),
    ("Price match promise — we'll match it", "/pages/price-match-promise"),
    ("2 year warranty & every spare part in stock", "/pages/warranty"),
]

USPS = [
    ("truck", "Free shipping", "On NZ orders over $100", "/pages/delivery"),
    ("tag", "Price match promise", "Seen it cheaper? We'll match it", "/pages/price-match-promise"),
    ("shield", "2 year warranty", "As standard on every scooter", "/pages/warranty"),
    ("wrench", "Spare parts for life", "Repair it, don't replace it", "/pages/spares-and-repairs"),
]

# Shop mega menu, in the UK site's order. Each tab: (label, link, columns, promos).
# A column is (heading, link, [(label, link), ...]).
MEGA_MENU = [
    ("Scooters", "/collections/all-scooters", [
        ("12 months +", "/collections/toddler-preschool-scooters", [
            ("View all", "/collections/toddler-preschool-scooters"),
            ("3 wheeled Mini scooters", "/collections/mini-micro-deluxe-scooters"),
            ("Ride-on scooters", "/collections/micro-ride-on-range"),
            ("Balance bikes", "/collections/balance-bikes"),
            ("Tricycles", "/collections/micro-trike-collection"),
            ("Eco scooters", "/collections/eco-friendly-kids-scooters"),
        ]),
        ("5 years +", "/collections/kids-scooters", [
            ("View all", "/collections/kids-scooters"),
            ("3 wheeled Maxi scooters", "/collections/maxi-micro-deluxe-scooter-range"),
            ("2 wheeled Cruiser scooters", "/collections/micro-cruiser-scooters"),
            ("2 wheeled Sprite scooters", "/collections/micro-sprite-range"),
            ("Light-up LED scooters", "/collections/led-range"),
            ("Personalised scooters", "/collections/personalised-scooters"),
        ]),
        ("8 years + & adult", "/collections/adult-scooters", [
            ("View all", "/collections/adult-scooters"),
            ("Teen scooters", "/collections/scooter-for-teenager"),
            ("Adult scooters", "/collections/adult-scooters"),
            ("Stunt scooters", "/collections/freestyle-scooters"),
            ("Luggage scooters", "/collections/luggage"),
        ]),
    ], "scooters"),
    ("Accessories", "/collections/kids-scooter-accessories", [
        ("Shop by product", "/collections/kids-scooter-accessories", [
            ("View all", "/collections/kids-scooter-accessories"),
            ("Helmets & safety gear", "/collections/all-helmets-safety-gear"),
            ("Adult accessories", "/collections/adult-scooter-accessories"),
            ("Luggage", "/collections/luggage"),
        ]),
        ("Style your ride", "/collections/neochrome-range", [
            ("Neochrome range", "/collections/neochrome-range"),
            ("Glow-in-the-dark", "/collections/glow-in-the-dark-scooters"),
            ("June Noir collection", "/collections/june-noir-collection"),
            ("Personalised", "/collections/personalised-scooters"),
        ]),
    ], "accessories"),
    ("Helmets", "/collections/all-helmets-safety-gear", [
        ("Helmets", "/collections/all-helmets-safety-gear", [
            ("View all", "/collections/all-helmets-safety-gear"),
            ("Kids helmets", "/collections/all-kids-helmets"),
            ("Helmet spare parts", "/collections/micro-helmets-spare-parts"),
            ("Helmet size guide", "/pages/micro-bike-helmet-size-specs"),
        ]),
    ], "helmets"),
    ("Spares & repairs", "/pages/spares-and-repairs", [
        ("Spares & repairs", "/pages/spares-and-repairs", [
            ("Find my spare part", "/pages/spares-finder"),
            ("Repair guides", "/blogs/how-tos"),
            ("Scooter repairs", "/pages/scooter-repairs"),
            ("Scooter maintenance", "/pages/scooter-maintenance"),
            ("Warranty", "/pages/warranty"),
        ]),
    ], "spares"),
    ("Balance bikes", "/collections/balance-bikes", [], None),
    ("Best sellers", "/collections/bestselling-scooters", [], None),
    ("Featured", "/collections/new-in-store", [
        ("Featured", "/collections/new-in-store", [
            ("Which scooter is right for you?", "/pages/your-best-micro-scooter"),
            ("Latest releases", "/collections/new-in-store"),
            ("Best sellers", "/collections/bestselling-scooters"),
            ("Neochrome range", "/collections/neochrome-range"),
            ("Personalised scooters", "/collections/personalised-scooters"),
            ("Eco scooters", "/collections/eco-friendly-kids-scooters"),
        ]),
    ], "featured"),
]

# Promo tiles shown beside a mega menu tab: (eyebrow, cta, link, collection handle for the image)
MEGA_PROMOS = {
    "scooters": [("Find their perfect scooter in minutes", "Start the quiz", "/pages/your-best-micro-scooter", "kids-scooters"),
                 ("Make it theirs", "Shop personalised", "/collections/personalised-scooters", "personalised-scooters")],
    "accessories": [("Match their helmet to their scooter", "Shop helmets", "/collections/all-helmets-safety-gear", "all-helmets-safety-gear"),
                    ("Neochrome: the colour-shift finish", "Shop the range", "/collections/neochrome-range", "neochrome-range")],
    "helmets": [("Designs everyone will love", "Shop helmets", "/collections/all-helmets-safety-gear", "all-helmets-safety-gear")],
    "spares": [("Repair, revamp or refurbish", "Find a part", "/pages/spares-finder", "micro-sprite-scooter-spare-parts")],
    "featured": [("Find their perfect scooter in minutes", "Start the quiz", "/pages/your-best-micro-scooter", "bestselling-scooters"),
                 ("Our newest arrivals", "Shop new in", "/collections/new-in-store", "new-in-store")],
}

HELP_MENU = [
    ("Before purchase", [
        ("FAQs", "/pages/scooter-faq-help-desk"),
        ("Contact us", "/pages/contact"),
        ("Scooter buying guides", "/blogs/buying-guides"),
        ("Which scooter is right for you?", "/pages/your-best-micro-scooter"),
        ("Shipping & delivery", "/pages/delivery"),
        ("Price match promise", "/pages/price-match-promise"),
        ("Payment options", "/pages/payment"),
        ("Afterpay", "/pages/pay-with-afterpay"),
        ("Find a stockist", "/pages/stockists"),
    ]),
    ("After purchase", [
        ("Returns & refunds", "/pages/returns-refunds"),
        ("Spares & repairs", "/pages/spares-and-repairs"),
        ("Repair guides", "/blogs/how-tos"),
        ("Scooter repairs", "/pages/scooter-repairs"),
        ("Warranty information", "/pages/warranty"),
        ("Scooter maintenance", "/pages/scooter-maintenance"),
        ("How to scoot safely", "/pages/scooter-safety"),
        ("Order changes", "/pages/order-change-policy"),
    ]),
]

ABOUT_MENU = [
    ("About Micro", [
        ("About us", "/pages/about-us"),
        ("Our Micro story", "/pages/micro-scooters-story"),
        ("Why choose Micro?", "/pages/why-choose-a-micro-scooter"),
        ("Swiss design", "/pages/swiss-design"),
        ("Innovation", "/pages/innovation"),
        ("Quality", "/pages/scooter-quality"),
        ("Awards", "/pages/awards"),
        ("Meet the team", "/pages/meet-the-team"),
        ("Explore our blog", "/blogs"),
    ]),
    ("Micro initiatives", [
        ("Recycled plastic scooters", "/pages/eco-recycled-plastic-range"),
        ("Scooter safety programme", "/pages/scooter-safety-program"),
        ("Scoot the commute", "/pages/scoot-to-work"),
        ("Corporate fleets", "/pages/office-scooting"),
        ("Fundraising", "/pages/fundraising"),
        ("Micro ambassadors", "/pages/micro-ambassador-program"),
        ("Become a retail partner", "/pages/become-a-retailer-partner"),
        ("Microlino", "/pages/microlino"),
    ]),
]

FOOTER_PILLARS = [
    ("Planet friendly", "Fewer car trips, longer-lasting products and recycled-plastic models."),
    ("Quality obsessed", "Swiss-designed, made from aluminium and stainless steel."),
    ("Scooting pioneers", "The people who started the kick-scooter, still innovating."),
    ("Built to last", "Every part replaceable, so scooters get passed on, not thrown out."),
]

FOOTER_COLUMNS = [
    ("Company", [
        ("About Micro Scooters", "/pages/about-us"),
        ("Why choose Micro?", "/pages/why-choose-a-micro-scooter"),
        ("Awards", "/pages/awards"),
        ("Reviews", "/pages/reviews"),
        ("Ambassador programme", "/pages/micro-ambassador-program"),
        ("Become a retail partner", "/pages/become-a-retailer-partner"),
        ("Corporate fleets", "/pages/office-scooting"),
        ("Microlino", "/pages/microlino"),
    ]),
    ("Support", [
        ("FAQs", "/pages/scooter-faq-help-desk"),
        ("Shipping & delivery", "/pages/delivery"),
        ("Returns & refunds", "/pages/returns-refunds"),
        ("Spares & repairs", "/pages/spares-finder"),
        ("Warranty", "/pages/warranty"),
        ("Find a stockist", "/pages/stockists"),
        ("Contact us", "/pages/contact"),
        ("Retailer login", "https://order.microscooters.co.nz/"),
    ]),
]

SOCIALS = [
    ("instagram", "https://www.instagram.com/micro_scooters/"),
    ("facebook", "https://www.facebook.com/micro.au.nz"),
    ("youtube", "https://www.youtube.com/channel/UCkrsmMczjS3VHRZvgnwFuZg"),
]

CONTACT = {"phone": "04 384 2300", "address": "171 Vivian Street, Te Aro, Wellington 6011", "page": "/pages/contact"}

LEGAL = [("Terms of service", "/policies/terms-of-service"), ("Privacy policy", "/policies/privacy-policy"),
         ("Shipping policy", "/policies/shipping-policy"), ("Refund policy", "/policies/refund-policy")]

# Homepage, in the UK homepage's section order.
HOME = {
    "hero": {
        "image": "https://www.microscooters.co.nz/cdn/shop/files/girls-riding-pink-and-purple-retro-kids-scooters.jpg",
        "title": "Scooters built to be handed down",
        "text": "Swiss-designed scooters for every age, with every spare part in stock in Wellington.",
        "ctas": [("Find their scooter", "/pages/your-best-micro-scooter"), ("Shop accessories", "/collections/kids-scooter-accessories")],
    },
    "age_cards": [
        ("Scooters, ride-ons & balance bikes", "For 12 months +", "/collections/toddler-preschool-scooters", "toddler-preschool-scooters", "navy"),
        ("3 & 2 wheeled scooters", "For 5 years +", "/collections/kids-scooters", "kids-scooters", "green"),
        ("2 wheeled scooters", "For teens & adults", "/collections/adult-scooters", "adult-scooters", "purple"),
        ("Helmets & safety gear", "For all ages", "/collections/all-helmets-safety-gear", "all-helmets-safety-gear", "teal"),
    ],
    "adviser": {"eyebrow": "Scooter adviser", "title": "Not sure which scooter?",
                "text": "Answer five quick questions and we'll match them to the right Micro.",
                "cta": ("Find your perfect scooter", "/pages/your-best-micro-scooter"), "collection": "bestselling-scooters"},
    "carousel_1": {"title": "Don't forget your…", "tabs": [
        ("Helmets", "all-helmets-safety-gear"), ("Accessories", "kids-scooter-accessories"),
        ("Adult accessories", "adult-scooter-accessories"), ("Luggage", "luggage")]},
    "personalise": {"eyebrow": "Personalised scooters", "title": "Add their name, make it theirs",
                    "text": "A personalised Micro is easy to spot at the school gate and hard to lose.",
                    "cta": ("Shop personalised", "/collections/personalised-scooters"), "collection": "personalised-scooters"},
    "carousel_2": {"title": "Most loved right now", "tabs": [
        ("Best sellers", "bestselling-scooters"), ("Latest releases", "new-in-store"),
        ("Light-up LED", "led-range"), ("Neochrome", "neochrome-range")]},
    "featured_pages": {"title": "From cool to cute, there's a look for every scoot", "tiles": [
        ("Neochrome", "/collections/neochrome-range", "neochrome-range"),
        ("June Noir", "/collections/june-noir-collection", "june-noir-collection"),
        ("Ride-ons", "/collections/micro-ride-on-range", "micro-ride-on-range"),
        ("Stunt", "/collections/freestyle-scooters", "freestyle-scooters")]},
    "quick_links": {"title": "Micro was made to make everyday journeys better — for families, and for the planet.", "links": [
        ("Our Micro story", "/pages/micro-scooters-story"), ("Swiss design", "/pages/swiss-design"),
        ("Quality", "/pages/scooter-quality"), ("Recycled plastic range", "/pages/eco-recycled-plastic-range"),
        ("Awards", "/pages/awards"), ("Scooter safety programme", "/pages/scooter-safety-program")],
        "collection": "eco-friendly-kids-scooters"},
    "ambassadors": {"title": "Become a Micro Ambassador", "text": "Love your Micro? Share it, earn rewards and get first look at new releases.",
                    "cta": ("Find out more", "/pages/micro-ambassador-program"),
                    "cards": [("Share your rides", "kids-scooters"), ("Earn rewards", "personalised-scooters"), ("First look at launches", "new-in-store")]},
    "text_grid": [
        ("Designed in Switzerland", "Trusted across New Zealand for more than 18 years and sold in over 80 countries."),
        ("Built to last", "Premium aluminium and stainless steel, made for years of scooting."),
        ("Every spare part", "We keep parts for current and past models, so a Micro can be repaired, not replaced."),
        ("Safety first", "Helmets, lights and bells designed to match, plus our scooter safety programme."),
    ],
    "seo": ("The best scooters for kids and adults",
            "Choose from three-wheeled scooters for toddlers, two-wheeled scooters for kids, and adult scooters for the commute. "
            "Every Micro is designed in Switzerland, built to last and backed by a two-year warranty and a full range of spare parts."),
}

# Scooter-finder quiz (UK: /pages/your-best-micro-scooter). Options marked by age are only shown for that age.
QUIZ = {
    "pools": {  # which NZ collections count as suitable for each rider
        "toddler": ["toddler-preschool-scooters", "micro-ride-on-range", "balance-bikes", "micro-trike-collection"],
        "kids": ["kids-scooters"],
        "teen": ["scooter-for-teenager", "freestyle-scooters"],
        "adult": ["adult-scooters"],
    },
    "steps": [
        {"id": "age", "q": "Who is the scooter for?", "options": [
            {"v": "toddler", "l": "A toddler or preschooler", "d": "Around 1 to 5 years"},
            {"v": "kids", "l": "A child", "d": "Around 5 to 12 years"},
            {"v": "teen", "l": "A teenager", "d": "Confident riders, 12 and up"},
            {"v": "adult", "l": "An adult", "d": "Commuting, fitness or fun"}]},
        {"id": "style", "q": "Which style suits them best?", "options": [
            {"v": "rideon", "l": "Sit-on ride-on", "d": "For little ones not yet scooting standing up", "ages": ["toddler"]},
            {"v": "3", "l": "Three wheels", "d": "Stable, easy to learn, lean-to-steer", "ages": ["toddler", "kids", "teen", "adult"]},
            {"v": "2", "l": "Two wheels", "d": "Faster and more agile, for confident riders", "ages": ["kids", "teen", "adult"]},
            {"v": "bike", "l": "Balance bike or tricycle", "d": "Builds bike skills, no pedals needed", "ages": ["toddler"]},
            {"v": "stunt", "l": "Stunt scooter", "d": "Built for the skatepark", "ages": ["kids", "teen", "adult"]},
            {"v": "any", "l": "Not sure", "d": "Show me the best options", "ages": ["toddler", "kids", "teen", "adult"]}]},
        {"id": "f", "q": "What matters most?", "multi": 2, "hint": "Pick up to two, or skip.", "options": [
            {"v": "led", "l": "Light-up wheels", "d": "Motion-powered LEDs, no batteries"},
            {"v": "foldable", "l": "Folds for carrying", "d": "Easy to store and take on outings"},
            {"v": "lightweight", "l": "Lightweight", "d": "Easy for small hands to carry"},
            {"v": "large", "l": "Big wheels", "d": "Smoother over footpaths and bumps"},
            {"v": "suspension", "l": "Suspension", "d": "Extra comfort on longer rides"},
            {"v": "personalised", "l": "Personalised", "d": "Add their name to the deck"}]},
        {"id": "use", "q": "Where will they ride most?", "options": [
            {"v": "home", "l": "Around home and the park", "d": "Everyday fun close to home", "ages": ["toddler", "kids"]},
            {"v": "school", "l": "The school or kindy run", "d": "Quick to fold at the gate", "ages": ["toddler", "kids", "teen"]},
            {"v": "travel", "l": "Travel and day trips", "d": "Compact and easy to pack", "ages": ["toddler", "kids", "adult"]},
            {"v": "commute", "l": "Commuting", "d": "Longer distances, smooth and fast", "ages": ["teen", "adult"]},
            {"v": "park", "l": "The skatepark", "d": "Tricks, ramps and jumps", "ages": ["kids", "teen", "adult"]}]},
        {"id": "budget", "q": "What's your budget?", "options": [
            {"v": "200", "l": "Up to $200", "d": "Micro scooters start from about $160"}, {"v": "250", "l": "Up to $250", "d": ""},
            {"v": "300", "l": "Up to $300", "d": ""}, {"v": "any", "l": "No set budget", "d": ""}]},
    ],
}

# Spare parts finder (UK: /pages/spares-finder). Every non-empty NZ spare-part collection is mapped here
# to a finder tab and a short model name; the audit fails if one is missing.
SPARES_TABS = [("toddler", "Toddler & ride-on"), ("kids", "Kids"), ("adult", "Teen & adult"), ("stunt", "Stunt"),
               ("balance", "Balance bikes & trikes"), ("luggage", "Luggage"), ("helmets", "Helmets")]
SPARES_MODELS = {
    "mini-micro-kids-scooter-spare-parts": ("toddler", "Mini Micro"),
    "mini-micro-deluxe-spare-parts": ("toddler", "Mini Micro Deluxe"),
    "micro-mini2go-scooter-spare-parts": ("toddler", "Mini2Go"),
    "mini2go-deluxe-spare-parts": ("toddler", "Mini2Go Deluxe"),
    "micro-mini2grow-scooter-spare-parts": ("toddler", "Mini2Grow"),
    "micro-rock-and-go-spare-parts": ("toddler", "Rock & Go and Mini2Grow"),
    "micro-mini-microlino-spare-parts": ("toddler", "Mini Microlino"),
    "mini-micro-seat-scooter-spare-parts": ("toddler", "Mini Micro Seat"),
    "sporty-mini-new-scooter-spare-parts": ("toddler", "Sporty Mini"),
    "maxi-micro-scooter-spare-parts": ("kids", "Maxi Micro"),
    "maxi-deluxe-spare-parts-online": ("kids", "Maxi Micro Deluxe"),
    "maxi-micro-deluxe-pro-spare-parts": ("kids", "Maxi Micro Deluxe Pro"),
    "micro-sprite-scooter-spare-parts": ("kids", "Sprite"),
    "micro-sprite-suspension-scooter-spare-parts": ("kids", "Sprite Suspension"),
    "micro-cruiser-scooter-spare-parts": ("kids", "Cruiser"),
    "micro-rocket-scooter-spare-parts": ("kids", "Rocket"),
    "micro-classic-white-scooter-spare-parts": ("adult", "Micro Classic"),
    "micro-deluxe-spare-parts": ("adult", "Micro Deluxe"),
    "micro-downtown-scooter-spare-parts": ("adult", "Downtown"),
    "micro-flex-scooter-spare-parts": ("adult", "Flex"),
    "micro-flex-scooter-spare-parts-1": ("adult", "Flex+"),
    "micro-flex-air-scooter-spare-parts": ("adult", "Flex Air"),
    "micro-flex-blue-scooter-spare-parts": ("adult", "Flex Blue"),
    "micro-light-scooter-spare-parts": ("adult", "Micro Light"),
    "micro-speed-scooter-spare-parts": ("adult", "Speed+"),
    "speed-deluxe-spare-parts": ("adult", "Speed+ Deluxe"),
    "micro-suspension-scooter-spare-parts": ("adult", "Suspension"),
    "suburb-reloaded-spare-parts": ("adult", "Suburb Reloaded"),
    "kickboard-compact-spare-parts": ("adult", "Kickboard Compact"),
    "kickboard-original-spare-parts": ("adult", "Kickboard Original"),
    "kickboard-reloaded-spare-parts": ("adult", "Kickboard Reloaded"),
    "micro-bullet-scooter-spare-parts": ("adult", "Bullet"),
    "micro-bullet-street-pro-spare-parts": ("adult", "Bullet Street Pro"),
    "monster-bullet-scooter-spare-parts": ("adult", "Monster Bullet"),
    "micro-pedalflow-spare-parts": ("adult", "Pedalflow"),
    "genesis-spare-parts": ("adult", "Genesis"),
    "micro-ramp-scooter-spare-parts": ("stunt", "Ramp"),
    "micro-mx-trixx-scooter-spare-parts": ("stunt", "mX Trixx"),
    "mx-crossneck-scooter-spare-parts": ("stunt", "mX Crossneck"),
    "micro-mx-benj-scooter-spare-parts": ("stunt", "mX BenJ"),
    "micro-mx-core-scooter-spare-parts": ("stunt", "mX Core"),
    "micro-mx-freeride-street-scooter-spare-parts": ("stunt", "mX Freeride Street"),
    "maverick-scooter-spare-parts": ("stunt", "Maverick"),
    "balance-bike-parts": ("balance", "Balance Bike Lite"),
    "balance-bike-deluxe-parts": ("balance", "Balance Bike Deluxe"),
    "g-bike-air-balance-bike-spare-parts": ("balance", "G-Bike+ Air"),
    "micro-g-bike-chopper-balance-bike-spare-parts": ("balance", "G-Bike Chopper"),
    "micro-g-bike-plus-balance-bike-spare-parts": ("balance", "G-Bike+"),
    "micro-trike-spare-parts": ("balance", "Micro Trike"),
    "tricycle-spare-parts": ("balance", "Tricycle"),
    "micro-luggage-junior-scooter-spare-parts": ("luggage", "Luggage Junior"),
    "luggage-eazy-spare-parts": ("luggage", "Luggage Eazy"),
    "micro-luggage-ii-scoooter-spare-parts": ("luggage", "Luggage II"),
    "micro-helmets-spare-parts": ("helmets", "Helmets"),
}
