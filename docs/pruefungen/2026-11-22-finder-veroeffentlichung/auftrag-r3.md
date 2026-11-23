# Prüfauftrag: Finder „Finden & Vergleichen“, Nachprüfung r3 (kritisch)

**Ziel:** Prüfen, ob Commit 73e2c6c die r2-Befunde R2-01…R2-09 schließt, ohne neue Fehler einzuführen; danach wird nur gh-pages veröffentlicht (`main` folgt später).

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“.
- Jeder r2-Befund ist geschlossen (Einordnung `bewertung-r2.md`); die Kriterien aus `auftrag.md` und `auftrag-r2.md` gelten weiter.
- `finder-daten.json` auf gh-pages wird weder von `veroeffentlichen.py` noch von `finder-daten.yml` durch einen Stand ersetzt, der die Online-Herkunft nicht enthält.

**Prüfgegenstand:** Diff `-Basis` (c4360f1) bis HEAD. Schwerpunkt: `werkzeuge/herkunft.py` (neu), `werkzeuge/{veroeffentlichen,datenbank,app_bauen,entdeckung}.py`, `werkzeuge/datenpflege/abruf.py` (`_norm`, `robots_erlaubt`), `.github/workflows/finder-daten.yml`, `app/finder/{bewertung,finder}.js` und die geänderten Tests.

**Selbstprüfung:** Jeder neue Test rot gegen c4360f1 (Wegwerf-Worktree: 9 Python-, 4 Node-Fehlschläge), grün auf 73e2c6c; Sammellauf Fehler 0/Warnungen 0; `datenbank.py pruefen` 301/389, Fehler 0, Warnungen 56; Geheimnis-Scan 0 Funde.

**Bekannte Grenzen:** `finder-daten.yml` nicht live gelaufen (läuft erst auf main). gh-pages hat heute keine `finder-daten.json`; erste Veröffentlichung kommt aus diesem Zweig, später gebaute main-Commits müssen ihn enthalten (Merge, kein Rebase), sonst bleibt der Datenworkflow rot (gewollt, nichts wird zurückgesetzt). Dateisperre: `msvcrt.locking` (Windows) bzw. `fcntl.flock`; nur gegen Läufe auf demselben Rechner.

**Prüffragen**
1. Lässt sich die Herkunftsprüfung umgehen (Groß-/Kleinschreibung, kurzer SHA, unbekanntes Objekt, Online-Datei kein Objekt, Fehler von `git merge-base`, Schrittreihenfolge im Workflow inkl. `bash -e`)?
2. Kann die erste Veröffentlichung oder ein späterer main-Lauf dadurch dauerhaft blockieren, ohne dass es auffällt?
3. Ist `_norm` für Pfad und Regel wirklich gleich (Prozent-Kleinbuchstaben, `%25`, unvollständiges `%`, Nicht-ASCII, `*`/`$`)?
4. Hält die neue Laufsperre in jedem Pfad genau einen Inhaber und wird sie immer freigegeben?
5. Steht im Diff etwas, das im öffentlichen Repo nicht stehen darf?
