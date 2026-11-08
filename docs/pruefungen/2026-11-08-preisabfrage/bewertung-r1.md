# Bewertung Codex R1 (codex-erst-20261108-202329.json)

| Befund | Schwere | Einordnung | Begründung / Maßnahme |
|---|---|---|---|
| B1 Kürzung verwirft Treffer | schwer | bestätigt | `push` in R4 ist auf 195 Zeichen gekürzt; bei mehreren Treffern fehlen Ereignisse, Stand wird trotzdem fortgeschrieben. Maßnahme: Meldetext im Adapter vollständig aus `bericht["treffer"]` (eine Zeile je Treffer, ntfy erlaubt 4096 Byte), R4 unverändert; Test mit Treffern für alle fünf Modelle. |
| B2 Stand vor bestätigtem Versand fortgeschrieben | schwer | bestätigt | Push lief vor ntfy; fehlendes Secret endete grün. Maßnahme statt Warteschlange: Reihenfolge Secret prüfen (fehlt → Lauf rot, vor jeder Verarbeitung) → preise.json schreiben → ntfy senden → erst dann pushen (`--nur-push`). Scheitert der Versand, bleibt der alte Stand, der nächste Lauf erkennt dasselbe Ereignis erneut (mindestens einmal; doppelt nur, wenn der Push nach erfolgreichem Versand scheitert). Totalausfall (Exit 3) wird weiter gepusht, Lauf danach rot. Anleitung präzisiert. Tests für Reihenfolge und `--nur-push`. |
