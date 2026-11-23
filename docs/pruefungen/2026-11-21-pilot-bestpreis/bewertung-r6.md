# Bewertung Runde 6 – Codex-Nachprüfung Pilot Bestpreis-Mix nach Umbau (22.11.2026)

Bericht: `codex-nach-20261122-061137.json` (nicht bestanden; **geschlossen D7-02, -11, -15, -16, -18**). Stand 31b3073.
Korrigiert am 22.11.2026 (Abschnitt „Umgesetzt“ unten); Nachprüfung in Runde 7.

| ID | Schwere | Einordnung | Maßnahme (geplant) |
|---|---|---|---|
| D7-R6-01 | schwer | bestätigt | Saturn-Zustand nur aus einem aktiven `<script>` nehmen (Zuweisung über `_Seitenteile` bzw. Skriptinhalt, nicht im Kommentar/Template); Rest des Befunds („teilweise gelesen“) im JSON nachlesen. Test. |
| D7-17 | schwer | bestätigt | `_cf_chl_opt = {` innerhalb eines JS-Strings sperrt; ohne JSON-LD sperrt der schwache Zweig auf Rohtext (Template). Schwachen Zweig auf Attribute/sichtbaren Text/aktive Skripte umstellen; Skriptprüfung nur außerhalb von String-Literalen. Test. |
| D7-R6-02 | schwer | bestätigt | `^\s*Just a moment` greift nur am Textanfang: Titel getrennt erfassen (`<title>`-Inhalt) und dort prüfen. Test. |
| D7-R6-03 | schwer | bestätigt | Gültige robots.txt mit Erweiterungsfeld (`X-…:`) gilt nicht als robots → Kommentartext sperrt. `ist_robots` an `robots_gueltig` angleichen (jedes Feld `Name: Wert`), Kommentare vor der Sperrprüfung ignorieren. Test. |
| D7-R6-04 | schwer | bestätigt | `isdigit()` akzeptiert `²` → Absturz statt NichtAbrufbar. Nur ASCII-Ziffern (`re.fullmatch(r"[0-9]{1,15}")`) an allen Content-Length-Stellen; Test. |

Fehlalarme: 0 von 5. Konvergenz: Der Umbau schloss 5 von 6 r5-Befunden; die neuen Befunde sind kleiner und lokal behebbar.

## Umgesetzt (22.11.2026)

Tests: Klasse `Runde6` in `tests/test_shopabfrage.py` (5 Tests); alle fünf schlagen gegen 9113b9f fehl (4 Fehlschläge, R6-04 mit dem gemeldeten `ValueError`), mit der Korrektur 75 von 75 grün.

| ID | Umsetzung in `werkzeuge/shopabfrage.py` |
|---|---|
| D7-R6-01 | `mms_zustand` liest nur Zuweisungen im Code ausführbarer Inline-Skripte (`seitenzerlegung`: ohne `type` oder JavaScript-Typ, ohne `src`, nicht in `<template>`/`<noscript>`/HTML-Kommentar), gesucht im Skript ohne Zeichenketten und Kommentare (`js_maskiert`). Nach dem Objektliteral nur `;` oder Skriptende; `.artikel`, `|| {}` oder ein Zeilenumbruch mit Fortsetzung = kein Nachweis. |
| D7-17 | `_cf_chl_opt = {` wird nur im maskierten Skriptcode gesucht. Der schwache Zweig (ohne JSON-LD) durchsucht nur noch sichtbaren Text, Attributwerte aktiver Elemente und maskierten Skriptcode statt des Rohtexts. |
| D7-R6-02 | `_Seitenteile` erfasst `<title>` getrennt; `SPERRE_TITEL` (`^\s*Just a moment`) gilt je Titeltext, nicht für den Gesamttext. |
| D7-R6-03 | `ist_robots` entfällt; `ist_challenge` nutzt dieselbe Prüfung wie die robots.txt-Auswertung (`robots_gueltig`), Erweiterungsfelder und Kommentare inklusive. |
| D7-R6-04 | `LAENGE` (`[0-9]{1,15}`, nur ASCII) in `_StrengeAntwort.begin` und `abrufen`; `²` oder `4_0` ergeben `NichtAbrufbar`. |

Livelauf lokal (22.11.2026, 29 s): Saturn S90H 1.399 € Eigenangebot (Seitenzustand), S26 bei Saturn als Marktplatz verworfen, Ninja/Dreame bei Saturn wie bisher Weiterleitung (nicht ausgewertet); Alternate, Proshop, heise ok, keine Quelle gesperrt (keine Fehlsperre).
