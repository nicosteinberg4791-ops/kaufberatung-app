# Erstprüfung – P2a-2 gebaut (Gewichtsfassung, Referenzvergleich, Freigabeschranke)

**Ziel:** Prüfen, ob der Bau von P2a-2 (Diff ab `-Basis dbfdca6` bis HEAD) den Entwurf `docs/recherche-ux/p2-entwurf.md` §2.1, §9.1, §9.3 und die Tests 3, 6, 37–42, 47, 48 (§9.9) erfüllt.

**Fertigkriterien:**
1. `powershell -File tests/alle-tests.ps1` → Fehler 0.
2. `python -I werkzeuge/datenbank.py pruefen` → Fehler 0; jede Kategorie in `daten/schema/kategorien.json` trägt `gewichte_version` `{nummer 1, stand 2026-11-26}`.
3. `python -I docs/pruefungen/2026-11-26-p2a2-bau/mutanten.py <projektordner>` → Original grün, jede Mutante rot, Arbeitsbaum danach sauber.
4. Referenzvergleich §9.3: Vorbedingungen für Kandidat und Referenz vor der Projektion; Projektion in Normalform und Reihenfolge; Regeln gleiche/abweichende/kleinere Nummer, Referenz mit Schema 1.
5. Referenz in allen drei Wegen = `herkunft` der zu ersetzenden Online-Datei, streng; lokal nur über `ls-remote` (nie vorhandener Ref); Datenworkflow je Versuch neuer Eltern-SHA, Commit nur aus `eltern`, Push mit Lease.
6. Fassung 1 ändert keine Note (Test 42), jede umlaufende `bewertung.js` verhält sich wie mit den Live-Daten (Test 37).

**Dateien (Stand HEAD):** `werkzeuge/datenbank.py` Z. 1–10, 105–113, 213–360 (`_doppelt` … `schema_fehler`), 634–700 (`bauen`, `main`, `--gegen`) · `werkzeuge/freigabe.py` (ganz, neu) · `werkzeuge/veroeffentlichen.py` Z. 314–331 · `.github/workflows/finder-daten.yml` Z. 1–25, 55–70 · `daten/schema/kategorien.json` · `tests/test_datenbank.py` ab Z. 434 (`Gewichtsfassung`) · `tests/test_freigabe.py` (neu) · `tests/test_app.py` `Veroeffentlichen` (47(b), (c)) · `tests/test_bewertung.mjs` Z. 1096–1260 · Doku `docs/punkteschema.md` §7a, Kopf von `p2-entwurf.md`.

**Selbstprüfung:** Sammellauf Fehler 0, Warnungen 0. `pruefen` 14 Dateien, 418 Varianten, Fehler 0. Mutantenlauf: 9 Mutanten, 11 Zielläufe rot, Original 11/11 grün. `pruefen --gegen` gegen das echte gh-pages (Herkunft 7339711, Schema 1): 0 Fehler.

**Bekannte Abweichungen (im Entwurfskopf benannt, keine Befunde, solange begründet):** neues Modul `werkzeuge/freigabe.py` außerhalb der Dateihoheit §5; eine neue Kategorie ohne Gegenstück in der Referenz wird nur auf ihre Form geprüft; Test 37 vergleicht gegen einen Bau mit Werkzeug und Schema der Live-Herkunft. Der Preis-Push (`preise_aktualisieren.py`, 47(i)–(k)) ist schon geprüft und nicht im Umfang. Offene Besitzerfragen F-2, F-3 sind keine Befunde.

**Prüffragen:**
1. Gibt es eine Schemaänderung, die eine Note ändert, aber die Projektion gleich lässt (oder umgekehrt), oder eine, die an den Vorbedingungen vorbeikommt und den Client die Datei verwerfen lässt?
2. Kann einer der drei Wege gegen eine andere Referenz als die `herkunft` der zu ersetzenden Datei prüfen, oder nach bestandener Prüfung etwas anderes pushen als geprüft (Wettlauf, gelöschter oder versetzter Zweig)?
3. Wird Test 37 bei einer naheliegenden Schemaänderung seit dem Live-Stand rot, und hängt er an einer Annahme, die bei künftigen Live-Ständen bricht?
4. Gibt es eine Regel aus §9.3 ohne Test, oder einen Test, der bei einer naheliegenden Mutante grün bliebe?
5. Lässt eine neue Kategorie ohne Referenz eine Lücke, die mehr als die Form betrifft?
