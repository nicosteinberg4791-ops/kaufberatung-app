# Bewertung r3 – P2a-1 gebaut (Codex gpt-6.2-sol medium, nach, nur P2A1-03)

Bericht: `codex-nach-20261126-093656.json` · geprüfter Stand `d062392` (Basis `ef5f946`, Auftrag `auftrag-r3.md`) · Urteil **nicht bestanden** (schwer 1) · 179 s, Eingabe ungecacht 49 727, Ausgabe 4 135. Der Prüfer bestätigt: Alle 5 237 vorgesehenen Paare werden direkt über `bewerteModell` verglichen, und `note`, `art`, Werte, Teilpunkte, Belege, Quellen und Testquelle stimmen überein.
Bewertet vom Lead am 26.11.2026 (Runde 3 auf des Besitzers Auftrag). Korrigiert ist nur `tests/test_bewertung.mjs` (Test „P2A1-03 (21)“).

| Nr. | Schwere | Einordnung | Klasse | Suche | Korrektur | Probe |
|---|---|---|---|---|---|---|
| P2A1-03 | schwer | bestätigt: `erwartet` wuchs in derselben Eingabeschleife wie `noten`. Eine ausgelassene Antwort senkte beide Zähler gleich (Gegenprobe des Prüfers: 5 237 → 5 223, Test grün). | Sollzahl nicht unabhängig von der Prüfschleife | Andere Zählprüfungen in den neuen Tests: keine. Auch die Zahl der Einträge (`modelle`) und der Kategorien war nur unten begrenzt (`> 300`). | Sollzahlen vor `datenPruefen` in einem eigenen Durchlauf über die Rohdaten: Einträge = Σ Modelle, Vergleiche = Σ Modelle × (1 + Zahl aller Antworten). Dazu Gleichheit der Zahl der Kategorien sowie je Kategorie `id` und Zahl der Modelle. | Mutanten am Test bzw. Code, je einzeln: M7 (eine Antwort der ersten Frage ausgelassen) → rot, 5 162 statt 5 237; M8 (eine ganze Frage ausgelassen) → rot; M9 (letztes Modell je Kategorie ausgelassen) → rot; M4 (Stufe bis 15 Codepunkte) → rot. Eine erste Fassung von M7 war wirkungslos (Frage-IDs gab es nicht) und zählt nicht. |

**Weiter:** Dies ist die dritte Runde, eine vierte starte ich nicht. Die Korrektur betrifft nur den Test und ist selbst geprüft, aber nicht vom Prüfer nachgeprüft (Restrisiko). Eine weitere Runde entscheidet Besitzer.
