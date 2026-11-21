# Bewertung Runde 4 – Codex-Nachprüfung Pilot Bestpreis-Mix (21.11.2026)

Bericht: `codex-nach-20261121-185847.json` (nicht bestanden; geschlossen D7-09, D7-14). Stand 11598dc.
Runde 4 liegt über dem Rundenlimit 3 (KERN §3): weiteres Vorgehen entscheidet der Besitzer.

| ID | Schwere | Einordnung | Begründung / mögliche Maßnahme |
|---|---|---|---|
| D7-02 | schwer | bestätigt | Chunked-Antwort mit Abschluss `0` ohne folgende Leerzeile: `http.client` liefert den Körper ohne `IncompleteRead`. Behebbar nur mit eigener Prüfung des Übertragungsendes (z. B. chunked ablehnen oder robots.txt doppelt lesen und vergleichen). Praktisch selten: Abbruch genau nach dem Endchunk. |
| D7-11 | schwer | bestätigt | Drei Teilfälle: (a) schwacher Prüfzweig durchsucht den ungefilterten Text, so sperrt robots.txt mit falschem Inhaltstyp `text/html` (einfach behebbar); (b) Aufforderung mit HTML-Auszeichnung im Satz (`<strong>CAPTCHA</strong>`) wird übersehen (Text vor der Prüfung von Tags befreien); (c) inaktives `<template>` mit Roboter-Text sperrt (Fehlsperre, sicherer Fehler). |
| D7-15 | schwer | bestätigt | Anker setzt die Feldfolge `id, currency, isProductOfTypeMarketplace` voraus; ein zweites Objekt derselben SKU mit anderer Reihenfolge bleibt unberücksichtigt. Maßnahme: alle Objekte mit `"id":"<Ziel>"` unabhängig von der Feldfolge dekodieren und gemeinsam auf Widerspruch prüfen. |

Fehlalarme: 0 von 3. Muster: Jede Runde findet neue Randfälle derselben drei Stellen (Übertragungsende, Sperrseitenerkennung, Saturn-Seitenzustand). Das spricht für Heuristik-Grenzen, nicht für Fehler im Grundaufbau.
