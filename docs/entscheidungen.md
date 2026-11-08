# Entscheidungen – Kaufberatung-App

Eine Zeile je Entscheidung; die neueste unten. Gilt, bis eine spätere Zeile sie ausdrücklich ersetzt.

| ID | Datum | Entscheidung | Grund | Beleg / Quelle | entschieden von | ersetzt |
|---|---|---|---|---|---|---|
| D1 | 08.11.2026 | Eigene Web-App (PWA) auf GitHub Pages, öffentliches Repo `kaufberatung-app` auf `nicosteinberg4791-ops` | kostenlos, installierbar über Chrome | Auswahl im Auftrag; Freigabe „Ja, so pushen“ | Nico | – |
| D2 | 08.11.2026 | Seiteninhalt bleibt unverändert; die Hülle ersetzt `window.claude.use("db"/"user")` durch preise.json (read-only) und localStorage (Wunschpreise) | Runde-6-Skripte laufen ohne Doppelpflege | `app/app.js` | Lead | – |
| D3 | 08.11.2026 | Pages aus Zweig `gh-pages` (nur gebaute Dateien), `main` trägt Quellen | `docs/` ist Projektdoku; tägliche preise.json-Commits getrennt von Quellen | `werkzeuge/veroeffentlichen.py` | Lead | – |
| D4 | 08.11.2026 | Verlässlich ist nur der Treffer-Hinweis beim Öffnen. Hintergrund-Benachrichtigung nur als Versuch per Periodic Background Sync (installierte App, Chrome, Zeitpunkt vom Browser, ohne Gewähr). Kein Web Push (bräuchte Server bzw. Schlüssel) | ehrlich, kostenlos, ohne Server | developer.chrome.com/docs/capabilities/periodic-background-sync (gelesen 08.11.2026: nur installierte App, Engagement > 0, „timing … not controlled by developers“) | Lead | – |
