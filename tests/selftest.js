// Browser self-test for the remake. Served by tools/serve.py at /__selftest.js and run from any page of the
// local preview:  await (await import('/__selftest.js')).run()
// Each test loads a real page in an iframe, drives it like a shopper would and checks the result.
// Results are POSTed to /__selftest, which writes reports/runtime.json for tools/audit.py.
// Note: the cart test creates (and empties) a real cart on the Micro NZ store; no order is placed.

const BASE = "/micro-uk";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function until(fn, ms = 8000, step = 50) {
  const t0 = Date.now();
  for (;;) {
    let v; try { v = fn(); } catch (e) { v = null; }
    if (v) return v;
    if (Date.now() - t0 > ms) throw new Error("timed out waiting for " + fn.toString().slice(0, 90));
    await sleep(step);
  }
}

async function open(path, width = 1280) {
  const f = document.createElement("iframe");
  f.style.cssText = `position:fixed;left:-${width + 50}px;top:0;width:${width}px;height:900px;border:0`;
  f.src = BASE + path;
  document.body.appendChild(f);
  await until(() => f.contentDocument && f.contentDocument.documentElement.getAttribute("data-app") === "ready", 15000);
  return { win: f.contentWindow, doc: f.contentDocument, close: () => f.remove() };
}

const tests = {
  "mega-menu": async () => {
    const { doc, close } = await open("/");
    doc.querySelector('[data-mega="mega-shop"]').click();
    const mega = doc.getElementById("mega-shop");
    const tabs = mega.querySelectorAll(".mega__tab");
    tabs[1].dispatchEvent(new Event("focus"));
    const ok = !mega.hidden && tabs.length >= 6 && mega.querySelector("#mega-1").classList.contains("is-active");
    doc.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    const closed = mega.hidden;
    close();
    return [ok && closed, `${tabs.length} tabs, panel switch on focus, Escape closes: ${closed}`];
  },
  "predictive-search": async () => {
    const { doc, win, close } = await open("/");
    doc.querySelector('[data-open="search"]').click();
    const input = doc.querySelector("[data-predictive]");
    input.value = "sprite"; input.dispatchEvent(new win.Event("input", { bubbles: true }));
    const n = await until(() => doc.querySelectorAll(".predictive__item").length);
    const all = doc.querySelector("[data-predictive-results] .btn").textContent;
    close();
    return [n >= 3, `${n} product suggestions for "sprite"; ${all.trim()}`];
  },
  "mobile-menu": async () => {
    const { doc, win, close } = await open("/", 375);
    const burger = doc.querySelector('[data-open="mobile-menu"]');
    const visible = win.getComputedStyle(burger).display !== "none";
    burger.click();
    const menu = doc.getElementById("mobile-menu");
    menu.querySelector("[data-to]").click();
    const sub = [...menu.querySelectorAll(".mm__panel")].find((p) => !p.hidden);
    sub.querySelector(".mm__back").click();
    const back = !doc.getElementById("mm-root").hidden;
    const desktopNavHidden = win.getComputedStyle(doc.querySelector(".nav--left")).display === "none";
    close();
    return [visible && !menu.hidden && sub.id !== "mm-root" && back && desktopNavHidden, `menu button shown at 375px, opened, drilled into "${sub.querySelector(".mm__title").textContent}", back works`];
  },
  "carousel-tabs": async () => {
    const { doc, close } = await open("/");
    const sec = doc.querySelector('[data-feature="tabbed-carousel"]');
    const tabs = sec.querySelectorAll("button.tab");
    tabs[1].click();
    const ok = !doc.getElementById("c1-1").hidden && doc.getElementById("c1-0").hidden && doc.getElementById("c1-1").querySelectorAll(".card").length > 1;
    close();
    return [ok, `switched to "${tabs[1].textContent}"`];
  },
  filters: async () => {
    const { doc, win, close } = await open("/collections/kids-scooters/");
    await until(() => doc.querySelector("[data-collection]").dataset.ready);
    const before = doc.querySelectorAll("[data-grid] .card").length;
    const cat = await win.MicroApp.catalogue();
    const box = doc.querySelector('#filters input[name="w"][value="3"]');
    box.checked = true; box.dispatchEvent(new win.Event("change", { bubbles: true }));
    const cards = [...doc.querySelectorAll("[data-grid] .card")];
    const allThree = cards.every((c) => cat.byHandle[c.dataset.h].w === "3");
    const url = win.location.search;
    doc.querySelector("[data-clear]").click();
    const restored = doc.querySelectorAll("[data-grid] .card").length;
    close();
    return [cards.length > 0 && cards.length < before && allThree && url.includes("w=3") && restored === before, `${before} → ${cards.length} with "3 wheels" (all 3-wheel), URL ${url}, cleared back to ${restored}`];
  },
  sort: async () => {
    const { doc, win, close } = await open("/collections/kids-scooters/");
    await until(() => doc.querySelector("[data-collection]").dataset.ready);
    const cat = await win.MicroApp.catalogue();
    const sel = doc.querySelector("[data-sort]"); sel.value = "price-asc"; sel.dispatchEvent(new win.Event("change", { bubbles: true }));
    const prices = [...doc.querySelectorAll("[data-grid] .card")].map((c) => cat.byHandle[c.dataset.h].p);
    const asc = prices.every((p, i) => !i || prices[i - 1] <= p);
    close();
    return [asc && prices.length > 1, `price low→high: ${prices[0]} … ${prices[prices.length - 1]}`];
  },
  "load-more": async () => {
    const { doc, close } = await open("/collections/all-scooters/");
    await until(() => doc.querySelector("[data-collection]").dataset.ready);
    const a = doc.querySelectorAll("[data-grid] .card").length;
    doc.querySelector("[data-load-more]").click();
    const b = doc.querySelectorAll("[data-grid] .card").length;
    const text = doc.querySelector("[data-shown]").textContent;
    close();
    return [a === 24 && b > a, `${a} → ${b} cards; "${text}"`];
  },
  compare: async () => {
    const { doc, win, close } = await open("/pages/compare-scooters/?p=micro-sprite-kids-scooter,mini-micro-deluxe-3-wheel-scooter,micro-classic-adult-scooter");
    const root = doc.querySelector("[data-compare]");
    await until(() => root.dataset.ready);
    const start = root.dataset.ready.split(",");
    const s0 = root.querySelector('select[data-col="0"]');
    s0.value = start[1]; s0.dispatchEvent(new win.Event("change", { bubbles: true }));
    const swapped = root.dataset.ready.split(",");
    const diff = doc.querySelector("[data-compare-diff]"); diff.checked = true; diff.dispatchEvent(new win.Event("change", { bubbles: true }));
    const same = root.querySelectorAll("tr.is-same").length, differ = root.querySelectorAll("tr.is-diff").length;
    const rows = root.querySelectorAll("tbody tr").length;
    const synced = win.location.search.includes(encodeURIComponent(swapped.join(",")));
    const notListed = root.querySelectorAll(".nl").length;
    close();
    const ok = start.length === 3 && swapped[0] === start[1] && swapped[1] === start[0] && differ > 0 && rows >= 10 && synced;
    return [ok, `3 columns from URL, picking a shown product swaps columns, ${rows} rows (${differ} differ, ${same} same, ${notListed} "Not listed" cells), URL synced`];
  },
  lightbox: async () => {
    const { doc, close } = await open("/products/micro-sprite-kids-scooter/");
    doc.querySelector("[data-lightbox]").click();
    const lb = doc.getElementById("lightbox"), img = lb.querySelector("[data-lb-img]");
    const a = img.getAttribute("src");
    lb.querySelector("[data-lb-next]").click();
    const b = img.getAttribute("src");
    close();
    return [!lb.hidden && a && b && a !== b, "opens on click, next image works"];
  },
  rating: async () => {
    const { doc, close } = await open("/products/micro-sprite-kids-scooter/");
    const el = doc.querySelector(".buy-box [data-okendo]");
    await until(() => el.innerHTML.trim());
    const text = el.textContent.trim();
    close();
    return [/\d\.\d/.test(text) || /No reviews/.test(text), `"${text}"`];
  },
  reviews: async () => {
    const { doc, close } = await open("/products/micro-sprite-kids-scooter/");
    const box = doc.querySelector("[data-reviews]");
    await until(() => box.querySelector(".review") || /No reviews|unavailable/.test(box.textContent));
    const n = box.querySelectorAll(".review").length;
    close();
    return [n > 0, `${n} recent reviews loaded from the NZ store's Okendo account`];
  },
  variant: async () => {
    const { doc, win, close } = await open("/products/micro-sprite-kids-scooter/");
    const opts = [...doc.querySelectorAll('.opt[data-option="Colour"]')];
    const before = doc.querySelector("[data-add-to-cart]").dataset.variant;
    opts[2].click();
    const after = doc.querySelector("[data-add-to-cart]").dataset.variant;
    const label = doc.querySelector('[data-option-label="Colour"]').textContent;
    const url = win.location.search;
    close();
    return [opts.length > 2 && before !== after && label === opts[2].dataset.value && url.includes("variant="), `${opts.length} colours; picked "${label}", variant and URL updated`];
  },
  "live-price": async () => {
    const { doc, close } = await open("/products/micro-sprite-kids-scooter/");
    await until(() => doc.querySelector("[data-product]").dataset.live === "1");
    close();
    return [true, "price and stock refreshed from the NZ Storefront API"];
  },
  "complete-set": async () => {
    const { doc, close } = await open("/products/micro-sprite-kids-scooter/");
    const box = doc.querySelector('[data-feature="complete-set"]');
    await until(() => !box.hidden);
    const n = box.querySelectorAll(".mini-item").length;
    close();
    return [n > 0, `${n} add-ons suggested`];
  },
  cart: async () => {
    const { doc, close } = await open("/products/mini-micro-deluxe-3-wheel-scooter/");
    const btn = doc.querySelector("[data-add-to-cart]");
    if (btn.disabled) { close(); return [false, "test product sold out"]; }
    btn.click();
    const drawer = doc.getElementById("cart");
    await until(() => !drawer.hidden && drawer.querySelector(".cart-line"), 15000);
    const count = doc.querySelector("[data-cart-count]").textContent;
    const checkout = doc.querySelector("[data-checkout]").href;
    drawer.querySelector('[data-qty="1"]').click();
    await until(() => doc.querySelector("[data-cart-count]").textContent === String(Number(count) + 1), 15000);
    drawer.querySelector("[data-remove]").click();
    await until(() => !drawer.querySelector(".cart-line") || doc.querySelector("[data-cart-count]").textContent !== String(Number(count) + 1), 15000);
    close();
    return [/microscooters\.co\.nz\/cart\/c\//.test(checkout), `added, quantity +1, removed; checkout goes to ${checkout.slice(0, 48)}…`];
  },
  "spares-finder": async () => {
    const { doc, win, close } = await open("/pages/spares-finder/");
    const tabs = doc.querySelectorAll("[data-finder-tabs] .tab");
    tabs[2].click();
    const tabOk = !doc.getElementById(tabs[2].dataset.tab).hidden;
    const input = doc.querySelector("[data-finder-search]");
    input.value = "sprite"; input.dispatchEvent(new win.Event("input", { bubbles: true }));
    const shown = [...doc.querySelectorAll(".model-tile")].filter((t) => !t.hidden).map((t) => t.dataset.model);
    input.value = "qqqq"; input.dispatchEvent(new win.Event("input", { bubbles: true }));
    const empty = !doc.querySelector("[data-finder-empty]").hidden;
    close();
    return [tabOk && shown.length >= 2 && shown.every((m) => m.includes("sprite")) && empty, `tabs switch; "sprite" → ${shown.join(", ")}; no-match message shown`];
  },
  "parts-filter": async () => {
    const { doc, win, close } = await open("/collections/micro-sprite-scooter-spare-parts/?pt=wheels");
    await until(() => doc.querySelector("[data-collection]").dataset.ready);
    const cat = await win.MicroApp.catalogue();
    const cards = [...doc.querySelectorAll("[data-grid] .card")];
    const all = JSON.parse(doc.querySelector("[data-collection]").dataset.collection).length;
    const ok = cards.length > 0 && cards.length < all && cards.every((c) => cat.byHandle[c.dataset.h].pt === "wheels");
    const chip = doc.querySelector('[data-pt-link="brakes"]'); chip.click();
    const brakes = [...doc.querySelectorAll("[data-grid] .card")].every((c) => cat.byHandle[c.dataset.h].pt === "brakes");
    close();
    return [ok && brakes, `deep link ?pt=wheels shows ${cards.length} of ${all} parts; brakes chip switches filter`];
  },
  quiz: async () => {
    const { doc, close } = await open("/pages/your-best-micro-scooter/");
    await until(() => doc.querySelector("[data-quiz]").dataset.ready);
    const step = () => [...doc.querySelectorAll(".quiz__step")].find((s) => !s.hidden);
    const answer = (vals) => { const st = step(); vals.forEach((v) => st.querySelector(`input[value="${v}"]`).closest("label").click()); st.querySelector("[data-quiz-next]").click(); };
    const disabledAtStart = step().querySelector("[data-quiz-next]").disabled;
    answer(["kids"]); answer(["3"]); answer(["led"]); answer(["home"]); answer(["300"]);
    const res = doc.querySelector("[data-quiz-results]");
    const picks = [...res.querySelectorAll("[data-pick]")].map((p) => p.dataset.pick);
    const cat = await doc.defaultView.MicroApp.catalogue();
    const right = picks.length && cat.byHandle[picks[0]].s.wheels === "3 wheels" && cat.byHandle[picks[0]].s.led;
    const shown = !res.hidden;
    doc.querySelector("[data-quiz-restart]").click();
    const reset = !step() || step().dataset.id === "age";
    close();
    const checks = { disabledAtStart, shown, three: picks.length === 3, right: !!right, reset };
    const bad = Object.keys(checks).filter((k) => !checks[k]);
    return [!bad.length, `kids / 3 wheels / light-up / home / $300 → ${picks.join(", ")}; restart resets` + (bad.length ? `; failed: ${bad.join(", ")}` : "")];
  },
  "search-page": async () => {
    const { doc, close } = await open("/search/?q=helmet");
    await until(() => doc.querySelectorAll("[data-search-products] .card").length);
    const n = doc.querySelectorAll("[data-search-products] .card").length;
    const status = doc.querySelector("[data-search-status]").textContent;
    close();
    return [n > 0, status];
  },
};

export async function run(only) {
  const out = [];
  for (const [id, fn] of Object.entries(tests)) {
    if (only && !only.includes(id)) continue;
    const t0 = performance.now();
    try { const [ok, detail] = await fn(); out.push({ id, ok: !!ok, detail, ms: Math.round(performance.now() - t0) }); }
    catch (e) { out.push({ id, ok: false, detail: "error: " + e.message, ms: Math.round(performance.now() - t0) }); }
  }
  const app = (document.querySelector('script[src*="app.js"]').getAttribute("src").match(/v=([0-9a-f]+)/) || [])[1];
  const report = { when: new Date().toISOString(), where: location.origin + BASE + " (" + navigator.userAgent.match(/(Chrome|Safari|Firefox)\/[\d.]+/)?.[0] + ")", app, tests: out };
  if (!only) await fetch("/__selftest", { method: "POST", body: JSON.stringify(report, null, 1) });
  return report;
}
