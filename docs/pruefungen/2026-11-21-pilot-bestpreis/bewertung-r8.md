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

## Abschluss (22.11.2026, Besitzerentscheid Option 1)

Der Besitzer hat Option 1 gewählt: Abschluss mit Leitplanke, keine Runde 9. Die fünf kleinen Korrekturen sind eingebaut (Stand nach 5897b2c, nur lokal). Selbst geprüft; keine unabhängige Nachprüfung dieser Korrekturen.

| ID | Korrektur in `werkzeuge/shopabfrage.py` | Test (`Runde8`) |
|---|---|---|
| D7-R8-01 | Skriptattribute wie im Browser: der erste Wert gilt. Ein Skript-Tag mit mehrfach gesetztem Attribut auf der Seite verwirft den Saturn-Nachweis (beide Reihenfolgen). | `test_d7_r8_01_doppeltes_typattribut` |
| D7-R8-02 | Saturn-Positivliste (Anfang, Zuweisung, Skriptende) nur mit ASCII-Leerraum `[ \t\n\r\f\v]`. | `test_d7_r8_02_nur_ascii_leerraum` |
| D7-R8-03 | Nennt ein anderes ausführbares Skript `__PRELOADED_STATE__` irgendwo im Rohtext, gibt es keinen Nachweis (auch in Zeichenketten; der r6-Test dazu ist entsprechend umgestellt). | `test_d7_r8_03_zustand_in_anderem_skript` |
| D7-R8-04 | Vor der Zerlegung `\r\n?` → `\n` (HTML-Vorverarbeitung). Die Skriptmaske behandelt LF, CR, U+2028 und U+2029 als Zeilenende. | `test_d7_r8_04_einzelnes_cr_und_zeilentrenner` |
| D7-R8-05 | JSON-LD-Merkmal nur beim vollständigen Typ `application/ld+json` (Groß-/Kleinschreibung und Rand-Leerraum egal). | `test_d7_r8_05_voller_jsonld_typ` |

**Nachweise (selbst geprüft, 22.11.2026):**
- `tests/alle-tests.ps1`: „Fehler: 0 · Warnungen: 0“; `test_shopabfrage` 85 Tests ok.
- Rot-Gegenprobe: alle fünf `Runde8`-Tests gegen `shopabfrage.py` aus 5897b2c rot, jeweils genau am Codex-Fall (`daten_zuerst`, `vorne '\x85'`, `template_interpolation`, `kommentar endet '\r'`, `text/not-ld+json`).
- Lokaler Livelauf (Heim-IP): S90H 1.399 € Saturn eigen; keine Quelle gesperrt (alle abgefragten Quellen „ok“ bzw. Saturn-Weiterleitung bei Ninja und Dreame wie bisher). Saturn-S26 liest den Seitenzustand und schließt das Angebot als Marktplatz aus. Die echten Saturn-Seiten nennen den Zustand also nur im Zustandsskript und haben keine doppelten Skriptattribute.

## Leitplanke und bekannte Grenzen

**Leitplanke:** Die Shopabfrage bildet HTML- und JavaScript-Semantik nur nach (Regex und `html.parser`), sie führt kein JavaScript aus. Eine Eingabe, die ein Browser anders auslegt, gilt als bekannte Grenze und nicht als Fehler, wenn (a) sie nur zu „kein Nachweis“ oder zu einer Fehlsperre führt (sichere Richtung: kein falscher Preis, Quelle in diesem Lauf nicht abgefragt) oder (b) sie eine gezielt manipulierte Shopseite braucht und das Angebot trotzdem EAN, Preis gleich JSON-LD, Korridor, Neuware und Lieferbarkeit erfüllen muss. Maßstab bleibt der Livelauf auf den echten Seiten.

**Bekannte Grenzen (bewusst nicht behandelt):**
1. Saturn-Nachweis: Ein zweites Skript mit zusammengesetztem Namen (`window["__PRELOADED_" + "STATE__"]`), Unicode-Escapes im Bezeichner oder ein externes Skript (`src`) kann den Zustand im Browser überschreiben, ohne dass die Abfrage das sieht (Richtung b).
2. Saturn-Nachweis: Nicht-ASCII-Leerraum, den JavaScript erlaubt (z. B. U+00A0, U+2028 vor der Zuweisung), ergibt keinen Nachweis (Richtung a).
3. Skriptmaske: Regex-Literale, verschachtelte Template-Literale und `-->` nach Nicht-ASCII-Leerraum werden nicht erkannt (D7-R7-03); passiver Text kann eine Fehlsperre auslösen oder Code verdecken (Richtung a bzw. b).
4. Ein Skript-Tag mit doppeltem Attribut irgendwo auf der Saturn-Seite verwirft den Nachweis, auch wenn der Browser das Zustandsskript korrekt ausführen würde (Richtung a).
5. `jsonld_bloecke` liest JSON-LD weiter per Regex über den Rohtext (nicht Teil der Befunde r8); eine manipulierte Seite könnte dort Daten unterschieben, die dann trotzdem alle Angebotsregeln erfüllen müssen (Richtung b).

**Weiter:** Pilot 3–5 Tage messen (Bericht Abschnitt 8, Schritt 8). Offen bleiben O12 (Saturn/Proshop sperren Actions-IPs) und O13 (alte Vorlagen in öffentlicher Historie).
