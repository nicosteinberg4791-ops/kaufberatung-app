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
  return { speicher, holen, geladen, kontext };
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
  const kaputt4 = JSON.parse(BEISPIEL); kaputt4.kategorien[0].id = "constructor";   // R3-02
  kaputt4.kategorien[0].felder.find(x => x.gewicht > 0).id = "prototype";
  for (const k of [JSON.stringify(kaputt1), JSON.stringify(kaputt2), JSON.stringify(kaputt3), JSON.stringify(kaputt4), "<html>Fehler</html>"]) {
    aktuell = k;
    assert.equal(await sw.holen(), BEISPIEL, "liefert den letzten brauchbaren Stand");
    assert.equal(sw.speicher.get("finder-daten.json"), BEISPIEL, "Cachekopie bleibt");
  }
});

test("R4-07: beschädigter Wunschpreis-Cache (__proto__) wiederholt dieselbe Preisalarm-Meldung nicht", async () => {
  const preise = JSON.stringify({ preise: { lg_c6elb: { name: "LG", aktuell: { gesamt: 90 } } } })
    .replace('{"preise":{', '{"preise":{"__proto__":{"name":"X","aktuell":{"gesamt":100}},');
  const sw = swStarten(() => new Response(preise, { status: 200, headers: { "Content-Type": "application/json" } }));
  const k = sw.kontext, Basis = Request;
  k.Request = class extends Basis { constructor(u, o) { super(new URL(u, "https://beispiel.invalid/"), o); } };
  k.Notification = { permission: "granted" }; k.self.Notification = k.Notification;
  const meldungen = [];
  k.self.registration = { showNotification: async t => { meldungen.push(t); } };
  sw.speicher.set("wunsch.json", '{"__proto__": {"preis": 200}, "lg_c6elb": {"preis": 95}}');
  const pruefe = vm.runInContext("pruefePreise", k);
  await pruefe();
  await pruefe();
  assert.equal(meldungen.length, 1, "Treffer wird genau einmal gemeldet");
  assert.match(meldungen[0], /LG/);
  assert.deepEqual(Object.keys(JSON.parse(sw.speicher.get("gemeldet.json"))), ["lg_c6elb"]);
});
