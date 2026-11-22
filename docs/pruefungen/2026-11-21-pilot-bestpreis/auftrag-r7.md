# Prüfauftrag: Pilot Bestpreis-Mix (D7), Nachprüfung Runde 7

**Ziel:** Prüfen, ob die Korrekturen die r6-Befunde D7-R6-01..04 und D7-17 schließen, ohne neue Fehler in denselben drei Prüfstellen einzuführen. D7-05 ist Besitzerentscheid und kein Prüfgegenstand.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“
- `python -I -B -m unittest discover -s tests -t tests -p test_shopabfrage.py` → OK (75 Tests)
- Saturn: Eigenangebot nur aus genau einer Zuweisung `window.__PRELOADED_STATE__ = {…}` im Code eines ausführbaren Inline-Skripts, rechts davon nur das Objektliteral, danach `;` oder Skriptende; sonst kein Nachweis.
- Sperrseite: sichtbare Aufforderungen (auch im `<title>`, unabhängig von der Position) und technische Merkmale aktiver Elemente sperren. Gültige robots.txt (gleiche Regel wie `robots_gueltig`), `<template>`, `<noscript>`, Kommentare und Skriptstrings sperren nicht, auch ohne JSON-LD.
- Content-Length nur aus ASCII-Ziffern; alles andere `NichtAbrufbar`, nie ein ungefangener Fehler.

**Dateien (Diff ab Basis):** `werkzeuge/shopabfrage.py` (Konstanten Z. 58–80, `js_maskiert`/`mms_zustand` Z. 257–310, `_Seitenteile`/`seitenzerlegung`/`ist_challenge` Z. 469–570, `_StrengeAntwort.begin` Z. 583–605, `abrufen` Z. 656–697) · `tests/test_shopabfrage.py` (Klasse `Runde6` ab Z. 812).

**Selbstprüfung:** alle-tests „Fehler: 0 · Warnungen: 0“. `Runde6` (5 Tests) schlägt gegen 9113b9f vollständig fehl (R6-04 mit dem gemeldeten `ValueError`). Lokaler Livelauf 22.11.2026: Ergebnis in `bewertung-r6.md`.

**Bekannte Grenzen:** `js_maskiert` erkennt keine Regex-Literale; ein Anführungszeichen darin kann folgenden Code verdecken (Folge: kein Saturn-Nachweis bzw. keine Skriptsperre; Sperrtext, Titel und Attribute wirken weiter). Eine Antwort, die robots-Format hat (jede Zeile `Feld: Wert`, mit User-agent), gilt nie als Sperrseite, auch wenn ein Feldname wie ein Sperrtext klingt; die Produktseite wird danach erneut geprüft. Sperrtexte bleiben feste Listen. O12/O13 entscheidet der Besitzer.

**Prüffragen**
1. Kann ein Saturn-Zustand, den der Browser nicht oder anders setzt, weiterhin als Eigenangebot gelten, oder wird der echte Zustand (ein `<script>` ohne Typ) jetzt verworfen?
2. Sperrt `ist_challenge` eine normale Produktseite oder robots.txt fälschlich, oder übersieht es einen Sperrtitel bzw. ein aktives Merkmal?
3. Gibt es eine Content-Length- oder Rahmenangabe, die zu einem ungefangenen Fehler oder zur Annahme einer unvollständigen Antwort führt?
