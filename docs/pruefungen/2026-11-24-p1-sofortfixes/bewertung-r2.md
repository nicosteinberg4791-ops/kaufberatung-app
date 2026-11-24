# Bewertung Codex P1 r2 (Nachprüfung, medium, 268fb06)

Bericht: `codex-nach-20261124-095135.json` · Urteil: nicht bestanden (schwer 1, mittel 1) · geschlossen: P1-02, P1-05 · bewertet 24.11.2026 (Claude, Lead).

| ID | Schwere | Einordnung | Klasse | Suche | Korrektur | Probe |
|---|---|---|---|---|---|---|
| P1-03/P1-04 | schwer | bestätigt: Wenn kein Modell eine Note hat, nannte `ohneEmpfehlungText` nur einen Notengrund. Gemischte Gründe (`keine_merkmale` neben `zu_wenig_daten`) und den Preisgrund ließ er weg. | Meldung ohne Empfehlung zu grob (wie r1 P1-03) | `rg -n "Datenblattwerte\|kein Merkmal" app/finder/finder.js` → `ohneEmpfehlungText`, `offenText` (dort gemischt schon dreistufig), Zeilenmarke, `notenBlock`, Warnung, Statusansage (je Modell, eindeutig) | Ohne Note: Satz 1 nennt den Notengrund (Datenblatt, kein Merkmal oder gemischt). Satz 2 nennt den Preisgrund (keiner bekannt, alle über Budget oder gemischt). | `test_finder_dom.mjs` „P1-03/P1-04 r2 …“: Air Fryer mit nur der Sync-Funktion gewichtet; drei Preisfälle (beide über Budget, beide ohne Preis, gemischt). Rot mit finder.js aus 268fb06, grün danach. |
| P1-01 (Rest) | mittel | bewusste Entscheidung: Bei gleicher angezeigter Zahl und gleichem Preis entscheidet die ungerundete Note über die Reihenfolge. Beide Modelle tragen denselben Rang (Fertigkriterium erfüllt). Für die Reihenfolge braucht es einen festen Gleichstandsbrecher. Die genauere Note sagt mehr als die Modellkennung und wählt bei der Empfehlung das etwas besser ausgestattete Modell. | – | – | keine | vorhandener Test `test_bewertung.mjs` „P1-01: Punkte je Euro …“ (Dreierfall) hält das Verhalten fest |

## Selbstprüfung

- `node --test tests/test_bewertung.mjs tests/test_finder_dom.mjs tests/test_sw_daten.mjs` → 58 pass, 0 fail.
- `python -I werkzeuge/app_bauen.py` → App 6e736864a717; `tests/alle-tests.ps1` → `Fehler: 0 · Warnungen: 0`.
