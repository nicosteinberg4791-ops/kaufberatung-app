# Nachprüfung r1 – P2a-2 Korrektur (Befunde P2A2-BAU-01 … 06)

**Ziel:** Prüfen, ob die Korrekturen zu den sechs Befunden der Erstprüfung (Bewertung `bewertung-r1.md`) die jeweilige Klasse schließen, ohne neue Lücken zu öffnen. Keine Vollprüfung.

**Fertigkriterien:**
1. `powershell -File tests/alle-tests.ps1` → Fehler 0.
2. `python -I docs/pruefungen/2026-11-26-p2a2-bau/mutanten.py <projektordner>` → Original grün, jede Mutante rot (auch die acht r1-Mutanten), Arbeitsbaum danach sauber.
3. Je Befund: Korrektur und Probe wie in `bewertung-r1.md`, Spalten „Korrektur“ und „Probe“.

**Korrekturstellen (Stand HEAD):** `werkzeuge/datenbank.py` `_endlich_float`, `_endlich_int`, `json_streng`, `schema_laden`, `pruefe_datei` (Lader), `fassung_gegen_fehler`, Ende von `bauen` · `werkzeuge/freigabe.py` `referenz`, Anfang von `daten_push` · `tests/test_datenbank.py` `Gewichtsfassung`: `test_referenz_schema_1`, `test_referenz_fassung_explizit_ungueltig`, `test_entfernte_kategorie`, `test_nur_endliche_zahlen` · `tests/test_freigabe.py` `test_datei_an_kandidat_gebunden` · `tests/test_bewertung.mjs` `vergleich37` und beide Fälle von Test 37 · `docs/pruefungen/2026-11-26-p2a2-bau/mutanten.py` (Abschnitt r1) · `docs/recherche-ux/p2-entwurf.md` §9.3 (drei neue Punkte).

**Selbstprüfung:** siehe `bewertung-r1.md`, Abschnitt „Selbstprüfung“.

**Bekannte Grenzen:** Test 37 läuft offline gegen den lokalen Ref `origin/gh-pages` und gibt den verwendeten Seiten-SHA aus (bewusste Entscheidung in BAU-02). Das Entfernen einer Kategorie ist jetzt in der Schranke gesperrt; ein Freigabeweg dafür ist nicht gebaut. Ganze Zahlen über 2^53 (Genauigkeit im Client) sind nicht Teil von BAU-01.

**Prüffragen (Klassenfragen):**
1. BAU-01: Gibt es noch einen Weg, auf dem eine nicht endliche oder vom Client anders gelesene Zahl ins Schema, in die Produktdaten oder in die gebaute Datei kommt?
2. BAU-02: Hängt Test 37 noch an einer Annahme über den Live-Stand, die eine eigene Veröffentlichung brechen kann?
3. BAU-03/05: Kann eine Referenz mit ungültiger, fehlender oder entfernter Fassung noch als Erstfassung oder als unbedenklich durchgehen?
4. BAU-04: Kann `daten_push` nach bestandener Prüfung andere Bytes veröffentlichen als die an den Kandidaten gebundenen?
5. BAU-06: Bleibt eine Regel aus §9.3 bei einer naheliegenden Mutante grün?
