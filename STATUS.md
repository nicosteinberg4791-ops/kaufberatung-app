# Stand – Kaufberatung-App

Stand: 26.11.2026 · Branch main, letzter Commit 789fb6f, P2a-1 gebaut, Codex r1–r3 bewertet und korrigiert (unabhängig geprüft bis d062392, Korrektur r3 nur selbst geprüft, nicht gepusht), Preis-Push abgeschlossen (O30 ohne r4) · Vollständiger Verlauf (Finder, UX, Pilot, Prüfrunden): [docs/status-verlauf.md](docs/status-verlauf.md) · Letzte Commits: `git log`.

## Lage

- **Live auf gh-pages:** App 1045baedfc64 (Stand 7339711, Inhalt Artifact-Version 30). Finder G1, Datenbank und UX-P1 sind auf `main`, nicht gepusht und nicht live.
- **Finder G1 (D26):** selbst geprüft bis 0996e86, Codex r3 bestanden mit Hinweisen. `main` und origin/main (Paket `abruf.py`, 40cf73f) sind auseinandergelaufen; Merge nur mit Auftrag.
- **P2 (Entwurf `docs/recherche-ux/p2-entwurf.md`):** geschnitten in P2a-1 und P2a-2. P2a-2 r3 nicht bestanden, bewertet, Entwurf nachgezogen; Rundenlimit erreicht. O26 und O28: keine weitere Runde am Entwurf, Restrisiko bis zum Bau.
- **Pilot Bestpreis (D7):** Messung Tag 2–5 bis 26.11., Entscheidung O12 am 26.11.

## Nächster Schritt

**P2a-1 gebaut (26.11.2026, selbst geprüft, nicht gepusht):** Schema 2 (`daten/schema/kategorien.json`), `werkzeuge/datenbank.py` (`schema_fehler`, Vertrag §9.6, Maße 0 < x ≤ 500, Quellen und Belege im Bau), `app/finder/bewertung.js` (`alternativen`, `notenblatt`, `methodik`, `fassung`, neue Prüfregeln), Doku `docs/punkteschema.md` §7a und `daten/produkte/FORMAT.md`. Sammellauf 0 Fehler; Mutanten: Bau 15/15 rot (Userinfo-Mutante erst mit kanon_host zusammen), Client 19/20 rot (1 äquivalent). Gegenprobe: 4 536 Noten alt gegen neu, 0 Abweichungen. `finder-daten.json` wächst von 330 436 auf 582 760 Byte (465 Quellen, 4 043 Belege; F-4 offen). **Codex-Prüfung P2a-1 (26.11., Sol 6.2 medium, `docs/pruefungen/2026-11-26-p2a1-bau/`):** r1 nicht bestanden, 4 Befunde bestätigt und korrigiert (ef5f946: `sichereQuelle` ohne `href`, Test 44 Freigabe nach Produktstand, Test 21 mit echten Daten, `persoenlich` nur bei anwendbarem Feld). r2 nicht bestanden: 3 geschlossen, P2A1-03 nachgeschärft (Live-Test über `bewerteModell`, 5 237 Vergleiche). r3 (Nicos Auftrag, nur P2A1-03) nicht bestanden: Sollzahl hing an der Prüfschleife, korrigiert (Sollzahlen vorab aus den Rohdaten, Mutanten M7–M9 rot), nur selbst geprüft; keine vierte Runde ohne Nico. P2A1-R2-01 (Testlinks speichern `href`, außerhalb des Umfangs) → O31. **Nicht erledigt:** Test 44 Bau gegen Client auf denselben Fällen gemeinsam, **P2a-2** (Pflicht und Fassung 1 von `gewichte_version`, Referenzvergleich, Freigabeschranke, Tests 6, 37–42, 47, 48; Gewichte brauchen deine Freigabe F-1). Preis-Push abgeschlossen (O30), wirksam erst nach Push von `main` (Nico). **Nächste Aufgabe:** P2a-2 bauen (Pflicht und Fassung 1 von `gewichte_version`, Referenzvergleich, Freigabeschranke; Tests 6, 37–42, 47, 48), sobald Nico F-1 entschieden hat. Fertig, wenn diese Tests rot vor und grün nach der Änderung sind, `tests/alle-tests.ps1` Fehler 0 meldet und die Erstprüfung gestartet ist. Lesen: [p2-entwurf.md](docs/recherche-ux/p2-entwurf.md) §2.1, §9.1, §9.3, §9.9 · `werkzeuge/datenbank.py` (`fassung_fehler`, `schema_fehler`) · [bewertung-r3.md](docs/pruefungen/2026-11-26-p2a1-bau/bewertung-r3.md).

## Offen für Nico

- Fotos Finder G1 freigeben; P2 GS-1, „gleichauf“ im Vergleich (`docs/pruefungen/2026-11-24-finder-g1/gestaltung-r3.md`).
- Push und gh-pages nach Merge; Impeccable installieren (D21).
- P2: F-1 (Gewichte), F-4 (Quellen in eigener Datei), Start P2a-2; O31 (Testlinks mit Originalzeichenfolge, in P2a-2 oder P6; `bewertung-r2.md`).
- O12, O13, O10, O5, O6, O7 – Wortlaut im Verlauf.
- Nicht auf echtem Android-Handy geprüft: Icons, Push-Zustellung, Besitzer-Merker.

## Wegweiser

Tests `powershell -File tests/alle-tests.ps1` · Bau `python -I werkzeuge/app_bauen.py` · Entscheidungen [docs/entscheidungen.md](docs/entscheidungen.md) · Finder [docs/uebergabe-finder.md](docs/uebergabe-finder.md).
