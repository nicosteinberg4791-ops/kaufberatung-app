# Bewertung r4 – P2a-2 Nachprüfung r3 (Codex)

Bericht: [codex-nach-20261127-113235.json](codex-nach-20261127-113235.json) · Prüfstand db9f4e6, Basis 676771b · Urteil: bestanden mit Hinweisen (mittel 2; geschlossen BAU-03, BAU-04-TEST) · 4. Runde, vom Besitzer freigegeben (KERN §3) · Bewertet vom Lead (Claude Opus 5.5) am 27.11.2026. Keine weitere Nachprüfung (nur mittel offen, KERN §3).

| ID | Schwere | Einordnung | Klasse | Suche | Korrektur | Probe |
|---|---|---|---|---|---|---|
| P2A2-BAU-02 | mittel | bestätigt: der neue dritte Fall von Test 37 verlangte `n2 < n1`, also mehr als ein Modell je Kategorie in der Ausgangsdatei | Test hängt an der Größe der Datei (Rest der Klasse aus r3, in der Probe selbst) | `grep -nE "n[0-9] [<>]\|size\|> [0-9]{4,}" tests/test_bewertung.mjs` → nur diese Zeile im Bereich von Test 37 | Größenbeziehung entfernt; beide Läufe müssen allein den Vergleich bestehen, ohne Altfall rot | Fall „kleiner Verlauf“ grün mit Verlauf nur Altfall und mit je einem Modell pro Kategorie (Probe des Berichts: gleiche Zahl in beiden Läufen ist jetzt zulässig) |
| P2A2-BAU-06 | mittel | bestätigt: die ID gewichteter Felder hatte keine isolierte Probe (die `constructor`-Probe betrifft ein Feld mit Gewicht 0 und die Vorbedingungen) | Bestandteil der Projektion (§9.3) ohne isolierte Probe | Bestandteile aus §9.3 erneut abgeglichen: Feld-ID war der letzte ohne Probe; Typ, Gewicht, Kurve (40, 6), Frage-ID (r3), Antwort-ID (39), Abschlag (r2) belegt | Keine Codeänderung nötig; Testlücke geschlossen | `test_feld_id_isoliert`: jedes gewichtete Feld jeder Kategorie einzeln umbenannt (Verweise in Antworten mit) → Schema gültig, genau „Nummer muss steigen“, neue Nummer grün. Mutante „BAU-06 r3-Hinweis Feld-ID aus der Projektion“: von Hand rot (50 Teilfälle), Original grün |

## Selbstprüfung

- `test_datenbank.py` 46 Tests OK; Test 37 drei Fälle grün; Mutante Feld-ID einzeln rot, danach `git checkout` sauber.
- Sammellauf: Commit-Hook des Korrekturcommits (siehe STATUS).
- Nachweis: selbst geprüft. Unabhängig geprüft: BAU-02/03/04/04-TEST/06 in ihrer Klasse bis db9f4e6 (Codex r3); die beiden Hinweiskorrekturen nur selbst geprüft.
