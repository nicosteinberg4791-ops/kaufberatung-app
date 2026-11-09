# Stand – Kaufberatung-App

Stand: 09.11.2026, ca. 06:55 · `main` auf github.com/nicosteinberg4791-ops/kaufberatung-app (öffentlich), Pages aus `gh-pages` (App d6e2a0bd6e50, Inhalt Version 9 = Artifact 1794136590-5658) · Prüfstufe Preisabfrage: selbst geprüft + unabhängig geprüft (Codex medium R1/R2: B1 behoben, B2-Rest bewusste Entscheidung D5 → kein schwerer Befund offen, Prüfung abgeschlossen 09.11.2026)

## Erledigt

- Hülle `app/`, Werkzeuge, Inhalt Version 8, veröffentlicht (Details: Git-Verlauf bis `3e910fe`, `docs/pruefungen/2026-11-08-app-huelle/`).
- **Tägliche Preisabfrage** (O1/O2): `.github/workflows/preise.yml`, `schedule` 05:23 UTC (= 06:23 MEZ, GitHub startet oft später) + `workflow_dispatch` (Häkchen Test-Benachrichtigung), bis 01.12.2026. Ablauf: Secret prüfen → `preise_aktualisieren.py --meldung` schreibt `.veroeffentlichung/preise.json` → ntfy senden → `--nur-push` (nur preise.json, nur gh-pages) → Totalausfall (Exit 3) macht den Lauf rot.
- `werkzeuge/preiswecker.py` = R4 aus Runde 6 (nur Kopf geändert), eingebunden mit `"version": 1` und `anlegen=True`.
- Wunschpreise optional nur als Secret `WUNSCHPREISE` (nie in preise.json/Log, Test + Gegenprobe). ntfy-Topic: Secret `NTFY_TOPIC`, Kopie für Nico in `C:\Users\Nico\Documents\Claude\Kaufberatung-App-privat\ntfy-topic.txt` (außerhalb des Repos).
- **Version 9 übernommen und live** (09.11.2026): Quelle = `Artifact read` der Kaufberatung (Live-Fassung 1794136590-5658, mit Runde 6: Preiswecker, Entscheiden, Kleingedrucktes). V9 liest preise.json Format 1 unverändert (`preise.<id>.aktuell.gesamt/haendler/sterne/zeit`, `tief.gesamt/datum`, `verlauf[{d,g,h}]`, `lauf.status/letzter/meldung/bis`, gleiche fünf IDs); Hülle unverändert, daher keine Codex-Prüfung nötig (AGENTS.md). Belege: Browserprüfung lokal und live (`--url` Pages) 375 px hell/dunkel scrollWidth = clientWidth = 375, Konsole leer (auch offline), SW aktiv, installierbar, Preiswecker „Lauf in Ordnung“ mit fünf Preisen, Wunschpreis setzen/neu laden/löschen ok, offline fünf Preise; Tests Fehler 0; Geheimnis-Scan 0 Funde. Fortschrittspunkte `.es-dots`: Standardlauf meldet `false/false/false`, das ist ein Messfehler von `pruefe.mjs` (misst vor dem Scrollen); mit sofortigem Scrollen treffen Mitte und +20 px alle sechs Punkte (44-px-Fläche aus `app.css`).
- Hinweis `pruefe.mjs`: `dist` als **absoluten** Pfad übergeben, sonst liefert der Prüfserver 404 (Vergleich mit `path.resolve`).
- O4 entschieden 09.11.2026: so lassen, keine Warteschlange ([D5](docs/entscheidungen.md)).
- Belege: `tests/alle-tests.ps1` Fehler 0 (27 Tests). Läufe 42514589798, 42514715464, 42515278390 grün (heise von GitHub erreichbar, alle fünf Modelle gelesen, preise.json live 20:29 MEZ, Pages-Deploy durch den Push ausgelöst). Test-Nachricht auf dem ntfy-Server abgefragt (Titel, Umlaute, Link korrekt); Zustellung aufs Handy erst nach Nicos Abo prüfbar. Secret im Log als `***`, Topic nirgends im Projekt (grep), Geheimnis-Scan 0 Funde.
- `docs/anleitung-handy.md`: Abschnitt ntfy (Abo, Test, Grenzen).

## Offen / blockiert

- **O5 (Nico):** Wunschpreise als Secret setzen? **O6:** heise-Nutzungsbedingungen ungeklärt (dokumentiert).
- Nico: ntfy-App abonnieren (Anleitung), dann Test-Lauf mit Häkchen → Zustellung bestätigen.
- Live-Konsole 09.11.2026 leer (Google-Schrift lud ohne Fehler). Nicht auf echtem Android-Handy installiert.
- Erster geplanter Lauf der Preisabfrage (05:23 UTC) war um 05:49 UTC noch nicht gestartet (GitHub verzögert geplante Läufe); beim nächsten Mal Laufliste prüfen.
- `pruefe.mjs` Punkte-Messung reparieren (sofort scrollen, ohne Reiter-Klick) und relativen `dist`-Pfad abfangen.
- Runde 6 passt den Seitensatz zur Uhrzeit an (gemeldet).

## Nächster Schritt

Geplanten Preisabfrage-Lauf vom 09.11. in `gh run list` bestätigen; danach Nicos offene Punkte (ntfy-Abo, O5). Neue Inhaltsfassung (Version 10) wie V9 nachziehen: `Artifact read` → Kopie → `app_bauen.py --quelle` → `pruefe.mjs <absoluter dist-Pfad>` → Tests → `veroeffentlichen.py`.
