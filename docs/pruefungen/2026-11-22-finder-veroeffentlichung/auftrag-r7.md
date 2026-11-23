# Prüfauftrag: Finder-Veröffentlichung, Nachprüfung r7 (kritisch, geschnittenes Paket)

**Ziel:** Prüfen, ob `werkzeuge/veroeffentlichen.py` R5-04 und R6-01 schließt, ohne neue Fehler einzuführen. Danach wird nur gh-pages veröffentlicht (O14). Der Besitzer hat das Paket geschnitten (O17).

**Umfang:** nur `werkzeuge/veroeffentlichen.py` und die Klasse `Veroeffentlichen` in `tests/test_app.py`. R5-01, R5-05 und R6-02 (`werkzeuge/datenpflege/abruf.py`, lokales Datenpflegewerkzeug, wird nicht ausgeliefert) sind ausgegliedert in ein eigenes Paket. Sie gehören nicht zu dieser Runde und sind nicht erneut zu melden.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“.
- R5-04 und R6-01 geschlossen (Einordnung und Behebung: `bewertung-r6.md`). Die Kriterien aus `auftrag-r6.md` zu `veroeffentlichen.py` gelten weiter.
- Die Bauquelle enthält genau die Dateien des geprüften Commits, unabhängig von lokalen Attributen. Ein Seitencommit entsteht nur, wenn seine Wurzelbaum-ID gleich dem aus dem Soll gebildeten Baum ist.

**Prüfgegenstand:** Diff `-Basis` (73a5df4) bis HEAD: `soll_baum`, `objekte_lesen`, `kopie_fehler`, `kopie_holen` und die Baumprüfung in `main`, dazu die neuen Tests und `_lauf(nach=...)`. 73a5df4 ändert nur Dokumentation.

**Selbstprüfung:** Neue Tests vor der Korrektur rot, danach grün: export-ignore, Link 120000, Abgleich, leerer Unterbaum. Sammellauf, `datenbank.py pruefen`, Bau und `veroeffentlichen.py --trocken` gegen das echte gh-pages: Ergebnisse stehen im Commit-Text.

**Bekannte Grenzen:** Der Lease schützt nur vor einem fremden Stand zwischen Abruf und Push. Dateisperren gelten nur gegen Läufe auf demselben Rechner. Die Bauquelle aus Blobs entspricht dem Checkout mit `* text=auto eol=lf` (`.gitattributes`); alle 208 Einträge des Repos sind 100644.

**Prüffragen**
1. Kann noch ein Inhalt in den gepushten Seitencommit gelangen, der nicht aus genau dem geprüften Commit gebaut und mit Baum-ID, Modus, Typ und Objekt-ID verglichen wurde?
2. Ist die Kopie aus Blobs gleichwertig zum Checkout (Zeilenenden, Pfade mit Umlauten, Unterordner), und fängt `kopie_holen` ungültige Pfade, Links, Untermodule und fehlende Objekte ab?
3. Kann `soll_baum` den Index des Seitenbaums oder der Quelle verändern, oder kann es eine ID bilden, die einem anderen Baum gleicht als dem Soll?
4. Steht im Diff etwas, das im öffentlichen Repo nicht stehen darf?
