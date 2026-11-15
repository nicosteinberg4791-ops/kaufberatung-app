# Bewertung Runde 1 (Codex erst, Stand 46877b6) – Korrektur in 54602a1

| Befund | Einordnung | Beleg / Korrektur |
|---|---|---|
| B429-01 schwer: Wartebudget sichert Workflow-Timeout nicht ab | bestätigt | Gesamtfrist `LAUF_FRIST` 420 s ab Laufbeginn (`time.monotonic`): Abruf startet nur bei Rest ≥ `ABRUF_MAX` 30 s, sonst Abruffehler „Lauffrist 420 s erreicht, nicht abgerufen“; Wiederholung nur, wenn Wartezeit + 30 s in den Rest passen. Rest 180 s für Checkout, Meldung, Push. Test `test_429_grenzen_und_andere_fehler` (Lauffrist-Teile, rot am Stand 46877b6). Grenze: ein einzelner Abruf kann bei tröpfelnder Antwort länger als 30 s dauern (urlopen-Timeout gilt je Socket-Operation); vorbestehend. |
| B429-02 schwer: lange Angebotsfehlerliste verdrängt Abruffehler | bestätigt | Laufmeldung neu aufgebaut: Abruffehler zuerst, dann Fehler, dann „Kein Angebot“; jede Liste bekommt Restplatz minus Reserve für die folgenden Teile, zu lange Listen als „Titel (n): a, b, +k weitere.“ (`_kurzliste`). Tests `test_abruffehler_eigene_meldung` (prüft gespeicherte `wecker_lauf.json`-Meldung ≤ 300, 23 × kein Angebot + 1 × 429) und `test_meldung_viele_abruffehler_gekuerzt` (20 × 429 + Problem + kein Angebot); beide rot am Stand 46877b6. |

Zusätzlich aus der Vorprüfung (Sonnet) ergänzt: Tests für andere HTTP-Fehler (503) und Timeout ohne Wiederholung, ungültiges Retry-After (fehlend, 0, negativ, 121, Datum, Text, Header None) → 30 s, Budget-Erschöpfung (3 Modelle × 429/120 s → 5 Abrufe, 2 Wartezeiten).

Selbstprüfung: `tests/alle-tests.ps1` Fehler 0 (auch Commit-Hook von 54602a1).
