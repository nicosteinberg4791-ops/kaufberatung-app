# Prüfauftrag Preis-Push (P2A2-05 nach O27, Erstprüfung am Code)

**Ziel:** `preise_aktualisieren.py --push/--nur-push` pusht auf gh-pages nur einen Commit, der aus dem Remote-Stand `eltern` gebaut ist, genau `preise.json` ändert und mit Lease auf `eltern` gepusht wird.

**Fertigkriterien:**
1. `python -I -B -m unittest discover -s tests -t tests -p test_app.py -k PreisPush -k PushSchutz -k Workflow` → OK (19 Tests).
2. 47(i): Ein lokaler Zusatzcommit (vor oder nach dem Abruf von `eltern`) und eine gestagte fremde Datei kommen nicht mit. Auf dem Remote liegt genau ein neuer Commit mit `eltern` als einzigem Elternteil, `diff-tree` = `preise.json`, `finder-daten.json` bytegleich.
3. 47(j): Eine eingeschleuste zweite Datei oder ein zweiter Elternteil → Abbruch, nichts gepusht.
4. 47(k): Ist der Remote weitergeschoben, auf einen Vorfahren zurückgesetzt oder gelöscht → Lease scheitert, kein Push, kein Zweig angelegt.
5. Actions (`preise.yml`, flacher Abruf, `--nur-push`): Nach einem fremden Push wird der Zweig nachgeholt, der Preiscommit baut auf dem neuen Stand auf. Am Workflow ist nichts geändert.

**Dateien:** `werkzeuge/preise_aktualisieren.py:213–295` (`git_lauf`, `eltern_holen`, `preis_commit`, `commit_fehler`, `push`), `tests/test_app.py:976–1220` (`PushSchutz`, neue Klasse `PreisPush`), Entwurf `docs/recherche-ux/p2-entwurf.md` §9.3 „Preis-Push“ (nur Bau-Vermerk). Gegenstand ist der Diff ab `-Basis`.

**Selbstprüfung:** Kriterium 1 ist grün. Gesamtlauf `tests/alle-tests.ps1` im Commit-Hook. Mutanten (je einzeln rot): Commit aus `HEAD` → 47(i) und flacher Klon; ohne `commit_fehler` → beide 47(j); Push ohne Lease → 47(k) Vorfahr und gelöscht; ohne Nachholen → flacher Klon; `eltern` = lokaler `HEAD` → 47(i) und flacher Klon. Die Vorprüfung (Sonnet medium, lesend) fand nichts Kritisches oder Schweres. Daraufhin korrigiert: Fehler beim Nachziehen nach dem Push brechen nicht mehr mit „nichts gepusht“ ab, die `ls-remote`-Zeile muss genau `refs/heads/gh-pages` sein, Meldungstext im Elternteil-Test, Zustand im Hinweisfall geprüft.

**Bekannte Grenzen:** Ein Push von Hand auf gh-pages umgeht den Mechanismus (Entwurf §7 R6). `commit-tree` startet keine Commit-Hooks (wie `veroeffentlichen.py`). In echtem Actions ist nichts gelaufen, getestet ist nur mit einem lokalen Bare-Repository und einem flachen `file://`-Klon. Der Preis-Push liest keine `herkunft` (bewusst, Entwurf §9.3 „Strikt“). Die frühere Ablehnung bei fremdem Index ist entfallen: Der Index geht nicht mehr in den Commit ein, das prüft der Test mit der gestagten fremden Datei. Ohne rote Seite sind 47(k) „weitergeschoben“ (scheitert auch ohne Lease an non-ff) und die genaue `ls-remote`-Zeile (Absicherung). Steht der lokale Zweig nicht auf `eltern`, bleibt `preise.json` dort als Änderung stehen.

**Prüffragen:**
1. Gibt es einen Weg, auf dem trotzdem etwas außer `preise.json` oder ein anderer Elternteil als der Remote-Stand auf gh-pages landet (Modi, Unterordner, Symlinks, `.gitattributes`/autocrlf bei `hash-object`, Umgebungsvariablen wie `GIT_DIR`/`GIT_INDEX_FILE`)?
2. Ist `eltern_holen` (ls-remote, Nachholen nur bei fehlendem Objekt, Gleichheitsprüfung) in Actions mit flachem Abruf und Credentials von `actions/checkout` tragfähig? Bleibt ein Lauf nach einem fremden Push dauerhaft rot?
3. Nachziehen des lokalen Zweigs (`update-ref` mit altem Wert, `reset -- preise.json`): Kann das einen lokalen Stand verlieren oder `veroeffentlichen.py` (sauberer Seitenbaum) blockieren?
4. Haben die Tests 47(i)–(k) eine echte rote Seite, oder bestehen sie auch über einen anderen Mechanismus als den, den sie benennen?
