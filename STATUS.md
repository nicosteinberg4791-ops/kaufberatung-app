# Stand – Kaufberatung-App

Stand: 25.11.2026 · Vollständiger Verlauf (Finder, UX, Pilot, Prüfrunden): [docs/status-verlauf.md](docs/status-verlauf.md) · Letzte Commits: `git log`.

## Lage

- **Live auf gh-pages:** App 1045baedfc64 (Stand 7339711, Inhalt Artifact-Version 30). Finder, Datenbank (325 Modelle) und UX-P1 sind auf `main`, aber nicht live.
- **Finder G1 (D26):** auf `main`, nicht gepusht; selbst geprüft bis 0996e86, Codex r3 bestanden mit Hinweisen. `main` und origin/main (Paket `abruf.py`, 40cf73f) sind auseinandergelaufen; Merge nur mit Auftrag, Konflikt in STATUS.md erwartet.
- **P2-Architekturprüfung r1:** nicht bestanden (11 Befunde bestätigt), Entwurf `p2-entwurf.md` §9 nachgezogen ([bewertung-r1.md](docs/pruefungen/2026-11-24-p2-architektur/bewertung-r1.md)).

## Nächster Schritt

Nachprüfung r2 der P2-Architektur (Skill `pruefschleife`, Auftrag `auftrag-r2.md` nur mit §9). Fertig, wenn r2 bestanden oder bewertet (`bewertung-r2.md`) und der Entwurf nachgezogen ist. Danach F-1…F-5 an Nico.

## Offen für Nico

- Fotos Finder G1 freigeben; P2 GS-1, „gleichauf“ im Vergleich (`docs/pruefungen/2026-11-24-finder-g1/gestaltung-r3.md`).
- Push und gh-pages nach Merge; Impeccable installieren (D21).
- O12 (Saturn/Proshop, Entscheidung 26.11.), O13, O10, O5, O6, O7 – Wortlaut im Verlauf.
- Nicht auf echtem Android-Handy geprüft: Icons, Push-Zustellung, Besitzer-Merker.

## Wegweiser

Tests `powershell -File tests/alle-tests.ps1` · Bau `python -I werkzeuge/app_bauen.py` · Entscheidungen [docs/entscheidungen.md](docs/entscheidungen.md) · Finder [docs/uebergabe-finder.md](docs/uebergabe-finder.md).
