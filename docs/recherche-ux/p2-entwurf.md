# P2 Notenmodell – Architekturentwurf (P2a Daten und Rechnung, Schnittstelle für P2b)

Stand: 24.11.2026 · Lead: Claude · Grundlage: `p2-plan.md`, D12, D13, D25 (`docs/entscheidungen.md`).
Status: **Entwurf zur Architekturprüfung (Codex high), nach r1 nachgezogen** (Befunde P2-01…P2-11, `docs/pruefungen/2026-11-24-p2-architektur/bewertung-r1.md`; Auflösung in §9, sie geht älteren Aussagen in §2–§8 vor). Nichts davon ist gebaut. Zeilenangaben beziehen sich auf den Stand von Commit `33fa490`. Seit Finder G1 (bis `0996e86`, D26) liegen die Stellen in `bewertung.js` ab `gewichte` um 4–5 Zeilen tiefer (z. B. `gewichte` 46, `bewerteModell` 121, `auswerten` 263, `datenPruefen` 423); geändert hat G1 dort nur `gewichte` (dritter Parameter `prio`) und `auswerten` (`prioritaeten`). Abstimmung mit G1: §8.

## 1. Ist-Stand (belegt)

**Gewichte und Antwortfaktoren.** `gewichte(kat, antworten)` (`app/finder/bewertung.js:43–63`) multipliziert die Faktoren aller gewählten Antworten (`antworten[].gewichte`, Z. 49–51), Faktor 0 schaltet ab, Felder mit `gewicht` ≤ 0 bleiben draußen (Z. 56), der Rest wird auf Summe 100 normiert (Z. 61). Die Seite übergibt `antwortenWirksam(kat)`: gewählte Antwort, sonst „egal“, falls vorhanden (`finder.js:208–215`), Aufruf in `fuelleErgebnis` (`finder.js:424`). Faktoren sind im Client auf 0..100 begrenzt (`bewertung.js:413`). Eine Version der Gewichte gibt es nicht: Eine Kategorie hat nur `id`, `name`, `felder`, `fragen` (`daten/schema/kategorien.json:77–80`, `:157–160`). `schema_version` ist 1 (`kategorien.json:2`) und wird von keinem Code gelesen (Suche über `werkzeuge/`, `app/`, `tests/`: nur Treffer in der JSON-Datei selbst).

**Note.** `bewerteModell` (`bewertung.js:117–149`) bildet R = Σ(g·t)/Σg über belegte Felder, Abdeckung = Σg(belegt)/Σg (Z. 132–133). Nicht anwendbare Felder entfallen (Z. 124), die Regel steht fest im Code (`NICHT_ANWENDBAR`, Z. 31–33), nicht im Schema. `datenblattNote` (Z. 107–112): `anker + (R − anker)·faktor − abzug − (1 − abdeckung)·20`, unter `abdeckung_mindest` `null`, begrenzt auf 0..100; Werte 50 / 0,85 / 3 / 0,7 (`kategorien.json:19–29`). Angezeigt wird `Math.round(note)` (`bewertung.js:154`), Rang nach angezeigter Zahl, bei Gleichstand das günstigere (Z. 156–164). Der Aufpreis-Hinweis wählt mit **ungerundeten** Noten (ΔN, Schwelle und Effizienz, Z. 207–212). Erst der Text nennt ΔN aus angezeigten Zahlen (Z. 216; korrigiert nach r1, P2-11).

**beitraege / fehlend.** `beitraege = [{feld, gewicht, teilpunkte, beitrag}]` nach Beitrag absteigend, `fehlend = [{feld, gewicht}]` nach Gewicht absteigend (Z. 122–131, 146–148). `gewicht` ist das normierte Gewicht aus `gewichte()`; bei nicht anwendbaren Feldern ergeben `beitraege` + `fehlend` zusammen weniger als 100. `beitrag` ist das Produkt `g · t` (Z. 128–132). Ein Anteil an R wird daraus erst nach Teilen durch Σ g der belegten Felder, an der Note ist es nie einer (korrigiert nach r1, P2-11). Heute zeigt die Karte nur `staerken()` (Teilpunkte ≥ 60, höchstens 3; `bewertung.js:321–323`) als „Stärken laut Datenblatt“ (`finder.js:552`, `:565`).

**tests[].** Getestet wäre ein Modell nur mit `tests[].punkte` (`bewertung.js:135–139`). Diese Stelle ist dreifach gesperrt: `datenbank.py` lehnt andere Testschlüssel als `url`, `titel` ab (`werkzeuge/datenbank.py:27`, `:230–232`), `testlinks()` gibt nur diese beiden aus (`:132–136`), `datenPruefen` filtert ebenfalls auf `{url, titel}` (`bewertung.js:438–439`). Bleibt so (D13).

**Maßfelder heute** (alle `typ: "zahl"`, `einheit: "cm"`):

| Kategorie | Feld | Gewicht | Beleg |
|---|---|---|---|
| Saugroboter | `hoehe_cm` „Bauhöhe“ | 6 (Bewertungsfeld, Kurve 7→100 … 12→20) | `kategorien.json:170` |
| Soundbar | `breite_cm` | 0, Filter über Antworten `hoechst` | `:449`, `:466–467` |
| Kühlschrank | `hoehe_cm` | 0 | `:561` |
| Geschirrspüler | `breite_cm` | 0, Filter über `hoechst`/`mindest` | `:600`, `:609–610` |

Korrektur zum Plan (`p2-plan.md:15`): Der Fernseher hat **kein** `breite_cm`, nur `diagonale_zoll` (`kategorien.json:91`). `tiefe_cm` gibt es nirgends. Die Namen sind also schon einheitlich. Es fehlen nur Felder und eine Regel.

**Prüfung und Bau.** `datenbank.py` prüft das Schema selbst nicht: `lade_schema()` lädt es nur (`:39–41`). Geprüft werden die Produktdateien (`pruefe_datei`, `:155–283`), eine Maßzahl nur über den Typ (`feld_ok`, `:59`: Zahl, kein bool, |x| < 1e7; **negative Werte gehen durch**). `bauen()` übernimmt je Kategorie nur `id`, `name`, `felder` (5 Schlüssel), `fragen`, `modelle` (`:316–317`). Je Modell gehen `werte`, `teilpunkte`, `preis`, `tests`, `ean` hinaus, **keine `belege` und keine `quellen`** (`:324–327`). Damit fehlen der App heute die Daten für Ebene 3 („Wert mit Quelle und Datum“).

**Auslieferung.** Ein Push auf `main`, der `daten/schema/**` oder `werkzeuge/datenbank.py` ändert, baut `finder-daten.json` und veröffentlicht sie ohne neue App-Fassung (`.github/workflows/finder-daten.yml:1–19`). Die App lädt die Datei netz-zuerst. Der Service Worker prüft sie mit `datenPruefen` aus der `bewertung.js`, die er beim Installieren über `importScripts("bewertung.js?v=" + VERSION)` geladen hat (`app/sw.js:14`, `:42–45`). Die Seite nutzt die Kopie aus dem App-Cache (Vorladen `:16–17`). Beide gehören zur Fassung des aktiven Workers (korrigiert nach r1, P2-11). Bei ungültigen Daten liefert der Worker die letzte gültige Cachekopie, ohne Kopie 503 (`:57–62`). Die Herkunftsprüfung vergleicht nur Commits, nicht den Inhalt (`werkzeuge/herkunft.py:1–7`). Die Datenpflege-Routine darf `kategorien.json` nicht ändern (`tests/test_entdeckung.py:263–267`).

## 2. Schemaänderung P2a

`schema_version`: **1 → 2**. Ab P2a prüft `datenbank.py` den Wert, damit eine alte Schemadatei nicht still gebaut wird. In `finder-daten.json` steht er nicht: Der Client erkennt neue Felder an ihrem Vorhandensein.

### 2.1 Gewichtsfassung je Kategorie (Pflicht)

```json
{"id": "saugroboter", "name": "Saugroboter",
 "gewichte_version": {"nummer": 1, "stand": "2026-11-24", "pruefsumme": "3f9a0c1b7d2e4a58"},
 "felder": [ … ], "fragen": [ … ]}
```

- `nummer`: ganze Zahl ≥ 1. Fassung 1 = heutige Werte (D25). `stand` = Tag der fachlichen Freigabe durch den Besitzer (Plan Schritt 3), JJJJ-MM-TT.
- **Nach r1 ersetzt durch §9.3** (Referenzvergleich statt gespeicherter Prüfsumme, P2-04). Ursprünglicher Vorschlag:
- `pruefsumme`: die ersten 16 Hex-Zeichen von SHA-256 über die kanonische JSON-Form (`sort_keys`, kompakt, UTF-8) von allem, was die Zahl bestimmt: je Feld `id, typ, gewicht, kurve`; je Antwort `gewichte`; aus `datenblatt_abschlag` die Werte `anker, faktor, abzug, abdeckung_mindest`. `mindest`/`hoechst` gehören nicht dazu (sie filtern, sie ändern keine Note). `datenbank.py` rechnet nach. Passt die Summe nicht, meldet es den Fehler „Gewichte geändert: Fassung erhöhen und Prüfsumme neu setzen“. So kann keine Gewichtsänderung ohne neue Fassung durchrutschen. Ein Hilfsbefehl gibt die Summe aus: `python -I werkzeuge/datenbank.py fassung <kategorie>`.
- Lücke: `NICHT_ANWENDBAR` (`bewertung.js:31–33`) liegt im Code und geht nicht in die Summe ein. Eine Änderung dort braucht eine Fassung von Hand (Prüffrage P-5).
- Bau: Hinaus gehen nur `{"nummer", "stand"}`, die Prüfsumme bleibt im Schema.

### 2.2 Testquelle je Kategorie (optional, höchstens eine)

```json
"testquelle": {"name": "Beispieltester", "url": "https://example.org/test/saugroboter",
               "methodik_url": "https://example.org/so-testen-wir", "stand": "2026-11-24"}
```

- Ein Objekt, keine Liste. Fehlt der Schlüssel, gibt es keine Primärquelle. P2a trägt **keine** Quelle ein, die Auswahl entscheidet der Besitzer (F-3).
- Genau die vier Schlüssel. Jeder weitere (`punkte`, `note`, `urteil` …) ist ein Fehler, wie bei `tests` (F-01). `name` 1–80 Zeichen; `url` und `methodik_url` über `kanon_host` (nur https, ohne Userinfo und Port, `datenbank.py:105–115`); `stand` über `ist_datum` (`:44–50`, 2020 bis heute).
- „Zweite Testquelle“ wird an drei Stellen abgefangen: als Liste (Typfehler), unter einem Tippnamen wie `testquellen` (neue Positivliste der Kategorieschlüssel: `id, name, felder, fragen, gewichte_version, testquelle`) und als doppelter Schlüssel im selben Objekt. Den doppelten Schlüssel nimmt Pythons `json.loads` heute still mit dem letzten Wert an. Neu ist deshalb `lade_schema()` mit `object_pairs_hook`, der bei doppelten Schlüsseln einen Fehler meldet.

### 2.3 Maße B/H/T (Regel jetzt, Felder und Werte mit Beleg in P6)

```json
{"id": "tiefe_cm", "name": "Tiefe", "einheit": "cm", "typ": "zahl", "kurve": {"art": "linear", "punkte": [[0, 0], [250, 0]]}, "gewicht": 0}
```

- Feste Namen `breite_cm`, `hoehe_cm`, `tiefe_cm`. Kommt einer davon vor, muss er `typ "zahl"` und `einheit "cm"` haben. Die Namensregel gegen `breite_mm` oder `hoehe` steht nach r1 in §9.7 (P2-09); die frühere Regel „anderes Feld mit Endung `_cm`“ fing diese Fälle nicht.
- Produktwerte dieser Felder: 0 < x ≤ 500. Die Obergrenze ist eine Plausibilitätsschranke (Vorschlag), kein Fachwert. Heute ist nur der Text schon rot (`feld_ok`, `:59`); negativ, 0 und unplausibel groß sind neu.
- Die vier vorhandenen Felder erfüllen die Regel schon. `hoehe_cm` beim Saugroboter bleibt Bewertungsfeld (Gewicht 6), denn eine Änderung würde Noten verschieben.
- **Vorschlag A (empfohlen):** P2a legt **keine neuen** Maßfelder an. Grund: Der Vergleich zeigt jedes Schemafeld als Zeile (`finder.js:690–700`). Leere Felder wären also sichtbar, und ein Schema-Push geht sofort live (§1). P6 legt das Feld je Kategorie zusammen mit den ersten belegten Werten an. **Vorschlag B:** Alle Felder sofort anlegen, `bauen()` lässt aber ein Feld mit Gewicht 0 weg, solange kein Modell der Kategorie einen Wert hat und keine Frage darauf verweist. Das ist mehr Regel für wenig Nutzen (F-2).

### 2.4 Quellen und Belege in `finder-daten.json` (Ergänzung zum Plan, für Ebene 3)

Je Kategorie `"quellen": {"<id>": {"titel", "url", "gelesen"}}` (nur Quellen, auf die verwiesen wird), je Modell `"belege": {"<feld>": "<quellen-id>"}`. Wert und Beleg kommen je Feld aus derselben Ebene (Modell oder Variante), nicht getrennt wie `werte` in `datenbank.py:321` (nach r1, §9.4, P2-05). Gemessen am heutigen Bestand: 465 Quellen mit rund 100 kB kompaktem JSON und 3 775 Belegverweise. Die heutige Datei hat 330 436 Bytes (lokaler Bau, 14 Dateien, 418 Varianten). Die Datei wächst also deutlich (F-4). Quell-URLs prüft der Bau neu mit `kanon_host`, bisher nur mit `startswith("https://")` (`:180`).

### 2.5 Abwärtsverträglichkeit

- **Alte App, neue Daten** (der Normalfall, §1): Alle Felder kommen zusätzlich dazu. Das alte `datenPruefen` prüft nur bekannte Schlüssel und lässt unbekannte stehen (`bewertung.js:424–440`), `feldPruefen` ebenso (`:401–406`). Nachweis beim Bau: `datenPruefen` aus `git show 33fa490:app/finder/bewertung.js` auf die neue `finder-daten.json` anwenden, Erwartung: kein Wurf, gleiche Noten.
- **Neue App, alte Daten** (Cache, offline): Alle neuen Felder sind im Client optional. Fehlt eins, gilt `fassung: null` bzw. „keine Testquelle“ bzw. „keine Quellenangabe“, und es gibt keinen Wurf. Sonst würde der Service Worker eine ältere gültige Datei als ungültig behandeln.
- `herkunft` und `herkunft.py` bleiben unverändert.

### 2.6 Prüfregeln im Client (`datenPruefen`, fremde Daten)

Geworfen wird wie bisher nur bei dem, was Navigation und Rechnung brauchen (`:370–373`). Die neuen Felder dienen nur der Anzeige, also **still verwerfen statt werfen**:
- `gewichte_version`: Objekt mit `nummer` als ganzer Zahl 1..9999 und `stand` nach `DATUM` (`:26`), sonst `null`. Hinaus geht nur `{nummer, stand}`.
- `testquelle`: `istName(name, 80)`, beide URLs über `sichereUrl` (`:339–342`), `stand` nach `DATUM`, sonst `null`; neu aufgebaut aus genau vier Schlüsseln.
- `quellen`: Schlüssel `kennungOk`, `titel` `istName(…, 200)`, `url` `sichereUrl`, `gelesen` `DATUM`, sonst wird die Quelle entfernt. `belege`: nur Einträge, deren Quelle bleibt und deren Feld einen Wert hat.
- Maßwerte ≤ 0 in `m.werte` werden entfernt, wie kaputte Teilpunkte (`:436`).
- Ausgabe nur als Text (`textContent`, Seitenregel `finder.js:3`). Links baut nur P2b, über das vorhandene `link()`.

## 3. Rechenregel „Note bei anderer Antwort“

```js
/* alternativen(kat, regeln, modell, antworten, max = 3) -> [{frage, frage_text, antwort, antwort_text,
     note, anzeige, art, abdeckung, delta, passt}] */
```

- **Eingabe:** die Kategorie aus `datenPruefen`, `daten.regeln`, ein Modell und dieselben wirksamen Antworten wie in `auswerten` (`antwortenWirksam`).
- **Kandidaten:** Für jede Frage mit mindestens zwei Antworten gilt jede Antwort außer der aktuellen. Es ändert sich immer genau **eine** Antwort, nie zwei zugleich (keine Kombinationen, die Zahl bleibt bei Σ(Antworten − 1)). Maßgeblich sind die **wirksamen** Antworten: Eine unbeantwortete Frage mit Antwort `egal` steht auf `egal` (dann ist `egal` die aktuelle Antwort). Nur eine Frage ohne wirksame Antwort liefert alle ihre Antworten als Kandidaten (präzisiert nach r1, P2-02).
- **Rechnung:** `gew' = gewichte(kat, {...antworten, [frage]: aid})`, `b = bewerteModell(modell, kat, gew', regeln)`. Das sind dieselben Funktionen wie für die Hauptnote, also bleibt die Rechnung gleich (Abschlag, 70 %-Schwelle, `nicht_anwendbar`, später auch die Mischung für getestete Modelle).
- **Rundung und Gleichstand wie P1:** `anzeige = Math.round(note)` (wie `:154`), `delta = anzeige' − anzeige` aus angezeigten Zahlen (wie `:216`). Ein Kandidat zählt nur, wenn sich die **angezeigte** Zahl oder der Zustand ändert (Note ↔ keine Note, `art`). Gleiche angezeigte Zahl heißt also keine Zeile, sonst entstünde ein „66 statt 66“ (07 B03).
- **Begrenzung:** höchstens `max` (3) Einträge. Sortiert nach |delta| absteigend, Übergänge zu oder von „keine Note“ zuerst. Bei Gleichstand gilt die Reihenfolge der Fragen in `kat.fragen`, dann die der Antworten. Die Reihenfolge ist damit fest und testbar.
- **`passt`:** `anforderungen(kat, antworten', {})` plus `pruefe` (`:68–103`) ergibt `"ok" | "nein" | "unbelegt"`. Würde das Modell unter Y eine Mindestanforderung verletzen, sagt die Ansicht das dazu. Es kommt keine Aussage über den Rang („wäre Platz 2“): Der Rang hängt von allen anderen Modellen, vom Budget und von den Filtern ab.
- **Keine neue Aussage:** Die Funktion liest nur `modell.teilpunkte`, `modell.werte` (für `nicht_anwendbar`), `kat.felder`, `kat.fragen` und die Regeln, also dieselben Datenblattwerte wie die Hauptnote. Sie ändert nichts an ihren Eingaben. Das Testorakel steht nach r1 in §9.2: `auswerten` direkt verliert Zeilen mit `passt "nein"`, weil `rang` nur passende Modelle enthält (P2-02).

## 4. Datenfluss und Schnittstelle für P2b

`kategorien.json` + `daten/produkte/*.json` → `datenbank.py pruefen` (Schranke, neu mit Schema) → `bauen()` (mit `gewichte_version`, `testquelle`, `quellen`, `belege`) → `finder-daten.json` → `datenPruefen` (Seite und SW) → `auswerten()` (neu: `fassung` im Ergebnis) → P2b-Ansicht.

Reine Funktionen in `bewertung.js` (kein DOM, Node-testbar; P2b baut nur die Ansicht):

```js
notenblatt(kat, regeln, eintrag, antworten) -> {
  note, anzeige, art, abdeckung, spanne, R,
  fassung,                                   // {nummer, stand} | null
  merkmale: [{feld, name, einheit, wert, teilpunkte, anteil, beitrag_r,  // anteil = Gewicht in % über alle zählenden Felder (Summe 100)
              beleg: {titel, url, gelesen} | null}],                     // Ebene 3
  fehlend: [{feld, name, anteil}], nicht_anwendbar: [feld],
  alternativen: alternativen(kat, regeln, eintrag.modell, antworten),
  testquelle,                                // | null (Link, D13)
  tests                                      // eintrag.modell.tests (Links)
}
methodik(daten) -> {abschlag: {anker, faktor, abzug, abdeckung_mindest, spanne_plus_minus},
                    kategorien: [{id, name, fassung, testquelle, grundgewichte: [{feld, name, anteil}]}]}
```

- Nenner und Zeilenaufbau sind nach r1 in §9.5 festgelegt (P2-06). Ursprünglich: `anteil` wird über `beitraege + fehlend` neu normiert, damit die Balken auch bei `nicht_anwendbar` 100 ergeben. `beitrag_r` ist ausdrücklich ein Anteil an R und nicht „Punkte der Note“. Die Note ist eine affine Umrechnung von R (§1), Anker und Abzug lassen sich nicht auf Merkmale verteilen. Die Ansicht beschriftet Balken deshalb als „Teilpunkte“ mit „zählt x %“.
- `wert` ist der Rohwert für `wertText` der Ansicht, `name`/`einheit` stammen aus `kat.felder`.
- P0 legt laut Konzept §4 `notenblatt(m)` als Platzhalter an. P2b ruft dort `KBBewertung.notenblatt(…)` auf. Router-Ziel `s=methodik` (heute `SCHRITTE`, `finder.js:9`, `:168`): Den Platzhalter legt P0 an (Konzept §4). Inhalt, Menüeintrag und das Entfernen von „Wie wir bewerten“ im Fuß (`app/finder/index.html:29–35`) gehören zu P2b, nach P0 (Übergabe §9.8, P2-10).

## 5. Dateihoheit

- **P2a ändert:** `daten/schema/kategorien.json`, `werkzeuge/datenbank.py`, `app/finder/bewertung.js`, `docs/punkteschema.md`, `daten/produkte/FORMAT.md` (Maßregel, Hinweis auf Belege im Bau), `tests/test_bewertung.mjs`, `tests/test_datenbank.py`; nach r1 auch `.github/workflows/finder-daten.yml` (Referenz für §9.3).
- **P2a ändert nicht:** `finder.js`, `finder.css`, `index.html`, `ansichten/*`, `app_bauen.py`, `tests/test_finder_*.mjs` (alles P0) sowie `sw.js`. Auch `tests/vorlagen/finder-beispiel.json` bleibt unberührt, weil `test_finder_dom.mjs` und `test_sw_daten.mjs` sie lesen. P2a nutzt eigene Testdaten in den Testdateien. `bewertung.js` steht nicht in der P0-Zeile (Konzept §4), damit gibt es keine Überschneidung.
- **P6:** Nur P6 trägt Maßwerte mit Beleg in `daten/produkte/*.json` ein und legt bei Vorschlag A die Maßfelder in `kategorien.json` an. Das ist ein Schemaeingriff von Hand, nicht durch die Routine (§1). Jedes neue Feld ändert die Prüfsumme, auch mit Gewicht 0 (es gehen `id, typ, gewicht, kurve` ein), und braucht damit eine neue Fassung. Prüffrage P-3: Filterfelder aus der Summe nehmen?

## 6. Testliste (rot vor der Änderung, grün danach; „schon rot“ = Regressionsschutz)

Nach r1 geändert: 6, 13, 15, 21, 22, 34, 36, 37; neu 38–46 (§9.9).

**`test_datenbank.py` (Schema und Bau):** 1 echtes Schema und echte Daten haben 0 Fehler (bestehender Test `test_echte_daten_ohne_fehler` bleibt) · 2 `schema_version` 1 ist ein Fehler · 3 Kategorie ohne `gewichte_version` · 4 `nummer` 0 / "1" / 1.5 · 5 `stand` "24.11.2026" und ein Datum in der Zukunft · 6 Gewicht eines Felds um 1 geändert, Fassung gleich → Prüfsumme rot; Faktor einer Antwort geändert → rot; Kurvenpunkt geändert → rot; nur `mindest` geändert → **grün** (Gegenprobe) · 7 `testquelle` als Liste · 8 doppelter Schlüssel `testquelle` im selben Objekt · 9 Tippname `testquellen` · 10 `testquelle.url` mit `http://`, `methodik_url` mit Userinfo bzw. Port · 11 `testquelle` mit `punkte` · 12 `name` leer bzw. 81 Zeichen · 13 Maßfeld `breite_cm` mit `einheit "mm"` bzw. `typ "stufe"` rot; Feld `hoehe_innen_cm` (Endung `_cm`, nicht in der Liste) rot · 14 Produktwert `breite_cm` −5, 0, 501 rot; 60 grün; "60" (schon rot, `:59`) · 15 Bau: `gewichte_version` ohne `pruefsumme`, `testquelle` mit genau vier Schlüsseln, `quellen` nur mit Verweis, `belege` der Variante überschreiben die des Modells · 16 Quell-URL mit Userinfo im Bau rot.

**`test_bewertung.mjs`:** 17 `datenPruefen` mit Daten ohne neue Felder: kein Wurf, `fassung null` (Abwärtsverträglichkeit) · 18 `gewichte_version` kaputt (`nummer` −1, `stand` Text) → `null`, kein Wurf · 19 `testquelle` mit `javascript:`- bzw. `http:`-URL → `null`; mit `punkte` → nur vier Schlüssel · 20 Quelle mit kaputter URL wird entfernt, ein Beleg darauf auch; Beleg auf ein Feld ohne Wert wird entfernt · 21 Maßwert −3 in `werte` wird entfernt · 22 `alternativen`: jede Zeile = `auswerten` mit Y (Oracle) · 23 Faktor ändert die Note nur um 0,3 (gleiche angezeigte Zahl) → keine Zeile (Gegenbeispiel) · 24 Alternative fällt unter 70 % → Zeile mit `note null`, `art "zu_wenig_daten"`, vor Zeilen mit Zahl · 25 Alternative schaltet alle Felder auf 0 → `art "keine_merkmale"` · 26 höchstens 3 Zeilen, feste Reihenfolge bei gleichem |delta| · 27 aktuelle Antwort nie als Alternative; Frage mit einer Antwort ergibt keine Zeile; Kategorie ohne Fragen → `[]` · 28 Alternative mit verletzter `mindest`-Anforderung → `passt "nein"` · 29 `modell` und `antworten` bleiben unverändert (tiefer Vergleich vorher und nachher) · 30 `notenblatt`: Summe aller `anteil` = 100 auch mit `nicht_anwendbar` (Air Fryer mit einem Korb, `:32`); `fehlend` nach Anteil absteigend; `beleg` `null` ohne Quelle · 31 `methodik(daten)` übernimmt die Abschlagswerte aus den Regeln, nicht aus Konstanten · 32 `auswerten().fassung` = Fassung der Kategorie.

**Manuell beim Bau:** alte `bewertung.js` (Commit `33fa490`) gegen die neue `finder-daten.json` (§2.5) · `python -I werkzeuge/datenbank.py pruefen` 0 Fehler · `powershell -File tests/alle-tests.ps1` grün · Größe vor und nach dem Bau notieren.

## 7. Risiken, offene Fragen, Prüffragen

**Risiken.** (R1) Ein Schema-Push veröffentlicht die Daten sofort (§1). Fehler in P2a gehen also ohne App-Freigabe live. Deshalb gilt: alles nur ergänzen, Nachweis mit der alten `bewertung.js`, Push erst nach bestandener Prüfung (AGENTS.md). (R2) Die Datei wächst durch Quellen und Belege (§2.4) und wird auf dem Handy langsamer. (R3) Die Prüfsumme macht jede Gewichtsänderung zum Pflichtschritt. Das ist so gewollt, kostet aber bei P6 eine Fassung je Gewichtsänderung. (R4) „Bei Nutzung Y wäre es Z“ kann wie eine Empfehlung wirken, deshalb gibt es keine Rangaussage (§3), den Wortlaut legt P2b fest. (R5) `sichereUrl` lässt Userinfo durch (`:341`). Schranke ist `datenbank.py`.

**Offene Fragen an den Besitzer.**
- **F-1 Gewichtstabelle zur Freigabe:** Vorschlag: Der Lead erzeugt je Kategorie eine Markdown-Tabelle aus dem Schema (Skript, kein Abtippen) in `docs/recherche-ux/p2-gewichte-fassung1.md`. Spalten: Merkmal · Grundgewicht · Anteil in % ohne Antworten · Faktoren je Antwort (Frage → Antwort → Faktor) · Spalte „Änderung (Besitzer)“. Die Freigabe setzt `stand` der Fassung 1. Vorschläge des Leads stehen getrennt („offensichtliche Lücke: …“).
- **F-2 Maße:** Vorschlag A (Regel jetzt, Felder mit P6) oder B (§2.3)? Und welche Kategorien bekommen B/H/T? Das ist fachlich offen. Naheliegend wären Großgeräte, Fernseher, Soundbar, Saugroboter und Air Fryer; bei Smartphone, Tablet, Laptop und Kopfhörern ist der Nutzen ungeklärt.
- **F-3 Testquelle:** Welche Primärquelle je Kategorie, nur als Link (D13)? P2a lässt alle leer.
- **F-4 Quellen in der App-Datei:** in `finder-daten.json` (einfach, Datei größer) oder in einer eigenen Datei, die erst bei Ebene 3 geladen wird (braucht einen `sw.js`-Eintrag, also nach P0)?
- **F-5 Umfang der Fassung:** sollen Kurven und Abschlagswerte in die Prüfsumme (Vorschlag: ja, „alles, was die Zahl bestimmt“)?

**Prüffragen für Codex (Architekturprüfung, high).**
- P-1 Ist §2.5 vollständig? Nimmt das alte `datenPruefen` (`bewertung.js:418–443`) jede neue Struktur an, auch `quellen` mit Schlüsseln aus fremden Daten (Prototyp-Namen, R3-02)?
- P-2 Sind Prüfsumme und kanonische Form in Python und JSON eindeutig, etwa Zahl 1 gegen 1.0, Reihenfolge der Kurvenpunkte, Unicode in Namen?
- P-3 Gehören Filterfelder mit Gewicht 0 in die Prüfsumme?
- P-4 Ist die Auswahl in `alternativen` (eine Antwort, angezeigte Zahl, höchstens 3, feste Reihenfolge) widerspruchsfrei zu Rang und Hinweisen aus P1 (`:154–216`)? Fehlt ein Fall, etwa „egal“ als Vorgabe ohne gewählte Antwort?
- P-5 Muss `NICHT_ANWENDBAR` ins Schema, damit die Fassung die Zahl vollständig festlegt?
- P-6 Reicht stilles Verwerfen im Client für `gewichte_version`/`testquelle`, oder muss eine kaputte Fassung die Datei ungültig machen?
- P-7 Überschneidet sich §5 mit P0 oder P6, etwa über `tests/vorlagen/` oder den Router?
- P-8 Ist `anteil`/`beitrag_r` in §4 eine ehrliche Grundlage für Balken, oder legt sie eine Aufteilung der Note nahe, die es nicht gibt?

## 8. Abstimmung mit G1 (Lead, 24.11.2026, Stand `0996e86`)

G1 (D26) hat Teile von P2b vorweggenommen. Belegt am Code:
- **Prioritäten-Regler.** `gewichte(kat, antworten, prio)` multipliziert jedes bewertete Feld (Gewicht > 0) zusätzlich mit `prio[feld]`. Gültig sind Zahl und Wert ≥ 0, sonst gilt 1 (`bewertung.js:41–67`). Die Faktoren `PRIO_FAKTOREN = [0, 0.5, 1, 2, 3]` stehen im Code (`:45`). `auswerten` reicht `eingabe.prioritaeten` durch (`:261–266`).
- **Adresse.** `p=feld.stufe~…` speichert die **Stufe** 0–4, nicht den Faktor. Übernommen wird nur ein Feld der Kategorie mit Gewicht > 0 und einer Stufe ungleich „normal“ (`finder.js:189–197`, `prioFaktoren` `:213–217`).
- **„Woher die Punkte kommen“.** `punkteHerkunft` (`finder.js:733–757`) zeigt `beitraege` und `fehlend` nach `gewicht` absteigend, also im Kern `notenblatt().merkmale` aus §4. Ein fehlender Wert gilt dort nicht als 0 Teilpunkte (G1-02).

Daraus folgen die Brüche und ihre Auflösung. Wo „Vorschlag“ steht, entscheidet die Architekturprüfung:

| Nr. | Bruch im Entwurf | Auflösung (Vorschlag) |
|---|---|---|
| A-1 | §3 rechnet `gewichte(kat, {...antworten, [frage]: aid})` **ohne** `prio`. Mit verstellten Reglern passt die Alternativzeile dann nicht zur angezeigten Hauptnote. Ein „66 statt 66“ wäre möglich, ebenso ein falsches Vorzeichen bei `delta`. | `alternativen(kat, regeln, modell, antworten, prio, max = 3)` rechnet mit derselben `prio` wie die Hauptnote. Testorakel 22 lautet dann `auswerten(kat, regeln, {antworten: antworten', prioritaeten: prio})`. Neuer Test: Mit gesetzten Reglern stimmt jede Zeile mit dem Orakel überein; ohne `prio` im Aufruf würde der Test rot. |
| A-2 | §4 `notenblatt(kat, regeln, eintrag, antworten)` kennt keine Prioritäten. `anteil` hätte dann nur Grund- und Antwortgewicht (ohne `prio` wirken die Antwortfaktoren weiter, `bewertung.js:48–65`; korrigiert nach r1, P2-11), während die Karte nach G1 auch das Prioritätsgewicht zeigt. | `notenblatt(kat, regeln, eintrag, antworten, prio)`. `anteil` stammt aus denselben Gewichten wie die Note (Nenner §9.5). Neu ist `persoenlich: true`, sobald ein Faktor ≠ 1 wirkt. Die Ansicht schreibt dann „nach deinen Prioritäten“ zur Note. `methodik().grundgewichte` bleibt ohne `prio`. |
| A-3 | Die Fassung (§2.1) legt nur die Grundgewichte fest. Mit Reglern ist die angezeigte Note „Fassung N plus deine Stufen“, keine reine Fassungsnote. | `fassung` beschreibt weiter nur das Schema. **Nach r1 (P2-07):** Die Adresse öffnet die **aktuelle** Rechnung (aktuelle Daten, Gewichtsfassung und App-Fassung mit `PRIO_FAKTOREN` und `NICHT_ANWENDBAR`). Eine frühere Note stellt sie nicht wieder her. Die Projektion (§9.3) bekommt keine Regler (Nutzereingabe, keine Redaktionsgewichtung). |
| A-4 | Die `PRIO_FAKTOREN` stehen im Code, wie `NICHT_ANWENDBAR` (P-5), und gehen nicht in die Prüfsumme ein. Ändert man sie, ändert sich die Bedeutung jeder geteilten Adresse mit `p=`. | Die Faktoren bleiben im Code und gehören zur App-Fassung, nicht zur Gewichtsfassung. In `docs/punkteschema.md` wird das festgehalten: Eine Änderung braucht eine Entscheidung in `entscheidungen.md` und einen Test, der die fünf Werte festschreibt (heute nicht vorhanden, gehört zu P2a). Prüffrage P-9. |
| A-5 | Eine neue Fassung kann ein Feld streichen, umbenennen oder auf Gewicht 0 setzen. Alte Adressen verlieren den Eintrag `p=` dafür still (`finder.js:191–196`). Ein neues Feld steht auf „normal“. | Das ist annehmbar: Die Adresse bleibt gültig und die Note rechnet mit der neuen Fassung. Feld-IDs werden aber nicht umbenannt (Regel in `FORMAT.md`/`punkteschema.md`); bei einem neuen Merkmal kommt eine neue ID. Kein Fassungsbezug in der Adresse (keine neue Zustandsquelle). Prüffrage P-10. |
| A-6 | §2.5 belegt die Abwärtsverträglichkeit mit `bewertung.js` aus `33fa490`. Wenn P2a live geht, kann aber G1 (`0996e86`) oder die heutige Live-Fassung (`7339711`) im Cache des Service Workers liegen. | Belegt wird mit **jeder** `bewertung.js`, die beim P2a-Push im Umlauf sein kann. **Nach r1 (P2-01):** Die Liste wird aus dem gh-pages-Verlauf erhoben, nicht angenommen. Die Erwartung je Fassung lautet „Verhalten wie mit den heutigen Live-Daten“ (§9.1). |
| A-7 | §5: „P2a ändert `finder.js` nicht“. Das passt weiter: G1 hat `finder.js` vor P0 geändert (D26). P2b soll aber `punkteHerkunft` auf `notenblatt()` umstellen, statt eine zweite Merkmalsansicht zu bauen. | §5 gilt unverändert. Ergänzung zur P2b-Zeile: `punkteHerkunft` nutzt dann `notenblatt().merkmale` (gleiche Sortierung, „nicht angegeben“ wie G1-02). Gemeinsame Tests: `test_finder_dom.mjs` „G1-02“. |
| A-8 | `anteil` in §4 wird über `beitraege + fehlend` neu normiert. G1 zeigt `gewicht` **ohne** Neunormierung. Bei `nicht_anwendbar` (Air Fryer mit einem Korb) ergibt die Summe in G1 also weniger als 100 %. | Mit P2b wird das einheitlich: `punkteHerkunft` zeigt `anteil`. Bis dahin ist es eine bekannte Grenze von G1. Sie ist sichtbar nur beim Air Fryer mit `koerbe = 1`. |
| A-9 | ~~Stellt ein Nutzer alle Regler auf „aus“, kann eine Alternative nie eine Note haben.~~ **Nach r1 gestrichen (P2-03):** Ein Feld, das eine Antwort auf Faktor 0 setzt, hat keinen Regler (`finder.js:455–456`), behält aber `prio` 1 (`bewertung.js:60`). Eine andere Antwort macht es wieder wirksam (Air Fryer `beilage`, `kategorien.json:217–218`). | Keine Abkürzung über den Hauptnotenstatus. Jeder Kandidat wird mit unveränderter `prio` gerechnet. `[]` gibt es nur, wenn kein Kandidat eine andere angezeigte Zahl oder einen anderen Zustand ergibt. Test 36 (§9.9). |

**Neue Prüffragen.**
- P-9 Reicht eine Entscheidung plus Test als Schutz für `PRIO_FAKTOREN` (A-4)? Oder sollen die Faktoren ins Schema und damit in die Prüfsumme?
- P-10 Ist A-5 tragfähig, also kein Fassungsbezug in der Adresse und ein stiller Verlust des `p=`-Eintrags? Oder braucht die Seite einen Hinweis „Prioritäten aus älterer Fassung teilweise verworfen“?
- P-11 Decken A-1/A-2 alle Stellen ab, an denen eine Note ohne `prio` entstehen kann (Aufpreis-Hinweis, Vergleich, Rangliste)? Lead-Suche `grep -n "gewichte(\|auswerten(" app/finder/*.js` auf `0996e86`: Alle Aufrufe geben `prio` mit (`finder.js:496`, `:576`, `:910`, `bewertung.js:266`). Die einzige Ausnahme ist `reglerFelder` (`finder.js:455`). Sie ist gewollt, weil die Reglerreihenfolge beim Ziehen nicht springen soll.

**Tests dazu (ergänzen §6).** 33 `alternativen` mit `prio` gleich Orakel mit `prioritaeten` (Orakel nach §9.2) · 34 `notenblatt` mit `prio` (nach r1 erweitert, §9.9) · 35 `PRIO_FAKTOREN` festgeschrieben `[0, 0.5, 1, 2, 3]` · 36 und 37: nach r1 neu gefasst (§9.9).

## 9. Nachzug nach Codex r1 (24.11.2026)

Grundlage: `docs/pruefungen/2026-11-24-p2-architektur/bewertung-r1.md` (11 Befunde, alle bestätigt). Dieser Abschnitt geht älteren Aussagen in §2–§8 vor.

### 9.1 Abwärtsverträglichkeit: Fassungen erheben, Fassung 1 ohne Notenänderung (P2-01)

- **Welche Fassungen:** alle verschiedenen Blobs von `bewertung.js` im gh-pages-Verlauf zum Pushzeitpunkt (`git log --format=%h origin/gh-pages -- bewertung.js`, je Commit `git rev-parse <c>:bewertung.js`), dazu die neueste App-Fassung auf `main`. Heute sind das `b24c18f` (23.11.) und `420722b` (24.11., Blob gleich `33fa490`/`7339711`), dazu G1 `0996e86`.
- **Erwartung je Fassung:** `datenPruefen` und alle Noten verhalten sich auf der neuen `finder-daten.json` **wie auf den heutigen Live-Daten**. Bei G1 gilt das für alle wirksamen Vorgaben und mit `prioritaeten`. `b24c18f` wirft schon heute („klassen“, seit Datenpush `a7434dd`, D12). Für diese Fassung lautet die Erwartung „wirft weiter, der Worker behält seine Cachekopie“ (`sw.js:57–62`). Das ist ein Altzustand und kein P2a-Ziel. Ihn zu beheben (Regelfelder `klassen`/`kappung` wieder mitliefern) würde D12 berühren und gehört nicht hierher.
- **Fassung 1 ändert keine Note:** Der P2a-Push trägt nur `gewichte_version` Nummer 1 mit den heutigen Werten. Durchgesetzt wird das über §9.3 (Referenz ohne Fassung → Projektion muss gleich sein) und über Test 42 (alle Modelle, alle Vorgaben: gleiche Note vor und nach dem Bau). Fachlich freigegebene Gewichtsänderungen (F-1) kommen in einem eigenen Push mit Nummer 2 und eigener Prüfung ihrer sichtbaren Wirkung.

### 9.2 Orakel und Kandidaten für `alternativen` (P2-02)

- **Zahl:** Das Orakel für eine Zeile ist `auswerten(kat1, regeln, {antworten: antworten', prioritaeten: prio})`. `kat1` ist eine Kopie der Kategorie mit nur diesem Modell und ohne `mindest`/`hoechst` in allen Antworten. Damit fällt das Modell nicht aus `rang`. Gewichte und Rechnung bleiben gleich, weil `gewichte` nur `gewichte` der Antworten liest (`bewertung.js:48–55`).
- **`passt`:** wird getrennt geprüft, gegen `anforderungen(kat, antworten', {})` der unveränderten Kategorie. Es gilt nur für Frageanforderungen. Oberflächenfilter gehen nicht ein, solange `alternativen` keine Filter bekommt (Test 46).
- **Ohne Note:** `anzeige` ist `null`, wenn `note` `null` ist. `delta` ist `null`, wenn eine Seite keine Note hat; dann trägt `art` die Aussage.

### 9.3 Gewichtsfassung: Referenzvergleich statt gespeicherter Prüfsumme (P2-04, Prüffrage 3)

- **Schema:** `gewichte_version: {nummer, stand}`, ohne `pruefsumme`. Die Nummer pflegt man von Hand.
- **Projektion je Kategorie** (alles, was die Zahl bestimmt): Felder mit Gewicht > 0 als Abbildung `id → {typ, gewicht, kurve}` (Reihenfolge der Felder egal). Fragen in ihrer Reihenfolge, je Frage `id` und Antworten in ihrer Reihenfolge mit `id` und `gewichte`. Die IDs gehören dazu, weil die Vorgabe über die ID `egal` wirkt (`finder.js:233`) und die Reihenfolge den Gleichstand in §3 entscheidet. Dazu aus den Regeln `datenblatt_abschlag` (`anker, faktor, abzug, abdeckung_mindest`, ggf. `getestet.mischung`); eine Änderung dort betrifft alle Kategorien. `mindest`/`hoechst` und Filterfelder mit Gewicht 0 gehören nicht dazu (P-3: nein, sie ändern keine Note).
- **Prüfung** in `datenbank.py pruefen --gegen <rev>`: Die Projektion wird mit der Projektion des Schemas in `<rev>` verglichen, über Python-Gleichheit nach `json.loads`. Damit sind `1` und `1.0` gleich, und eine Kanonisierung entfällt (P-2). Regeln:
  - Ist die Projektion gleich, muss die Nummer gleich bleiben.
  - Weicht sie ab, muss die Nummer größer sein als in `<rev>`, und `stand` muss neu gesetzt sein.
  - Eine kleinere Nummer ist immer ein Fehler.
  - Hat `<rev>` noch keine `gewichte_version` (Schema 1), muss die Projektion gleich sein und die Nummer 1 lauten (§9.1).
- **Referenz:** In `finder-daten.yml` ist `<rev>` die `herkunft` der Online-Datei. Das ist die Freigabereferenz, die `herkunft.py` heute schon liest. Lokal ist `<rev>` `origin/main`. Ist die Referenz nicht erreichbar, bricht der Lauf ab.
- **Kosten:** Die volle Geschichte holt der Workflow schon (`finder-daten.yml:38`, `fetch-depth: 0`). Die Online-`herkunft` liest er aber erst nach dem Bau, beim gh-pages-Schritt (`:44` gegen `:64`). Er braucht deshalb einen Schritt vorher, der die Referenz liest und an `pruefen --gegen` gibt. `finder-daten.yml` kommt dafür in die Dateihoheit von P2a (§5 ergänzt). Den Hilfsbefehl `fassung` und die doppelte Pflege gibt es nicht mehr.
- **F-5** fragt nur noch nach dem Umfang der Projektion (Kurven und Abschlag: Vorschlag ja).

### 9.4 Belege im Bau (P2-05)

Je Feld gilt: Hat die Variante einen eigenen Wert, kommen Wert und Beleg aus der Variante, sonst beide aus dem Modell. Ein Variantenbeleg ohne Variantenwert wird im Bau nicht übernommen (die Warnung in `datenbank.py:202–204` bleibt). Der Client behält einen Beleg nur, wenn seine Quelle bleibt und das Feld einen Wert hat (§2.6). Den Ursprung des Belegs kann er nicht prüfen, das bleibt Aufgabe des Baus.

### 9.5 `notenblatt`: Nenner und Zeilen (P2-06)

- `g` ist das Gewicht aus `gewichte(kat, antworten, prio)`, also Grund-, Antwort- und Prioritätsgewicht.
- **`anteil` = g / Σ g über alle anwendbaren Felder** (belegt und fehlend). Die Summe ergibt 100, auch bei `nicht_anwendbar`. Es ist ausdrücklich nicht das `gewicht` aus G1, dessen Nenner nicht anwendbare Felder enthält.
- **`beitrag_r` = g · t / Σ g über die belegten anwendbaren Felder**, Summe = R.
- `merkmale` enthält **beide** Zeilentypen mit `belegt: true|false` (fehlend: `wert`, `teilpunkte`, `beitrag_r` = `null`), sortiert nach `anteil` absteigend, bei Gleichstand nach der Feldreihenfolge im Schema. `fehlend` bleibt als Liste der IDs für die Abdeckung. P2b kann so `punkteHerkunft` allein aus `merkmale` bauen („nicht angegeben“ wie G1-02).
- Quelle für Note und Beiträge ist die bewertete Zeile aus `auswerten` (dieselbe `bewerteModell`-Rechnung), es gibt keine zweite Rechnung. Bei `keine_merkmale` ist `merkmale` leer.

### 9.6 Gemeinsamer Vertrag für neue Metadaten (P2-08)

| Wert | Bau (`datenbank.py`) | Client (`datenPruefen`) |
|---|---|---|
| `gewichte_version.nummer` | ganze Zahl 1..9999, Pflicht ab Schema 2 (Fehler) | ganze Zahl 1..9999, sonst `fassung null` (still) |
| `stand`, `gelesen` | `ist_datum`, nicht in der Zukunft | echtes Kalenderdatum (Rundlauf über `Date.UTC`), nicht nach dem Datum der Datei (`d.stand`, sofern gesetzt) |
| `url`, `methodik_url`, Quell-URL | `kanon_host`: https, ohne Userinfo und Port | neue `sichereQuelle`: https, `username`/`password`/`port` leer, Länge ≤ 2000 |

`sichereUrl` bleibt für Preise und Tests unverändert (kein Eingriff in bestehende Prüfungen). Beide Seiten bekommen dieselben Testfälle (Test 44).

### 9.7 Maße (P2-09)

- Namensregel: Jede **Feld**-ID, die mit `breite`, `hoehe` oder `tiefe` beginnt, muss genau `breite_cm`, `hoehe_cm` oder `tiefe_cm` sein. Frage-IDs wie `breite` (Geschirrspüler) sind ausgenommen. Andere `_mm`-Felder bleiben erlaubt (`schwelle_mm`, `mopp_anheben_mm`, `kategorien.json:167–168`).
- Entfernt der Client einen Maßwert ≤ 0, entfernt er auch dessen Teilpunkte. Sonst zählt `hoehe_cm` beim Saugroboter (Gewicht 6) ohne Wert weiter und erhöht die Abdeckung.
- F-2: Vorschlag A bleibt die Empfehlung. Er vermeidet leere Vergleichszeilen, und P6 führt Feld und belegte Werte zusammen ein. B bräuchte zusätzliche Ausgabe- und Referenztests.

### 9.8 Übergabe zwischen P0, P2b und P6 (P2-10)

- **P0** legt das Router-Ziel `s=methodik` und im Ergebnismodul (Nachfolger von `finder.js`) den Aufrufplatz für `notenblatt` an. `punkteHerkunft` zieht dabei unverändert mit um, `test_finder_dom.mjs` „G1-02“ zieht mit.
- **P2b** füllt beide Plätze und stellt `punkteHerkunft` auf `notenblatt().merkmale` um. G1-02 läuft danach am neuen Pfad weiter.
- **P2a** ändert gemeinsame Vorlagen nicht (`tests/vorlagen/`). Neu in der Dateihoheit ist nur `.github/workflows/finder-daten.yml` (§9.3).
- **P6:** Maßarbeit an Schema und `datenbank.py` kommt erst nach P2a (wie Konzept §4, Z. 187). Reine Preis- und Produktpflege läuft parallel weiter.

### 9.9 Geänderte und neue Tests

- **6 (ersetzt)** Prüfsumme entfällt. Gegen eine Referenz: Gewicht eines Felds um 1 geändert bei gleicher Nummer → rot; dasselbe mit Nummer + 1 und neuem `stand` → grün; Faktor einer Antwort, Kurvenpunkt, `anker` jeweils geändert bei gleicher Nummer → rot; nur `mindest` geändert → grün (Gegenprobe).
- **13 (erweitert)** `breite_mm`, `hoehe`, `tiefe_innen_cm` als Feld-ID → rot; `schwelle_mm` → grün; Frage-ID `breite` → grün.
- **15 (erweitert)** Modell hat Wert und Quelle A, Variante nur Beleg B → Bau gibt Wert mit A aus. Gegenprobe: Variante mit eigenem Wert und Beleg B → Wert der Variante mit B.
- **21 (erweitert)** Maßwert −3 wird entfernt, seine Teilpunkte auch, und die Abdeckung sinkt.
- **22 (Orakel nach §9.2)** jede Zeile gleich dem Orakel, auch eine Zeile mit `passt "nein"` (Fall: Air Fryer mit einem Garraum, Wechsel `beilage` → `ja`).
- **34 (erweitert)** Priorität + fehlender Wert + nicht anwendbares Feld zusammen: Summe `anteil` = 100, Σ `beitrag_r` = R, `persoenlich` gesetzt; dazu `keine_merkmale` → `merkmale` leer.
- **36 (neu gefasst)** (a) alle bewertbaren Felder per Regler aus, keine Antwort macht ein Feld wirksam → `[]`; (b) Air Fryer `beilage=nein`, alle sichtbaren Regler aus → Zeile für `beilage=ja` mit Note.
- **37 (neu gefasst)** jede Fassung aus §9.1 gegen die neue Datei, Erwartung „wie mit den heutigen Live-Daten“.
- **38** Referenzvergleich: gleiche Projektion, gleiche Nummer → grün; gleiche Projektion, Nummer erhöht → rot.
- **39** Antwort `egal` umbenannt, alle Faktoren gleich → Projektion anders → ohne neue Nummer rot.
- **40** `1` gegen `1.0` → gleich; andere Reihenfolge der Felder → gleich; andere Reihenfolge der Fragen, Antworten oder Kurvenpunkte → anders.
- **41** Nummer kleiner als in der Referenz → rot; Referenz ohne `gewichte_version` und geänderte Projektion → rot.
- **42** Fassung 1: alle Modelle, alle wirksamen Vorgaben, Note vor und nach dem Bau gleich.
- **43** `alternativen`: unbeantwortete Frage mit `egal` (egal ist aktuell, nie Kandidat); unbeantwortete Frage ohne `egal` (alle Antworten Kandidaten); `anzeige` und `delta` `null` ohne Note.
- **44** Vertrag §9.6 mit denselben Fällen in Python und Node: Nummer 0 und 10000, Datum `2026-02-30` und Zukunft, URL mit Userinfo bzw. Port.
- **45** `NICHT_ANWENDBAR` festgeschrieben (Air Fryer `sync_funktion` bei `koerbe = 1`), wie Test 35 für `PRIO_FAKTOREN` (P-5/P-9: beide bleiben im Code, die App-Fassung gehört zur Rechengrundlage).
- **46** `passt` hängt nicht von Oberflächenfiltern ab.

**P-10 (A-5):** Die Adresse bleibt tragfähig, wenn sie bewusst die aktuelle Rechnung öffnet (A-3). Ein Hinweis auf verworfene Prioritäten ist möglich, abgeleitet aus den Einträgen, die der Parser tatsächlich verworfen hat (`finder.js:192–195`). Ob P2b ihn zeigt, ist eine Gestaltungsfrage.
