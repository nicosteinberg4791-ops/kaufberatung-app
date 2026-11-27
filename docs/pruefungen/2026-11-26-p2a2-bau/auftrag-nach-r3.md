# Nachprüfung r3 – P2a-2 Korrektur r3 (offen: P2A2-BAU-02, -03, -06, -04-TEST)

**Ziel:** Nur prüfen, ob die vier Korrekturen r3 ihre Klasse schließen. Keine Vollprüfung, keine anderen Befunde, kein Mutantenlauf (Ergebnis in `bewertung-r3.md`, Selbstprüfung).

**Budget:** nur die genannten Funktionen lesen; kein Durchsuchen des ganzen Repos, keine Sammelläufe. Eine Speicherprobe je Klassenfrage genügt.

**Korrekturstellen (Diff ab 676771b):**
- `werkzeuge/datenbank.py` `fassung_gegen_fehler` (Vordurchlauf vor der ersten `projektion`)
- `tests/test_bewertung.mjs` `vergleich37` (Zähler `bearbeitet`, `soll`), dritter Fall von Test 37
- `tests/test_datenbank.py` `test_referenz_gerundet_und_ohne_projektion` (Ende), `test_frage_id_isoliert`, Prüfwort in `test_referenz_fassung_explizit_ungueltig`
- `tests/test_freigabe.py` `Repos.blob_bytes`, letzte Zusicherung von `test_datei_an_kandidat_gebunden`

**Bekannte Grenzen:** wie r2 (Interpreter, lokaler Ref `origin/gh-pages`).

**Klassenfragen (je eine Antwort):**
1. BAU-02: Hängt Test 37 noch an einer Größe des Verlaufs oder der Datei statt am Vergleich je Fassung?
2. BAU-03: Kann `projektion` noch laufen, bevor Schema-Version und alle Fassungsangaben der Referenz geprüft sind?
3. BAU-06: Bleibt ein Bestandteil der Projektion aus §9.3 bei seiner isolierten Änderung grün?
4. BAU-04-TEST: Vergleicht eine Bytegegenprobe noch aufbereitete statt unveränderter Bytes?
