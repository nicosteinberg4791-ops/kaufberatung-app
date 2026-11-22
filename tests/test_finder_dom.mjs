// Rauchtest der Oberfläche app/finder/finder.js mit einem kleinen DOM-Ersatz (kein Browser, nur eingebaute Module).
// Prüft Abläufe (Kategorie → Budget → Fragen → Ergebnis, Adresse, Vergleich, Budget ändern) und dass Daten nur als Text landen.
// Aufruf: node --test tests/test_finder_dom.mjs
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const HIER = path.dirname(fileURLToPath(import.meta.url));
const ORDNER = path.resolve(HIER, "..", "app", "finder");
const BEISPIEL = fs.readFileSync(path.join(HIER, "vorlagen", "finder-beispiel.json"), "utf8");

// ---- DOM-Ersatz: nur, was finder.js benutzt ----
class Knoten {
  constructor(typ) { this.nodeType = typ; this.childNodes = []; this.parentNode = null; }
  get firstChild() { return this.childNodes[0] || null; }
  appendChild(k) { if (k.parentNode) k.parentNode.removeChild(k); k.parentNode = this; this.childNodes.push(k); return k; }
  removeChild(k) { const i = this.childNodes.indexOf(k); if (i >= 0) this.childNodes.splice(i, 1); k.parentNode = null; return k; }
  get textContent() { return this.nodeType === 3 ? this.daten : this.childNodes.map(k => k.textContent).join(""); }
  set textContent(t) { if (this.nodeType === 3) { this.daten = String(t); return; } this.childNodes = []; if (t !== "") this.appendChild(new Text(String(t))); }
}
class Text extends Knoten { constructor(t) { super(3); this.daten = t; } }
class Element extends Knoten {
  constructor(tag, dok) { super(1); this.tagName = tag.toUpperCase(); this.attr = {}; this.hoerer = {}; this.dok = dok; this.value = ""; this.checked = false; this.disabled = false; this.hidden = false; }
  set innerHTML(v) { throw new Error("innerHTML benutzt"); }
  setAttribute(k, v) { this.attr[k] = String(v); if (k === "value") this.value = String(v); if (k === "checked") this.checked = true; if (k === "disabled") this.disabled = true; }
  getAttribute(k) { return k in this.attr ? this.attr[k] : null; }
  removeAttribute(k) { delete this.attr[k]; }
  set className(v) { this.attr.class = v; } get className() { return this.attr.class || ""; }
  get id() { return this.attr.id || ""; }
  get classList() { const e = this; return { add: c => { e.className = (e.className + " " + c).trim(); }, contains: c => e.className.split(/\s+/).includes(c) }; }
  addEventListener(t, f) { (this.hoerer[t] = this.hoerer[t] || []).push(f); }
  ausloesen(t) { for (const f of this.hoerer[t] || []) f({ target: this, preventDefault() {} }); }
  focus() { this.dok.activeElement = this; }
  scrollIntoView() {}
}
function neuesDokument() {
  const dok = { activeElement: null, title: "" };
  dok.createElement = t => new Element(t, dok);
  dok.createElementNS = (ns, t) => new Element(t, dok);
  dok.createTextNode = t => new Text(String(t));
  dok.body = new Element("body", dok);
  dok.getElementById = id => alle(dok.body).find(e => e.id === id) || null;
  for (const id of ["inhalt", "datenstand", "ablage", "m-kappung"]) { const e = dok.createElement(id === "inhalt" ? "main" : "div"); e.setAttribute("id", id); dok.body.appendChild(e); }
  return dok;
}
function alle(k, l = []) { for (const c of k.childNodes) if (c.nodeType === 1) { l.push(c); alle(c, l); } return l; }
const text = k => k.textContent.replace(/\s+/g, " ");
const knopf = (dok, t) => alle(dok.body).find(e => e.tagName === "BUTTON" && text(e).includes(t));
const warte = () => new Promise(r => setTimeout(r, 10));

async function starte(hash = "", daten = BEISPIEL, preise = null) {
  const dok = neuesDokument();
  const ort = { hash, pathname: "/", search: "", reload() {} };
  const geschichte = { eintraege: 0, pushState(s, t, u) { this.eintraege++; ort.hash = String(u).startsWith("#") ? u : ""; }, replaceState(s, t, u) { ort.hash = String(u).startsWith("#") ? u : ""; } };
  const hoerer = {};
  const fenster = {
    addEventListener: (t, f) => { (hoerer[t] = hoerer[t] || []).push(f); },
    matchMedia: () => ({ matches: false }), scrollTo() {},
  };
  const kontext = {
    window: fenster, document: dok, location: ort, history: geschichte, URL, URLSearchParams, console, setTimeout,
    fetch: async url => {
      if (url === "finder-daten.json") return daten === null ? { ok: false, status: 404 } : { ok: true, json: async () => JSON.parse(daten) };
      if (url === "finder-preise.json" && preise) return { ok: true, json: async () => preise };
      return { ok: false, status: 404 };
    },
  };
  fenster.KBBewertung = undefined;
  vm.createContext(kontext);
  kontext.self = kontext.window;
  vm.runInContext(fs.readFileSync(path.join(ORDNER, "bewertung.js"), "utf8"), kontext);
  kontext.window.KBBewertung = kontext.self.KBBewertung;
  vm.runInContext(fs.readFileSync(path.join(ORDNER, "finder.js"), "utf8"), kontext);
  await warte();
  return { dok, ort, geschichte, zurueck: async h => { ort.hash = h; for (const f of hoerer.popstate || []) f(); await warte(); } };
}

test("Quelltext: kein innerHTML, Links nur mit noopener noreferrer", () => {
  const js = fs.readFileSync(path.join(ORDNER, "finder.js"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
  assert.equal(/innerHTML|outerHTML|insertAdjacentHTML|document\.write/.test(js), false);
  assert.match(js, /rel: "noopener noreferrer"/);
  assert.equal(/<script[^>]+src="https?:/i.test(fs.readFileSync(path.join(ORDNER, "index.html"), "utf8")), false);
});

test("Ablauf Fernseher: Kacheln → Budget → Fragen → Ergebnis mit Empfehlung und Aufpreis-Hinweis", async () => {
  const { dok, ort, geschichte } = await starte();
  const kacheln = alle(dok.body).filter(e => e.className.includes("kachel") && e.tagName === "BUTTON");
  assert.equal(kacheln.length, 14);
  assert.ok(text(dok.body).includes("Wohnzimmer"));
  kacheln.find(e => text(e).includes("Fernseher")).ausloesen("click");
  assert.match(ort.hash, /k=fernseher/);
  assert.ok(text(dok.body).includes("Wie viel möchtest du höchstens ausgeben?"));
  assert.ok(text(dok.body).includes("Welche Größe soll er haben?"));
  knopf(dok, "bis 600 €").ausloesen("click");
  assert.match(ort.hash, /b=600/);
  assert.equal(knopf(dok, "bis 600 €").getAttribute("aria-pressed"), "true");
  knopf(dok, "Weiter zu den Fragen").ausloesen("click");
  assert.ok(text(dok.body).includes("Wofür nutzt du den Fernseher meistens?"));
  const egal = alle(dok.body).filter(e => e.tagName === "INPUT" && e.attr.type === "radio" && e.checked);
  assert.equal(egal.length, 4, "jede Frage hat eine sichtbare Vorauswahl");
  const spiele = alle(dok.body).find(e => e.id === "frage-zweck-spiele");
  spiele.checked = true; spiele.ausloesen("change");
  assert.match(ort.hash, /a=zweck\.spiele/);
  knopf(dok, "Ergebnis zeigen").ausloesen("click");
  const t = text(dok.body);
  assert.ok(t.includes("Unsere Empfehlung bis 600 €"), t.slice(0, 400));
  assert.ok(t.includes("aus Datenblatt"));
  assert.ok(t.includes("Zum Angebot"));
  assert.ok(t.includes("Alle passenden Modelle"));
  const angebot = alle(dok.body).find(e => e.tagName === "A" && text(e) === "Zum Angebot");
  assert.equal(angebot.getAttribute("rel"), "noopener noreferrer");
  assert.equal(angebot.getAttribute("target"), "_blank");
  assert.ok(angebot.getAttribute("href").startsWith("https://example.org/"));
  assert.ok(geschichte.eintraege >= 3);
});

test("Ergebnis aus der Adresse, Budget ändern ohne Neuaufbau, Vergleich, Sortierung", async () => {
  const { dok, ort } = await starte("#k=fernseher&s=ergebnis&b=500");
  let t = text(dok.body);
  assert.ok(t.includes("Für 140 € mehr bekommst du +16 Punkte (Klasse „gut“ statt „ordentlich“)."), t.slice(0, 600));
  const feld = dok.getElementById("budget-fernseher-oben");
  assert.ok(feld);
  feld.focus(); feld.value = "1500"; feld.ausloesen("input");
  assert.equal(dok.getElementById("budget-fernseher-oben"), feld, "Eingabefeld bleibt dasselbe Element");
  assert.equal(dok.activeElement, feld);
  assert.match(ort.hash, /b=1500/);
  t = text(dok.body);
  assert.ok(t.includes("Unsere Empfehlung bis 1.500 €"));
  // zwei Modelle vergleichen
  const schalter = alle(dok.body).filter(e => e.tagName === "INPUT" && e.attr.type === "checkbox" && e.id.startsWith("vgl-rang-"));
  schalter[0].checked = true; schalter[0].ausloesen("change");
  let s2 = alle(dok.body).filter(e => e.tagName === "INPUT" && e.attr.type === "checkbox" && e.id.startsWith("vgl-rang-"));
  s2[1].checked = true; s2[1].ausloesen("change");
  assert.match(ort.hash, /v=[a-z0-9-]+~[a-z0-9-]+/);
  t = text(dok.body);
  assert.ok(t.includes("2 von 3 zum Vergleich"));
  assert.ok(alle(dok.body).some(e => e.className.includes("vgl-wert vorn")), "gewonnene Felder hervorgehoben");
  assert.equal(dok.getElementById("ablage").hidden, false);
  // Sortierung nach Preis
  const preis = alle(dok.body).find(e => e.tagName === "INPUT" && e.attr.name === "sortierung" && e.attr.value === "preis");
  preis.checked = true; preis.ausloesen("change");
  assert.match(ort.hash, /o=preis/);
  const preise = alle(dok.body).filter(e => e.className === "rang-preis").map(e => text(e));
  const zahlen = preise.filter(p => p !== "–").map(p => Number(p.replace(/[^\d,]/g, "").replace(",", ".")));
  assert.deepEqual(zahlen, zahlen.slice().sort((a, b) => a - b));
  // Egal-Budget: kein Aufpreis-Hinweis
  knopf(dok, "Egal").ausloesen("click");
  assert.equal(text(dok.body).includes("mehr bekommst du"), false);
  assert.equal(/b=/.test(ort.hash), false);
});

test("Zurück-Knopf des Browsers stellt den Schritt wieder her", async () => {
  const app = await starte("#k=airfryer&s=ergebnis&b=100");
  assert.ok(text(app.dok.body).includes("Air Fryer"));
  await app.zurueck("#k=airfryer&s=fragen&b=100");
  assert.ok(text(app.dok.body).includes("Für wie viele Personen kochst du meistens?"));
  await app.zurueck("");
  assert.ok(text(app.dok.body).includes("Was suchst du?"));
});

test("Budget aus der Adresse im Ergebnis: Feld und Schnellwahl ziehen nach (Browserbefund 21.11.)", async () => {
  const app = await starte("#k=fernseher&s=ergebnis&b=500");
  const feld = app.dok.getElementById("budget-fernseher-oben");
  assert.equal(feld.value, "500");
  await app.zurueck("#k=fernseher&s=ergebnis&b=1500");
  assert.equal(app.dok.getElementById("budget-fernseher-oben"), feld, "Feld bleibt dasselbe Element");
  assert.equal(feld.value, "1500", "Eingabefeld zeigt das Budget aus der Adresse");
  assert.ok(text(app.dok.body).includes("Unsere Empfehlung bis 1.500 €"));
  const gedrueckt = alle(app.dok.body).filter(e => e.getAttribute("aria-pressed") === "true" && e.getAttribute("data-budget"));
  assert.ok(gedrueckt.every(e => e.getAttribute("data-budget") === "1500"), "keine alte Schnellwahl bleibt markiert");
});

test("Leere Kategorie, Ladefehler, ungültige Adresse", async () => {
  const leer = await starte("#k=laptop");
  assert.ok(text(leer.dok.body).includes("Hier kommen bald Modelle."));
  const kaputt = await starte("#k=<script>&b=-5&v=x~y");
  assert.ok(text(kaputt.dok.body).includes("Was suchst du?"));
  const fehler = await starte("", null);
  assert.ok(text(fehler.dok.body).includes("nicht laden"));
  const muell = await starte("", "{\"kein\":\"format\"}");
  assert.ok(text(muell.dok.body).includes("beschädigt"));
});

test("Fremde Texte bleiben Text; nur https-Links; aktuelle Preise überlagern", async () => {
  const d = JSON.parse(BEISPIEL);
  const af = d.kategorien.find(k => k.id === "airfryer");
  af.modelle[0].name = "<img src=x onerror=alert(1)>";
  af.modelle[1].preis.url = "javascript:alert(1)";
  const id = af.modelle[2].id;
  const app = await starte("#k=airfryer&s=ergebnis", JSON.stringify(d), { stand: "2026-11-21", preise: { [id]: { eur: 77, haendler: "Neu-Shop", url: "https://example.org/neu", stand: "2026-11-21" } } });
  const t = text(app.dok.body);
  assert.ok(t.includes("<img src=x onerror=alert(1)>"), "als Text sichtbar, nicht als Element");
  assert.equal(alle(app.dok.body).some(e => e.tagName === "IMG"), false);
  assert.equal(alle(app.dok.body).some(e => e.tagName === "A" && /^javascript:/i.test(e.getAttribute("href") || "")), false);
  assert.ok(t.includes("77 €"), "überlagerter Preis in der Rangliste");
});

// ---------- Codex r1 (Finder-Veröffentlichung) ----------
test("F-08/F-09: beschädigte Felder oder Klassengrenzen zeigen die Fehlermeldung statt abzubrechen", async () => {
  const d1 = JSON.parse(BEISPIEL); d1.kategorien[0].felder.push(null);
  const a = await starte("#k=fernseher&s=ergebnis", JSON.stringify(d1));
  assert.ok(text(a.dok.body).includes("beschädigt"));
  const d2 = JSON.parse(BEISPIEL); d2.regeln.klassen[0].ab = "0;background:red";
  const b = await starte("#k=fernseher&s=ergebnis", JSON.stringify(d2));
  assert.ok(text(b.dok.body).includes("beschädigt"));
  assert.equal(alle(b.dok.body).some(e => /background/.test(e.getAttribute("style") || "")), false);
});

test("F-10: Modell im Budget ohne Note wird als solches gezeigt, nicht „Im Budget passt nichts“", async () => {
  const d = JSON.parse(BEISPIEL);
  const af = d.kategorien.find(k => k.id === "airfryer");
  af.modelle[0].teilpunkte = {}; af.modelle[0].preis.eur = 10;
  const app = await starte("#k=airfryer&s=ergebnis&b=20", JSON.stringify(d));
  const t = text(app.dok.body);
  assert.equal(t.includes("Im Budget passt nichts"), false);
  assert.ok(t.includes("Modell ohne Note"), t.slice(0, 400));
  assert.ok(t.includes("Keine Note: zu wenig Daten"));
});
