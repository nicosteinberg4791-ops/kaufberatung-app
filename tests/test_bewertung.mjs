// Tests für app/finder/bewertung.js (node:test, nur eingebaute Module). Aufruf: node --test tests/test_bewertung.mjs
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
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
  const d = { regeln: alt, kategorien: [{ id: "probe", name: "Probe", felder: kopie(KAT.felder), fragen: kopie(KAT.fragen), modelle: [modell("m", { a: 100, b: 100 }, {}, 100)] }] };
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
  modelle: [modell("m", { a: 90, b: 100 }, {}, 100)] }] });

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
  d.kategorien[0].modelle[0].werte = { a: { toString: null }, b: 3, c: true, e: "gut", f: Infinity, g: "x".repeat(201), h: null };
  B.datenPruefen(d);
  assert.deepEqual(d.kategorien[0].modelle[0].werte, { b: 3, c: true, e: "gut" });
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
