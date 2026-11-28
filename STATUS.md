# Stand – Kaufberatung-App

Stand: 28.11.2026 · **Live:** gh-pages App cd6f226225dc aus 8a41085 (= origin/main), Prüfpunkt Veröffentlichung bestanden mit Hinweisen (Codex r3) · P2a-2 und P2a-1 mit veröffentlicht (Prüfstufen siehe Verlauf) · Vollständiger Verlauf: [docs/status-verlauf.md](docs/status-verlauf.md).

## Lage

- **Live auf gh-pages (28.11.2026):** App cd6f226225dc, Herkunft 8a41085 (Inhalt Artifact-Version 30), Finder-Daten 8a41085. Enthalten: Finder G1, Datenbank, UX-P1, P2a-1, P2a-2, Paket `abruf.py`, Merge a01e7fa.
- **Prüfstufen Veröffentlichung:** selbst geprüft: Commit-Hook (Sammellauf) an c168282 und 17d8df7 Fehler 0 · Warnungen 0, an 8a41085 ohne Abbruch (Ausgabe gekürzt), Geheimnis-Scan Historie 2070 Dateistände 0 Funde. Unabhängig geprüft: Codex r1 high nicht bestanden, r2 medium nicht bestanden, r3 medium bestanden mit Hinweisen ([bewertung-r3.md](docs/pruefungen/2026-11-28-veroeffentlichung/bewertung-r3.md)). Vom Besitzer freigegeben: Push und Veröffentlichung („bis live“), VER-02 angenommen (Push ohne Historienänderung, [bewertung-r2.md](docs/pruefungen/2026-11-28-veroeffentlichung/bewertung-r2.md)).
- **Abnahme live:** `version.json` app cd6f226225dc; `finder-daten.json` herkunft 8a41085, SHA-256 gleich gh-pages; Datenworkflow Finder-Daten (Lauf 46148631127) grün mit Pages-Abnahme; Browser: Startseite Finder mit Kategorienkacheln, Ratgeber erreichbar, Cache kb-app-cd6f226225dc, Konsole ohne Fehler. Nicht auf echtem Android-Gerät geprüft.
- **Pilot Bestpreis (D7):** Entscheidung O12 stand am 26.11. an.

## Erledigt (26.11.2026)

- **Entscheidungen F-1, F-4, O31** (Besitzer): [D27](docs/entscheidungen.md).
- **P2a-2 gebaut:** `gewichte_version` ist Pflicht, Fassung 1 ({nummer 1, stand 2026-11-26}) steht in allen 14 Kategorien ([kategorien.json](daten/schema/kategorien.json)). [datenbank.py](werkzeuge/datenbank.py): `vorbedingung_fehler` (eindeutige IDs, Schema wie im Client, Kurven), `projektion`, `fassung_gegen_fehler`, `pruefen --gegen [<commit>]`. Neu ist [freigabe.py](werkzeuge/freigabe.py): strenge Referenz aus `<eltern>:finder-daten.json`, lokale Prüfung über `ls-remote`, Workflow-Schritt `daten-push` mit Lease. Angebunden in [veroeffentlichen.py](werkzeuge/veroeffentlichen.py) (vor dem Bau) und [finder-daten.yml](.github/workflows/finder-daten.yml).
- **Tests:** 3, 6, 38–41, 48 in `tests/test_datenbank.py` (Klasse `Gewichtsfassung`), 47(a), (c)–(h) in [tests/test_freigabe.py](tests/test_freigabe.py), 47(b), (c) in `tests/test_app.py` (`Veroeffentlichen`), 37, 40 (R2-01), 42 in `tests/test_bewertung.mjs`. Vor der Änderung rot: 3, 6, 38–41, 47, 48, 42. Schon vorher grün (Regressionsschutz): 37, 40-R2-01. Sammellauf `tests/alle-tests.ps1`: Fehler 0, Warnungen 0. `pruefen --gegen` gegen das echte gh-pages (Herkunft 7339711, Schema 1): 0 Fehler.

- **P2a-2 abgeschlossen:** Test 37 vergleicht gegen einen Bau mit Werkzeug und Schema der Live-Herkunft (`bauMitStand(herkunft)`). Mutanten ([mutanten.py](docs/pruefungen/2026-11-26-p2a2-bau/mutanten.py)): 9 Mutanten, 11 Zielläufe rot, Original 11/11 grün. Doku: `punkteschema.md` §7a, Kopf und §9.9 von `p2-entwurf.md`. Sammellauf Fehler 0.

## Erledigt (27.11.2026)

- **Erstprüfung r1 bewertet und korrigiert:** alle sechs Befunde bestätigt ([bewertung-r1.md](docs/pruefungen/2026-11-26-p2a2-bau/bewertung-r1.md)). Korrektur 171fb5d: strenges JSON auf allen Lesewegen und `allow_nan=False` im Bau (01), Test 37 ohne Annahme über den Live-Stand plus Fall „nach Veröffentlichung“ (02), Altschema-Ausnahme nur Schema 1 ohne Schlüssel (03), `daten_push` bindet die Datei an den Kandidaten (04), entfernte Referenzkategorie ist Fehler (05), Test 41 erweitert (06). Mutantenlauf 17 Mutanten, 20 Zielläufe rot, Original 20/20 grün; Sammellauf Fehler 0.

- **Nachprüfung r1 bewertet und korrigiert:** vier Befunde bestätigt ([bewertung-r2.md](docs/pruefungen/2026-11-26-p2a2-bau/bewertung-r2.md)). Korrektur 8ca76c0 plus Folgecommit: `daten_push` vergleicht die Bytes mit dem Nachbau aus `neu` (`freigabe.bau_aus_commit`, 04), Test 37 ohne feste Zahl werfender Fassungen, Altfall an Blob gebunden (02), Altschema nur bei ganzer Zahl 1, Referenzfassung vor jeder Projektion geprüft, Kandidat braucht ganze Zahl 2 (03), `test_abschlag_isoliert` (06). Sammellauf Fehler 0; Mutantenlauf 28/30 rot, die zwei verdeckten r1-Mutanten nach Testkorrektur einzeln rot.

- **Nachprüfung r2 bewertet und korrigiert:** vier Befunde bestätigt ([bewertung-r3.md](docs/pruefungen/2026-11-26-p2a2-bau/bewertung-r3.md)). Korrektur 288125d: Test 37 ohne Mindestgröße und Notenschwelle, stattdessen Vollständigkeit je Fassung (02); `fassung_gegen_fehler` prüft Schema-Version und alle Fassungsangaben vor der ersten Projektion (03); `test_frage_id_isoliert` (06); Bytegegenprobe binär (04-TEST). Sammellauf Fehler 0; Mutantenlauf 36/36 rot, Original einmal nicht reproduzierbar rot (siehe Bewertung). Selbst geprüft.
- **Nachprüfung r3 (Codex, gpt-6.2-sol medium, 129 s, Eingabe 330 Tsd., ungecacht 56 Tsd.):** bestanden mit Hinweisen; geschlossen BAU-03 und BAU-04-TEST, BAU-02 und BAU-06 auf mittel gesunken. Beide Hinweise korrigiert: Test 37 ohne Größenvergleich im Probenfall, `test_feld_id_isoliert` ([bewertung-r4.md](docs/pruefungen/2026-11-26-p2a2-bau/bewertung-r4.md)).

## Nächster Schritt

Veröffentlichung abgeschlossen (siehe Lage). Besitzer hat am 28.11. D28–D31 entschieden (Vorlagen in `docs/vorlagen/`). Nächstes Paket: G1-Korrektur (b) Auf/Zu-Marke und (c) „gleichauf“ nach D29 (Skills `impeccable`, `frontend-design`), dann Fotos neu; danach P0 und P2b (D30). Impeccable installiert (D21 erledigt).
Offen aus P2a-2: ein einmaliger, nicht reproduzierter Fehlschlag von `test_datei_an_kandidat_gebunden` im Mutantenlauf ([bewertung-r3.md](docs/pruefungen/2026-11-26-p2a2-bau/bewertung-r3.md), Selbstprüfung).

## Offen für den Besitzer

- Fotos G1 freigeben, sobald nach D29 neu aufgenommen; Ratgeber-Regel „nur die Spitze zählt“ für „gleichauf“ bestätigen (D29).
- O13, O10, O5, O6, O7: Wortlaut im Verlauf; O12 entschieden (D28), Rechtsfrage Heimrechner offen, weitere Pilot-Messtage je Lauf freigeben.
- Nicht auf echtem Android-Handy geprüft: Icons, Push-Zustellung, Besitzer-Merker.

## Wegweiser

Tests `powershell -File tests/alle-tests.ps1` · Bau `python -I werkzeuge/app_bauen.py` · Schranke `python -I werkzeuge/datenbank.py pruefen --gegen` · Entscheidungen [docs/entscheidungen.md](docs/entscheidungen.md) · Finder [docs/uebergabe-finder.md](docs/uebergabe-finder.md).
