# Kaufberatung-App

Installierbare Android-App (PWA) der privaten Kaufberatung (Fernseher und Staubsauger) für Nico, kostenlos auf GitHub Pages. Ordner: `C:\Users\Nico\Documents\Claude\Kaufberatung-App`. Sprache: Deutsch.
Gemeinsame Regeln: AI Work Playbook (global geladen; Details `KERN.md` nur bei Bedarf).
Vorlagenversion: 2

## Rollen

- **Lead:** Claude (Claude Code) baut, testet, dokumentiert, bearbeitet Befunde.
- **Prüfer:** Codex prüft unabhängig an den Prüfpunkten (Skill `pruefschleife`), nur lesend.
- **Nico:** entscheidet fachlich, gibt frei, beauftragt Push/Deploy.

## Prüfpunkte

| Paket | Auslöser | Risikoklasse (KERN §4) |
|---|---|---|
| App-Hülle (Manifest, Service Worker, Ersatz `window.claude`) | vor erstem Push | normal (Codex medium) |
| Inhalt nachziehen (Version 9/10) | jede neue Inhaltsfassung | normal (Browsertest, Codex bei Hüllenänderung) |
| Veröffentlichung | vor jedem Push auf gh-pages | kritisch |

## Harte Regeln

- Inhalte nie hier pflegen: Quelle ist das fertige `kaufberatung.html` der Kaufberatung (claude.ai-Artifact), übernommen nur über `werkzeuge/app_bauen.py --quelle`. Änderungen nur in `app/` (Hülle).
- Repo und Seite sind öffentlich: keine Zugangsdaten, keine Wunschpreise, keine persönlichen Daten über die bestehenden Inhalte hinaus.
- Wunschpreise nur per `localStorage` auf dem Gerät; alle fremden Daten (preise.json, localStorage) prüfen und nur als Text ausgeben.
- Nichts versprechen, was nicht belegt ist (Benachrichtigungen: siehe docs/entscheidungen.md D4).
- Erst-Push von Nico freigegeben (08.11.2026, Repo `kaufberatung-app`, öffentlich). Weitere Pushes von App-Fassungen nach bestandener Prüfung; tägliche `preise.json`-Pushes durch die Preisabfrage sind erlaubt.
- Geheimnisse und Rückweg: KERN §7.

## Prüfen

- Tests: `powershell -File tests/alle-tests.ps1` (unittest `tests/test_*.py`) · Bauen: `python -I werkzeuge/app_bauen.py` · Ansicht: `preview_start` „kb-app“ → `http://127.0.0.1:8790/` · Geheimnisse: `werkzeuge/geheimnisse.py <Ordner>` im Playbook.

## Konnektoren

Benötigt: keine (GitHub über `gh`, Konto `nicosteinberg4791-ops`).

## Wegweiser (nur die passende Zeile lesen)

| Aufgabe | Datei |
|---|---|
| Stand, nächster Schritt | STATUS.md |
| Entscheidungen mit Grund | docs/entscheidungen.md |
| Offene Fragen | docs/offene-punkte.md |
| Gestaltung der Hülle | docs/DESIGN.md |
| Inhalt nachziehen, Preise | werkzeuge/app_bauen.py, werkzeuge/preise_aktualisieren.py (Kopf) |
