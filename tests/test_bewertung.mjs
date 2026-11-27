// Tests für app/finder/bewertung.js (node:test, nur eingebaute Module). Aufruf: node --test tests/test_bewertung.mjs
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const HIER = path.dirname(fileURLToPath(import.meta.url));
const PROJEKT = path.resolve(HIER, "..");
const require = createRequire(import.meta.url);
const B = require(path.join(PROJEKT, "app", "finder", "bewertung.js"));

const SCHEMA = JSON.parse(fs.readFileSync(path.join(PROJEKT, "daten", "schema", "kategorien.json"), "utf8"));
const REGELN = Object.fromEntries(["unterschiedsschwelle_punkte", "datenblatt_abschlag", "aufpreis_regeln"].map(k => [k, SCHEMA[k]]));
const DB = REGELN.datenblatt_abschlag;
const beispiel = () => B.datenPruefen(JSON.parse(fs.readFileSync(path.join(HIER, "vorlagen", "finder-beispiel.json"), "utf8")));
const nah = (a, b, eps = 1e-6) => assert.ok(Math.abs(a - b) <= eps, `${a} ≠ ${b}`);

// Kleine Testkategorie: zwei bewertete Felder (80/20), ein Filterfeld
const KAT = {
  id: "probe", name: "Probe",
  felder: [
    { id: "a", name: "Feld A", einheit: "", typ: "zahl", gewicht: 80 },
    { id: "b", name: "Feld B", einheit: "", typ: "bool", gewicht: 20 },
    { id: "groesse", name: "Größe", einheit: "Zoll", typ: "zahl", gewicht: 0 },
  ],
  fragen: [
    { id: "f1", text: "?", antworten: [
      { id: "mehr_b", text: "", gewichte: { b: 4 }, mindest: {} },
      { id: "ohne_b", text: "", gewichte: { b: 0 }, mindest: {} },
      { id: "gross", text: "", gewichte: {}, mindest: { groesse: 55 } },
      { id: "klein", text: "", gewichte: {}, mindest: {}, hoechst: { groesse: 43 } },
      { id: "b_pflicht", text: "", gewichte: {}, mindest: { b: true } },
    ] },
    { id: "f2", text: "?", antworten: [{ id: "halb_b", text: "", gewichte: { b: 0.5, a: 2 }, mindest: {} }] },
  ],
  modelle: [],
};
const modell = (id, tp, werte = {}, eur = null) => ({
  id, modell: id, hersteller: "Beispiel A", name: id, variante: "", werte, teilpunkte: tp,
  preis: eur === null ? null : { eur, haendler: "Beispielshop", url: "https://example.org/" + id, stand: "2026-11-20" }, tests: [],
});
// Eintrag wie aus auswerten() für die Hinweisregeln
const eintrag = (id, preis, note, art = "datenblatt") => ({ modell: { id }, preis, note, art });

test("Gewichte: Faktoren multiplizieren, 0 schaltet ab, Summe 100, Filterfelder ohne Gewicht", () => {
  const g0 = B.gewichte(KAT, {});
  nah(g0.a, 80); nah(g0.b, 20); assert.equal("groesse" in g0, false);
  const g1 = B.gewichte(KAT, { f1: "mehr_b" });          // a 80, b 80
  nah(g1.a, 50); nah(g1.b, 50);
  const g2 = B.gewichte(KAT, { f1: "mehr_b", f2: "halb_b" }); // a 160, b 20*4*0.5 = 40
  nah(g2.a, 80); nah(g2.b, 20);
  nah(Object.values(g2).reduce((s, x) => s + x, 0), 100);
  const g3 = B.gewichte(KAT, { f1: "ohne_b" });
  assert.deepEqual(Object.keys(g3), ["a"]); nah(g3.a, 100);
  // unbekannte Antwort = egal
  assert.deepEqual(B.gewichte(KAT, { f1: "gibtsnicht" }), g0);
});

test("G1: Prioritäten als drittes Argument: Faktor 0 schaltet ab, ½ und 3 verschieben, Filterfelder bleiben draußen", () => {
  assert.deepEqual(B.PRIO_FAKTOREN, [0, 0.5, 1, 2, 3]);
  const g0 = B.gewichte(KAT, {}, {});
  nah(g0.a, 80); nah(g0.b, 20);
  const aus = B.gewichte(KAT, {}, { b: 0 });
  assert.deepEqual(Object.keys(aus), ["a"]); nah(aus.a, 100);
  const halb = B.gewichte(KAT, {}, { a: 0.5 });           // a 40, b 20
  nah(halb.a, 40 / 60 * 100); nah(halb.b, 20 / 60 * 100);
  const drei = B.gewichte(KAT, { f1: "mehr_b" }, { b: 3 }); // a 80, b 20 * 4 * 3 = 240
  nah(drei.a, 25); nah(drei.b, 75);
  // Filterfeld (Gewicht 0) bekommt auch mit Faktor kein Gewicht; ungültige Faktoren zählen als 1
  assert.equal("groesse" in B.gewichte(KAT, {}, { groesse: 3 }), false);
  assert.deepEqual(B.gewichte(KAT, {}, { a: -1, b: "3", constructor: 0 }), g0);
  // alles aus: keine Gewichte, Modell ohne Note mit Grund „kein Merkmal zählt“
  assert.deepEqual(B.gewichte(KAT, {}, { a: 0, b: 0 }), {});
  const k = Object.assign({}, KAT, { modelle: [modell("m1", { a: 80, b: 100 }, { a: 5, b: true }, 100)] });
  const r = B.auswerten(k, REGELN, { prioritaeten: { a: 0, b: 0 } });
  assert.equal(r.rang[0].note, null); assert.equal(r.rang[0].art, "keine_merkmale");
  // auswerten reicht die Prioritäten durch: a 80, b 20 * 3 = 60
  nah(B.auswerten(k, REGELN, { prioritaeten: { b: 3 } }).gewichte.b, 60 / 140 * 100);
});

test("Gewichte: echte Schemakategorien normieren auf 100", () => {
  for (const k of SCHEMA.kategorien) {
    const antworten = Object.fromEntries(k.fragen.map(f => [f.id, f.antworten[0].id]));
    const g = B.gewichte(k, antworten);
    nah(Object.values(g).reduce((s, x) => s + x, 0), 100, 1e-9);
  }
});

test("Abschlag: Beispiele aus dem Schema (R 90 → 81, R 95 → 85,25 ohne Kappung (D12), R 70 → 64, R 80 bei 80 % → 68,5)", () => {
  nah(B.datenblattNote(90, 1, DB), 81);
  nah(B.datenblattNote(95, 1, DB), 85.25);
  nah(B.datenblattNote(100, 1, DB), 89.5);
  assert.equal("kappung" in DB, false, "D12: Schema ohne Kappung");
  nah(B.datenblattNote(70, 1, DB), 64);
  nah(B.datenblattNote(80, 0.8, DB), 68.5);
  // genau Mindestabdeckung: Note; knapp darunter: keine Note
  assert.notEqual(B.datenblattNote(80, 0.7, DB), null);
  assert.equal(B.datenblattNote(80, 0.6999, DB), null);
});

test("Rohwert und Abdeckung über belegte Felder; unter 70 % keine Note", () => {
  const g = B.gewichte(KAT, {});
  const r1 = B.bewerteModell(modell("m1", { a: 80 }), KAT, g, REGELN);   // b fehlt → Abdeckung 0,8
  nah(r1.R, 80); nah(r1.abdeckung, 0.8); nah(r1.note, 68.5);
  assert.equal(r1.art, "datenblatt"); assert.equal("klasse" in r1, false); assert.equal(r1.spanne, 8);
  assert.deepEqual(r1.fehlend.map(f => f.feld), ["b"]);
  const r2 = B.bewerteModell(modell("m2", { b: 100 }), KAT, g, REGELN);  // nur 20 % belegt
  assert.equal(r2.note, null); assert.equal(r2.art, "zu_wenig_daten");
  assert.deepEqual(r2.fehlend.map(f => f.feld), ["a"], "fehlende Felder nach Gewicht für „Noch nicht bewertbar“");
  const r3 = B.bewerteModell(modell("m3", { a: 90, b: 90 }), KAT, g, REGELN);
  nah(r3.note, 81); assert.equal(r3.beitraege[0].feld, "a");
});

test("Nicht anwendbar: Sync-Funktion bei einem Garraum kostet keine Abdeckung", () => {
  const kat = SCHEMA.kategorien.find(k => k.id === "airfryer");
  const g = B.gewichte(kat, {});
  const tp = { volumen_l: 80, spuelmaschinenfest: 100, koerbe: 50, leistung_w: 75, sichtfenster: 100, beschichtung: 60, temp_max_c: 80, doerren: 100 };
  const r = B.bewerteModell(modell("af", tp, { koerbe: 1 }), kat, g, REGELN);
  nah(r.abdeckung, 1);
  const r2 = B.bewerteModell(modell("af2", tp, { koerbe: 2 }), kat, g, REGELN);
  assert.ok(r2.abdeckung < 1);
});

test("Getestet (nur wenn Testpunkte als Zahl vorliegen): 0,6 × Test + 0,4 × R, ohne Kappung", () => {
  const m = modell("t", { a: 100, b: 100 }); m.tests = [{ url: "https://example.org/t", titel: "x", punkte: 90 }];
  const r = B.bewerteModell(m, KAT, B.gewichte(KAT, {}), REGELN);
  assert.equal(r.art, "getestet"); nah(r.note, 94);
});

test("D12: keine Klassen und keine Kappung, auch wenn ältere Daten sie noch tragen", () => {
  assert.equal("klasse" in B, false);
  assert.equal("klassen" in SCHEMA, false, "Schema ohne Klassen");
  const alt = kopie(REGELN);
  alt.klassen = [{ ab: "0;background:red", name: "<b>x</b>" }];
  alt.datenblatt_abschlag.kappung = 84;
  const d = { regeln: alt, kategorien: [{ id: "probe", name: "Probe", felder: kopie(KAT.felder), fragen: kopie(KAT.fragen), modelle: [modell("m", { a: 100, b: 100 }, { a: 5, b: true }, 100)] }] };   // P2a-1: Teilpunkte brauchen den Wert
  assert.doesNotThrow(() => B.datenPruefen(d), "Altdaten bleiben lesbar");
  const r = B.bewerteModell(d.kategorien[0].modelle[0], d.kategorien[0], B.gewichte(d.kategorien[0], {}), d.regeln);
  nah(r.note, 89.5, 1e-9);   // nicht auf 84 gekappt
});

test("Mindest/Höchst: verletzt schließt aus, unbelegt bleibt markiert", () => {
  const kat = Object.assign({}, KAT, { modelle: [
    modell("gross", { a: 80, b: 100 }, { groesse: 65, b: true }, 400),
    modell("klein", { a: 90, b: 100 }, { groesse: 43, b: true }, 300),
    modell("ohne", { a: 85, b: 100 }, { b: true }, 350),
  ] });
  const r = B.auswerten(kat, REGELN, { antworten: { f1: "gross" }, budget: 500 });
  assert.deepEqual(r.rang.map(e => e.modell.id), ["ohne", "gross"]);
  assert.equal(r.ausgeschlossen, 1);
  const ohne = r.rang.find(e => e.modell.id === "ohne");
  assert.equal(ohne.unbelegt.length, 1); assert.equal(ohne.unbelegt[0].feld, "groesse");
  // Empfehlung bevorzugt das belegt passende Modell, obwohl "ohne" die höhere Note hat
  assert.equal(r.empfehlung.modell.id, "gross"); assert.equal(r.status, "passt");
  // Höchstwert und Pflicht-ja
  const r2 = B.auswerten(kat, REGELN, { antworten: { f1: "klein" }, budget: null });
  assert.deepEqual(r2.rang.filter(e => !e.unbelegt.length).map(e => e.modell.id), ["klein"]);
  assert.equal(B.pruefe({ b: false }, { feld: "b", art: "ja", wert: true }), "nein");
  assert.equal(B.pruefe({ s: "x" }, { feld: "s", art: "liste", wert: ["x", "y"] }), "ok");
  assert.equal(B.pruefe({ s: "z" }, { feld: "s", art: "liste", wert: ["x", "y"] }), "nein");
  assert.equal(B.pruefe({ g: 55 }, { feld: "g", art: "mindest", wert: 55 }), "ok");   // genau auf Grenze
  assert.equal(B.pruefe({ g: 43 }, { feld: "g", art: "hoechst", wert: 43 }), "ok");
  assert.equal(B.pruefe({}, { feld: "g", art: "mindest", wert: 1 }), "unbelegt");
});

test("Filter der Oberfläche (Diagonale, Bauart) wirken wie Anforderungen", () => {
  const anf = B.anforderungen(KAT, {}, { groesse: { mindest: 48, hoechst: 55 }, bauart: { liste: ["frontlader"] } });
  assert.deepEqual(anf.map(a => a.art + ":" + a.feld), ["mindest:groesse", "hoechst:groesse", "liste:bauart"]);
  assert.ok(anf.every(a => a.quelle === "filter"));
});

test("Aufpreis: Beispiel Fernseher aus dem Schema (Budget 500)", () => {
  const A = eintrag("A", 489, 68), Bm = eintrag("B", 589, 77), D = eintrag("D", 649, 82), E = eintrag("E", 539, 70);
  const h = B.aufpreisHinweis(A, [Bm, D, E], 500, REGELN);
  assert.equal(h.modell.modell.id, "B"); assert.equal(h.aufpreis, 100); assert.equal(h.punkte, 9);
  assert.equal(h.text, "Für 100 € mehr bekommst du +9 Punkte.");
  // D allein: über 1,25 × Budget; E allein: zu wenig Punkte
  assert.equal(B.aufpreisHinweis(A, [D], 500, REGELN), null);
  assert.equal(B.aufpreisHinweis(A, [E], 500, REGELN), null);
});

test("R4-06: Platzhalter nur aus eigenen Einträgen, geerbte ({constructor}) bleiben wörtlich stehen", () => {
  const r = JSON.parse(JSON.stringify(REGELN));
  r.aufpreis_regeln.aufpreis.text = "Für {aufpreis} € mehr {constructor}{toString}{__proto__}";
  const h = B.aufpreisHinweis(eintrag("A", 489, 68), [eintrag("B", 589, 77)], 500, r);
  assert.equal(h.text, "Für 100 € mehr {constructor}{toString}{__proto__}");
  assert.ok(!/function|native code|object Object/.test(h.text));
});

test("Aufpreis: Air-Fryer-Beispiel, genau 20 € und genau 5 Punkte", () => {
  const h = B.aufpreisHinweis(eintrag("A", 99, 62), [eintrag("B", 119, 67)], 100, REGELN);
  assert.equal(h.text, "Für 20 € mehr bekommst du +5 Punkte.");
  assert.equal(B.aufpreisHinweis(eintrag("A", 99, 62), [eintrag("B", 118.99, 67)], 100, REGELN), null); // 19,99 €
  assert.equal(B.aufpreisHinweis(eintrag("A", 99, 62), [eintrag("B", 119, 66.99)], 100, REGELN), null); // < 5 Punkte
  // getestet auf beiden Seiten: 3 Punkte reichen
  const t = B.aufpreisHinweis(eintrag("A", 99, 62, "getestet"), [eintrag("B", 119, 65, "getestet")], 100, REGELN);
  assert.ok(t);
});

test("Aufpreis: genau auf 1,25 × Budget gilt, darüber nicht (auch mit Cent-Preisen)", () => {
  const A = eintrag("A", 450, 60);
  assert.ok(B.aufpreisHinweis(A, [eintrag("B", 625, 75)], 500, REGELN));
  assert.equal(B.aufpreisHinweis(A, [eintrag("B", 625.01, 75)], 500, REGELN), null);
  const Ac = eintrag("A", 489.99, 68);
  const h = B.aufpreisHinweis(Ac, [eintrag("B", 509.99, 73)], 500, REGELN);   // 20,00 € in Gleitkomma
  assert.ok(h); assert.equal(h.aufpreis, 20);
});

test("Aufpreis: Effizienz 3 je 100 € genau, darunter kein Hinweis (D12: kein Klassensprung mehr)", () => {
  const A = eintrag("A", 400, 62);
  assert.ok(B.aufpreisHinweis(A, [eintrag("B", 600, 68)], 500, REGELN));        // E = 3
  assert.equal(B.aufpreisHinweis(A, [eintrag("B", 601, 68)], 500, REGELN), null); // E < 3
  assert.equal(B.aufpreisHinweis(eintrag("A", 700, 70), [eintrag("B", 1100, 76)], 1000, REGELN), null); // E 1,5
  // ältere Regeltexte mit {klasse_text} ergeben keinen Klassenrest
  const alt = kopie(REGELN); alt.aufpreis_regeln.aufpreis.text = "Für {aufpreis} € mehr +{dN} Punkte{klasse_text}.";
  assert.equal(B.aufpreisHinweis(A, [eintrag("B", 600, 68)], 500, alt).text, "Für 200 € mehr +6 Punkte.");
});

test("Aufpreis: höchstens ein Hinweis, größtes E, bei Gleichstand kleinerer Aufpreis", () => {
  const A = eintrag("A", 400, 60);
  const h = B.aufpreisHinweis(A, [eintrag("B1", 500, 66), eintrag("B2", 450, 66), eintrag("B3", 600, 80)], 500, REGELN);
  assert.equal(h.modell.modell.id, "B2");                            // E 12 > E 10 = B3 > E 6
  const g = B.aufpreisHinweis(A, [eintrag("X", 500, 70), eintrag("Y", 450, 65)], 500, REGELN); // beide E 10
  assert.equal(g.modell.modell.id, "Y");
});

test("Aufpreis: kein Budget (egal) oder A ohne Preis → kein Hinweis", () => {
  assert.equal(B.aufpreisHinweis(eintrag("A", 400, 60), [eintrag("B", 450, 70)], null, REGELN), null);
  assert.equal(B.aufpreisHinweis(eintrag("A", null, 60), [eintrag("B", 450, 70)], 500, REGELN), null);
});

test("Spar: Beispiel aus dem Schema und Grenzfälle", () => {
  const A = eintrag("A", 489, 68);
  const h = B.sparHinweis(A, [eintrag("C", 409, 66)], REGELN);
  assert.equal(h.text, "Für 80 € weniger fast gleich gut (66 statt 68 Punkte)."); assert.equal(h.art, "gleich");
  // Mindestersparnis genau 10 % bzw. 30 €
  assert.ok(B.sparHinweis(eintrag("A", 500, 70), [eintrag("C", 450, 68)], REGELN));
  assert.equal(B.sparHinweis(eintrag("A", 500, 70), [eintrag("C", 450.01, 68)], REGELN), null);
  assert.ok(B.sparHinweis(eintrag("A", 100, 70), [eintrag("C", 70, 68)], REGELN));
  assert.equal(B.sparHinweis(eintrag("A", 100, 70), [eintrag("C", 71, 68)], REGELN), null);
  // Verlust genau 3 → fast gleich gut; D12: ohne Klassengrenze zählt nur der Verlust
  assert.ok(B.sparHinweis(eintrag("A", 500, 70), [eintrag("C", 400, 67)], REGELN));
  assert.equal(B.sparHinweis(eintrag("A", 500, 76), [eintrag("C", 400, 74)], REGELN).art, "gleich");
  assert.equal(B.sparHinweis(eintrag("A", 500, 76), [eintrag("C", 400, 72.9)], REGELN), null);   // Verlust > 3, < 25 %
  // etwas schwächer: Verlust 4,5 und genau 25 % Ersparnis
  const s = B.sparHinweis(eintrag("A", 400, 70), [eintrag("C", 300, 65.5)], REGELN);
  assert.equal(s.art, "schwaecher"); assert.equal(s.text, "Für 100 € weniger etwas schwächer (66 statt 70 Punkte).");
  assert.equal(B.sparHinweis(eintrag("A", 400, 70), [eintrag("C", 301, 65.5)], REGELN), null);
  assert.equal(B.sparHinweis(eintrag("A", 400, 70), [eintrag("C", 200, 64.9)], REGELN), null);   // Verlust > 5
  // Auswahl: größte Ersparnis
  const w = B.sparHinweis(eintrag("A", 500, 70), [eintrag("C1", 440, 69), eintrag("C2", 420, 68)], REGELN);
  assert.equal(w.modell.modell.id, "C2");
});

test("Fehlende Preise: nie Empfehlung ohne Preis, auch bei Budget „egal“ (08 G)", () => {
  const kat = Object.assign({}, KAT, { modelle: [
    modell("teuer_ohne", { a: 95, b: 100 }, {}, null),
    modell("mit", { a: 70, b: 100 }, {}, 300),
  ] });
  const r = B.auswerten(kat, REGELN, { budget: 500 });
  assert.equal(r.empfehlung.modell.id, "mit");
  assert.equal(r.rang.find(e => e.modell.id === "teuer_ohne").imBudget, null);
  const egal = B.auswerten(kat, REGELN, { budget: null });
  assert.equal(egal.empfehlung.modell.id, "mit"); assert.equal(egal.status, "passt");
  assert.equal(egal.rang[0].modell.id, "teuer_ohne", "bleibt in der Rangliste vorn sichtbar");
  // nur Modelle ohne Preis: keine Empfehlung
  const nurOhne = B.auswerten(Object.assign({}, KAT, { modelle: [modell("o1", { a: 95, b: 100 }), modell("o2", {})] }), REGELN, { budget: null });
  assert.equal(nurOhne.empfehlung, null); assert.equal(nurOhne.status, "leer"); assert.equal(nurOhne.rang.length, 2);
  assert.equal(egal.aufpreis, null); assert.equal(egal.spar, null);
  // Rangfolge nach Preis: ohne Preis ans Ende
  assert.deepEqual(B.sortiere(egal.rang, "preis").map(e => e.modell.id), ["mit", "teuer_ohne"]);
});

test("Nichts im Budget: bestes passendes Modell mit Hinweis über Budget", () => {
  const kat = Object.assign({}, KAT, { modelle: [modell("x", { a: 70, b: 100 }, {}, 800), modell("y", { a: 90, b: 100 }, {}, 900)] });
  const r = B.auswerten(kat, REGELN, { budget: 500 });
  assert.equal(r.status, "ueber_budget"); assert.equal(r.empfehlung.modell.id, "y");
  assert.equal(r.aufpreis, null);
  const leer = B.auswerten(Object.assign({}, KAT, { modelle: [] }), REGELN, { budget: 500 });
  assert.equal(leer.status, "leer"); assert.equal(leer.empfehlung, null);
});

test("Rangfolge: Note, dann Preis; Punkte je Euro", () => {
  const l = [eintrag("a", 500, 70), eintrag("b", 400, 70), eintrag("c", 300, 60), eintrag("d", null, 80), eintrag("e", 100, null)];
  assert.deepEqual(B.sortiere(l, "note").map(e => e.modell.id), ["d", "b", "a", "c", "e"]);
  assert.deepEqual(B.sortiere(l, "effizienz").map(e => e.modell.id), ["c", "b", "a", "d", "e"]);
});

test("07 B03/B15: gleiche angezeigte Note → günstigeres zuerst und als Empfehlung", () => {
  // 84,4 und 83,6 zeigen beide 84: der günstigere gewinnt, obwohl seine ungerundete Note kleiner ist
  const l = [eintrag("teuer", 130, 84.4), eintrag("billig", 65, 83.6), eintrag("ohne", null, 84.2), eintrag("klar", 400, 84.6)];
  assert.deepEqual(B.sortiere(l, "note").map(e => e.modell.id), ["klar", "billig", "teuer", "ohne"]);
  const kat = Object.assign({}, KAT, { modelle: [
    modell("teuer", { a: 98, b: 100 }, {}, 130),   // R 98,4 → 88,14 → angezeigt 88
    modell("billig", { a: 98, b: 99 }, {}, 65),     // R 98,2 → 87,97 → angezeigt 88
  ] });
  const r = B.auswerten(kat, REGELN, { budget: null });
  nah(r.rang[1].note, 88.14); nah(r.rang[0].note, 87.97);
  assert.equal(r.empfehlung.modell.id, "billig"); assert.equal(r.spar, null);
  // Spar-Hinweis nie „84 statt 84“: gleiche angezeigte Zahl → eigener Text
  const s = B.sparHinweis(eintrag("A", 130, 84.4), [eintrag("C", 65, 83.6)], REGELN);
  assert.equal(s.art, "gleichauf"); assert.equal(s.text, "Gleichauf mit 84 Punkten und 65 € günstiger.");
  const ohneText = kopie(REGELN); delete ohneText.aufpreis_regeln.spar.text_gleichauf;
  assert.equal(B.sparHinweis(eintrag("A", 130, 84.4), [eintrag("C", 65, 83.6)], ohneText), null);
});

test("Beispieldaten (erfunden): Auswertung Fernseher 500 €, Air Fryer 100 €, Budget egal", () => {
  const d = beispiel();
  assert.equal(d.erfunden, true);
  for (const k of d.kategorien) for (const m of k.modelle) {
    assert.match(m.hersteller, /^Beispiel [ABC]$/);
    if (m.preis) assert.ok(m.preis.url.startsWith("https://example.org/"));
  }
  const tv = d.kategorien.find(k => k.id === "fernseher");
  const r = B.auswerten(tv, d.regeln, { budget: 500 });
  assert.equal(r.status, "passt"); assert.ok(r.empfehlung.preis <= 500);
  assert.ok(r.aufpreis && r.aufpreis.modell.preis <= 625);
  assert.ok(r.rang.some(e => e.note === null), "Modell mit zu wenig Daten bleibt sichtbar");
  const af = B.auswerten(d.kategorien.find(k => k.id === "airfryer"), d.regeln, { budget: 100, antworten: { beilage: "ja" } });
  assert.ok(af.rang.every(e => e.modell.werte.koerbe === 2));
  assert.equal(af.status, "ueber_budget");
  const egal = B.auswerten(tv, d.regeln, { budget: null });
  assert.equal(egal.empfehlung.modell.id, egal.rang[0].modell.id);
  assert.deepEqual(B.budgetStufen(tv.modelle), [350, 600, 1000, 1600]);
  assert.equal(d.kategorien.find(k => k.id === "laptop").modelle.length, 0);
});

test("Preise überlagern: nur gültig und neuer; https-Pflicht", () => {
  const d = beispiel();
  const tv = d.kategorien.find(k => k.id === "fernseher");
  const id = tv.modelle[0].id, id2 = tv.modelle[1].id, id3 = tv.modelle[2].id;
  const n = B.preiseUeberlagern(d, { stand: "2026-11-21", preise: {
    [id]: { eur: 279, haendler: "Beispielshop Z", url: "https://example.org/neu", stand: "2026-11-21" },
    [id2]: { eur: 1, haendler: "Alt", url: "https://example.org/alt", stand: "2026-11-01" },
    [id3]: { eur: 100, haendler: "Böse", url: "javascript:alert(1)", stand: "2026-11-22" },
    "gibt-es-nicht": { eur: 5, haendler: "x", url: "https://example.org/", stand: "2026-11-21" },
  } });
  assert.equal(n, 1);
  assert.equal(tv.modelle[0].preis.eur, 279);
  assert.equal(tv.modelle[1].preis.haendler, "Beispielshop X");
  assert.ok(tv.modelle[2].preis.url.startsWith("https://example.org/"));
  // fehlender Preis wird ergänzt
  const sauger = d.kategorien.find(k => k.id === "akkusauger");
  const ohne = sauger.modelle.find(m => m.preis === null);
  assert.equal(B.preiseUeberlagern(d, { preise: { [ohne.id]: { eur: 299, haendler: "Y", url: "https://example.org/y", stand: "2026-11-01" } } }), 1);
  assert.equal(B.preiseUeberlagern(d, null), 0);
  assert.equal(B.sichereUrl("http://example.org/"), null);
  assert.equal(B.sichereUrl("https://example.org/a"), "https://example.org/a");
});

test("Datenprüfung: kaputte Preise werden entfernt, falsches Format wirft", () => {
  const d = { regeln: REGELN, kategorien: [{ id: "x", name: "X", felder: [], modelle: [{ id: "m", hersteller: "H", name: "M", werte: {}, teilpunkte: {}, preis: { eur: "1", haendler: "", url: "http://x", stand: "gestern" } }] }] };
  B.datenPruefen(d);
  assert.equal(d.kategorien[0].modelle[0].preis, null);
  assert.throws(() => B.datenPruefen({}));
  assert.throws(() => B.datenPruefen({ regeln: {}, kategorien: [] }));
});

test("Budgetstufen: runde Beträge, aufsteigend, ohne Doppelte", () => {
  assert.deepEqual(B.budgetStufen([]), []);
  const ms = [39, 59, 79, 89, 99, 119, 139, 179].map((p, i) => modell("m" + i, {}, {}, p));
  assert.deepEqual(B.budgetStufen(ms), [60, 90, 125, 200]);
  assert.deepEqual(B.budgetStufen([modell("e", {}, {}, 299)]), [300]);
});

test("Feldsieger und Stärken", () => {
  const e1 = { modell: { id: "x", teilpunkte: { a: 80, b: 100 } } }, e2 = { modell: { id: "y", teilpunkte: { a: 90, b: 100 } } };
  assert.deepEqual(B.feldSieger([e1, e2], KAT.felder), { a: ["y"] });
  const r = B.bewerteModell(modell("s", { a: 90, b: 40 }), KAT, B.gewichte(KAT, {}), REGELN);
  assert.deepEqual(B.staerken(r).map(s => s.feld), ["a"]);
});

// ---------- Codex r1 (Finder-Veröffentlichung) ----------
const kopie = x => JSON.parse(JSON.stringify(x));
const minimal = () => ({ regeln: kopie(REGELN), kategorien: [{ id: "probe", name: "Probe", felder: kopie(KAT.felder), fragen: kopie(KAT.fragen),
  modelle: [modell("m", { a: 90, b: 100 }, { a: 5, b: true }, 100)] }] });

test("F-01: Testlinks verlieren übernommene Punkte, die Note bleibt aus dem Datenblatt", () => {
  const d = minimal();
  d.kategorien[0].modelle[0].tests = [{ url: "https://example.org/t", titel: "Test", punkte: 90, text: "x" }, { url: "http://x", titel: "y" }, null];
  B.datenPruefen(d);
  const m = d.kategorien[0].modelle[0];
  assert.deepEqual(m.tests, [{ url: "https://example.org/t", titel: "Test" }]);
  const r = B.bewerteModell(m, d.kategorien[0], B.gewichte(d.kategorien[0], {}), d.regeln);
  assert.equal(r.art, "datenblatt"); nah(r.note, B.datenblattNote(r.R, r.abdeckung, DB));
});

test("F-08: beschädigte Felder, Fragen oder Regeln werfen (letzter Stand bleibt)", () => {
  const faelle = [
    d => { d.kategorien[0].felder.push(null); },
    d => { d.kategorien[0].felder[0].gewicht = "80"; },
    d => { d.kategorien[0].felder[0].typ = "html"; },
    d => { d.kategorien[0].fragen[0].antworten = null; },
    d => { d.kategorien[0].fragen.push({ id: "f3", text: "?", antworten: [null] }); },
    d => { d.kategorien[0].name = null; },
    d => { d.regeln.aufpreis_regeln.spar = null; },
    d => { d.regeln.datenblatt_abschlag.anker = "50"; },
  ];
  for (const f of faelle) { const d = minimal(); f(d); assert.throws(() => B.datenPruefen(d), String(f)); }
  assert.doesNotThrow(() => B.datenPruefen(minimal()));
});

test("F-09: Zahlen, die in style landen (Spanne), nur als Zahl 0..100", () => {
  for (const kaputt of ["8;background:red", -1, 101, NaN, null]) {
    const d = minimal(); d.regeln.datenblatt_abschlag.spanne_plus_minus = kaputt;
    assert.throws(() => B.datenPruefen(d), "spanne " + kaputt);
  }
  const d = minimal(); d.regeln.aufpreis_regeln.spar.text_gleichauf = { x: 1 };
  assert.throws(() => B.datenPruefen(d), "text_gleichauf nur als Text");
});

test("F-08: kaputte Teilpunkte und Modelle ohne Namen fallen still weg", () => {
  const d = minimal();
  d.kategorien[0].modelle[0].teilpunkte = { a: 90, b: "100" };
  d.kategorien[0].modelle.push({ id: "x", hersteller: null, name: "X" });
  B.datenPruefen(d);
  assert.deepEqual(d.kategorien[0].modelle[0].teilpunkte, { a: 90 });
  assert.equal(d.kategorien[0].modelle.length, 1);
});

test("F-10: Modell im Budget ohne Note wird gezeigt, nicht „passt nichts“", () => {
  const kat = Object.assign({}, KAT, { modelle: [modell("billig", {}, {}, 90), modell("teuer", { a: 90, b: 100 }, {}, 150)] });
  const r = B.auswerten(kat, REGELN, { budget: 100 });
  assert.equal(r.status, "ohne_note"); assert.equal(r.empfehlung.modell.id, "billig"); assert.equal(r.empfehlung.note, null);
  assert.equal(r.aufpreis, null); assert.equal(r.spar, null);
  // ohne Modell im Budget bleibt es beim Hinweis über Budget
  const r2 = B.auswerten(Object.assign({}, KAT, { modelle: [modell("teuer", { a: 90, b: 100 }, {}, 150)] }), REGELN, { budget: 100 });
  assert.equal(r2.status, "ueber_budget");
});

test("R2-03: stand und herkunft nur gültig, sonst Fehler; Modellwerte nur einfache Typen", () => {
  for (const st of [{ toString: null }, 5, "22.11.2026", ["2026-11-22"]]) {
    const d = minimal(); d.stand = st; assert.throws(() => B.datenPruefen(d), JSON.stringify(st));
  }
  for (const hk of ["main", { a: 1 }, "A".repeat(40)]) {
    const d = minimal(); d.herkunft = hk; assert.throws(() => B.datenPruefen(d), JSON.stringify(hk));
  }
  const ok = minimal(); ok.stand = "2026-11-22"; ok.herkunft = "0123456789abcdef0123456789abcdef01234567";
  assert.doesNotThrow(() => B.datenPruefen(ok));
  const n = minimal(); n.stand = null; assert.doesNotThrow(() => B.datenPruefen(n));
  const d = minimal();
  // P2a-1 (R2-06): Schemafelder nach Typ; hier „groesse“ (zahl), „a“ (zahl, Objekt), nicht im Schema: c, e, f, g, h (einfache Typen)
  d.kategorien[0].modelle[0].werte = { a: { toString: null }, groesse: 3, c: true, e: "gut", f: Infinity, g: "x".repeat(201), h: null };
  B.datenPruefen(d);
  assert.deepEqual(d.kategorien[0].modelle[0].werte, { groesse: 3, c: true, e: "gut" });
});

test("R3-02: Kennungen aus dem Objekt-Prototyp machen die Datei ungültig, solche Wert-Schlüssel fallen weg", () => {
  const faelle = [
    d => { d.kategorien[0].id = "constructor"; },
    d => { d.kategorien[0].id = "__proto__"; },
    d => { d.kategorien[0].felder[0].id = "prototype"; },
    d => { d.kategorien[0].felder[0].id = "constructor"; },
    d => { d.kategorien[0].fragen[0].id = "constructor"; },
    d => { d.kategorien[0].fragen[0].antworten[0].id = "__proto__"; },
    d => { d.kategorien[0].fragen[0].antworten[0].gewichte = { constructor: 2 }; },
    d => { d.kategorien[0].fragen[0].antworten[0].mindest = { prototype: 1 }; },
    d => { d.kategorien[0].fragen[0].antworten[0].hoechst = { constructor: 1 }; },
  ];
  for (const f of faelle) { const d = minimal(); f(d); assert.throws(() => B.datenPruefen(d), String(f)); }
  const d = minimal(), m = d.kategorien[0].modelle[0];
  m.werte = JSON.parse('{"constructor": 1, "__proto__": 2, "prototype": 3, "a": 4}');
  m.teilpunkte = JSON.parse('{"constructor": 50, "__proto__": 60, "a": 90}');
  B.datenPruefen(d);
  assert.deepEqual(Object.keys(m.werte), ["a"]);
  assert.deepEqual(Object.keys(m.teilpunkte), ["a"]);
  // Nachschlagen nur in eigenen Einträgen, auch ohne vorherige Prüfung
  assert.equal(B.nichtAnwendbar("constructor", "prototype", {}), false);
  assert.equal(B.nichtAnwendbar("airfryer", "constructor", {}), false);
  assert.equal(B.nichtAnwendbar("airfryer", "sync_funktion", { koerbe: 1 }), true);
  const kat = Object.assign(kopie(KAT), { id: "constructor" });
  kat.fragen[0].antworten[0].gewichte = { constructor: 2, b: 4 };
  const g = B.gewichte(kat, { f1: "mehr_b" });
  nah(g.a, 50); nah(g.b, 50);
  assert.equal(B.pruefe({}, { feld: "constructor", art: "ja", wert: true }), "unbelegt");
  assert.doesNotThrow(() => B.auswerten(Object.assign(kat, { modelle: [modell("m", { a: 90, b: 100 }, {}, 100)] }), REGELN, {}));
});

test("P1-01: Punkte je Euro mit der angezeigten Note – gleiche Zahl, günstigeres zuerst", () => {
  // 84,6 und 85,4 zeigen beide 85; ungerundet läge das teurere vorn (0,8497 > 0,846)
  const l = [eintrag("teuer", 100.5, 85.4), eintrag("billig", 100, 84.6), eintrag("klar", 100, 86.6), eintrag("ohne", null, 90)];
  assert.deepEqual(B.sortiere(l, "effizienz").map(e => e.modell.id), ["klar", "billig", "teuer", "ohne"]);
  // gleiche Effizienz der angezeigten Zahl → Note-Reihenfolge: höhere Zahl, dann günstiger, dann ungerundete Note
  const g = [eintrag("x", 200, 80.4), eintrag("y", 100, 39.6), eintrag("z", 100, 40.4)];
  assert.deepEqual(B.sortiere(g, "effizienz").map(e => e.modell.id), ["x", "z", "y"]);
});

test("P1-04: ohne wirksame Gewichte art „keine_merkmale“, fehlende Werte bleiben „zu_wenig_daten“", () => {
  const null_kat = Object.assign({}, KAT, { felder: KAT.felder.map(f => Object.assign({}, f, { gewicht: 0 })),
    modelle: [modell("m1", { a: 90, b: 100 }, {}, 100)] });
  const r = B.auswerten(null_kat, REGELN, { budget: null });
  assert.equal(r.rang[0].note, null);
  assert.equal(r.rang[0].art, "keine_merkmale");
  assert.deepEqual(r.rang[0].fehlend, []);
  // Antwort setzt die Gewichte auf 0 (ohne_b bei nur b gewichtet)
  const nurB = Object.assign({}, KAT, { felder: KAT.felder.map(f => Object.assign({}, f, { gewicht: f.id === "b" ? 20 : 0 })),
    modelle: [modell("m2", { b: 100 }, {}, 100)] });
  assert.equal(B.auswerten(nurB, REGELN, { antworten: { f1: "ohne_b" }, budget: null }).rang[0].art, "keine_merkmale");
  assert.notEqual(B.auswerten(nurB, REGELN, { budget: null }).rang[0].note, null);
  const luecke = Object.assign({}, KAT, { modelle: [modell("m3", { b: 100 }, {}, 100)] });
  const e = B.auswerten(luecke, REGELN, { budget: null }).rang[0];
  assert.equal(e.note, null); assert.equal(e.art, "zu_wenig_daten"); assert.equal(e.fehlend[0].feld, "a");
});

// ====================================================================================================================
// P2a-1 (Notenmodell, Rechnung und Schnittstelle; docs/recherche-ux/p2-entwurf.md, Testnummern in Klammern)
// ====================================================================================================================
const emoji = n => "😀".repeat(n);
const AFKAT = () => kopie(SCHEMA.kategorien.find(k => k.id === "airfryer"));
// Air Fryer mit einem Garraum: Teilpunkte nach den Kurven des Schemas (Volumen 5 l → 67,5 usw.)
const AF_WERTE = { volumen_l: 5, spuelmaschinenfest: true, koerbe: 1, leistung_w: 1700, sichtfenster: true, beschichtung: "keramik",
  sync_funktion: false, temp_max_c: 200, doerren: false };
const AF_TP = { volumen_l: 67.5, spuelmaschinenfest: 100, koerbe: 50, leistung_w: 75, sichtfenster: 100, beschichtung: 100,
  sync_funktion: 0, temp_max_c: 80, doerren: 0 };
const afModell = (id, werte = {}, tp = {}) => modell(id, Object.assign({}, AF_TP, tp), Object.assign({}, AF_WERTE, werte), 100);
const mitModell = (kat, m) => Object.assign(kopie(kat), { modelle: [m] });
const eintragFuer = (kat, m, antworten, prio) => Object.assign({ modell: m, preis: null },
  B.bewerteModell(m, kat, B.gewichte(kat, antworten, prio), REGELN));
// Orakel (§9.2): auswerten auf einer Ein-Modell-Kopie ohne mindest/hoechst
function orakel(kat, m, antworten, prio) {
  const k1 = kopie(kat); k1.modelle = [kopie(m)];
  for (const f of k1.fragen || []) for (const a of f.antworten) { delete a.mindest; delete a.hoechst; }
  return B.auswerten(k1, REGELN, { antworten, prioritaeten: prio }).rang[0];
}
const angezeigt = n => (typeof n === "number" ? Math.round(n) : null);
function alleKandidaten(kat, antworten) {
  const aus = [];
  for (const f of kat.fragen || []) {
    if ((f.antworten || []).length < 2) continue;
    for (const a of f.antworten) if (antworten[f.id] !== a.id) aus.push({ frage: f.id, antwort: a.id });
  }
  return aus;
}
/* Jede Zeile gleich dem Orakel (Zahl, Zustand, Abdeckung, delta) und genau die Kandidaten mit geänderter angezeigter Zahl */
function pruefeGegenOrakel(kat, m, antworten, prio) {
  const zeilen = B.alternativen(kat, REGELN, m, antworten, prio, 1000);
  const basis = orakel(kat, m, antworten, prio), a0 = angezeigt(basis.note);
  for (const z of zeilen) {
    const o = orakel(kat, m, Object.assign({}, antworten, { [z.frage]: z.antwort }), prio);
    assert.equal(z.note, o.note, `${z.frage}/${z.antwort}`);
    assert.equal(z.anzeige, angezeigt(o.note));
    assert.equal(z.art, o.art);
    assert.equal(z.abdeckung, o.abdeckung);
    assert.equal(z.delta, a0 === null || z.anzeige === null ? null : z.anzeige - a0);
  }
  const erwartet = alleKandidaten(kat, antworten).filter(c => {
    const o = orakel(kat, m, Object.assign({}, antworten, { [c.frage]: c.antwort }), prio), a1 = angezeigt(o.note);
    return a1 !== a0 || (a1 === null && o.art !== basis.art);
  }).map(c => c.frage + "/" + c.antwort).sort();
  assert.deepEqual(zeilen.map(z => z.frage + "/" + z.antwort).sort(), erwartet);
  return zeilen;
}

test("P2a-1 (17): Daten ohne neue Felder – kein Wurf, Fassung, Testquelle und Quellen leer", () => {
  const d = minimal(); B.datenPruefen(d);
  const k = d.kategorien[0];
  assert.equal(k.gewichte_version, null); assert.equal(k.testquelle, null);
  assert.deepEqual(k.quellen, {}); assert.deepEqual(k.modelle[0].belege, {});
  assert.equal(B.auswerten(k, d.regeln, {}).fassung, null);
  assert.doesNotThrow(beispiel);   // die Beispieldaten (erfunden, ohne Schema 2) bleiben gültig
});

test("P2a-1 (18): gewichte_version kaputt → null ohne Wurf; gültig → genau {nummer, stand}", () => {
  const faelle = [{ nummer: -1, stand: "2026-11-24" }, { nummer: 0, stand: "2026-11-24" }, { nummer: 10000, stand: "2026-11-24" },
    { nummer: 1.5, stand: "2026-11-24" }, { nummer: "1", stand: "2026-11-24" }, { nummer: true, stand: "2026-11-24" },
    { nummer: 1, stand: "24.11.2026" }, { nummer: 1, stand: "2026-02-30" }, { nummer: 1, stand: "2019-12-31" }, { nummer: 1 },
    [1], "1", 1, true];
  for (const f of faelle) {
    const d = minimal(); d.kategorien[0].gewichte_version = f;
    assert.doesNotThrow(() => B.datenPruefen(d), JSON.stringify(f));
    assert.equal(d.kategorien[0].gewichte_version, null, JSON.stringify(f));
  }
  const ok = minimal(); ok.kategorien[0].gewichte_version = { nummer: 3, stand: "2026-11-24", pruefsumme: "x", html: "<b>" };
  B.datenPruefen(ok);
  assert.deepEqual(ok.kategorien[0].gewichte_version, { nummer: 3, stand: "2026-11-24" });
  assert.deepEqual(B.auswerten(ok.kategorien[0], ok.regeln, {}).fassung, { nummer: 3, stand: "2026-11-24" });
});

test("P2a-1 (19): testquelle – unsichere URL oder Name → null; zusätzliche Schlüssel entfallen", () => {
  const gut = { name: "Beispieltester", url: "https://example.org/test/probe", methodik_url: "https://example.org/so-testen-wir", stand: "2026-11-24" };
  const mit = t => { const d = minimal(); d.kategorien[0].testquelle = t; B.datenPruefen(d); return d.kategorien[0].testquelle; };
  assert.deepEqual(mit(gut), gut);
  assert.deepEqual(Object.keys(mit(Object.assign({ punkte: 99, note: "sehr gut", urteil: "x" }, gut))).sort(),
    ["methodik_url", "name", "stand", "url"]);
  for (const kaputt of [{ url: "javascript:alert(1)" }, { url: "http://example.org/x" }, { methodik_url: "javascript:alert(1)" },
    { methodik_url: "https://user:pw@example.org/x" }, { name: "" }, { name: emoji(81) }, { stand: "2026-13-01" }, { name: undefined }]) {
    assert.equal(mit(Object.assign({}, gut, kaputt)), null, JSON.stringify(kaputt));
  }
  for (const nichtObjekt of [[gut], "x", 5, true]) assert.equal(mit(nichtObjekt), null);
  assert.deepEqual(mit(Object.assign({}, gut, { name: emoji(80) })).name, emoji(80));
});

test("P2a-1 (20): Quellen und Belege – kaputte Quelle, Beleg auf Feld ohne Wert und Verweis ins Leere entfallen", () => {
  const d = minimal(), k = d.kategorien[0];
  k.quellen = JSON.parse(`{"gut": {"titel": "Datenblatt", "url": "https://example.org/db", "gelesen": "2026-11-20", "extra": 1},
    "kaputt": {"titel": "Seite", "url": "javascript:alert(1)", "gelesen": "2026-11-20"},
    "ohne-datum": {"titel": "Seite", "url": "https://example.org/x", "gelesen": "20.11.2026"},
    "Gross": {"titel": "x", "url": "https://example.org/x", "gelesen": "2026-11-20"},
    "__proto__": {"titel": "x", "url": "https://example.org/x", "gelesen": "2026-11-20"}}`);
  k.modelle[0].belege = { a: "gut", b: "kaputt", groesse: "gut", unbekannt: "gut", c: "gibtsnicht" };
  k.modelle[0].werte.c = 1;
  B.datenPruefen(d);
  assert.deepEqual(Object.keys(k.quellen), ["gut"]);
  assert.deepEqual(k.quellen.gut, { titel: "Datenblatt", url: "https://example.org/db", gelesen: "2026-11-20" });
  // a: Wert + gültige Quelle; b: Quelle entfernt; groesse/unbekannt: kein Wert; c: Quelle unbekannt
  assert.deepEqual(k.modelle[0].belege, { a: "gut" });
  for (const nichtObjekt of [null, [1], "x", 3]) {
    const e = minimal(); e.kategorien[0].quellen = nichtObjekt; e.kategorien[0].modelle[0].belege = nichtObjekt;
    assert.doesNotThrow(() => B.datenPruefen(e));
    assert.deepEqual(e.kategorien[0].quellen, {}); assert.deepEqual(e.kategorien[0].modelle[0].belege, {});
  }
});

test("P2a-1 (21): Wert und Teilpunkte (und Beleg) gehören zusammen; Maße 0 < x ≤ 500; Wert nach Typ", () => {
  const bau = (werte, tp, belege = {}) => {
    const d = minimal(), k = d.kategorien[0];
    k.felder.push({ id: "hoehe_cm", name: "Höhe", einheit: "cm", typ: "zahl", gewicht: 6 }, { id: "form", name: "Form", einheit: "", typ: "stufe", gewicht: 4 });
    k.quellen = { q1: { titel: "Datenblatt", url: "https://example.org/db", gelesen: "2026-11-20" } };
    Object.assign(k.modelle[0], { werte: Object.assign({ a: 5, b: true, hoehe_cm: 9, form: "rund" }, werte),
      teilpunkte: Object.assign({ a: 90, b: 100, hoehe_cm: 70, form: 60 }, tp),
      belege: Object.assign({ a: "q1", b: "q1", hoehe_cm: "q1", form: "q1" }, belege) });
    B.datenPruefen(d);
    const m = k.modelle[0];
    return { m, abdeckung: B.bewerteModell(m, k, B.gewichte(k, {}), d.regeln).abdeckung };
  };
  const voll = bau({}, {});
  assert.equal(voll.abdeckung, 1);
  assert.deepEqual(Object.keys(voll.m.belege).sort(), ["a", "b", "form", "hoehe_cm"]);
  // Maßfeld: negativ, 0, Objekt, Text, 501 → Wert, Teilpunkte und Beleg weg, Abdeckung sinkt
  for (const schlecht of [-3, 0, { wert: 9 }, "9", 501, Infinity, true]) {
    const r = bau({ hoehe_cm: schlecht }, {});
    assert.equal("hoehe_cm" in r.m.werte, false, JSON.stringify(schlecht));
    assert.equal("hoehe_cm" in r.m.teilpunkte, false); assert.equal("hoehe_cm" in r.m.belege, false);
    assert.ok(r.abdeckung < 1, "Abdeckung sinkt: " + JSON.stringify(schlecht));
  }
  for (const gut of [0.5, 9, 500]) assert.equal(bau({ hoehe_cm: gut }, {}).m.werte.hoehe_cm, gut);
  // Nicht-Maßfeld mit Objektwert → Wert und Teilpunkte weg (Teilpunkte „hängen“ nicht allein)
  const o = bau({ a: { wert: 9 } }, {});
  assert.equal("a" in o.m.werte, false); assert.equal("a" in o.m.teilpunkte, false); assert.equal("a" in o.m.belege, false);
  // typfalscher Wert außerhalb der Maßfelder: Zahlfeld mit Text, Zahlfeld mit |x| ≥ 1e7, bool-Feld mit Text oder Zahl
  for (const [feld, schlecht] of [["a", "1400"], ["a", 1e7], ["a", true], ["b", "ja"], ["b", 3], ["form", 5], ["form", true], ["form", ""]]) {
    const r = bau({ [feld]: schlecht }, {});
    assert.equal(feld in r.m.werte, false, feld + " " + JSON.stringify(schlecht));
    assert.equal(feld in r.m.teilpunkte, false); assert.equal(feld in r.m.belege, false);
    assert.ok(r.abdeckung < 1);
  }
  assert.equal(bau({ a: 9999999 }, {}).m.werte.a, 9999999);
  // Stufenwert: 200 Codepunkte (Emoji, 400 UTF-16-Einheiten) bleibt, 201 entfällt
  assert.equal(bau({ form: emoji(200) }, {}).m.werte.form, emoji(200));
  assert.equal("form" in bau({ form: emoji(201) }, {}).m.werte, false);
  // Teilpunkt ohne Wert entfällt, Wert ohne Teilpunkt bleibt (R4-01)
  const ohneWert = bau({ hoehe_cm: undefined }, {});
  assert.equal("hoehe_cm" in ohneWert.m.teilpunkte, false);
  const tp101 = bau({}, { a: 101 });
  assert.equal(tp101.m.werte.a, 5); assert.equal("a" in tp101.m.teilpunkte, false);
  // gültige Daten: Werte und Teilpunkte bleiben unverändert (Beispieldaten), damit auch jede Note
  const roh = JSON.parse(fs.readFileSync(path.join(HIER, "vorlagen", "finder-beispiel.json"), "utf8")), vorher = kopie(roh);
  B.datenPruefen(roh);
  roh.kategorien.forEach((k, i) => k.modelle.forEach((m, j) => {
    assert.deepEqual(m.werte, vorher.kategorien[i].modelle[j].werte, m.id);
    assert.deepEqual(m.teilpunkte, vorher.kategorien[i].modelle[j].teilpunkte, m.id);
  }));
});

test("P2a-1 (22/28): alternativen – jede Zeile gleich dem Orakel, auch mit passt „nein“ (Air Fryer mit einem Garraum)", () => {
  const kat = mitModell(AFKAT(), afModell("na120-00"));
  const antworten = { personen: "p34", beilage: "nein", reinigung: "normal", material: "egal" };
  const zeilen = pruefeGegenOrakel(kat, kat.modelle[0], antworten, {});
  const ja = zeilen.find(z => z.frage === "beilage" && z.antwort === "ja");
  assert.ok(ja, "beilage → ja ändert die angezeigte Zahl");
  assert.equal(ja.passt, "nein");                 // mindest koerbe 2, das Modell hat einen Garraum
  assert.equal(ja.frage_text, kat.fragen.find(f => f.id === "beilage").text);
  assert.equal(ja.antwort_text, "Ja");
  // eine Zeile mit passt „nein“ gibt es in auswerten() nicht – dort fällt das Modell aus rang
  const r = B.auswerten(kat, REGELN, { antworten: Object.assign({}, antworten, { beilage: "ja" }) });
  assert.equal(r.rang.length, 0);
  // Gegenprobe: ein Modell mit zwei Garräumen passt
  const kat2 = mitModell(AFKAT(), afModell("zwei", { koerbe: 2 }, { koerbe: 100 }));
  const z2 = pruefeGegenOrakel(kat2, kat2.modelle[0], antworten, {});
  for (const z of z2.filter(x => x.frage === "beilage")) assert.equal(z.passt, "ok");
  // unbelegt: Wert fehlt, Anforderung (mindest volumen_l 7 bei „5 oder mehr“) ist nicht prüfbar
  const kat3 = mitModell(AFKAT(), afModell("ohne-volumen"));
  delete kat3.modelle[0].werte.volumen_l; delete kat3.modelle[0].teilpunkte.volumen_l;
  const z3 = pruefeGegenOrakel(kat3, kat3.modelle[0], antworten, {});
  const p5 = z3.find(z => z.frage === "personen" && z.antwort === "p5");
  if (p5) assert.equal(p5.passt, "unbelegt");
  assert.ok(z3.every(z => ["ok", "nein", "unbelegt"].includes(z.passt)));
  // alle Modelle der Beispieldaten (ohne Antworten und mit Reglern)
  for (const k of beispiel().kategorien) for (const m of k.modelle.slice(0, 3)) pruefeGegenOrakel(k, m, {}, {});
});

test("P2a-1 (23): Faktor ändert die Note nur um 0,3 (gleiche angezeigte Zahl) → keine Zeile", () => {
  const kat = { id: "p23", name: "P", felder: [{ id: "a", name: "A", einheit: "", typ: "zahl", gewicht: 50 }, { id: "b", name: "B", einheit: "", typ: "zahl", gewicht: 50 }],
    fragen: [{ id: "q", text: "?", antworten: [{ id: "std", text: "", gewichte: {} }, { id: "leicht", text: "", gewichte: { b: 1.05 } }] }], modelle: [] };
  const m = modell("m", { a: 60, b: 62 }, { a: 1, b: 2 }, 100);
  const n0 = orakel(kat, m, { q: "std" }).note, n1 = orakel(kat, m, { q: "leicht" }).note;
  assert.ok(n1 !== n0 && Math.abs(n1 - n0) < 0.5 && Math.round(n1) === Math.round(n0), `${n0} ${n1}`);
  assert.deepEqual(B.alternativen(kat, REGELN, m, { q: "std" }, {}), []);
});

test("P2a-1 (24): Alternative unter 70 % → Zeile ohne Note, vor Zeilen mit Zahl", () => {
  const kat = Object.assign(kopie(KAT), { modelle: [] });
  const m = modell("m", { a: 80 }, { a: 5 }, 100);
  const zeilen = pruefeGegenOrakel(kat, m, {}, {});
  assert.deepEqual(zeilen.map(z => z.antwort), ["mehr_b", "ohne_b"]);
  const z0 = zeilen[0];
  assert.equal(z0.note, null); assert.equal(z0.anzeige, null); assert.equal(z0.delta, null);
  assert.equal(z0.art, "zu_wenig_daten"); assert.equal(z0.abdeckung, 0.5);
  assert.equal(zeilen[1].delta, zeilen[1].anzeige - 69);   // Basis: 68,5 → 69
  assert.ok(zeilen[1].delta > 0);
});

test("P2a-1 (25): Alternative schaltet alle Felder aus → art „keine_merkmale“", () => {
  const kat = Object.assign(kopie(KAT), { felder: KAT.felder.map(f => Object.assign({}, f, { gewicht: f.id === "b" ? 20 : 0 })), modelle: [] });
  const m = modell("m", { b: 100 }, { b: true }, 100);
  const zeilen = pruefeGegenOrakel(kat, m, {}, {});
  assert.equal(zeilen.length, 1);
  assert.equal(zeilen[0].antwort, "ohne_b"); assert.equal(zeilen[0].art, "keine_merkmale");
  assert.equal(zeilen[0].note, null); assert.equal(zeilen[0].anzeige, null); assert.equal(zeilen[0].delta, null);
});

test("P2a-1 (26): höchstens 3 Zeilen; feste Reihenfolge nach |delta|, dann Frage, dann Antwort", () => {
  const alt = (id, gew) => ({ id: "q" + id, text: "Frage " + id, antworten: [{ id: "std", text: "", gewichte: {} }, { id: "plus", text: "plus", gewichte: gew }] });
  const kat = { id: "p26", name: "P", felder: [{ id: "a", name: "A", einheit: "", typ: "zahl", gewicht: 50 }, { id: "b", name: "B", einheit: "", typ: "zahl", gewicht: 50 }],
    fragen: [alt(1, { a: 2 }), alt(2, { a: 2 }), alt(3, { a: 2 }), alt(4, { a: 2 }), alt(5, { a: 4 }), alt(6, { b: 4 })], modelle: [] };
  const m = modell("m", { a: 90, b: 30 }, { a: 1, b: 2 }, 100);
  const antworten = { q1: "std", q2: "std", q3: "std", q4: "std", q5: "std", q6: "std" };
  const alle = pruefeGegenOrakel(kat, m, antworten, {});
  assert.deepEqual(alle.map(z => z.frage), ["q6", "q5", "q1", "q2", "q3", "q4"]);   // |−16| > 15 > 8 = 8 = 8 = 8
  assert.deepEqual(B.alternativen(kat, REGELN, m, antworten, {}).map(z => z.frage), ["q6", "q5", "q1"]);   // max 3 ist Standard
  assert.deepEqual(B.alternativen(kat, REGELN, m, antworten, {}, 2).map(z => z.frage), ["q6", "q5"]);
  assert.ok(alle[0].delta < 0 && alle[1].delta > 0);
  // gleiche |delta| innerhalb einer Frage: Antwortreihenfolge
  const k2 = { id: "p26b", name: "P", felder: kat.felder, modelle: [],
    fragen: [{ id: "q", text: "?", antworten: [{ id: "x", text: "", gewichte: {} }, { id: "y", text: "", gewichte: { a: 2 } }, { id: "z", text: "", gewichte: { a: 2 } }] }] };
  assert.deepEqual(B.alternativen(k2, REGELN, m, { q: "x" }, {}).map(z => z.antwort), ["y", "z"]);
});

test("P2a-1 (27): aktuelle Antwort nie Alternative; Frage mit einer Antwort ohne Zeile; ohne Fragen []", () => {
  const m = modell("m", { a: 80, b: 100 }, { a: 5, b: true }, 100);
  const mitAntwort = B.alternativen(KAT, REGELN, m, { f1: "mehr_b" }, {}, 1000);
  assert.equal(mitAntwort.some(z => z.frage === "f1" && z.antwort === "mehr_b"), false);
  assert.ok(mitAntwort.some(z => z.frage === "f1" && z.antwort === "ohne_b"));
  assert.equal(mitAntwort.some(z => z.frage === "f2"), false);          // f2 hat nur „halb_b“
  assert.deepEqual(B.alternativen(Object.assign({}, KAT, { fragen: [] }), REGELN, m, {}, {}), []);
  assert.deepEqual(B.alternativen(Object.assign({}, KAT, { fragen: undefined }), REGELN, m, undefined, undefined), []);
});

test("P2a-1 (29): modell, antworten, prio und Kategorie bleiben unverändert", () => {
  const kat = mitModell(AFKAT(), afModell("na120-00"));
  const antworten = { personen: "p34", beilage: "nein" }, prio = { volumen_l: 2, doerren: 0 };
  const vorher = kopie({ kat, antworten, prio });
  const eintrag = eintragFuer(kat, kat.modelle[0], antworten, prio);
  const eVorher = kopie(eintrag);
  B.alternativen(kat, REGELN, kat.modelle[0], antworten, prio);
  B.notenblatt(kat, REGELN, eintrag, antworten, prio);
  B.methodik({ regeln: REGELN, kategorien: [kat] });
  assert.deepEqual(kopie({ kat, antworten, prio }), vorher);
  assert.deepEqual(kopie(eintrag), eVorher);
});

test("P2a-1 (30): notenblatt – Air Fryer mit einem Garraum: Summe der Gewichte 86,96, Summe anteil 100; beilage=nein 100/100", () => {
  const kat = mitModell(AFKAT(), afModell("na120-00", {}, {}));
  const m = kat.modelle[0];
  const summe = l => l.reduce((s, x) => s + x, 0);
  const blatt = antw => {
    const e = eintragFuer(kat, m, antw, {});
    return { e, b: B.notenblatt(kat, REGELN, e, antw, {}) };
  };
  const ja = blatt({ beilage: "ja" });
  nah(summe(ja.e.beitraege.map(x => x.gewicht)) + summe(ja.e.fehlend.map(x => x.gewicht)), 86.9565, 1e-3);
  nah(summe(ja.b.merkmale.map(x => x.anteil)), 100);
  assert.deepEqual(ja.b.nicht_anwendbar, ["sync_funktion"]);
  assert.equal(ja.b.merkmale.some(x => x.feld === "sync_funktion"), false);
  const nein = blatt({ beilage: "nein" });
  nah(summe(nein.e.beitraege.map(x => x.gewicht)) + summe(nein.e.fehlend.map(x => x.gewicht)), 100);
  nah(summe(nein.b.merkmale.map(x => x.anteil)), 100);
  assert.deepEqual(nein.b.nicht_anwendbar, []);   // sync_funktion steht per Antwort schon auf Faktor 0 (kein Gewicht mehr)
  // Sortierung: anteil absteigend, bei Gleichstand Schemareihenfolge
  const ids = kat.felder.map(f => f.id);
  for (let i = 1; i < ja.b.merkmale.length; i++) {
    const a = ja.b.merkmale[i - 1], b = ja.b.merkmale[i];
    assert.ok(a.anteil > b.anteil + 1e-9 || (Math.abs(a.anteil - b.anteil) <= 1e-9 && ids.indexOf(a.feld) < ids.indexOf(b.feld)), a.feld + " " + b.feld);
  }
  // fehlend = IDs der unbelegten anwendbaren Felder; beleg null ohne Quelle
  const luecke = mitModell(AFKAT(), afModell("luecke"));
  delete luecke.modelle[0].teilpunkte.doerren; delete luecke.modelle[0].werte.doerren;
  const el = eintragFuer(luecke, luecke.modelle[0], {}, {});
  const bl = B.notenblatt(luecke, REGELN, el, {}, {});
  assert.deepEqual(bl.fehlend, ["doerren"]);
  const zeile = bl.merkmale.find(x => x.feld === "doerren");
  assert.equal(zeile.belegt, false);
  for (const f of ["wert", "teilpunkte", "beitrag_r", "beleg"]) assert.equal(zeile[f], null, f);
  const volumen = bl.merkmale.find(x => x.feld === "volumen_l");
  assert.equal(volumen.belegt, true); assert.equal(volumen.wert, 5); assert.equal(volumen.teilpunkte, 67.5);
  assert.equal(volumen.beleg, null); assert.equal(volumen.name, kat.felder[0].name); assert.equal(volumen.einheit, "l");
  // Note, R, Abdeckung stammen aus dem Eintrag (keine zweite Rechnung)
  assert.equal(bl.note, el.note); assert.equal(bl.R, el.R); assert.equal(bl.abdeckung, el.abdeckung); assert.equal(bl.art, el.art);
  assert.equal(bl.anzeige, Math.round(bl.note));
});

test("P2a-1 (30b): notenblatt – Beleg mit Quelle, tests, testquelle, fassung", () => {
  const d = { regeln: kopie(REGELN), kategorien: [Object.assign(AFKAT(), {
    gewichte_version: { nummer: 1, stand: "2026-11-24" },
    testquelle: { name: "Beispieltester", url: "https://example.org/t", methodik_url: "https://example.org/m", stand: "2026-11-24" },
    quellen: { q1: { titel: "Datenblatt", url: "https://example.org/db", gelesen: "2026-11-20" } },
    modelle: [Object.assign(afModell("m1"), { belege: { volumen_l: "q1" }, tests: [{ url: "https://example.org/t1", titel: "Test" }] })] })] };
  B.datenPruefen(d);
  const kat = d.kategorien[0], m = kat.modelle[0];
  const b = B.notenblatt(kat, d.regeln, eintragFuer(kat, m, {}, {}), {}, {});
  assert.deepEqual(b.merkmale.find(x => x.feld === "volumen_l").beleg, { titel: "Datenblatt", url: "https://example.org/db", gelesen: "2026-11-20" });
  assert.equal(b.merkmale.find(x => x.feld === "koerbe").beleg, null);
  assert.deepEqual(b.fassung, { nummer: 1, stand: "2026-11-24" });
  assert.equal(b.testquelle.name, "Beispieltester");
  assert.deepEqual(b.tests, [{ url: "https://example.org/t1", titel: "Test" }]);
  assert.ok(Array.isArray(b.alternativen));
});

test("P2a-1 (31): methodik übernimmt Abschlagswerte aus den Regeln, nicht aus Konstanten", () => {
  const regeln = kopie(REGELN);
  Object.assign(regeln.datenblatt_abschlag, { anker: 41, faktor: 0.9, abzug: 2, abdeckung_mindest: 0.6, spanne_plus_minus: 7 });
  const kat = mitModell(AFKAT(), afModell("m"));
  kat.gewichte_version = { nummer: 2, stand: "2026-11-25" };
  const me = B.methodik({ regeln, kategorien: [kat, KAT] });
  assert.deepEqual(me.abschlag, { anker: 41, faktor: 0.9, abzug: 2, abdeckung_mindest: 0.6, spanne_plus_minus: 7 });
  assert.equal(me.kategorien.length, 2);
  assert.deepEqual(me.kategorien[0].fassung, { nummer: 2, stand: "2026-11-25" });
  assert.equal(me.kategorien[1].fassung, null); assert.equal(me.kategorien[1].testquelle, null);
  assert.equal(me.kategorien[0].id, "airfryer");
  const g = me.kategorien[0].grundgewichte;
  nah(g.reduce((s, x) => s + x.anteil, 0), 100);
  assert.deepEqual(Object.keys(g[0]).sort(), ["anteil", "feld", "name"]);
  assert.equal(g[0].feld, "volumen_l"); nah(g[0].anteil, 25);   // Grundgewichte ohne Antworten und ohne Regler
  assert.equal(me.kategorien[1].grundgewichte.some(x => x.feld === "groesse"), false);   // Filterfelder (Gewicht 0) fehlen
});

test("P2a-1 (32): auswerten liefert die Fassung der Kategorie", () => {
  const kat = Object.assign(kopie(KAT), { gewichte_version: { nummer: 4, stand: "2026-11-24" }, modelle: [modell("m", { a: 90, b: 100 }, {}, 100)] });
  assert.deepEqual(B.auswerten(kat, REGELN, {}).fassung, { nummer: 4, stand: "2026-11-24" });
  kat.gewichte_version = { nummer: 0, stand: "2026-11-24" };   // auch ungeprüfte Kategorien: kaputte Fassung → null
  assert.equal(B.auswerten(kat, REGELN, {}).fassung, null);
  assert.equal(B.auswerten(KAT, REGELN, {}).fassung, null);
});

test("P2a-1 (33/A-1): alternativen rechnet mit denselben Reglern wie die Hauptnote", () => {
  const kat = mitModell(AFKAT(), afModell("m", { koerbe: 2 }, { koerbe: 100, doerren: 100 }));
  const antworten = { personen: "p34", beilage: "nein", reinigung: "normal", material: "egal" };
  const prio = { volumen_l: 3, leistung_w: 0, temp_max_c: 2, doerren: 0.5 };
  const mit = pruefeGegenOrakel(kat, kat.modelle[0], antworten, prio);
  assert.ok(mit.length > 0);
  // ohne prio wären die Zeilen andere (sonst bewiese der Test nichts)
  const ohne = B.alternativen(kat, REGELN, kat.modelle[0], antworten, undefined, 1000);
  assert.notDeepEqual(ohne.map(z => [z.frage, z.antwort, z.note]), mit.map(z => [z.frage, z.antwort, z.note]));
});

test("P2a-1 (34/A-2): notenblatt mit prio – Priorität + fehlender Wert + nicht anwendbares Feld; Zahlenbeispiel; Sonderfälle", () => {
  const summe = l => l.reduce((s, x) => s + x, 0);
  // Priorität, fehlender Wert und nicht anwendbares Feld zusammen
  const kat = mitModell(AFKAT(), afModell("m"));
  delete kat.modelle[0].teilpunkte.doerren; delete kat.modelle[0].werte.doerren;
  const antw = { beilage: "ja" }, prio = { volumen_l: 2 };
  const e = eintragFuer(kat, kat.modelle[0], antw, prio);
  const b = B.notenblatt(kat, REGELN, e, antw, prio);
  nah(summe(b.merkmale.map(x => x.anteil)), 100);
  nah(summe(b.merkmale.filter(x => x.belegt).map(x => x.beitrag_r)), e.R);
  assert.equal(b.persoenlich, true);
  assert.deepEqual(b.nicht_anwendbar, ["sync_funktion"]); assert.deepEqual(b.fehlend, ["doerren"]);
  assert.equal(B.notenblatt(kat, REGELN, eintragFuer(kat, kat.modelle[0], antw, {}), antw, {}).persoenlich, false);
  // persönlich nur, wenn ein Regler wirkt: Faktor 1, ungültige Faktoren und per Antwort abgeschaltete Felder zählen nicht
  const pers = p => B.notenblatt(kat, REGELN, eintragFuer(kat, kat.modelle[0], { beilage: "nein" }, p), { beilage: "nein" }, p).persoenlich;
  assert.equal(pers({ volumen_l: 1 }), false); assert.equal(pers({ koerbe: 3 }), false); assert.equal(pers({ volumen_l: 0 }), true);
  assert.equal(pers({ volumen_l: "2" }), false); assert.equal(pers({ volumen_l: -1 }), false); assert.equal(pers(undefined), false);
  // konkreter Prozentwert: g = 5 / 3 / 4 → 41,67 / 25 / 33,33 (nicht 0,4167)
  const k3 = { id: "p34", name: "P", fragen: [], modelle: [], felder: [["x", 5], ["y", 3], ["z", 4]].map(([id, g]) => ({ id, name: id, einheit: "", typ: "zahl", gewicht: g })) };
  const m3 = modell("m3", { x: 80, y: 60, z: 40 }, { x: 1, y: 2, z: 3 }, 100);
  const b3 = B.notenblatt(k3, REGELN, eintragFuer(k3, m3, {}, {}), {}, {});
  assert.deepEqual(b3.merkmale.map(x => x.feld), ["x", "z", "y"]);
  nah(b3.merkmale[0].anteil, 41.6667, 1e-3); nah(b3.merkmale[1].anteil, 33.3333, 1e-3); nah(b3.merkmale[2].anteil, 25, 1e-9);
  nah(summe(b3.merkmale.map(x => x.beitrag_r)), b3.R);
  // nur fehlende Merkmale: R null, jedes beitrag_r null, Summe anteil 100
  const bl = B.notenblatt(k3, REGELN, eintragFuer(k3, modell("leer", {}, {}, 100), {}, {}), {}, {});
  assert.equal(bl.R, null); assert.equal(bl.merkmale.length, 3);
  for (const x of bl.merkmale) { assert.equal(x.beitrag_r, null); assert.equal(x.belegt, false); }
  nah(summe(bl.merkmale.map(x => x.anteil)), 100);
  // keine_merkmale: alle Felder aus → merkmale leer, fehlend leer
  const aus = { x: 0, y: 0, z: 0 };
  const bk = B.notenblatt(k3, REGELN, eintragFuer(k3, m3, {}, aus), {}, aus);
  assert.equal(bk.art, "keine_merkmale"); assert.deepEqual(bk.merkmale, []); assert.deepEqual(bk.fehlend, []);
  // R4-01: gültiger Wert, Teilpunkte außerhalb 0..100 verworfen → Zeile nicht belegt, Feld in fehlend
  const d = { regeln: kopie(REGELN), kategorien: [Object.assign(AFKAT(), {
    quellen: { q1: { titel: "Datenblatt", url: "https://example.org/db", gelesen: "2026-11-20" } },
    modelle: [Object.assign(afModell("r4", { leistung_w: 1400 }, { leistung_w: 101 }), { belege: { leistung_w: "q1" } })] })] };
  B.datenPruefen(d);
  const kr = d.kategorien[0], br = B.notenblatt(kr, d.regeln, eintragFuer(kr, kr.modelle[0], {}, {}), {}, {});
  const zr = br.merkmale.find(x => x.feld === "leistung_w");
  assert.equal(kr.modelle[0].werte.leistung_w, 1400);
  assert.equal(zr.belegt, false);
  for (const f of ["wert", "teilpunkte", "beitrag_r", "beleg"]) assert.equal(zr[f], null, f);
  assert.ok(br.fehlend.includes("leistung_w"));
});

test("P2a-1 (35/45): PRIO_FAKTOREN und NICHT_ANWENDBAR sind festgeschrieben", () => {
  assert.deepEqual(B.PRIO_FAKTOREN, [0, 0.5, 1, 2, 3]);
  assert.deepEqual(Object.keys(B.NICHT_ANWENDBAR), ["airfryer"]);
  assert.deepEqual(Object.keys(B.NICHT_ANWENDBAR.airfryer), ["sync_funktion"]);
  assert.equal(B.nichtAnwendbar("airfryer", "sync_funktion", { koerbe: 1 }), true);
  assert.equal(B.nichtAnwendbar("airfryer", "sync_funktion", { koerbe: 2 }), false);
  assert.equal(B.nichtAnwendbar("airfryer", "koerbe", { koerbe: 1 }), false);
  assert.equal(B.nichtAnwendbar("fernseher", "sync_funktion", { koerbe: 1 }), false);
});

test("P2a-1 (36): alternativen – alle Regler aus → []; Air Fryer beilage=nein mit Reglern aus → Zeile für beilage=ja mit Note", () => {
  const m = modell("m", { a: 80, b: 100 }, { a: 5, b: true }, 100);
  assert.deepEqual(B.alternativen(KAT, REGELN, m, {}, { a: 0, b: 0 }, 1000), []);
  const kat = mitModell(AFKAT(), afModell("zwei", { koerbe: 2 }, { koerbe: 100, sync_funktion: 100 }));
  const aus = { volumen_l: 0, spuelmaschinenfest: 0, leistung_w: 0, sichtfenster: 0, beschichtung: 0, temp_max_c: 0, doerren: 0 };
  const antworten = { personen: "p34", beilage: "nein", reinigung: "normal", material: "egal" };
  assert.equal(orakel(kat, kat.modelle[0], antworten, aus).art, "keine_merkmale");
  const zeilen = pruefeGegenOrakel(kat, kat.modelle[0], antworten, aus);
  const ja = zeilen.find(z => z.frage === "beilage" && z.antwort === "ja");
  assert.ok(ja); assert.equal(ja.art, "datenblatt"); assert.equal(typeof ja.note, "number");
  assert.equal(ja.delta, null); assert.equal(ja.passt, "ok");
});

test("P2a-1 (43): alternativen – egal als Vorgabe; Frage ohne egal; null ohne Note", () => {
  const kat = Object.assign(kopie(KAT), { fragen: [
    { id: "f", text: "?", antworten: [{ id: "egal", text: "egal", gewichte: {} }, { id: "mehr", text: "mehr", gewichte: { b: 4 } }, { id: "aus", text: "aus", gewichte: { b: 0 } }] },
    { id: "g", text: "?", antworten: [{ id: "x", text: "x", gewichte: { a: 0 } }, { id: "y", text: "y", gewichte: { a: 3 } }] }] });
  const m = modell("m", { a: 40, b: 100 }, { a: 5, b: true }, 100);
  // egal ist wirksame Antwort (kommt von der Seite als antwortenWirksam): nie Kandidat
  const z1 = pruefeGegenOrakel(kat, m, { f: "egal", g: "y" }, {});
  assert.equal(z1.some(z => z.frage === "f" && z.antwort === "egal"), false);
  assert.ok(z1.some(z => z.frage === "f" && z.antwort === "aus"));
  // unbeantwortete Frage ohne egal: alle Antworten sind Kandidaten
  const z2 = pruefeGegenOrakel(kat, m, { f: "egal" }, {});
  assert.ok(z2.some(z => z.frage === "g" && z.antwort === "x") && z2.some(z => z.frage === "g" && z.antwort === "y"));
  // ohne Note: anzeige und delta null
  const ohneNote = modell("n", { b: 100 }, { b: true }, 100);
  const z3 = pruefeGegenOrakel(kat, ohneNote, { f: "egal", g: "y" }, {});
  assert.ok(z3.length >= 1);
  for (const z of z3.filter(x => x.note === null)) { assert.equal(z.anzeige, null); assert.equal(z.delta, null); }
});

test("P2a-1 (46): passt hängt nur von den Frageanforderungen ab, nicht von Oberflächenfiltern", () => {
  const kat = Object.assign(kopie(KAT), { fragen: [{ id: "g", text: "?", antworten: [
    { id: "x", text: "x", gewichte: {} },
    { id: "gross", text: "gross", gewichte: { a: 3 }, mindest: { groesse: 55 } },
    { id: "klein", text: "klein", gewichte: { a: 0.2 }, hoechst: { groesse: 43 } }] }] });
  const m = modell("m", { a: 40, b: 100 }, { a: 5, b: true, groesse: 50 }, 100);
  const zeilen = B.alternativen(kat, REGELN, m, { g: "x" }, {}, 1000);
  assert.equal(zeilen.find(z => z.antwort === "gross").passt, "nein");   // 50 < 55
  assert.equal(zeilen.find(z => z.antwort === "klein").passt, "nein");   // 50 > 43
  assert.equal(B.alternativen.length <= 6, true);                        // kein Parameter für Filter
  // Ohne Wert für groesse: unbelegt, nicht „nein“
  const m2 = modell("m2", { a: 40, b: 100 }, { a: 5, b: true }, 100);
  assert.equal(B.alternativen(kat, REGELN, m2, { g: "x" }, {}, 1000).find(z => z.antwort === "gross").passt, "unbelegt");
});

test("P2a-1 (44, Client): gemeinsamer Vertrag – Datum, URL, Namen, Quellen-ID", () => {
  // Datum: echtes Kalenderdatum ab 2020-01-01, keine obere Grenze im Client
  for (const gut of ["2020-01-01", "2026-02-28", "2024-02-29", "2099-12-31"]) assert.equal(B.quellDatum(gut), true, gut);
  for (const schlecht of ["2026-02-30", "2019-12-31", "2026-13-01", "2026-1-1", "26-01-01", "2026-01-01\n", "", null, 20260101, "2023-02-29"])
    assert.equal(B.quellDatum(schlecht), false, String(schlecht));
  // URL: https, ASCII, DNS-Name ohne Port, Userinfo, Punycode
  for (const u of ["https://example.org/", "https://example.org/pfad?x=1#a", "https://ab--c.de/", "https://www.sub.example.co.uk/x", "https://example.org"])
    assert.ok(B.sichereQuelle(u), u);
  const lang = n => "https://example.org/" + "a".repeat(n - 20);
  assert.equal(lang(2000).length, 2000); assert.ok(B.sichereQuelle(lang(2000)));
  assert.equal(B.sichereQuelle(lang(2001)), null);
  for (const u of ["http://example.org/", "https://user:pw@example.org/", "https://example.org:8443/", "https://example.org:443/",
    "https://999.999.999.999/", "https://192.168.0.1/", "https://localhost/", "https://Example.org/", "https://example.ORG/",
    "https://example.org/pfad/ä", "https://example.org/a b", "https://xn--a.de/", "https://xn--mnchen-3ya.de/", "https://a.xn--b.de/",
    "javascript:alert(1)", "//example.org/", "https://example.org/\n", "https://example.org/\t", "https://-a.de/", "https://a-.de/",
    "https://example.1/", "https://.example.org/", "", null, 5, {}])
    assert.equal(B.sichereQuelle(u), null, String(u));
  // Namen: Codepunkte statt UTF-16-Einheiten, nicht nur Leerraum
  assert.equal(B.quellName(emoji(200), 200), true); assert.equal(B.quellName(emoji(201), 200), false);
  assert.equal(B.quellName(emoji(80), 80), true); assert.equal(B.quellName(emoji(81), 80), false);
  for (const schlecht of ["", " ", " ", "\t", "﻿", 5, null, undefined]) assert.equal(B.quellName(schlecht, 200), false, JSON.stringify(schlecht));
  // Quellen-ID und Titel am Verwendungsort
  const d = minimal(), k = d.kategorien[0];
  const Q = JSON.stringify({ titel: "T", url: "https://example.org/x", gelesen: "2026-11-20" });
  const t201 = JSON.stringify({ titel: "x".repeat(201), url: "https://example.org/x", gelesen: "2026-11-20" });
  const e200 = JSON.stringify({ titel: emoji(200), url: "https://example.org/x", gelesen: "2026-11-20" });
  const e201 = JSON.stringify({ titel: emoji(201), url: "https://example.org/x", gelesen: "2026-11-20" });
  const leer = JSON.stringify({ titel: " ", url: "https://example.org/x", gelesen: "2026-11-20" });
  k.quellen = JSON.parse(`{"gut": ${Q}, "constructor": ${Q}, "prototype": ${Q}, "quelle\\n": ${Q}, "q-1_a": ${Q}, "toString": ${Q},
    "__proto__": ${Q}, "t201": ${t201}, "e200": ${e200}, "e201": ${e201}, "leer": ${leer}}`);
  B.datenPruefen(d);
  assert.deepEqual(Object.keys(k.quellen).sort(), ["e200", "gut", "q-1_a"]);
  assert.equal(Object.getPrototypeOf(k.quellen), Object.prototype);
});

// ---- Erstprüfung P2a-1 (Codex, docs/pruefungen/2026-11-26-p2a1-bau/bewertung-r1.md) ----

test("P2A1-01 (44): gültige 2000-Zeichen-URL, die new URL umkodiert, bleibt bis methodik und notenblatt erhalten", () => {
  // ' (Abfrage) und " (Pfad) kodiert new URL zu %27/%22 um; die geprüfte Zeichenfolge muss unverändert bleiben
  const urls = ["https://ab.de/?q=" + "'".repeat(1983), "https://ab.de/" + '"'.repeat(1986), "https://ab.de/{" + "a".repeat(1985)];
  for (const u of urls) {
    assert.equal(u.length, 2000);
    assert.equal(B.sichereQuelle(u), u, u.slice(0, 20));
    const d = minimal(), k = d.kategorien[0];
    k.testquelle = { name: "Beispieltester", url: u, methodik_url: u, stand: "2026-11-24" };
    k.quellen = { q1: { titel: "T", url: u, gelesen: "2026-11-20" } };
    k.modelle[0].belege = { a: "q1" };
    B.datenPruefen(d);
    for (let lauf = 0; lauf < 2; lauf++) {   // zweiter Lauf: datenPruefen ist auf geprüften Daten ohne Wirkung
      assert.deepEqual(k.testquelle, { name: "Beispieltester", url: u, methodik_url: u, stand: "2026-11-24" });
      assert.equal(k.quellen.q1.url, u); assert.deepEqual(k.modelle[0].belege, { a: "q1" });
      assert.deepEqual(B.methodik(d).kategorien[0].testquelle, k.testquelle);
      const nb = B.notenblatt(k, d.regeln, eintragFuer(k, k.modelle[0], {}, {}), {}, {});
      assert.deepEqual(nb.testquelle, k.testquelle);
      assert.equal(nb.merkmale.find(x => x.feld === "a").beleg.url, u);
      B.datenPruefen(d);
    }
  }
});

test("P2A1-02 (44): Freigabe nach dem Produktdatenstand (stand später als d.stand, nicht in der Zukunft) → gültig", () => {
  const d = minimal(); d.stand = "2026-11-20";
  d.kategorien[0].gewichte_version = { nummer: 2, stand: "2026-11-25" };
  d.kategorien[0].testquelle = { name: "T", url: "https://example.org/t", methodik_url: "https://example.org/m", stand: "2026-11-25" };
  B.datenPruefen(d);
  assert.ok(d.kategorien[0].gewichte_version.stand > d.stand);
  assert.deepEqual(d.kategorien[0].gewichte_version, { nummer: 2, stand: "2026-11-25" });
  assert.equal(d.kategorien[0].testquelle.stand, "2026-11-25");
  assert.deepEqual(B.auswerten(d.kategorien[0], d.regeln, {}).fassung, { nummer: 2, stand: "2026-11-25" });
  // gleicher Tag und früher bleiben ebenso gültig
  for (const s of ["2026-11-20", "2026-11-01"]) {
    const e = minimal(); e.stand = "2026-11-20"; e.kategorien[0].gewichte_version = { nummer: 1, stand: s };
    B.datenPruefen(e); assert.deepEqual(e.kategorien[0].gewichte_version, { nummer: 1, stand: s });
  }
});

test("P2A1-03 (21): echte Daten – datenPruefen ändert keinen Wert, Teilpunkt, Beleg und keine Note", () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "kb-p2a1-"));
  try {
    const ziel = path.join(tmp, "finder-daten.json");
    execFileSync(process.env.PYTHON || "python", ["-I", path.join(PROJEKT, "werkzeuge", "datenbank.py"), "bauen", ziel], { stdio: "pipe" });
    const roh = JSON.parse(fs.readFileSync(ziel, "utf8")), vorher = kopie(roh);
    // r3 (P2A1-03): Sollzahlen vorab und unabhängig von den Prüfschleifen aus den Rohdaten:
    // Einträge = Σ Modelle, Vergleiche = Σ Modelle × (1 Vorgabe + Zahl aller Antworten)
    const sollModelle = vorher.kategorien.reduce((s, k) => s + k.modelle.length, 0);
    const sollNoten = vorher.kategorien.reduce((s, k) =>
      s + k.modelle.length * (1 + (k.fragen || []).reduce((t, f) => t + f.antworten.length, 0)), 0);
    B.datenPruefen(roh);
    assert.equal(roh.kategorien.length, vorher.kategorien.length);
    let modelle = 0, noten = 0;
    roh.kategorien.forEach((k, i) => {
      const alt = vorher.kategorien[i];
      assert.equal(k.id, alt.id); assert.equal(k.modelle.length, alt.modelle.length, k.id);
      assert.deepEqual(k.testquelle || null, alt.testquelle || null, k.id);
      assert.deepEqual(k.quellen, alt.quellen || {}, k.id);
      k.modelle.forEach((m, j) => {
        const a = alt.modelle[j];
        assert.equal(m.id, a.id);
        assert.deepEqual(m.werte, a.werte, m.id); assert.deepEqual(m.teilpunkte, a.teilpunkte, m.id);
        assert.deepEqual(m.belege, a.belege || {}, m.id);
        modelle++;
      });
      // Noten: Vorgabe und jede einzelne Antwort, jedes Modell direkt über bewerteModell (r2, P2A1-03: auch Modelle, die
      // eine Anforderung aus der Rangliste nimmt), je Seite mit eigenen Gewichten; Zahl der Vergleiche aus den Rohdaten
      const eingaben = [{}].concat(...(alt.fragen || []).map(f => f.antworten.map(x => ({ [f.id]: x.id }))));
      for (const antworten of eingaben) {
        const gNeu = B.gewichte(k, antworten), gAlt = B.gewichte(alt, antworten);
        alt.modelle.forEach((a, j) => {
          const neu = B.bewerteModell(k.modelle[j], k, gNeu, roh.regeln), vorh = B.bewerteModell(a, alt, gAlt, vorher.regeln);
          assert.equal(neu.note, vorh.note, a.id + " " + JSON.stringify(antworten));
          assert.equal(neu.art, vorh.art, a.id + " " + JSON.stringify(antworten));
          noten++;
        });
      }
    });
    assert.equal(modelle, sollModelle); assert.equal(noten, sollNoten);
    assert.ok(modelle > 300 && noten > 5000, modelle + " Modelle, " + noten + " Noten");
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
});

test("P2A1-04 (34): persoenlich nur, wenn ein Regler auf ein für dieses Modell anwendbares Feld wirkt", () => {
  const pers = (kat, antw, p) => B.notenblatt(kat, REGELN, eintragFuer(kat, kat.modelle[0], antw, p), antw, p).persoenlich;
  const ein = mitModell(AFKAT(), afModell("ein"));                                   // ein Garraum: sync_funktion nicht anwendbar
  const zwei = mitModell(AFKAT(), afModell("zwei", { koerbe: 2 }, { koerbe: 100 }));  // zwei Garräume: anwendbar
  const antw = { beilage: "ja" };
  assert.equal(pers(ein, antw, { sync_funktion: 3 }), false);
  assert.equal(pers(ein, antw, { sync_funktion: 0 }), false);
  assert.equal(pers(ein, antw, { sync_funktion: 3, volumen_l: 2 }), true);
  assert.equal(pers(zwei, antw, { sync_funktion: 3 }), true);
  // Gegenprobe: die Note des Ein-Garraum-Modells ist mit und ohne diesen Regler gleich
  assert.equal(eintragFuer(ein, ein.modelle[0], antw, { sync_funktion: 3 }).note, eintragFuer(ein, ein.modelle[0], antw, {}).note);
});

/* ---- P2a-2 (Entwurf §9.1, §9.3, §9.9): Fassung 1 ändert keine Note, umlaufende bewertung.js, Rechnung R2-01 ---- */
const PY = process.env.PYTHON || "python";
const git = (...a) => execFileSync("git", ["-C", PROJEKT, ...a], { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
const VOR_P2A2 = "dbfdca67a49387371846d2587f69363574175bed";   // letzter Stand vor P2a-2 (ohne gewichte_version)
const MIT_FASSUNG1 = "6bc96605a622fe05d2b10c358d39f3916eaab0ce";   // erster Stand mit Fassung 1 (P2a-2 gebaut)
const bauNeu = ziel => execFileSync(PY, ["-I", path.join(PROJEKT, "werkzeuge", "datenbank.py"), "bauen", ziel], { stdio: "pipe" });
/* Bau mit Werkzeug und Schema eines Commits, aber den heutigen Produktdaten und Freigaben (gleiche Eingabe, alte Regeln) */
function bauMitStand(commit, tmp, ziel) {
  const w = path.join(tmp, "stand");
  fs.mkdirSync(path.join(w, "werkzeuge"), { recursive: true }); fs.mkdirSync(path.join(w, "daten", "schema"), { recursive: true });
  fs.writeFileSync(path.join(w, "werkzeuge", "datenbank.py"), git("show", commit + ":werkzeuge/datenbank.py"));
  fs.writeFileSync(path.join(w, "daten", "schema", "kategorien.json"), git("show", commit + ":daten/schema/kategorien.json"));
  fs.copyFileSync(path.join(PROJEKT, "daten", "quellen.json"), path.join(w, "daten", "quellen.json"));
  fs.cpSync(path.join(PROJEKT, "daten", "produkte"), path.join(w, "daten", "produkte"), { recursive: true });
  execFileSync(PY, ["-I", path.join(w, "werkzeuge", "datenbank.py"), "bauen", ziel], { stdio: "pipe" });
}
/* Vorgabe und jede einzelne Antwort (wie Test 21), für jedes Modell direkt über bewerteModell */
const eingabenVon = k => [{}].concat(...(k.fragen || []).map(f => f.antworten.map(x => ({ [f.id]: x.id }))));

test("P2a-2 (42): Fassung 1 – alle Modelle, alle Vorgaben, Note vor und nach dem Bau gleich", () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "kb-p2a2-42-"));
  try {
    bauMitStand(VOR_P2A2, tmp, path.join(tmp, "vor.json")); bauNeu(path.join(tmp, "nach.json"));
    const vor = B.datenPruefen(JSON.parse(fs.readFileSync(path.join(tmp, "vor.json"), "utf8")));
    const nach = B.datenPruefen(JSON.parse(fs.readFileSync(path.join(tmp, "nach.json"), "utf8")));
    const sollNoten = nach.kategorien.reduce((s, k) => s + k.modelle.length * eingabenVon(k).length * 2, 0);
    let noten = 0, kategorien = 0;
    assert.deepEqual(nach.regeln, vor.regeln);
    nach.kategorien.forEach((k, i) => {
      const a = vor.kategorien[i];
      assert.equal(k.id, a.id);
      assert.equal(a.gewichte_version, null, "vorher ohne Fassung");
      assert.deepEqual(k.gewichte_version, { nummer: 1, stand: "2026-11-26" }, k.id);   // F-1: Fassung 1 freigegeben
      kategorien++;
      assert.deepEqual(k.felder, a.felder, k.id); assert.deepEqual(k.fragen, a.fragen, k.id);
      assert.equal(k.modelle.length, a.modelle.length, k.id);
      const prio = { [k.felder.find(f => f.gewicht > 0).id]: 3 };   // auch mit gesetztem Regler (G1)
      for (const antworten of eingabenVon(k)) for (const p of [undefined, prio]) {
        const gN = B.gewichte(k, antworten, p), gV = B.gewichte(a, antworten, p);
        k.modelle.forEach((m, j) => {
          const n = B.bewerteModell(m, k, gN, nach.regeln), v = B.bewerteModell(a.modelle[j], a, gV, vor.regeln);
          assert.equal(m.id, a.modelle[j].id);
          assert.equal(n.note, v.note, m.id + " " + JSON.stringify(antworten)); assert.equal(n.art, v.art, m.id);
          noten++;
        });
      }
    });
    assert.equal(kategorien, 14); assert.equal(noten, sollNoten); assert.ok(noten > 10000, noten + " Noten");
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
});

/* §9.1/§9.9 (37): jede umlaufende bewertung.js auf der neuen Datei gegen die Datei aus Werkzeug und Schema von
   `herkunft` (dazu die heutigen Produktdaten). Keine Annahme über Fassungsmetadaten der Vergleichsdatei (P2A2-BAU-02):
   verglichen werden nur Werfen, Modellzahl, Note und Art je Client. */
// §9.1: b24c18f wirft schon heute („klassen“); die Erwartung ist an diesen Blob gebunden, nicht an eine Anzahl (P2A2-BAU-02)
const ALTFALL_B24C18F = "4f725603c46208eb562fe780640a271b87751f3a";

// opts.verlauf: Blob-Liste statt des gh-pages-Verlaufs; opts.kuerzen: je Kategorie nur das erste Modell (beide Dateien)
// – beides nur für die Probe zu P2A2-BAU-02 r3 (kleiner Verlauf, kleine Datei)
function vergleich37(herkunft, zusatz = [], opts = {}) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "kb-p2a2-37-"));
  try {
    bauNeu(path.join(tmp, "neu.json"));
    const kurz = d => { if (opts.kuerzen) d.kategorien.forEach(k => { k.modelle = k.modelle.slice(0, 1); }); return d; };
    const neu = kurz(JSON.parse(fs.readFileSync(path.join(tmp, "neu.json"), "utf8")));
    bauMitStand(herkunft, tmp, path.join(tmp, "alt.json"));
    const alt = kurz(JSON.parse(fs.readFileSync(path.join(tmp, "alt.json"), "utf8")));
    // §9.1: alle Blobs von bewertung.js im gh-pages-Verlauf, dazu G1 und die heutige Fassung auf main
    const blobs = new Set(opts.verlauf || git("log", "--format=%H", "origin/gh-pages", "--", "bewertung.js").split("\n").filter(Boolean)
      .map(c => git("rev-parse", c + ":bewertung.js").trim()));
    blobs.add(git("rev-parse", "0996e86:app/finder/bewertung.js").trim());
    // P2A2-BAU-02 r3: keine Mindestgröße des Verlaufs; gebunden ist nur der dokumentierte Altfall
    assert.ok(blobs.has(ALTFALL_B24C18F), "Altfall b24c18f im Verlauf");
    const fassungen = [...blobs].map(b => ["blob " + b.slice(0, 7), git("cat-file", "blob", b), b]);
    fassungen.push(["main", fs.readFileSync(path.join(PROJEKT, "app", "finder", "bewertung.js"), "utf8"), null]);
    fassungen.push(...zusatz);
    // P2A2-BAU-02 r3: statt absoluter Schwellen vollständige Bearbeitung – jede ermittelte Fassung verglichen, bei
    // rechnenden Fassungen jede Kategorie, jedes Modell, jede Eingabe (Vorgabe, jede Antwort, mit und ohne Regler)
    let gerechnet = 0, soll = 0, bearbeitet = 0;
    fassungen.forEach(([name, text, blob], i) => {
      const datei = path.join(tmp, `bewertung-${i}.js`);
      fs.writeFileSync(datei, text);
      const V = require(datei);
      const lauf = d => { try { return { d: V.datenPruefen(kopie(d)) }; } catch (e) { return { fehler: e.message }; } };
      const n = lauf(neu), a = lauf(alt);
      assert.equal(n.fehler, a.fehler, name + ": gleiches Werfen");
      if (blob === ALTFALL_B24C18F) assert.ok(n.fehler, "b24c18f wirft weiter (klassen, §9.1)");
      bearbeitet++;
      if (name === "main") assert.ok(!n.fehler, "main rechnet auf der neuen Datei: " + n.fehler);
      if (n.fehler) return;
      assert.equal(n.d.kategorien.length, a.d.kategorien.length, name + ": Kategorienzahl");
      soll += n.d.kategorien.reduce((s, k) => s + k.modelle.length * eingabenVon(k).length * 2, 0);
      n.d.kategorien.forEach((k, ki) => {
        const ak = a.d.kategorien[ki];
        assert.equal(k.modelle.length, ak.modelle.length, name + " " + k.id);
        const prio = V.PRIO_FAKTOREN ? { [k.felder.find(f => f.gewicht > 0).id]: 3 } : undefined;
        for (const antworten of eingabenVon(k)) for (const p of [undefined, prio]) {
          const gN = V.gewichte(k, antworten, p), gA = V.gewichte(ak, antworten, p);
          k.modelle.forEach((m, j) => {
            const x = V.bewerteModell(m, k, gN, n.d.regeln), y = V.bewerteModell(ak.modelle[j], ak, gA, a.d.regeln);
            assert.equal(x.note, y.note, name + " " + m.id); assert.equal(x.art, y.art, name + " " + m.id);
            gerechnet++;
          });
        }
      });
    });
    assert.equal(bearbeitet, fassungen.length, "jede Fassung verglichen");
    assert.equal(gerechnet, soll, "jede Eingabe jeder rechnenden Fassung verglichen");
    return gerechnet;
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
}

test("P2a-2 (37): jede umlaufende bewertung.js verhält sich auf der neuen Datei wie mit den Live-Daten", t => {
  // Vergleichsdatei aus der herkunft der Datei auf gh-pages (lokaler Ref, offline); der verwendete Seitenstand
  // wird ausgegeben, damit ein veralteter Ref im Lauf sichtbar ist (P2A2-BAU-02).
  const seite = git("rev-parse", "origin/gh-pages").trim();
  const live = JSON.parse(git("show", seite + ":finder-daten.json").replace(/^﻿/, ""));
  assert.match(String(live.herkunft), /^[0-9a-f]{40}$/, "herkunft der Live-Datei");
  t.diagnostic(`gh-pages ${seite}, herkunft ${live.herkunft}`);
  vergleich37(live.herkunft);
});

test("P2a-2 (37): nach Veröffentlichung von Fassung 1 – Vergleich gegen eine Herkunft mit gewichte_version", () => {
  // P2A2-BAU-02: so sieht der Live-Stand aus, sobald dieser Bau online ist. Dazu zwei weitere veröffentlichte Fassungen
  // mit gleichem Verhalten wie vorhandene (nur Kommentar verschieden): eine werfende und eine rechnende. Keine Annahme
  // über die Zahl werfender Fassungen, Kriterium ist allein der Vergleich je Fassung.
  const text = b => git("cat-file", "blob", b);
  const main = fs.readFileSync(path.join(PROJEKT, "app", "finder", "bewertung.js"), "utf8");
  const KOPIE = String.fromCharCode(10) + "// Kopie" + String.fromCharCode(10);
  vergleich37(MIT_FASSUNG1, [["Kopie b24c18f", text(ALTFALL_B24C18F) + KOPIE, null],
                             ["Kopie main", main + KOPIE, null]]);
});

test("P2a-2 (37): kleiner Verlauf und kleine Datei – Kriterium ist der Vergleich, keine Mindestgröße (P2A2-BAU-02 r3)", () => {
  // Speicherproben aus dem Bericht r2: Verlauf nur mit dem Altfall (dazu G1 und main), einmal mit allen Modellen,
  // einmal mit je einem Modell pro Kategorie; beide Male verhält sich jede Fassung auf beiden Dateien gleich
  // r3-Hinweis: keine Größenbeziehung zwischen beiden Läufen (bei schon kleinen Dateien wären sie gleich groß)
  vergleich37(MIT_FASSUNG1, [], { verlauf: [ALTFALL_B24C18F] });
  vergleich37(MIT_FASSUNG1, [], { verlauf: [ALTFALL_B24C18F], kuerzen: true });
  assert.throws(() => vergleich37(MIT_FASSUNG1, [], { verlauf: [] }), /Altfall b24c18f/, "ohne Altfall rot");
});

test("P2a-2 (40): R2-01 – Feldreihenfolge kippt die angezeigte Zahl an der ,5-Grenze", () => {
  const felder = [8, 3, 7, 11, 5].map((g, i) => ({ id: "f" + i, name: "F" + i, einheit: "", typ: "zahl", gewicht: g }));
  const tp = { f0: 59.8, f1: 31.5, f2: 64.6, f3: 22.9, f4: 16.6 };
  const note = fs => { const k = { id: "r", name: "R", felder: fs, fragen: [] };
    return B.bewerteModell({ id: "m", teilpunkte: tp, werte: {} }, k, B.gewichte(k, {}), REGELN); };
  const vorwaerts = note(felder), rueckwaerts = note(kopie(felder).reverse());
  assert.equal(vorwaerts.note, 38.5); assert.equal(Math.round(vorwaerts.note), 39);
  assert.equal(rueckwaerts.note, 38.499999999999986); assert.equal(Math.round(rueckwaerts.note), 38);
});
