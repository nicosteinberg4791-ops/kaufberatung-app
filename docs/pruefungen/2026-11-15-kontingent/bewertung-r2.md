# Bewertung Runde 2 (Codex nach, Stand 05aee2c) – Korrektur im folgenden Commit

| Befund | Einordnung | Beleg / Korrektur |
|---|---|---|
| KONT-02 mittel: nicht abgerufene Modelle bekommen einen Versuchszeitpunkt | bestätigt | Modelle, die wegen der Lauffrist übersprungen werden (`preiswecker.py`), tragen `nicht_versucht: True`. Dasselbe gilt für „heute_schon“-Modelle, die in `aktualisiere` zum Fehler umgewandelt werden, weil kein Preis von heute vorliegt. Diese Lücke ist bei der Rot-Probe aufgefallen. `lauf.versuche` erfasst nur Modelle mit tatsächlicher Anfrage. Test `test_lauffrist_gibt_keinen_versuchszeitpunkt`: Frist erschöpft, 0 Anfragen, `versuche` bleibt leer, die Meldung nennt den Abruffehler. |

Rot-Probe: Der neue Test am Stand 05aee2c schlägt fehl (1 Fehlschlag), mit Korrektur ist er grün. `tests/alle-tests.ps1` meldet Fehler 0.
