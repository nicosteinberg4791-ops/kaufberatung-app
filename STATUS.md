# Stand – Kaufberatung-App

Stand: 25.11.2026 · Branch main, Preis-Push selbst geprüft bis 40ed171, Codex r3 nicht bestanden (b47a70b) · Vollständiger Verlauf (Finder, UX, Pilot, Prüfrunden): [docs/status-verlauf.md](docs/status-verlauf.md) · Letzte Commits: `git log`.

## Lage

- **Live auf gh-pages:** App 1045baedfc64 (Stand 7339711, Inhalt Artifact-Version 30). Finder G1, Datenbank und UX-P1 sind auf `main`, nicht gepusht und nicht live.
- **Finder G1 (D26):** selbst geprüft bis 0996e86, Codex r3 bestanden mit Hinweisen. `main` und origin/main (Paket `abruf.py`, 40cf73f) sind auseinandergelaufen; Merge nur mit Auftrag.
- **P2 (Entwurf `docs/recherche-ux/p2-entwurf.md`):** geschnitten in P2a-1 und P2a-2. P2a-2 r3 nicht bestanden, bewertet, Entwurf nachgezogen; Rundenlimit erreicht. O26 und O28: keine weitere Runde am Entwurf, Restrisiko bis zum Bau.
- **Pilot Bestpreis (D7):** Messung Tag 2–5 bis 26.11., Entscheidung O12 am 26.11.

## Nächster Schritt

**Preis-Push (Besitzer 25.11.: zuerst):** gebaut (`werkzeuge/preise_aktualisieren.py` `push()`, Tests `PreisPush` in `tests/test_app.py`), Codex r1 nicht bestanden → 5 korrigiert (dc8a741), r2 nicht bestanden → bewertet ([bewertung-r2.md](docs/pruefungen/2026-11-25-preis-push/bewertung-r2.md)), **O29 = Neuansatz** (Besitzer 25.11.2026): R2-01–05 korrigiert (40ed171, Mutanten 9/9 rot). r3 (Codex high) nicht bestanden: R2-02/-03/-05 geschlossen, neu R3-01 kritisch (URL als Remote-Name aufgelöst), R3-02 schwer (`GIT_CONFIG` täuscht die pushInsteadOf-Prüfung), R3-03 mittel außerhalb, alle nur bei manipulierter lokaler Konfiguration, in Actions nicht wirksam ([bewertung-r3.md](docs/pruefungen/2026-11-25-preis-push/bewertung-r3.md)), nicht korrigiert. **O30 (Nico, Rundenlimit erreicht):** Vorschlag: R3-01 bis R3-03 mechanisch korrigieren, selbst geprüft, ohne r4, Rest als lokale Grenze annehmen. Alternative: nichts korrigieren und `--push` lokal sperren. Danach P2a-1/P2a-2 bauen. Nichts gepusht.

## Offen für Nico

- Fotos Finder G1 freigeben; P2 GS-1, „gleichauf“ im Vergleich (`docs/pruefungen/2026-11-24-finder-g1/gestaltung-r3.md`).
- Push und gh-pages nach Merge; Impeccable installieren (D21).
- O12, O13, O10, O5, O6, O7 – Wortlaut im Verlauf.
- Nicht auf echtem Android-Handy geprüft: Icons, Push-Zustellung, Besitzer-Merker.

## Wegweiser

Tests `powershell -File tests/alle-tests.ps1` · Bau `python -I werkzeuge/app_bauen.py` · Entscheidungen [docs/entscheidungen.md](docs/entscheidungen.md) · Finder [docs/uebergabe-finder.md](docs/uebergabe-finder.md).
