# Prüfauftrag: Finder-Veröffentlichung, Nachprüfung r8 (kritisch, geschnittenes Paket)

**Ziel:** Prüfen, ob R7-01, R7-02 und R7-03 geschlossen sind, ohne neue Fehler einzuführen. Danach wird nur gh-pages veröffentlicht (O14).

**Umfang:** nur `werkzeuge/veroeffentlichen.py`, `werkzeuge/herkunft.py` (nur `git_vorfahr`) und die Klassen `Veroeffentlichen` und `Herkunft` in `tests/test_app.py`. R5-01, R5-05 und R6-02 (`werkzeuge/datenpflege/abruf.py`) sind in ein eigenes Paket ausgegliedert (O17). Sie gehören nicht zu dieser Runde und sind nicht erneut zu melden.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“.
- R7-01…R7-03 geschlossen (Einordnung und Behebung: `bewertung-r7.md`). Die Kriterien aus `auftrag-r7.md` gelten weiter.
- Kein Git-Aufruf der Veröffentlichung und der Herkunftsprüfung folgt lokalen Ersetzungsreferenzen oder Grafts. Die Bauquelle hat nur 100644-Dateien. Baumpfade kommen unverändert an, Steuerzeichen brechen ab.

**Prüfgegenstand:** Diff `-Basis` (4cb0f2b) bis HEAD: `umgebung`, `git`, `baum_eintraege`, `soll_baum`, `objekte_lesen`, `kopie_holen`, `app_bau_starten`, `herkunft.git_vorfahr`, dazu die neuen Tests, `_stand_mit`, `_ersetzt` und `_lauf(vorher=...)`. 4cb0f2b ändert gegenüber ae56dbe (Stand r7) nur Dokumentation.

**Selbstprüfung:** Neue Tests vor der Korrektur rot, danach grün. Sammellauf, `datenbank.py pruefen`, Bau und `--trocken` gegen das echte gh-pages: Ergebnisse in `bewertung-r7.md` (Behebung).

**Bekannte Grenzen:** wie `auftrag-r7.md`. Grafts (`.git/info/grafts`) wirken trotz `GIT_NO_REPLACE_OBJECTS` weiter; deshalb zusätzlich `GIT_GRAFT_FILE` = Nullgerät. Ein flacher Klon (`.git/shallow`) kann Elterncommits nur verbergen: Die Herkunftsprüfung bricht dann ab, sie lässt nichts zusätzlich durch. Der Lease schützt nur zwischen Abruf und Push.

**Prüffragen**
1. Gibt es im Lauf noch einen Git-Aufruf oder Kindprozess ohne `OHNE_ERSATZ` (`GIT_NO_REPLACE_OBJECTS`, `GIT_GRAFT_FILE`), dessen Ergebnis in Bau, Prüfung, Commit oder Push eingeht?
2. Kann ein Pfad aus `ls-tree` verändert ankommen oder anders verglichen werden als er im Baum steht (Kodierung, Steuerzeichen, Umlaute)?
3. Bricht `kopie_holen` bei jedem Eintrag ab, der nicht als gleichwertige normale Datei geschrieben werden kann?
4. Steht im Diff etwas, das im öffentlichen Repo nicht stehen darf?
