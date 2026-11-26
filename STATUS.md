# Stand – Kaufberatung-App

Stand: 26.11.2026 · Branch main, P2a-1 gebaut und selbst geprüft (Erstprüfung durch Codex offen), Preis-Push abgeschlossen (O30 ohne r4) · Vollständiger Verlauf (Finder, UX, Pilot, Prüfrunden): [docs/status-verlauf.md](docs/status-verlauf.md) · Letzte Commits: `git log`.

## Lage

- **Live auf gh-pages:** App 1045baedfc64 (Stand 7339711, Inhalt Artifact-Version 30). Finder G1, Datenbank und UX-P1 sind auf `main`, nicht gepusht und nicht live.
- **Finder G1 (D26):** selbst geprüft bis 0996e86, Codex r3 bestanden mit Hinweisen. `main` und origin/main (Paket `abruf.py`, 40cf73f) sind auseinandergelaufen; Merge nur mit Auftrag.
- **P2 (Entwurf `docs/recherche-ux/p2-entwurf.md`):** geschnitten in P2a-1 und P2a-2. P2a-2 r3 nicht bestanden, bewertet, Entwurf nachgezogen; Rundenlimit erreicht. O26 und O28: keine weitere Runde am Entwurf, Restrisiko bis zum Bau.
- **Pilot Bestpreis (D7):** Messung Tag 2–5 bis 26.11., Entscheidung O12 am 26.11.

## Nächster Schritt

**P2a-1 gebaut (26.11.2026, selbst geprüft, nicht gepusht):** Schema 2 (`daten/schema/kategorien.json`), `werkzeuge/datenbank.py` (`schema_fehler`, Vertrag §9.6, Maße 0 < x ≤ 500, Quellen und Belege im Bau), `app/finder/bewertung.js` (`alternativen`, `notenblatt`, `methodik`, `fassung`, neue Prüfregeln), Doku `docs/punkteschema.md` §7a und `daten/produkte/FORMAT.md`. Sammellauf 0 Fehler; Mutanten: Bau 15/15 rot (Userinfo-Mutante erst mit kanon_host zusammen), Client 19/20 rot (1 äquivalent). Gegenprobe: 4 536 Noten alt gegen neu, 0 Abweichungen. `finder-daten.json` wächst von 330 436 auf 582 760 Byte (465 Quellen, 4 043 Belege; F-4 offen). **Nicht erledigt:** Codex-Erstprüfung (Skill `pruefschleife`), Test 44 Bau gegen Client auf denselben Fällen gemeinsam, **P2a-2** (Pflicht und Fassung 1 von `gewichte_version`, Referenzvergleich, Freigabeschranke, Tests 6, 37–42, 47, 48; Gewichte brauchen deine Freigabe F-1). Preis-Push abgeschlossen (O30), wirksam erst nach Push von `main` (Nico). **Nächste Aufgabe:** Erstprüfung P2a-1 starten, dann P2a-2 bauen nach [p2-entwurf.md](docs/recherche-ux/p2-entwurf.md).

## Offen für Nico

- Fotos Finder G1 freigeben; P2 GS-1, „gleichauf“ im Vergleich (`docs/pruefungen/2026-11-24-finder-g1/gestaltung-r3.md`).
- Push und gh-pages nach Merge; Impeccable installieren (D21).
- O12, O13, O10, O5, O6, O7 – Wortlaut im Verlauf.
- Nicht auf echtem Android-Handy geprüft: Icons, Push-Zustellung, Besitzer-Merker.

## Wegweiser

Tests `powershell -File tests/alle-tests.ps1` · Bau `python -I werkzeuge/app_bauen.py` · Entscheidungen [docs/entscheidungen.md](docs/entscheidungen.md) · Finder [docs/uebergabe-finder.md](docs/uebergabe-finder.md).
