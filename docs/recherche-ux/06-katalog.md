# Recherche 06: Katalogausbau (mehr Modelle je Kategorie und Preisstufe)

Stand: 24.11.2026 · Prüfstand: selbst ausgewertet (Python über `daten/produkte/*.json`, `datenbank.py pruefen`, ein GET auf `eprel.ec.europa.eu/api/product-groups`, 3 Websuchen) · unabhängig: nein · Besitzer: Entscheidungen offen. Keine Produktdatei geändert.

## 1. Ist-Analyse (Stand `main`: 325 Modelle, 413 Varianten, 0 Fehler, 56 Warnungen)

Preisbänder sind hier einheitlich je Kategorie festgelegt. Die App bildet ihre Chips dagegen aus Quartilen der vorhandenen Preise (`budgetStufen` in `app/finder/bewertung.js`); eine dünne Datenlage verschiebt sie also mit. Zahl = Modelle mit Preis im Band (in Klammern Hersteller). Fernseher zählt Modelle nach günstigster Variante.

| Kategorie | Modelle (Var.) | ohne Preis | Warn. (keine Note) | Band 1 | Band 2 | Band 3 | Band 4 | Band 5 | Hersteller (Modelle) |
|---|---|---|---|---|---|---|---|---|---|
| Fernseher | 22 (75) | 12 | 0 | ≤400: 2 (1) | ≤700: 3 (3) | ≤1000: 3 (2) | ≤1500: 1 (1) | >1500: 1 (1) | Philips 5, Hisense 4, Samsung 4, LG 3, Sony 2, TCL 2, Panasonic 2; nur 32 von 75 Varianten mit Preis |
| Soundbar | 14 | 5 | 2 | ≤150: 1 (1) | ≤300: 2 (2) | ≤500: 3 (3) | ≤800: 1 (1) | >800: 2 (2) | Sonos 4, Samsung 4, Bose 2, Yamaha 2, JBL 1, Sony 1 |
| In-Ear | 16 | 0 | 6 | ≤50: 2 (1) | ≤100: 5 (4) | ≤180: 6 (5) | ≤250: 2 (2) | >250: 1 (1) | Soundcore 4, Sony 3, JBL 2, Bose 2, Sennheiser 2, Nothing/Google/Apple je 1 |
| Over-Ear | 17 | 0 | 7 | ≤80: 2 (1) | ≤150: 3 (3) | ≤250: 5 (5) | ≤400: 5 (4) | >400: 2 (2) | Soundcore 4, Sennheiser 3, B&W 3, Bose 2, JBL/Marshall/beyerdynamic/Sony/Apple je 1 |
| Tablet | 11 (26) | 2 | 0 | ≤200: 1 (1) | ≤350: 1 (1) | ≤600: 4 (3) | ≤1000: 1 (1) | >1000: 2 (1) | Samsung 8, Apple/Lenovo/Xiaomi je 1 |
| Smartphone | 22 (40) | **19** | 3 | ≤250: 0 | ≤450: 1 | ≤700: 0 | ≤1000: 1 | >1000: 1 | Samsung 12, Google 6, Xiaomi 2, Apple 1, Motorola 1 |
| Saugroboter | 22 | 2 | 8 | ≤250: 2 (2) | ≤400: 5 (2) | ≤700: 6 (5) | ≤1000: 5 (3) | >1000: 2 (1) | Ecovacs 10, Roborock 6, Shark 3, Dreame 2, Xiaomi 1 |
| Akkusauger | 24 | 7 | **20** | ≤150: 4 (3) | ≤250: 5 (4) | ≤400: 4 (4) | ≤600: 3 (3) | >600: 1 (1) | Dyson 6, Rowenta 5, Bosch 5, Gorenje 2, je 1 Medion/Tineco/Kärcher/Roborock/Dreame/Miele |
| Waschmaschine | 24 | 3 | 0 | ≤400: 5 (5) | ≤550: 6 (5) | ≤750: 3 (3) | ≤1000: 5 (3) | >1000: 2 (1) | Miele 5, Samsung 4, Siemens 3, 8 weitere mit 1–2 |
| Trockner | 29 | 3 | 1 | ≤500: 7 (6) | ≤700: 8 (5) | ≤1000: 5 (4) | ≤1500: 4 (2) | >1500: 2 (1) | Miele 7, Siemens 4, Samsung 4, Bosch 3 … |
| Air Fryer | 28 | 11 | 7 | ≤80: 1 (1) | ≤120: 7 (4) | ≤180: 5 (2) | ≤250: 3 (2) | >250: 1 (1) | Philips 9, Ninja 7, Cosori 6, Tefal 2, 4 mit 1 |
| Laptop | 30 (32) | 7 | 0 | ≤500: 2 (1) | ≤800: 3 (2) | ≤1200: 7 (4) | ≤1800: 11 (5) | >1800: 0 | ASUS 11, Apple 6, Lenovo 4, HP 3, Acer 2, 4 mit 1 |
| Geschirrspüler | 31 | 0 | 1 | ≤400: 8 (5) | ≤550: 6 (5) | ≤750: 9 (5) | ≤1000: 3 (3) | >1000: 5 (3) | Bosch 6, Miele 6, AEG 5, Beko 3, Gorenje 3, Siemens 3 … |
| Kühlschrank | 35 | 3 | 1 | ≤400: 6 (5) | ≤600: 7 (7) | ≤900: 8 (6) | ≤1300: 7 (5) | >1300: 4 (4) | Beko/Bosch/Samsung/Liebherr/Siemens/Miele je 4, 5 weitere |

Befund:
1. **Dünn sind nicht die Haushaltsgeräte, sondern alles andere.** Haushaltsgeräte haben je Band 5–9 Modelle und 3–7 Hersteller. Die Unterhaltungselektronik hat je Band 1–3 Modelle, oft nur 1 Hersteller; das ist genau die Beobachtung des Besitzers.
2. **Smartphone ist faktisch leer** (19 von 22 ohne Preis, damit in der Budgetsuche kaum sichtbar). Fernseher: 43 von 75 Varianten ohne Preis. Soundbar, Air Fryer, Laptop, Akkusauger je 5–11 Modelle ohne Preis.
3. **Obere Preisklassen fehlen fast überall** (Fernseher > 1500 €, Laptop > 1800 €, Air Fryer > 250 €, Akkusauger > 600 €).
4. **Hersteller-Lücken** (Eindruck aus dem Bestand, nicht aus Marktdaten): Fernseher ohne Xiaomi/Loewe/Grundig; Soundbar ohne Sennheiser, Denon, LG, Hisense; Smartphone ohne OnePlus, Nothing, Honor, Oppo/Realme, Fairphone, kaum Apple/Motorola; Tablet ohne Honor, Realme, Amazon Fire; Saugroboter ohne iRobot, Eufy, Narwal, Bosch; Akkusauger ohne Shark, Tefal, Philips, Samsung; Air Fryer ohne Russell Hobbs, Klarstein; Laptop ohne Samsung, Huawei, Framework.
5. **56 Warnungen** (Abdeckung < 70 %, keine Note) konzentrieren sich auf Akkusauger (20 von 24), Saugroboter (8), Over-Ear (7), In-Ear (6), Air Fryer (7). Diese Modelle zählen für die Auswahl faktisch nicht.
6. **Aussagefähig sind nur Modelle mit Preis und Note.** Diese wirksame Zahl liegt in Akkusauger bei ca. 10, Saugroboter ca. 12, Over-Ear ca. 10, Smartphone ca. 1.

## 2. Zielgröße je Kategorie

Marktgröße: Eine belastbare, zitierbare Zahl „Modelle im DE-Handel je Kategorie“ habe ich nicht gefunden. Preisvergleiche nennen keine Kategoriezahlen (Websuche 24.11.2026; nur Gesamtzahlen, z. B. billiger.de „mehr als 2 Millionen Produkte“). Die EPREL-Zahlen je Gruppe sind ohne Schlüssel nicht abrufbar (Modelllisten liefern 403); EPREL insgesamt „über 2 Millionen Modelle“ laut Drittseite euverify.com (nicht amtlich). Einzige Messung im Projekt: Saturn „4K-Fernseher“ 1197 Artikel am 21.11.2026 (`docs/recherche-datenquellen.md`), einschließlich Größenvarianten, Zubehör und Marktplatz. **Grobe Schätzung aus Fachwissen (nicht belegt, nur Größenordnung):** Fernseher 150–250 Modellfamilien, Smartphone 150–300, Laptop 300+, Waschmaschine 200–400, Kühlschrank 400+, Saugroboter 100–150, Akkusauger 100–150, Air Fryer 150+, In-Ear 150+, Over-Ear 80–120. Vollständigkeit ist weder erreichbar noch nötig.

Maßstab statt Vollständigkeit: **je Preisband (5 Bänder) mindestens 6 Modelle von mindestens 3 Herstellern, davon mindestens 80 % mit Preis und Note**, außerdem die für Käufer relevanten Marken. Das ergibt 30–60 Modelle je Kategorie.

| Kategorie | Ist | Ziel Modelle | Ziel Hersteller | Hauptlücke |
|---|---|---|---|---|
| Fernseher | 22 | 45 | ≥ 9 | Bänder ≤400 und >1500; Xiaomi, mehr Sony/TCL/Philips; Preise für 43 Varianten |
| Soundbar | 14 | 35 | ≥ 8 | alle Bänder; Bose, Sennheiser, LG, Denon, Hisense |
| In-Ear | 16 | 40 | ≥ 10 | Bänder >180 und ≤50; Warnungen beheben |
| Over-Ear | 17 | 35 | ≥ 9 | Bänder ≤80 und >400; Warnungen beheben |
| Tablet | 11 | 30 | ≥ 7 | alle Bänder, Preise, Honor/Amazon/Realme |
| Smartphone | 22 | 55 | ≥ 10 | Preise (19 fehlen), Bänder ≤250 und 450–700, Apple, OnePlus, Nothing, Motorola |
| Saugroboter | 22 | 45 | ≥ 9 | iRobot, Eufy, Narwal; ≤250 und >1000 |
| Akkusauger | 24 | 45 | ≥ 10 | 20 Warnungen beheben; Band >600 |
| Waschmaschine | 24 | 45 | ≥ 10 | Bänder 550–750, >1000 |
| Trockner | 29 | 40 | ≥ 10 | Bänder >1000 |
| Air Fryer | 28 | 45 | ≥ 10 | Band >180 (nur Cosori/Philips), Preise für 11 |
| Laptop | 30 | 60 | ≥ 10 | ≤500, ≤800, >1800; Samsung/Huawei; Chromebooks |
| Geschirrspüler | 31 | 45 | ≥ 10 | Bänder 750–1000 und >1000 |
| Kühlschrank | 35 | 55 | ≥ 11 | >1300; Gefrierkombi/Side-by-Side getrennt kennzeichnen |
| **Summe** | **325** | **~620** | | **+ ca. 295 Modelle, ca. 60 Preisnachträge, 56 Abdeckungsreparaturen** |

Begründung: 5 Bänder × 6 Modelle = 30 als Untergrenze, bei breiten Märkten (TV mit Größenstufen, Smartphone, Laptop, Kühlschrank) bis 60. Mehr als ~60 je Kategorie verbessert die Auswahl kaum, erhöht aber Pflegeaufwand (Preise täglich, Aktualität) und Fehlerrisiko. Das ist ein Vorschlag; der Besitzer entscheidet.

## 3. Durchsatz und Quellen

### Messwerte aus dem Projekt

- Abstand ≥ 61 s je Domain über alle Prozesse (`werkzeuge/datenpflege/abruf.py`): **höchstens ~59 Abrufe je Stunde und Domain**.
- Laptop-Lauf 22.11. (allein, Alternate): 28 Abrufe für 24 neue Modelle, also **~1,2 Abrufe je Modell** (Produktseite = Datenblatttabelle + JSON-LD mit Preis und Verkäufer).
- Sechs parallele Agenten am 21.11. teilten sich den Saturn-Takt; der Laptop-Agent kam auf 3 Abrufe in ~9 min. Der Takt ist ein Einzelbetriebsmittel: mehr Agenten je Domain bringen nichts.
- Sperren: Alternate 429 nach ~15 schnellen Abrufen (bei 61 s Takt keine), Proshop teils 403, Herstellerseiten 403/429 (Sony, JBL, Dyson, Miele, Roborock, Dreame). Saturn bei ≥ 60 s ohne Sperre.
- Entdeckung 22.11. (`%TEMP%/kb-datenpflege/entdeckung/kandidaten.json`): 3 Saturn-Seiten je Kategorie = 36 Treffer, davon 20–36 unbekannte Kandidaten, zusammen **~375 Kandidaten**. Das reicht nicht sicher für +295 brauchbare Modelle (Zubehör, Auslaufmodelle, Marktplatz, Doppelte; Annahme Ausbeute ~50 %). Es brauchen 5–6 Seiten je Kategorie einmalig (D10 begrenzt auf 3).

### Quellen im Vergleich

| Quelle | Abrufe je Modell | Liefert | Nutzen für das Ziel | Hindernis |
|---|---|---|---|---|
| **Saturn-Produktseite** | 1 | Haushaltsgeräte: Label-/Datenblattwerte, EAN, Preis, Verkäufer (`mms_preisfeld`); Unterhaltungselektronik: wenig Werte | sehr hoch für Waschmaschine, Trockner, Kühlschrank, Geschirrspüler | Takt 61 s; Marktplatzangebote ausschließen |
| **Alternate-Produktseite** | 1 | Datenblatttabelle + JSON-LD (Preis, Verkäufer); gut für Laptop, TV, Tablet, Smartphone, Saugroboter, Kopfhörer, Soundbar | hoch (24 Laptops in 28 Abrufen) | Takt; 429 bei Überschreitung; geratene Listenseiten 404 |
| **Proshop** | 1 | Preis ja, Datenblatt im HTML nein | nur Preis-Zweitquelle | teils 403 |
| **Herstellerseiten** | 1–2 | HDR-Formate, HDMI 2.1, Saugleistung usw. | nötig nur für Felder, die Shops nicht haben; je Hersteller eigene Domain, also **eigener Takt, parallel möglich** | oft 403/429; Layout je Hersteller verschieden |
| **EPREL-Einzeldatensatz** (`/api/products/<gruppe>/<Nr>`) | 1 | amtliche Werte für TV, Smartphone, Tablet, Haushaltsgeräte | Zusatzwerte; ersetzt Shopseiten nicht | Nummer nur über QR-Code/Suche; Handelsname und EAN fehlen; Zugang einmal 200, einmal 403 (ungeklärt) |
| **EPREL mit Schlüssel (Liste)** | 1 je Listenseite | Modellkennungen, Marktstart/-ende der 6 Gruppen | spart Entdeckungsabrufe, nicht Preis- und Wertabrufe; Zuordnung Kennung zu Handelsname bleibt Handarbeit | Schlüssel nur per digital signierter Erklärung des Besitzers (D11: vorerst nicht beantragen) |
| **Open Icecat** | 1 | strukturierte Datenblätter | unsicher: nur Sponsor-Marken (belegt: HP, Sony, Microsoft, Tefal, Whirlpool, Intel, BenQ; Samsung, LG, Bosch, Philips, Lenovo, ASUS, Dyson in der Websuche vom 24.11.2026 nicht auffindbar) | Konto nötig (Besitzer); Lizenz 1.4 (11.02.2026) erlaubt kostenlose öffentliche App mit Vermerk, KI-Training verboten; `icecat.biz` hinter Bot-Prüfung (nicht umgangen) |
| **Hersteller-PDF-Datenblätter** | 1–2 | volle Werte | niedrig: PDF-Link muss erst gefunden werden, Formate uneinheitlich | Zuordnungs- und Parsingaufwand je Hersteller |

Folgerung: **Keine Quelle liefert viele Werte mit wenigen Abrufen; der Engpass ist 1 Produktseite = 1 Abruf = 61 s.** EPREL mit Schlüssel und Icecat sparen nur Entdeckung bzw. einzelne Felder und bringen dem Besitzer Konto- und Signaturpflichten. Die wirtschaftlichste Quelle je Kategorie ist Saturn (Haushaltsgeräte) bzw. Alternate (Technik).

### Aufwandsrechnung für das Ziel (+295 Modelle)

| Posten | Abrufe |
|---|---|
| Neue Modelle (Haushaltsgeräte Saturn ~1,0, Technik Alternate ~1,3 je Modell) | ≈ 355 |
| Preise und Werte nachtragen für ca. 60 Bestandsmodelle ohne Preis | ≈ 70 |
| Abdeckungsreparatur 56 Warnungen (je ~1 Herstellerseite, ~50 % erfolgreich) | ≈ 60 |
| Entdeckung: zusätzliche Listenseiten (14 Kategorien × 3 weitere) | ≈ 42 |
| Fehlversuche, Weiterleitungen, Sperren (Zuschlag 20 %) | ≈ 115 |
| Stichproben-Neuabruf 10 % der Neueinträge | ≈ 30 |
| **Summe** | **≈ 670** |

Verteilung grob: Saturn ~280, Alternate ~270, Proshop ~20, Herstellerdomains ~100 (auf ~15 Domains).
- **Reiner Takt:** Saturn 280 min ≈ 4,7 h, Alternate 270 min ≈ 4,5 h. Läuft beides gleichzeitig (verschiedene Domains), sind das **~5 Stunden Wanduhr** bei voller Auslastung.
- **Realistisch** (Agentenarbeit, Korrekturschleifen, Sperrpausen von 30 min, Takt nur zu ~60 % ausgelastet): **2–3 Arbeitstage**, auf zwei bis drei Läufe verteilt. Stufe 1 und 2 (Abschnitt 4, ~270 Abrufe) in etwa 1 Tag.
- Die wöchentliche Routine (D11: ≤ 10 neue Modelle) bräuchte für +295 Modelle ~30 Wochen: **Ausbau als einmalige Aktion, nicht über die Routine.**
- Alle Zahlen sind Schätzungen aus den Messwerten oben; die Ausbeute der Kandidaten ist die größte Unbekannte.

## 4. Vorgehen für den parallelen Ausbau

**Grundidee: nach Domain trennen, nicht nach Kategorie.** Der Takt gilt je Domain. Kategorie-Agenten, die alle Saturn brauchen, blockieren sich (Lehre 21.11.). Besser eine **Zweistufen-Pipeline**:

1. **Abrufstufe (ein Prozess je Domain, läuft im Hintergrund):**
   - Lane S (Saturn): Haushaltsgeräte, danach Air Fryer, Saugroboter, Akkusauger, Kopfhörer.
   - Lane A (Alternate): Laptop, Tablet, Smartphone, Fernseher, Soundbar, Saugroboter.
   - Lane P (Proshop): nur Preisnachträge.
   - Lane H (Hersteller): ein Prozess, wechselt reihum zwischen Herstellerdomains (je Domain 61 s, daher kaum Wartezeit); nur für Felder, die Shops nicht haben.
   - Jede Lane arbeitet eine **Warteschlange** (JSON im Temp-Ordner: URL, Kategorie, Modellname) ab; `abruf.py` legt die Seiten schon unter `%TEMP%/kb-datenpflege/abrufe` ab. Der Lead startet, überwacht und beendet die Lanes; **kein Agent beendet Abrufprozesse anderer** (Fehler 21.11.).
2. **Eintragsstufe (ein Agent je Kategorie, ohne Netzzugriff auf die Shops):** liest nur die abgelegten Seiten, schreibt die eigene Produktdatei, prüft mit `datenbank.py`. Kein Takt-Konflikt, Agenten laufen parallel, eine Datei je Agent wie bisher. Optional ein kleines Extraktionsskript je Shop (Datenblatttabelle → Rohwerte mit wörtlichem Beleg), das die Agenten nur noch prüfen und auf Schemafelder abbilden.
3. **Entdeckung vorab (einmal):** `entdeckung.py --seiten 6` je Kategorie (setzt eine Besitzerfreigabe für D10 voraus). Aus Kandidaten und Zielbändern entsteht die Warteschlange gezielt je Lücke (Preisband × Hersteller), nicht in Reihenfolge der Saturn-Liste.

**Reihenfolge nach Nutzen:**
1. **Preise und Werte für Bestand ohne Preis** (Smartphone 19, Fernseher 43 Varianten, Air Fryer 11, Soundbar 5, Laptop 7). Höchster Nutzen je Abruf, weil ein Modell erst damit in der Budgetsuche erscheint.
2. **Haushaltsgeräte-Bänder auffüllen** (Saturn-Lane, hohe Datenqualität): Waschmaschine, Geschirrspüler, Trockner, Kühlschrank (+ ca. 70 Modelle).
3. **Unterhaltungselektronik** (Alternate-Lane): Fernseher, Soundbar, Smartphone, Tablet (+ ca. 110 Modelle).
4. **Laptop** (+ 30): Alternate-Lane, erprobt (1,2 Abrufe je Modell).
5. **Saugroboter, Akkusauger, Air Fryer** (+ ca. 60): erst Warnungen beheben, dann ausbauen (Werte oft nur bei Herstellern).
6. **In-Ear/Over-Ear** (+ ca. 45): zuletzt, hoher Warnungsanteil, Herstellerseiten gesperrt.

**Entscheidungen für den Besitzer:** (a) D10 „≤ 3 Listenseiten je Kategorie“ für einen einmaligen Ausbau auf bis zu 6 anheben (nur Kandidatenliste, § 87b-Restrisiko wie bisher begründet); (b) Zielzahlen; (c) EPREL-Schlüssel und Icecat-Konto sind für das Ziel **nicht** nötig.

## 5. Qualität: häufige Fehler und Gegenmaßnahmen

Fehler aus den Agentenberichten (`docs/uebergabe-finder.md`, 21.–22.11.2026) und die vorgeschlagene Schranke:

| Fehler bisher | Gegenmaßnahme (möglichst automatisch) |
|---|---|
| Preise aus nicht freigegebenen Quellen (Atlas Vision Store, MediaMarkt) | Domain-Positivliste in `datenbank.py` besteht. Zusätzlich: Preis nur zulässig, wenn der Abruflog der Sitzung (`abruf.py`: URL, Zeitstempel, Preis, Verkäufer) einen passenden Eintrag hat. |
| Weiterleitung per neuer URL nachgezogen statt Exit 5 zu beachten | `abruf.py` gibt die Zielseite nur als Hinweis aus; neue URL kommt als neuer Warteschlangeneintrag mit Freigabe des Leads. |
| Werte gedeutet statt belegt (dToF → `lidar`, Reactive AI → `kamera_ki`, „PureVoice“ → `sprachmodus`, Yamaha-Kanäle abgeleitet, `wischsystem` aus Modellname) | **Deutungsliste** je Feld (z. B. `daten/schema/deutungen.json`: erlaubte Begriffe → Wert, vom Lead freigegeben). Wert nur zulässig, wenn (a) ein wörtlicher Beleg (Zahl + Einheit oder Stufenwort) in der gespeicherten Seite steht oder (b) der Begriff in der Deutungsliste steht. Ein Prüfbefehl sucht den Beleg in der Ablage und meldet ungedeckte Werte. |
| Werte nur aus dem zweiten Saturn-Datensatz (anderer Anbieter; IP-Schutz, Akku) | Bei Saturn nur der Datensatz des eigenen Angebots (`mms_preisfeld`); Prüfer markiert Werte, die nur im Marktplatzblock stehen. |
| Unplausible oder widersprüchliche Werte (Bauhöhe 11,1 vs. 8,9 cm; Schwelle 80 mm; 120 vs. 144 Hz; Energieklasse F vs. E) | Plausibilitätsgrenzen je Feld im Schema (min/max); außerhalb = Fehler. Widersprechen sich zwei Quellen, wird der Wert weggelassen und im Bericht genannt. |
| Fremde Schlüssel (`listenpreis`) | Schranke besteht (unbekannte Schlüssel = Fehler); als Beispiel in die Anleitung aufnehmen. |
| Zuordnung per Websuche (EPREL, Xiaomi 17T); EU-Mindestwert statt Herstellerzusage (`update_jahre`) | Zuordnung nur über EAN/MPN auf der Produktseite, sonst weglassen. `update_jahre` nur mit Herstellerzusage (O13 klären). |
| Fremde Prozesse beendet (Saturn-Abrufe anderer Agenten) | Nur der Lead startet und beendet Abrufprozesse; Eintragsagenten haben keinen Abrufzugriff (Pipeline oben). |
| Takt-Verschwendung (3 Abrufe in 9 min), geratene Listenseiten (404) | Lanes statt Agenten je Kategorie; Listen-URLs nur aus `sitemap-productlistpages.xml` bzw. `entdeckung.py`. |
| Ausbau ändert oder löscht Bestand | `git diff`-Schranke: nur Modelle hinzufügen und fehlende Werte ergänzen; geänderte oder entfernte Bestandswerte müssen im Bericht stehen (D11 verbietet Löschen ohnehin). |
| Doppelte Modelle | Schranke: gleiche EAN/MPN oder gleicher Hersteller + Name in derselben Kategorie = Fehler. |
| Abdeckung < 70 % erst nachträglich bemerkt | Vor dem Eintrag Abdeckung rechnen; Modell unter 70 % nur eintragen, wenn ein Herstellerabruf folgt, sonst verwerfen („lieber 8 gut belegte als 20 halbe“). |
| Ungeprüfte Übernahme | Stichprobe 10 % der Neueinträge per Neuabruf (21.11.: 18 von 19 bestätigt); Prüfpunkt je Stufe vor Veröffentlichung. |

Reihenfolge der Schranken (Aufwand klein bis mittel): Plausibilitätsgrenzen im Schema, Duplikatprüfung, Diff-Schranke, danach Belegprüfung gegen die Abrufablage und Deutungsliste.

## Quellen (abgerufen 24.11.2026)

- EPREL Produktgruppen: https://eprel.ec.europa.eu/api/product-groups (200, 33 Gruppen, keine Anzahl je Gruppe)
- EPREL-Nutzungsbedingungen, API-Schlüssel, Signatur, Open-Icecat-Lizenz: `docs/recherche-datenquellen.md` (abgerufen 21.11.2026)
- Icecat-Sponsoren (Websuche 24.11.2026): https://iceclog.com/gain-access-to-the-global-e-commerce-market-as-open-icecat-sponsor/amp/
- EPREL-Gesamtbestand (Drittseite, nicht amtlich): https://euverify.com/resource/eu-energy-label/
- Saturn-Entdeckungsstand 22.11.2026 und Abrufmessungen: `docs/uebergabe-finder.md`, `%TEMP%/kb-datenpflege/entdeckung/kandidaten.json`
