# Bewertung Codex-Erstprüfung (codex-erst-20261108-115245.json)

| ID | Schwere | Einordnung | Beleg / Korrektur |
|---|---|---|---|
| B1 | schwer | bestätigt: `warGesteuert` war Konstante | app.js: `gesteuert` wird bei der ersten Übernahme fortgeschrieben, jeder spätere Wechsel lädt genau einmal neu. Browser (Chrome headless, `update.mjs --fremd`): erster Besuch, neue Fassung von außen aktiviert (postMessage ohne Klick) → Seite lädt neu, app.css?v=neu, alte Caches weg; mit Klick ebenso. |
| B2 | schwer | bestätigt: Commit ohne Pfadbegrenzung | preise_aktualisieren.py `push()`: fremde Index-Einträge → Abbruch ohne Commit; `add`/`diff`/`commit` nur `-- preise.json`. Tests `PushSchutz.test_fremder_index_wird_abgelehnt`, `test_commit_nur_preise`. |
| B3 | schwer | bestätigt: nur Pfadvergleich | `arbeitsbaum_pruefen()`: `rev-parse --show-toplevel` = Ordner und `symbolic-ref HEAD` = gh-pages, vor dem Schreiben und vor dem Commit. Tests `test_kein_arbeitsbaum` (auch Unterordner eines anderen Repos), `test_falscher_zweig`. |
| B4 | mittel | bestätigt: ungeprüfte 200-Antwort ersetzte den Cache | sw.js `netzZuerst()`: JSON lesen, `preise`-Objekt verlangen, sonst letzter gültiger Stand. Browser: preise.json durch HTML ersetzt → Antwort ist der gecachte JSON-Stand, Cache gültig. Dabei neu gefunden: beim ersten Besuch blieb der Daten-Cache leer (Seite noch ohne Worker) → `activate` holt preise.json einmal selbst; danach offline 5 Preise ab erstem Besuch. |

Prüfgrenze des Prüfers „Python nicht installiert“: Tests laufen hier (`tests/alle-tests.ps1`, 19 Tests, Fehler 0).
