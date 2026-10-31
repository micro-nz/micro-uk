// Exhaustive tests for the quiz and comparison engines in assets/app.js, run in JavaScriptCore:
//   jsc tests/stub.js assets/app.js tests/engine_test.js -- dist/assets/catalogue.json tests/.quiz.json
var cat = JSON.parse(readFile(arguments[0]));
var cfg = JSON.parse(readFile(arguments[1]));
cat.byHandle = {}; cat.forEach(function (x) { cat.byHandle[x.h] = x; });
var Q = window.MicroApp.Quiz, C = window.MicroApp.Compare, pools = cfg.pools;
var fails = [], combos = 0, relaxed = 0, soldOutOnly = 0, under3 = 0;
function fail(msg, a) { if (fails.length < 40) fails.push(msg + " :: " + JSON.stringify(a)); else fails.length++; }
var step = function (id) { return cfg.steps.filter(function (s) { return s.id === id; })[0]; };
var ages = step("age").options.map(function (o) { return o.v; });
ages.forEach(function (age) {
  var pool = Q.pool(age, cat, pools);
  if (pool.length < 3) fail("pool too small for " + age + ": " + pool.length, {});
  // the UI only offers options the pool can satisfy (mirrors prepare() in initQuiz)
  var styles = step("style").options.filter(function (o) { return o.ages.indexOf(age) > -1 && (o.v === "any" || pool.some(function (x) { return Q.style(x, o.v); })); }).map(function (o) { return o.v; });
  var feats = step("f").options.filter(function (o) { return pool.some(function (x) { return x.a && Q.has(x, o.v); }); }).map(function (o) { return o.v; });
  var uses = [undefined].concat(step("use").options.filter(function (o) { return o.ages.indexOf(age) > -1; }).map(function (o) { return o.v; }));
  var fsets = [[]]; feats.forEach(function (a, i) { fsets.push([a]); feats.slice(i + 1).forEach(function (b) { fsets.push([a, b]); }); });
  styles.forEach(function (style) { fsets.forEach(function (f) { uses.forEach(function (use) { step("budget").options.forEach(function (b) {
    var a = { age: age, style: style, f: f, use: use, budget: b.v }; combos++;
    var r = Q.recommend(a, cat, pools);
    if (!r.picks.length) return fail("no picks", a);
    if (r.picks.length < 3) { under3++; if (!r.more.length && pool.filter(function (x) { return x.a; }).length > r.picks.length) fail("few picks and no alternatives", a); }
    var hard = r.notes.filter(function (n) { return !/^Only \d/.test(n); });
    if (hard.length) relaxed++;
    var sold = r.notes.some(function (n) { return /sold out/.test(n); }); if (sold) soldOutOnly++;
    var budget = b.v === "any" ? Infinity : Number(b.v);
    var hs = {};
    r.picks.forEach(function (o) {
      var x = o.x;
      if (hs[x.h]) fail("duplicate pick " + x.h, a); hs[x.h] = 1;
      if (pool.indexOf(x) < 0) fail("pick outside age pool: " + x.t, a);
      if (["scooters", "ride-ons", "luggage"].indexOf(x.cat) < 0) fail("non-scooter pick: " + x.t, a);
      if (!x.a && !sold) fail("sold-out pick without note: " + x.t, a);
      if (!hard.length && style !== "any" && !Q.style(x, style)) fail("style not honoured: " + x.t, a);
      if (!hard.length && x.p > budget) fail("over budget without note: " + x.t + " " + x.p, a);
      o.why.forEach(function (w) { if (w.t.indexOf("undefined") > -1) fail("bad reason text: " + w.t, a); });
      f.forEach(function (k) {
        var claim = o.why.filter(function (w) { return w.t === Q.FEAT[k][0] || w.t === Q.FEAT[k][1]; })[0];
        if (!claim || claim.ok !== Q.has(x, k)) fail("reason flag wrong for " + k + " on " + x.t, a);
      });
    });
    // a pick that misses a wanted feature must not outrank an available, in-style, in-budget item that has all of them
    if (f.length && !hard.length) {
      var full = pool.filter(function (x) { return x.a && (style === "any" || Q.style(x, style)) && x.p <= budget && f.every(function (k) { return Q.has(x, k); }); });
      if (full.length && !f.every(function (k) { return Q.has(r.picks[0].x, k); })) fail("top pick misses a feature another product has: " + r.picks[0].x.t, a);
    }
    // variety: distinct families when the candidate set allows it
    var fams = r.picks.map(function (o) { return Q.family(o.x); });
    var distinctAvail = {}; pool.filter(function (x) { return x.a && (style === "any" || Q.style(x, style)) && x.p <= budget; }).forEach(function (x) { distinctAvail[Q.family(x)] = 1; });
    var want = Math.min(3, Object.keys(distinctAvail).length);
    var got = {}; fams.forEach(function (f2) { got[f2] = 1; });
    if (!hard.length && Object.keys(got).length < want) fail("picks not varied: " + fams.join(" | "), a);
  }); }); }); });
});
// spot checks
function top(a) { return Q.recommend(a, cat, pools).picks.map(function (o) { return o.x; }); }
var t1 = top({ age: "toddler", style: "3", f: ["led"], budget: "any" });
if (!t1.length || !t1[0].s.led || t1[0].s.wheels !== "3 wheels") fail("toddler 3-wheel LED top pick wrong", t1[0] && t1[0].t);
var t2 = top({ age: "adult", style: "stunt", f: [], budget: "any" });
if (!t2.every(function (x) { return x.col.indexOf("freestyle-scooters") > -1; })) fail("adult stunt picks not all stunt", t2.map(function (x) { return x.t; }));
var t3 = top({ age: "kids", style: "2", f: ["foldable"], budget: "250" });
if (!t3.every(function (x) { return x.s.wheels === "2 wheels" && x.p <= 250; })) fail("kids 2-wheel <=250 wrong", t3.map(function (x) { return x.t + " " + x.p; }));
var t4 = top({ age: "toddler", style: "bike", f: [], budget: "any" });
if (!t4.every(function (x) { return /Balance bike|Tricycle/.test(x.s.wheels); })) fail("toddler bike picks wrong", t4.map(function (x) { return x.t; }));

// comparison engine
var comparable = cat.filter(function (x) { return x.s && x.s.wheels && (x.cat === "scooters" || x.cat === "ride-ons"); });
var cmpFails = 0;
for (var i = 0; i + 2 < comparable.length; i++) {
  var sel = [comparable[i], comparable[i + 1], comparable[i + 2]];
  var html = C.table(comparable, sel, "t");
  ["Price", "Suits", "Wheels", "Availability", "Colours"].forEach(function (row) { if (html.indexOf(">" + row + "</th>") < 0) { cmpFails++; fail("compare row missing: " + row, sel.map(function (x) { return x.h; })); } });
  sel.forEach(function (x, j) { if (html.indexOf('value="' + x.h + '" selected') < 0) { cmpFails++; fail("compare select not set", x.h); } });
  if ((html.match(/<option /g) || []).length !== comparable.length * 3) { cmpFails++; fail("compare options count", (html.match(/<option /g) || []).length); }
  if (/undefined|NaN|null/.test(html.replace(/data-okendo="[^"]*"/g, ""))) { cmpFails++; fail("compare renders undefined/NaN", sel.map(function (x) { return x.h; })); }
  var rows = html.split("<tr").length - 2;
  if (rows < 8) { cmpFails++; fail("compare too few rows", rows); }
}
var allNl = C.table(comparable, [comparable[0], comparable[0], comparable[0]], "t");
print(JSON.stringify({ quiz_combinations: combos, relaxed: relaxed, sold_out_fallbacks: soldOutOnly, fewer_than_3_picks: under3,
  compare_tables: comparable.length - 2, comparable_products: comparable.length, failures: fails.length }));
fails.slice(0, 40).forEach(function (f) { print("FAIL " + f); });
