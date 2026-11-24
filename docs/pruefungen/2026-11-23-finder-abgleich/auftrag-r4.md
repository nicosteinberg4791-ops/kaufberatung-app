# Nachprüfauftrag r4: Finder-Abgleich, nur A2-01 (schmal, vom Besitzer über das Rundenlimit hinaus beauftragt)

**Ziel:** Prüfen, ob A2-01 aus r3 geschlossen ist.

**Prüfgegenstand:** nur der Diff `-Basis` (0087589) bis HEAD. Bewertung: `bewertung-r3.md`.

**Entscheidung des Besitzers (O21, 24.11.2026):** A2-01 beheben, Runde 4 nur dafür. R2-02 und R2-03 (Unterbrechungsfenster/Doppelfehler beim Bau, nur eigene bzw. leere Verzeichnisse) sind als Restrisiko angenommen und nicht Gegenstand dieser Runde, ebenso A1-01/R2-01. R2-04 (`gesperrt_bis`) liegt außerhalb des Umfangs.

**Fertigkriterien:**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“
- A2-01: In `sperre_holen` heißt nur `FileNotFoundError` von `os.lstat` „kein Stempel“ (keine Wartezeit); jeder andere `OSError` ergibt genau einmal `ABSTAND`, ohne den Stempel zu lesen; nur nach erfolgreichem `lstat` entscheidet der Stempelinhalt.

**Betroffene Dateien:** `werkzeuge/datenpflege/abruf.py` `sperre_holen` Z. 88–110 · `tests/test_abruf.py` `test_fehler_beim_pruefen_liest_auch_einen_gueltigen_stempel_nicht` (Z. 282)

**Selbstprüfung:** Neuer Test rot ohne Korrektur (3 Unterfälle `PermissionError`, `OSError(5)`, `NotADirectoryError`: Wartezeit [] statt [ABSTAND]), grün mit Korrektur; Gegenprobe ohne Fehler wartet nicht. Sammellauf „Fehler: 0“, Datenbank „Fehler 0“, `core.bare` false.

**Prüffragen:**
1. Gibt es in `sperre_holen` noch einen Weg, auf dem ein vorhandener, aber nicht prüfbarer Stempel ohne volle Wartezeit durchgeht?
2. Kann ein Fehler im neuen Ablauf die Sperre halten oder ohne Freigabe verlassen?
