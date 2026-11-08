# Stand – Kaufberatung-App

Stand: 08.11.2026, ca. 11:00 · Branch `main` (noch kein Commit) · Prüfstufe: selbst geprüft teilweise (Build und Preisabruf laufen; Browser, Offline, Codex offen)

## Erledigt

- Projekt eingerichtet (Skill `neues-projekt`, Vorlagenversion 2), Git `main`, Hook `.githooks`.
- Hülle: `app/manifest.webmanifest`, `app/sw.js` (versionierter Cache, preise.json zuerst vom Netz, Schrift-Cache, Periodic Sync, Benachrichtigungsklick), `app/app.js` (Ersatz `window.claude.use`, Treffer-Hinweis, „Neue Fassung“-Karte, Benachrichtigung als Versuch), `app/app.css` (Touch 44 px, Karten).
- Symbol `app/icons/icon.svg` + maskierbar, PNG 192/512 und apple-touch 180 per `werkzeuge/symbole.py` (Chrome headless + Pillow), angesehen.
- `werkzeuge/app_bauen.py`: Version 8 übernommen (`quelle/herkunft.json`, 269.444 Bytes, gleich dem lokalen Bau von Version 8), `dist/` gebaut, App `aa36593ad296`.
- `werkzeuge/preise_aktualisieren.py` nutzt `preiswecker.py` (Kopie in `werkzeuge/`, Original Runde 6); Probelauf 10:50: alle fünf Preise, Werte gleich Runde 6 (TCL 2.369 €, LG 2.779/2.499 €, Samsung 2.799/2.999 €) → `dist/preise.json`.
- `werkzeuge/veroeffentlichen.py` geschrieben, **ungetestet**.
- Push-Freigabe Nico (08.11.2026): Repo `kaufberatung-app`, öffentlich, Inhalt wie in AGENTS.md.

## Offen / blockiert

- O1, O2 siehe docs/offene-punkte.md.
- Nicht geprüft: Browser 375 px hell/dunkel, Installierbarkeit, Offline-Neuladen, Konsole, Ersatz `window.claude` mit Runde-6-Inhalt, Tests `tests/test_app.py` (noch nicht geschrieben), Codex.

## Nächster Schritt

Prüfen, Codex, veröffentlichen nach Übergabenotiz `side-session-notes/local_2f3f979b…/kaufberatung-app-uebergabe.md`. Fertig, wenn die URL auf GitHub Pages geöffnet und geprüft ist und die Anleitung `docs/anleitung-handy.md` steht.
