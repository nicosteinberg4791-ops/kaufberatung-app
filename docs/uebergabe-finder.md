# Übergabe: Finder „Finden & Vergleichen“ (Zweig `datenbank`)

Stand: 21.11.2026 · Zweig `datenbank` (Worktree `.claude/worktrees/datenbank`, in `.git/info/exclude`) · Commit c20480f · Prüfstufe: selbst geprüft (Prüfskript, Tests) · unabhängig nein · Besitzer: Ziel freigegeben, Veröffentlichung nach Prüfung.

## Auftrag des Besitzers (21.11.2026)

Suche mit freiem Preisrahmen („Fernseher bis 500 €“) und Aufpreis-/Spar-Hinweis („für 100 € mehr +9 Punkte“), große Vergleichsdatenbank aller aktuellen Modelle, intuitiv für jeden, aktualisiert sich von allein, legal, schnell, immer verfügbar. Kategorien: alle 14 (TV, Akkusauger, Saugroboter, Air Fryer, Smartphone, Tablet, Laptop, Kopfhörer In-Ear/Over-Ear, Soundbar, Waschmaschine, Trockner, Kühlschrank, Geschirrspüler). Fertig, wenn live.

## Entscheidungen (noch in `docs/entscheidungen.md` als D8–D11 eintragen)

- D8 Architektur: Datenbank im App-Repo (`daten/produkte/*.json`, Schema `daten/schema/kategorien.json`); neue Startseite Finder (Wurzel `index.html`), bisheriger Artifact-Inhalt wird `ratgeber.html`. AGENTS-Regel „Inhalt nur aus dem Artifact“ gilt dann nur noch für den Ratgeber. (Lead-Empfehlung, Besitzer: „Was empfiehlst du … muss langfristig funktionieren“.)
- D9 Punkte ohne Test „aus Datenblatt“ mit Abschlag (Formel im Schema, Kappung 84, unter 70 % Abdeckung keine Note). Besitzer.
- D10 Wöchentliche Entdeckung neuer Modelle über Saturn-Kategorieseiten, begrenzt (≤ 3 Listenseiten je Kategorie, Pausen), nur Kandidatenliste (§ 87b-Restrisiko). Besitzer.
- D11 Wöchentliche Claude-Routine trägt neue Modelle mit belegten Werten ein; geht automatisch live, wenn `datenbank.py pruefen` grün ist; nie automatisch löschen. Besitzer. EPREL-Schlüssel: vorerst nicht beantragen.
- Startbestand: je Preisstufe eine sinnvolle Auswahl (Besitzer: „Top 10 je Preisstufe als Beispiel, sinnvolle Anzahl, verschiedene Hersteller“).

## Erledigt (Zweig `datenbank`)

- `docs/recherche-datenquellen.md` (EPREL, Open Icecat, Shops, § 87b), `docs/punkteschema.md` + `daten/schema/kategorien.json` (14 Kategorien, Kurven, Fragen, Klassen, Abschlag, Aufpreis-/Spar-Regeln).
- `daten/produkte/FORMAT.md` + `werkzeuge/datenbank.py` (`pruefen`, `bauen <ziel>` → kompakte `finder-daten.json` mit Teilpunkten).
- 14 Produktdateien: 278 Modelle, 362 Varianten, 0 Fehler, 85 Abdeckungswarnungen.
- `app/finder/` (index.html, finder.js, finder.css, bewertung.js) + `tests/test_bewertung.mjs`, `tests/test_finder_dom.mjs` (`node --test` 30/30), Beispieldaten `tests/vorlagen/finder-beispiel.json` (erfunden, nie in die App).

## Datenlage je Kategorie (Modelle / Varianten mit Preis / Hersteller)

| Kategorie | Modelle | mit Preis | Hersteller | Lücke |
|---|---|---|---|---|
| Waschmaschine, Trockner, Kühlschrank, Geschirrspüler | 24/29/35/31 | 21/26/32/31 | 10–11 | gut (Saturn-Seiten, 1 Abruf/min, keine Sperre) |
| Air Fryer | 28 | 17 | 8 | über 250 € nur Cosori |
| Fernseher | 16 (67 Var.) | 31 | 4 | Sony/TCL/Panasonic fehlen; LG ohne Hz/HDMI/eARC; `hdmi_4k120_anzahl` überall leer |
| Soundbar | 10 | 7 | 3 | JBL/Sony/Yamaha fehlen |
| Akkusauger | 24 | 14 | 10 | viele < 70 % Abdeckung |
| Saugroboter | 13 | 11 | 2 | nur Ecovacs/Shark, über 1000 € leer |
| Kopfhörer In/Over | 16/17 | alle | 8/9 | 31 von 33 < 70 % Abdeckung (keine Note) |
| Smartphone, Tablet | 20/9 | 0 | 3/2 | kein iPhone/Motorola/Lenovo, keine Preise |
| Laptop | 6 | 0 | 1 (Apple) | Windows/ChromeOS fehlen ganz |

Erkenntnisse: Alternate sperrt nach ~15 schnellen Abrufen (429, Cloudflare), Proshop teils 403, viele Herstellerseiten 403/429 (Sony, JBL, Dyson, Miele, Roborock, Dreame). Saturn mit ≥ 60 s Abstand ohne Sperre, liefert bei Haushaltsgeräten Labelwerte, EAN, Verkäufer. EPREL-Einzeldatensatz per API ohne Schlüssel: bei einem Agenten 200, bei einem anderen 403 – klären. Agenten-Abweichungen zum Nachprüfen: Feld `listenpreis` (airfryer, laptop) nicht im Format; Saturn-Verkäufer bei Kopfhörern nur erschlossen; drei EPREL-Zuordnungen per Websuche (Xiaomi 17T, Pixel 11 Pro/XL); `update_jahre` = EU-Mindestwert statt Herstellerzusage.

## Offen / blockiert

- O11 Impeccable: **entschieden** (Besitzer 21.11.2026: „Installation freigeben“). `.impeccable/config.json` mit Telemetrie aus liegt im Worktree. Installiert vom Besitzer am 22.11.2026 (impeccable 4.10.0, Projektbereich, ohne Hook, ohne Konto, `telemetry status`: off). README-Stand 21.11.: `--no-hooks` ist nicht mehr dokumentiert, der Installer fragt nach dem Hook (mit „nein“ beantworten); Telemetrie laut README per `npx impeccable telemetry off`, `DO_NOT_TRACK=1` oder `config.json`. Danach AGENTS-Vermerk „Design: Impeccable (Projekt, Telemetrie aus, ohne Hook)“.
- O12 `listenpreis` ins Format aufnehmen (Preisstufe ohne Lieferbarkeit) oder streichen → Lead.
- O13 `update_jahre`: EU-Mindestwert oder Herstellerzusage → Besitzer.
- Pilot-Preisabruf (O9) wird in der Pilot-Sitzung nach Codex-R1 „nicht bestanden“ korrigiert; tägliche Finder-Preise hängen davon ab.

## Stand 21.11.2026 abends (Arbeitszweig `claude/admiring-pasteur-32f79f`)

- **Schritt 1 erledigt** (Commit 8ce6e78, selbst geprüft): `app_bauen.py` baut `index.html` = Finder (Hülle `app/finder/finder-app.js`: Service Worker, Hinweis „Neue Fassung“, alte Sprungmarken ohne „=“ → `ratgeber.html`), `ratgeber.html` = Artifact-Inhalt (mit Rückweg-Link „‹ Finden & Vergleichen“ aus `app.js`), `finder-daten.json` über `datenbank.bauen`, leere `finder-preise.json` als Startstand; `sw.js` Navigation je Seite, finder-*.json netz-zuerst, Benachrichtigungsziele `ratgeber.html#…`; `veroeffentlichen.py` behält `finder-preise.json`; `alle-tests.ps1` mit `node --test` (Finder 31 + Weiterleitung 3 Tests); `pruefe.mjs` prüft Finder und Ratgeber. Belege: Sammellauf 0 Fehler, `pruefe.mjs` lokal: 14 Kacheln, Ergebnis 700 € mit Aufpreis-Hinweis „+10 Punkte“, hell/dunkel 375 px ohne Überbreite, 0 Tippziele < 44 px, offline beide Seiten, installierbar. Browserbefund behoben: Budgetfeld folgte Adresswechsel nicht (Test rot→grün).
- **Schritt 2 läuft:** sechs Subagenten (Sonnet medium) bearbeiten je eigene Dateien in `daten/produkte/` (laptop; smartphone+tablet; saugroboter; kopfhoerer_inear+overear; fernseher; soundbar+akkusauger) nach `werkzeuge/datenpflege/ANLEITUNG.md`. Alle Abrufe über `werkzeuge/datenpflege/abruf.py` (je Domain ≥ 61 s über alle Prozesse, robots.txt, Sperre bei 403/429 30 min, Saturn-Eigenangebot über `mms_preisfeld`). Ihre Änderungen sind **nicht committet und nicht geprüft**.
- **Agentenbericht Laptop (21.11.):** keine Änderung an `laptop.json`; nur 3 Abrufe in ~9 min (geteilter Takt bei 6 Agenten zu langsam), Alternate `/Notebooks` 404, ASUS-Markenseite ohne JSON-LD (Produktseiten-IDs 100201883, 100227399, 100214553, 100227394, 100189890, 100201882, 100227395). `listenpreis` steht noch in 8 Apple-Varianten (entfernen, O12). Folgerung: Laptop allein und später neu starten, Produktseiten direkt statt geratener Listenseiten.
- **Agentenbericht Smartphone/Tablet (21.11., ungeprüft, unkommittet):** Smartphone 20→22 Modelle (iPhone 17, moto g67), Tablet 8→11 (Lenovo Idea Tab Pro Gen 2, Redmi Pad 2); Preise 4 bzw. 16 Varianten. EPREL-API `eprel.ec.europa.eu/api/products/smartphonestablets20231669/<Nr>` liefert ohne Schlüssel JSON (Ladezyklen in Hundertern). Xiaomi-17T-EPREL-Werte entfernt (nicht belegbar), Pixel 11 Pro/XL jetzt über Google-Rechtshinweise belegt. Nachprüfen: Galaxy A57 256 GB 403 € Alternate (Samsung 459 €), iPad Proshop-MPN MD3Y4KN/A (nordische Variante?), Samsung-Shop ohne Verkäuferangabe im JSON-LD, Xiaomi-17T-Betriebssystem nur per Fußnote belegt. `update_jahre` überall EU-Mindestwert (O13 offen); Pixel 11 Pro EPREL minYears 5 widerspricht Score „>7“.
- **Agentenbericht Soundbar/Akkusauger (21.11., ungeprüft, unkommittet):** Soundbar 10→14 (JBL Bar 800 459 € Alternate, Sony HT-SF150 77,90 € Alternate, Yamaha SR-B40A/B30A ohne Preis – nur Marktplatz). Nachprüfen: JBL `sprachmodus=true` nur aus „PureVoice“ erschlossen (ohne ihn 64 % → keine Note), Yamaha `kanaele` 2.1 abgeleitet, B30A-Sprachmodus aus Saturn-Text. de.jbl.com 403. Akkusauger: Warnungen 21→20, Preise 14→17 Varianten (Bosch-Shop „BSH“), Rowenta RH9958/Kärcher VC 6 ergänzt; Bosch-Seiten nennen keine AW/Filter/Bürste, daher bleiben viele knapp unter 70 %. Schema-Lücke: Kanäle „3.0.2“ (Sony Trio) nicht vorgesehen.
- **Agentenbericht Fernseher (21.11., ungeprüft, unkommittet):** 16→22 Modelle (Sony BRAVIA 3/8, TCL C7K/P7L, Panasonic Z90B/Z95B), 75 Varianten, 39 mit Preis, 0 Warnungen; LG C6/B6/G6 mit Hz, HDMI-4K120, eARC; `hdmi_4k120_anzahl` für LG, S90H, Panasonic. **Regelabweichungen vor Übernahme klären:** (1) Panasonic-Preise vom Atlas Vision Store – Quelle nicht in `daten/quellen.json` geprüft (robots/AGB) → prüfen oder Preise entfernen; (2) zwei Weiterleitungen (Saturn BRAVIA 8, Atlas Z95B) per neuer URL nachgezogen statt „nicht verfolgen“ → Z95B-Preis prüfen; (3) TCL-Preise von MediaMarkt, dort laut `quellen.json` nur Link (automatisch=false) → Freigabe klären. Offen: LG C6 65″ Energieklasse F (LG) vs. E (Saturn); TCL C7K 120 vs. 144 Hz (120 eingetragen).
- **Agentenbericht Saugroboter (21.11., ungeprüft, unkommittet):** 13→22 Modelle (Roborock 6, Dreame 2, Xiaomi 1; alle Preise Alternate, InStock), über 1.000 € nur Saros 20 Complete ×2; Ecovacs-Navigation nachbelegt (4 Modelle jetzt ≥ 70 %), 8 Warnungen. iRobot fehlt (Alternate führt keine, Proshop „Discontinued“). de.roborock.com und dreametech.com 429. **Gedeutete Werte prüfen:** dToF/Mini-ToF → `lidar`, „Reactive AI“ → `kamera_ki`, VibraRise → `vibrierend`, Aqua10 `wischsystem` aus Modellname, `schwelle_mm` 80 (Aqua10) und Bauhöhe 11,1 cm (L60) unplausibel → im Zweifel entfernen.
- **Agentenbericht Kopfhörer (21.11., ungeprüft, unkommittet):** 22 von 31 Modellen jetzt ≥ 70 % (In-Ear Warnungen 14→4, Over-Ear 17→5); alle 33 Saturn-Preise mit Eigenangebot-Nachweis bestätigt. **Prüfen:** Werte nur aus dem *zweiten* Saturn-Datensatz (anderer Anbieter) – IP54 bei P30i v2/Nothing Ear (a)/Pixel Buds 2a, Bose QC Ultra Earbuds 2 (kabellos laden, BT 5.3, IPX4), AirPods Max 2 `faltbar` → im Zweifel entfernen; aptX Lossless/HD → `aptx_adaptive`/`aptx` gemappt; B&W `akku_h` 30 ohne ANC-Angabe. Liberty Buds `akku_gesamt_h` 27→26 korrigiert. Der Agent hat versehentlich laufende Saturn-Abrufe anderer Agenten per Prozess-Kill abgebrochen.
- **Schritt 3 begonnen:** `.github/workflows/finder-daten.yml` (bei Änderung `daten/**` auf main: prüfen → bauen → nur `finder-daten.json` auf gh-pages, Push mit Neuaufsetzen bei Konflikt), nicht gelaufen.
- **Erkenntnis für Schritt 3:** Saturn und Proshop sperren GitHub-Actions-IPs (Pilot-Lauf 44871394260). Entdeckung (D10) und Datenpflege-Routine (D11) daher **lokal am Heimrechner** (geplante Aufgabe in Claude Desktop), nicht in Actions oder als Cloud-Routine; Grenze: Rechner muss laufen. `preise_aktualisieren.py push` hat keinen Wiederholversuch bei Konflikt mit dem Finder-Daten-Push (kleines Zeitfenster, offen).
- Offen: Saturn-Sitemap `sitemaps/sitemap-productlistpages.xml` über den Helfer brach mit Exit 255 ab (Ursache ungeklärt; evtl. Größe/Gzip). Rückweg-Link im Ratgeber liegt auf dem Handy knapp über der sichtbaren Fläche (Seite scrollt beim Start 44 px), Gestaltung offen. Impeccable (O11) weiter beim Besitzer; Hook verlangt sonst Zeile „Impeccable: entfällt – <Grund>“ in AGENTS.md.

## Schritt 2 übernommen (21.11.2026 spät, Lead, selbst geprüft)

Ergebnis: 278 → 301 Modelle, 389 Varianten, `datenbank.py pruefen` 0 Fehler, Warnungen 85 → 56. Bereinigt (Grundsatz „im Zweifel entfernen“):
- **Preise entfernt:** TCL C7K/P7L (MediaMarkt, laut `daten/quellen.json` nur Link), Panasonic Z90B ×3 und Z95B (Atlas Vision Store: nicht freigegeben; Z95B zusätzlich über Weiterleitung). Datenblattwerte aus diesen Seiten bleiben (Fakten einer Produktseite, Quelle genannt). BRAVIA 8 hat keinen Preis (Weiterleitung folgenlos).
- **Kopfhörer-Werte entfernt** (nur aus zweitem Saturn-Datensatz oder ohne ANC-Angabe): IP-Schutz bei P30i v2, Nothing Ear (a), Pixel Buds 2a, Bose QC Ultra Earbuds 2 (dort auch kabellos laden, BT-Version); AirPods Max 2 `faltbar`; B&W Px8 und Px8 S2 `akku_h`. Behalten: aptX Lossless → `aptx_adaptive` (Teil von aptX Adaptive), aptX HD → `aptx` (untere Stufe).
- **Saugroboter:** Quelle neu gelesen (Alternate): Saros 10 „Kamera, LiDAR“ + ReactiveAI → `kamera_ki` belegt; VibraRise „Vibrationswischfunktion/-mopp“ → `vibrierend` belegt; Aqua10 `schwelle_mm` 80 steht so im Datenblatt (bleibt); Saros 20 Sonic 88 mm = „doppelte Schwellen bis 8,8 cm“ (bleibt). Entfernt: Aqua10 `wischsystem` (nur Modellname), L60 `hoehe_cm` (Seite nennt 8,9 cm mit abgesenktem LDS, Datenblatt 11,1). dToF/LDS → `lidar` gilt als Begriffsgleichheit (Laser-Abstandssensor).
- **Soundbar:** JBL Bar 800 `sprachmodus` belegt („PureVoice … optimiert die Sprachverständlichkeit“, Alternate); Yamaha `kanaele` 2.1 aus „Front L/R 2-ch + Subwoofer“ (Yamaha-Datenblatt) belegt.
- **`listenpreis` gestrichen** (O12 entschieden, Lead): 12 Air-Fryer- und 8 Laptop-Varianten; nicht lieferbare Preise gehören nicht in die Preisstufe.
- **Schranke verschärft:** `datenbank.py` meldet unbekannte Schlüssel (Modell, Variante, Preis) und Preise von Domains mit `automatisch: false` in `daten/quellen.json` als Fehler; Tests `tests/test_datenbank.py` (5). FORMAT.md ergänzt.
- **Stichproben** (selbst neu abgerufen über `abruf.py`, Seed 20261121): 19 Preise aus allen 8 Dateien, 18 bestätigt (Preis gleich, Verkäufer = Shop, lieferbar; Saturn mit `mms_preisfeld` ohne Marktplatz). Galaxy A57 256 GB 403 € (Alternate) und iPad Proshop 539 € bestätigt. **LG B6 83″:** LG-Seite zeigt 6.099 €, nicht lieferbar → Preis entfernt; die übrigen 8 LG-Shop-Preise einzeln nachgeprüft und bestätigt (lieferbar, Verkäufer LG DE). Werte: 8 von 16 Zahl-/Textwerten wörtlich gefunden, Rest (bool/Stufe) nicht automatisch prüfbar.
- Offen (Daten): LG C6 65″ Energieklasse F (LG) vs. E (Saturn) – LG-Wert bleibt; TCL C7K 120 Hz laut Quelle; Pixel 11 `update_jahre` 5 = EPREL-Mindestwert (O13 Besitzer); Laptop weiter nur Apple; Atlas/Panasonic-Preise erst nach Quellenprüfung.

## Nächste Schritte (in dieser Reihenfolge)

1. **Einbau in den App-Bau:** `werkzeuge/app_bauen.py` baut `index.html` aus `app/finder/index.html` (+ Manifest, Icons, Service-Worker-Anmeldung, Weiterleitung `#besitzer…`/`#preiswecker` → `ratgeber.html`), den Artifact-Inhalt als `ratgeber.html`, `finder-daten.json` über `datenbank.py bauen`; `sw.js`: Navigation je Pfad (`index`/`ratgeber`), `finder-daten.json` und `finder-preise.json` netz-zuerst, Benachrichtigungsziel `./#preiswecker` → `ratgeber.html#preiswecker`; `tests/alle-tests.ps1` um `node --test` ergänzen; `veroeffentlichen.py` prüfen. Fertig, wenn Bau + alle Tests grün und `preview_start` „kb-app“ den Finder mit echten Daten zeigt (360 px, hell/dunkel, Ablauf Kategorie → Budget → Fragen → Ergebnis, Aufpreis-Hinweis sichtbar).
2. Datenlücken schließen (Laptop Windows, Smartphone-/Tablet-Preise, Saugroboter, Kopfhörer-Abdeckung) – Subagenten, je Shop ≤ 1 Abruf/min, Saturn bevorzugt.
3. Automatik: Workflow `finder-daten.yml` (bei Änderung `daten/**`: prüfen, bauen, nur `finder-daten.json` auf gh-pages), Entdeckungslauf wöchentlich (D10), Preislauf (nach Pilot), Claude-Routine (D11, Skill `schedule`).
4. Prüfpunkt Veröffentlichung (kritisch): Codex-Prüfung (`pruefschleife`), dann `veroeffentlichen.py`, `pruefe.mjs --url`.
