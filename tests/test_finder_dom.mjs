// Rauchtest der Oberfläche app/finder/finder.js mit einem kleinen DOM-Ersatz (kein Browser, nur eingebaute Module).
// Prüft Abläufe (Kategorie → Budget → Fragen → Ergebnis, Adresse, Vergleich, Budget ändern) und dass Daten nur als Text landen.
// Aufruf: node --test tests/test_finder_dom.mjs
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

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
  get classList() {
    const e = this, hat = c => e.className.split(/\s+/).includes(c);
    return { add: c => { if (!hat(c)) e.className = (e.className + " " + c).trim(); }, contains: hat,
      toggle: (c, an) => { const soll = an === undefined ? !hat(c) : !!an; e.className = e.className.split(/\s+/).filter(x => x && x !== c).concat(soll ? [c] : []).join(" "); return soll; } };
  }
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

async function starte(hash = "", daten = BEISPIEL, preise = null, extra = {}) {
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
  // G1-04/G1-05: Proben können Fenster (matchMedia) und Kontext (IntersectionObserver) ersetzen
  Object.assign(fenster, extra.fenster || {});
  Object.assign(kontext, extra.kontext || {});
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

test("P1-02: „haupt“ ist nur noch Knopfstil, das Layout heißt .hauptspalte (Browserbefund 24.11., Codex P1-02)", () => {
  const css = fs.readFileSync(path.join(ORDNER, "finder.css"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
  // jeder Selektorteil mit der Klasse .haupt (Wortgrenze, nicht .rang-haupt/.hauptspalte) ist genau .knopf.haupt
  const selektoren = [...css.matchAll(/(^|\})([^{}]+)\{/g)].flatMap(m => m[2].split(",").map(x => x.trim()));
  const mitHaupt = selektoren.filter(x => /\.haupt(?![\w-])/.test(x));
  assert.ok(mitHaupt.length >= 1);
  for (const x of mitHaupt) assert.match(x, /^\.knopf\.haupt$/, "Selektor trifft mehr als den Knopf: " + x);
  assert.match(css, /(^|\})\s*\.leiste, \.hauptspalte, \.fuss \{[^}]*width: 100%/);
  assert.match(fs.readFileSync(path.join(ORDNER, "index.html"), "utf8"), /<main id="inhalt" class="hauptspalte"/);
  // in den Skripten steht „haupt“ als Klasse nur zusammen mit „knopf“ (Ablage, Angebotslink, Neu laden, Weiter)
  for (const datei of ["finder.js", "finder-app.js"]) {
    const js = fs.readFileSync(path.join(ORDNER, datei), "utf8");
    for (const m of js.matchAll(/(?:class(?:Name)?\s*[:=]\s*)"([^"]*)"/g)) {
      if (m[1].split(/\s+/).includes("haupt")) assert.ok(m[1].split(/\s+/).includes("knopf"), datei + ": " + m[1]);
    }
  }
  const text = (css.match(/\.ablage-text \{([^}]*)\}/) || [])[1] || "";
  assert.match(text, /white-space: nowrap/);
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
  assert.ok(t.includes("Passt am besten zu dir bis 600 €"), t.slice(0, 400));
  assert.ok(t.includes("aus dem Datenblatt, kein Test"));
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
  assert.ok(t.includes("Für 140 € mehr bekommst du +16 Punkte."), t.slice(0, 600));
  const feld = dok.getElementById("budget-fernseher-oben");
  assert.ok(feld);
  feld.focus(); feld.value = "1500"; feld.ausloesen("input");
  assert.equal(dok.getElementById("budget-fernseher-oben"), feld, "Eingabefeld bleibt dasselbe Element");
  assert.equal(dok.activeElement, feld);
  assert.match(ort.hash, /b=1500/);
  t = text(dok.body);
  assert.ok(t.includes("Passt am besten zu dir bis 1.500 €"));
  // zwei Modelle vergleichen
  // G1: Umschaltknopf mit aria-pressed statt Kontrollkästchen
  const schalter = alle(dok.body).filter(e => e.tagName === "BUTTON" && e.id.startsWith("vgl-rang-"));
  assert.ok(schalter.length >= 2 && schalter.every(e => e.getAttribute("aria-pressed") === "false"));
  assert.equal(alle(dok.body).some(e => e.tagName === "INPUT" && e.attr.type === "checkbox"), false, "kein Kontrollkästchen mehr");
  schalter[0].ausloesen("click");
  let s2 = alle(dok.body).filter(e => e.tagName === "BUTTON" && e.id.startsWith("vgl-rang-"));
  assert.equal(s2[0].getAttribute("aria-pressed"), "true");
  assert.ok(text(s2[0]).includes("Im Vergleich"));
  s2[1].ausloesen("click");
  assert.match(ort.hash, /v=[a-z0-9-]+~[a-z0-9-]+/);
  t = text(dok.body);
  assert.ok(t.includes("2 von 3 gewählt"));
  assert.ok(dok.body.classList.contains("mit-ablage"), "07 B12: Platz für die Ablage");
  assert.ok(alle(dok.body).some(e => /vgl-bahn farbe-\d vorn/.test(e.className)), "Bahn des Vorderen markiert");
  assert.ok(/Vorn: |gleichauf/.test(text(dok.getElementById("vergleich"))), "Marke je Merkmal");
  assert.equal(dok.getElementById("ablage").hidden, false);
  // Sortierung nach Preis
  const preis = alle(dok.body).find(e => e.tagName === "INPUT" && e.attr.name === "sortierung" && e.attr.value === "preis");
  preis.checked = true; preis.ausloesen("change");
  assert.match(ort.hash, /o=preis/);
  // sortiert wird die Rangliste; Modelle ohne Note stehen getrennt darunter (07 B10)
  const preise = alle(alle(dok.body).find(e => e.className === "rang")).filter(e => e.className === "rang-preis").map(e => text(e));
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
  assert.ok(text(app.dok.body).includes("Passt am besten zu dir bis 1.500 €"));
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
test("F-08/F-09: beschädigte Felder oder Spanne zeigen die Fehlermeldung statt abzubrechen", async () => {
  const d1 = JSON.parse(BEISPIEL); d1.kategorien[0].felder.push(null);
  const a = await starte("#k=fernseher&s=ergebnis", JSON.stringify(d1));
  assert.ok(text(a.dok.body).includes("beschädigt"));
  const d2 = JSON.parse(BEISPIEL); d2.regeln.datenblatt_abschlag.spanne_plus_minus = "0;background:red";
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
  // Statusansage entsteht bei Änderungen im eingehängten Schirm (Budget ändern ohne Neuaufbau)
  const feld = app.dok.getElementById("budget-airfryer-oben");
  feld.value = "25"; feld.ausloesen("input");
  const status = text(app.dok.getElementById("ergebnis-status"));
  assert.ok(status.includes("Modell ohne Note"), status);
  assert.equal(/–\s*Punkte|Punkte/.test(status), false, "R2-09: kein Punktetext ohne Note: " + status);
});

test("R2-03: Objekt statt Datum in stand zeigt die Fehlermeldung statt einer leeren Seite", async () => {
  const d = JSON.parse(BEISPIEL); d.stand = { toString: null };
  const a = await starte("#k=fernseher&s=ergebnis", JSON.stringify(d));
  assert.ok(text(a.dok.body).includes("beschädigt"), text(a.dok.body).slice(0, 200));
  const w = JSON.parse(BEISPIEL); w.kategorien[0].modelle[0].werte[w.kategorien[0].felder[0].id] = { toString: null };
  const b = await starte("#k=fernseher&s=ergebnis", JSON.stringify(w));
  assert.equal(text(b.dok.body).includes("beschädigt"), false);
  assert.ok(text(b.dok.body).length > 100, "Seite zeichnet trotz kaputtem Einzelwert");
});

test("R3-02: Kategorie constructor / Feld prototype zeigt die Fehlermeldung statt einer leeren Seite", async () => {
  const d = JSON.parse(BEISPIEL); d.kategorien[0].id = "constructor";
  const f = d.kategorien[0].felder.find(x => x.gewicht > 0); f.id = "prototype";
  const a = await starte("#k=constructor&s=ergebnis", JSON.stringify(d));
  assert.ok(text(a.dok.body).includes("beschädigt"), text(a.dok.body).slice(0, 200));
});

// ---------- P1 Sofortfixes (UX-Neuausrichtung, 24.11.2026) ----------
const klassen = (dok, k) => alle(dok.body).filter(e => e.className.split(/\s+/).includes(k));

test("P1/D12: keine Klassenwörter, keine Kappung, Preis vor der Note, Rechnung eingeklappt", async () => {
  const { dok } = await starte("#k=fernseher&s=ergebnis&b=500");
  const t = text(dok.body);
  for (const wort of ["sehr gut", "hervorragend", "ordentlich", "Unsere Empfehlung", "nur mit unabhängigem Test", "Klasse"]) {
    assert.equal(t.includes(wort), false, "kein „" + wort + "“");
  }
  assert.equal(klassen(dok, "skala-stufe").length + klassen(dok, "skala-test").length + klassen(dok, "rang-klasse").length, 0);
  const karte = klassen(dok, "empfehlung")[0];
  const reihenfolge = karte.childNodes.map(k => k.className);
  assert.ok(reihenfolge.indexOf("kauf") >= 0 && reihenfolge.indexOf("kauf") < reihenfolge.indexOf("note-block"), "08 F: Preis vor Note: " + reihenfolge);
  const details = alle(karte).find(e => e.tagName === "DETAILS");
  assert.ok(details && text(details).includes("So kommt die Note zustande"));
  // G1: Punktbahn mit Spanne steht sichtbar im Notenblock, nicht mehr in der eingeklappten Erklärung
  const block = klassen(dok, "note-block")[0];
  assert.ok(block.childNodes.some(e => e.className === "skala"), "Punktbahn sichtbar");
  assert.equal(alle(details).some(e => e.className === "skala"), false);
});

test("P1 07 B15/B10: gleiche angezeigte Note = gleicher Rang, ohne Note eigene Gruppe ohne Rang mit „fehlt“", async () => {
  const { dok } = await starte("#k=fernseher&s=ergebnis&b=500");
  const [bewertet, offen] = alle(dok.body).filter(e => e.className === "rang");
  // Beispieldaten: zwei Größen derselben Serie mit 56 Punkten, dann 41 und 39
  assert.deepEqual(alle(bewertet).filter(e => e.className === "rang-nr").map(e => text(e)), ["1", "1", "3", "4"]);
  assert.ok(text(dok.body).includes("Noch nicht bewertbar (1)"));
  assert.equal(alle(offen).filter(e => e.className === "rang-nr").length, 0, "keine Rangnummer");
  assert.ok(alle(offen).some(e => e.className.includes("ohne-nr")));
  assert.match(text(offen), /fehlt: /);
  assert.equal(text(dok.body).includes("zu wenig Daten für eine Note"), false);
});

test("P1 08 F: Deine Angaben mit Fragetext", async () => {
  const { dok } = await starte("#k=fernseher&s=ergebnis&b=600&g=50-55&a=zweck.spiele~ton.ja");
  const dt = alle(dok.body).filter(e => e.tagName === "DT").map(e => text(e));
  const dd = alle(dok.body).filter(e => e.tagName === "DD").map(e => text(e));
  assert.ok(dt.includes("Wofür nutzt du den Fernseher meistens?"), dt.join(" | "));
  assert.equal(dd[dt.indexOf("Wofür nutzt du den Fernseher meistens?")], "Spielkonsole oder PC");
  assert.equal(dd[dt.indexOf("Größe")], "50 bis 55 Zoll");
  assert.equal(dt.length, 3);
});

test("P1 08 G: ohne Preis keine Empfehlung, auch bei Budget egal", async () => {
  const d = JSON.parse(BEISPIEL);
  const tv = d.kategorien.find(k => k.id === "fernseher");
  const spitze = tv.modelle.find(m => m.id === "tv-a4-65");
  spitze.preis = null;
  const { dok } = await starte("#k=fernseher&s=ergebnis", JSON.stringify(d));
  const karte = klassen(dok, "empfehlung")[0];
  assert.ok(karte, "es gibt eine Empfehlung");
  assert.equal(text(karte).includes("Preis unbekannt"), false, text(karte).slice(0, 200));
  // nur Modelle ohne Preis: Hinweis statt Empfehlung
  for (const m of tv.modelle) m.preis = null;
  const leer = await starte("#k=fernseher&s=ergebnis", JSON.stringify(d));
  assert.equal(klassen(leer.dok, "empfehlung").length, 0);
  assert.ok(text(leer.dok.body).includes("kennen wir gerade keinen Preis"));
});

test("P1 07 B08 / Testlinks: Variante „Standard“ und doppelte Typnummer weg, Tests anderer als Link", async () => {
  const d = JSON.parse(BEISPIEL);
  const af = d.kategorien.find(k => k.id === "airfryer");
  af.modelle.forEach((m, i) => { m.variante = i % 2 ? "Standard" : m.name.split(" ").pop(); });
  af.modelle.forEach(m => { m.tests = [{ url: "https://example.org/test/" + m.id, titel: "Test bei Beispiel-Labor" }]; });
  const { dok } = await starte("#k=airfryer&s=ergebnis", JSON.stringify(d));
  const t = text(dok.body);
  assert.equal(/, Standard/.test(t), false);
  for (const m of af.modelle) assert.equal(t.includes(m.name + ", " + m.name.split(" ").pop()), false, "Typnummer doppelt: " + m.name);
  assert.ok(t.includes("Tests anderer"));
  const testlink = alle(dok.body).find(e => e.tagName === "A" && text(e) === "Test bei Beispiel-Labor");
  assert.equal(testlink.getAttribute("rel"), "noopener noreferrer");
  assert.ok(testlink.getAttribute("href").startsWith("https://example.org/test/"));
});

test("P1-01: gleiche angezeigte Note → gleicher Rang in jeder Sortierung", async () => {
  const raenge = async o => {
    const { dok } = await starte("#k=fernseher&s=ergebnis&b=500&o=" + o);
    const [bewertet] = alle(dok.body).filter(e => e.className === "rang");
    return Object.fromEntries(alle(bewertet).filter(e => e.className.startsWith("rang-eintrag")).map(li => [
      text(alle(li).find(e => e.className === "rang-name")), text(alle(li).find(e => e.className === "rang-nr"))]));
  };
  const note = await raenge("note");
  assert.deepEqual(Object.values(note).sort(), ["1", "1", "3", "4"]);
  assert.deepEqual(await raenge("preis"), note, "Günstigste");
  assert.deepEqual(await raenge("effizienz"), note, "Punkte je Euro");
});

test("P1-03: gemischte Daten – Meldung nennt Note, Preis und Budget statt pauschal „kein Preis“", async () => {
  const d = JSON.parse(BEISPIEL);
  const tv = d.kategorien.find(k => k.id === "fernseher");
  for (const m of tv.modelle) m.preis = null;
  const ohneNote = tv.modelle.find(m => m.id === "tv-c6-32");
  ohneNote.teilpunkte = {};
  ohneNote.preis = { eur: 100.5, haendler: "Beispielshop", url: "https://example.org/c6", stand: "2026-11-20" };
  const { dok } = await starte("#k=fernseher&s=ergebnis&b=95", JSON.stringify(d));
  const t = text(dok.body);
  assert.equal(klassen(dok, "empfehlung").length, 0);
  assert.equal(t.includes("Für die passenden Modelle kennen wir gerade keinen Preis"), false, t.slice(0, 500));
  assert.ok(t.includes("Für die Modelle mit Note kennen wir gerade keinen Preis, und die Modelle mit Preis liegen über deinem Budget und haben keine Note, weil Datenblattwerte fehlen."), t.slice(0, 500));
  // ohne jeden Preis bleibt die bisherige Meldung
  ohneNote.preis = null;
  const leer = await starte("#k=fernseher&s=ergebnis&b=95", JSON.stringify(d));
  assert.ok(text(leer.dok.body).includes("Für die passenden Modelle kennen wir gerade keinen Preis"));
});

test("P1-04: zählt kein Merkmal (alle Gewichte 0), nennt die Ansicht das statt fehlender Datenblattwerte", async () => {
  const d = JSON.parse(BEISPIEL);
  const tv = d.kategorien.find(k => k.id === "fernseher");
  for (const f of tv.felder) f.gewicht = 0;
  const { dok } = await starte("#k=fernseher&s=ergebnis&b=500", JSON.stringify(d));
  const t = text(dok.body);
  const offen = alle(dok.body).find(e => e.className === "offen");
  assert.ok(offen, t.slice(0, 300));
  const zeilen = alle(offen).filter(e => e.className.startsWith("rang-eintrag"));
  assert.ok(zeilen.length >= 1);
  for (const z of zeilen) assert.ok(text(z).includes("kein Merkmal zählt in die Note"), text(z));
  assert.ok(text(offen).includes("Für deine Angaben zählt gerade kein Merkmal in die Note."));
  assert.equal(t.includes("Datenblattwerte"), false, "keine falsche Ursache: " + t.slice(0, 600));
  assert.equal(t.includes("zu wenig Daten"), false);
  // Gegenfall: fehlende Werte nennen weiter „fehlt: …“
  const normal = await starte("#k=fernseher&s=ergebnis&b=500");
  assert.ok(text(normal.dok.body).includes("Für eine Note fehlen zu viele Datenblattwerte."));
});

test("P1-03/P1-04 r2: ohne Note nennt die Meldung Notengrund und Preisgrund, auch gemischt (Codex r2)", async () => {
  const preis = eur => ({ eur, haendler: "Beispielshop", url: "https://example.org/p" + eur, stand: "2026-11-20" });
  // Air Fryer, nur die Sync-Funktion gewichtet: beim Einkorbmodell nicht anwendbar (kein Merkmal zählt),
  // beim Zweikorbmodell fehlt ihr Wert (zu wenig Daten)
  const meldung = async (p1, p2, b) => {
    const d = JSON.parse(BEISPIEL);
    const af = d.kategorien.find(k => k.id === "airfryer");
    for (const f of af.felder) f.gewicht = f.id === "sync_funktion" ? 10 : 0;
    for (const fr of af.fragen) for (const a of fr.antworten) a.gewichte = {};
    const ein = af.modelle.find(m => m.werte.koerbe === 1), zwei = af.modelle.find(m => m.werte.koerbe === 2);
    delete zwei.teilpunkte.sync_funktion;
    ein.preis = p1; zwei.preis = p2; af.modelle = [ein, zwei];
    const { dok } = await starte("#k=airfryer&s=ergebnis" + (b ? "&b=" + b : ""), JSON.stringify(d));
    assert.equal(klassen(dok, "empfehlung").length, 0);
    return text(klassen(dok, "karte").find(k => k.className.includes("leise")));
  };
  const gemischt = "Keins der passenden Modelle hat eine Note: Bei einigen fehlen Datenblattwerte, bei den anderen zählt für deine Angaben kein Merkmal.";
  let t = await meldung(preis(100), preis(110), 95);
  assert.ok(t.includes(gemischt) && t.includes("Alle liegen über deinem Budget."), t);
  t = await meldung(null, null, null);
  assert.ok(t.includes(gemischt) && t.includes("Einen Preis kennen wir für keins."), t);
  t = await meldung(preis(100), null, 95);
  assert.ok(t.includes("Die Modelle mit Preis liegen über deinem Budget, für die übrigen kennen wir keinen Preis."), t);
  assert.equal(t.includes("reichen die Datenblattangaben"), false, t);
});

test("P1-03/P1-04 r3: gemischt mit Note – Notengrund der Modelle mit Preis (kein Merkmal / beides)", async () => {
  const preis = eur => ({ eur, haendler: "Beispielshop", url: "https://example.org/q" + eur, stand: "2026-11-20" });
  // Air Fryer, nur Sync gewichtet: Zweikorb mit Sync-Wert hat eine Note (ohne Preis); Einkorb: Sync nicht anwendbar
  // (kein Merkmal), zweites Zweikorbmodell ohne Sync-Wert (Datenblatt fehlt)
  const meldung = async mitLuecke => {
    const d = JSON.parse(BEISPIEL);
    const af = d.kategorien.find(k => k.id === "airfryer");
    for (const f of af.felder) f.gewicht = f.id === "sync_funktion" ? 10 : 0;
    for (const fr of af.fragen) for (const a of fr.antworten) a.gewichte = {};
    const ein = af.modelle.find(m => m.werte.koerbe === 1), zwei = af.modelle.find(m => m.werte.koerbe === 2);
    const luecke = JSON.parse(JSON.stringify(zwei)); luecke.id = "af-luecke"; luecke.modell = "Luecke"; delete luecke.teilpunkte.sync_funktion;
    zwei.preis = null; ein.preis = preis(100); luecke.preis = preis(120);
    af.modelle = mitLuecke ? [zwei, ein, luecke] : [zwei, ein];
    const { dok } = await starte("#k=airfryer&s=ergebnis&b=95", JSON.stringify(d));
    assert.equal(klassen(dok, "empfehlung").length, 0);
    return text(klassen(dok, "karte").find(k => k.className.includes("leise")));
  };
  let t = await meldung(false);
  assert.ok(t.includes("haben keine Note, weil für deine Angaben kein Merkmal zählt."), t);
  t = await meldung(true);
  assert.ok(t.includes("haben keine Note, weil Datenblattwerte fehlen oder für deine Angaben kein Merkmal zählt."), t);
});

// ---------- G1: Prioritäten-Regler, Woher die Punkte kommen, Punktbahnen (24.11.2026) ----------
const regler = dok => alle(dok.body).filter(e => e.tagName === "INPUT" && e.attr.type === "range");
const rangNamen = dok => { const [b] = alle(dok.body).filter(e => e.className === "rang");
  return alle(b).filter(e => e.className === "rang-name").map(e => text(e)); };
const bewertung = () => createRequire(import.meta.url)(path.join(ORDNER, "bewertung.js"));

test("G1: Regler verschieben Gewichte live, Adresse p= nur abweichende Stufen, Zurück auf Antworten", async () => {
  const { dok, ort } = await starte("#k=fernseher&s=ergebnis");
  assert.ok(text(dok.body).includes("Deine Prioritäten verschieben"));
  // Reihenfolge: Empfehlung oben, Regler dazwischen, Rangliste und Vergleich darunter (Browserbefund G1)
  const schirm = dok.getElementById("ergebnis-koerper").parentNode;
  const ids = schirm.childNodes.map(k => k.id).filter(Boolean);
  assert.deepEqual(ids.slice(-3), ["ergebnis-koerper", "prio", "ergebnis-unten"]);
  assert.ok(dok.getElementById("ergebnis-unten").childNodes.length >= 2, "Rangliste und Vergleich unten");
  assert.equal(alle(dok.getElementById("ergebnis-koerper")).some(e => e.id === "rang-titel" || e.id === "vergleich"), false);
  const r0 = regler(dok);
  assert.ok(r0.length >= 2, "Regler je bewertetem Merkmal");
  assert.ok(r0.every(e => e.value === "2" && e.attr.min === "0" && e.attr.max === "4"), "Start auf „normal“");
  assert.ok(r0.every(e => /^normal, zählt \d+ %$/.test(e.getAttribute("aria-valuetext"))), r0[0].getAttribute("aria-valuetext"));
  const zurueck = dok.getElementById("prio-zurueck");
  assert.equal(zurueck.hidden, true, "ohne Abweichung kein Zurück-Knopf");
  const vorher = rangNamen(dok);
  // erstes Merkmal aus: Anteil 0, Regler bleibt dasselbe Element (Ziehen bricht nicht ab)
  const erster = r0[0];
  const fid = erster.id.replace("prio-", "");
  erster.focus(); erster.value = "0"; erster.ausloesen("input");
  assert.equal(regler(dok)[0], erster);
  assert.equal(dok.activeElement, erster);
  assert.equal(erster.getAttribute("aria-valuetext"), "aus, zählt nicht");
  assert.ok(ort.hash.includes("p=" + fid + ".0"), ort.hash);
  assert.equal(zurueck.hidden, false);
  // „viel mehr“ auf das zweite steht in der Adresse, „normal“ nie
  const zweiter = regler(dok)[1];
  zweiter.value = "4"; zweiter.ausloesen("input");
  assert.match(ort.hash, /p=[a-z0-9_-]+\.0~[a-z0-9_-]+\.4/);
  assert.match(zweiter.getAttribute("aria-valuetext"), /^viel mehr, zählt \d+ %$/);
  zweiter.value = "2"; zweiter.ausloesen("input");
  assert.equal(/\.2(~|&|$)/.test(ort.hash), false, "normal steht nicht in der Adresse");
  assert.deepEqual(rangNamen(dok).slice().sort(), vorher.slice().sort(), "dieselben Modelle");
  // zurück auf die Antworten: alles normal, p= weg, Reihenfolge wie vorher
  zurueck.ausloesen("click");
  assert.equal(/p=/.test(ort.hash), false);
  assert.ok(regler(dok).every(e => e.value === "2"));
  assert.deepEqual(rangNamen(dok), vorher);
  assert.equal(zurueck.hidden, true);
});

test("G1: Regler rechnen wie bewertung.js (alle Merkmale aus außer einem, Note der Empfehlung)", async () => {
  const B = bewertung();
  const kat = B.datenPruefen(JSON.parse(BEISPIEL)).kategorien.find(k => k.id === "fernseher");
  const bewertet = kat.felder.filter(f => f.gewicht > 0).map(f => f.id);
  const p = bewertet.slice(1).map(f => f + ".0").join("~");
  const app = await starte("#k=fernseher&s=ergebnis&p=" + p);
  const r0 = regler(app.dok).find(e => e.id === "prio-" + bewertet[0]);
  assert.match(r0.getAttribute("aria-valuetext"), /zählt 100 %/);
  assert.ok(regler(app.dok).filter(e => e !== r0).every(e => e.getAttribute("aria-valuetext") === "aus, zählt nicht"));
  const faktoren = Object.fromEntries(bewertet.slice(1).map(f => [f, 0]));
  assert.deepEqual(Object.keys(B.gewichte(kat, {}, faktoren)), [bewertet[0]]);
  // angezeigte Note der Empfehlung = Rechnung mit denselben Faktoren
  const daten = B.datenPruefen(JSON.parse(BEISPIEL));
  const r = B.auswerten(daten.kategorien.find(k => k.id === "fernseher"), daten.regeln, { antworten: {}, prioritaeten: faktoren });
  if (r.empfehlung && r.empfehlung.note !== null) {
    const zahl = klassen(app.dok, "note-zahl")[0];
    assert.ok(text(zahl).startsWith(String(Math.round(r.empfehlung.note))), text(zahl));
  }
});

test("G1: Adresse p= wird geprüft (unbekanntes Feld, Filterfeld, Stufe außerhalb 0–4, normal, doppelt)", async () => {
  const kat = JSON.parse(BEISPIEL).kategorien.find(k => k.id === "fernseher");
  const feld = kat.felder.find(f => f.gewicht > 0).id;
  const filter = (kat.felder.find(f => f.gewicht === 0) || { id: "gibtsnicht" }).id;
  const app = await starte("#k=fernseher&s=ergebnis&p=" + [feld + ".3", feld + ".0", "constructor.1", "__proto__.1", filter + ".1", "x.9", feld + ".5", "zz.2"].join("~"));
  const r = regler(app.dok).find(e => e.id === "prio-" + feld);
  assert.equal(r.value, "3", "erste gültige Angabe gilt");
  assert.equal(regler(app.dok).filter(e => e.value !== "2").length, 1);
  // nach der nächsten Änderung steht nur noch die bereinigte Angabe in der Adresse
  const anderer = regler(app.dok).find(e => e.id !== "prio-" + feld);
  anderer.value = "1"; anderer.ausloesen("input");
  assert.ok(app.ort.hash.endsWith("&p=" + feld + ".3~" + anderer.id.replace("prio-", "") + ".1"), app.ort.hash);
  // eine neue Kategorie beginnt ohne Regleränderung
  const neu = await starte("#k=fernseher&s=ergebnis&p=" + feld + ".4");
  knopf(neu.dok, "Andere Kategorie").ausloesen("click");
  alle(neu.dok.body).filter(e => e.className.includes("kachel") && e.tagName === "BUTTON").find(e => text(e).includes("Fernseher")).ausloesen("click");
  assert.equal(/p=/.test(neu.ort.hash), false);
});

test("G1: Woher die Punkte kommen, Punktbahn in Rangliste, Vorn/gleichauf", async () => {
  const { dok } = await starte("#k=fernseher&s=ergebnis&b=1500");
  const karte = klassen(dok, "empfehlung")[0];
  const t = text(karte);
  assert.ok(t.includes("Woher die Punkte kommen"));
  assert.equal(t.includes("Stärken laut Datenblatt"), false);
  const zeilen = alle(karte).filter(e => e.className.split(/\s+/).includes("hz"));
  assert.ok(zeilen.length >= 2);
  for (const z of zeilen) assert.match(text(z), /zählt (\d+|unter 1) %/);
  for (const b of klassen(dok, "hz-balken")) assert.match(b.getAttribute("style"), /^width:\d+(\.\d+)?%$/);
  // Rangliste: Achse einmal, Bahn je bewertetem Eintrag, Vorn-Zeile
  const [bewertet] = alle(dok.body).filter(e => e.className === "rang");
  const eintraege = alle(bewertet).filter(e => e.className.startsWith("rang-eintrag"));
  assert.equal(klassen(dok, "rang-achse").length, 1);
  assert.equal(alle(bewertet).filter(e => e.className === "rang-bahn").length, eintraege.length);
  assert.ok(eintraege.every(e => e.getAttribute("data-modell")), "FLIP-Schlüssel je Eintrag");
  assert.match(text(klassen(dok, "rang-vorn")[0]), /^(Vorn: .+ mit \d+ Punkten vor .+\.|Gleichauf: .+ und .+ liegen weniger als 3 Punkte auseinander\.)$/);
  // Beispieldaten bis 500 €: zwei Modelle mit 56 Punkten → gleichauf
  const b2 = await starte("#k=fernseher&s=ergebnis&b=500");
  assert.ok(klassen(b2.dok, "rang-vorn")[0].className.includes("gleichauf"));
});

test("G1: Vergleich mit drei Modellen: Farbe je Platz, Name in jeder Bahn, Text nie in Serienfarbe, voll deaktiviert", async () => {
  const ids = JSON.parse(BEISPIEL).kategorien.find(k => k.id === "fernseher").modelle.slice(0, 3).map(m => m.id);
  const { dok } = await starte("#k=fernseher&s=ergebnis&v=" + ids.join("~"));
  const vgl = dok.getElementById("vergleich");
  const bahnen = alle(vgl).filter(e => e.className.startsWith("vgl-bahn farbe-"));
  assert.ok(bahnen.length >= 6, String(bahnen.length));
  for (const b of bahnen) assert.ok(text(alle(b).find(e => e.className === "vgl-bahn-name")).length > 0, "Name als Text");
  assert.deepEqual([...new Set(bahnen.map(b => b.className.match(/farbe-(\d)/)[1]))].sort(), ["1", "2", "3"]);
  assert.equal(alle(vgl).some(e => /farbe-\d/.test(e.className) && e.tagName === "SPAN"), false);
  const voll = alle(dok.body).filter(e => e.tagName === "BUTTON" && e.id.startsWith("vgl-rang-") && e.disabled);
  assert.ok(voll.length >= 1 && voll.every(e => text(e).includes("Vergleich voll (3)")));
});

// ---------- G1 Codex r1 (G1-01 … G1-05) ----------
test("G1-01: Wechsel der Ergebnisadresse baut fehlende Regler nach (Antwort, die ein Merkmal abschaltet)", async () => {
  const app = await starte("#k=fernseher&s=ergebnis&a=ton.ja");
  assert.equal(app.dok.getElementById("prio-lautsprecher_w"), null, "mit ton.ja zählt die Lautsprecherleistung nicht");
  await app.zurueck("#k=fernseher&s=ergebnis");
  assert.ok(app.dok.getElementById("prio-lautsprecher_w"), "nach dem Wechsel zählt sie wieder, also braucht sie einen Regler");
  const direkt = await starte("#k=fernseher&s=ergebnis");
  assert.deepEqual(regler(app.dok).map(e => e.id), regler(direkt.dok).map(e => e.id), "wie beim direkten Öffnen");
  // umgekehrt: abgeschaltetes Merkmal verliert seinen Regler; ohne Feldwechsel bleibt der Regler dasselbe Element
  await app.zurueck("#k=fernseher&s=ergebnis&a=ton.ja");
  assert.equal(app.dok.getElementById("prio-lautsprecher_w"), null);
  const r = regler(app.dok)[0];
  await app.zurueck("#k=fernseher&s=ergebnis&a=ton.ja&b=900");
  assert.equal(regler(app.dok)[0], r);
});

test("G1-02: fehlender Wert heißt in der Punkteherkunft „nicht angegeben“, nicht „0 Punkte“", async () => {
  const d = JSON.parse(BEISPIEL);
  for (const m of d.kategorien.find(k => k.id === "fernseher").modelle) { delete m.werte.tuner_triple; delete m.teilpunkte.tuner_triple; }
  const { dok } = await starte("#k=fernseher&s=ergebnis", JSON.stringify(d));
  const fehlt = alle(klassen(dok, "empfehlung")[0]).filter(e => e.className === "hz fehlt");
  assert.ok(fehlt.length >= 1, "Zeile für den fehlenden Wert");
  for (const z of fehlt) {
    const bahn = alle(z).find(e => e.className === "hz-bahn");
    assert.equal(bahn.getAttribute("aria-label"), "nicht angegeben");
    assert.ok(text(z).includes("nicht angegeben"));
  }
});

test("G1-03: Vergleich – Vorn/gleichauf aus den angezeigten Teilpunkten (82,6 vs 80,4 → 83 vs 80 = Vorn +3)", async () => {
  const d = JSON.parse(BEISPIEL);
  const [m1, m2] = d.kategorien.find(k => k.id === "fernseher").modelle;
  m1.teilpunkte.bildtechnik = 82.6; m2.teilpunkte.bildtechnik = 80.4;
  m1.teilpunkte.hdr_formate = 80.4; m2.teilpunkte.hdr_formate = 82.4;   // 80 vs 82 → gleichauf
  const { dok } = await starte("#k=fernseher&s=ergebnis&v=" + m1.id + "~" + m2.id, JSON.stringify(d));
  const block = name => alle(dok.getElementById("vergleich")).find(e => e.className === "vgl-block" && text(alle(e).find(x => x.className === "vgl-feld-name")) === name);
  const bild = block("Bildtechnik");
  assert.ok(bild, "Block Bildtechnik");
  const marke = text(alle(bild).find(e => e.className.startsWith("vgl-marke")));
  assert.match(marke, /^Vorn: .+ \+3$/);
  assert.ok(text(bild).includes("83 von 100 Teilpunkten") && text(bild).includes("80 von 100 Teilpunkten"));
  const hdr = alle(dok.getElementById("vergleich")).filter(e => e.className === "vgl-block").find(e => /HDR/.test(text(e)));
  assert.equal(text(alle(hdr).find(e => e.className.startsWith("vgl-marke"))), "gleichauf");
});

test("G1-04: Glas-Beobachter meldet entfernte Hinweiskarten ab (Schirmwechsel, Neurechnen ohne Karten)", async () => {
  const beobachtet = new Set();
  class IO { constructor() { this.eigene = new Set(); }
    observe(k) { this.eigene.add(k); beobachtet.add(k); }
    disconnect() { for (const k of this.eigene) beobachtet.delete(k); this.eigene.clear(); } }
  const app = await starte("#k=fernseher&s=ergebnis&b=500", BEISPIEL, null, { kontext: { IntersectionObserver: IO } });
  assert.ok(beobachtet.size >= 1, "bei 500 € gibt es den Aufpreis-Hinweis");
  await app.zurueck("#k=fernseher&s=ergebnis");   // Budget egal: Neurechnen ohne Hinweiskarten
  assert.equal([...beobachtet].every(k => alle(app.dok.body).includes(k)), true, "nur Karten, die noch im Dokument stehen");
  await app.zurueck("#k=fernseher&s=budget");
  assert.equal(beobachtet.size, 0, "Budgetschirm: keine Karte mehr beobachtet");
});

test("G1-05: FLIP fragt die Bewegungseinstellung bei jedem Umordnen neu", async () => {
  const stand = { reduziert: false };
  let animiert = 0;
  Element.prototype.getBoundingClientRect = function () { const p = this.parentNode; return { top: p ? p.childNodes.indexOf(this) * 100 : 0 }; };
  Element.prototype.animate = function () { animiert++; };
  try {
    const { dok } = await starte("#k=fernseher&s=ergebnis", BEISPIEL, null,
      { fenster: { matchMedia: () => ({ get matches() { return stand.reduziert; } }) } });
    const vorher = rangNamen(dok);
    const erster = regler(dok)[0];
    erster.value = "0"; erster.ausloesen("input");
    assert.notDeepEqual(rangNamen(dok), vorher, "Probe braucht eine Umordnung");
    assert.ok(animiert > 0, "ohne Reduktion gleitet die Liste");
    // Reduktion bei offener Seite einschalten: nächste Umordnung ohne Animation
    stand.reduziert = true;
    const n = animiert;
    erster.value = "2"; erster.ausloesen("input");
    assert.deepEqual(rangNamen(dok), vorher);
    assert.equal(animiert, n, "reduziert: sofort, ohne Animation");
  } finally { delete Element.prototype.getBoundingClientRect; delete Element.prototype.animate; }
});
