/* Bewertungslogik der Startseite „Finden & Vergleichen“ (reine Rechnung, kein DOM).
   Browser: window.KBBewertung · Node: require("./bewertung.js").
   Regeln: daten/schema/kategorien.json (regeln, datenblatt_abschlag, aufpreis_regeln), Begründung docs/punkteschema.md.
   D12 (24.11.2026): keine Kappung, keine Klassenwörter; ältere Daten mit „klassen“/„kappung“ werden still ignoriert.
   Eingang: App-Daten aus werkzeuge/datenbank.py bauen() (finder-daten.json), optional finder-preise.json.
   Festlegungen, die das Schema offen lässt (siehe Kopf der jeweiligen Funktion):
   - Rangfolge nach der angezeigten (gerundeten) Note; bei gleicher angezeigter Note steht das günstigere Modell vorn.
   - Modell A (Empfehlung) braucht immer einen Preis und muss alle Anforderungen belegt erfüllen; gibt es keins, zählt
     das beste im Budget mit „nicht belegt“-Markierung (Status "unbelegt"); dann ein passendes Modell im Budget ohne
     Note ("ohne_note"); passt nichts ins Budget, das beste über Budget ("ueber_budget").
   - B (Aufpreis) und C (Spar) müssen alle Anforderungen belegt erfüllen, eine Note und einen Preis haben.
   - Schwellen werden mit ungerundeten Werten und einer Toleranz von 1e-9 geprüft (Gleitkomma bei Cent-Preisen).
   P2a-1 (docs/recherche-ux/p2-entwurf.md): alternativen (Note bei anderer Antwort), notenblatt, methodik und die
   Prüfung der neuen Metadaten (gewichte_version, testquelle, quellen, belege) in datenPruefen; alles nur Rechnung, kein DOM. */
(function (wurzel, fabrik) {
  "use strict";
  const api = fabrik();
  if (typeof module === "object" && module && module.exports) module.exports = api;
  else wurzel.KBBewertung = api;
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const EPS = 1e-9;
  const ge = (a, b) => a >= b - EPS;
  const le = (a, b) => a <= b + EPS;
  const istZahl = x => typeof x === "number" && isFinite(x);
  const istObjekt = x => x !== null && typeof x === "object" && !Array.isArray(x);
  const DATUM = /^\d{4}-\d{2}-\d{2}$/;
  const eigen = (o, k) => o !== null && typeof o === "object" && Object.prototype.hasOwnProperty.call(o, k);

  /* Nicht anwendbare Felder (regeln.nicht_anwendbar): Gewicht entfällt ohne Abdeckungsverlust.
     Das Datenformat kennt dafür keinen eigenen Wert; die bekannten Fälle stehen hier. */
  const NICHT_ANWENDBAR = {
    airfryer: { sync_funktion: w => w.koerbe === 1 },
  };
  function nichtAnwendbar(katId, fid, werte) {
    // R3-02: nur eigene Einträge und aufrufbare Regeln (Kennung "constructor"/"prototype" trifft sonst den Prototyp)
    const k = eigen(NICHT_ANWENDBAR, katId) ? NICHT_ANWENDBAR[katId] : null;
    const r = k && eigen(k, fid) ? k[fid] : null;
    return !!(typeof r === "function" && werte && r(werte));
  }

  /* Gewichte nach Antworten: Faktoren aller gewählten Antworten multiplizieren, Faktor 0 schaltet ab,
     Filterfelder (Gewicht 0) bleiben draußen, Rest auf Summe 100 normieren. antworten = {frageId: antwortId}.
     G1: prio = {feldId: Faktor} aus den Prioritäten-Reglern (PRIO_FAKTOREN, 0 = aus) wirkt zusätzlich, nur auf Felder
     mit Gewicht > 0; ungültige Faktoren (keine Zahl, negativ) zählen als 1. */
  const PRIO_FAKTOREN = [0, 0.5, 1, 2, 3];   // Stufen aus / weniger / normal / mehr / viel mehr
  function gewichte(kat, antworten, prio) {
    const faktor = Object.create(null);   // R3-02: ohne Prototyp, Schlüssel kommen aus fremden Daten
    for (const frage of kat.fragen || []) {
      const aid = antworten && antworten[frage.id];
      const antw = (frage.antworten || []).find(a => a.id === aid);
      if (!antw) continue;
      for (const [fid, f] of Object.entries(antw.gewichte || {})) {
        if (istZahl(f) && f >= 0) faktor[fid] = (fid in faktor ? faktor[fid] : 1) * f;
      }
    }
    const roh = {};
    let summe = 0;
    for (const feld of kat.felder || []) {
      if (!istZahl(feld.gewicht) || feld.gewicht <= 0) continue;
      const p = eigen(prio, feld.id) && istZahl(prio[feld.id]) && prio[feld.id] >= 0 ? prio[feld.id] : 1;
      const g = feld.gewicht * (feld.id in faktor ? faktor[feld.id] : 1) * p;
      if (g > 0) { roh[feld.id] = g; summe += g; }
    }
    const aus = {};
    if (summe > 0) for (const [fid, g] of Object.entries(roh)) aus[fid] = g / summe * 100;
    return aus;
  }

  /* Anforderungen aus Antworten (mindest, hoechst) und Oberflächenfiltern.
     filter = {feldId: {mindest?: Zahl, hoechst?: Zahl, liste?: [Stufen], ja?: true}}.
     Ergebnis: [{feld, art: "mindest"|"hoechst"|"ja"|"liste", wert, quelle: "frage"|"filter"}]. */
  function anforderungen(kat, antworten, filter) {
    const liste = [];
    const dazu = (feld, art, wert, quelle) => liste.push({ feld, art, wert, quelle });
    for (const frage of kat.fragen || []) {
      const aid = antworten && antworten[frage.id];
      const antw = (frage.antworten || []).find(a => a.id === aid);
      if (!antw) continue;
      for (const [fid, w] of Object.entries(antw.mindest || {})) {
        if (istZahl(w)) dazu(fid, "mindest", w, "frage");
        else if (w === true) dazu(fid, "ja", true, "frage");
        else if (Array.isArray(w)) dazu(fid, "liste", w.slice(), "frage");
      }
      for (const [fid, w] of Object.entries(antw.hoechst || {})) if (istZahl(w)) dazu(fid, "hoechst", w, "frage");
    }
    for (const [fid, f] of Object.entries(filter || {})) {
      if (!istObjekt(f)) continue;
      if (istZahl(f.mindest)) dazu(fid, "mindest", f.mindest, "filter");
      if (istZahl(f.hoechst)) dazu(fid, "hoechst", f.hoechst, "filter");
      if (Array.isArray(f.liste) && f.liste.length) dazu(fid, "liste", f.liste.slice(), "filter");
      if (f.ja === true) dazu(fid, "ja", true, "filter");
    }
    return liste;
  }

  /* Eine Anforderung gegen die Werte eines Modells: "ok" | "nein" | "unbelegt" (Wert fehlt oder passt nicht zum Typ). */
  function pruefe(werte, anf) {
    const w = eigen(werte, anf.feld) ? werte[anf.feld] : undefined;
    if (w === undefined || w === null) return "unbelegt";
    switch (anf.art) {
      case "mindest": return istZahl(w) ? (ge(w, anf.wert) ? "ok" : "nein") : "unbelegt";
      case "hoechst": return istZahl(w) ? (le(w, anf.wert) ? "ok" : "nein") : "unbelegt";
      case "ja": return typeof w === "boolean" ? (w ? "ok" : "nein") : "unbelegt";
      case "liste": return anf.wert.indexOf(w) >= 0 ? "ok" : "nein";
      default: return "unbelegt";
    }
  }

  /* Datenblatt-Note mit Abschlag: anker + (R − anker) × faktor − abzug − (1 − abdeckung) × 20 (D12: ohne Kappung),
     unter abdeckung_mindest keine Note (null). Ergebnis auf 0..100 begrenzt. */
  function datenblattNote(R, abdeckung, db) {
    if (!istZahl(R) || !istZahl(abdeckung)) return null;
    if (abdeckung < db.abdeckung_mindest - EPS) return null;
    const n = db.anker + (R - db.anker) * db.faktor - db.abzug - (1 - abdeckung) * 20;
    return Math.max(0, Math.min(100, n));
  }

  /* Ein Modell bewerten: Rohwert R über belegte Felder, Abdeckung, angezeigte Note, Beiträge je Feld und
     fehlende bewertete Felder (fehlend, nach Gewicht absteigend).
     Getestete Modelle nur, wenn ein Testeintrag eine Zahl "punkte" (0..100) trägt (heute: Tests sind nur Links). */
  function bewerteModell(modell, kat, gew, regeln) {
    const db = regeln.datenblatt_abschlag;
    const werte = modell.werte || {};
    const tp = modell.teilpunkte || {};
    let summeG = 0, summeBel = 0, zaehler = 0;
    const beitraege = [], fehlend = [];
    for (const [fid, g] of Object.entries(gew)) {
      if (nichtAnwendbar(kat.id, fid, werte)) continue;
      summeG += g;
      const t = tp[fid];
      if (istZahl(t)) {
        summeBel += g; zaehler += g * t;
        beitraege.push({ feld: fid, gewicht: g, teilpunkte: t, beitrag: g * t });
      } else fehlend.push({ feld: fid, gewicht: g });
    }
    const R = summeBel > 0 ? zaehler / summeBel : null;
    const abdeckung = summeG > 0 ? summeBel / summeG : 0;
    let note = null, art = "zu_wenig_daten", spanne = null;
    const test = (modell.tests || []).find(t => t && istZahl(t.punkte) && t.punkte >= 0 && t.punkte <= 100);
    if (test && db.getestet) {
      const m = db.getestet.mischung;
      note = istZahl(R) ? m.test * test.punkte + m.datenblatt_roh * R : test.punkte;
      art = "getestet";
    } else {
      note = datenblattNote(R, abdeckung, db);
      if (note !== null) { art = "datenblatt"; spanne = db.spanne_plus_minus; }
      // P1-04: kein Merkmal zählt (alle wirksamen Gewichte 0) – keine Note, aber nicht wegen fehlender Datenblattwerte
      else if (summeG <= 0) art = "keine_merkmale";
    }
    beitraege.sort((a, b) => b.beitrag - a.beitrag);
    fehlend.sort((a, b) => b.gewicht - a.gewicht);
    return { R, abdeckung, note, art, spanne, beitraege, fehlend };
  }

  const preisVon = m => (m.preis && istZahl(m.preis.eur) && m.preis.eur > 0 ? m.preis.eur : null);

  /* Angezeigte Note (ganze Zahl) bzw. -Infinity ohne Note */
  const anzeige = e => (istZahl(e.note) ? Math.round(e.note) : -Infinity);
  /* Note absteigend nach angezeigter Zahl; Gleichstand → günstiger zuerst (07 B03/B15), dann ungerundete Note */
  function vergleichNote(a, b) {
    const na = anzeige(a), nb = anzeige(b);
    if (nb !== na) return nb - na;
    const pa = a.preis === null ? Infinity : a.preis, pb = b.preis === null ? Infinity : b.preis;
    if (pa !== pb) return pa - pb;
    const ra = istZahl(a.note) ? a.note : -Infinity, rb = istZahl(b.note) ? b.note : -Infinity;
    if (rb !== ra) return rb - ra;
    return String(a.modell.id).localeCompare(String(b.modell.id));
  }
  function vergleichPreis(a, b, ohneNote) {
    const pa = a.preis === null ? Infinity : a.preis, pb = b.preis === null ? Infinity : b.preis;
    if (pa !== pb) return pa - pb;
    if (!ohneNote) { const n = vergleichNote(a, b); if (n) return n; }
    return String(a.modell.id).localeCompare(String(b.modell.id));
  }
  /* P1-01: Punkte je Euro aus der angezeigten (gerundeten) Note, sonst setzen verborgene Nachkommastellen
     bei gleicher angezeigter Zahl das teurere Modell vor das günstigere */
  function effizienz(e) { return istZahl(e.note) && e.preis !== null && e.preis > 0 ? anzeige(e) / e.preis : null; }

  /* Rangfolge: "note" (Note absteigend, dann Preis), "preis" (aufsteigend, dann Note), "effizienz" (Punkte je Euro). */
  function sortiere(liste, art) {
    const l = liste.slice();
    if (art === "preis") l.sort((a, b) => vergleichPreis(a, b, false));
    else if (art === "effizienz") l.sort((a, b) => {
      const ea = effizienz(a), eb = effizienz(b);
      if (ea === null && eb === null) return vergleichNote(a, b);
      if (ea === null) return 1;
      if (eb === null) return -1;
      return eb - ea || vergleichNote(a, b);
    });
    else l.sort(vergleichNote);
    return l;
  }

  function fuelle(text, werte) {
    // R4-06: nur eigene Einträge der Ersetzungstabelle, nie geerbte (z. B. {constructor})
    return String(text).replace(/\{(\w+)\}/g, (m, k) => (eigen(werte, k) ? String(werte[k]) : m));
  }

  /* Aufpreis-Hinweis (aufpreis_regeln.aufpreis). A, kandidaten: Einträge aus auswerten() mit note, preis, art.
     Kandidaten müssen schon „alle Anforderungen erfüllt“ sein. Ohne Budget (egal) kein Hinweis. */
  function aufpreisHinweis(A, kandidaten, budget, regeln) {
    const r = regeln.aufpreis_regeln.aufpreis;
    if (!A || A.preis === null || !istZahl(A.note) || !istZahl(budget)) return null;
    const grenze = budget * r.budget_faktor_max;
    let best = null;
    for (const B of kandidaten) {
      if (B === A || B.modell.id === A.modell.id || B.preis === null || !istZahl(B.note)) continue;
      if (!(B.preis > A.preis + EPS) || !le(B.preis, grenze)) continue;
      const dp = B.preis - A.preis;
      if (!ge(dp, r.aufpreis_min_eur)) continue;
      const dN = B.note - A.note;
      const min = A.art === "datenblatt" || B.art === "datenblatt" ? r.punkte_min_datenblatt : r.punkte_min;
      if (!ge(dN, min)) continue;
      const E = dN / dp * 100;
      if (!ge(E, r.effizienz_min_je_100eur)) continue;
      if (!best || E > best.E + EPS || (Math.abs(E - best.E) <= EPS && dp < best.dp)) best = { B, dp, dN, E };
    }
    if (!best) return null;
    const aufpreis = Math.round(best.dp);
    const dNAnzeige = Math.round(best.B.note) - Math.round(A.note);
    return {
      modell: best.B, aufpreis, punkte: dNAnzeige, effizienz: best.E,
      // klasse_text leer: ältere Regeltexte tragen den Platzhalter noch, D12 kennt keine Klassen
      text: fuelle(r.text, { aufpreis: aufpreis.toLocaleString("de-DE"), dN: dNAnzeige, klasse_text: "" }),
    };
  }

  /* Spar-Hinweis (aufpreis_regeln.spar): größte Ersparnis, bei Gleichstand kleinerer Punktverlust.
     Gleiche angezeigte Zahl nie als „66 statt 66“ (07 B03): dann text_gleichauf, ohne diesen Text kein Hinweis. */
  function sparHinweis(A, kandidaten, regeln) {
    const r = regeln.aufpreis_regeln.spar;
    if (!A || A.preis === null || !istZahl(A.note)) return null;
    const minS = Math.max(r.ersparnis_min_eur, r.ersparnis_min_anteil * A.preis);
    let best = null;
    for (const C of kandidaten) {
      if (C === A || C.modell.id === A.modell.id || C.preis === null || !istZahl(C.note)) continue;
      if (!(C.preis < A.preis - EPS)) continue;
      const S = A.preis - C.preis;
      if (!ge(S, minS)) continue;
      const verlust = A.note - C.note;
      const gleich = le(verlust, r.verlust_max_gleich);
      const schwaecher = le(verlust, r.verlust_max_schwaecher) && ge(S, r.ersparnis_anteil_schwaecher * A.preis);
      if (!gleich && !schwaecher) continue;
      if (!best || S > best.S + EPS || (Math.abs(S - best.S) <= EPS && verlust < best.verlust)) {
        best = { C, S, verlust, art: gleich ? "gleich" : "schwaecher" };
      }
    }
    if (!best) return null;
    const ersparnis = Math.round(best.S);
    const w = { ersparnis: ersparnis.toLocaleString("de-DE"), N_C: Math.round(best.C.note), N_A: Math.round(A.note) };
    const gleichauf = w.N_C === w.N_A;
    if (gleichauf && !istText(r.text_gleichauf)) return null;
    return {
      modell: best.C, ersparnis, verlust: best.verlust, art: gleichauf ? "gleichauf" : best.art,
      text: fuelle(gleichauf ? r.text_gleichauf : best.art === "gleich" ? r.text_gleich : r.text_schwaecher, w),
    };
  }

  /* Gesamtauswertung einer Kategorie.
     eingabe = {antworten: {frageId: antwortId}, budget: Zahl|null (null = egal), filter: {…}, sortierung: "note"|"preis"|"effizienz",
       prioritaeten: {feldId: Faktor} (G1, optional)}
     Ergebnis: {gewichte, anforderungen, rang, empfehlung, status, aufpreis, spar, fassung, ausgeschlossen, ohneNote, anzahl}
     (fassung = {nummer, stand} der Gewichtsfassung der Kategorie oder null, P2a-1) */
  function auswerten(kat, regeln, eingabe) {
    const e = eingabe || {};
    const budget = istZahl(e.budget) && e.budget > 0 ? e.budget : null;
    const gew = gewichte(kat, e.antworten, e.prioritaeten);
    const anf = anforderungen(kat, e.antworten, e.filter);
    const alle = (kat.modelle || []).map(m => {
      const b = bewerteModell(m, kat, gew, regeln);
      const pruefungen = anf.map(a => Object.assign({}, a, { ergebnis: pruefe(m.werte, a) }));
      const preis = preisVon(m);
      return Object.assign({ modell: m, preis }, b, {
        verletzt: pruefungen.filter(p => p.ergebnis === "nein"),
        unbelegt: pruefungen.filter(p => p.ergebnis === "unbelegt"),
        imBudget: budget === null ? true : preis === null ? null : le(preis, budget),
      });
    });
    const passend = alle.filter(x => x.verletzt.length === 0);
    const nachNote = sortiere(passend, "note");
    const mitNote = nachNote.filter(x => x.note !== null);
    const voll = x => x.unbelegt.length === 0;
    // 08 G: empfohlen wird nur ein Modell mit Preis (ohne Budget ist imBudget auch ohne Preis true)
    const kaufbar = x => x.imBudget === true && x.preis !== null;
    let A = mitNote.find(x => kaufbar(x) && voll(x)) || null;
    let status = A ? "passt" : null;
    if (!A) { A = mitNote.find(kaufbar) || null; if (A) status = "unbelegt"; }
    if (!A) {
      // F-10: Passt ein Modell ins Budget, hat aber (zu wenig Daten) keine Note, wird es gezeigt statt „passt nichts“
      const ohneNote = nachNote.filter(x => x.note === null && kaufbar(x));
      A = ohneNote.find(voll) || ohneNote[0] || null;
      if (A) status = "ohne_note";
    }
    if (!A && budget !== null) {
      A = mitNote.find(x => voll(x) && x.preis !== null) || mitNote.find(x => x.preis !== null) || null;
      if (A) status = "ueber_budget";
    }
    let aufpreis = null, spar = null;
    if (A && (status === "passt" || status === "unbelegt")) {
      const kand = mitNote.filter(x => voll(x) && x.preis !== null && x !== A);
      aufpreis = aufpreisHinweis(A, kand, budget, regeln);
      spar = sparHinweis(A, kand, regeln);
    }
    return {
      gewichte: gew, anforderungen: anf, rang: sortiere(passend, e.sortierung || "note"),
      empfehlung: A, status: status || "leer", aufpreis, spar, budget, fassung: fassungPruefen(kat.gewichte_version),
      ausgeschlossen: alle.length - passend.length, ohneNote: passend.length - mitNote.length, anzahl: alle.length,
    };
  }

  /* Felder, in denen ein Modell vorn liegt (für den Vergleich): je Feld die höchsten Teilpunkte unter den Gewählten.
     Ergebnis {feldId: [modellIds]}; bei Gleichstand aller Gewählten kein Gewinner. */
  function feldSieger(eintraege, felder) {
    const aus = {};
    for (const f of felder) {
      if (!(f.gewicht > 0)) continue;
      const werte = eintraege.map(e => (e.modell.teilpunkte || {})[f.id]).filter(istZahl);
      if (werte.length < 2) continue;
      const max = Math.max.apply(null, werte), min = Math.min.apply(null, werte);
      if (max - min <= EPS) continue;
      aus[f.id] = eintraege.filter(e => istZahl((e.modell.teilpunkte || {})[f.id]) && Math.abs(e.modell.teilpunkte[f.id] - max) <= EPS).map(e => e.modell.id);
    }
    return aus;
  }

  /* Stärken: die höchsten Beiträge (Gewicht × Teilpunkte) mit guten Teilpunkten (mindestens 60). */
  function staerken(eintrag, n) {
    return (eintrag.beitraege || []).filter(b => b.teilpunkte >= 60).slice(0, n || 3);
  }

  /* P2a-1, §3: „Note bei anderer Antwort“. Für jede Frage mit mindestens zwei Antworten und jede Antwort außer der
     aktuellen wird genau diese eine Antwort geändert (nie zwei zugleich) und das Modell mit denselben Funktionen,
     denselben wirksamen Antworten und denselben Reglern (prio) wie die Hauptnote neu bewertet. Eine Zeile gibt es nur,
     wenn sich die angezeigte (gerundete) Zahl oder der Zustand (Note ↔ keine Note) ändert, nie „66 statt 66“.
     Zeile: {frage, frage_text, antwort, antwort_text, note, anzeige, art, abdeckung, delta, passt}; delta aus
     angezeigten Zahlen, null ohne Note auf einer Seite; passt = "ok"|"nein"|"unbelegt" nur für Frageanforderungen (keine
     Oberflächenfilter). Reihenfolge: Zeilen ohne Note zuerst, dann |delta| absteigend, bei Gleichstand Reihenfolge der
     Fragen und Antworten; höchstens max (3) Zeilen. Eingaben bleiben unverändert. */
  const angezeigteNote = n => (istZahl(n) ? Math.round(n) : null);
  function alternativen(kat, regeln, modell, antworten, prio, max) {
    const grenze = istZahl(max) && max >= 0 ? Math.floor(max) : 3;
    const aktuell = antworten || {};
    const basis = bewerteModell(modell, kat, gewichte(kat, aktuell, prio), regeln);
    const a0 = angezeigteNote(basis.note);
    const zeilen = [];
    let nr = 0;
    for (const frage of kat.fragen || []) {
      const liste = frage.antworten || [];
      if (liste.length < 2) continue;
      for (const a of liste) {
        const reihe = nr++;
        if (a.id === aktuell[frage.id]) continue;
        const neu = Object.assign({}, aktuell, { [frage.id]: a.id });
        const b = bewerteModell(modell, kat, gewichte(kat, neu, prio), regeln);
        const a1 = angezeigteNote(b.note);
        if (a1 === a0 && !(a1 === null && b.art !== basis.art)) continue;
        const pr = anforderungen(kat, neu, {}).map(x => pruefe(modell.werte, x));
        zeilen.push({ reihe, zeile: {
          frage: frage.id, frage_text: frage.text, antwort: a.id, antwort_text: a.text,
          note: b.note, anzeige: a1, art: b.art, abdeckung: b.abdeckung,
          delta: a0 === null || a1 === null ? null : a1 - a0,
          passt: pr.indexOf("nein") >= 0 ? "nein" : pr.indexOf("unbelegt") >= 0 ? "unbelegt" : "ok",
        } });
      }
    }
    const rang = z => (z.delta === null ? 0 : 1), betrag = z => (z.delta === null ? 0 : Math.abs(z.delta));
    zeilen.sort((x, y) => rang(x.zeile) - rang(y.zeile) || betrag(y.zeile) - betrag(x.zeile) || x.reihe - y.reihe);
    return zeilen.slice(0, grenze).map(x => x.zeile);
  }

  /* P2a-1, §4/§9.5: alles, was das Notenblatt (P2b) braucht, aus der bewerteten Zeile `eintrag` (Ergebnis von auswerten
     bzw. bewerteModell, keine zweite Rechnung). anteil = 100 · g / Σ g über alle anwendbaren Felder (belegt und fehlend),
     beitrag_r = g · Teilpunkte / Σ g über die belegten anwendbaren Felder (Summe = R, ein Anteil an R und keine
     „Punkte der Note“). merkmale enthält beide Zeilentypen (belegt: true|false; fehlend: wert, teilpunkte, beitrag_r,
     beleg = null), sortiert nach anteil absteigend, dann Schemareihenfolge; bei keine_merkmale leer.
     persoenlich: mindestens ein gültiger Regler ≠ 1 wirkt auf ein Feld, das die Antworten nicht schon abgeschaltet haben. */
  function belegFuer(kat, modell, feld) {
    const qid = eigen(modell.belege, feld) ? modell.belege[feld] : null;
    const q = typeof qid === "string" && eigen(kat.quellen, qid) ? kat.quellen[qid] : null;
    return q ? { titel: q.titel, url: q.url, gelesen: q.gelesen } : null;
  }
  function reglerWirken(kat, antworten, prio) {
    if (!istObjekt(prio)) return false;
    const g0 = gewichte(kat, antworten, undefined);
    return (kat.felder || []).some(f => istZahl(f.gewicht) && f.gewicht > 0 && eigen(prio, f.id) && istZahl(prio[f.id])
      && prio[f.id] >= 0 && prio[f.id] !== 1 && eigen(g0, f.id));
  }
  function notenblatt(kat, regeln, eintrag, antworten, prio) {
    const modell = eintrag.modell, werte = modell.werte || {};
    const beitraege = eintrag.beitraege || [], fehlend = eintrag.fehlend || [];
    const summe = [...beitraege, ...fehlend].reduce((s, x) => s + x.gewicht, 0);
    const summeBelegt = beitraege.reduce((s, x) => s + x.gewicht, 0);
    const felder = kat.felder || [];
    const zeile = (id, g, t) => {
      const f = felder.find(x => x.id === id), belegt = t !== null;
      return {
        feld: id, name: f ? f.name : id, einheit: f && f.einheit ? f.einheit : "", belegt,
        wert: belegt && eigen(werte, id) ? werte[id] : null, teilpunkte: t,
        anteil: 100 * g / summe,
        beitrag_r: belegt && summeBelegt > 0 ? g * t / summeBelegt : null,
        beleg: belegt ? belegFuer(kat, modell, id) : null,
      };
    };
    const merkmale = summe > 0
      ? [...beitraege.map(b => zeile(b.feld, b.gewicht, b.teilpunkte)), ...fehlend.map(f => zeile(f.feld, f.gewicht, null))] : [];
    const platz = id => felder.findIndex(f => f.id === id);
    merkmale.sort((a, b) => b.anteil - a.anteil || platz(a.feld) - platz(b.feld));
    const gew = gewichte(kat, antworten, prio);
    return {
      note: eintrag.note, anzeige: angezeigteNote(eintrag.note), art: eintrag.art, abdeckung: eintrag.abdeckung,
      spanne: eintrag.spanne, R: eintrag.R, persoenlich: reglerWirken(kat, antworten, prio),
      fassung: fassungPruefen(kat.gewichte_version),
      merkmale, fehlend: fehlend.map(f => f.feld),
      nicht_anwendbar: Object.keys(gew).filter(id => nichtAnwendbar(kat.id, id, werte)),
      alternativen: alternativen(kat, regeln, modell, antworten, prio),
      testquelle: testquellePruefen(kat.testquelle), tests: modell.tests || [],
    };
  }

  /* P2a-1, §4: Angaben für die Methodikseite (P2b): Abschlagswerte aus den Regeln, je Kategorie Gewichtsfassung,
     Testquelle und die Grundgewichte (ohne Antworten und ohne Regler, Summe 100, nur Felder mit Gewicht > 0). */
  function methodik(daten) {
    const db = daten.regeln.datenblatt_abschlag;
    return {
      abschlag: { anker: db.anker, faktor: db.faktor, abzug: db.abzug, abdeckung_mindest: db.abdeckung_mindest,
        spanne_plus_minus: db.spanne_plus_minus },
      kategorien: (daten.kategorien || []).map(k => {
        const g = gewichte(k, {});
        const grund = (k.felder || []).filter(f => eigen(g, f.id)).map((f, i) => ({ feld: f.id, name: f.name, anteil: g[f.id], i }))
          .sort((a, b) => b.anteil - a.anteil || a.i - b.i).map(({ feld, name, anteil }) => ({ feld, name, anteil }));
        return { id: k.id, name: k.name, fassung: fassungPruefen(k.gewichte_version), testquelle: testquellePruefen(k.testquelle),
          grundgewichte: grund };
      }),
    };
  }

  /* Budget-Schnellwahl aus vorhandenen Preisen: Quartile und Höchstpreis, auf runde Beträge aufgerundet. */
  function budgetStufen(modelle) {
    const p = (modelle || []).map(preisVon).filter(x => x !== null).sort((a, b) => a - b);
    if (!p.length) return [];
    const rund = x => {
      const s = x < 100 ? 10 : x < 300 ? 25 : x < 1000 ? 50 : x < 3000 ? 100 : 250;
      return Math.ceil(x / s - EPS) * s;
    };
    const q = f => p[Math.min(p.length - 1, Math.max(0, Math.ceil(f * p.length) - 1))];
    const stufen = [q(0.25), q(0.5), q(0.75), p[p.length - 1]].map(rund);
    return stufen.filter((x, i) => stufen.indexOf(x) === i);
  }

  /* Nur https-Adressen zulassen (fremde Daten); sonst null. */
  function sichereUrl(u) {
    if (typeof u !== "string" || u.length > 2000) return null;
    try { const x = new URL(u); return x.protocol === "https:" ? x.href : null; } catch (err) { return null; }
  }

  function preisOk(p) {
    return istObjekt(p) && istZahl(p.eur) && p.eur >= 1 && p.eur <= 100000 && typeof p.haendler === "string"
      && p.haendler.trim() !== "" && p.haendler.length <= 80 && sichereUrl(p.url) !== null
      && typeof p.stand === "string" && DATUM.test(p.stand);
  }

  /* Aktuelle Preise überlagern (finder-preise.json: {stand, preise: {variantenId: {eur, haendler, url, stand}}}).
     Ersetzt den Preis nur, wenn der Eintrag gültig und neuer ist (stand später) oder bisher kein Preis da war.
     Ändert daten an Ort und Stelle; Rückgabe: Zahl ersetzter Preise. */
  function preiseUeberlagern(daten, datei) {
    if (!istObjekt(daten) || !istObjekt(datei) || !istObjekt(datei.preise)) return 0;
    let n = 0;
    for (const kat of daten.kategorien || []) {
      for (const m of kat.modelle || []) {
        if (!Object.prototype.hasOwnProperty.call(datei.preise, m.id)) continue;
        const neu = datei.preise[m.id];
        if (!preisOk(neu)) continue;
        const alt = m.preis;
        if (alt && preisOk(alt) && !(neu.stand > alt.stand)) continue;
        m.preis = { eur: neu.eur, haendler: neu.haendler.trim(), url: neu.url, stand: neu.stand };
        n++;
      }
    }
    return n;
  }

  /* Strukturprüfung der App-Daten (fremde Datei, F-08/F-09). Wirft bei allem, was Navigation, Bewertung oder Anzeige
     braucht (Regeln, Kategorien, Felder, Fragen); der Service Worker nutzt dieselbe Prüfung, bevor er die Cachekopie
     ersetzt, damit eine beschädigte Datei den letzten brauchbaren Stand nicht verdrängt. Einzelne kaputte Modelle,
     Preise und Teilpunkte werden still entfernt. Testlinks nur mit url und titel (F-01: keine übernommenen Noten). */
  const KENNUNG = /^[a-z0-9_]+(?:-[a-z0-9_]+)*$/;
  // R3-02: Namen aus dem Objekt-Prototyp (constructor, __proto__ …) und prototype sind als Kennung oder Schlüssel verboten
  const reserviert = x => x === "prototype" || x === "__proto__" || x in Object.prototype;
  const kennungOk = x => typeof x === "string" && KENNUNG.test(x) && !reserviert(x);
  const schluesselOk = o => Object.keys(o).every(k => !reserviert(k));
  const zahlIn = (x, lo, hi) => istZahl(x) && x >= lo && x <= hi;
  const istText = (x, max) => typeof x === "string" && x.length <= (max || 500);
  const istName = (x, max) => istText(x, max) && x.trim() !== "";
  function pruefOderWirf(ok, was) { if (!ok) throw new Error(was); }

  /* P2a-1, gemeinsamer Vertrag mit werkzeuge/datenbank.py (p2-entwurf.md §9.6). Die neuen Angaben (Gewichtsfassung,
     Testquelle, Quellen, Belege) dienen nur der Anzeige und werden still verworfen statt zu werfen (§2.6).
     Abweichung laut Entwurf: Datum ohne obere Grenze (der Client kennt kein verlässliches „heute“), Namen in Codepunkten. */
  const codepunkte = x => Array.from(x).length;
  const quellName = (x, max) => typeof x === "string" && codepunkte(x) >= 1 && codepunkte(x) <= max && x.trim() !== "";
  function quellDatum(x) {
    if (typeof x !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(x)) return false;
    const [j, m, t] = x.split("-").map(Number);
    if (j < 2020) return false;
    const d = new Date(Date.UTC(j, m - 1, t));
    return d.getUTCFullYear() === j && d.getUTCMonth() === m - 1 && d.getUTCDate() === t;
  }
  // Hostteil: DNS-Name in Kleinbuchstaben mit Punkt, Endung beginnt mit Buchstaben (keine IP), kein Port, kein Userinfo, kein xn--
  const DNS_NAME = /^([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z]([a-z0-9-]*[a-z0-9])?$/;
  function sichereQuelle(u) {
    if (typeof u !== "string" || u.length < 1 || u.length > 2000 || !/^[\x21-\x7e]+$/.test(u) || u.indexOf("https://") !== 0) return null;
    const rest = u.slice(8), ende = rest.search(/[/?#]/);
    const host = ende < 0 ? rest : rest.slice(0, ende);
    if (!DNS_NAME.test(host) || host.split(".").some(l => l.indexOf("xn--") === 0)) return null;
    try { const x = new URL(u); return x.protocol === "https:" ? x.href : null; } catch (err) { return null; }
  }
  function fassungPruefen(f) {
    return istObjekt(f) && Number.isInteger(f.nummer) && f.nummer >= 1 && f.nummer <= 9999 && quellDatum(f.stand)
      ? { nummer: f.nummer, stand: f.stand } : null;
  }
  function testquellePruefen(t) {
    if (!istObjekt(t)) return null;
    const url = sichereQuelle(t.url), methodikUrl = sichereQuelle(t.methodik_url);
    return quellName(t.name, 80) && url && methodikUrl && quellDatum(t.stand)
      ? { name: t.name, url, methodik_url: methodikUrl, stand: t.stand } : null;
  }
  function quellenPruefen(q) {
    const aus = {};
    if (!istObjekt(q)) return aus;
    for (const [id, x] of Object.entries(q)) {
      if (!kennungOk(id) || !istObjekt(x)) continue;
      const url = sichereQuelle(x.url);
      if (quellName(x.titel, 200) && url && quellDatum(x.gelesen)) aus[id] = { titel: x.titel, url, gelesen: x.gelesen };
    }
    return aus;
  }
  // Maßfelder haben feste Namen (Entwurf §2.3, §9.7); Wert nur 0 < x ≤ 500
  const MASSFELDER = ["breite_cm", "hoehe_cm", "tiefe_cm"];
  function regelnPruefen(r) {
    pruefOderWirf(istObjekt(r), "regeln");
    // D12: klassen und kappung werden nicht mehr gelesen (ältere Dateien dürfen sie noch tragen)
    const db = r.datenblatt_abschlag;
    pruefOderWirf(istObjekt(db) && ["anker", "abzug", "spanne_plus_minus"].every(n => zahlIn(db[n], 0, 100))
      && zahlIn(db.faktor, 0, 2) && zahlIn(db.abdeckung_mindest, 0, 1), "datenblatt_abschlag");
    if (db.getestet !== undefined) {
      const m = istObjekt(db.getestet) ? db.getestet.mischung : null;
      pruefOderWirf(istObjekt(m) && zahlIn(m.test, 0, 1) && zahlIn(m.datenblatt_roh, 0, 1), "getestet");
    }
    const a = r.aufpreis_regeln;
    pruefOderWirf(istObjekt(a) && istObjekt(a.aufpreis) && istObjekt(a.spar), "aufpreis_regeln");
    pruefOderWirf(["budget_faktor_max", "aufpreis_min_eur", "punkte_min", "punkte_min_datenblatt", "effizienz_min_je_100eur"]
      .every(n => zahlIn(a.aufpreis[n], 0, 100000)) && istText(a.aufpreis.text), "aufpreis");
    pruefOderWirf(["ersparnis_min_eur", "ersparnis_min_anteil", "verlust_max_gleich", "verlust_max_schwaecher",
      "ersparnis_anteil_schwaecher"].every(n => zahlIn(a.spar[n], 0, 100000)) && istText(a.spar.text_gleich) && istText(a.spar.text_schwaecher)
      && (a.spar.text_gleichauf === undefined || istText(a.spar.text_gleichauf)), "spar");
  }
  function feldPruefen(f) {
    pruefOderWirf(istObjekt(f) && kennungOk(f.id) && istName(f.name, 80)
      && ["zahl", "bool", "stufe"].indexOf(f.typ) >= 0 && zahlIn(f.gewicht, 0, 1000)
      && (f.einheit === undefined || f.einheit === null || istText(f.einheit, 20)), "feld");
    if (f.einheit === undefined || f.einheit === null) f.einheit = "";
  }
  function fragePruefen(f) {
    pruefOderWirf(istObjekt(f) && kennungOk(f.id) && istText(f.text)
      && Array.isArray(f.antworten) && f.antworten.length > 0, "frage");
    for (const a of f.antworten) {
      pruefOderWirf(istObjekt(a) && kennungOk(a.id) && istText(a.text), "antwort");
      for (const n of ["gewichte", "mindest", "hoechst"]) pruefOderWirf(a[n] === undefined || (istObjekt(a[n]) && schluesselOk(a[n])), "antwort." + n);
      if (a.gewichte) pruefOderWirf(Object.values(a.gewichte).every(g => zahlIn(g, 0, 100)), "antwort.gewichte");
    }
  }
  /* Modellwert, wie die Anzeige ihn braucht (R2-03): endliche Zahl, Wahrheitswert oder kurzer Text */
  const wertOk = w => istZahl(w) || typeof w === "boolean" || istText(w, 200);
  /* Wert nach dem veröffentlichten Typ des Schemafelds (P2a-1, §2.6/§9.7, wie feld_ok im Bau): zahl = endliche Zahl mit
     |x| < 1e7, bool = Wahrheitswert, stufe = Text mit 1..200 Codepunkten; Maßfelder zusätzlich 0 < x ≤ 500. Ohne
     Schemafeld gilt wie bisher nur wertOk. */
  function wertNachTyp(feld, w) {
    if (!feld) return wertOk(w);
    if (feld.typ === "zahl") return istZahl(w) && Math.abs(w) < 1e7 && (MASSFELDER.indexOf(feld.id) < 0 || (w > 0 && w <= 500));
    if (feld.typ === "bool") return typeof w === "boolean";
    return typeof w === "string" && codepunkte(w) >= 1 && codepunkte(w) <= 200;
  }
  function datenPruefen(d) {
    pruefOderWirf(istObjekt(d) && Array.isArray(d.kategorien) && istObjekt(d.regeln), "format");
    // Kopfangaben (R2-03): stand nur null/Datum, herkunft nur Commit (40 Hex-Zeichen); sonst ganze Datei ungültig
    pruefOderWirf(d.stand === undefined || d.stand === null || (typeof d.stand === "string" && DATUM.test(d.stand)), "stand");
    pruefOderWirf(d.herkunft === undefined || (typeof d.herkunft === "string" && /^[0-9a-f]{40}$/.test(d.herkunft)), "herkunft");
    regelnPruefen(d.regeln);
    for (const k of d.kategorien) {
      pruefOderWirf(istObjekt(k) && kennungOk(k.id) && istName(k.name, 80)
        && Array.isArray(k.felder) && Array.isArray(k.modelle), "kategorie");
      k.felder.forEach(feldPruefen);
      k.fragen = k.fragen === undefined ? [] : k.fragen;
      pruefOderWirf(Array.isArray(k.fragen), "fragen");
      k.fragen.forEach(fragePruefen);
      k.gewichte_version = fassungPruefen(k.gewichte_version);   // P2a-1: neue Angaben optional, kaputt → still verworfen
      k.testquelle = testquellePruefen(k.testquelle);
      k.quellen = quellenPruefen(k.quellen);
      const feldVon = Object.create(null);
      for (const f of k.felder) if (!(f.id in feldVon)) feldVon[f.id] = f;
      k.modelle = k.modelle.filter(m => istObjekt(m) && typeof m.id === "string" && m.id !== "" && istName(m.hersteller, 80)
        && istName(m.name, 200) && (m.variante === undefined || m.variante === null || istText(m.variante, 200))
        && (m.werte === undefined || istObjekt(m.werte)) && (m.teilpunkte === undefined || istObjekt(m.teilpunkte)));
      for (const m of k.modelle) {
        // Wert, Teilpunkte und Beleg gehören zusammen (P2a-1, R2-06): Teilpunkt und Beleg nur für ein Feld, dessen Wert bleibt
        m.werte = Object.fromEntries(Object.entries(m.werte || {}).filter(([f, w]) => !reserviert(f) && wertNachTyp(feldVon[f], w)));
        m.teilpunkte = Object.fromEntries(Object.entries(m.teilpunkte || {})
          .filter(([f, t]) => !reserviert(f) && zahlIn(t, 0, 100) && eigen(m.werte, f)));
        m.belege = Object.fromEntries(Object.entries(istObjekt(m.belege) ? m.belege : {})
          .filter(([f, q]) => !reserviert(f) && eigen(m.werte, f) && typeof q === "string" && eigen(k.quellen, q)));
        if (m.preis !== null && m.preis !== undefined && !preisOk(m.preis)) m.preis = null;
        m.tests = (Array.isArray(m.tests) ? m.tests : []).filter(t => istObjekt(t) && sichereUrl(t.url) && istName(t.titel, 200))
          .map(t => ({ url: sichereUrl(t.url), titel: t.titel }));
      }
    }
    return d;
  }

  return {
    gewichte, anforderungen, pruefe, datenblattNote, bewerteModell, sortiere, auswerten,
    aufpreisHinweis, sparHinweis, feldSieger, staerken, budgetStufen, sichereUrl, preiseUeberlagern, datenPruefen,
    nichtAnwendbar, PRIO_FAKTOREN, NICHT_ANWENDBAR,
    alternativen, notenblatt, methodik, quellDatum, sichereQuelle, quellName,
  };
});
