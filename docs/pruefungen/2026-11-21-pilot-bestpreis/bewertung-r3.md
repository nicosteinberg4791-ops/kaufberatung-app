# Bewertung Runde 3 – Codex-Nachprüfung Pilot Bestpreis-Mix (21.11.2026)

Bericht: `codex-nach-20261121-072327.json` (nicht bestanden; geschlossen D7-04, -07, -10, -12, -13). Stand c36205f.
Korrigiert in der Folgesitzung (Commit nach fed7378).

| ID | Schwere | Einordnung | Maßnahme |
|---|---|---|---|
| D7-02 | schwer | bestätigt | `abrufen()` vergleicht die gelesene Länge mit Content-Length und wertet `http.client.IncompleteRead` (chunked) als nicht abrufbar. Test mit lokalem Server: gekürzte 200-Antwort, abgebrochener Chunk, robots.txt dadurch nicht lesbar. |
| D7-05 | schwer | bewusste Entscheidung | Besitzer 21.11.2026: heise-Treffer dürfen den Bestpreis stellen (Vergleichsquelle, Kriterium für heise entsprechend angepasst; `docs/entscheidungen.md` D7 Nachtrag). Kein Code geändert. |
| D7-09 | schwer | bestätigt | Alternate-Vorlage auf Produkt/Angebot gekürzt (kein Breadcrumb, Logo, Energiedaten). In allen Vorlagen URL-Namen durch `testprodukt-<sku>` und Filialnamen durch „Filiale n“ ersetzt. In den Prüfprotokollen (r1/r2-Bericht, r2/r3-Auftrag) Werbezitat und Kontopfad durch Platzhalter ersetzt. Alte Fassungen in der Historie: O13 (Besitzer). |
| D7-11 | schwer | bestätigt | Ausdrückliche Captcha-/Roboter-Aufforderungen (deutsch/englisch) sind eindeutige Sperrmerkmale. robots.txt-Anweisungszeilen werden vor der Prüfung entfernt, passive Sperrpfade sperren nicht mehr. Test: Aufforderung als `text/plain` und spät im HTML, robots.txt mit Challenge-Pfaden, reCAPTCHA-Formular auf Produktseite. |
| D7-14 | schwer | bestätigt | `mms_preisfeld` dekodiert mit `object_pairs_hook`, der doppelte Schlüssel ablehnt → kein Nachweis. Test: widersprüchlicher Marktplatzstatus verworfen, Gegenprobe ohne Dublette gültig. Livelauf lokal: Saturn S90H weiter 1.399 €. |

Rot-Gegenprobe: die 3 neuen Tests (Klasse `Runde3`) schlagen gegen fed7378 fehl. alle-tests Fehler 0 (62 Shopabfrage-Tests). Fehlalarme: 0 von 5.
