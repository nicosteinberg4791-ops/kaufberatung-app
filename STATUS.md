# Stand – Kaufberatung-App

Stand: 26.11.2026 · Branch main, Preis-Push selbst geprüft bis zum Commit „Preis-Push R3-01–03“ (Codex r1–r3 nicht bestanden, O30 ohne r4) · Vollständiger Verlauf (Finder, UX, Pilot, Prüfrunden): [docs/status-verlauf.md](docs/status-verlauf.md) · Letzte Commits: `git log`.

## Lage

- **Live auf gh-pages:** App 1045baedfc64 (Stand 7339711, Inhalt Artifact-Version 30). Finder G1, Datenbank und UX-P1 sind auf `main`, nicht gepusht und nicht live.
- **Finder G1 (D26):** selbst geprüft bis 0996e86, Codex r3 bestanden mit Hinweisen. `main` und origin/main (Paket `abruf.py`, 40cf73f) sind auseinandergelaufen; Merge nur mit Auftrag.
- **P2 (Entwurf `docs/recherche-ux/p2-entwurf.md`):** geschnitten in P2a-1 und P2a-2. P2a-2 r3 nicht bestanden, bewertet, Entwurf nachgezogen; Rundenlimit erreicht. O26 und O28: keine weitere Runde am Entwurf, Restrisiko bis zum Bau.
- **Pilot Bestpreis (D7):** Messung Tag 2–5 bis 26.11., Entscheidung O12 am 26.11.

## Nächster Schritt

**Preis-Push abgeschlossen (nicht gepusht):** `werkzeuge/preise_aktualisieren.py` `push()`, Codex r1–r3 nicht bestanden, alle 15 bestätigten Befunde korrigiert ([bewertung-r2.md](docs/pruefungen/2026-11-25-preis-push/bewertung-r2.md), [bewertung-r3.md](docs/pruefungen/2026-11-25-preis-push/bewertung-r3.md)); **O30 (Nico 26.11.):** R3-01–03 ohne r4 korrigiert, Mutanten 4/4 rot, Restrisiko nur bei manipulierter lokaler Git-Konfiguration. Wirksam erst nach Push von `main` (Nico). **Nächste Aufgabe:** P2a-1/P2a-2 bauen nach [p2-entwurf.md](docs/recherche-ux/p2-entwurf.md); fertig, wenn Tests grün und Erstprüfung gestartet.

## Offen für Nico

- Fotos Finder G1 freigeben; P2 GS-1, „gleichauf“ im Vergleich (`docs/pruefungen/2026-11-24-finder-g1/gestaltung-r3.md`).
- Push und gh-pages nach Merge; Impeccable installieren (D21).
- O12, O13, O10, O5, O6, O7 – Wortlaut im Verlauf.
- Nicht auf echtem Android-Handy geprüft: Icons, Push-Zustellung, Besitzer-Merker.

## Wegweiser

Tests `powershell -File tests/alle-tests.ps1` · Bau `python -I werkzeuge/app_bauen.py` · Entscheidungen [docs/entscheidungen.md](docs/entscheidungen.md) · Finder [docs/uebergabe-finder.md](docs/uebergabe-finder.md).
