# Bewertung Codex r7 – Finder-Veröffentlichung, geschnittenes Paket (22.11.2026)

Bericht: `codex-nach-20261122-174100.json`
- Prüfer: Codex gpt-6.2-sol high, Stand ae56dbe, 322 s.
- Verbrauch: 0,45 Mio. Eingabe-Tokens, davon 62 Tsd. ungecacht.
- Urteil: nicht bestanden. Geschlossen: R5-04, R6-01. Neu: R7-01 (schwer), R7-02 und R7-03 (mittel).

Einordnung nach Skill `pruefschleife` Schritt 5, belegt am Code bzw. im Wegwerf-Repo. **Noch nichts behoben**, weil eine weitere Runde der Besitzer entscheidet (O18).

| ID | Schwere | Einordnung | Beleg und Korrekturvorschlag |
|---|---|---|---|
| R7-01 | schwer | bestätigt. Im Wegwerf-Repo zeigt nach `git replace A B` der Befehl `ls-tree A` den Baum von B, `cat-file -p A:a.txt` liefert „fremd“, `rev-parse` bleibt bei A. Mit `GIT_NO_REPLACE_OBJECTS=1` kommt der Originalbaum. | `GIT_NO_REPLACE_OBJECTS=1` für alle Git-Aufrufe des Laufs setzen, auch `herkunft.py` und den Seitenbaum. Test: Ersetzungsreferenz auf einen Commit mit anderem `app/seite.txt` → gebaut wird der Originalinhalt. Erreichbar nur über eine lokale Ersetzungsreferenz im Repo; die Klasse ist dieselbe wie bei R5-04. |
| R7-02 | mittel | bestätigt. Laut Code erlaubt `ERLAUBT` den Modus 100755, `write_bytes` setzt aber kein Ausführungsbit, und `kopie_fehler` prüft keinen Modus. | Nur 100644 zulassen und bei 100755 abbrechen, so wie das Repo ist: alle 208 Einträge haben 100644, und gebaut wird mit `python -I`, nicht durch direkten Aufruf. |
| R7-03 | mittel | bestätigt. Laut Code liest `git()` mit `text=True`, und die Zeilenumwandlung von Python macht aus einem `\r` im Pfad ein `\n`. | `ls-tree -z` als Bytes lesen und Pfade ohne Umwandlung dekodieren; Steuerzeichen in Pfaden ablehnen. Unter Windows sind solche Namen ohnehin unzulässig, und der Commit enthält keine. |

Fehlalarme: 0 von 3. Keine bewusste Entscheidung, nichts ungeklärt.

Muster: Die Befunde werden weiter enger.
- R7-01 setzt einen gezielten lokalen Eingriff in die Objektauflösung des eigenen Repos voraus.
- R7-02 und R7-03 setzen Dateien voraus, die es im Repo nicht gibt.
- Alle drei Korrekturen sind mechanisch: eine Umgebungsvariable, ein Modus, Lesen als Bytes.
- Selbst belegt in dieser Runde: Der Bau aus der Objektkopie ist bytegleich zum Bau aus dem Arbeitsbaum mit derselben Herkunft (App cc449855d69a, 14 Dateien). Der Trockenlauf gegen das echte gh-pages (69e744d) ergab Baum 4112b5d21767, geprüft.
