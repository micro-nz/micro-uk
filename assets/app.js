/* Micro UK design remake — client behaviour. No dependencies. */
(function () {
  "use strict";
  var M = window.MICRO || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var money = function (n) { return "$" + Number(n || 0).toLocaleString("en-NZ", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
  var U = function (path) { var p = path.split("?"); var b = p[0]; if (!/\/$/.test(b) && b.split("/").pop().indexOf(".") < 0) b += "/"; return M.base + b + (p[1] ? "?" + p[1] : ""); };
  var sized = function (url, w) { if (!url) return ""; if (url.indexOf("//") === 0) url = "https:" + url; url = url.replace(/([?&])width=\d+&?/, "$1").replace(/[?&]$/, ""); return url + (url.indexOf("?") > -1 ? "&" : "?") + "width=" + w; };
  var icon = function (n, cls) { return '<svg class="' + (cls || "icon") + '" aria-hidden="true" focusable="false"><use href="#i-' + n + '"></use></svg>'; };
  var params = function () { return new URLSearchParams(location.search); };
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
                set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
                del: function (k) { try { localStorage.removeItem(k); } catch (e) {} } };
  var AGE = { toddler: "Toddlers & preschool", kids: "Kids", adult: "Teens & adults" };
  var FEATURES = { led: "Light-up wheels", foldable: "Foldable", lightweight: "Lightweight", "large-wheels": "Large wheels", suspension: "Suspension", personalised: "Personalised", eco: "Eco material" };
  var PRICE_BANDS = [["0-50", 0, 50], ["50-100", 50, 100], ["100-200", 100, 200], ["200-300", 200, 300], ["300+", 300, 1e9]];

  function toast(msg) {
    var t = document.createElement("div"); t.className = "toast"; t.setAttribute("role", "status"); t.textContent = msg;
    document.body.appendChild(t); setTimeout(function () { t.remove(); }, 2600);
  }

  // ------------------------------------------------------------- data
  var cache = {};
  function getJSON(url) {
    if (!cache[url]) cache[url] = fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
    return cache[url];
  }
  var catalogue = function () {
    return getJSON(M.catalogue).then(function (list) {
      if (!list.byHandle) { list.byHandle = {}; list.forEach(function (x) { list.byHandle[x.h] = x; }); }
      return list;
    });
  };
  var contentIndex = function () { return getJSON(M.content); };

  function gql(query, variables) {
    return fetch(M.store + "/api/" + M.api + "/graphql.json", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: query, variables: variables || {} })
    }).then(function (r) { return r.json(); }).then(function (d) {
      if (d.errors) throw new Error(d.errors.map(function (e) { return e.message; }).join("; "));
      return d.data;
    });
  }

  // ------------------------------------------------------------- product card (mirrors remake/html.py product_card)
  function priceHTML(p, c) {
    return c ? '<div class="price price--sale"><span class="price__now">Now ' + money(p) + '</span><span class="price__was">Was <s>' + money(c) + '</s></span></div>'
             : '<div class="price"><span class="price__now">' + money(p) + '</span></div>';
  }
  function imgHTML(url, alt, sizes, cls, widths) {
    if (!url) return '<div class="img-placeholder ' + (cls || "") + '"></div>';
    widths = widths || [180, 360, 540, 720];
    return '<img src="' + esc(sized(url, widths[Math.min(2, widths.length - 1)])) + '" srcset="' + widths.map(function (w) { return esc(sized(url, w)) + " " + w + "w"; }).join(", ") +
      '" sizes="' + esc(sizes) + '" alt="' + esc(alt) + '" class="' + (cls || "") + '" loading="lazy" decoding="async">';
  }
  function cardHTML(x) {
    var url = U("/products/" + x.h), sizes = "(min-width: 990px) 22vw, (min-width: 750px) 30vw, 46vw";
    var badge = x.b ? '<span class="badge badge--' + esc(x.b.toLowerCase().replace(/ /g, "-")) + '">' + esc(x.b) + "</span>" : "";
    var sw = "";
    if (x.sw && x.sw.length > 1) {
      sw = '<ul class="card__swatches" aria-label="' + x.sw.length + ' colours">' + x.sw.slice(0, 6).map(function (s) {
        return '<li title="' + esc(s[0]) + '">' + imgHTML(s[1], s[0], "40px", "swatch__img", [60, 120]) + "</li>"; }).join("") +
        (x.sw.length > 6 ? '<li class="swatch__more">+' + (x.sw.length - 6) + "</li>" : "") + "</ul>";
    }
    var pills = (x.f || []).slice(0, 2).map(function (f) { return "<li>" + esc(FEATURES[f] || f) + "</li>"; }).join("");
    return '<article class="card" data-feature="product-card" data-h="' + esc(x.h) + '"><a class="card__media" href="' + url + '" tabindex="-1" aria-hidden="true">' +
      imgHTML(x.i, x.t, sizes, "card__img") + (x.i2 ? imgHTML(x.i2, "", sizes, "card__img card__img--hover") : "") + badge + "</a>" + sw +
      '<div class="card__body"><h3 class="card__title"><a href="' + url + '">' + esc(x.t) + "</a></h3>" + priceHTML(x.p, x.c) +
      (pills ? '<ul class="pills">' + pills + "</ul>" : "") + "</div></article>";
  }

  // ------------------------------------------------------------- overlays, drawers, menus
  var lastFocus = null;
  function openLayer(id) {
    var el = document.getElementById(id); if (!el) return;
    closeMegas();
    lastFocus = document.activeElement;
    el.hidden = false;
    var scrim = $("[data-scrim]"); if (el.classList.contains("drawer")) scrim.hidden = false;
    document.documentElement.style.overflow = "hidden";
    var f = $("input, button, a", el); if (f) setTimeout(function () { f.focus(); }, 30);
    if (id === "cart") Cart.render();
  }
  function closeLayers() {
    $$(".drawer, .search-overlay, .lightbox").forEach(function (el) { el.hidden = true; });
    $("[data-scrim]").hidden = true;
    document.documentElement.style.overflow = "";
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  function closeMegas(except) {
    $$("[data-mega]").forEach(function (b) {
      if (b === except) return;
      b.setAttribute("aria-expanded", "false");
      var m = document.getElementById(b.getAttribute("data-mega")); if (m) m.hidden = true;
    });
  }
  function initChrome() {
    document.addEventListener("click", function (e) {
      var o = e.target.closest("[data-open]");
      if (o) { e.preventDefault(); openLayer(o.getAttribute("data-open")); return; }
      if (e.target.closest("[data-close]") || e.target.matches("[data-scrim]") || e.target.matches(".search-overlay")) { closeLayers(); return; }
      var mb = e.target.closest("[data-mega]");
      if (mb) {
        var menu = document.getElementById(mb.getAttribute("data-mega"));
        var open = mb.getAttribute("aria-expanded") !== "true";
        closeMegas(mb); mb.setAttribute("aria-expanded", String(open)); menu.hidden = !open; return;
      }
      if (!e.target.closest(".mega")) closeMegas();
      if (!e.target.closest(".facet")) $$(".facet__menu").forEach(function (m) { m.hidden = true; m.previousElementSibling.setAttribute("aria-expanded", "false"); });
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") { closeMegas(); closeLayers(); } });
    // desktop hover intent for mega menus
    if (window.matchMedia("(hover: hover)").matches) {
      var t;
      $$("[data-mega]").forEach(function (b) {
        var menu = document.getElementById(b.getAttribute("data-mega"));
        var show = function () { clearTimeout(t); closeMegas(b); b.setAttribute("aria-expanded", "true"); menu.hidden = false; };
        var hide = function () { t = setTimeout(function () { b.setAttribute("aria-expanded", "false"); menu.hidden = true; }, 220); };
        b.addEventListener("mouseenter", show); b.addEventListener("mouseleave", hide);
        menu.addEventListener("mouseenter", function () { clearTimeout(t); }); menu.addEventListener("mouseleave", hide);
      });
    }
    $$(".mega__tab").forEach(function (tab) {
      var activate = function () {
        $$(".mega__tab").forEach(function (x) { x.classList.toggle("is-active", x === tab); });
        $$(".mega__panel").forEach(function (p) { p.classList.toggle("is-active", p.id === tab.getAttribute("data-panel")); });
      };
      tab.addEventListener("mouseenter", activate); tab.addEventListener("focus", activate);
    });
    // mobile menu panels
    $$("[data-to]").forEach(function (b) {
      b.addEventListener("click", function () {
        $$(".mm__panel").forEach(function (p) { p.hidden = p.id !== b.getAttribute("data-to"); });
        var f = $("#" + b.getAttribute("data-to") + " button, #" + b.getAttribute("data-to") + " a"); if (f) f.focus();
      });
    });
    // announcement rotation
    var msgs = $$(".ann__msg"), i = 0;
    if (msgs.length > 1 && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setInterval(function () { msgs[i].classList.remove("is-active"); i = (i + 1) % msgs.length; msgs[i].classList.add("is-active"); }, 4500);
    }
    // generic tabs (tab buttons with data-tab inside a tablist)
    document.addEventListener("click", function (e) {
      var tab = e.target.closest("button.tab[data-tab]"); if (!tab) return;
      var list = tab.parentElement;
      $$("button.tab[data-tab]", list).forEach(function (b) {
        var on = b === tab; b.classList.toggle("is-active", on); b.setAttribute("aria-selected", String(on));
        var panel = document.getElementById(b.getAttribute("data-tab")); if (panel) { panel.hidden = !on; panel.classList.toggle("is-active", on); }
      });
      initCarousels();
    });
    // copy link
    document.addEventListener("click", function (e) {
      var c = e.target.closest("[data-copy]"); if (!c) return;
      (navigator.clipboard ? navigator.clipboard.writeText(c.getAttribute("data-copy")) : Promise.reject()).then(function () { toast("Link copied"); }, function () { toast("Copy failed"); });
    });
    initCarousels();
  }
  function initCarousels() {
    $$("[data-carousel]").forEach(function (c) {
      var track = $(".carousel__track", c), prev = $("[data-prev]", c), next = $("[data-next]", c);
      if (!track || c._init) { if (c._update) c._update(); return; }
      c._init = true;
      var update = function () {
        prev.disabled = track.scrollLeft < 8;
        next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 8;
      };
      c._update = update;
      prev.addEventListener("click", function () { track.scrollBy({ left: -track.clientWidth * .9, behavior: "smooth" }); });
      next.addEventListener("click", function () { track.scrollBy({ left: track.clientWidth * .9, behavior: "smooth" }); });
      track.addEventListener("scroll", update, { passive: true }); window.addEventListener("resize", update);
      update();
    });
  }

  // ------------------------------------------------------------- search
  function scoreText(q, text) {
    text = (text || "").toLowerCase(); var words = q.toLowerCase().split(/\s+/).filter(Boolean); var s = 0;
    for (var i = 0; i < words.length; i++) { var w = words[i]; var at = text.indexOf(w); if (at < 0) return 0; s += at === 0 ? 3 : (/\s/.test(text.charAt(at - 1)) ? 2 : 1); }
    return s;
  }
  function searchAll(q) {
    return Promise.all([catalogue(), contentIndex()]).then(function (r) {
      var prods = r[0].map(function (x) { return { x: x, s: scoreText(q, x.t) * 3 + (x.a ? 1 : 0) - (x.cat === "parts" ? 1 : 0) }; })
        .filter(function (o) { return o.s > 0; }).sort(function (a, b) { return b.s - a.s; }).map(function (o) { return o.x; });
      var content = r[1].map(function (c) { return { c: c, s: scoreText(q, c.t) * 2 + scoreText(q, c.x) }; })
        .filter(function (o) { return o.s > 0; }).sort(function (a, b) { return b.s - a.s; }).map(function (o) { return o.c; });
      return { products: prods, articles: content.filter(function (c) { return c.k === "article"; }),
               pages: content.filter(function (c) { return c.k === "page"; }), collections: content.filter(function (c) { return c.k === "collection"; }) };
    });
  }
  function initPredictive() {
    var input = $("[data-predictive]"), out = $("[data-predictive-results]"); if (!input) return;
    var hint = out.innerHTML, timer;
    input.addEventListener("input", function () {
      clearTimeout(timer);
      var q = input.value.trim();
      if (q.length < 2) { out.innerHTML = hint; return; }
      timer = setTimeout(function () {
        searchAll(q).then(function (r) {
          if (input.value.trim() !== q) return;
          var prods = r.products.slice(0, 6).map(function (x) {
            return '<a class="predictive__item" href="' + U("/products/" + x.h) + '">' + imgHTML(x.i, "", "64px", "", [120]) + "<span><b>" + esc(x.t) + "</b>" + money(x.p) + "</span></a>"; }).join("");
          var links = r.collections.slice(0, 4).concat(r.articles.slice(0, 3), r.pages.slice(0, 3)).map(function (c) {
            return '<a href="' + U(c.u) + '">' + esc(c.t) + "</a>"; }).join("");
          out.innerHTML = (prods || links) ? '<div class="predictive__grid"><div><h3>Products</h3><div class="predictive__products">' + (prods || '<p class="muted">No products</p>') +
            '</div></div><div class="predictive__links"><h3>Suggestions</h3>' + (links || '<p class="muted">No pages</p>') + '</div></div><p><a class="btn btn--dark btn--sm" href="' +
            U("/search?q=" + encodeURIComponent(q)) + '">See all ' + r.products.length + " results</a></p>" : '<p class="muted">No results for "' + esc(q) + '".</p>';
        });
      }, 120);
    });
  }
  function initSearchPage() {
    var input = $("[data-search-input]"); if (!input) return;
    var q = params().get("q") || ""; input.value = q;
    var status = $("[data-search-status]");
    if (!q) return;
    status.textContent = "Searching…";
    searchAll(q).then(function (r) {
      $("[data-search-products]").innerHTML = r.products.slice(0, 48).map(cardHTML).join("");
      $("[data-search-articles]").innerHTML = r.articles.map(function (a) {
        return '<article class="post-card"><a class="post-card__media" href="' + U(a.u) + '">' + imgHTML(a.i, a.t, "30vw", "") + '</a><div class="post-card__body"><p class="eyebrow">' + esc(a.b) +
          '</p><h3><a href="' + U(a.u) + '">' + esc(a.t) + "</a></h3><p>" + esc(a.x) + "</p></div></article>"; }).join("");
      $("[data-search-pages]").innerHTML = r.collections.concat(r.pages).map(function (p) { return '<li><a href="' + U(p.u) + '">' + esc(p.t) + "<small>" + esc(p.x) + "</small></a></li>"; }).join("");
      $('[data-n="products"]').textContent = "(" + r.products.length + ")";
      $('[data-n="articles"]').textContent = "(" + r.articles.length + ")";
      $('[data-n="pages"]').textContent = "(" + (r.collections.length + r.pages.length) + ")";
      var total = r.products.length + r.articles.length + r.pages.length + r.collections.length;
      status.textContent = total ? total + ' results for "' + q + '"' + (r.products.length > 48 ? " (showing the first 48 products)" : "") : 'No results for "' + q + '". Try a shorter search.';
      if (!r.products.length && (r.articles.length || r.pages.length)) { var t = $('[data-tab="' + (r.articles.length ? "sr-articles" : "sr-pages") + '"]'); if (t) t.click(); }
    });
  }

  // ------------------------------------------------------------- cart (Storefront API cart, checkout on the NZ store)
  var CART_FIELDS = "id checkoutUrl totalQuantity cost { subtotalAmount { amount } } lines(first: 50) { nodes { id quantity " +
    "merchandise { ... on ProductVariant { id title image { url } price { amount } product { handle title } } } } }";
  var Cart = {
    id: store.get("micro_cart"),
    data: null,
    load: function () {
      if (!Cart.id) return Promise.resolve(null);
      return gql("query($id: ID!) { cart(id: $id) { " + CART_FIELDS + " } }", { id: Cart.id }).then(function (d) {
        if (!d.cart) { store.del("micro_cart"); Cart.id = null; }
        Cart.data = d.cart; Cart.paint(); return d.cart;
      }).catch(function () { return null; });
    },
    add: function (variantGid, qty) {
      var done = function (cart) { Cart.data = cart; Cart.id = cart.id; store.set("micro_cart", cart.id); Cart.paint(); return cart; };
      if (!Cart.id) {
        return gql("mutation($lines: [CartLineInput!]) { cartCreate(input: { lines: $lines }) { cart { " + CART_FIELDS + " } userErrors { message } } }",
          { lines: [{ merchandiseId: variantGid, quantity: qty || 1 }] }).then(function (d) {
          if (d.cartCreate.userErrors.length) throw new Error(d.cartCreate.userErrors[0].message); return done(d.cartCreate.cart); });
      }
      return gql("mutation($id: ID!, $lines: [CartLineInput!]!) { cartLinesAdd(cartId: $id, lines: $lines) { cart { " + CART_FIELDS + " } userErrors { message } } }",
        { id: Cart.id, lines: [{ merchandiseId: variantGid, quantity: qty || 1 }] }).then(function (d) {
        if (d.cartLinesAdd.userErrors.length) throw new Error(d.cartLinesAdd.userErrors[0].message);
        if (!d.cartLinesAdd.cart) { Cart.id = null; return Cart.add(variantGid, qty); }
        return done(d.cartLinesAdd.cart); });
    },
    update: function (lineId, qty) {
      var q = qty > 0 ? gql("mutation($id: ID!, $lines: [CartLineUpdateInput!]!) { cartLinesUpdate(cartId: $id, lines: $lines) { cart { " + CART_FIELDS + " } } }",
                            { id: Cart.id, lines: [{ id: lineId, quantity: qty }] }).then(function (d) { return d.cartLinesUpdate.cart; })
                      : gql("mutation($id: ID!, $ids: [ID!]!) { cartLinesRemove(cartId: $id, lineIds: $ids) { cart { " + CART_FIELDS + " } } }",
                            { id: Cart.id, ids: [lineId] }).then(function (d) { return d.cartLinesRemove.cart; });
      return q.then(function (cart) { Cart.data = cart; Cart.paint(); return cart; });
    },
    linesHTML: function (cart) {
      if (!cart || !cart.lines.nodes.length) return '<p class="cart-empty">Your cart is empty.</p>';
      return cart.lines.nodes.map(function (l) {
        var m = l.merchandise;
        return '<div class="cart-line" data-line="' + esc(l.id) + '">' + imgHTML(m.image && m.image.url, "", "80px", "", [160]) +
          '<div><a class="cart-line__title" href="' + U("/products/" + m.product.handle) + '">' + esc(m.product.title) + "</a>" +
          (m.title && m.title !== "Default Title" ? '<span class="cart-line__variant">' + esc(m.title) + "</span>" : "") +
          '<div><span class="qty"><button type="button" data-qty="-1" aria-label="Decrease quantity">' + icon("minus", "icon icon--sm") + "</button><span>" + l.quantity +
          '</span><button type="button" data-qty="1" aria-label="Increase quantity">' + icon("plus", "icon icon--sm") + '</button></span><button type="button" class="cart-line__remove" data-remove>Remove</button></div></div>' +
          '<div class="cart-line__price">' + money(m.price.amount * l.quantity) + "</div></div>";
      }).join("");
    },
    paint: function () {
      var c = Cart.data, n = c ? c.totalQuantity : 0, sub = c ? Number(c.cost.subtotalAmount.amount) : 0;
      $$("[data-cart-count]").forEach(function (el) { el.textContent = n; el.hidden = !n; });
      $$("[data-cart-count-text]").forEach(function (el) { el.textContent = n ? "(" + n + ")" : ""; });
      $$("[data-cart-subtotal]").forEach(function (el) { el.textContent = money(sub); });
      $$("[data-checkout]").forEach(function (el) { if (c && c.checkoutUrl) el.href = c.checkoutUrl; });
      var left = M.freeShip - sub;
      $$("[data-ship-text]").forEach(function (el) { el.innerHTML = sub <= 0 ? "Spend " + money(M.freeShip) + " for free shipping" : left > 0 ? "You're <b>" + money(left) + "</b> away from free shipping" : "<b>You've unlocked free shipping</b>"; });
      $$("[data-ship-bar]").forEach(function (el) { el.style.width = Math.min(100, sub / M.freeShip * 100) + "%"; });
      var lines = $("[data-cart-lines]"); if (lines) lines.innerHTML = Cart.linesHTML(c);
      var foot = $("[data-cart-foot]"); if (foot) foot.hidden = !n;
      var page = $("[data-cart-page-lines]"); if (page) page.innerHTML = Cart.linesHTML(c);
    },
    render: function () { Cart.paint(); return Cart.load(); }
  };
  function initCart() {
    Cart.paint();
    if (Cart.id) Cart.load().then(function () { if ($("[data-cart-page-lines]")) Cart.paint(); });
    else if ($("[data-cart-page-lines]")) Cart.paint();
    document.addEventListener("click", function (e) {
      var line = e.target.closest("[data-line]"); if (!line || !Cart.data) return;
      var l = Cart.data.lines.nodes.filter(function (x) { return x.id === line.getAttribute("data-line"); })[0]; if (!l) return;
      var q = e.target.closest("[data-qty]"), rm = e.target.closest("[data-remove]");
      if (!q && !rm) return;
      line.style.opacity = .5;
      Cart.update(l.id, rm ? 0 : l.quantity + Number(q.getAttribute("data-qty")));
    });
    document.addEventListener("click", function (e) {
      var b = e.target.closest("[data-quick-add]"); if (!b) return;
      e.preventDefault(); addToCart(b, b.getAttribute("data-quick-add"));
    });
  }
  function addToCart(btn, gid) {
    var label = btn.innerHTML; btn.disabled = true; btn.textContent = "Adding…";
    return Cart.add(gid, 1).then(function () { btn.innerHTML = label; btn.disabled = false; openLayer("cart"); },
      function (err) { btn.innerHTML = label; btn.disabled = false; toast("Couldn't add to cart: " + err.message); });
  }

  // ------------------------------------------------------------- reviews (Okendo, the NZ store's review platform)
  var OK = "https://api.okendo.io/v1/stores/" + M.okendo + "/products/shopify-";
  function starsHTML(r) {
    var s = ""; for (var i = 1; i <= 5; i++) s += icon("star", "icon" + (r >= i - .25 ? " is-on" : ""));
    return '<span class="stars" aria-hidden="true">' + s + "</span>";
  }
  function ratingInto(el) {
    var id = el.getAttribute("data-okendo"); if (!id || el.getAttribute("data-done")) return;
    el.setAttribute("data-done", "1");
    var compact = !!el.closest(".compare");
    getJSON(OK + id + "/review_aggregate").then(function (d) {
      var a = d.reviewAggregate || {};
      var n = a.reviewCount || a.ratingAndReviewCount || 0;
      var avg = a.ratingAndReviewValuesTotal && a.ratingAndReviewCount ? a.ratingAndReviewValuesTotal / a.ratingAndReviewCount : (a.avgRating || a.averageRating || 0);
      if (!n || !avg) { el.innerHTML = compact ? '<span class="nl">No reviews yet</span>' : '<span class="muted small">No reviews yet</span>'; return; }
      el.innerHTML = starsHTML(avg) + "<span>" + avg.toFixed(1) + "</span> " + (compact ? '<span class="muted">(' + n + ")</span>" : '<a href="#reviews">' + n + " review" + (n === 1 ? "" : "s") + "</a>");
      el.setAttribute("aria-label", "Rated " + avg.toFixed(1) + " out of 5 from " + n + " reviews");
    }).catch(function () { el.innerHTML = compact ? '<span class="nl">Unavailable</span>' : ""; });
  }
  function initRatings(scope) {
    $$("[data-okendo]", scope || document).forEach(ratingInto);
    if (scope) return;
    var box = $("[data-reviews]"); if (!box) return;
    var sec = box.closest("section"); if (sec) sec.id = "reviews";
    getJSON(OK + box.getAttribute("data-reviews") + "/reviews?limit=6&orderBy=date%20desc").then(function (d) {
      var rs = d.reviews || [];
      if (!rs.length) { box.innerHTML = '<p class="muted">No reviews yet for this product.</p>'; return; }
      box.innerHTML = rs.map(function (r) {
        var name = ((r.reviewer && r.reviewer.displayName) || "Verified buyer").split(" ")[0];
        return '<article class="review">' + starsHTML(r.rating) + "<h3>" + esc(r.title || "") + "</h3><p>" + esc(r.body || "") + '</p><p class="review__meta">' + esc(name) +
          (r.dateCreated ? " · " + new Date(r.dateCreated).toLocaleDateString("en-NZ", { day: "numeric", month: "short", year: "numeric" }) : "") + "</p></article>";
      }).join("");
    }).catch(function () { box.innerHTML = '<p class="muted">Reviews are unavailable right now.</p>'; });
  }

  // ------------------------------------------------------------- product page
  function initProduct() {
    var root = $("[data-product]"); if (!root) return;
    var P = JSON.parse(root.getAttribute("data-product"));
    var selected = {};
    var first = P.variants[0];
    if (first) Object.keys(first.options).forEach(function (k) { selected[k] = first.options[k]; });
    var want = params().get("variant");
    if (want) { var v0 = P.variants.filter(function (v) { return v.id === want; })[0]; if (v0) selected = Object.assign({}, v0.options); }
    var btn = $("[data-add-to-cart]");
    function current() {
      return P.variants.filter(function (v) { return Object.keys(selected).every(function (k) { return v.options[k] === selected[k]; }); })[0];
    }
    function paint() {
      var v = current();
      $$(".opt").forEach(function (o) {
        var on = selected[o.getAttribute("data-option")] === o.getAttribute("data-value");
        o.classList.toggle("is-selected", on); o.setAttribute("aria-pressed", String(on));
        var trial = Object.assign({}, selected); trial[o.getAttribute("data-option")] = o.getAttribute("data-value");
        var match = P.variants.filter(function (x) { return Object.keys(trial).every(function (k) { return x.options[k] === trial[k]; }); })[0];
        o.classList.toggle("is-unavailable", !match || !match.available);
      });
      $$("[data-option-label]").forEach(function (l) { l.textContent = selected[l.getAttribute("data-option-label")] || ""; });
      if (!v) { btn.disabled = true; btn.textContent = "Unavailable"; return; }
      var compare = v.compare > v.price ? v.compare : 0;
      $("[data-price]").innerHTML = priceHTML(v.price, compare);
      var save = $("[data-save]");
      if (compare) { save.hidden = false; save.textContent = "Save " + money(compare - v.price) + " (" + Math.round(100 * (compare - v.price) / compare) + "%)"; } else save.hidden = true;
      $("[data-instalment]").textContent = money(v.price / 4);
      var stock = $("[data-stock]"); stock.textContent = v.available ? "In stock" : "Sold out"; stock.classList.toggle("is-out", !v.available);
      btn.disabled = !v.available; btn.textContent = v.available ? "Add to cart" : "Sold out"; btn.setAttribute("data-variant", v.gid);
      if (v.image) {
        var imgs = $$(".gallery__item img"), hit = imgs.filter(function (i) { return i.currentSrc && i.src.split("?")[0] === v.image.split("?")[0] || (i.getAttribute("src") || "").split("?")[0] === v.image.split("?")[0]; })[0];
        if (hit) { var item = hit.closest(".gallery__item"); var g = item.parentElement;
          if (getComputedStyle(g).overflowX === "auto") g.scrollTo({ left: item.offsetLeft - g.offsetLeft, behavior: "smooth" });
          else if (item !== g.firstElementChild) g.insertBefore(item, g.firstElementChild); }
      }
      if (P.variants.length > 1) { var u = new URL(location.href); u.searchParams.set("variant", v.id); history.replaceState(null, "", u); }
    }
    $$(".opt").forEach(function (o) { o.addEventListener("click", function () { selected[o.getAttribute("data-option")] = o.getAttribute("data-value"); paint(); }); });
    btn.addEventListener("click", function () { addToCart(btn, btn.getAttribute("data-variant")); });
    paint();
    // live price and stock from the NZ store
    gql("query($h: String!) { product(handle: $h) { variants(first: 100) { nodes { id availableForSale price { amount } compareAtPrice { amount } } } } }", { h: P.handle })
      .then(function (d) {
        if (!d.product) return;
        d.product.variants.nodes.forEach(function (n) {
          P.variants.forEach(function (v) { if (v.gid === n.id) { v.available = n.availableForSale; v.price = Number(n.price.amount); v.compare = n.compareAtPrice ? Number(n.compareAtPrice.amount) : 0; } });
        });
        root.setAttribute("data-live", "1"); paint();
      }).catch(function () {});
    // lightbox
    var lb = $("#lightbox"), srcs = JSON.parse($("[data-lb-src]").textContent || "[]"), idx = 0;
    var show = function (i) { idx = (i + srcs.length) % srcs.length; $("[data-lb-img]").src = srcs[idx]; };
    $$("[data-lightbox]").forEach(function (b) { b.addEventListener("click", function () { lastFocus = b; show(Number(b.getAttribute("data-lightbox"))); lb.hidden = false; $(".lightbox__close").focus(); }); });
    $("[data-lb-prev]").addEventListener("click", function () { show(idx - 1); });
    $("[data-lb-next]").addEventListener("click", function () { show(idx + 1); });
    lb.addEventListener("keydown", function (e) { if (e.key === "ArrowLeft") show(idx - 1); if (e.key === "ArrowRight") show(idx + 1); });
    // complete the set: Shopify complementary recommendations, else helmets and accessories from the catalogue
    var cs = $("[data-complete-items]");
    if (cs) {
      var renderSet = function (items) {
        items = items.filter(function (x) { return x && x.a; }).slice(0, 3);
        if (!items.length) return;
        cs.innerHTML = items.map(function (x) {
          return '<div class="mini-item">' + imgHTML(x.i, "", "56px", "", [120]) + '<span><a href="' + U("/products/" + x.h) + '">' + esc(x.t) + "</a><br>" + money(x.p) + "</span>" +
            (x.multi ? '<a class="btn btn--outline btn--sm" href="' + U("/products/" + x.h) + '">Choose</a>' : '<button class="btn btn--dark btn--sm" data-quick-add="' + esc(x.vg) + '">Add</button>') + "</div>"; }).join("");
        cs.parentElement.hidden = false;
      };
      catalogue().then(function (cat) {
        return gql("query($id: ID!) { productRecommendations(productId: $id, intent: COMPLEMENTARY) { handle } }", { id: P.gid })
          .then(function (d) { return (d.productRecommendations || []).map(function (r) { return cat.byHandle[r.handle]; }); }, function () { return []; })
          .then(function (recs) {
            recs = recs.filter(Boolean);
            if (!recs.length) {
              var me = cat.byHandle[P.handle] || {};
              if (me.cat !== "scooters" && me.cat !== "ride-ons") return;
              var helmet = cat.filter(function (x) { return x.cat === "helmets" && x.a; })[0];
              var acc = cat.filter(function (x) { return x.cat === "accessories" && x.a && !/seat|personalis/i.test(x.t); }).slice(0, 2);
              recs = [helmet].concat(acc);
            }
            renderSet(recs);
          });
      });
    }
  }

  // ------------------------------------------------------------- collection filters, sort, paging
  function initCollection() {
    var root = $("[data-collection]"); if (!root) return;
    var handles = JSON.parse(root.getAttribute("data-collection")), size = Number(root.getAttribute("data-page-size")) || 24;
    var grid = $("[data-grid]"), shown = size, items = [];
    var keys = ["w", "f", "age", "pt", "price", "a"];
    var state = {};
    var p = params();
    keys.forEach(function (k) { state[k] = (p.get(k) || "").split(",").filter(Boolean); });
    var sortSel = $("[data-sort]"); if (p.get("sort")) sortSel.value = p.get("sort");
    function syncBoxes() { $$('input[type="checkbox"]', root.closest("section")).forEach(function (b) { b.checked = (state[b.name] || []).indexOf(b.value) > -1; }); }
    function match(x) {
      return keys.every(function (k) {
        var vals = state[k]; if (!vals.length) return true;
        if (k === "f") return vals.some(function (v) { return x.f.indexOf(v) > -1; });
        if (k === "price") return vals.some(function (v) { var b = PRICE_BANDS.filter(function (pb) { return pb[0] === v; })[0]; return b && x.p >= b[1] && x.p < b[2]; });
        if (k === "a") return x.a === 1;
        return vals.indexOf(String(x[k])) > -1;
      });
    }
    function sorted(list) {
      var s = sortSel.value, l = list.slice();
      var by = { "price-asc": function (a, b) { return a.p - b.p; }, "price-desc": function (a, b) { return b.p - a.p; },
                 "title-asc": function (a, b) { return a.t.localeCompare(b.t); }, "title-desc": function (a, b) { return b.t.localeCompare(a.t); },
                 "date-desc": function (a, b) { return (b.d || "").localeCompare(a.d || ""); } }[s];
      return by ? l.sort(by) : l;
    }
    function render(keepShown) {
      var list = sorted(items.filter(match));
      if (!keepShown) shown = size;
      grid.innerHTML = list.slice(0, shown).map(cardHTML).join("");
      $("[data-count]").textContent = list.length + " product" + (list.length === 1 ? "" : "s");
      var more = $("[data-load-more]"); more.hidden = list.length <= shown;
      $("[data-shown]").textContent = "Showing " + Math.min(shown, list.length) + " of " + list.length;
      var empty = $("[data-empty]"); if (empty) empty.hidden = list.length > 0;
      var chips = [];
      keys.forEach(function (k) { state[k].forEach(function (v) {
        var box = $('input[name="' + k + '"][value="' + v + '"]', root.closest("section"));
        var label = box ? box.nextElementSibling.textContent.trim() : v;
        chips.push('<button type="button" data-unset="' + k + ":" + esc(v) + '">' + esc(label) + " " + icon("close", "icon icon--xs") + "</button>"); }); });
      $("[data-active-filters]").innerHTML = chips.length ? chips.join("") + '<button type="button" data-clear>Clear all</button>' : "";
      $$("[data-pt-link]").forEach(function (a) { a.classList.toggle("is-active", state.pt.indexOf(a.getAttribute("data-pt-link")) > -1); });
      var u = new URL(location.href);
      keys.forEach(function (k) { if (state[k].length) u.searchParams.set(k, state[k].join(",")); else u.searchParams.delete(k); });
      if (sortSel.value !== "featured") u.searchParams.set("sort", sortSel.value); else u.searchParams.delete("sort");
      history.replaceState(null, "", u);
    }
    catalogue().then(function (cat) {
      items = handles.map(function (h) { return cat.byHandle[h]; }).filter(Boolean);
      syncBoxes();
      var hasState = keys.some(function (k) { return state[k].length; }) || sortSel.value !== "featured";
      if (hasState) render(); else render(true);
      root.setAttribute("data-ready", "1");
    });
    var section = root.closest("section");
    section.addEventListener("change", function (e) {
      var b = e.target; if (b.type !== "checkbox") return;
      $$('input[name="' + b.name + '"][value="' + b.value + '"]', section).forEach(function (o) { o.checked = b.checked; });
      state[b.name] = $$('input[name="' + b.name + '"]:checked', $("#filters")).map(function (o) { return o.value; });
      render();
    });
    sortSel.addEventListener("change", function () { render(); });
    $("[data-load-more]").addEventListener("click", function () { shown += size; render(true); });
    document.addEventListener("click", function (e) {
      var t = e.target.closest("[data-facet-toggle]");
      if (t) { var m = t.nextElementSibling, open = m.hidden; $$(".facet__menu").forEach(function (x) { x.hidden = true; x.previousElementSibling.setAttribute("aria-expanded", "false"); });
        m.hidden = !open; t.setAttribute("aria-expanded", String(open)); return; }
      if (e.target.closest("[data-clear]")) { keys.forEach(function (k) { state[k] = []; }); syncBoxes(); render(); return; }
      var u = e.target.closest("[data-unset]");
      if (u) { var kv = u.getAttribute("data-unset").split(":"); state[kv[0]] = state[kv[0]].filter(function (v) { return v !== kv[1]; }); syncBoxes(); render(); return; }
      var pt = e.target.closest("[data-pt-link]");
      if (pt) { e.preventDefault(); var code = pt.getAttribute("data-pt-link"); state.pt = state.pt.length === 1 && state.pt[0] === code ? [] : [code]; syncBoxes(); render(); root.scrollIntoView({ behavior: "smooth" }); }
    });
  }

  // ------------------------------------------------------------- comparison
  var Compare = {
    rows: [
      ["Price", function (x) { return { h: priceHTML(x.p, x.c), v: x.p }; }],
      ["Rating", function (x) { return { h: '<div class="rating" data-okendo="' + esc(x.id) + '"></div>', v: null }; }],
      ["Suits", function (x) { return Compare.val(AGE[x.age]); }],
      ["Recommended ages", function (x) { return Compare.val(x.s.ages); }],
      ["Wheels", function (x) { return Compare.val(x.s.wheels); }],
      ["Wheel size", function (x) { return Compare.val(x.s.wheel_mm); }],
      ["Sit-on ride-on", function (x) { return Compare.yn(!!x.s.rideon); }, function (sel) { return sel.some(function (x) { return x.s.rideon; }); }],
      ["Folds", function (x) { return Compare.yn(x.s.folds); }],
      ["Light-up wheels", function (x) { return Compare.yn(!!x.s.led); }],
      ["Large wheels", function (x) { return Compare.yn(x.s.large_wheels ? true : undefined); }],
      ["Suspension", function (x) { return Compare.yn(!!x.s.suspension); }],
      ["Lightweight", function (x) { return Compare.yn(x.s.lightweight ? true : undefined); }],
      ["Max rider weight", function (x) { return Compare.val(x.s.max_weight); }],
      ["Scooter weight", function (x) { return Compare.val(x.s.weight); }],
      ["Handlebar height", function (x) { return Compare.val(x.s.handlebar); }],
      ["Colours", function (x) { var n = (x.sw && x.sw.length) || 1; return { v: n, h: n + (n === 1 ? " colour" : " colours") +
        (x.sw && x.sw.length > 1 ? '<div class="compare__swatches">' + x.sw.slice(0, 8).map(function (s) { return '<img src="' + esc(sized(s[1], 60)) + '" alt="' + esc(s[0]) + '" title="' + esc(s[0]) + '" loading="lazy">'; }).join("") + "</div>" : "") }; }],
      ["Availability", function (x) { return { v: x.a, h: x.a ? '<span class="yes">In stock</span>' : '<span class="no">Sold out</span>' }; }],
      ["", function (x) { return { v: null, h: !x.a ? '<span class="muted">Sold out</span>' : x.multi ? '<a class="btn btn--outline btn--sm" href="' + U("/products/" + x.h) + '">Choose options</a>'
        : '<button type="button" class="btn btn--dark btn--sm" data-quick-add="' + esc(x.vg) + '">Add to cart</button>' }; }]
    ],
    val: function (s) { return s ? { v: s, h: esc(s) } : { v: "", h: '<span class="nl">Not listed</span>', nl: true }; },
    yn: function (b) { return b === true ? { v: "yes", h: '<span class="yes">' + icon("check", "icon icon--sm") + " Yes</span>" } : b === false ? { v: "no", h: '<span class="no">No</span>' } : { v: "", h: '<span class="nl">Not listed</span>', nl: true }; },
    group: function (x) { return AGE[x.age] || "Other"; },
    table: function (items, sel, uid) {
      var groups = {}; items.forEach(function (x) { (groups[Compare.group(x)] = groups[Compare.group(x)] || []).push(x); });
      var order = ["Toddlers & preschool", "Kids", "Teens & adults", "Other"];
      var head = '<tr><th scope="col"><span class="sr-only">Specification</span></th>' + sel.map(function (x, i) {
        var opts = order.filter(function (g) { return groups[g]; }).map(function (g) {
          return '<optgroup label="' + esc(g) + '">' + groups[g].map(function (o) { return '<option value="' + esc(o.h) + '"' + (o.h === x.h ? " selected" : "") + ">" + esc(o.t) + "</option>"; }).join("") + "</optgroup>"; }).join("");
        return '<th scope="col"><label class="sr-only" for="' + uid + "-s" + i + '">Product ' + (i + 1) + '</label><select id="' + uid + "-s" + i + '" data-col="' + i + '">' + opts + "</select>" +
          '<a class="compare__img" href="' + U("/products/" + x.h) + '" tabindex="-1" aria-hidden="true">' + imgHTML(x.i, "", "(min-width: 990px) 20vw, 40vw", "", [240, 480]) + "</a>" +
          '<a class="compare__name" href="' + U("/products/" + x.h) + '">' + esc(x.t) + "</a></th>"; }).join("") + "</tr>";
      var body = Compare.rows.map(function (r) {
        if (r[2] && !r[2](sel)) return "";
        var cells = sel.map(function (x) { return r[1](x); });
        if (r[0] && cells.every(function (c) { return c.nl; })) return "";
        var comparable = cells[0].v !== null;
        var same = comparable && cells.every(function (c) { return String(c.v) === String(cells[0].v); });
        return '<tr class="' + (comparable ? (same ? "is-same" : "is-diff") : "") + '"><th scope="row">' + esc(r[0]) + "</th>" + cells.map(function (c) { return "<td>" + c.h + "</td>"; }).join("") + "</tr>";
      }).join("");
      return '<table><caption class="sr-only">Product comparison</caption><thead>' + head + "</thead><tbody>" + body + "</tbody></table>";
    },
    init: function (root, cat) {
      var handles = JSON.parse(root.getAttribute("data-handles")), uid = root.id || "cmp";
      var items = handles.map(function (h) { return cat.byHandle[h]; }).filter(function (x) { return x && x.s; });
      var want = (root.getAttribute("data-url-sync") && params().get("p") || "").split(",").filter(function (h) { return cat.byHandle[h] && handles.indexOf(h) > -1; });
      var sel = (want.length ? want : JSON.parse(root.getAttribute("data-defaults"))).map(function (h) { return cat.byHandle[h]; }).filter(Boolean);
      items.forEach(function (x) { if (sel.length < Math.min(3, items.length) && sel.indexOf(x) < 0) sel.push(x); });
      sel = sel.slice(0, 3);
      var diff = root.closest("section").querySelector("[data-compare-diff]");
      var draw = function () {
        root.innerHTML = Compare.table(items, sel, uid);
        root.classList.toggle("show-diff", !!(diff && diff.checked));
        $$("tr.is-same", root).forEach(function (tr) { tr.hidden = false; });
        if (!(diff && diff.checked)) $$("tr", root).forEach(function (tr) { tr.classList.remove("is-same", "is-diff"); tr.dataset.cmp = ""; });
        root.setAttribute("data-ready", sel.map(function (x) { return x.h; }).join(","));
        initRatings(root);
        if (root.getAttribute("data-url-sync")) { var u = new URL(location.href); u.searchParams.set("p", sel.map(function (x) { return x.h; }).join(",")); history.replaceState(null, "", u); }
      };
      root.addEventListener("change", function (e) {
        var s = e.target.closest("select[data-col]"); if (!s) return;
        var i = Number(s.getAttribute("data-col")), pick = cat.byHandle[s.value], prev = sel[i], j = sel.indexOf(pick);
        if (j > -1 && j !== i) sel[j] = prev; // already shown in another column: swap
        sel[i] = pick; draw();
        var again = $("#" + uid + "-s" + i); if (again) again.focus();
      });
      if (diff) diff.addEventListener("change", draw);
      draw();
    }
  };
  function initCompare() {
    var roots = $$("[data-compare]"); if (!roots.length) return;
    catalogue().then(function (cat) { roots.forEach(function (r) { Compare.init(r, cat); }); });
  }
  // ------------------------------------------------------------- scooter finder quiz
  var Quiz = {
    STYLE: { rideon: "Sit-on ride-on", "3": "3 wheels", "2": "2 wheels", bike: "Balance bike or trike", stunt: "Stunt scooter" },
    FEAT: { led: ["Light-up wheels", "No light-up wheels"], foldable: ["Folds for carrying", "Doesn't fold"], lightweight: ["Lightweight", "Not listed as lightweight"],
            large: ["Big wheels", "Standard wheels"], suspension: ["Suspension", "No suspension"], personalised: ["Can be personalised", "Not personalisable"] },
    has: function (x, f) {
      var s = x.s || {};
      return { led: !!s.led, foldable: s.folds === true, lightweight: !!s.lightweight, large: !!s.large_wheels, suspension: !!s.suspension,
               personalised: !!s.personalised || (x.col || []).indexOf("personalised-scooters") > -1 }[f];
    },
    style: function (x, st) {
      var s = x.s || {};
      if (st === "rideon") return !!s.rideon;
      if (st === "3") return s.wheels === "3 wheels";
      if (st === "2") return s.wheels === "2 wheels" && (x.col || []).indexOf("freestyle-scooters") < 0;
      if (st === "stunt") return (x.col || []).indexOf("freestyle-scooters") > -1;
      if (st === "bike") return s.wheels === "Balance bike" || s.wheels === "Tricycle";
      return true;
    },
    pool: function (age, items, pools) {
      var want = pools[age] || [];
      return items.filter(function (x) { return x.s && (x.cat === "scooters" || x.cat === "ride-ons" || x.cat === "luggage") && (x.col || []).some(function (c) { return want.indexOf(c) > -1; }); });
    },
    family: function (x) {
      var stop = /^(micro|scooter|scooters|kids|kid|adult|2|3|wheel|wheels|led|light|up|light-up|neochrome|pearl|silverchrome|glow|white|black|art|collection|special|edition|eco|glitter|magic|nanogrid|grey|the|&|x|bmw|in|plus|-)$/;
      return x.t.toLowerCase().replace(/[^a-z0-9+& -]/g, " ").split(/\s+/).filter(function (w) { return w && !stop.test(w); }).slice(0, 2).join(" ");
    },
    recommend: function (ans, items, pools) {
      var f = ans.f || [], budget = ans.budget && ans.budget !== "any" ? Number(ans.budget) : Infinity, notes = [];
      var pool = Quiz.pool(ans.age, items, pools);
      var styleOk = function (x) { return !ans.style || ans.style === "any" || Quiz.style(x, ans.style); };
      var c = pool.filter(function (x) { return x.a && styleOk(x) && x.p <= budget; });
      if (!c.length && budget < Infinity) { c = pool.filter(function (x) { return x.a && styleOk(x); }); if (c.length) notes.push("Nothing" + (ans.style && ans.style !== "any" ? " in that style" : "") + " fits a $" + budget + " budget, so these are the closest options above it."); }
      if (!c.length && ans.style && ans.style !== "any") { c = pool.filter(function (x) { return x.a && x.p <= budget; }); if (c.length) notes.push("We don't currently have a " + Quiz.STYLE[ans.style].toLowerCase() + " in stock for this age, so here are the closest alternatives."); }
      if (!c.length) { c = pool.slice(); if (c.length) notes.push("These are currently sold out online; check back soon or ask a stockist."); }
      var scored = c.map(function (x) {
        var s = 0, s2 = x.s || {};
        f.forEach(function (k) { if (Quiz.has(x, k)) s += 8; });
        var use = ans.use;
        if (use === "school") s += (s2.folds ? 2 : 0) + (s2.lightweight ? 1 : 0);
        if (use === "travel") s += (s2.folds ? 2 : 0) + (s2.lightweight ? 1 : 0) + (x.cat === "luggage" ? 3 : 0);
        if (use === "commute") s += (s2.large_wheels ? 2 : 0) + (s2.folds ? 2 : 0) + (s2.suspension ? 1 : 0);
        if (use === "park") s += (x.col || []).indexOf("freestyle-scooters") > -1 ? 3 : 0;
        if (use === "home") s += s2.led ? 1 : 0;
        if (x.cat === "luggage" && use !== "travel") s -= 4;
        if ((x.col || []).indexOf("bestselling-scooters") > -1) s += 1.5;
        if (x.p > budget) s -= 1 + (x.p - budget) / 25; // the further over budget, the lower it ranks
        return { x: x, score: s };
      }).sort(function (a, b) { return b.score - a.score || a.x.p - b.x.p; });
      var picks = [], seen = {}, rest = [];
      scored.forEach(function (o) { var fam = Quiz.family(o.x); if (picks.length < 3 && !seen[fam]) { seen[fam] = 1; picks.push(o); } else rest.push(o); });
      while (picks.length < 3 && rest.length) picks.push(rest.shift());
      var reasons = function (x) {
        var r = [{ ok: true, t: "Suits " + ({ toddler: "toddlers and preschoolers", kids: "children", teen: "teenagers", adult: "adults" })[ans.age] + (x.s.ages ? " (" + x.s.ages + ")" : "") }];
        if (ans.style && ans.style !== "any") r.push({ ok: Quiz.style(x, ans.style), t: Quiz.STYLE[ans.style] });
        else if (x.s.wheels) r.push({ ok: true, t: x.s.wheels });
        f.forEach(function (k) { var ok = Quiz.has(x, k); r.push({ ok: ok, t: Quiz.FEAT[k][ok ? 0 : 1] }); });
        if (budget < Infinity) r.push({ ok: x.p <= budget, t: x.p <= budget ? "Within your $" + budget + " budget" : money(x.p) + ", above your budget" });
        if (x.s.max_weight) r.push({ ok: true, t: "Max rider weight " + x.s.max_weight });
        return r;
      };
      var more = rest.slice(0, 8).map(function (o) { return o.x; }), moreLabel = "More good matches";
      if (picks.length < 3) {
        // only a few products fit: offer near misses (other styles or over budget), same style first, then cheapest
        var taken = picks.map(function (o) { return o.x; });
        more = pool.filter(function (x) { return x.a && taken.indexOf(x) < 0; })
          .sort(function (a, b) { return (styleOk(b) - styleOk(a)) || (a.p - b.p); }).slice(0, 6);
        moreLabel = "Close alternatives";
        if (!notes.length && more.length) notes.push("Only " + picks.length + " product" + (picks.length === 1 ? " matches" : "s match") + " every answer, so we've added some close alternatives below.");
      }
      return { picks: picks.map(function (o) { return { x: o.x, score: o.score, why: reasons(o.x) }; }), more: more, moreLabel: moreLabel, notes: notes, pool: pool.length };
    }
  };
  function initQuiz() {
    var form = $("[data-quiz]"); if (!form) return;
    var pools = JSON.parse(form.getAttribute("data-pools")), steps = $$(".quiz__step", form), at = 0, items = [];
    var results = $("[data-quiz-results]"), bar = $("[data-quiz-bar]");
    var ans = function () {
      var a = {}; steps.forEach(function (st) {
        var id = st.getAttribute("data-id"), ch = $$("input:checked", st).map(function (i) { return i.value; });
        if (st.hasAttribute("data-multi")) a[id] = ch; else if (ch.length) a[id] = ch[0]; });
      return a;
    };
    function visibleOpts(st) { return $$(".quiz__opt", st).filter(function (o) { return !o.hidden; }); }
    function prepare(st) {
      var a = ans(), age = a.age;
      $$(".quiz__opt", st).forEach(function (o) {
        var ages = (o.getAttribute("data-ages") || "").split(" ").filter(Boolean);
        var show = !ages.length || !age || ages.indexOf(age) > -1;
        if (show && st.getAttribute("data-id") === "f" && items.length) {
          var v = $("input", o).value; show = Quiz.pool(age, items, pools).some(function (x) { return x.a && Quiz.has(x, v); });
        }
        if (show && st.getAttribute("data-id") === "style" && items.length && $("input", o).value !== "any") {
          var sv = $("input", o).value; show = Quiz.pool(age, items, pools).some(function (x) { return Quiz.style(x, sv); });
        }
        o.hidden = !show; if (!show) $("input", o).checked = false;
      });
      refresh(st);
    }
    function refresh(st) {
      var multi = Number(st.getAttribute("data-multi") || 0), n = $$("input:checked", st).length;
      $("[data-quiz-next]", st).disabled = multi ? false : n === 0;
      $("[data-quiz-next]", st).textContent = (st === steps[steps.length - 1]) ? "See my matches" : (multi && !n ? "Skip" : "Next");
      if (multi) $$(".quiz__opt", st).forEach(function (o) { var i = $("input", o); var off = !i.checked && n >= multi; i.disabled = off; o.classList.toggle("is-disabled", off); });
      var skip = $("[data-quiz-skip]", st); if (skip) skip.hidden = !multi || !n ? true : false;
    }
    function go(i) {
      at = Math.max(0, Math.min(steps.length - 1, i));
      steps.forEach(function (st, j) { st.hidden = j !== at; });
      prepare(steps[at]);
      if (visibleOpts(steps[at]).length === 0) return go(at + (i >= at ? 1 : -1));
      bar.style.width = Math.round((at + 1) / (steps.length + 1) * 100) + "%";
      results.hidden = true; form.hidden = false;
      var lg = $("legend", steps[at]); if (lg && document.activeElement && document.activeElement !== document.body) lg.focus();
    }
    function finish(push) {
      var a = ans(), r = Quiz.recommend(a, items, pools);
      bar.style.width = "100%"; form.hidden = true; results.hidden = false;
      var who = { toddler: "a toddler", kids: "a child", teen: "a teenager", adult: "an adult" }[a.age];
      var bits = [];
      if (a.style && a.style !== "any") bits.push(Quiz.STYLE[a.style].toLowerCase());
      (a.f || []).forEach(function (k) { bits.push(Quiz.FEAT[k][0].toLowerCase()); });
      $("[data-quiz-summary]").textContent = "For " + who + (bits.length ? ", looking for " + bits.join(", ") : "") + (a.budget && a.budget !== "any" ? ", up to $" + a.budget : "") + ".";
      var note = $("[data-quiz-note]"); note.hidden = !r.notes.length; note.textContent = r.notes.join(" ");
      $("[data-quiz-title]").textContent = r.picks.length ? "Our top " + (r.picks.length === 1 ? "pick" : r.picks.length + " picks") : "No matches";
      $("[data-quiz-grid]").innerHTML = r.picks.length ? r.picks.map(function (o, i) {
        var x = o.x;
        return '<div class="quiz-pick" data-pick="' + esc(x.h) + '"><p class="quiz-pick__rank">' + (o.why.some(function (w) { return !w.ok; }) ? "Worth considering" : i === 0 ? "Best match" : "Also a great match") + "</p>" + cardHTML(x) +
          '<ul class="quiz-pick__why">' + o.why.map(function (w) { return '<li class="' + (w.ok ? "" : "is-miss") + '">' + icon(w.ok ? "check" : "minus") + "<span>" + esc(w.t) + "</span></li>"; }).join("") + "</ul>" +
          '<div class="btn-row">' + (x.a && !x.multi ? '<button type="button" class="btn btn--dark btn--sm" data-quick-add="' + esc(x.vg) + '">Add to cart</button>' : "") +
          '<a class="btn btn--outline btn--sm" href="' + U("/products/" + x.h) + '">' + (x.multi ? "Choose colour" : "View details") + "</a></div></div>";
      }).join("") : '<p>We couldn\'t find a match. <a href="' + U("/collections/all-scooters") + '">Browse all scooters</a> or <a href="' + U("/pages/contact") + '">ask our team</a>.</p>';
      $("[data-quiz-more-wrap]").hidden = !r.more.length;
      $("[data-quiz-more-title]").textContent = r.moreLabel;
      $("[data-quiz-more]").innerHTML = r.more.map(cardHTML).join("");
      var cmp = $("[data-quiz-compare]"); cmp.hidden = r.picks.length < 2;
      cmp.href = U("/pages/compare-scooters?p=" + r.picks.map(function (o) { return o.x.h; }).join(","));
      if (push !== false) {
        var u = new URL(location.href); u.search = "";
        Object.keys(a).forEach(function (k) { var v = Array.isArray(a[k]) ? a[k].join(",") : a[k]; if (v) u.searchParams.set(k, v); });
        history.replaceState(null, "", u);
      }
      results.setAttribute("data-ready", r.picks.map(function (o) { return o.x.h; }).join(","));
      if (push !== false) results.focus();
      initRatings(results);
    }
    form.addEventListener("change", function (e) {
      var st = e.target.closest(".quiz__step"); refresh(st);
      if (!st.hasAttribute("data-multi") && e.target.checked && e.isTrusted && window.matchMedia("(hover: hover)").matches) { /* stay: let people review before Next */ }
    });
    form.addEventListener("click", function (e) {
      if (e.target.closest("[data-quiz-next]")) { if (at === steps.length - 1) finish(); else go(at + 1); }
      if (e.target.closest("[data-quiz-back]")) go(at - 1);
      if (e.target.closest("[data-quiz-skip]")) { $$("input", steps[at]).forEach(function (i) { i.checked = false; }); if (at === steps.length - 1) finish(); else go(at + 1); }
    });
    $("[data-quiz-restart]").addEventListener("click", function () {
      $$("input", form).forEach(function (i) { i.checked = false; i.disabled = false; });
      history.replaceState(null, "", location.pathname); go(0);
    });
    catalogue().then(function (cat) {
      items = cat;
      var p = params();
      if (p.get("age")) {
        steps.forEach(function (st) {
          var id = st.getAttribute("data-id"), vals = (p.get(id) || "").split(",");
          $$("input", st).forEach(function (i) { i.checked = vals.indexOf(i.value) > -1; });
        });
        finish(false);
      } else go(0);
      form.setAttribute("data-ready", "1");
    });
    window.MicroQuiz = { recommend: function (a) { return Quiz.recommend(a, items, pools); }, pools: pools, ready: function () { return catalogue(); } };
  }

  // ------------------------------------------------------------- spares finder
  function initFinder() {
    var input = $("[data-finder-search]"); if (!input) return;
    var section = input.closest("section"), status = $("[data-finder-status]"), empty = $("[data-finder-empty]");
    var q0 = params().get("q"); if (q0) input.value = q0;
    function run() {
      var q = input.value.trim().toLowerCase().replace(/[^a-z0-9+& ]/g, " "), words = q.split(/\s+/).filter(Boolean);
      section.classList.toggle("is-filtering", !!words.length);
      var n = 0;
      $$(".model-tile", section).forEach(function (t) {
        var name = t.getAttribute("data-model"), ok = words.every(function (w) { return name.indexOf(w) > -1; });
        t.hidden = words.length ? !ok : false; if (ok && words.length) n++;
      });
      $$(".tabpanel", section).forEach(function (p) {
        if (words.length) p.hidden = !$$(".model-tile", p).some(function (t) { return !t.hidden; });
        else p.hidden = !p.classList.contains("is-active");
      });
      empty.hidden = !words.length || n > 0;
      status.textContent = words.length ? (n ? n + " model" + (n === 1 ? "" : "s") + " match" + (n === 1 ? "es" : "") : "") : "";
      var u = new URL(location.href); if (words.length) u.searchParams.set("q", input.value.trim()); else u.searchParams.delete("q"); history.replaceState(null, "", u);
    }
    input.addEventListener("input", run);
    if (q0) run();
  }

  // ------------------------------------------------------------- blog paging
  function initBlog() {
    var grid = $("[data-paged]"); if (!grid) return;
    var size = Number(grid.getAttribute("data-paged")), cards = $$(".post-card", grid), shown = size, btn = $("[data-load-more-posts]");
    var paint = function () { cards.forEach(function (c, i) { c.hidden = i >= shown; }); btn.hidden = shown >= cards.length; };
    btn.addEventListener("click", function () { shown += size; paint(); });
    paint();
  }

  function boot() {
    initChrome(); initPredictive(); initSearchPage(); initCart(); initProduct(); initCollection(); initCompare(); initQuiz(); initFinder(); initBlog(); initRatings();
    document.documentElement.setAttribute("data-app", "ready");
  }
  window.MicroApp = { Cart: Cart, Quiz: Quiz, Compare: Compare, catalogue: catalogue, searchAll: searchAll };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
