# Nachprüfauftrag r2: Finder-Abgleich, Korrekturen zu Codex r1

**Ziel:** Prüfen, ob A1-01, A2-01, A2-02 und A2-03 aus r1 geschlossen sind, ohne neue Lücke derselben Klasse.

**Prüfgegenstand:** nur der Diff `-Basis` (8cb198d) bis HEAD. Bewertung: `bewertung-r1.md`.

**Fertigkriterien:**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“
- A1-01: `baue(ziel=…)` schreibt nur in ein exklusiv angelegtes Nachbarverzeichnis; das Ziel wird nur ersetzt, wenn es dann noch fehlt oder leer ist (`os.rmdir`, `os.rename`); sonst Abbruch ohne Rest und ohne Änderung im Ziel.
- A2-01: Ein vorhandener, nicht auflösbarer Stempel-Eintrag ergibt genau `ABSTAND`.
- A2-02/A2-03: Tests unabhängig von der Laufzeit seit Systemstart; Abbruchtest löst nach dem Öffnen (bei `fsync`) aus.

**Betroffene Dateien:** `werkzeuge/app_bauen.py` `baue()`/`_baue()` Z. 129–171 · `werkzeuge/datenpflege/abruf.py` Z. 91 · `tests/test_app.py` Klasse `BauZiel` · `tests/test_abruf.py` `test_zeitstempel_vor_dem_http_versuch`, `test_abbruch_beim_schreiben_laesst_den_alten_stempel`, `test_link_ohne_ziel_heisst_voller_abstand`

**Selbstprüfung:** Sammellauf 0 Fehler, Datenbank 0 Fehler, `core.bare` false. Mutanten rot: Fassung 8cb198d von `app_bauen.py` (BauZiel), `exists()` statt `lexists` (Junction-Test, lief unter Windows, nicht übersprungen), direktes Schreiben in den Stempel (Abbruchtest).

**Bekannte Grenzen:** `gesperrt_bis` (abruf.py Z. 150) prüft die Sperrdatei weiter mit `exists()`; gleiche Klasse, aber außerhalb A1–A3, an den Besitzer gemeldet. Unter POSIX ersetzt `os.rename` ein inzwischen neu angelegtes leeres Verzeichnis (nichts geht verloren). Das Bauverzeichnis hat unter POSIX Modus 0700.

**Prüffragen:**
1. Gibt es zwischen Leerprüfung, `os.rmdir` und `os.rename` einen Weg, auf dem Dateien im oder außerhalb des Ziels gelöscht oder überschrieben werden (Windows und POSIX, Links, Junctions)?
2. Bleibt bei jedem Abbruch (auch `BaseException`) kein Bauverzeichnis liegen, und kann das Aufräumen fremde Daten treffen?
3. Gibt es in `sperre_holen`/`holen` weitere Prüfungen, die einen vorhandenen, unlesbaren Stempel als „fehlend“ behandeln?
