# Bewertung Codex R1 (medium, erst) – Web Push

| Befund | Schwere | Einordnung | Begründung / Korrektur |
|---|---|---|---|
| B1 Anleitung verspricht unbelegt Zustellzeit und Zuverlässigkeit | schwer | bestätigt | „ein bis zwei Minuten“ und „Damit es zuverlässig ankommt“ entfernt (Web Push und ntfy); jetzt „keine feste Zustellzeit“, „Eine Zustellung ist nicht garantiert … Was helfen kann“, Hinweis auf den Laufschritt. Test `test_anleitung_ohne_zustellungszusage`. |
| B2 Lokales Abo wird als fertige Einrichtung angezeigt | mittel | bestätigt | Status nennt nur die lokale Anmeldung und verlangt das Secret PUSH_ABO plus Testlauf („Dieses Handy ist für Push angemeldet. Meldungen kommen erst, wenn …“). Der Knopf „Einrichtungscode zeigen“ bleibt sichtbar. Test in `test_oeffentlicher_schluessel_in_app`. |
| B3 Testnachricht ersetzt die Treffermeldung | mittel | bestätigt | Nachricht trägt `art` (treffer/test, CLI `--art`, unbekannte Art = Exit 5). Service Worker: Treffer ohne Tag (bleiben einzeln stehen), nur Tests mit `kb-push-test`. Verhaltenstests: CLI-Art (entschlüsselter Körper) und Service Worker im vm-Kontext (6 Push-Fälle); Gegenprobe mit altem Tag → 1 Test rot. |
