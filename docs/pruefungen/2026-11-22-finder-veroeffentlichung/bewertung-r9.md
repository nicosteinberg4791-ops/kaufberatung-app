# Bewertung Codex r9 – Finder-Veröffentlichung, schmale Nachprüfung (23.11.2026)

Bericht: `codex-nach-20261123-065737.json`
- Prüfer: Codex gpt-6.2-sol high, Stand 00bfb96, Basis e7a30fa, 313 s.
- Verbrauch: 0,50 Mio. Eingabe-Tokens, davon 61 Tsd. ungecacht.
- Urteil: nicht bestanden. Geschlossen: R8-01, R8-02. Neu: R9-01 (schwer), R9-02 (mittel). Beide führen R8-03 weiter.

Einordnung nach Skill `pruefschleife` Schritt 5, selbst nachgestellt. **Noch nichts behoben**, weil eine weitere Runde oder die Veröffentlichung der Besitzer entscheidet (O20).

| ID | Schwere | Einordnung | Beleg und Korrekturvorschlag |
|---|---|---|---|
| R9-01 | schwer | bestätigt, gemessen am eigenen Fertigkriterium („vor dem ersten Schreiben“). Nachgestellt: `windows_pfad_fehler` lässt eine Namenskomponente aus 256 Zeichen durch; das Schreiben in die Wegwerf-Kopie scheitert dann mit `FileNotFoundError` (errno 2), der Lauf bricht ab. Davor geschriebene Dateien liegen nur in der Wegwerf-Kopie. Die Schwere ist eher gering. | Jede Komponente in UTF-16-Codeeinheiten auf höchstens 255 prüfen; Test mit einem gültigen Pfad davor, keine Datei geschrieben. |
| R9-02 | mittel | bestätigt. Nachgestellt: `werkzeuge/veroeffentlichen.py` und `werkzeuge/veroef~1.py` passieren gemeinsam, und auf diesem Volume ist die 8.3-Kurznamenvergabe aktiv (`samefile` = True). Die zweite Datei überschreibt die erste in der Wegwerf-Kopie; der exakte Abgleich bricht danach ab. Veröffentlicht wird nichts. | Komponenten der Form `<Name>~<Ziffern>[.<Endung>]` vorab ablehnen; Test mit dem aufgelösten Kurznamen. |

Fehlalarme: 0 von 2. Keine bewusste Entscheidung, nichts ungeklärt.

Muster:
- Seit r7 finden die Runden neue Randfälle eines einzigen, selbst gesetzten Kriteriums (Pfade unter Windows). Die eigentliche Schutzeigenschaft hält in allen gemeldeten Fällen: Geschrieben wird nur in die Wegwerf-Kopie, der exakte Abgleich danach stoppt jede Abweichung, nichts Falsches wird veröffentlicht.
- Beide Korrekturen sind je zwei bis drei Zeilen und ein Testfall.

## Eigenbefund nach r9 (behoben)

Beim Commit 4d88574 setzte der Commit-Hook `core.bare=true` in die gemeinsame `.git/config`, `git status` brach danach ab. Ursache: `test_laufzeitkonfiguration_bleibt` (aus 00bfb96) rief `git init` mit der Umgebung des Aufrufers auf, im Hook ist dort `GIT_DIR` gesetzt. Nachgestellt in einem Wegwerf-Repo mit Worktree. Korrektur: Der Test entfernt wie die übrigen Git-Tests alle `GIT_*`-Variablen; rot→grün mit `GIT_DIR` auf ein Wegwerf-Worktree belegt. `core.bare` zurück auf `false`, sonst war die Konfiguration unverändert. Nur Testcode, `veroeffentlichen.py` und `herkunft.py` unverändert.
