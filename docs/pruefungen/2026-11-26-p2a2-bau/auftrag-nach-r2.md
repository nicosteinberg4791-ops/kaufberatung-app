# Nachprüfung r2 – P2a-2 Korrektur r2 (offen: P2A2-BAU-04, -02, -03, -06)

**Ziel:** Prüfen, ob die Korrekturen r2 die vier offenen Befunde der Nachprüfung r1 je Klasse schließen. Nur diese vier, keine Vollprüfung, keine erneute Prüfung von BAU-01/05.

**Fertigkriterien:**
1. `python -I docs/pruefungen/2026-11-26-p2a2-bau/mutanten.py <projektordner>` → Original grün, jede Mutante rot (Abschnitt „Korrektur r2“), danach sauber.
2. Je Befund: Korrektur und Probe wie in `bewertung-r2.md`, Spalten „Korrektur“ und „Probe“.

**Korrekturstellen (Diff ab 275e635):** `werkzeuge/freigabe.py` `bau_aus_commit`, Anfang von `daten_push` · `werkzeuge/datenbank.py` `fassung_gegen_fehler` (Altschema, Reihenfolge vor `projektion`), Anfang von `schema_fehler` · `tests/test_freigabe.py` `Repos.__init__`, `Repos.bau`, `test_datei_an_kandidat_gebunden` · `tests/test_datenbank.py` `test_referenz_gerundet_und_ohne_projektion`, `test_abschlag_isoliert` · `tests/test_bewertung.mjs` `ALTFALL_B24C18F`, `vergleich37`, zweiter Fall von Test 37 · `mutanten.py` Abschnitt r2.

**Selbstprüfung:** `bewertung-r2.md`, Abschnitt „Selbstprüfung“.

**Bekannte Grenzen:** Der Nachbau in `daten_push` nutzt denselben Python-Interpreter wie der Workflow-Bau; abweichende Interpreter zwischen Bau- und Pushschritt sind nicht Teil des Befunds. Test 37 läuft weiter offline gegen den lokalen Ref `origin/gh-pages` (bewusste Entscheidung r1).

**Prüffragen (Klassenfragen):**
1. BAU-04: Kann `daten_push` noch Bytes veröffentlichen, die nicht genau dem Bau aus dem Commit `neu` gleichen (z. B. über Arbeitsbaum, Dateimodus, Pfade außerhalb `daten/`/`werkzeuge/`, die der Bau liest)?
2. BAU-02: Hängt Test 37 noch an einer Annahme über Anzahl oder Inhalt der Fassungen im Seitenverlauf außer dem dokumentierten Altfall?
3. BAU-03: Gilt irgendwo noch eine nicht ganzzahlige oder gerundete Versionsangabe als gültig, oder läuft `projektion` vor der Prüfung der Referenzfassung?
4. BAU-06: Bleibt ein Bestandteil der Projektion aus §9.3 bei seiner isolierten Änderung grün?
