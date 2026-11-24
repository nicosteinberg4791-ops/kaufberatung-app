# Nachprüfauftrag r3: Finder-Abgleich, Korrekturen zu Codex r2 (schmal, letzte Runde nach KERN §3)

**Ziel:** Prüfen, ob A2-01, R2-02 und R2-03 aus r2 geschlossen sind.

**Prüfgegenstand:** nur der Diff `-Basis` (17599c1) bis HEAD. Bewertung: `bewertung-r2.md`.

**Entscheidung des Besitzers (23.11.2026):** A1-01 und R2-01 (fremder lokaler Prozess tauscht Verzeichniseinträge gegen Link/Junction) sind als Restrisiko angenommen und nicht Gegenstand dieser Runde. R2-04 (`gesperrt_bis`) liegt außerhalb des Umfangs.

**Fertigkriterien:**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“
- A2-01: In `sperre_holen` heißt nur `FileNotFoundError` von `os.lstat` „kein Stempel“; jeder andere `OSError` ergibt genau `ABSTAND`.
- R2-02: `mkdtemp` liegt im geschützten Block; bleibt das eigene Bauverzeichnis nach einem Abbruch stehen, wird es auf stderr gemeldet.
- R2-03: Scheitert `os.rename` nach `os.rmdir` des zuvor leeren Ziels, ist das Ziel danach wieder ein leeres Verzeichnis.

**Betroffene Dateien:** `werkzeuge/datenpflege/abruf.py` `sperre_holen` Z. 88–105 · `werkzeuge/app_bauen.py` `baue()` Z. 141–165 · `tests/test_abruf.py` `test_fehler_beim_pruefen_des_stempels_heisst_voller_abstand` · `tests/test_app.py` `BauZiel.test_gescheitertes_umbenennen_laesst_das_leere_ziel`, `BauZiel.test_rest_des_bauverzeichnisses_wird_gemeldet`

**Selbstprüfung:** Die drei neuen Tests rot mit dem Stand 17599c1, grün mit der Korrektur; Sammellauf und Datenbank 0 Fehler; `core.bare` false.

**Prüffragen:**
1. Gibt es in `sperre_holen` noch einen Weg, auf dem ein vorhandener, aber nicht prüfbarer Stempel ohne Wartezeit durchgeht?
2. Kann die Wiederherstellung in R2-03 oder das Aufräumen in R2-02 fremde Daten löschen oder überschreiben (außerhalb des angenommenen Restrisikos)?
