# Bewertung Runde 3 – Codex-Nachprüfung Pilot Bestpreis-Mix (21.11.2026)

Bericht: `codex-nach-20261121-072327.json` (nicht bestanden; geschlossen D7-04, -07, -10, -12, -13). Stand c36205f.
Noch nicht korrigiert (Kontext-Haltepunkt); Korrektur und Runde 4 in neuer Sitzung.

| ID | Schwere | Einordnung | Maßnahme (geplant) |
|---|---|---|---|
| D7-02 | schwer | bestätigt | Gekürzte 200-Antwort (Content-Length größer als Körper): Länge gegen Content-Length prüfen, `http.client.IncompleteRead` als nicht abrufbar; Test mit lokalem Server. |
| D7-05 | schwer | ungeklärt → Nico | Besitzerentscheid: heise-Treffer als Bestpreis zulassen (Kriterium ändern) oder nur „Vergleichspreis heise“; ggf. `delivery_time` „nicht lieferbar“ verwerfen. |
| D7-09 | schwer | bestätigt | Restliche Shoptexte (Alternate-Breadcrumb) aus Vorlagen; Zitat des Werbezusatzes in Prüfprotokollen (Bericht/Bewertung) neutralisieren, bevor gepusht wird. |
| D7-11 | schwer | bestätigt | Ausdrückliche Captcha-Aufforderung („complete the CAPTCHA“, „Ich bin kein Roboter“ o. ä.) als eindeutiges Sperrmerkmal; Test. |
| D7-14 | schwer | bestätigt | Doppelter Schlüssel `isProductOfTypeMarketplace` im selben Objekt: mit `object_pairs_hook` doppelte Schlüssel erkennen → kein Nachweis; Test. |
