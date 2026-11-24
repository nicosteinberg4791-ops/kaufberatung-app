/* Startseite „Finden & Vergleichen“: Kategorie → Budget → Fragen → Ergebnis.
   Rechnung in bewertung.js (window.KBBewertung), hier nur Oberfläche und Zustand in der Adresse (#k=…&b=…).
   Sicherheit: Daten aus finder-daten.json / finder-preise.json sind fremde Daten. Ausgabe nur per textContent und
   setAttribute, nie innerHTML; Links nur https mit rel="noopener noreferrer" und target="_blank". */
(function () {
  "use strict";
  const B = window.KBBewertung;
  const SVGNS = "http://www.w3.org/2000/svg";
  const SCHRITTE = ["budget", "fragen", "ergebnis"];
  const SORTEN = [["note", "Beste Note"], ["preis", "Günstigste"], ["effizienz", "Punkte je Euro"]];
  const ID = /^[a-z0-9_-]{1,80}$/;

  /* Kategorien in Gruppen, mit eigenen Strichsymbolen (24er-Raster, nur Pfade, currentColor) */
  const GRUPPEN = [
    ["Wohnzimmer", ["fernseher", "soundbar"]],
    ["Küche", ["airfryer", "kuehlschrank", "geschirrspueler"]],
    ["Haushalt", ["akkusauger", "saugroboter", "waschmaschine", "trockner"]],
    ["Unterwegs", ["smartphone", "tablet", "laptop", "kopfhoerer_inear", "kopfhoerer_overear"]],
  ];
  const KASTEN = "M6 2.5h12a1.5 1.5 0 0 1 1.5 1.5v16a1.5 1.5 0 0 1-1.5 1.5H6A1.5 1.5 0 0 1 4.5 20V4A1.5 1.5 0 0 1 6 2.5z";
  const SYMBOLE = {
    fernseher: ["M3.5 4.5h17a1.5 1.5 0 0 1 1.5 1.5v9.5a1.5 1.5 0 0 1-1.5 1.5h-17A1.5 1.5 0 0 1 2 15.5V6a1.5 1.5 0 0 1 1.5-1.5z", "M8 20.5h8", "M12 17v3.5"],
    soundbar: ["M3.5 9h17a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1-1.5 1.5h-17A1.5 1.5 0 0 1 2 13.5v-3A1.5 1.5 0 0 1 3.5 9z", "M7 12h.01", "M12 12h.01", "M17 12h.01", "M6 18.5h12"],
    airfryer: ["M7 3.5h10a2.5 2.5 0 0 1 2.5 2.5v12a2.5 2.5 0 0 1-2.5 2.5H7A2.5 2.5 0 0 1 4.5 18V6A2.5 2.5 0 0 1 7 3.5z", "M4.5 10h15", "M9.5 14.5h5", "M8.5 6.8h.01"],
    kuehlschrank: [KASTEN, "M4.5 9h15", "M8 5v2", "M8 11.5v3.5"],
    geschirrspueler: [KASTEN, "M4.5 7h15", "M7.5 4.8h3", "M7.5 12.5h9", "M7.5 16.5h9", "M9.5 12.5v4", "M14.5 12.5v4"],
    akkusauger: ["M15.5 2.5l-4.2 14.5", "M6 17h7.5a2 2 0 0 1 2 2v1.5H6a1 1 0 0 1-1-1V18a1 1 0 0 1 1-1z", "M13.6 6.6l2.9 1v3.2l-3.8-.3"],
    saugroboter: ["M12 3a9 9 0 1 1 0 18a9 9 0 1 1 0-18z", "M8 8.5h8", "M12 12.5a2.2 2.2 0 1 1 0 4.4a2.2 2.2 0 1 1 0-4.4z"],
    waschmaschine: [KASTEN, "M4.5 7h15", "M7.5 4.8h2", "M12 10a4.5 4.5 0 1 1 0 9a4.5 4.5 0 1 1 0-9z", "M10 15.2c.8-.8 1.6.8 2.4 0s1.6-.8 1.6-.8"],
    trockner: [KASTEN, "M4.5 7h15", "M7.5 4.8h2", "M12 10a4.5 4.5 0 1 1 0 9a4.5 4.5 0 1 1 0-9z", "M10.4 13.2c-.6.9.6 1.6 0 2.6", "M13.6 13.2c-.6.9.6 1.6 0 2.6"],
    smartphone: ["M8 2.5h8A1.5 1.5 0 0 1 17.5 4v16a1.5 1.5 0 0 1-1.5 1.5H8A1.5 1.5 0 0 1 6.5 20V4A1.5 1.5 0 0 1 8 2.5z", "M11 18.5h2"],
    tablet: ["M5 3h14a1.5 1.5 0 0 1 1.5 1.5v15A1.5 1.5 0 0 1 19 21H5a1.5 1.5 0 0 1-1.5-1.5v-15A1.5 1.5 0 0 1 5 3z", "M11 18h2"],
    laptop: ["M5 5h14a1 1 0 0 1 1 1v9.5H4V6a1 1 0 0 1 1-1z", "M2 18.5h20", "M4 15.5l-2 3", "M20 15.5l2 3"],
    kopfhoerer_inear: ["M8.5 5.5a3.2 3.2 0 1 0 0 6.4", "M8.5 11.9V19", "M15.5 5.5a3.2 3.2 0 1 1 0 6.4", "M15.5 11.9V19"],
    kopfhoerer_overear: ["M4 15v-3a8 8 0 0 1 16 0v3", "M4 14h3v6.5H5a1 1 0 0 1-1-1z", "M20 14h-3v6.5h2a1 1 0 0 0 1-1z"],
  };
  const PFEIL_ZURUECK = ["M14.5 6l-6 6l6 6"];

  /* Fernseher: Größe als Filter auf diagonale_zoll */
  const GROESSEN = [
    { id: "bis43", text: "bis 43 Zoll", f: { hoechst: 43 } },
    { id: "50-55", text: "50 bis 55 Zoll", f: { mindest: 48, hoechst: 55 } },
    { id: "65", text: "um 65 Zoll", f: { mindest: 58, hoechst: 68 } },
    { id: "ab75", text: "75 Zoll und mehr", f: { mindest: 70 } },
  ];

  /* Lesbare Namen für Stufenwerte; Unbekanntes: Unterstriche zu Leerzeichen */
  const STUFEN = {
    oled: "OLED", miniled: "Mini-LED", lcd_local_dimming: "LCD mit Local Dimming", lcd_quantum_dot: "LCD mit Quantum Dot (QLED)", lcd: "LCD",
    nur_hdr10: "nur HDR10", dolby_vision: "Dolby Vision", hdr10plus: "HDR10+", beide: "Dolby Vision und HDR10+",
    hd: "HD", fullhd: "Full HD", "4k": "4K", "8k": "8K",
    hepa_h13_oder_besser: "HEPA H13 oder besser", hepa_ohne_klasse: "HEPA ohne Klasse", kein_hepa: "kein HEPA",
    lidar: "Laser (LiDAR)", kamera_vslam: "Kamera", gyroskop: "Gyroskop", zufall: "Zufallsfahrt",
    kamera_ki: "Kamera mit KI", strukturiertes_licht: "strukturiertes Licht", nur_stossfaenger: "nur Stoßfänger",
    rotierend_oder_walze: "rotierende Mopps oder Walze", vibrierend: "vibrierende Platte", statisches_tuch: "festes Tuch", keines: "keines",
    edelstahl: "Edelstahl", keramik: "Keramik", ptfe: "PTFE-Beschichtung",
    android: "Android", ios: "iOS", windows: "Windows", macos: "macOS", chromeos: "ChromeOS", linux: "Linux", ohne: "ohne",
    ips: "IPS", va: "VA", tn: "TN", wifi5: "Wi-Fi 5", wifi6: "Wi-Fi 6", wifi6e: "Wi-Fi 6E", wifi7: "Wi-Fi 7",
    sbc: "SBC", aac: "AAC", aptx: "aptX", aptx_adaptive: "aptX Adaptive", ldac: "LDAC", lc3: "LC3",
    integriert: "eingebaut", extern_kabel: "extern mit Kabel", extern_kabellos: "extern ohne Kabel", keiner: "keiner",
    vollschutz: "Vollschutz", teilschutz: "Teilschutz",
    frontlader: "Frontlader", toplader: "Toplader", einbau: "Einbau", stand: "frei stehend", unterbau: "Unterbau",
    side_by_side: "Side-by-Side", vollintegriert: "vollintegriert", teilintegriert: "teilintegriert", freistehend: "frei stehend", tisch: "Tischgerät",
  };

  let daten = null;
  let zustand = leererZustand();
  let letzterSchirm = "";
  let teurereZeigen = false;
  let budgetTeile = [];      // Eingabefeld und Schnellwahl des aktuellen Schirms
  let reglerTeile = [];      // G1: Prioritäten-Regler des aktuellen Ergebnisschirms ({fid, eingabe, ausgabe})
  let reglerZurueck = null;  // G1: Knopf „Zurück auf deine Antworten“
  let ergebnisTeile = null;  // G1: {unten, prio} des aktuellen Ergebnisschirms (vor dem Einhängen nicht per id auffindbar)
  let glasBeobachter = null; // G1: Lichtstreif der Glas-Hinweise nur, solange sichtbar
  const wurzel = document.getElementById("inhalt");
  const fuss = document.getElementById("datenstand");
  // G1-05: bei jeder Bewegung neu fragen, damit eine geänderte Einstellung ohne Neuladen gilt
  const reduziert = () => { try { return window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) { return false; } };

  /* G1: fünf Stufen je Merkmal; Faktoren in bewertung.js (PRIO_FAKTOREN), „normal“ (2) steht nie in der Adresse */
  const PRIO_NAMEN = ["aus", "weniger", "normal", "mehr", "viel mehr"];
  const PRIO_NORMAL = 2;
  const PRIO_OFFEN = 5;      // so viele Regler stehen offen, der Rest ist eingeklappt

  function leererZustand() { return { k: null, s: "budget", b: null, g: null, ba: null, a: {}, o: "note", v: [], p: {} }; }

  /* ---------- DOM-Helfer (nur textContent / setAttribute) ---------- */
  function h(tag, props, kinder) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(props || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") e.className = v;
      else if (k === "text") e.textContent = String(v);
      else if (k === "on") for (const [ev, fn] of Object.entries(v)) e.addEventListener(ev, fn);
      else if (k === "hidden") e.hidden = true;
      else e.setAttribute(k, v === true ? "" : String(v));
    }
    anhaengen(e, kinder);
    return e;
  }
  function anhaengen(e, kinder) {
    for (const k of [].concat(kinder || [])) {
      if (k === null || k === undefined || k === false) continue;
      e.appendChild(typeof k === "string" ? document.createTextNode(k) : k);
    }
    return e;
  }
  function symbol(pfade, klasse) {
    const s = document.createElementNS(SVGNS, "svg");
    s.setAttribute("viewBox", "0 0 24 24");
    s.setAttribute("aria-hidden", "true");
    s.setAttribute("focusable", "false");
    s.setAttribute("class", klasse || "sym");
    for (const d of pfade) {
      const p = document.createElementNS(SVGNS, "path");
      p.setAttribute("d", d);
      s.appendChild(p);
    }
    return s;
  }
  function leeren(e) { while (e.firstChild) e.removeChild(e.firstChild); }
  function link(url, text, klasse) {
    const u = B.sichereUrl(url);
    if (!u) return null;
    return h("a", { href: u, target: "_blank", rel: "noopener noreferrer", class: klasse || null }, [text]);
  }
  function findeFokus(knoten, schluessel) {
    if (!knoten || !schluessel) return null;
    if (knoten.getAttribute && knoten.getAttribute("data-fokus") === schluessel) return knoten;
    for (const k of Array.from(knoten.childNodes || [])) { const f = findeFokus(k, schluessel); if (f) return f; }
    return null;
  }

  /* ---------- Formate ---------- */
  function eur(v) {
    return v.toLocaleString("de-DE", { minimumFractionDigits: Number.isInteger(v) ? 0 : 2, maximumFractionDigits: 2 }) + " €";
  }
  function datum(iso) {
    const m = typeof iso === "string" ? /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso) : null;
    return m ? `${m[3]}.${m[2]}.${m[1]}` : "";
  }
  function stufeText(w) { return Object.prototype.hasOwnProperty.call(STUFEN, w) ? STUFEN[w] : String(w).replace(/_/g, " "); }
  function wertText(feld, w) {
    if (w === undefined || w === null) return "nicht angegeben";
    if (feld.typ === "bool" || typeof w === "boolean") return w ? "ja" : "nein";
    if (feld.typ === "zahl" && typeof w === "number") {
      const z = w.toLocaleString("de-DE", { maximumFractionDigits: 2 });
      if (feld.einheit === "fach") return z + "-fach";
      return feld.einheit ? z + " " + feld.einheit : z;
    }
    return stufeText(w);
  }
  /* Variante nur zeigen, wenn sie etwas sagt (07 B08): nicht „Standard“ und nicht schon im Modellnamen enthalten */
  const flach = t => String(t || "").toLowerCase().replace(/[^a-z0-9äöüß]/g, "");
  function varianteText(m) {
    const v = typeof m.variante === "string" ? m.variante.trim() : "";
    if (!v || /^standard$/i.test(v)) return "";
    const fv = flach(v);
    return fv && flach(m.name).indexOf(fv) >= 0 ? "" : v;
  }
  function modellName(m) { return [m.name, varianteText(m)].filter(Boolean).join(", "); }
  function note(n) { return n === null ? "–" : String(Math.round(n)); }

  /* ---------- Zustand <-> Adresse ---------- */
  function katVon(id) { return daten && daten.kategorien.find(k => k.id === id) || null; }
  function ausAdresse() {
    const z = leererZustand();
    let p;
    try { p = new URLSearchParams(String(location.hash || "").replace(/^#/, "")); } catch (e) { return z; }
    const kat = katVon(p.get("k"));
    if (!kat) return z;
    z.k = kat.id;
    const s = p.get("s");
    if (SCHRITTE.indexOf(s) >= 0) z.s = s;
    const b = Number(p.get("b"));
    if (isFinite(b) && b >= 1 && b <= 100000) z.b = Math.round(b);
    if (GROESSEN.some(g => g.id === p.get("g"))) z.g = p.get("g");
    const ba = p.get("ba");
    if (ba && ID.test(ba)) z.ba = ba;
    for (const teil of String(p.get("a") || "").split("~")) {
      const [fid, aid] = teil.split(".");
      const frage = kat.fragen.find(f => f.id === fid);
      if (frage && frage.antworten.some(x => x.id === aid)) z.a[fid] = aid;
    }
    const o = p.get("o");
    if (SORTEN.some(x => x[0] === o)) z.o = o;
    const ids = new Set(kat.modelle.map(m => m.id));
    z.v = String(p.get("v") || "").split("~").filter(x => ids.has(x)).filter((x, i, l) => l.indexOf(x) === i).slice(0, 3);
    // G1: p=feld.stufe~… nur bewertete Felder der Kategorie (Gewicht > 0) und Stufe 0–4 außer „normal“
    const bewertbar = new Set(kat.felder.filter(f => f.gewicht > 0).map(f => f.id));
    z.p = {};
    for (const teil of String(p.get("p") || "").split("~")) {
      const m = /^([a-z0-9_-]{1,80})\.([0-4])$/.exec(teil);
      if (m && ID.test(m[1]) && bewertbar.has(m[1]) && Number(m[2]) !== PRIO_NORMAL && !(m[1] in z.p)) z.p[m[1]] = Number(m[2]);
    }
    return z;
  }
  function alsAdresse(z) {
    if (!z.k) return "";
    const teile = ["k=" + z.k, "s=" + z.s];
    if (z.b) teile.push("b=" + z.b);
    if (z.g) teile.push("g=" + z.g);
    if (z.ba) teile.push("ba=" + encodeURIComponent(z.ba));
    const a = Object.entries(z.a).map(([f, x]) => f + "." + x).join("~");
    if (a) teile.push("a=" + encodeURIComponent(a).replace(/%7E/gi, "~"));
    if (z.o !== "note") teile.push("o=" + z.o);
    if (z.v.length) teile.push("v=" + z.v.join("~"));
    const p = Object.entries(z.p || {}).filter(([, s]) => s !== PRIO_NORMAL).map(([f, s]) => f + "." + s).join("~");
    if (p) teile.push("p=" + p);
    return "#" + teile.join("&");
  }
  /* G1: Stufen aus der Adresse als Faktoren für bewertung.js */
  function prioFaktoren() {
    const aus = {};
    for (const [fid, s] of Object.entries(zustand.p || {})) aus[fid] = B.PRIO_FAKTOREN[s];
    return aus;
  }
  function setze(aenderung, neuerEintrag) {
    zustand = Object.assign({}, zustand, aenderung);
    const ziel = alsAdresse(zustand) || location.pathname + location.search;
    try {
      if (neuerEintrag) history.pushState(null, "", ziel);
      else history.replaceState(null, "", ziel);
    } catch (e) { /* ohne Verlauf (z. B. file:) bleibt die Seite bedienbar */ }
    zeichne();
  }

  /* Wirksame Antworten: Fragen mit eigener Antwort „egal“ starten dort; sonst fehlt die Antwort (= egal) */
  function antwortenWirksam(kat) {
    const a = {};
    for (const f of kat.fragen) {
      if (zustand.a[f.id]) a[f.id] = zustand.a[f.id];
      else if (f.antworten.some(x => x.id === "egal")) a[f.id] = "egal";
    }
    return a;
  }
  function bauartWerte(kat) {
    if (!kat.felder.some(f => f.id === "bauart")) return [];
    const perFrage = kat.fragen.some(f => f.antworten.some(x => x.mindest && "bauart" in x.mindest));
    if (perFrage) return [];
    const w = kat.modelle.map(m => m.werte.bauart).filter(x => typeof x === "string" && ID.test(x));
    return w.filter((x, i) => w.indexOf(x) === i).sort();
  }
  function filterWirksam(kat) {
    const f = {};
    if (kat.id === "fernseher" && zustand.g) {
      const g = GROESSEN.find(x => x.id === zustand.g);
      if (g) f.diagonale_zoll = g.f;
    }
    if (zustand.ba && bauartWerte(kat).indexOf(zustand.ba) >= 0) f.bauart = { liste: [zustand.ba] };
    return f;
  }

  /* ---------- Bausteine ---------- */
  function kopf(kat, schritt) {
    const nr = SCHRITTE.indexOf(schritt) + 1;
    const zurueck = schritt === "budget" ? { k: null, s: "budget" } : { s: SCHRITTE[nr - 2] };
    return h("div", { class: "kopf" }, [
      h("button", { type: "button", class: "zurueck", on: { click: () => setze(zurueck, true) } },
        [symbol(PFEIL_ZURUECK, "sym klein"), schritt === "budget" ? "Kategorien" : "Zurück"]),
      h("p", { class: "schritt" }, [h("span", { text: kat.name }), " – Schritt " + nr + " von 3"]),
    ]);
  }
  function chip(text, gewaehlt, onClick, extra) {
    return h("button", Object.assign({ type: "button", class: "chip", "aria-pressed": gewaehlt ? "true" : "false", on: { click: onClick } }, extra || {}), [text]);
  }
  function titel(text) { return h("h1", { tabindex: "-1", class: "titel" }, [text]); }

  /* ---------- Schirm 1: Kategorie ---------- */
  function schirmKategorien() {
    const teile = [
      titel("Was suchst du?"),
      h("p", { class: "lead" }, ["Kategorie antippen, Budget nennen, ein paar Fragen beantworten. Dann siehst du, welches Modell für dich am besten passt."]),
    ];
    const bekannt = new Set();
    for (const [gruppe, ids] of GRUPPEN) {
      const kats = ids.map(katVon).filter(Boolean);
      if (!kats.length) continue;
      kats.forEach(k => bekannt.add(k.id));
      teile.push(kachelGruppe(gruppe, kats));
    }
    const rest = daten.kategorien.filter(k => !bekannt.has(k.id));
    if (rest.length) teile.push(kachelGruppe("Weitere", rest));
    return h("section", { class: "schirm" }, teile);
  }
  function kachelGruppe(name, kats) {
    const gid = "gruppe-" + name.toLowerCase().replace(/[^a-z]/g, "");
    return h("section", { class: "gruppe", "aria-labelledby": gid }, [
      h("h2", { id: gid, class: "gruppe-name" }, [name]),
      h("ul", { class: "kacheln" }, kats.map(k => {
        const n = k.modelle.length;
        return h("li", null, [h("button", { type: "button", class: "kachel" + (n ? "" : " leer"),
          on: { click: () => { teurereZeigen = false; setze(Object.assign(leererZustand(), { k: k.id }), true); } } }, [
          symbol(SYMBOLE[k.id] || SYMBOLE.tablet, "sym kachel-sym"),
          h("span", { class: "kachel-name", text: k.name }),
          h("span", { class: "kachel-zahl", text: n ? n + (n === 1 ? " Modell" : " Modelle") : "bald" }),
        ])]);
      })),
    ]);
  }

  /* ---------- Leere Kategorie ---------- */
  function schirmLeer(kat) {
    return h("section", { class: "schirm" }, [
      h("div", { class: "kopf" }, [h("button", { type: "button", class: "zurueck", on: { click: () => setze({ k: null }, true) } },
        [symbol(PFEIL_ZURUECK, "sym klein"), "Kategorien"])]),
      titel(kat.name),
      h("div", { class: "karte leise" }, [
        h("p", { class: "gross" }, ["Hier kommen bald Modelle."]),
        h("p", null, ["Wir tragen gerade Datenblätter zusammen. Bis dahin hilft der ausführliche Ratgeber."]),
        h("a", { href: "ratgeber.html", class: "knopf neben" }, ["Zum Ratgeber"]),
      ]),
    ]);
  }

  /* ---------- Schirm 2: Budget, Größe, Bauart ---------- */
  function budgetFeld(kat, sofort) {
    const id = "budget-" + kat.id + (sofort ? "-oben" : "");
    const eingabe = h("input", {
      id, type: "number", inputmode: "numeric", min: "1", max: "100000", step: "1", class: "budget-zahl",
      placeholder: "egal", value: zustand.b ? String(zustand.b) : null, "aria-describedby": sofort ? null : id + "-hilfe", "data-fokus": "budget",
      on: { input: e => {
        const v = Number(e.target.value);
        budgetSetzen(e.target.value !== "" && isFinite(v) && v >= 1 ? Math.min(100000, Math.round(v)) : null, e.target);
      } },
    });
    budgetTeile.push(eingabe);
    return h("div", { class: "budget-zeile" }, [
      h("label", { for: id, class: sofort ? "budget-label klein" : "budget-label visuell-weg" }, ["Höchstens"]),
      h("span", { class: "budget-box" }, [eingabe, h("span", { class: "euro", "aria-hidden": "true" }, ["€"])]),
    ]);
  }
  function budgetChips(kat, sofort) {
    const stufen = B.budgetStufen(kat.modelle);
    const auswahl = h("div", { class: sofort ? "chips kompakt" : "chips", role: "group", "aria-label": "Schnellwahl Budget" },
      stufen.map(s => chip("bis " + eur(s), zustand.b === s, () => budgetSetzen(s, null), { "data-budget": String(s), "data-fokus": "chip-b" + s }))
        .concat([chip("Egal", !zustand.b, () => budgetSetzen(null, null), { "data-budget": "egal", "data-fokus": "chip-egal" })]));
    budgetTeile.push(auswahl);
    return auswahl;
  }
  /* Budget ändern, ohne Eingabefeld und Schnellwahl neu zu bauen (Fokus und Schreibmarke bleiben) */
  function budgetSetzen(b, quelle) {
    zustand = Object.assign({}, zustand, { b });
    try { history.replaceState(null, "", alsAdresse(zustand)); } catch (e) { /* ohne Verlauf */ }
    budgetAnzeigen(b, quelle);
    const kat = katVon(zustand.k);
    const koerper = document.getElementById("ergebnis-koerper");
    if (kat && koerper && zustand.s === "ergebnis") fuelleErgebnis(kat, koerper);
  }
  /* Eingabefeld (außer der gerade tippenden Quelle) und Schnellwahl auf Budget b setzen */
  function budgetAnzeigen(b, quelle) {
    for (const t of budgetTeile) {
      if (t.tagName === "INPUT") { if (t !== quelle) t.value = b ? String(b) : ""; continue; }
      for (const c of Array.from(t.childNodes)) {
        const w = c.getAttribute("data-budget");
        c.setAttribute("aria-pressed", (w === "egal" ? !b : w === String(b)) ? "true" : "false");
      }
    }
  }
  function schirmBudget(kat) {
    const teile = [
      kopf(kat, "budget"),
      titel("Wie viel möchtest du höchstens ausgeben?"),
      budgetFeld(kat, false),
      h("p", { id: "budget-" + kat.id + "-hilfe", class: "hilfe" }, ["Betrag in Euro eintippen oder unten wählen. Leer lassen heißt: egal."]),
      budgetChips(kat, false),
    ];
    if (kat.id === "fernseher") {
      teile.push(h("fieldset", { class: "frage" }, [
        h("legend", null, ["Welche Größe soll er haben?"]),
        h("div", { class: "chips" }, [chip("Egal", !zustand.g, () => setze({ g: null }, false), { "data-fokus": "g-egal" })]
          .concat(GROESSEN.map(g => chip(g.text, zustand.g === g.id, () => setze({ g: g.id }, false), { "data-fokus": "g-" + g.id })))),
      ]));
    }
    const bauarten = bauartWerte(kat);
    if (bauarten.length > 1) {
      teile.push(h("fieldset", { class: "frage" }, [
        h("legend", null, ["Welche Bauart?"]),
        h("div", { class: "chips" }, [chip("Egal", !zustand.ba, () => setze({ ba: null }, false), { "data-fokus": "ba-egal" })]
          .concat(bauarten.map(b => chip(stufeText(b), zustand.ba === b, () => setze({ ba: b }, false), { "data-fokus": "ba-" + b })))),
      ]));
    }
    teile.push(h("div", { class: "weiter" }, [
      h("button", { type: "button", class: "knopf haupt", on: { click: () => setze({ s: kat.fragen.length ? "fragen" : "ergebnis" }, true) } },
        [kat.fragen.length ? "Weiter zu den Fragen" : "Ergebnis zeigen"]),
    ]));
    return h("section", { class: "schirm" }, teile);
  }

  /* ---------- Schirm 3: Fragen ---------- */
  function schirmFragen(kat) {
    const wirksam = antwortenWirksam(kat);
    const fragen = kat.fragen.map(f => {
      const name = "frage-" + f.id;
      const hatEgal = f.antworten.some(x => x.id === "egal");
      const optionen = (hatEgal ? [] : [{ id: "", text: "Egal / weiß nicht" }]).concat(f.antworten.map(a => ({ id: a.id, text: a.text })));
      return h("fieldset", { class: "frage" }, [
        h("legend", null, [f.text]),
        h("div", { class: "optionen" }, optionen.map(o => {
          const oid = name + "-" + (o.id || "egal");
          const an = (wirksam[f.id] || "") === o.id;
          return h("label", { class: "option", for: oid }, [
            h("input", { type: "radio", id: oid, name, value: o.id, checked: an, "data-fokus": oid,
              on: { change: () => {
                const a = Object.assign({}, zustand.a);
                if (o.id && o.id !== "egal") a[f.id] = o.id; else delete a[f.id];
                setze({ a }, false);
              } } }),
            h("span", { text: o.text }),
          ]);
        })),
      ]);
    });
    return h("section", { class: "schirm" }, [
      kopf(kat, "fragen"),
      titel("Noch " + (kat.fragen.length === 1 ? "eine kurze Frage" : kat.fragen.length + " kurze Fragen")),
      h("p", { class: "lead" }, ["Jede Antwort verschiebt, was zählt. Was du nicht weißt, lässt du auf „egal“."]),
    ].concat(fragen, [h("div", { class: "weiter" }, [
      h("button", { type: "button", class: "knopf haupt", on: { click: () => setze({ s: "ergebnis" }, true) } }, ["Ergebnis zeigen"]),
    ])]));
  }

  /* ---------- Ergebnis ---------- */
  function schirmErgebnis(kat) {
    // G1: Empfehlung oben, Regler dazwischen (bleibt beim Neurechnen stehen, damit Ziehen nicht abbricht), Liste unten
    const koerper = h("div", { id: "ergebnis-koerper", class: "ergebnis-teil" });
    const unten = h("div", { id: "ergebnis-unten", class: "ergebnis-teil" });
    reglerTeile = []; reglerZurueck = null;
    const prioPanel = reglerPanel(kat);
    ergebnisTeile = { unten, prio: prioPanel };
    const s = h("section", { class: "schirm ergebnis" }, [
      h("div", { class: "kopf" }, [
        h("button", { type: "button", class: "zurueck", on: { click: () => setze({ s: kat.fragen.length ? "fragen" : "budget" }, true) } },
          [symbol(PFEIL_ZURUECK, "sym klein"), "Antworten ändern"]),
        h("button", { type: "button", class: "zurueck rechts", on: { click: () => setze({ k: null }, true) } }, ["Andere Kategorie"]),
      ]),
      titel(kat.name),
      h("div", { class: "budget-leiste" }, [budgetFeld(kat, true), budgetChips(kat, true)]),
      h("p", { id: "ergebnis-status", class: "visuell-weg", role: "status" }),
      koerper,
      prioPanel,
      unten,
    ]);
    fuelleErgebnis(kat, koerper);
    return s;
  }

  /* ---------- G1: Prioritäten-Regler „Deine Prioritäten verschieben“ ---------- */
  function anteilText(g) {
    if (!(g > 0)) return "zählt nicht";
    return g < 0.5 ? "zählt unter 1 %" : "zählt " + Math.round(g) + " %";
  }
  // Reihenfolge nach dem Gewicht aus den Antworten (ohne Regler), damit die Liste beim Ziehen nicht springt
  function reglerFelder(kat) {
    const basis = B.gewichte(kat, antwortenWirksam(kat));
    return kat.felder.filter(f => basis[f.id] > 0).sort((a, b) => basis[b.id] - basis[a.id]);
  }
  // G1-01: welche Regler stehen gerade; ändert sich die Feldauswahl (Adresse, Zurück), wird das Panel neu gebaut
  const reglerSchluessel = felder => felder.map(f => f.id).join("~");
  let reglerStand = null;
  function reglerPanel(kat) {
    const felder = reglerFelder(kat);
    reglerStand = reglerSchluessel(felder);
    const panel = h("section", { id: "prio", class: "panel prio", "aria-labelledby": "prio-titel", hidden: !felder.length });
    if (!felder.length) return panel;
    const zeile = f => {
      const id = "prio-" + f.id;
      const s = Object.prototype.hasOwnProperty.call(zustand.p, f.id) ? zustand.p[f.id] : PRIO_NORMAL;
      const ausgabe = h("output", { id: id + "-wert", for: id, class: "regler-wert" });
      const eingabe = h("input", { type: "range", id, min: "0", max: "4", step: "1", value: String(s), class: "regler-spur", "data-fokus": id,
        on: { input: e => prioSetzen(kat, f.id, Number(e.target.value)) } });
      reglerTeile.push({ fid: f.id, eingabe, ausgabe });
      return h("div", { class: "regler" }, [h("label", { for: id, class: "regler-name", text: f.name }), ausgabe, eingabe]);
    };
    const offen = felder.slice(0, PRIO_OFFEN), rest = felder.slice(PRIO_OFFEN);
    anhaengen(panel, [
      h("h2", { id: "prio-titel", class: "prio-titel", tabindex: "-1" }, ["Deine Prioritäten verschieben"]),
      h("p", { class: "hilfe" }, ["Je Merkmal fünf Stufen von „aus“ bis „viel mehr“. Die Liste darunter rechnet sofort neu. Der Preis zählt nie in die Note."]),
      h("div", { class: "regler-liste" }, offen.map(zeile)),
      rest.length ? h("details", { class: "regler-mehr" }, [h("summary", null, ["Alle Merkmale (" + felder.length + ")"]), h("div", { class: "regler-liste" }, rest.map(zeile))]) : null,
      reglerZurueck = h("button", { type: "button", id: "prio-zurueck", class: "knopf neben", "data-fokus": "prio-zurueck", on: { click: () => {
        zustand = Object.assign({}, zustand, { p: {} });
        try { history.replaceState(null, "", alsAdresse(zustand)); } catch (e) { /* ohne Verlauf */ }
        reglerAnzeigen(kat);
        fuelleErgebnis(kat, document.getElementById("ergebnis-koerper"), true);
        const erster = reglerTeile[0] && reglerTeile[0].eingabe;
        if (erster && erster.focus) erster.focus();
      } } }, ["Zurück auf deine Antworten"]),
    ]);
    reglerAnzeigen(kat);
    return panel;
  }
  /* Regler, Anteile und Zurück-Knopf auf den Zustand setzen (ohne Neuaufbau, Ziehen und Fokus bleiben) */
  function reglerAnzeigen(kat) {
    if (!reglerTeile.length) return;
    const gew = B.gewichte(kat, antwortenWirksam(kat), prioFaktoren());
    for (const t of reglerTeile) {
      const s = Object.prototype.hasOwnProperty.call(zustand.p, t.fid) ? zustand.p[t.fid] : PRIO_NORMAL;
      if (String(t.eingabe.value) !== String(s)) t.eingabe.value = String(s);
      const text = PRIO_NAMEN[s] + ", " + anteilText(gew[t.fid]);
      t.ausgabe.textContent = text;
      t.eingabe.setAttribute("aria-valuetext", text);
      t.eingabe.setAttribute("style", "--fill:" + s * 25 + "%");
    }
    if (reglerZurueck) reglerZurueck.hidden = !Object.keys(zustand.p).length;
  }
  function prioSetzen(kat, fid, s) {
    if (!(s >= 0 && s <= 4)) return;
    const p = Object.assign({}, zustand.p);
    if (s === PRIO_NORMAL) delete p[fid]; else p[fid] = Math.round(s);
    zustand = Object.assign({}, zustand, { p });
    try { history.replaceState(null, "", alsAdresse(zustand)); } catch (e) { /* ohne Verlauf */ }
    reglerAnzeigen(kat);
    fuelleErgebnis(kat, document.getElementById("ergebnis-koerper"), true);
  }

  /* FLIP (240 ms, nur transform): Einträge der Rangliste gleiten an ihren neuen Platz; reduziert: sofort */
  function rangLagen(teil) {
    const lagen = new Map();
    if (!teil || reduziert()) return lagen;
    for (const li of alleKnoten(teil)) {
      const id = li.getAttribute && li.getAttribute("data-modell");
      if (id && li.getBoundingClientRect) lagen.set(id, li.getBoundingClientRect().top - teil.getBoundingClientRect().top);
    }
    return lagen;
  }
  // G1-R2-02: laufende Gleitbewegungen, damit sie bei eingeschalteter Bewegungsreduktion sofort enden
  let gleitend = [];
  function gleitenStoppen() {
    for (const a of gleitend) { try { a.cancel(); } catch (e) { /* schon beendet */ } }
    gleitend = [];
  }
  function rangGleiten(teil, vorher) {
    gleitenStoppen();   // alte Einträge sind ersetzt; ihre Bewegung endet jetzt
    if (!vorher.size || reduziert()) return;
    for (const li of alleKnoten(teil)) {
      const id = li.getAttribute && li.getAttribute("data-modell");
      if (!id || !vorher.has(id) || !li.animate) continue;
      const dy = vorher.get(id) - (li.getBoundingClientRect().top - teil.getBoundingClientRect().top);
      if (Math.abs(dy) < 1) continue;
      const a = li.animate([{ transform: "translateY(" + Math.round(dy) + "px)" }, { transform: "none" }], { duration: 240, easing: "cubic-bezier(0.23, 1, 0.32, 1)" });
      if (a && a.cancel) gleitend.push(a);
    }
  }
  /* G1-R2-01: aufgeklappte Bereiche (<details>, nach Klasse) überstehen einen Neuaufbau; ein Fokusziel in einem
     zugeklappten Bereich wird freigelegt, sonst nimmt der Browser den Fokus nicht an */
  function offeneBereiche(teile) {
    const offen = new Set();
    for (const t of teile) if (t) for (const k of alleKnoten(t)) if (k.tagName === "DETAILS" && k.open && k.className) offen.add(k.className);
    return offen;
  }
  function bereicheOeffnen(teile, offen) {
    if (!offen.size) return;
    for (const t of teile) if (t) for (const k of alleKnoten(t)) if (k.tagName === "DETAILS" && offen.has(k.className)) k.open = true;
  }
  function fokusFreilegen(f) {
    for (let k = f && f.parentNode; k; k = k.parentNode) if (k.tagName === "DETAILS" && !k.open) k.open = true;
  }
  function alleKnoten(k, l) {
    l = l || [];
    for (const c of Array.from(k.childNodes || [])) if (c.nodeType === 1) { l.push(c); alleKnoten(c, l); }
    return l;
  }

  function fuelleErgebnis(kat, koerper, gleiten) {
    const unten = ergebnisTeile ? ergebnisTeile.unten : null;
    const fokus = document.activeElement && document.activeElement.getAttribute ? document.activeElement.getAttribute("data-fokus") : null;
    const fokusDrin = fokus && (findeFokus(koerper, fokus) || findeFokus(unten, fokus));
    const vorher = gleiten ? rangLagen(unten) : new Map();
    const offen = offeneBereiche([koerper, unten]);
    leeren(koerper);
    if (unten) leeren(unten);
    const ziel = unten || koerper;
    const r = B.auswerten(kat, daten.regeln, { antworten: antwortenWirksam(kat), budget: zustand.b, filter: filterWirksam(kat), sortierung: zustand.o, prioritaeten: prioFaktoren() });
    const prio = ergebnisTeile ? ergebnisTeile.prio : null;
    if (prio) prio.hidden = !r.rang.length || !reglerTeile.length;
    anhaengen(koerper, [auswahlZeile(kat)]);
    if (!r.rang.length) {
      anhaengen(koerper, [h("div", { class: "karte leise" }, [
        h("p", { class: "gross" }, ["Kein Modell passt zu allen Antworten."]),
        h("p", null, [r.ausgeschlossen + " von " + r.anzahl + " Modellen fallen durch eine Antwort oder einen Filter heraus. Lockere eine Antwort, dann erscheinen sie wieder."]),
        h("button", { type: "button", class: "knopf neben", on: { click: () => setze({ s: kat.fragen.length ? "fragen" : "budget" }, true) } }, ["Antworten ändern"]),
      ])]);
    } else {
      if (r.empfehlung) anhaengen(koerper, [empfehlungsKarte(kat, r)]);
      else anhaengen(koerper, [h("div", { class: "karte leise" }, [h("p", null, [ohneEmpfehlungText(r)])])]);
      if (r.aufpreis) anhaengen(koerper, [hinweisKarte("mehr", "Lohnt sich mehr?", r.aufpreis.text, r.aufpreis.modell)]);
      if (r.spar) anhaengen(koerper, [hinweisKarte("weniger", "Geht es günstiger?", r.spar.text, r.spar.modell)]);
      anhaengen(ziel, [rangliste(kat, r), vergleich(kat, r, prioFaktoren())]);
    }
    zeichneAblage(kat);
    glasBeobachten(koerper);
    bereicheOeffnen([koerper, unten], offen);
    if (unten) rangGleiten(unten, vorher);
    const status = document.getElementById("ergebnis-status");
    if (status) status.textContent = r.rang.length
      ? r.rang.length + (r.rang.length === 1 ? " Modell passt" : " Modelle passen") + (!r.empfehlung ? "." : r.empfehlung.note === null
        ? ". Modell ohne Note: " + r.empfehlung.modell.hersteller + " " + modellName(r.empfehlung.modell) + (r.empfehlung.art === "keine_merkmale" ? ", kein Merkmal zählt in die Note." : ", für eine Note fehlen Datenblattwerte.")   // R2-09, P1-04
        : ". Passt am besten: " + r.empfehlung.modell.hersteller + " " + modellName(r.empfehlung.modell) + ", " + note(r.empfehlung.note) + " Punkte.")
      : "Kein Modell passt.";
    if (fokusDrin) { const f = findeFokus(koerper, fokus) || findeFokus(unten, fokus); if (f && f.focus) { fokusFreilegen(f); f.focus(); } }
  }

  /* P1-03/P1-04 (r2): Grund für die fehlende Empfehlung aus den tatsächlichen Kombinationen von Note, Preis und Budget.
     Ohne Empfehlung gilt (bewertung.js auswerten): kein Modell mit Preis im Budget, und kein Modell mit Note hat einen Preis.
     Satz 1 nennt den Notengrund, Satz 2 den Preisgrund; gemischte Ursachen werden beide genannt. */
  function ohneEmpfehlungText(r) {
    const ende = " Deshalb empfehlen wir keins. Die Liste unten zeigt sie trotzdem.";
    const ohneNote = r.rang.filter(e => e.note === null);
    const mitPreis = r.rang.filter(e => e.preis !== null).length;
    // Notengrund einer Gruppe ohne Note: Datenblatt, kein Merkmal oder beides
    const grund = l => { const k = l.filter(e => e.art === "keine_merkmale").length;
      return k === 0 ? "Datenblattwerte fehlen" : k === l.length ? "für deine Angaben kein Merkmal zählt" : "Datenblattwerte fehlen oder für deine Angaben kein Merkmal zählt"; };
    if (ohneNote.length < r.rang.length) {
      // 08 G: ohne bekannten Preis keine Empfehlung
      if (!mitPreis) return "Für die passenden Modelle kennen wir gerade keinen Preis." + ende;
      // P1-03/P1-04 r3: Modelle mit Preis haben hier nie eine Note (sonst gäbe es eine Empfehlung); Grund nennen
      return "Für die Modelle mit Note kennen wir gerade keinen Preis, und die Modelle mit Preis liegen über deinem Budget und haben keine Note, weil "
        + grund(r.rang.filter(e => e.preis !== null)) + "." + ende;
    }
    const km = ohneNote.filter(e => e.art === "keine_merkmale").length;
    const note = km === 0 ? "Für keins der passenden Modelle reichen die Datenblattangaben für eine Note."
      : km === ohneNote.length ? "Für deine Angaben zählt gerade kein Merkmal in die Note."
      : "Keins der passenden Modelle hat eine Note: Bei einigen fehlen Datenblattwerte, bei den anderen zählt für deine Angaben kein Merkmal.";
    const preis = !mitPreis ? " Einen Preis kennen wir für keins."
      : mitPreis === r.rang.length ? " Alle liegen über deinem Budget."
      : " Die Modelle mit Preis liegen über deinem Budget, für die übrigen kennen wir keinen Preis.";
    return note + preis + ende;
  }

  /* Deine Angaben mit Fragetext (08 F): „Antwort“ allein (z. B. „Ja“) sagt ohne Frage nichts */
  function auswahlZeile(kat) {
    const zeilen = [];
    const wirksam = antwortenWirksam(kat);
    for (const f of kat.fragen) {
      const a = f.antworten.find(x => x.id === wirksam[f.id]);
      if (a && a.id !== "egal") zeilen.push([f.text, a.text]);
    }
    if (zustand.g) zeilen.push(["Größe", (GROESSEN.find(g => g.id === zustand.g) || {}).text]);
    if (zustand.ba) zeilen.push(["Bauart", stufeText(zustand.ba)]);
    if (!zeilen.length) return h("p", { class: "auswahl" }, ["Ohne Angaben zu deiner Nutzung bewertet."]);
    const liste = h("dl", { class: "angaben-liste" });
    for (const [frage, antwort] of zeilen) anhaengen(liste, [h("dt", { text: frage }), h("dd", { text: antwort })]);
    return h("section", { class: "angaben", "aria-labelledby": "angaben-titel" }, [
      h("h2", { id: "angaben-titel", class: "angaben-titel" }, ["Deine Angaben"]), liste]);
  }

  /* Prozentwert für style: nur endliche Zahlen, auf 0..100 begrenzt (F-09; datenPruefen prüft die Regeln vorher). */
  function prozent(x) { const z = typeof x === "number" && isFinite(x) ? x : 0; return Math.max(0, Math.min(100, z)); }
  /* D12/G1: Punktbahn 0–100 ohne Klassenbänder und ohne Kappung; die Spanne zeigt, wie unsicher eine Datenblatt-Note ist.
     opt.achse: Marken 0/50/100 darunter · opt.farbe: Vergleichsfarbe 1–3 (sonst Tinte) */
  function notenSkala(e, opt) {
    const o = opt || {};
    const n = prozent(e.note);
    const spanne = e.spanne ? [Math.max(0, n - e.spanne), Math.min(100, n + e.spanne)] : null;
    const beschr = "Note " + Math.round(n) + " von 100" + (spanne ? ", Spanne etwa " + Math.round(spanne[0]) + " bis " + Math.round(spanne[1]) : "");
    const bahn = h("div", { class: "skala-bahn" });
    if (spanne) bahn.appendChild(h("span", { class: "skala-spanne", style: "left:" + spanne[0] + "%;width:" + (spanne[1] - spanne[0]) + "%" }));
    bahn.appendChild(h("span", { class: "skala-punkt", style: "left:" + n + "%" }));
    return h("div", { class: "skala" + (o.farbe ? " farbe-" + o.farbe : ""), role: "img", "aria-label": (o.name ? o.name + ": " : "") + beschr },
      [bahn, o.achse ? achse() : null]);
  }
  function achse(klasse) {
    return h("div", { class: klasse || "skala-marken", "aria-hidden": "true" }, [0, 50, 100].map(x => h("span", { style: "left:" + x + "%", text: String(x) })));
  }
  /* Note mit Herkunft; die Rechnung ist eingeklappt (08 F) */
  function notenBlock(e) {
    if (e.note === null) return h("p", { class: "note-zeile marke" }, [e.art === "keine_merkmale" ? "Keine Note: kein Merkmal zählt" : "Keine Note: zu wenig Daten"]);
    const spanne = e.spanne ? " Die Zahl ist deshalb unsicher, etwa " + Math.round(Math.max(0, e.note - e.spanne)) + " bis " + Math.round(Math.min(100, e.note + e.spanne)) + "." : "";
    const erklaerung = e.art === "getestet"
      ? "Die Note mischt ein unabhängiges Testergebnis (60 %) mit den Datenblattwerten (40 %), gewichtet nach deinen Antworten."
      : "Die Punkte zählen die Ausstattung laut Hersteller (Datenblatt, EU-Label), gewichtet nach deinen Antworten. Wie gut Bild, Ton oder Saugen wirklich sind, steht in keinem Datenblatt." + spanne
        + " Belegt sind " + Math.round(prozent(e.abdeckung * 100)) + " % der Merkmale, die für dich zählen.";
    return h("div", { class: "note-block" }, [
      h("div", { class: "note-zeile" }, [
        h("p", { class: "note-zahl" }, [h("span", { class: "zahl", text: note(e.note) }), h("span", { class: "von" }, [" von 100"])]),
        h("p", { class: "marke" }, [e.art === "getestet" ? "mit unabhängigem Test" : "aus dem Datenblatt, kein Test"]),
      ]),
      notenSkala(e, { achse: true }),
      h("details", { class: "note-herkunft" }, [
        h("summary", null, ["So kommt die Note zustande"]),
        h("p", { class: "hilfe" }, [erklaerung]),
      ]),
    ]);
  }

  function preisBlock(e, gross) {
    const p = e.modell.preis;
    if (!p) return h("div", { class: "preis" }, [h("p", { class: "preis-betrag leise-text" }, ["Preis unbekannt"])]);
    return h("div", { class: "preis" }, [
      h("p", { class: gross ? "preis-betrag" : "preis-betrag klein" }, [eur(p.eur)]),
      h("p", { class: "preis-quelle" }, ["bei " + p.haendler + ", Stand " + datum(p.stand)]),
    ]);
  }

  function empfehlungsKarte(kat, r) {
    const e = r.empfehlung, m = e.modell;
    const felder = Object.fromEntries(kat.felder.map(f => [f.id, f]));
    let kopfText = zustand.b ? "Passt am besten zu dir bis " + eur(zustand.b) : "Passt am besten zu dir";
    let warnung = null;
    if (r.status === "ueber_budget") {
      kopfText = "Im Budget passt nichts";
      warnung = "Das beste passende Modell kostet " + eur(e.preis) + ", also " + eur(Math.round(e.preis - zustand.b)) + " mehr als geplant.";
    } else if (r.status === "ohne_note") {
      kopfText = zustand.b ? "Im Budget bis " + eur(zustand.b) + ": Modell ohne Note" : "Passendes Modell ohne Note";
      warnung = (e.art === "keine_merkmale" ? "Für deine Angaben zählt gerade kein Merkmal in die Note." : "Für eine Note fehlen Datenblattwerte.") + " Das Modell erfüllt deine Angaben" + (e.unbelegt.length ? " soweit belegt" : "")
        + ", ist aber nicht mit anderen vergleichbar bewertet. Prüfe es vor dem Kauf.";
    } else if (r.status === "unbelegt") {
      warnung = "Nicht im Datenblatt belegt: " + e.unbelegt.map(u => (felder[u.feld] || { name: u.feld }).name).join(", ") + ". Prüfe das vor dem Kauf.";
    }
    const angebot = m.preis ? link(m.preis.url, "Zum Angebot", "knopf haupt") : null;
    if (angebot) angebot.setAttribute("aria-label", "Zum Angebot: " + modellName(m) + " bei " + m.preis.haendler + " (öffnet neues Fenster)");
    const variante = varianteText(m);
    // 08 F: Preis und Knopf oben, die Note darunter
    return h("article", { class: "karte empfehlung", "aria-labelledby": "empf-name" }, [
      h("p", { class: "karte-kopf" + (r.status === "ueber_budget" || r.status === "ohne_note" ? " warn" : "") }, [kopfText]),
      h("p", { class: "hersteller", text: m.hersteller }),
      h("h2", { id: "empf-name", class: "modell" }, [m.name]),
      variante ? h("p", { class: "variante", text: variante }) : null,
      h("div", { class: "kauf" }, [preisBlock(e, true), angebot]),
      warnung ? h("p", { class: "warnung" }, [warnung]) : null,
      notenBlock(e),
      punkteHerkunft(e, felder),
      testLinks(m),
      vergleichSchalter(m, "empf"),
    ]);
  }

  /* G1: „Woher die Punkte kommen“: je wirksamem Merkmal (Beiträge und fehlende, nach Gewicht) Name, Anteil, Wert und
     Teilpunkte als Balken in Tinte; fehlende Werte gestrichelt. Die 5 schwersten offen, der Rest eingeklappt. */
  function punkteHerkunft(e, felder) {
    const zeilen = (e.beitraege || []).map(b => ({ feld: b.feld, gewicht: b.gewicht, tp: b.teilpunkte }))
      .concat((e.fehlend || []).map(f => ({ feld: f.feld, gewicht: f.gewicht, tp: null })))
      .sort((a, b) => b.gewicht - a.gewicht);
    if (!zeilen.length) return null;
    const zeile = z => {
      const f = felder[z.feld] || { name: z.feld, typ: "stufe" };
      const fehlt = z.tp === null;
      const tp = fehlt ? 0 : prozent(z.tp);
      return h("li", { class: "hz" + (fehlt ? " fehlt" : "") }, [
        h("p", { class: "hz-kopf" }, [h("span", { class: "hz-name", text: f.name }), h("span", { class: "hz-anteil", text: anteilText(z.gewicht) })]),
        // G1-02: fehlende Werte zählen nicht als 0 Teilpunkte (bewertung.js nimmt sie aus dem Mittel)
        h("div", { class: "hz-bahn", role: "img", "aria-label": fehlt ? "nicht angegeben" : Math.round(tp) + " von 100 Teilpunkten" },
          fehlt ? [] : [h("span", { class: "hz-balken", style: "width:" + tp + "%" })]),
        h("p", { class: "hz-fuss" }, [h("span", { class: "hz-wert", text: fehlt ? "nicht angegeben" : wertText(f, (e.modell.werte || {})[z.feld]) }),
          h("span", { class: "hz-punkte", "aria-hidden": "true", text: fehlt ? "–" : String(Math.round(tp)) })]),
      ]);
    };
    const offen = zeilen.slice(0, PRIO_OFFEN), rest = zeilen.slice(PRIO_OFFEN);
    return h("section", { class: "herkunft", "aria-labelledby": "herkunft-titel" }, [
      h("h3", { id: "herkunft-titel" }, ["Woher die Punkte kommen"]),
      h("ul", { class: "hz-liste" }, offen.map(zeile)),
      rest.length ? h("details", { class: "hz-mehr" }, [h("summary", null, ["Alle Merkmale (" + zeilen.length + ")"]), h("ul", { class: "hz-liste" }, rest.map(zeile))]) : null,
    ]);
  }

  /* Testberichte anderer nur als Link (D13); die Datenprüfung lässt nur https-Links mit Titel durch */
  function testLinks(m) {
    const links = (m.tests || []).slice(0, 3).map(t => {
      const a = link(t.url, t.titel, "textlink");
      if (a) a.setAttribute("aria-label", t.titel + " (Testbericht, öffnet neues Fenster)");
      return a;
    }).filter(Boolean);
    if (!links.length) return null;
    return h("div", { class: "tests" }, [h("h3", null, ["Tests anderer"]), h("ul", null, links.map(a => h("li", null, [a])))]);
  }

  function hinweisKarte(art, ueberschrift, text, e) {
    const m = e.modell;
    const angebot = m.preis ? link(m.preis.url, "Zum Angebot", "knopf neben") : null;
    if (angebot) angebot.setAttribute("aria-label", "Zum Angebot: " + modellName(m) + " (öffnet neues Fenster)");
    return h("aside", { class: "karte hinweis glas-hin " + art, "aria-label": ueberschrift }, [
      h("p", { class: "hinweis-text", text }),
      h("p", { class: "hinweis-modell" }, [m.hersteller + " " + modellName(m) + ", " + note(e.note) + " Punkte, " + (e.preis !== null ? eur(e.preis) : "Preis unbekannt")]),
      h("div", { class: "hinweis-knoepfe" }, [angebot, vergleichSchalter(m, art)]),
    ]);
  }

  /* G1: Umschaltknopf statt Kontrollkästchen (aria-pressed); voll: deaktiviert mit Grund */
  function vergleichSchalter(m, ort) {
    const an = zustand.v.indexOf(m.id) >= 0;
    const voll = !an && zustand.v.length >= 3;
    const id = "vgl-" + ort + "-" + m.id;
    const knopf = h("button", { type: "button", id, class: "vgl-knopf", "aria-pressed": an ? "true" : "false", disabled: voll, "data-fokus": id,
      on: { click: () => {
        const v = zustand.v.filter(x => x !== m.id);
        if (!an) v.push(m.id);
        setze({ v: v.slice(0, 3) }, false);
      } } }, [
        voll ? null : h("span", { class: "vgl-zeichen", "aria-hidden": "true", text: an ? "✓" : "＋" }),
        voll ? "Vergleich voll (3)" : an ? "Im Vergleich" : "Vergleichen",
        h("span", { class: "visuell-weg", text: ": " + modellName(m) }),
      ]);
    return knopf;
  }

  /* Glas-Hinweise: Lichtstreif nur, solange die Karte sichtbar ist (reduziert steht er, CSS) */
  function glasBeobachten(teil) {
    // G1-04: alte Karten immer abmelden, auch wenn keine neuen kommen
    if (glasBeobachter) glasBeobachter.disconnect();
    const karten = alleKnoten(teil).filter(k => k.classList && k.classList.contains("glas-hin"));
    if (!karten.length) return;
    if (!glasBeobachter && typeof IntersectionObserver === "function") {
      glasBeobachter = new IntersectionObserver(eintraege => {
        for (const x of eintraege) x.target.classList.toggle("is-sicht", x.isIntersecting);
      });
    }
    for (const k of karten) { if (glasBeobachter) glasBeobachter.observe(k); else k.classList.add("is-sicht"); }
  }

  function rangZeile(e, nr, r, felder) {
    const m = e.modell;
    const marken = [];
    if (e.note === null && e.art === "keine_merkmale") marken.push("kein Merkmal zählt in die Note");
    else if (e.note === null && e.fehlend && e.fehlend.length) marken.push("fehlt: " + e.fehlend.slice(0, 3).map(f => (felder[f.feld] || { name: f.feld }).name).join(", "));
    if (e.imBudget === false) marken.push("über Budget");
    if (e.imBudget === null && zustand.b) marken.push("Preis unbekannt");
    if (e.unbelegt.length) marken.push("nicht belegt: " + e.unbelegt.map(u => (felder[u.feld] || { name: u.feld }).name).join(", "));
    const angebot = m.preis ? link(m.preis.url, "Angebot", "textlink") : null;
    if (angebot) angebot.setAttribute("aria-label", "Angebot für " + modellName(m) + " (öffnet neues Fenster)");
    return h("li", { class: "rang-eintrag" + (nr === null ? " ohne-nr" : "") + (e === r.empfehlung ? " erste" : ""), "data-modell": m.id }, [
      nr === null ? null : h("span", { class: "rang-nr", "aria-hidden": "true", text: String(nr) }),
      h("div", { class: "rang-haupt" }, [
        h("p", { class: "rang-name" }, [h("span", { class: "hersteller-inline", text: m.hersteller + " " }), modellName(m)]),
        marken.length ? h("p", { class: "rang-marken", text: marken.join("; ") }) : null,
        h("div", { class: "rang-aktionen" }, [angebot, vergleichSchalter(m, "rang")]),
      ]),
      h("div", { class: "rang-werte" }, [
        e.note === null ? null : h("p", { class: "rang-note" }, [h("span", { class: "zahl", text: note(e.note) })]),
        h("p", { class: "rang-preis", text: e.preis !== null ? eur(e.preis) : "–" }),
      ]),
      e.note === null ? null : h("div", { class: "rang-bahn" }, [notenSkala(e, { name: modellName(m) })]),
    ]);
  }

  /* G1: „Vorn: X +n vor Y“ für die zwei besten angezeigten Noten; unter 3 Punkten gleichauf (Ratgeber-Regel) */
  function vornZeile(bewertet) {
    if (bewertet.length < 2) return null;
    const l = bewertet.slice().sort((a, b) => Math.round(b.note) - Math.round(a.note));
    const d = Math.round(l[0].note) - Math.round(l[1].note);
    const n = e => e.modell.hersteller + " " + modellName(e.modell);
    return h("p", { class: "rang-vorn" + (d >= 3 ? "" : " gleichauf") }, [d >= 3
      ? "Vorn: " + n(l[0]) + " mit " + d + " Punkten vor " + n(l[1]) + "."
      : "Gleichauf: " + n(l[0]) + " und " + n(l[1]) + " liegen weniger als 3 Punkte auseinander."]);
  }

  /* P1-04: Grund der Gruppe „Noch nicht bewertbar“ nur nennen, wenn er für die Modelle zutrifft */
  function offenText(offen) {
    const keine = offen.filter(e => e.art === "keine_merkmale").length;
    const ende = " Die Modelle passen zu deinen Antworten, stehen aber ohne Rang hier.";
    if (keine === offen.length) return "Für deine Angaben zählt gerade kein Merkmal in die Note." + ende;
    if (keine === 0) return "Für eine Note fehlen zu viele Datenblattwerte." + ende;
    return "Für eine Note fehlen zu viele Datenblattwerte, oder es zählt kein Merkmal in die Note." + ende;
  }

  function rangliste(kat, r) {
    const felder = Object.fromEntries(kat.felder.map(f => [f.id, f]));
    const imBudget = r.rang.filter(e => e.imBudget === true);
    const sonst = r.rang.filter(e => e.imBudget !== true);
    const zeigen = zustand.b && !teurereZeigen ? imBudget : r.rang;
    // 07 B10: Modelle ohne Note stehen in einer eigenen Gruppe ohne Rangnummer
    const bewertet = zeigen.filter(e => e.note !== null), offen = zeigen.filter(e => e.note === null);
    // 07 B15 / P1-01: Rang = Notenrang aus der angezeigten Zahl, unabhängig von der Sortierung
    // (gleiche angezeigte Note → gleicher Rang; Rang = 1 + Anzahl der Modelle mit höherer angezeigter Note)
    const nummern = bewertet.map(e => 1 + bewertet.filter(x => Math.round(x.note) > Math.round(e.note)).length);
    const sortierung = h("div", { class: "segment", role: "radiogroup", "aria-label": "Sortieren nach" }, SORTEN.map(([id, text]) =>
      h("label", { class: "segment-wahl" }, [
        h("input", { type: "radio", name: "sortierung", value: id, checked: zustand.o === id, "data-fokus": "sort-" + id,
          on: { change: () => setze({ o: id }, false) } }),
        h("span", { text }),
      ])));
    const teile = [
      h("div", { class: "rang-kopf" }, [h("h2", { id: "rang-titel" }, ["Alle passenden Modelle"]), sortierung]),
      vornZeile(bewertet),
      bewertet.length ? achse("rang-achse") : null,
      bewertet.length ? h("ol", { class: "rang" }, bewertet.map((e, i) => rangZeile(e, nummern[i], r, felder))) : null,
    ];
    if (offen.length) {
      teile.push(h("section", { class: "offen", "aria-labelledby": "offen-titel" }, [
        h("h3", { id: "offen-titel", class: "offen-titel" }, ["Noch nicht bewertbar (" + offen.length + ")"]),
        h("p", { class: "hilfe" }, [offenText(offen)]),
        h("ul", { class: "rang" }, offen.map(e => rangZeile(e, null, r, felder))),
      ]));
    }
    if (zustand.b && sonst.length) {
      teile.push(h("button", { type: "button", class: "knopf neben breit", "data-fokus": "teurer", "aria-expanded": teurereZeigen ? "true" : "false",
        on: { click: () => { teurereZeigen = !teurereZeigen; zeichne(); } } },
      [teurereZeigen ? "Nur Modelle im Budget zeigen" : "Auch teurere und ohne Preis zeigen (" + sonst.length + ")"]));
    }
    if (r.ausgeschlossen) {
      teile.push(h("p", { class: "hilfe" }, [r.ausgeschlossen + (r.ausgeschlossen === 1 ? " Modell passt" : " Modelle passen") + " nicht zu deinen Antworten und " + (r.ausgeschlossen === 1 ? "ist" : "sind") + " ausgeblendet."]));
    }
    return h("section", { class: "abschnitt", "aria-labelledby": "rang-titel" }, teile);
  }

  /* G1: Vergleich als Bahnen. Farbe je Platz in der Auswahl (farbe-1..3, nur Punkte und Spannen), Name immer als Text.
     Je Merkmal „Vorn: X +n“ ab 3 Teilpunkten Vorsprung, sonst „gleichauf“ (Ratgeber-Regel). */
  function vergleich(kat, r, prio) {
    const gewaehlt = zustand.v.map(id => r.rang.find(e => e.modell.id === id)).filter(Boolean);
    const abschnitt = h("section", { class: "abschnitt", id: "vergleich", "aria-labelledby": "vgl-titel" }, [
      h("h2", { id: "vgl-titel", tabindex: "-1" }, ["Vergleich"]),
    ]);
    if (gewaehlt.length < 2) {
      abschnitt.appendChild(h("p", { class: "hilfe" }, ["Tippe bei bis zu drei Modellen auf „Vergleichen“, dann stehen sie hier untereinander."]));
      return abschnitt;
    }
    const farbe = e => zustand.v.indexOf(e.modell.id) + 1;
    const gew = B.gewichte(kat, antwortenWirksam(kat), prio);
    const reihen = kat.felder.slice().sort((a, b) => (gew[b.id] || 0) - (gew[a.id] || 0));
    const spalten = "spalten-" + gewaehlt.length;
    const kopfzeile = h("div", { class: "vgl-reihe vgl-modelle " + spalten }, gewaehlt.map(e => h("div", { class: "vgl-zelle farbe-" + farbe(e) }, [
      h("p", { class: "vgl-name" }, [h("span", { class: "vgl-farbe", "aria-hidden": "true" }), e.modell.hersteller + " " + modellName(e.modell)]),
      h("p", { class: "vgl-note" }, [h("span", { class: "zahl", text: note(e.note) }), e.note === null ? " keine Note" : " Punkte"]),
      h("p", { class: "vgl-preis", text: e.preis !== null ? eur(e.preis) : "Preis unbekannt" }),
    ])));
    // Gesamtnote je Modell als Punktbahn mit Spanne
    const gesamt = h("div", { class: "vgl-block vgl-gesamt" }, [
      h("p", { class: "vgl-feld" }, [h("span", { class: "vgl-feld-name", text: "Note" })]),
      h("div", { class: "vgl-bahnen" }, gewaehlt.map(e => h("div", { class: "vgl-bahn farbe-" + farbe(e) }, [
        h("span", { class: "vgl-bahn-name", text: modellName(e.modell) }),
        e.note === null ? h("span", { class: "vgl-spur leer", "aria-hidden": "true" }) : notenSkala(e, { farbe: farbe(e), name: modellName(e.modell) }),
        h("span", { class: "vgl-bahn-wert", text: e.note === null ? "keine Note" : note(e.note) }),
      ]))),
      achse("rang-achse vgl-achse"),
    ]);
    const bloecke = reihen.map(f => {
      const zaehlt = gew[f.id] > 0;
      // G1-03: „Vorn/gleichauf“ aus den angezeigten (gerundeten) Teilpunkten, wie in der Rangliste
      const tpVon = e => { const t = (e.modell.teilpunkte || {})[f.id]; return typeof t === "number" && isFinite(t) ? Math.round(prozent(t)) : null; };
      const tps = gewaehlt.map(tpVon).filter(x => x !== null).sort((a, b) => b - a);
      let marke = null, vorneId = null;
      if (zaehlt && tps.length >= 2) {
        const d = tps[0] - tps[1];
        if (d >= 3) {
          const v = gewaehlt.find(e => tpVon(e) === tps[0]);
          vorneId = v.modell.id;
          marke = h("span", { class: "vgl-marke vorn" }, ["Vorn: " + modellName(v.modell) + " +" + Math.round(d)]);
        } else marke = h("span", { class: "vgl-marke" }, ["gleichauf"]);
      }
      return h("div", { class: "vgl-block" }, [
        h("p", { class: "vgl-feld" }, [
          h("span", { class: "vgl-feld-name", text: f.name }),
          h("span", { class: "vgl-feld-anteil", text: f.gewicht === 0 ? "Filter, zählt nicht in die Note" : anteilText(gew[f.id]) }),
          marke,
        ]),
        h("div", { class: "vgl-bahnen" }, gewaehlt.map(e => {
          const w = e.modell.werte[f.id];
          const tp = tpVon(e);
          const vorn = vorneId === e.modell.id;
          const mitPunkt = zaehlt && tp !== null;
          return h("div", { class: "vgl-bahn farbe-" + farbe(e) + (vorn ? " vorn" : "") + (w === undefined ? " fehlt" : "") }, [
            h("span", { class: "vgl-bahn-name", text: modellName(e.modell) }),
            h("span", { class: "vgl-spur" + (mitPunkt ? "" : " leer"), "aria-hidden": "true" },
              mitPunkt ? [h("span", { class: "vgl-punkt", style: "left:" + prozent(tp) + "%" })] : []),
            h("span", { class: "vgl-bahn-wert" }, [wertText(f, w),
              mitPunkt ? h("span", { class: "visuell-weg", text: ", " + Math.round(prozent(tp)) + " von 100 Teilpunkten" }) : null,
              vorn ? h("span", { class: "visuell-weg", text: " (vorn)" }) : null]),
          ]);
        })),
      ]);
    });
    abschnitt.appendChild(h("div", { class: "vgl-tabelle" }, [kopfzeile, gesamt].concat(bloecke)));
    abschnitt.appendChild(h("p", { class: "hilfe" }, ["Punkt auf der Bahn: Teilpunkte von 0 bis 100 im Merkmal. „Vorn“ steht nur bei mindestens 3 Punkten Vorsprung. Die Merkmale stehen in der Reihenfolge, wie stark sie für dich zählen."]));
    return abschnitt;
  }

  /* Ablage unten: wie viele Modelle zum Vergleich gewählt sind */
  function zeichneAblage(kat) {
    const ablage = document.getElementById("ablage");
    if (!ablage) return;
    leeren(ablage);
    const zeigen = !!(kat && zustand.v.length);
    // 07 B12: unten Platz in Höhe der Ablage lassen, damit sie keinen Inhalt verdeckt
    if (document.body && document.body.classList && document.body.classList.toggle) document.body.classList.toggle("mit-ablage", zeigen);
    if (!zeigen) { ablage.hidden = true; return; }
    ablage.hidden = false;
    anhaengen(ablage, [
      h("p", { class: "ablage-text" }, [zustand.v.length + " von 3 gewählt"]),
      h("button", { type: "button", class: "knopf neben", on: { click: () => setze({ v: [] }, false) } }, ["Leeren"]),
      h("button", { type: "button", class: "knopf haupt", disabled: zustand.v.length < 2, on: { click: () => {
        const z = document.getElementById("vgl-titel");
        if (z) { if (z.scrollIntoView) z.scrollIntoView({ behavior: reduziert() ? "auto" : "smooth", block: "start" }); z.focus({ preventScroll: true }); }
      } } }, ["Vergleichen"]),
    ]);
  }

  /* ---------- Zeichnen ---------- */
  function zeichne() {
    if (!daten) return;
    const kat = katVon(zustand.k);
    let schluessel = "kategorien";
    if (kat && !kat.modelle.length) schluessel = "leer:" + kat.id;
    else if (kat) schluessel = (zustand.s === "fragen" && !kat.fragen.length ? "ergebnis" : zustand.s) + ":" + kat.id;
    // Im Ergebnis nur den Körper neu füllen, damit Budgetfeld, Schreibmarke und Fokus bleiben
    const koerper = document.getElementById("ergebnis-koerper");
    if (schluessel === letzterSchirm && schluessel.indexOf("ergebnis:") === 0 && koerper && reglerSchluessel(reglerFelder(kat)) === reglerStand) {
      // Budget kann sich über die Adresse geändert haben (Zurück, Link): Feld und Schnellwahl nachziehen,
      // ein Feld, in dem gerade getippt wird, behält seinen Text
      budgetAnzeigen(zustand.b, document.activeElement);
      reglerAnzeigen(kat);
      fuelleErgebnis(kat, koerper);
      return;
    }
    const fokus = document.activeElement && document.activeElement.getAttribute ? document.activeElement.getAttribute("data-fokus") : null;
    if (glasBeobachter) glasBeobachter.disconnect();   // G1-04: der alte Schirm verschwindet ganz
    budgetTeile = [];
    const offen = schluessel === letzterSchirm ? offeneBereiche([wurzel]) : new Set();
    let schirm;
    if (!kat) schirm = schirmKategorien();
    else if (!kat.modelle.length) schirm = schirmLeer(kat);
    else if (schluessel.indexOf("ergebnis:") === 0) schirm = schirmErgebnis(kat);
    else if (zustand.s === "fragen") schirm = schirmFragen(kat);
    else schirm = schirmBudget(kat);
    leeren(wurzel);
    bereicheOeffnen([schirm], offen);
    wurzel.appendChild(schirm);
    if (schluessel.indexOf("ergebnis:") !== 0) zeichneAblage(null);
    document.title = kat ? kat.name + " finden – Kaufberatung" : "Finden & Vergleichen – Kaufberatung";
    if (schluessel !== letzterSchirm) schirm.classList.add("neu");
    if (schluessel !== letzterSchirm) {
      const t = findeTitel(schirm);
      if (letzterSchirm && t) { t.focus(); try { window.scrollTo(0, 0); } catch (e) { /* ohne Fenster */ } }
      letzterSchirm = schluessel;
    } else if (fokus) {
      const f = findeFokus(schirm, fokus);
      if (f && f.focus) { fokusFreilegen(f); f.focus(); }
    }
  }
  function findeTitel(k) {
    if (k.tagName === "H1") return k;
    for (const c of Array.from(k.childNodes || [])) { const t = c.nodeType === 1 ? findeTitel(c) : null; if (t) return t; }
    return null;
  }

  function fusszeile() {
    if (!fuss) return;
    leeren(fuss);
    const preisStaende = [];
    for (const k of daten.kategorien) for (const m of k.modelle) if (m.preis && m.preis.stand) preisStaende.push(m.preis.stand);
    preisStaende.sort();
    const teile = [];
    if (daten.stand) teile.push("Datenblätter: Stand " + datum(daten.stand));
    if (preisStaende.length) teile.push("Preise: " + (preisStaende[0] === preisStaende[preisStaende.length - 1] ? "Stand " + datum(preisStaende[0]) : "Stand " + datum(preisStaende[0]) + " bis " + datum(preisStaende[preisStaende.length - 1])));
    fuss.textContent = teile.join(". ") + (teile.length ? "." : "");
  }

  function zeigeFehler(text) {
    leeren(wurzel);
    wurzel.removeAttribute("aria-busy");
    wurzel.appendChild(h("section", { class: "schirm" }, [
      titel("Die Produktdaten fehlen gerade"),
      h("div", { class: "karte leise", role: "alert" }, [
        h("p", null, [text]),
        h("button", { type: "button", class: "knopf haupt", on: { click: () => location.reload() } }, ["Neu laden"]),
        h("a", { href: "ratgeber.html", class: "knopf neben" }, ["Zum Ratgeber"]),
      ]),
    ]));
  }

  async function laden() {
    let roh;
    try {
      const r = await fetch("finder-daten.json", { cache: "no-cache" });
      if (!r.ok) throw new Error("HTTP " + r.status);
      roh = await r.json();
    } catch (e) {
      zeigeFehler("Die Seite konnte die Modellliste nicht laden. Prüfe die Internetverbindung und lade neu. Wenn du die App schon einmal geöffnet hattest, klappt es danach auch ohne Netz.");
      return;
    }
    try { daten = B.datenPruefen(roh); } catch (e) {
      zeigeFehler("Die Modellliste ist beschädigt und kann nicht angezeigt werden. Lade die Seite später neu.");
      return;
    }
    try {
      const r = await fetch("finder-preise.json", { cache: "no-cache" });
      if (r.ok) B.preiseUeberlagern(daten, await r.json());
    } catch (e) { /* optional: ohne aktuelle Preise gelten die Preise aus finder-daten.json */ }
    wurzel.removeAttribute("aria-busy");
    fusszeile();
    zustand = ausAdresse();
    zeichne();
    // G1-R2-02: Bewegungsreduktion bei offener Seite eingeschaltet → laufende Gleitbewegung sofort beenden
    try {
      const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
      const wechsel = e => { if (e && e.matches) gleitenStoppen(); };
      if (mq && mq.addEventListener) mq.addEventListener("change", wechsel);
      else if (mq && mq.addListener) mq.addListener(wechsel);
    } catch (e) { /* ohne matchMedia */ }
    window.addEventListener("popstate", () => { zustand = ausAdresse(); zeichne(); });
    window.addEventListener("hashchange", () => { const z = ausAdresse(); if (alsAdresse(z) !== alsAdresse(zustand)) { zustand = z; zeichne(); } });
  }

  if (!B || !wurzel) return;
  laden();
})();
