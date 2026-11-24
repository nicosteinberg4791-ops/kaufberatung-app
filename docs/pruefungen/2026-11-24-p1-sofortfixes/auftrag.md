# Prüfauftrag P1 Sofortfixes Finder (Erstprüfung, Codex medium)

**Ziel:** Prüfen, ob die P1-Sofortfixes des Finders (Entscheidungen D12–D24, `docs/entscheidungen.md`) korrekt, sicher und ohne Rückschritt umgesetzt sind.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → `Fehler: 0`
- `node --test tests/test_bewertung.mjs tests/test_finder_dom.mjs tests/test_sw_daten.mjs` → 0 fail
- `python -I werkzeuge/datenbank.py pruefen` → `Fehler 0`
- Bewertung ohne Klassen und Kappung: ältere Daten mit `klassen`/`kappung` werden ignoriert, nicht abgelehnt (D12).
- Gleiche angezeigte Note → gleicher Rang, günstigeres Modell zuerst; ohne Note eigene Gruppe „Noch nicht bewertbar (n)“ ohne Rang, mit „fehlt: …“.
- Empfehlung („Passt am besten zu dir“) nur für Modelle mit Preis, auch bei Budget „egal“.
- Spar-Hinweis zeigt nie „X statt X“ (bei gleicher Zahl `text_gleichauf`).
- Fremde Daten (Produktdaten, Preise, Adresse/Hash) nur als Text ausgegeben, Links nur https mit `noopener noreferrer`.

**Betroffene Dateien** (Diff ab `-Basis`): `app/finder/bewertung.js` (v. a. Z. 107–300), `app/finder/finder.js` (Ergebnisansicht, Ablage Z. 680–700), `app/finder/finder.css` (Ablage Z. 281–296), `app/finder/index.html`, `daten/schema/kategorien.json`, `werkzeuge/datenbank.py`, `docs/punkteschema.md`, `tests/test_bewertung.mjs`, `tests/test_finder_dom.mjs`, `tests/test_sw_daten.mjs`, `tests/vorlagen/finder-beispiel.json`. Datenänderungen unter `daten/produkte/` sind nur Preisnachträge (P6) und nicht Gegenstand, außer sie brechen die Bewertung.

**Selbstprüfung:** `test_bewertung.mjs` 33/33, `test_finder_dom.mjs` 17/17; Gegenprobe: neue Tests scheitern mit altem Code bzw. ohne CSS-Korrektur. `alle-tests.ps1` Fehler 0. Browser mobil 375 px hell/dunkel (Kopfhörer Over-Ear bis 350 €, Fernseher bis 700 € mit Ablage, Waschmaschine, Akku-Staubsauger); Bilder in `bilder/`. Dabei gefunden und behoben: Layoutklasse `.haupt` zog den Ablage-Knopf `knopf haupt` auf 100 % Breite.

**Bekannte Grenzen:** Kein Layouttest im Headless-Browser (nur statische CSS-Prüfung). Testlinks („Tests anderer“) haben noch keine Daten. Klassenname `.haupt` doppelt belegt (Layout und Knopf), nur in der Ablage entschärft.

**Prüffragen**
1. Kann eine Eingabe (Hash-Parameter, Preisdaten, alte Schemafelder) zu falscher Reihenfolge, falschem Rang oder einer Empfehlung ohne Preis führen?
2. Sind Gleichstand und Rangvergabe stabil (gleiche Note, gleicher Preis, fehlender Preis)?
3. Trifft die doppelt belegte Klasse `.haupt` weitere Knöpfe so, dass Layout bricht (andere Stellen als die Ablage)?
4. Fehlen Tests für eine der Fertigkriterien oben?
