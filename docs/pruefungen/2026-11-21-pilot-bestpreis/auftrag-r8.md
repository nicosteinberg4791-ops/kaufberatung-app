# Prüfauftrag: Pilot Bestpreis-Mix (D7), Nachprüfung Runde 8 (letzte Runde, Paketschnitt)

**Ziel:** Prüfen, ob die Korrekturen D7-R7-01..05 schließen. Maßstab sind die geschnittenen Fertigkriterien unten (Besitzerentscheid 22.11.2026). D7-05 ist Besitzerentscheid und kein Prüfgegenstand.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“
- `python -I -B -m unittest discover -s tests -t tests -p test_shopabfrage.py` → OK (80 Tests)
- Saturn (Positivliste): Ein Eigenangebot gibt es nur, wenn genau ein ausführbares Inline-Skript (kein `src`, ohne Typ oder mit JS-Typ, nicht in Kommentar, `<template>` oder `<noscript>`) nach Leerraum mit `window.__PRELOADED_STATE__ = {` beginnt. Danach folgt nur das Objektliteral, optional `;` und Leerraum bis zum Skriptende. Kein anderes ausführbares Skript nennt den Zustand im Code. Jede andere Form ergibt keinen Nachweis (sichere Richtung).
- Sperrseite: Sichtbare Aufforderungen (auch im leerraumnormalisierten `<title>`, an jeder Position) und technische Merkmale aktiver Elemente sperren. Gültige robots.txt, `<template>`, `<noscript>` und HTML-Kommentare sperren nicht. Die JSON-LD-Ausnahme gilt nur für einen echten geparsten Block.
- **Leitplanke Skripttext:** Einfache Zeichenketten, Template-Literale ohne Verschachtelung, `//`, `/* */`, `<!--` und `-->` am Zeilenanfang sperren nicht. Bei verschachtelten Template-Literalen und Regex-Literalen ist eine Fehlsperre zulässig (Quelle in diesem Lauf nicht abgefragt, kein falscher Preis). Das ist kein Befund.

**Dateien (Diff ab Basis 8caf11b):** `werkzeuge/shopabfrage.py` (`_ZUSTAND_START`/`js_maskiert`/`mms_zustand` Z. 257–315, `_Seitenteile` Z. 474–535, `ist_challenge` Z. 560–578) · `tests/test_shopabfrage.py` (Klasse `Runde7` ab Z. 917).

**Selbstprüfung:** alle-tests „Fehler: 0 · Warnungen: 0“. `Runde7` (5 Tests) schlägt gegen 8caf11b vollständig fehl. Lokaler Livelauf 22.11.2026: Die echte Saturn-Seite erfüllt die Positivliste (S90H 1.399 € Eigenangebot), S26 wird als Marktplatz verworfen, keine Fehlsperre.

**Prüffragen**
1. Kann ein Saturn-Zustand, der die Positivliste nicht erfüllt oder den der Browser anders setzt, als Eigenangebot gelten?
2. Übersieht `ist_challenge` einen Sperrtitel oder ein aktives Merkmal? Sperrt es außerhalb der Leitplanke eine normale Seite?
3. Hat die Korrektur in den geänderten Zeilen einen neuen Fehler eingeführt?
