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

- O11 Impeccable-Installation (`npx impeccable install --scope=project --providers=claude --no-hooks`, Telemetrie aus) von der automatischen Freigabe abgelehnt → Besitzer gibt frei oder entfällt mit Grund.
- O12 `listenpreis` ins Format aufnehmen (Preisstufe ohne Lieferbarkeit) oder streichen → Lead.
- O13 `update_jahre`: EU-Mindestwert oder Herstellerzusage → Besitzer.
- Pilot-Preisabruf (O9) wird in der Pilot-Sitzung nach Codex-R1 „nicht bestanden“ korrigiert; tägliche Finder-Preise hängen davon ab.

## Nächste Schritte (in dieser Reihenfolge)

1. **Einbau in den App-Bau:** `werkzeuge/app_bauen.py` baut `index.html` aus `app/finder/index.html` (+ Manifest, Icons, Service-Worker-Anmeldung, Weiterleitung `#besitzer…`/`#preiswecker` → `ratgeber.html`), den Artifact-Inhalt als `ratgeber.html`, `finder-daten.json` über `datenbank.py bauen`; `sw.js`: Navigation je Pfad (`index`/`ratgeber`), `finder-daten.json` und `finder-preise.json` netz-zuerst, Benachrichtigungsziel `./#preiswecker` → `ratgeber.html#preiswecker`; `tests/alle-tests.ps1` um `node --test` ergänzen; `veroeffentlichen.py` prüfen. Fertig, wenn Bau + alle Tests grün und `preview_start` „kb-app“ den Finder mit echten Daten zeigt (360 px, hell/dunkel, Ablauf Kategorie → Budget → Fragen → Ergebnis, Aufpreis-Hinweis sichtbar).
2. Datenlücken schließen (Laptop Windows, Smartphone-/Tablet-Preise, Saugroboter, Kopfhörer-Abdeckung) – Subagenten, je Shop ≤ 1 Abruf/min, Saturn bevorzugt.
3. Automatik: Workflow `finder-daten.yml` (bei Änderung `daten/**`: prüfen, bauen, nur `finder-daten.json` auf gh-pages), Entdeckungslauf wöchentlich (D10), Preislauf (nach Pilot), Claude-Routine (D11, Skill `schedule`).
4. Prüfpunkt Veröffentlichung (kritisch): Codex-Prüfung (`pruefschleife`), dann `veroeffentlichen.py`, `pruefe.mjs --url`.
