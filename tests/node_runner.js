// Runs the jsc-style engine tests under Node (used in GitHub Actions):
//   node tests/node_runner.js tests/stub.js assets/app.js tests/engine_test.js -- <catalogue.json> <quiz.json>
const fs = require("fs"), vm = require("vm");
const argv = process.argv.slice(2), cut = argv.indexOf("--");
globalThis.readFile = (p) => fs.readFileSync(p, "utf8");
globalThis.print = (...a) => console.log(...a);
vm.runInThisContext("var arguments = " + JSON.stringify(argv.slice(cut + 1)) + ";");
argv.slice(0, cut).forEach((f) => vm.runInThisContext(fs.readFileSync(f, "utf8"), { filename: f }));
