# Bewertung Runde 8 – Codex-Nachprüfung Pilot Bestpreis-Mix, letzte Runde nach Paketschnitt (22.11.2026)

Bericht: `codex-nach-20261122-065552.json` (nicht bestanden; **geschlossen D7-R7-01..05**). Stand 53c374b. Codex gpt-6.2-sol medium, 256 s, Eingabe 1.090.571 Tokens (ungecacht 49.803), Ausgabe 6.247.
Laut Besitzerentscheid war das die letzte Runde. Nicht korrigiert; der Besitzer entscheidet über den Abschluss.

| ID | Schwere | Einordnung | Maßnahme (Vorschlag, je klein) |
|---|---|---|---|
| D7-R8-01 | schwer | bestätigt | Doppeltes `type`: Der Browser nimmt den ersten Wert, `dict(attrs)` den letzten. Bei einem mehrfach gesetzten Attribut gilt das Skript nie als ausführbar. |
| D7-R8-02 | schwer | bestätigt | Python-`\s` umfasst U+0085, JavaScript-Leerraum nicht. Leerraum explizit als `[ \t\n\r\f\v ﻿  …]` bzw. nur ASCII-Leerraum zulassen. |
| D7-R8-03 | schwer | bestätigt | Eine Zuweisung in einer Template-Interpolation oder über `window["__PRELOADED_STATE__"]` in einem zweiten Skript wird übersehen. Kommt `__PRELOADED_STATE__` in einem anderen Skript irgendwo vor (Rohtext statt Maske), gibt es keinen Nachweis. |
| D7-R8-04 | schwer | bestätigt | Ein einzelnes CR gilt in der Maske nicht als Zeilenende. Vor der Analyse `\r\n?` → `\n` normalisieren, auch U+2028/U+2029. |
| D7-R8-05 | schwer | bestätigt | `text/not-ld+json` setzt das JSON-LD-Merkmal per Teilstring. Vergleich mit dem vollständigen Typ `application/ld+json`. |

Fehlalarme: 0 von 5.

**Konvergenz:** Die beanstandeten Fälle schließen jede Runde vollständig (r7: 5 von 5). Jede Runde findet aber neue künstliche Randfälle derselben Klasse: HTML- bzw. JavaScript-Semantik, nachgebaut mit Regex und html.parser. Keiner der Fälle kommt auf den echten Seiten vor; die Livelaufe r6 und r7 sind korrekt. Sicherheitsrichtung: R8-01..03 könnten ein Saturn-Eigenangebot falsch anerkennen. Dafür müsste die Saturn-Seite gezielt manipuliert sein, und das Angebot muss trotzdem EAN, Preis gleich JSON-LD, Korridor und Lieferbarkeit erfüllen. R8-04/-05 betreffen nur Fehlsperre bzw. schwache Captcha-Merkmale.

**Optionen für den Besitzer:**
1. **Abschluss mit Leitplanke (empfohlen):** R8-01..05 als bekannte Grenzen in die Leitplanke aufnehmen. Die fünf kleinen Korrekturen oben optional ohne weitere Runde einbauen (Selbstprüfung, Tests). Danach Pilot 3–5 Tage messen.
2. **Runde 9:** nur mit neuem Maßstab („Eingaben, die ein Browser anders auslegt, sind kein Befund, solange die echte Seite stimmt“). Sonst ist ein weiteres Nicht-Bestehen zu erwarten.
