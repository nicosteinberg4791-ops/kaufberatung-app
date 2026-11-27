# Stand – Kaufberatung-App

Stand: 27.11.2026 · Branch main, P2a-2 gebaut, Nachprüfung r1 bewertet und korrigiert (selbst geprüft bis Korrektur r2; Codex-Nachprüfung r2 nicht bestanden, unbewertet; nicht gepusht) · P2a-1 unabhängig geprüft bis d062392 (Korrektur r3 nur selbst geprüft) · Vollständiger Verlauf: [docs/status-verlauf.md](docs/status-verlauf.md).

## Lage

- **Live auf gh-pages:** App 1045baedfc64 (Herkunft 7339711, Inhalt Artifact-Version 30). Finder G1, Datenbank, UX-P1, P2a-1 und P2a-2 sind auf `main`, nicht gepusht und nicht live. `main` und origin/main (Paket `abruf.py`, 40cf73f) sind auseinandergelaufen; Merge nur mit Auftrag.
- **Pilot Bestpreis (D7):** Entscheidung O12 stand am 26.11. an.

## Erledigt (26.11.2026)

- **Entscheidungen F-1, F-4, O31** (Besitzer): [D27](docs/entscheidungen.md).
- **P2a-2 gebaut:** `gewichte_version` ist Pflicht, Fassung 1 ({nummer 1, stand 2026-11-26}) steht in allen 14 Kategorien ([kategorien.json](daten/schema/kategorien.json)). [datenbank.py](werkzeuge/datenbank.py): `vorbedingung_fehler` (eindeutige IDs, Schema wie im Client, Kurven), `projektion`, `fassung_gegen_fehler`, `pruefen --gegen [<commit>]`. Neu ist [freigabe.py](werkzeuge/freigabe.py): strenge Referenz aus `<eltern>:finder-daten.json`, lokale Prüfung über `ls-remote`, Workflow-Schritt `daten-push` mit Lease. Angebunden in [veroeffentlichen.py](werkzeuge/veroeffentlichen.py) (vor dem Bau) und [finder-daten.yml](.github/workflows/finder-daten.yml).
- **Tests:** 3, 6, 38–41, 48 in `tests/test_datenbank.py` (Klasse `Gewichtsfassung`), 47(a), (c)–(h) in [tests/test_freigabe.py](tests/test_freigabe.py), 47(b), (c) in `tests/test_app.py` (`Veroeffentlichen`), 37, 40 (R2-01), 42 in `tests/test_bewertung.mjs`. Vor der Änderung rot: 3, 6, 38–41, 47, 48, 42. Schon vorher grün (Regressionsschutz): 37, 40-R2-01. Sammellauf `tests/alle-tests.ps1`: Fehler 0, Warnungen 0. `pruefen --gegen` gegen das echte gh-pages (Herkunft 7339711, Schema 1): 0 Fehler.

- **P2a-2 abgeschlossen:** Test 37 vergleicht gegen einen Bau mit Werkzeug und Schema der Live-Herkunft (`bauMitStand(herkunft)`). Mutanten ([mutanten.py](docs/pruefungen/2026-11-26-p2a2-bau/mutanten.py)): 9 Mutanten, 11 Zielläufe rot, Original 11/11 grün. Doku: `punkteschema.md` §7a, Kopf und §9.9 von `p2-entwurf.md`. Sammellauf Fehler 0.

## Erledigt (27.11.2026)

- **Erstprüfung r1 bewertet und korrigiert:** alle sechs Befunde bestätigt ([bewertung-r1.md](docs/pruefungen/2026-11-26-p2a2-bau/bewertung-r1.md)). Korrektur 171fb5d: strenges JSON auf allen Lesewegen und `allow_nan=False` im Bau (01), Test 37 ohne Annahme über den Live-Stand plus Fall „nach Veröffentlichung“ (02), Altschema-Ausnahme nur Schema 1 ohne Schlüssel (03), `daten_push` bindet die Datei an den Kandidaten (04), entfernte Referenzkategorie ist Fehler (05), Test 41 erweitert (06). Mutantenlauf 17 Mutanten, 20 Zielläufe rot, Original 20/20 grün; Sammellauf Fehler 0.

- **Nachprüfung r1 bewertet und korrigiert:** vier Befunde bestätigt ([bewertung-r2.md](docs/pruefungen/2026-11-26-p2a2-bau/bewertung-r2.md)). Korrektur 8ca76c0 plus Folgecommit: `daten_push` vergleicht die Bytes mit dem Nachbau aus `neu` (`freigabe.bau_aus_commit`, 04), Test 37 ohne feste Zahl werfender Fassungen, Altfall an Blob gebunden (02), Altschema nur bei ganzer Zahl 1, Referenzfassung vor jeder Projektion geprüft, Kandidat braucht ganze Zahl 2 (03), `test_abschlag_isoliert` (06). Sammellauf Fehler 0; Mutantenlauf 28/30 rot, die zwei verdeckten r1-Mutanten nach Testkorrektur einzeln rot.

## Nächster Schritt

**Codex-Nachprüfung P2a-2 r2 auswerten** (gpt-6.2-sol medium, `-Art nach`, Basis 275e635, Prüfstand 676771b, 397 s): nicht bestanden. Geschlossen BAU-04; offen BAU-02 schwer (Test 37 verlangt Mindestgröße des Verlaufs), BAU-03 schwer (Referenzfassung erst während der Projektion geprüft), BAU-06 mittel (Mutante ohne Frage-ID überlebt), neu BAU-04-TEST mittel (Gegenprobe vergleicht keine unveränderten Blob-Bytes). Einordnen in `bewertung-r3.md` wie r2, korrigieren mit Probe, einfrieren; Nachprüfung r3 nur bei offenem schwer, Auftrag noch schmaler (Warnung: Eingabe 1,6 Mio. Tokens). Rundenlimit nach KERN §3 beachten, ggf. Nico fragen.
**Fertig, wenn** jeder Befund eingeordnet ist, die bestätigten korrigiert sind, der Sammellauf Fehler 0 meldet und committet ist. Lesen: [codex-nach-20261127-092527.json](docs/pruefungen/2026-11-26-p2a2-bau/codex-nach-20261127-092527.json), dann nur genannte Stellen.

## Offen für Nico

- Fotos Finder G1 freigeben; P2 GS-1, „gleichauf“ im Vergleich (`docs/pruefungen/2026-11-24-finder-g1/gestaltung-r3.md`).
- Push und gh-pages nach Merge; Impeccable installieren (D21). Ein Push von `main` mit P2a-2 bringt die Schranke in den Datenworkflow (Auslöser `daten/schema/**`).
- P2: F-2 (Maße), F-3 (Testquelle), F-5 (Umfang der Projektion; gebaut nach Vorschlag „ja“: Kurven und Abschlag gehören dazu).
- O12, O13, O10, O5, O6, O7: Wortlaut im Verlauf.
- Nicht auf echtem Android-Handy geprüft: Icons, Push-Zustellung, Besitzer-Merker.

## Wegweiser

Tests `powershell -File tests/alle-tests.ps1` · Bau `python -I werkzeuge/app_bauen.py` · Schranke `python -I werkzeuge/datenbank.py pruefen --gegen` · Entscheidungen [docs/entscheidungen.md](docs/entscheidungen.md) · Finder [docs/uebergabe-finder.md](docs/uebergabe-finder.md).
