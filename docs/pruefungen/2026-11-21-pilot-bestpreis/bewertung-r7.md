# Bewertung Runde 7 – Codex-Nachprüfung Pilot Bestpreis-Mix (22.11.2026)

Bericht: `codex-nach-20261122-063019.json` (nicht bestanden; **geschlossen D7-R6-02, -03, -04**; Codex hat die 75 Shopabfrage-Tests selbst ausgeführt, alle grün). Stand 8caf11b. Codex gpt-6.2-sol medium, 253 s, Eingabe 811.195 Tokens (ungecacht 58.939), Ausgabe 6.450.
Rundenlimit (KERN §3) weit überschritten. Besitzerentscheid 22.11.2026: Option 1 (Paket schneiden, letzte Runde 8).

| ID | Schwere | Einordnung | Maßnahme (Vorschlag) |
|---|---|---|---|
| D7-R7-01 | schwer | bestätigt | `<script src>` ohne Wert: html.parser liefert `None`, gilt fälschlich als „kein src“. Anwesenheit des Attributs prüfen (`"src" in a`). Test. Klein. |
| D7-R7-02 | schwer | bestätigt | Angehängtes Template-Literal wird maskiert und übersehen. Fremdes Ziel `other.window.__PRELOADED_STATE__` passt per Teilstring. Statt allgemeiner JS-Prüfung eine enge Positivliste nach der echten Seite: Skript beginnt (nach Leerraum) genau mit `window.__PRELOADED_STATE__ = {`, danach nur das Objektliteral, `;` und Leerraum bis zum Skriptende. Test. |
| D7-R7-03 | schwer | bestätigt | `js_maskiert` erkennt keine verschachtelten Template-Literale (`${`…`}`) und keine HTML-artigen Skriptkommentare (`<!--`, `-->`). Folge: Fehlsperre (sichere Richtung, kein falscher Preis), verletzt aber das Fertigkriterium. Maske erweitern oder Skriptmerkmal nur am Skriptanfang suchen. Test. |
| D7-R7-04 | schwer | bestätigt | Titel nicht leerraumnormalisiert: `Just\n a moment` wird übersehen. `re.sub(r"\s+", " ", …)` je Titel. Test. Klein. |
| D7-R7-05 | mittel | bestätigt | `application/ld+json` im HTML-Kommentar schaltet den schwachen Zweig ab (Prüfung auf Rohtext, aus der Zeit vor r7). Stattdessen `jsonld_bloecke` bzw. geparsten JSON-LD-Skriptblock verlangen. Test. Klein. |

Fehlalarme: 0 von 5.

**Konvergenz:** Die Prüfstelle Übertragungsrahmen ist zu (R6-04). Offen bleiben zwei Prüfstellen, beide wegen einer allgemeinen JavaScript-Auswertung mit regulären Ausdrücken. Jede Runde findet dort einen neuen künstlichen Randfall (Kommentar, Template, Zuweisungsziel, Maskierung). Keiner der Fälle kommt auf den echten Seiten vor (Livelauf 22.11.: alle Quellen ok, S90H 1.399 € korrekt). Ein vollständiger JS-Tokenizer passt nicht zum Rahmen „nur Standardbibliothek, Pilot“.

**Optionen für den Besitzer:**
1. **Paket schneiden (empfohlen):** R7-01, -04, -05 klein beheben. R7-02 über die enge Positivliste (Saturn-Nachweis nur in genau der Form der echten Seite, sonst kein Nachweis = sichere Richtung). R7-03 durch eine Leitplanke im Ergebnis: Ein Skriptmerkmal in passivem Skripttext darf eine Fehlsperre auslösen (sichere Richtung). Das Fertigkriterium wird entsprechend geändert. Danach eine letzte schmale Runde 8.
2. **Leitplanke ohne weitere Runde:** Pilot mit dokumentierter Restgrenze weiter messen (3–5 Tage), Befunde als bekannte Grenzen.

## Umgesetzt (22.11.2026, Option 1)

Tests: Klasse `Runde7` (5 Tests); alle fünf schlagen gegen 8caf11b fehl, mit Korrektur 80 von 80 grün, alle-tests „Fehler: 0“.

| ID | Umsetzung in `werkzeuge/shopabfrage.py` |
|---|---|
| D7-R7-01 | Skript mit `src`-Attribut (auch ohne Wert) ist nie ausführbares Inline-Skript (`"src" not in a`). |
| D7-R7-02 | Positivliste: genau ein ausführbares Skript beginnt (nach Leerraum) mit `window.__PRELOADED_STATE__ = {`; danach nur Objektliteral, optional `;`, Leerraum bis Skriptende. Nennt ein anderes ausführbares Skript den Zustand im Code, gibt es keinen Nachweis. |
| D7-R7-03 | Maske erkennt `<!--` und `-->` am Zeilenanfang als Zeilenkommentar. **Leitplanke:** verschachtelte Template-Literale und Regex-Literale bleiben unerkannt; eine Fehlsperre dadurch ist zulässig (sichere Richtung, kein falscher Preis). Fertigkriterium in `auftrag-r8.md` entsprechend. |
| D7-R7-04 | Titeltext wird vor der Musterprüfung leerraumnormalisiert. |
| D7-R7-05 | Ausnahme „JSON-LD vorhanden“ nur bei einem geparsten `<script type=…ld+json>` außerhalb von Kommentar/`<template>`/`<noscript>`. |

Livelauf lokal (22.11.2026): unverändert zu r6 (S90H 1.399 € Saturn eigen über die Positivliste, S26 Marktplatz verworfen, keine Fehlsperre).
