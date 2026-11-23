# Prüfauftrag: Finder-Veröffentlichung, Nachprüfung r9 (schmal)

**Ziel:** Prüfen, ob R8-01, R8-02 und R8-03 geschlossen sind und ihre Korrekturen nichts Neues brechen. Danach wird nur gh-pages veröffentlicht (O14).

**Umfang (schmal, Besitzerentscheid O19):** nur der Diff `-Basis` (e7a30fa) bis HEAD, also die Korrekturen zu R8-01…R8-03 und ihre Tests. Kein erneuter Gesamtblick auf `veroeffentlichen.py`; frühere Runden gelten als abgeschlossen. R5-01, R5-05, R6-02 (`abruf.py`) sind ausgegliedert (O17), nicht melden.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“.
- R8-01: `herkunft.OHNE_ERSATZ` setzt nur `GIT_NO_REPLACE_OBJECTS` und `GIT_GRAFT_FILE`, vorhandene `GIT_CONFIG_*` bleiben erhalten.
- R8-02: Baumpfade mit Unicode-Klasse C (Cc, Cf, Cs, Co, Cn), Zl oder Zp brechen in `baum_eintraege` ab.
- R8-03: Unter Windows unzulässige oder nur in der Schreibweise verschiedene Pfade brechen in `kopie_holen` vor dem ersten Schreiben ab (`windows_pfad_fehler`).
- Im Diff steht nichts, was im öffentlichen Repo nicht stehen darf.

**Prüfgegenstand:** `werkzeuge/herkunft.py` (`OHNE_ERSATZ`), `werkzeuge/veroeffentlichen.py` (`baum_eintraege`, `GERAETE`, `windows_pfad_fehler`, `kopie_holen`), `tests/test_app.py` (`_stand_roh`, `test_pfade_unveraendert_und_ohne_steuerzeichen`, `test_windows_pfade_vor_dem_schreiben`, `test_laufzeitkonfiguration_bleibt`).

**Selbstprüfung:** Neue Tests vor der Korrektur rot, danach grün; Sammellauf, Datenbank, Bau, `--trocken` gegen gh-pages: `bewertung-r8.md` (Behebung).

**Bekannte Grenzen:** Der Graft-Hinweis von Git auf stderr bleibt bewusst (R8-01). Die Windows-Regeln sind absichtlich streng und können nur abbrechen, nie veröffentlichen. Überlange Pfade (MAX_PATH) werden nicht vorab geprüft (nicht nachgestellt); ein Schreibfehler in der Wegwerf-Kopie bricht ab.

**Prüffragen**
1. Überschreibt `OHNE_ERSATZ` noch eine Einstellung des Aufrufers, oder fehlt einem Git-Aufruf im Diff die Abschaltung?
2. Kann ein Pfad mit einem täuschenden Zeichen die neue Prüfung in `baum_eintraege` passieren?
3. Kann `kopie_holen` vor dem Abbruch noch etwas schreiben, oder kann ein unter Windows verändert geschriebener Pfad den Abgleich bestehen?
