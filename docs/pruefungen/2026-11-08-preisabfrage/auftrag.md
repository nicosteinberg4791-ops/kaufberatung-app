# Prüfauftrag: tägliche Preisabfrage (GitHub Actions) mit ntfy-Push, preiswecker R4 eingebunden

**Ziel:** Prüfen, ob die tägliche Preisabfrage im öffentlichen Repo korrekt, sicher und ohne Datenabfluss arbeitet.

**Fertigkriterien:** Workflow `schedule` + `workflow_dispatch`; preise.json nur auf gh-pages, nur diese Datei committet; ntfy nur über Secret `NTFY_TOPIC`, Meldung je Ereignis einmal (neuer Tiefstpreis, Wunschpreis); Wunschpreise (optional, Secret `WUNSCHPREISE`) nie in preise.json, nie auf stdout/stderr (Actions-Logs sind öffentlich); `preiswecker.py` = Stand R4 (nur Kopf geändert) mit `abgleich(..., anlegen=True)` und Dokumenten mit `"version": 1`; Totalausfall (z. B. heise 403) → Exit 3, alte Preise bleiben.

**Betroffene Dateien:** `.github/workflows/preise.yml`, `werkzeuge/preise_aktualisieren.py`, `werkzeuge/preiswecker.py` (gegen Basis nur Austausch durch R4), `tests/test_app.py` (Klassen Preise, PushSchutz, Workflow), `docs/anleitung-handy.md` (Abschnitt ntfy).

**Selbstprüfung:** `powershell -File tests/alle-tests.ps1` → Fehler 0 (25 Tests). Gegenprobe: ohne `oeffentlicher_lauftext` schlägt `test_wunschpreis_bleibt_privat` fehl. Zwei `workflow_dispatch`-Läufe grün (alle fünf Modelle gelesen, preise.json live aktualisiert), Test-Nachricht auf dem ntfy-Server abgefragt. Secret im Log als `***`.

**Bekannte Grenzen:** preise.json ändert sich bei jedem Lauf (Zeitstempel), daher praktisch täglich ein Commit. Nutzungsbedingungen heise ungeklärt (robots.txt erlaubt Produktseiten). Der Wunschpreis-Treffer vergleicht den gestrigen Preis mit dem heutigen Wunschpreis (kein gespeicherter Wunschpreis). Zustellung auf dem Handy hängt vom Abonnieren ab.

**Prüffragen:**
1. Kann ein Wunschpreis auf irgendeinem Weg in preise.json, stdout/stderr oder Commit-Text gelangen (auch bei Fehlern, Kürzung auf 300 Zeichen, ungültigem JSON)?
2. Ist der Workflow sicher (Rechte minimal, kein Einschleusen über Eingaben, Topic nie im Klartext, curl-Fehlermeldungen)?
3. Stimmt die Treffer-Logik „je Ereignis einmal“ beim Übergang alt → neu (erste Ausführung mit vorhandener preise.json im alten Format, Modell ohne Angebot an einem Tag, Wunschpreis geändert)?
4. Push-Schutz: kann der Workflow etwas anderes als preise.json committen oder auf einen anderen Zweig pushen? Wettlauf mit `werkzeuge/veroeffentlichen.py`?
5. Fehlerpfade: Exit 3 bei Totalausfall, `assert` bei unplausiblem Preis, fehlendes Secret, Laufzeitende 01.12.2026.
6. Deckt die Anleitung (Abschnitt ntfy) das Einrichten korrekt und ohne unbelegte Versprechen ab?
