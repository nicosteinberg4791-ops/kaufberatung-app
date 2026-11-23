# Prüfauftrag: Finder-Veröffentlichung, Nachprüfung r10 (schmal)

**Ziel:** Prüfen, ob R9-01 und R9-02 geschlossen sind und ihre Korrekturen nichts Neues brechen. Danach wird nur gh-pages veröffentlicht (O14).

**Umfang (schmal, Besitzerentscheid O20):** nur der Diff `-Basis` (4d88574, Bewertungscommit r9) bis HEAD: die Korrekturen zu R9-01 und R9-02 mit Tests sowie die Testkorrektur aus 9175869 (Eigenbefund `core.bare`, `bewertung-r9.md`). Kein erneuter Gesamtblick; frühere Runden gelten als abgeschlossen. R5-01, R5-05, R6-02 (`abruf.py`) sind ausgegliedert (O17), nicht melden.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“.
- R9-01: `windows_pfad_fehler` lehnt jede Pfadkomponente über 255 UTF-16-Codeeinheiten vor dem ersten Schreiben ab.
- R9-02: `windows_pfad_fehler` lehnt jede Komponente mit möglichem 8.3-Kurznamen (`~` und Ziffer) vor dem ersten Schreiben ab.
- `test_laufzeitkonfiguration_bleibt` läuft ohne geerbte `GIT_*`-Variablen und ändert die Konfiguration des aufrufenden Repos nicht.

**Prüfgegenstand:** `werkzeuge/veroeffentlichen.py` (`KURZNAME`, `windows_pfad_fehler`), `tests/test_app.py` (`test_windows_pfade_vor_dem_schreiben`, `test_laufzeitkonfiguration_bleibt`).

**Selbstprüfung:** Neue Fälle vor der Korrektur rot, danach grün; Sammellauf, Datenbank, Bau, `--trocken` gegen gh-pages: `bewertung-r9.md` (Behebung).

**Bekannte Grenzen:** Die Windows-Regeln sind absichtlich streng und können nur abbrechen, nie veröffentlichen. Gesamtpfadlänge (MAX_PATH) wird nicht vorab geprüft; ein Schreibfehler in der Wegwerf-Kopie bricht ab. Die Tests prüfen das Verhalten auf NTFS mit aktiver 8.3-Vergabe (Rechner des Besitzers).

**Prüffragen**
1. Gibt es eine Pfadkomponente, die unter Windows auf dieselbe Datei wie eine andere zeigt oder nicht anlegbar ist und `windows_pfad_fehler` trotzdem passiert?
2. Zählt die Längenprüfung genau wie NTFS (UTF-16-Codeeinheiten je Komponente)?
3. Kann ein Test im Commit-Hook noch die Konfiguration des echten Repos ändern?
