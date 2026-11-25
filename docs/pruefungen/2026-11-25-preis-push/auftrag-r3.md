# Nachprüfung r3 – Preis-Push (nur Korrekturen aus r2, Neuansatz O29)

**Ziel:** Die fünf Befunde aus r2 (`bewertung-r2.md`) sind am Code geschlossen; die Klassen R2-01 und R2-04 sind durch Weglassen bzw. ein festes Ziel beseitigt, nicht weiter geflickt.

**Fertigkriterien:**
1. `python -I -B -m unittest discover -s tests -t tests -p test_app.py -k PreisPush -k PushSchutz -k Workflow` → OK (33 Tests, 1 übersprungen: Symlink unter Windows ohne Recht).
2. R2-01: Nach `push()` schreibt nichts mehr auf Index, HEAD oder lokalen Zweig (kein `update-ref`, kein `reset`).
3. R2-02: `main()` ruft `ziel_pruefen()` bei `--push`/`--nur-push` vor `lies_alt`, `lade_skript` und `aktualisiere` auf.
4. R2-03: `commit_fehler` liest `ls-tree -z` als Bytes und vergleicht Pfade bytegenau.
5. R2-04: `git_umgebung()` entfernt `GIT_CONFIG_COUNT/KEY_n/VALUE_n/PARAMETERS`; `ls-remote`, `fetch` und `push` gehen an genau die URL aus `ziel_url()`; gesetztes `url.*.pushInsteadOf` → Abbruch.
6. R2-05: Kandidat ohne `preise.json` → Grund statt `KeyError`.

**Dateien:** Diff ab `-Basis` (`werkzeuge/preise_aktualisieren.py`: `umgebungs_konfig`, `git_umgebung`, `ziel_pruefen`, `git_bytes`, `ziel_url`, `eltern_holen`, `preis_commit`, `commit_fehler`, `push`, Anfang von `main`; `tests/test_app.py`: `PreisPush`). Der Stand von r2 ist Basis, damit die Korrekturen zusammen sichtbar sind.

**Selbstprüfung:** Kriterium 1 grün; neun Mutanten je einzeln rot (Liste in `bewertung-r2.md`, Abschnitt „Korrigiert“); Gesamtlauf im Commit-Hook grün.

**Bekannte Grenzen:** wie r1/r2 (Push von Hand, keine Hooks bei `commit-tree`, nicht in echtem Actions gelaufen). Ein Symlink, der zwischen `ziel_pruefen` und dem Schreiben eingesetzt wird (TOCTOU), bleibt offen. `insteadOf` aus Konfigurationsdateien wirkt weiter, aber auf Lesen und Schreiben gleich. Lokal bleibt `preise.json` nach dem Push als Änderung stehen; `veroeffentlichen.py` bricht dann sicher ab.

**Prüffragen:**
1. Öffnet eine Korrektur eine neue Lücke, besonders: Kommt der Push in Actions mit der URL statt `origin` noch an die Zugangsdaten von `actions/checkout` (extraheader je URL, `.github/workflows/preise.yml`)?
2. Gibt es noch einen Weg, dass `ls-remote`/`fetch` und `push` verschiedene Ziele treffen?
3. Gibt es in `push()` oder `main()` noch einen Lese- oder Schreibzugriff auf Ziel, Index oder Zweig vor bzw. außerhalb der Prüfungen?
