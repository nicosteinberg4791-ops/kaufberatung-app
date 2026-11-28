# Prüfauftrag: Veröffentlichung `main` → origin/main und gh-pages (kritisch), Erstprüfung

**Ziel:** Prüfen, ob der Stand `main` (Merge a01e7fa plus Folgecommit) gefahrlos auf das öffentliche origin/main und per `veroeffentlichen.py` auf GitHub Pages gehen kann. Live ist Herkunft 7339711.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I werkzeuge/datenbank.py pruefen --gegen` → „Fehler 0“ gegen das Schema an der Live-Herkunft.
- Merge-Auflösung `tests/test_app.py` (`_lauf`, ca. Z. 330–365) und `STATUS.md` verliert keine Seite: P2a-Schema-Aufbau von `main` und UTF-8-Probe „geprüft“ von origin/main sind beide wirksam.
- Veröffentlichungsweg: `werkzeuge/veroeffentlichen.py` ruft die Freigabeschranke (`werkzeuge/freigabe.py`) vor dem Bau auf; `.github/workflows/finder-daten.yml` prüft vor dem Daten-Push mit Lease; `werkzeuge/preise_aktualisieren.py` pusht nur `preise.json`/`finder-preise.json` an das feste Ziel.
- Der Client (`app/finder/*.js`) gibt fremde Werte (finder-daten.json, finder-preise.json, localStorage) nur als Text aus; keine Laufzeitfehler bei Daten mit Schema 1 (live) und Schema 2 (neu).
- Öffentliches Repo: keine Zugangsdaten, persönlichen Daten, lokalen Pfade oder Konto-URLs im Diff (AGENTS.md, harte Regeln).

**Prüfgegenstand:** Diff `-Basis` 7339711 bis HEAD ohne `daten/produkte/*.json` (nur über die Schranke) und ohne Prüfberichte `docs/pruefungen/**` (nur auf persönliche Daten). Schwerpunkt: `werkzeuge/{veroeffentlichen,freigabe,datenbank,preise_aktualisieren}.py`, `werkzeuge/datenpflege/abruf.py`, `.github/workflows/finder-daten.yml`, `app/finder/{finder,bewertung}.js`, `daten/schema/kategorien.json`, `.claude/settings.json`.

**Selbstprüfung:** Sammellauf vor dem Merge-Commit Fehler 0 (eine Warnung „Stand verändert“, weil STATUS währenddessen bearbeitet wurde); Commit-Hook am Merge-Commit „Fehler: 0 · Warnungen: 0“; `pruefen --gegen`: 14 Dateien, 330 Modelle, 418 Varianten, Fehler 0, Warnungen 60 (Abdeckung); Geheimnis-Scan 449 Dateistände, 0 Funde; ein lokaler Pfad in `docs/pruefungen/2026-11-24-finder-g1/codex-nach-20261124-155951.stderr.txt` durch `<playbook>` ersetzt.

**Bekannte Grenzen (schon einzeln geprüft, nicht neu aufrollen):** Pakete Finder G1 (bestanden mit Hinweisen), P1-Sofortfixes (bestanden), Preis-Push (r3 nicht bestanden, Befunde nach O30 ohne r4 korrigiert, Restrisiko manipulierte lokale Git-Konfiguration), P2a-1 (r3-Rest nur selbst geprüft), P2a-2 (bestanden mit Hinweisen), `abruf.py` (r4-Befunde nach O23 ohne r5 korrigiert, R10-01 Restrisiko). Ältere öffentliche Commits enthalten schon lokale Pfade (Historie wird nicht umgeschrieben). Nicht auf echtem Android-Gerät geprüft.

**Prüffragen**
1. Passen die Pakete nach dem Merge zusammen (z. B. Freigabeschranke und Preis-Push auf demselben gh-pages, Lease-Reihenfolge, Herkunftsprüfung bei Schemawechsel 1 → 2)?
2. Kann der erste Push von `main` mit P2a-2 den Datenworkflow (Auslöser `daten/schema/**`) rot laufen lassen oder eine Live-Datei falsch ersetzen?
3. Kann ein installierter Client mit altem Service Worker nach der neuen Fassung kaputt oder veraltet bleiben?
4. Steht im Diff etwas, das im öffentlichen Repo nicht stehen darf?
5. Sind die Korrekturen, die nur selbst geprüft wurden (P2a-1 r3, Preis-Push R3-01…03, abruf r4), wirksam und mit Test belegt?
