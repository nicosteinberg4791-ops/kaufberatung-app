// Hülle der Startseite (app/finder/finder-app.js): alte Ratgeber-Sprungmarken führen auf ratgeber.html, Finder-Zustand
// (#k=…) und die eigene Sprungmarke #inhalt bleiben. Aufruf: node --test tests/test_finder_app.mjs
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const QUELLE = fs.readFileSync(path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "app", "finder", "finder-app.js"), "utf8");

function lauf(hash) {
  const ziele = [], hoerer = {};
  const ort = { hash, replace: u => ziele.push(u) };
  const kontext = {
    location: ort, navigator: {}, console,
    window: { addEventListener: (t, f) => { (hoerer[t] = hoerer[t] || []).push(f); } },
    document: { readyState: "complete", addEventListener() {}, getElementById: () => null },
  };
  vm.createContext(kontext);
  vm.runInContext(QUELLE, kontext);
  return { ziele, ort, hashchange: h => { ort.hash = h; for (const f of hoerer.hashchange || []) f(); } };
}

test("Ratgeber-Sprungmarken werden umgeleitet", () => {
  for (const h of ["#preiswecker", "#besitzer", "#kein-besitzer", "#tv-empfehlung"]) {
    assert.deepEqual(lauf(h).ziele, ["ratgeber.html" + h], h);
  }
});

test("Finder-Zustand, leere Adresse und #inhalt bleiben", () => {
  for (const h of ["", "#k=fernseher&s=ergebnis&b=700", "#inhalt", "#<script>"]) {
    assert.deepEqual(lauf(h).ziele, [], h);
  }
});

test("Hash-Wechsel in der offenen Seite leitet ebenfalls um", () => {
  const l = lauf("#k=airfryer&s=budget");
  l.hashchange("#inhalt");
  assert.deepEqual(l.ziele, []);
  l.hashchange("#preiswecker");
  assert.deepEqual(l.ziele, ["ratgeber.html#preiswecker"]);
});
