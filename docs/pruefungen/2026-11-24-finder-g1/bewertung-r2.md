# Bewertung Codex r2 (medium, nach, Basis 54052c3, Stand b7f5b24)

Bericht: `codex-nach-20261124-150540.json` · Urteil: bestanden mit Hinweisen (kritisch 0, schwer 0, mittel 4). G1-01…G1-05 nicht mehr offen.

| Befund | Schwere | Einordnung |
|---|---|---|
| G1-R2-01 Neuaufbau des Regler-Panels (G1-01-Pfad) verliert den Fokus eines weiter vorhandenen Reglers (`finder.js:480`) | mittel | ungeklärt → Nico: Lead hat noch nicht nachgeprüft (Kontextgrenze); Vorschlag: im nächsten Paket beheben |
| G1-R2-02 laufende FLIP-Animation reagiert nicht auf jetzt aktivierte Bewegungsreduktion (`finder.js:534`) | mittel | ungeklärt → Nico: höchstens 240 ms Restbewegung; Vorschlag: Restrisiko |
| G1-R2-03 Probe G1-04 erreicht den Pfad „Neurechnen ohne neue Hinweiskarten“ nicht (`test_finder_dom.mjs:628`) | mittel | ungeklärt → Nico: Testlücke, Korrektur selbst unverändert; Vorschlag: Probe nachschärfen |
| G1-R2-04 Probe G1-02 prüft keine echten 0 Teilpunkte (`test_finder_dom.mjs:592`) | mittel | ungeklärt → Nico: Testlücke; Vorschlag: Probe nachschärfen |
