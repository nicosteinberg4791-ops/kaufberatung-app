# Stand – Kaufberatung-App

Stand: 08.11.2026, ca. 12:10 · Branch `main`, Commits `ea41852`, `9431ceb`, `92624ad` + Doku (nur lokal, kein Remote) · Prüfstufe: selbst geprüft + unabhängig geprüft (Codex medium, bestanden mit Hinweisen, Hinweis behoben); von Nico freigegeben: Push (weitergeleitet), Repo noch nicht angelegt

## Erledigt

- Hülle `app/` (Manifest, Service Worker, Ersatz `window.claude.use`, Treffer- und Update-Karte, Touch 44 px), Werkzeuge, Inhalt Version 8 unverändert.
- Tests `tests/test_app.py` (19): Build, Manifest, SW-Dateiliste, Symbole, Inhalt unverändert, Rahmen der Live-Seite, Preisfortschreibung, Push-Schutz. `tests/alle-tests.ps1` → Fehler 0.
- Browser (Chrome headless über DevTools-Protokoll, `werkzeuge/browserpruefung/*.mjs`; die eingebaute Browser-Leiste der Claude-App lässt keine Service Worker zu): 375 px hell/dunkel ohne Querscrollen, Konsole leer, `getInstallabilityErrors` leer, SW aktiv ab erstem Besuch ohne Doppel-Laden, Offline-Neuladen mit 5 Preisen, Treffer-Karte, Update-Ablauf (Klick und von außen), Preis-Cache übersteht HTML/ungültige Antworten. Mit Runde-6-Inhalt (Kopie in %TEMP%\kbapp-r6): Preiswecker zeigt preise.json („Lauf in Ordnung“), Wunschpreis setzen/löschen, Touch-Ziele ≥ 44 px (Schrittpunkte per unsichtbarer Trefferfläche).
- Korrekturen dabei: unnötiges Neuladen beim ersten Besuch, Wunschpreis löschen (`preis: null`), Datum deutsch, Touch Runde 6, LF in `.gitattributes`.
- Codex (`docs/pruefungen/2026-11-08-app-huelle/`): R1 nicht bestanden (B1–B3 schwer, B4 mittel), alle bestätigt und behoben; R2 bestanden mit Hinweisen (B4 Rest), behoben und im Browser belegt.
- `docs/anleitung-handy.md` geschrieben (Adresse noch nicht online).

## Offen / blockiert

- **O3:** `gh repo create … --public` von der Freigabesperre der Sitzung blockiert → App nicht online, `veroeffentlichen.py` noch nicht gegen das Remote gelaufen, Live-URL nicht geprüft.
- O1/O2 (Nicos Entscheidung 08.11.2026): GitHub Actions + ntfy umsetzen, siehe docs/offene-punkte.md.
- Version 9/10 nachziehen, sobald veröffentlicht (`app_bauen.py --quelle`, dann `browserpruefung/pruefe.mjs`).

## Nächster Schritt

Nach Nicos direkter Freigabe: `gh repo create nicosteinberg4791-ops/kaufberatung-app --public --source . --push`, `python -I werkzeuge/veroeffentlichen.py`, Pages auf `gh-pages` einschalten, URL prüfen (`node werkzeuge/browserpruefung/pruefe.mjs <dist> <aus> --url https://nicosteinberg4791-ops.github.io/kaufberatung-app/`). Danach Actions + ntfy (Übergabe im Notizordner).
