# Bewertung Runde 1 (Codex erst, Stand e6eaceb) – Korrektur im folgenden Commit

| Befund | Einordnung | Beleg / Korrektur |
|---|---|---|
| KONT-01 schwer: Wiederholungen nach 429 überschreiten das Limit | bestätigt | `abruf_alle`: Jetzt zählt `nr` alle HTTP-Anfragen gegen `ABRUF_JE_LAUF`. Ist das Kontingent erreicht, wird ein Modell als „verschoben“ markiert, statt die Liste vorab zu schneiden. Wiederholt wird nur, solange `nr < ABRUF_JE_LAUF` ist. Abgedeckt durch Test `test_wiederholung_zaehlt_gegen_kontingent`: 1 × 429 ergibt 16 Anfragen für 15 Modelle; 429 auf der letzten Anfrage führt zu keiner Wiederholung. |
| KONT-02 mittel: scheiternde Modelle hungern spätere aus | bestätigt | `preise.json` → `lauf.versuche` speichert je Modell den letzten Abrufversuch (nur Zeitpunkte). `abrufreihe` sortiert nach dem späteren Zeitpunkt aus Preis und Versuch, gerade versuchte Modelle rücken also nach hinten. Test `test_scheiternde_modelle_blockieren_nicht`: 16 Modelle bleiben erfolglos, danach stehen die 8 nie versuchten vorn. |

Rot-Probe: Beide neuen Tests am Stand e6eaceb ergeben 1 Fehlschlag und 1 Fehler, mit Korrektur sind sie grün. `tests/alle-tests.ps1` meldet Fehler 0.
