// Minimal browser stubs so app.js can load in jsc (JavaScriptCore) for engine tests.
var window = this;
window.MICRO = { base: "/micro-uk", store: "https://www.microscooters.co.nz", api: "2026-01", okendo: "x", freeShip: 100, catalogue: "c", content: "i" };
var document = { readyState: "loading", addEventListener: function () {}, querySelector: function () { return null; }, querySelectorAll: function () { return []; }, documentElement: { setAttribute: function () {} } };
var localStorage = { getItem: function () { return null; }, setItem: function () {}, removeItem: function () {} };
var location = { search: "", href: "https://x/", pathname: "/" };
var URLSearchParams = function () { this.get = function () { return null; }; };
