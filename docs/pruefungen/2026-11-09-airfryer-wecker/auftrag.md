# Prüfauftrag: Air Fryer im Preiswecker (Kaufberatung-App)

**Ziel:** Drei Air Fryer zusätzlich zu den fünf Fernsehern in die tägliche heise-Preisabfrage aufnehmen, sonst unverändert.

**Fertigkriterien**
- `werkzeuge/preiswecker.py`: MODELLE/NAMEN/KURZ um `af_cosori_tt`, `af_medion_p20`, `af_cosori_r901`; Preisgrenze je Modell (Fernseher 500–20000 unverändert, Air Fryer 30–1000); Rechenlogik (Versand, Tiefstpreis, Verlauf) unverändert.
- `app/app.js`: IDS gleich MODELLE (sonst filtert die Hülle die neuen Dokumente aus preise.json weg).
- Keine Änderung an Workflow, Push-Pfad, Geheimnissen; Medion-Variante (4 heise-Einträge zur MD11760) bewusst „XXL Twin“.
- Artifact-Seite (TV-Wecker `r6.js`) filtert auf ihre eigenen 5 Ids und zeigt keine Air Fryer.

**Dateien:** werkzeuge/preiswecker.py, app/app.js, tests/test_app.py (Klasse AirFryerImWecker, test_fortschreiben)

**Selbstprüfung:** `tests/alle-tests.ps1` Fehler 0, Warnungen 0. Livelauf `preise_aktualisieren.py --ziel <temp>`: Status ok, 8 Modelle, Cosori TT 249 €, Medion 79,95 €, R901 118,98 €, alle Versand belegt.

**Grenzen:** heise-Seiten per Livelauf, nicht per Mock; Medion-Variantenwahl offen für Nico; `.github/workflows/preise.yml` Push-Titel bleibt „TV-Preiswecker“ (bewusst).

**Prüffragen**
1. Kann die neue Preisgrenze (Parameter `grenzen`) die TV-Auswertung verändern oder einen Aufruf mit alter Signatur brechen?
2. Gibt es Stellen in `preise_aktualisieren.py`, Workflow, `sw.js` oder `webpush.mjs`, die eine feste Modellzahl 5 oder Namen/Ids annehmen?
3. Kann ein Air-Fryer-Fehler (heise-Fehler, kein Angebot) die TV-Preise beeinträchtigen?
4. Sind die neuen Tests aussagekräftig (würden sie bei fehlender Aufnahme oder falscher Grenze scheitern)?
