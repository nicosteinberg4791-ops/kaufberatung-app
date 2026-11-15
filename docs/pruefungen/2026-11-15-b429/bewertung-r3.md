# Bewertung Runde 3 (Codex nach, Stand ffe1078) – Korrektur in d0a6169

| Befund | Einordnung | Beleg / Korrektur |
|---|---|---|
| B429-01 schwer: blockweises Lesen setzt die Frist nicht durch (read(65536) füllt den Block über viele Empfänge) | bestätigt | Zweiter gezielter Versuch gescheitert → Verfahren gewechselt: `_mit_frist` führt jeden Abruf in einem Daemon-Thread aus, `join(Rest der Lauffrist)`, sonst TimeoutError (Abruffehler); deckt DNS, Verbindungsaufbau und Lesen ab. Zusätzlich `read1` (ein Socket-Empfang je Aufruf; `http.client.HTTPResponse.read1` vorhanden, Python 3.11.9). Test `test_blockierender_abruf_endet_mit_lauffrist` (Abruf hängt 30 s, Lauf endet < 5 s; Fehler aus dem Thread kommen unverändert an); am Stand ffe1078 rot (30 s Hänger). |

`tests/alle-tests.ps1` Fehler 0 (Commit-Hook d0a6169).
