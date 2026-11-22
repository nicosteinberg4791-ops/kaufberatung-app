# Prüfauftrag: Finder „Finden & Vergleichen“, Nachprüfung r2 (kritisch)

**Ziel:** Prüfen, ob die Korrekturen zu F-01…F-13 (Commit c4360f1) die Befunde aus r1 wirklich schließen und keine neuen Fehler einführen; danach soll nur gh-pages veröffentlicht werden (`main` folgt später).

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“.
- Jeder r1-Befund ist geschlossen; die Einordnung in `bewertung-r1.md` (F-02 Fehlalarm mit Beleg) ist nachvollziehbar.
- `veroeffentlichen.py --stand <Commit>` pusht nur einen sauberen, geprüften Stand nach gh-pages, ohne Erzwingen, ohne neuere `finder-daten.json` zu ersetzen, und berührt `main` nicht.
- Die Kriterien des Erstauftrags (`auftrag.md`) gelten weiter.

**Prüfgegenstand:** Diff `-Basis` (aa03841) bis HEAD, ohne `daten/produkte/*.json`. Schwerpunkt: `werkzeuge/{datenbank,entdeckung,veroeffentlichen,app_bauen}.py`, `werkzeuge/datenpflege/{abruf,routine}.py`, `app/finder/{bewertung,finder}.js`, `app/sw.js`, `.github/workflows/finder-daten.yml` und die zugehörigen Tests (`tests/test_{abruf,datenbank,entdeckung,app}.py`, `tests/test_{bewertung,finder_dom,sw_daten}.mjs`).

**Selbstprüfung:** Je Befund Test rot gegen alten Stand, grün danach. Sammellauf Fehler 0; `datenbank.py pruefen` 301 Modelle/389 Varianten, Fehler 0; `pruefe.mjs` lokal: 14 Kacheln, offline ok, nur erwartete 503 für lokal fehlendes `preise.json`.

**Bekannte Grenzen:** F-02-Abnahmeschritt in `finder-daten.yml` nicht live gelaufen (Workflow läuft erst auf main). `RoutineGit`-Tests entfernen `GIT_*`-Umgebungsvariablen (vorher beschädigte ein Commit-Hook den Index). Abgleich der Entdeckung: Modellname, der alle Wörter eines Bestandsmodells enthält, gilt als bekannt. `shopabfrage.py` bewusst unverändert (Pilot).

**Prüffragen**
1. Lassen sich die neuen Sperren umgehen (Routine: Commitkette, Merge, Umbenennen, paralleler Commit; Entdeckung: Laufsperre, verwaiste Sperre, unlesbarer Zeitstempel; Veröffentlichung: unsauberer Baum, falscher `--stand`)?
2. Wertet die robots.txt-Auswertung (RFC 9309, Agent-Gruppe, `*`/`$`, Gleichstand) in einem Fall zu großzügig aus?
3. Kann ein Datenwert trotz `datenPruefen` (Seite und Service Worker) als HTML/CSS wirken oder die Seite brechen; ist `ohne_note` überall sauber behandelt?
4. Lässt die Domain-Positivliste in `datenbank.py` über Schreibweisen (Großbuchstaben, Punkt am Ende, IDN, Subdomain) etwas Unfreigegebenes durch?
5. Steht im Diff etwas, das im öffentlichen Repo nicht stehen darf?
