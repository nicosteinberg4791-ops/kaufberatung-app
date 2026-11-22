# Bewertung Codex r8 – Finder-Veröffentlichung, geschnittenes Paket (22.11.2026)

Bericht: `codex-nach-20261122-202919.json`
- Prüfer: Codex gpt-6.2-sol high, Stand fe31ae2, Basis 4cb0f2b, 314 s.
- Verbrauch: 0,63 Mio. Eingabe-Tokens, davon 71 Tsd. ungecacht.
- Urteil: nicht bestanden. Geschlossen: R7-01, R7-02. Neu: R8-01 und R8-02 (schwer), R8-03 (mittel). R8-02 und R8-03 führen R7-03 weiter.

Einordnung nach Skill `pruefschleife` Schritt 5, selbst nachgestellt. **Noch nichts behoben**, weil eine weitere Runde der Besitzer entscheidet (O19).

| ID | Schwere | Einordnung | Beleg und Korrekturvorschlag |
|---|---|---|---|
| R8-01 | schwer | bestätigt. Regression aus dieser Runde: `OHNE_ERSATZ` setzt `GIT_CONFIG_COUNT=1` und `GIT_CONFIG_KEY_0`, um den Graft-Hinweis abzuschalten. Nachgestellt: Mit vorhandenem `GIT_CONFIG_KEY_0=safe.directory` liefert `umgebung()` danach `advice.graftFileDeprecated`, die Einstellung des Aufrufers ist weg. In dieser Umgebung sind keine `GIT_CONFIG_*`-Variablen gesetzt, deshalb lief der Trockenlauf durch. Bei Codex (und typisch in CI) bricht der Lauf schon beim Abruf ab. | Nur `GIT_NO_REPLACE_OBJECTS` und `GIT_GRAFT_FILE` setzen. Den Hinweis entweder hinnehmen (nur stderr) oder als Eintrag `n` an vorhandene `GIT_CONFIG_COUNT=n` anhängen. Test: vorhandene Laufzeitkonfiguration bleibt in `umgebung()` und in `OHNE_ERSATZ` erhalten. |
| R8-02 | schwer | bestätigt, gemessen am eigenen Fertigkriterium („Steuerzeichen brechen ab“). Nachgestellt: Ein Pfad mit U+0085 (Kategorie Cc) wird angenommen. Der Pfad bleibt dabei unverändert und wird in der Kopie exakt verglichen, verfälscht wird nichts. Die Schwere ist eher mittel. | `unicodedata.category(c) == "Cc"` ablehnen, im Pfadtest einen C1-Fall ergänzen. |
| R8-03 | mittel | bestätigt, Wirkung nur Abbruch. Nachgestellt mit `app\b.txt`, `a.`, `..\raus.txt`, `app/x:y.txt`: Jeder Fall bricht ab, ohne etwas zu veröffentlichen. Geschrieben wird höchstens in die Wegwerf-Kopie, nie außerhalb (Prüfung `ziel in datei.parents`). Bei Zeichen wie `<>|?*` kann statt `SystemExit` ein `OSError` kommen, das ebenfalls abbricht. | Vor dem ersten Schreiben alle Pfade nach Windows-Regeln prüfen: kein `\`, keine Zeichen `<>:"|?*`, kein Punkt oder Leerzeichen am Ende, keine Gerätenamen (CON, NUL, COM1 …). |

Fehlalarme: 0 von 3. Keine bewusste Entscheidung, nichts ungeklärt.

Muster:
- R8-01 ist ein echter Rückschritt aus der Korrektur selbst (die Abschaltung des Hinweises war Zusatz, nicht verlangt).
- R8-02 und R8-03 betreffen Dateinamen, die es im Repo nicht gibt. Beide enden ohne Korrektur in einem Abbruch oder in einer exakt verglichenen Kopie.
- Alle drei Korrekturen sind mechanisch und klein.
