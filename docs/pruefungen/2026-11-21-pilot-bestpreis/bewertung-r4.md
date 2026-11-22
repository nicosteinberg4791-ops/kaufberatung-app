# Bewertung Runde 4 – Codex-Nachprüfung Pilot Bestpreis-Mix (21.11.2026)

Bericht: `codex-nach-20261121-185847.json` (nicht bestanden; geschlossen D7-09, D7-14). Stand 11598dc.
Runde 4 liegt über dem Rundenlimit 3 (KERN §3): weiteres Vorgehen entscheidet der Besitzer.

| ID | Schwere | Einordnung | Begründung / mögliche Maßnahme |
|---|---|---|---|
| D7-02 | schwer | bestätigt | Chunked-Antwort mit Abschluss `0` ohne folgende Leerzeile: `http.client` liefert den Körper ohne `IncompleteRead`. Behebbar nur mit eigener Prüfung des Übertragungsendes (z. B. chunked ablehnen oder robots.txt doppelt lesen und vergleichen). Praktisch selten: Abbruch genau nach dem Endchunk. |
| D7-11 | schwer | bestätigt | Drei Teilfälle: (a) schwacher Prüfzweig durchsucht den ungefilterten Text, so sperrt robots.txt mit falschem Inhaltstyp `text/html` (einfach behebbar); (b) Aufforderung mit HTML-Auszeichnung im Satz (`<strong>CAPTCHA</strong>`) wird übersehen (Text vor der Prüfung von Tags befreien); (c) inaktives `<template>` mit Roboter-Text sperrt (Fehlsperre, sicherer Fehler). |
| D7-15 | schwer | bestätigt | Anker setzt die Feldfolge `id, currency, isProductOfTypeMarketplace` voraus; ein zweites Objekt derselben SKU mit anderer Reihenfolge bleibt unberücksichtigt. Maßnahme: alle Objekte mit `"id":"<Ziel>"` unabhängig von der Feldfolge dekodieren und gemeinsam auf Widerspruch prüfen. |

Fehlalarme: 0 von 3. Muster: Jede Runde findet neue Randfälle derselben drei Stellen (Übertragungsende, Sperrseitenerkennung, Saturn-Seitenzustand). Das spricht für Heuristik-Grenzen, nicht für Fehler im Grundaufbau.

## Korrektur (22.11.2026, Besitzer: „Korrigieren + Runde 5“)

- **D7-02:** Eigene Antwortklasse für den Abruf: chunked nur mit vollständigem Abschluss (Leerzeile nach dem Endchunk), sonst `IncompleteRead` → nicht abrufbar. Test: Ende nach `0` und nach `0\r\n` abgelehnt, sauberer Abschluss angenommen.
- **D7-11:** Ausdrückliche Aufforderungen werden im sichtbaren Text geprüft (ohne Tags, Skripte, Stile, `<template>`, `<noscript>`, Kommentare; Entities aufgelöst). robots.txt-Anweisungen sind in allen Prüfzweigen ausgenommen. Test: `<strong>CAPTCHA</strong>`, `&nbsp;`, robots.txt als `text/html`, inaktive Vorlage, Skripttext.
- **D7-15:** Anker ist jedes Feld `"id":"<Ziel>"` unabhängig von der Feldfolge; alle Preisobjekte (Typ `CofrPriceFeature` oder ohne Typ mit Preisfeldern) müssen übereinstimmen. Andere Merkmale derselben SKU (Abholung, Lieferung, Medien) werden übersprungen. Test: zweites Objekt mit anderer Feldfolge und Marktplatz verworfen, echte Seitenstruktur gültig, nicht dekodierbares Preisfeld = kein Nachweis.
- Systematische Fehlersuche während der Korrektur: Der erste D7-15-Ansatz verwarf auf der echten Saturn-Seite das gültige Angebot (Liefer-/Abholobjekte mit eigenem Marktplatzfeld, nicht dekodierbare Medienobjekte). Behoben und als Testfall aufgenommen; Livelauf danach wieder S90H 1.399 €.
- Rot-Gegenprobe: `Runde4`-Tests und der erweiterte D7-02-Test schlagen gegen 6a62c59 fehl. alle-tests Fehler 0 (64 Shopabfrage-Tests).
