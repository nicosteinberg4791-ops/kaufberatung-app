# Nachprüfung r2 – Preis-Push (nur Korrekturen aus r1)

**Ziel:** Die fünf Befunde aus r1 (`bewertung-r1.md`) sind am Code geschlossen, ohne neue Lücke derselben Klassen.

**Fertigkriterien:**
1. `python -I -B -m unittest discover -s tests -t tests -p test_app.py -k PreisPush -k PushSchutz -k Workflow` → OK (25 Tests).
2. -01/-05: Jeder Git-Aufruf in `preise_aktualisieren.py` läuft über `git_umgebung()`, also ohne Ersatzobjekte und Grafts und ohne geerbtes `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` oder Objektspeicher.
3. -02: `commit_fehler` vergleicht die Wurzeleinträge. Genau `preise.json` ändert sich, und zwar als Blob 100644/100755.
4. -03: Nachgezogen wird nur, wenn der Indexeintrag von `preise.json` gleich `eltern` ist und `HEAD` = `eltern`.
5. -04: Der Blob entsteht aus denselben Bytes wie das JSON (`--no-filters --stdin`, CRLF → LF). Ein Symlink oder ein nicht regulärer Eintrag führt zum Abbruch.

**Dateien:** Diff ab `-Basis` (`werkzeuge/preise_aktualisieren.py`: `git_umgebung`, `git_aus`, `git_lauf`, `preis_commit`, `commit_fehler`, Ende von `push`; `tests/test_app.py`: neue Tests in `PreisPush`).

**Selbstprüfung:** Kriterium 1 ist grün. Die Mutanten F bis J sind je einzeln rot (Tabelle in `bewertung-r1.md`). Der Gesamtlauf läuft im Commit-Hook.

**Bekannte Grenzen:** wie in r1 (Push von Hand, keine Commit-Hooks bei `commit-tree`, nicht in echtem Actions gelaufen). Die LF-Normalisierung ändert eine Datei mit CRLF absichtlich.

**Prüffragen:**
1. Hat eine der Korrekturen eine neue Lücke geöffnet (z. B. fehlen für Fetch oder Push in Actions jetzt Zugangsdaten, weil die Umgebung gefiltert ist; ist `ls-tree -z` beim Parsen robust)?
2. Gibt es in derselben Klasse noch eine Instanz (eine weitere Variable oder Konfiguration, die Objekte, Index oder Repository umlenkt, z. B. `core.worktree` in der Konfiguration oder `GIT_CONFIG_*`)?
3. Ist die Bedingung für das Nachziehen jetzt vollständig, sodass kein lokaler Stand verloren geht?
