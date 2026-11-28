# Prüfauftrag: Veröffentlichung, Nachprüfung r2 (kritisch)

**Ziel:** Prüfen, ob die Korrekturen zu VER-01, VER-03 und VER-04 aus r1 wirksam sind und ihre Fehlerklasse ganz abdecken; Prüfgegenstand ist der Diff 4804a09..HEAD (c168282), keine Vollprüfung.

**Korrekturstellen** (Einordnung und Proben: `bewertung-r1.md`)
- VER-01 (Klasse: persönliche Angaben und lokale Pfade im versionierten Stand): Vorname durch „Besitzer“ ersetzt in `STATUS.md`, `docs/status-verlauf.md` und Prüfberichten; `docs/pruefungen/2026-11-24-finder-g1/fotos.mjs` liest den Chrome-Pfad aus `CHROME`. Erwartet: `git grep -w -E "<vorname>s?"` → 0, `git grep -i <nachname>` → 0, keine Laufwerkspfade `Users\<name>` im Stand.
- VER-03 (Klasse: veröffentlichte Dateien mit Plattform-Zeilenende): `newline="\n"` in `werkzeuge/datenbank.py` (finder-daten.json) und `werkzeuge/app_bauen.py` (herkunft.json, finder-preise.json, version.json). Tests `test_datenbank.BauMetadaten.test_bau_schreibt_lf`, `test_app.Bau.test_bau_schreibt_nur_lf`.
- VER-04 (Klasse: Dateiidentität über Pfadvergleich): `dieselbe_datei()` in `werkzeuge/preise_aktualisieren.py`; Test `test_meldung_gleich_ziel_bricht_vor_dem_abruf_ab` mit Hardlink-Fällen.
- VER-02 (bewusste Entscheidung, bitte bestätigen oder widersprechen): lokaler Pfad in nicht gepushtem Commit 0634588 bleibt; öffentliche Historie enthält dieselben Angabearten schon, Historie wird ohne Auftrag des Besitzers nicht umgeschrieben.

**Selbstprüfung:** Commit-Hook (Sammellauf `tests/alle-tests.ps1`) an c168282: Fehler 0; neue Tests ohne Korrektur rot, mit Korrektur grün (Mutanten siehe Bewertung).

**Prüffragen**
1. Gibt es weitere Schreibstellen veröffentlichter Dateien (gh-pages, Workflow) ohne festes LF oder weitere Pfadvergleiche für Dateiidentität?
2. Bleibt im Stand HEAD eine persönliche Angabe, ein lokaler Pfad oder eine Konto-URL, die r1 nicht erfasst hat?
3. Ist VER-02 als bewusste Entscheidung vertretbar, oder ist ein Push ohne Historienbereinigung ein Blocker?
