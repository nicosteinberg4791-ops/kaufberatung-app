# Prüfauftrag: Pilot Bestpreis-Mix (D7), Nachprüfung Runde 6 (nach Umbau)

**Ziel:** Prüfen, ob der Umbau der drei Prüfstellen (Übertragungsrahmen, Saturn-Seitenzustand, Sperrseitenerkennung) die r5-Befunde D7-02, -11, -15, -16, -17, -18 grundsätzlich schließt, ohne neue Fehler einzuführen. Runde 6 auf Besitzerentscheid (22.11.2026). D7-05 ist Besitzerentscheid und kein Prüfgegenstand.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“
- `python -I -B -m unittest discover -s tests -t tests -p test_shopabfrage.py` → OK (70 Tests)
- Antwortende eindeutig belegt: Content-Length mit gleicher Länge oder chunked mit streng CRLF-gerahmtem Abschluss. Sonst nicht abrufbar, robots.txt dann nicht lesbar = Quelle nicht abfragen.
- Saturn: Eigenangebot nur, wenn der einzige `window.__PRELOADED_STATE__` vollständig lesbar ist und alle Preisobjekte der Ziel-SKU vollständig sind und übereinstimmen (kein Marktplatz, gleicher Preis wie JSON-LD).
- Sperrseite: sichtbare Aufforderungen und technische Merkmale aktiver Elemente sperren. Echte robots.txt, `<template>`, `<noscript>`, Kommentare und Skriptstrings sperren nicht.

**Dateien (Diff ab Basis):** `werkzeuge/shopabfrage.py` (Kopf Z. 55–80, `mms_zustand`/`mms_preisfeld` Z. 250–332, `_Seitenteile`/`ist_robots`/`ist_challenge` Z. 445–536, `_StrengeAntwort` bis `abrufen` Z. 538–655) · `tests/test_shopabfrage.py` (Klasse `Runde5` ab Z. 694, Helfer `zustand_skript`) · `tests/vorlagen/saturn_*.html` (nur Formatumstellung).

**Selbstprüfung:** alle-tests Fehler 0. `Runde5` (6 Tests) schlägt gegen bd5a1ff vollständig fehl. Lokaler Livelauf 22.11.2026 wie zuvor: Saturn S90H 1.399 € Eigenangebot (echter Zustand in 0,06 s gelesen), S26 als Marktplatz verworfen, Alternate/Proshop/heise ok, keine Fehlsperre. Live senden alle vier Shops Produktseiten chunked, deshalb wurde „nur Content-Length“ verworfen.

**Bekannte Grenzen:** `_StrengeAntwort` überschreibt interne http.client-Methoden (`begin` erweitert, `_get_chunk_left`, `_read_and_discard_trailer`); Tests sichern das Verhalten. Sperrtexte und technische Merkmale bleiben feste Listen (deutsch/englisch). Unbekannte Formulierungen werden nicht erkannt. Ändert Saturn das Zustandsformat, fällt der Nachweis weg (sichere Richtung). O12/O13 entscheidet der Besitzer.

**Prüffragen**
1. Gibt es einen Rahmen, bei dem eine unvollständige Antwort angenommen oder eine gültige Antwort der echten Shops abgelehnt wird?
2. Kann ein Marktplatz-, widersprüchliches oder unvollständiges Saturn-Angebot als Eigenangebot gelten, oder wird ein gültiges verworfen?
3. Sperrt `ist_challenge` eine normale Produktseite oder robots.txt fälschlich, oder übersieht es eine sichtbare Aufforderung bzw. ein aktives technisches Merkmal?
