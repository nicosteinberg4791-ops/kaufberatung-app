# Stand – Kaufberatung-App

Stand: 08.11.2026, ca. 20:40 · `main` auf github.com/nicosteinberg4791-ops/kaufberatung-app (öffentlich), Pages aus `gh-pages` (App c68a0d42d414, Inhalt Version 8) · Prüfstufe Preisabfrage: selbst geprüft + unabhängig geprüft (Codex medium R1/R2, **nicht bestanden**: B1 geschlossen, B2-Rest wartet auf Nicos Entscheidung O4)

## Erledigt

- Hülle `app/`, Werkzeuge, Inhalt Version 8, veröffentlicht (Details: Git-Verlauf bis `3e910fe`, `docs/pruefungen/2026-11-08-app-huelle/`).
- **Tägliche Preisabfrage** (O1/O2): `.github/workflows/preise.yml`, `schedule` 05:23 UTC (= 06:23 MEZ, GitHub startet oft später) + `workflow_dispatch` (Häkchen Test-Benachrichtigung), bis 01.12.2026. Ablauf: Secret prüfen → `preise_aktualisieren.py --meldung` schreibt `.veroeffentlichung/preise.json` → ntfy senden → `--nur-push` (nur preise.json, nur gh-pages) → Totalausfall (Exit 3) macht den Lauf rot.
- `werkzeuge/preiswecker.py` = R4 aus Runde 6 (nur Kopf geändert), eingebunden mit `"version": 1` und `anlegen=True`.
- Wunschpreise optional nur als Secret `WUNSCHPREISE` (nie in preise.json/Log, Test + Gegenprobe). ntfy-Topic: Secret `NTFY_TOPIC`, Kopie für Nico in `C:\Users\Nico\Documents\Claude\Kaufberatung-App-privat\ntfy-topic.txt` (außerhalb des Repos).
- Belege: `tests/alle-tests.ps1` Fehler 0 (28 Tests). Läufe 42514589798, 42514715464, 42515278390 grün (heise von GitHub erreichbar, alle fünf Modelle gelesen, preise.json live 20:29 MEZ, Pages-Deploy durch den Push ausgelöst). Test-Nachricht auf dem ntfy-Server abgefragt (Titel, Umlaute, Link korrekt); Zustellung aufs Handy erst nach Nicos Abo prüfbar. Secret im Log als `***`, Topic nirgends im Projekt (grep), Geheimnis-Scan 0 Funde.
- `docs/anleitung-handy.md`: Abschnitt ntfy (Abo, Test, Grenzen).

## Offen / blockiert

- **O4 (Nico):** Codex R2-B2 – verpasste Meldung wird nach Preisanstieg nicht nachgereicht; Vorschlag: so lassen. Bestätigt Nico, gilt die Prüfung als abgeschlossen; sonst Warteschlange als eigenes Paket.
- **O5 (Nico):** Wunschpreise als Secret setzen? **O6:** heise-Nutzungsbedingungen ungeklärt (dokumentiert).
- Nico: ntfy-App abonnieren (Anleitung), dann Test-Lauf mit Häkchen → Zustellung bestätigen.
- Live-Konsole: Ladefehler der Google-Schrift einmal wiederholen prüfen (alt). Nicht auf echtem Android-Handy installiert.
- Runde 6 passt den Seitensatz zur Uhrzeit an (gemeldet).

## Nächster Schritt

Version 9 nachziehen (laut Runde 6 live): `Artifact read` der Kaufberatung → Kopie → `python -I werkzeuge/app_bauen.py --quelle <kopie> --version "Artifact-Version 9"` → `node werkzeuge/browserpruefung/pruefe.mjs` → Tests → `python -I werkzeuge/veroeffentlichen.py` (Push erlaubt nach bestandener Prüfung). Vorher prüfen, ob V9 preise.json im Format 1 liest (`lauf.status`, `preise.<id>.aktuell/tief/verlauf`). Fertig, wenn: App mit V9 live, Browserprüfung 375 px hell/dunkel ohne Querscrollen, Konsole leer, Tests Fehler 0.
