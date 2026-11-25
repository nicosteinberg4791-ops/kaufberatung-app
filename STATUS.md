# Stand – Kaufberatung-App

Stand: 25.11.2026 · Vollständiger Verlauf (Finder, UX, Pilot, Prüfrunden): [docs/status-verlauf.md](docs/status-verlauf.md) · Letzte Commits: `git log`.

## Lage

- **Live auf gh-pages:** App 1045baedfc64 (Stand 7339711, Inhalt Artifact-Version 30). Finder G1, Datenbank und UX-P1 sind auf `main`, nicht gepusht und nicht live.
- **Finder G1 (D26):** selbst geprüft bis 0996e86, Codex r3 bestanden mit Hinweisen. `main` und origin/main (Paket `abruf.py`, 40cf73f) sind auseinandergelaufen; Merge nur mit Auftrag.
- **P2 (Entwurf `docs/recherche-ux/p2-entwurf.md`):** geschnitten in P2a-1 und P2a-2. P2a-2 r3 nicht bestanden, bewertet, Entwurf nachgezogen; Rundenlimit erreicht.
- **Pilot Bestpreis (D7):** Messung Tag 2–5 bis 26.11., Entscheidung O12 am 26.11.

## Nächster Schritt

**O28 (Besitzer):** entscheiden, wie es nach dem Rundenlimit bei P2a-2 weitergeht; danach P2a-1 und P2a-2 bauen oder zuerst den Preis-Push als eigenes Paket (Wortlaut im Verlauf).

## Offen für Nico

- Fotos Finder G1 freigeben; P2 GS-1, „gleichauf“ im Vergleich (`docs/pruefungen/2026-11-24-finder-g1/gestaltung-r3.md`).
- Push und gh-pages nach Merge; Impeccable installieren (D21).
- O12, O13, O10, O5, O6, O7 – Wortlaut im Verlauf.
- Nicht auf echtem Android-Handy geprüft: Icons, Push-Zustellung, Besitzer-Merker.

## Wegweiser

Tests `powershell -File tests/alle-tests.ps1` · Bau `python -I werkzeuge/app_bauen.py` · Entscheidungen [docs/entscheidungen.md](docs/entscheidungen.md) · Finder [docs/uebergabe-finder.md](docs/uebergabe-finder.md).
