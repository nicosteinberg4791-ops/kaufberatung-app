# Prüfauftrag B-429 Preiswecker (Erstprüfung)

**Ziel:** Der tägliche Preisabruf übersteht die heise-Drosselung (HTTP 429) und meldet einen gescheiterten Abruf nicht mehr als „Kein Angebot“.

**Hintergrund:** Seit 24 Modellen (statt 15) lieferte heise ab dem ~19. Abruf (2 s Pause) HTTP 429; 6 Modelle behielten den alten Preis, Status „teilweise“, Meldung fälschlich „Kein Angebot mit belegtem Versand“.

**Fertigkriterien**
- Nach HTTP 429 wird je Modell genau einmal wiederholt; andere HTTP-Fehler und sonstige Fehler werden nicht wiederholt.
- Wartezeit vor der Wiederholung = Retry-After in Sekunden, wenn 1–120; sonst 30 s.
- Wartebudget für 429-Wartezeiten höchstens 240 s je Lauf; der Lauf bleibt sicher unter dem Workflow-Timeout von 10 min (`.github/workflows/preise.yml` Zeile 31, Abruf-Timeout 30 s in `abrufen`).
- Gescheiterter Abruf: Laufmeldung „Abruf fehlgeschlagen, alter Preis bleibt: <Modell> (HTTP <code>)“, nicht unter „Kein Angebot mit belegtem Versand“; alter Preis wird nicht überschrieben; Status wie bisher (ok / teilweise / fehler).
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“.

**Betroffene Dateien (Diff ab Basis)**
- `werkzeuge/preiswecker.py` Zeilen 180–217 (`_warte_429`, `abruf_alle`), 279–370 (`abgleich`).
- `tests/test_app.py` Zeilen 518–560 (`test_429_wird_einmal_wiederholt`, `test_abruffehler_eigene_meldung`).
- `werkzeuge/preise_aktualisieren.py` `oeffentlicher_lauftext` (ab Runde 2 geändert, B429-03; ruft `abruf_alle`/`abgleich`, kürzt Meldung auf 300 Zeichen).

**Selbstprüfung:** `tests/alle-tests.ps1` Fehler 0 (auch im Commit-Hook); beide neuen Tests rot vor der Korrektur, grün danach.

**Bekannte Grenzen:** Wirksamkeit gegen heise nur im Live-Lauf belegbar. `kaufberatung/build/preiswecker.py` ist eine ältere Eigenfassung außerhalb des Workflows und nicht Gegenstand.

**Prüffragen**
1. Kann die Wiederholungsschleife hängen, doppelt zählen oder ein Modell ohne Eintrag lassen?
2. Ist die Retry-After-Auswertung robust (fehlend, Datum statt Zahl, 0, negativ, > 120, Header-Objekt-Typen von `HTTPError`)?
3. Reicht das Budget rechnerisch für den schlechtesten Fall unter 10 min (24 Modelle, je 30 s Timeout ×2, 2 s Pause, 240 s Warten)?
4. Stimmen `n_ok`, Status und Meldungstext, wenn Abruffehler, „kein Angebot“ und Probleme gemischt auftreten? Kann ein Abruffehler weiterhin als „Kein Angebot“ erscheinen oder umgekehrt?
5. Prüfen die Tests das Verhalten wirklich (u. a. kein Sleep im Test, Budget-Erschöpfung ungetestet?)
