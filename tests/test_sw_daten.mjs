// Service Worker (app/sw.js): eine beschädigte finder-daten.json ersetzt die letzte brauchbare Cachekopie nicht (Codex r1 F-08).
// Aufruf: node --test tests/test_sw_daten.mjs
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HIER = path.dirname(fileURLToPath(import.meta.url));
const PROJEKT = path.resolve(HIER, "..");
const BEISPIEL = fs.readFileSync(path.join(HIER, "vorlagen", "finder-beispiel.json"), "utf8");

function swStarten(antwort) {
  const quelle = fs.readFileSync(path.join(PROJEKT, "app", "sw.js"), "utf8")
    .replace('"__VERSION__"', '"test"').replace("__DATEIEN__", "[]");
  const speicher = new Map(), handler = {}, geladen = [];
  const kontext = {
    console, URL, Response, Request, AbortController, setTimeout, clearTimeout, JSON,
    caches: { open: async () => ({ put: async (n, r) => { speicher.set(n, await r.text()); },
      match: async n => (speicher.has(n) ? new Response(speicher.get(n)) : undefined) }), keys: async () => [] },
    fetch: async () => antwort(),
  };
  kontext.self = { addEventListener: (t, f) => { handler[t] = f; }, location: { origin: "https://beispiel.invalid" } };
  kontext.location = kontext.self.location;
  kontext.importScripts = url => {
    geladen.push(url);
    vm.runInContext(fs.readFileSync(path.join(PROJEKT, "app", "finder", "bewertung.js"), "utf8"), kontext);
  };
  vm.createContext(kontext);
  vm.runInContext(quelle, kontext);
  const holen = async () => {
    let p = null;
    handler.fetch({ request: { method: "GET", url: "https://beispiel.invalid/finder-daten.json" }, respondWith: x => { p = x; } });
    return (await p).text();
  };
  return { speicher, holen, geladen };
}

test("F-08: gültige Datei ersetzt die Kopie, beschädigte (null in felder, Klassengrenze als Text, HTML) nicht", async () => {
  let aktuell = BEISPIEL;
  const sw = swStarten(() => new Response(aktuell, { status: 200 }));
  assert.deepEqual(sw.geladen, ["bewertung.js?v=test"]);
  assert.equal(await sw.holen(), BEISPIEL);
  assert.equal(sw.speicher.get("finder-daten.json"), BEISPIEL);
  const kaputt1 = JSON.parse(BEISPIEL); kaputt1.kategorien[0].felder.push(null);
  const kaputt2 = JSON.parse(BEISPIEL); kaputt2.regeln.klassen[0].ab = "0;background:red";
  const kaputt3 = JSON.parse(BEISPIEL); kaputt3.stand = { toString: null };   // R2-03
  for (const k of [JSON.stringify(kaputt1), JSON.stringify(kaputt2), JSON.stringify(kaputt3), "<html>Fehler</html>"]) {
    aktuell = k;
    assert.equal(await sw.holen(), BEISPIEL, "liefert den letzten brauchbaren Stand");
    assert.equal(sw.speicher.get("finder-daten.json"), BEISPIEL, "Cachekopie bleibt");
  }
});
