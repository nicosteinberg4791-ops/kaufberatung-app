# Prüfauftrag: Finder „Finden & Vergleichen“, Nachprüfung r6 (kritisch)

**Ziel:** Prüfen, ob der eingefrorene Stand die r5-Befunde R5-01…R5-05 schließt, ohne neue Fehler einzuführen; danach wird nur gh-pages veröffentlicht (`main` folgt später, O14). Runde 6 vom Besitzer beauftragt (O16).

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“.
- Jeder r5-Befund ist geschlossen (Einordnung `bewertung-r5.md`); die Kriterien aus `auftrag.md` und `auftrag-r2.md` bis `auftrag-r5.md` gelten weiter.
- `veroeffentlichen.py` baut aus einer Kopie genau des geprüften Commits, vergleicht Modus, Typ und Objekt-ID jedes Baumeintrags und pusht nur, wenn gh-pages noch genau der geprüfte Elterncommit ist.

**Prüfgegenstand:** Diff `-Basis` (ae72e55) bis HEAD. Schwerpunkt: `werkzeuge/veroeffentlichen.py` (`bau_erwartet`, `baum_eintraege`, `baum_fehler`, `kopie_holen`, `app_bau_starten`, `baue_aus_stand`, Push in `main`), `werkzeuge/app_bauen.py` (`main`: `--ziel`, `--herkunft`), `werkzeuge/datenpflege/abruf.py` (`letzter_abruf`, `stempel_schreiben`, `robots_ursprung`, `robots_text`, `robots_ok`) und die geänderten Tests (`tests/test_app.py` Klasse `Veroeffentlichen`, `tests/test_abruf.py`). 594cd3f und dafc6eb ändern nur Dokumentation.

**Selbstprüfung:** Jeder neue Test rot vor der Korrektur und danach grün (R5-01: Abbruch beim Endstempel, leerer/unlesbarer/zukünftiger Stempel; R5-02: Moduswechsel auf 120000 bei gleicher Blob-ID vor `write-tree`; R5-03: gh-pages vor dem Push zurückgesetzt bzw. gelöscht; R5-04: Arbeitsbaumänderung während des Baus, `kopie_holen`; R5-05: Port 8443, http gegen https). Sammellauf, `datenbank.py pruefen`, Bau, `pruefe.mjs` lokal und `veroeffentlichen.py --trocken` gegen das echte gh-pages: Ergebnisse im Commit-Text.

**Bekannte Grenzen:** Der Lease schützt vor einem fremden Stand auf GitHub zwischen Abruf und Push, nicht vor Eingriffen mit Schreibrecht danach. `git archive` liefert den Commitinhalt ohne Untermodule (das Projekt hat keine). Dateisperren und Zeitstempel nur gegen Läufe auf demselben Rechner. `finder-daten.yml` nicht live gelaufen (läuft erst auf main).

**Prüffragen**
1. Kann noch irgendein Inhalt in den gepushten Seitencommit gelangen, der nicht aus dem geprüften Commit gebaut und mit Modus, Typ und ID verglichen wurde (Kopie, Bauprozess, Index, Elterncommit, Push-Ziel)?
2. Ist der Bau aus `git archive` mit dem Bauskript der Kopie gleichwertig zum bisherigen Bau (gleiche Dateien, gleiche Zeilenenden, Herkunft in `finder-daten.json`)?
3. Gilt der Mindestabstand je Domain jetzt in jedem Abbruch- und Lesepfad des Stempels?
4. Bindet `robots_ok` Regeln und Ablage in jedem Fall an Schema, Host und effektiven Port (IPv6, Standardport ausdrücklich, ungültiger Port)?
5. Steht im Diff etwas, das im öffentlichen Repo nicht stehen darf?
