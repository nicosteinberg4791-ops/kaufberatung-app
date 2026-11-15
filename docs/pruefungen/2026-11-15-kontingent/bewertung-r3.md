# Selbstbefund nach Runde 3 (Livelauf 43758483221, Stand 94f6267) – Korrektur im folgenden Commit

| Befund | Einordnung | Beleg / Korrektur |
|---|---|---|
| SELBST-01 mittel: Der Status eines früheren Laufs bleibt stehen, wenn alle Preise von heute sind | bestätigt | Livelauf: „abgerufen 0“, alle 24 Preise von heute, `preise.json` blieb aber auf „teilweise“ von 19:48 mit veralteter 429-Meldung. Korrektur: Nichts abgerufen wird nur, wenn der Status schon „ok“ ist. Sonst läuft `abruf_alle([])` (0 Anfragen, alle als heute_schon) durch `aktualisiere`, und der Status wird neu berechnet. Test `test_nachlauf_ohne_offene_modelle_ruft_nichts_ab` hat einen zweiten Fall bekommen: von „teilweise“ wird ohne Anfrage „ok“ mit der Meldung „Alle 24 Preise gelesen.“ |

Rot-Probe: Der Test am Stand 94f6267 schlägt fehl (1 Fehlschlag), mit Korrektur ist er grün.
