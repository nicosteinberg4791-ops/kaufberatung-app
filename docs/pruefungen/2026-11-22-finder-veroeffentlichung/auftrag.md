# Prüfauftrag: Finder „Finden & Vergleichen“ vor Veröffentlichung (kritisch), Erstprüfung

**Ziel:** Prüfen, ob Finder-Hülle, Produktdatenbank-Schranke, Entdeckung (D10) und Datenpflege-Routine (D11) gefahrlos öffentlich auf `main`/GitHub Pages gehen können.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“.
- Finder zeigt nur Daten aus `finder-daten.json`/`finder-preise.json`, alle fremden Werte nur als Text (kein innerHTML mit Daten); alte Sprungmarken/Benachrichtigungen landen in `ratgeber.html`.
- `sw.js`: Navigation je Seite, `finder-*.json` netz-zuerst, keine veraltete Seite nach neuer Fassung.
- `datenbank.py pruefen` lehnt unbelegte Werte, unbekannte Schlüssel, Preise nicht freigegebener Domains (`automatisch: false`) ab.
- `entdeckung.py`: je Kategorie ≤ 3 Saturn-Listenseiten, höchstens alle 6 Tage, alle Abrufe über `abruf.py` (Takt ≥ 61 s, robots.txt, 403/429 → Abbruch, nie umgangen); speichert nur Name/URL/Saturn-Nr. in `%TEMP%/kb-datenpflege/entdeckung/` (nie im Repo).
- `routine.py pruefen --pushen` pusht nur, wenn: Baum sauber, HEAD auf origin/main, nur `daten/produkte/*.json` geändert, keine Modell-/Varianten-ID verloren, Datenbank und Tests grün; kein Force-Push.
- `finder-daten.yml`: Schranke vor Bau, nur `finder-daten.json` auf gh-pages, Rechte minimal.
- Öffentliches Repo: keine persönlichen Daten, lokalen Pfade, Konto-URLs, kopierten Shoptexte.

**Prüfgegenstand:** Diff `-Basis` bis HEAD, ohne `daten/produkte/*.json` und `tests/vorlagen/finder-beispiel.json` (Daten: nur Stichprobe über die Schranke). Schwerpunkt: `app/finder/*.js`, `app/sw.js`, `app/app.js`, `werkzeuge/{app_bauen,datenbank,entdeckung,veroeffentlichen}.py`, `werkzeuge/datenpflege/{abruf,routine}.py`, `.github/workflows/finder-daten.yml`, `tests/test_{datenbank,entdeckung,app}.py`, `tests/test_finder_*.mjs`, `tests/test_bewertung.mjs`.

**Selbstprüfung:** Sammellauf Fehler 0/Warnungen 0; datenbank.py 301 Modelle, 389 Varianten, Fehler 0, Warnungen 56; `pruefe.mjs` lokal ohne Meldungen (Schritt 1); Schranke in Wegwerfklon: grün mit neuem Modell (Push auf Test-Origin), rot bei gelöschtem Modell/Variante, `vorbereiten` bricht bei Resten und ungepushten Commits ab; Entdeckung live gelaufen (je Kategorie 36 Einträge, 20–30 Kandidaten, keine Sperre). Vorprüfung (Sonnet): 11 Befunde, behoben in 1b1581f: 1, 3–7, 9, 10.

**Bekannte Grenzen:** Rechtliche Einstufung (§ 87b UrhG, D10) ist Recherchestand. Routine (geplante Aufgabe Claude Desktop, pausiert bis Livegang) läuft nur bei eingeschaltetem Rechner; Kuratieren der Kandidaten macht das Modell nach ANLEITUNG.md, die Schranke prüft Format und Belegpflicht, nicht die inhaltliche Richtigkeit. Abgleich nach Namen kann Länder-MPN-Varianten als bekannt einstufen (gewollt) und Modelle mit sehr kurzen Namen verfehlen. `preise_aktualisieren.py push` ohne Wiederholung bei gh-pages-Konflikt. Offen aus Vorprüfung: `veroeffentlichen.py` prüft Stand gegen origin/main nicht (2), robots.txt-Ablage ohne Ablauf und ohne Wildcards (8), Klassengrenzen in finder.js ungeprüft in style (11).

**Prüffragen**
1. Kann ein Wert aus Daten/Netz im Finder als HTML/Script wirken oder die Seite brechen?
2. Kann die Routine trotz Schranke etwas löschen, Code ändern oder rot pushen (Reihenfolge, Umgehung über Umbenennen, Leer-Diff, kaputtes JSON)?
3. Hält die Entdeckung die D10-Grenzen in jedem Pfad ein (Fehler, Teilergebnis, mehrfacher Aufruf, `--kategorie`)?
4. Ist der Service-Worker-Wechsel (alte App → Finder als Startseite) für installierte Nutzer sicher?
5. Steht etwas im Diff, das im öffentlichen Repo nicht stehen darf?
