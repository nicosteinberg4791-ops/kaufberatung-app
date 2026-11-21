# Bewertung Runde 2 – Codex-Nachprüfung Pilot Bestpreis-Mix (21.11.2026)

Bericht: `codex-nach-20261121-071534.json` (nicht bestanden; geschlossen D7-01, D7-03, D7-06, D7-08). Stand 10b8897.

| ID | Schwere | Einordnung | Begründung / Maßnahme |
|---|---|---|---|
| D7-02 | schwer | bestätigt | Teilantwort/Lesegrenze. `abrufen()` wertet nur HTTP 200 aus und liest `MAX_BYTES + 1`; 206 oder Überlänge = nicht abrufbar. Test mit lokalem Server (206, Lesegrenze). |
| D7-04 | schwer | bestätigt | Feldreihenfolge. Anker bleibt die Feldfolge `id, currency, isProductOfTypeMarketplace`; von dort zur umschließenden Klammer zurück, vollständiges Objekt per `raw_decode`, nur dessen Felder. Tests: Folgeobjekt mit `__typename` vorn, echte Struktur (Preisobjekt beginnt mit `__typename`); Livegegenprobe Saturn S90H 1.399 € ok. |
| D7-05 | schwer | ungeklärt → Nico | Wie r1: Besitzerentscheid nötig, ob heise-Treffer ohne Nachweis von Lieferbarkeit/Zustand den Bestpreis stellen dürfen oder nur „Vergleichspreis heise“ sind. `delivery_time` ist Freitext; ohne belegte Wertliste kein Filter erfunden. |
| D7-07 | schwer | bestätigt | Normalisierung zu grob. Dubletten nur noch bei gleichem Namen nach Klein-/Leerraumangleichung oder ausdrücklichem Alias aus `quellen.json`. Test Proshop/Pro-Shop getrennt. |
| D7-09 | schwer | bestätigt | Werbezusätze in Produktnamen. Alle Vorlagen: Produktnamen synthetisch („Testprodukt <sku>“), Saturn-Seitenzustand synthetisch mit nur geprüften Feldern. Alte Fassungen bleiben in der öffentlichen Historie (79daf34); Umschreiben der Historie entscheidet der Besitzer. |
| D7-10 | kritisch | bestätigt | Neu durch r1-Korrektur. `betrag_ok()` (endlich, ≥ 0) für Preis, Versand JSON-LD und Seitenzustand. Test negativer Versand und NaN. |
| D7-11 | schwer | bestätigt | Eindeutige Sperrmerkmale jetzt im ganzen Text und unabhängig vom Inhaltstyp; passive Erwähnung in robots.txt bleibt erlaubt. Test spät/`text/plain`. |
| D7-12 | schwer | bestätigt | `automatisch` muss JSON-Boolean sein (`pruefe_daten`), Abruf nur bei `is True`. Test mit `"false"`. |
| D7-13 | gering | bestätigt | Hinweistexte in `daten/pilot_modelle.json` verweisen jetzt auf `quellen.json`. |

Rot-Gegenprobe: die 6 neuen Befundtests (D7-02, -04, -07, -10, -11, -12) schlagen gegen 10b8897 fehl. Fehlalarme: 0 von 9.
