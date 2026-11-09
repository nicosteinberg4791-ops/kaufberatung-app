# Prüfauftrag: alle zehn Air Fryer der Top 10 im Preiswecker

**Ziel:** Der tägliche Preiswecker liest neben den fünf Fernsehern alle zehn Air Fryer aus dem Bericht „Air Fryer Top 10“ (bisher drei).

**Fertigkriterien**
- `MODELLE` enthält sieben neue heise-Produktseiten (Caso 3186, AEG AAFD11B, Russell Hobbs 27680-56, Ninja DZ400EU, Tefal EY942BE0, Gastroback 42586, Ninja AF500EU); jede passt zur genannten Modellnummer.
- Jeder Air Fryer hat die Grenze 30–1000 €, kein Fernseher (Grenze jetzt aus Präfix `af_` abgeleitet).
- `NAMEN`, `KURZ` und `IDS` in `app/app.js` decken genau `MODELLE` in gleicher Reihenfolge ab.
- Bestehende Fernseher- und Air-Fryer-Einträge unverändert; Laufstatus „ok“ nur, wenn alle 15 gelesen.

**Betroffene Dateien:** `werkzeuge/preiswecker.py`, `app/app.js`, `tests/test_app.py` (Diff ab Basis).

**Selbstprüfung:** `powershell -File tests/alle-tests.ps1` → Fehler 0, Warnungen 0. Livelauf `preiswecker.py` + `preise_aktualisieren.py --abruf … --ziel <temp>` → Status ok, „Alle 15 Preise gelesen.“, Preise 118–249 € je Air Fryer.

**Bekannte Grenzen:** Variantenwahl bei mehreren heise-Einträgen (Ninja: Grundeintrag ohne Farbsuffix; Tefal: EY942BE0 wie im Bericht). Der Artifact-Abgleich (`wecker_abgleich.py`, anderes Projekt) nimmt bewusst nur die Fernseher. Push-Titel bleibt „TV-Preiswecker“.

**Prüffragen**
1. Kann die abgeleitete `GRENZEN`-Regel einen Fernseher oder ein künftiges Modell falsch begrenzen?
2. Passen die sieben URLs (Pfadnamen) eindeutig zu den Modellen, oder ist eine Variante falsch gewählt?
3. Bricht etwas in `preise_aktualisieren.py` oder der App-Hülle bei 15 statt 8 Modellen (Anzeige, Laufzeit, Text)?
4. Decken die Tests die Fertigkriterien ab (insbesondere Reihenfolge `IDS` = `MODELLE`)?
