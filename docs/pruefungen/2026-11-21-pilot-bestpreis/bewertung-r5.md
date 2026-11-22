# Bewertung Runde 5 – Codex-Nachprüfung Pilot Bestpreis-Mix (22.11.2026)

Bericht: `codex-nach-20261122-055617.json` (nicht bestanden; geschlossen keine, die Gegenproben aus r4 sind abgedeckt). Stand 774e6f9.
Runde 5 liegt über dem Rundenlimit 3 (KERN §3). Weiteres Vorgehen entscheidet der Besitzer.

| ID | Schwere | Einordnung | Richtung | Begründung |
|---|---|---|---|---|
| D7-02 | schwer | bestätigt | unsicher | Chunked-Abschluss `0\r\n\n` (LF statt CRLF) wird angenommen. |
| D7-16 | schwer | bestätigt | unsicher/sperrend | `Transfer-Encoding: chunked ` mit Leerzeichen: http.client erkennt chunked nicht, Rohdaten werden ausgewertet. |
| D7-11 | schwer | bestätigt | unsicher | `CAP<strong>T</strong>CHA` wird durch die Tag-Ersetzung zu `CAP T CHA`. |
| D7-17 | schwer | bestätigt | sperrend (sicher) | Technische Merkmale in `<template>`, Skriptstrings und robots.txt-Kommentaren sperren eine gültige Quelle. |
| D7-15 | schwer | bestätigt | unsicher | Preisobjekt ohne `currency`/Marktplatzfeld bzw. mit doppeltem Typfeld vor der id wird übersprungen. |
| D7-18 | schwer | bestätigt | verwerfend (sicher) | Großes Medienobjekt: die Rückwärtssuche (60 Klammern) erreicht dessen Anfang nicht, das gültige Angebot fällt weg. |

Fehlalarme: 0 von 6. Alle Gegenproben sind künstlich gebaut; auf den echten Seiten (Livelauf 22.11.2026) trat keiner der Fälle auf.

**Befund zum Vorgehen (systematic-debugging, Phase 4.5):** Fünf Runden, jede Korrektur erzeugt neue Randfälle an denselben drei Stellen. Das ist ein Architektursignal, kein einzelner Fehler:

1. **Saturn-Seitenzustand** wird per Regex-Anker und Rückwärtssuche gelesen. Strukturell richtig wäre, das eingebettete Zustandsobjekt als Ganzes zu dekodieren und den Baum nach Objekten der Ziel-SKU zu durchlaufen. Das schließt D7-15 und D7-18 grundsätzlich.
2. **Übertragungsrahmen** prüft der Pilot an http.client vorbei. Einfache harte Regel statt Feinprüfung: nur Antworten mit gültiger Content-Length auswerten, chunked oder Rahmen ohne Länge = nicht abrufbar (schließt D7-02, D7-16). Vorher klären, ob die vier Shops Content-Length senden.
3. **Sperrseitenerkennung** ist eine Merkmalsliste. Mit `html.parser` den sichtbaren Text sauber auslesen (D7-11) und technische Merkmale nur in aktiven Skripten und Attributen werten (D7-17). Bleibt eine Heuristik.

Unsichere Richtung (falscher Preis oder Abruf trotz Sperre) haben D7-02, -11, -15, -16. Sichere Richtung (Quelle oder Angebot fällt weg) haben D7-17 und -18.

## Umbau (22.11.2026, Besitzer: „Umbau + Runde 6“)

- **Übertragungsrahmen (D7-02, D7-16):** „Nur Content-Length“ ist nicht umsetzbar. Live senden alle vier Shops Produktseiten chunked ohne Content-Length (Saturn nur bei robots.txt mit Content-Length). Stattdessen erlaubt eine eigene Antwortklasse genau zwei Rahmen. Bei Content-Length wird die gelesene Länge verglichen. Bei chunked (Kopfwert nach Angleichung genau „chunked“) müssen Größenzeilen, Chunk-Enden und Abschluss streng CRLF haben. Alles andere gilt als nicht abrufbar: anderes Transfer-Encoding, beides zugleich, Ende nur durch Verbindungsabbau.
- **Saturn-Zustand (D7-15, D7-18):** `window.__PRELOADED_STATE__` wird als Ganzes gelesen. Das JavaScript-Objektliteral wird mit `undefined` → `null` zu JSON und mit Dublettenprüfung dekodiert. Danach werden alle Objekte der Ziel-SKU im Baum durchlaufen. Preisobjekte sind am Typ oder am Preisfeld erkennbar und müssen vollständig sein und übereinstimmen. Andere Merkmale derselben SKU zählen nicht. Bei mehr als einer Zuweisung oder unlesbarem Zustand gibt es keinen Nachweis. Regex-Anker und Rückwärtssuche entfallen.
- **Testvorlagen:** Die Saturn-Vorlagen und Testhelfer nutzten ein erfundenes Format (JSON-String in `__ZUSTAND__`). Sie sind auf das echte Format umgestellt (Objektliteral in `__PRELOADED_STATE__`).
- **Sperrerkennung (D7-11, D7-17):** `html.parser` zerlegt die Seite in sichtbaren Text, Attributwerte aktiver Elemente und aktive Inline-Skripte. Inline-Auszeichnung trennt keine Wörter. `<template>`, `<noscript>`, Kommentare und Skriptstrings zählen nicht. Technische Merkmale zählen nur in Attributen (z. B. `id="px-captcha"`, Skript-`src`), im Skript nur die Zuweisung `_cf_chl_opt = {`. Eine echte robots.txt (nur bekannte Anweisungen und Kommentare) ist nie eine Sperrseite.
- **Belege:** Klasse `Runde5` (6 Tests) schlägt gegen bd5a1ff vollständig fehl. alle-tests Fehler 0 (70 Shopabfrage-Tests). Livelauf 22.11.2026 identisch mit den Vorläufen: Saturn S90H 1.399 € Eigenangebot, S26 als Marktplatz verworfen, Alternate/Proshop/heise ok, keine Fehlsperre. Echte Saturn-Seite: Zustand in 0,06 s gelesen.
