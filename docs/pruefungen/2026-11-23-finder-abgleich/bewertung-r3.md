# Bewertung Codex r3 (Nachprüfung, high, Basis 17599c1, Stand baf723f)

Bericht: `codex-nach-20261124-063305.json` · Urteil nicht bestanden · geschlossen: keiner · im Umfang offen: schwer 2, mittel 1 · Rundenlimit erreicht (KERN §3), nichts behoben, Entscheidung beim Besitzer (O21).

| Nr. | Schwere | Einordnung | Klasse | Suche |
|---|---|---|---|---|
| A2-01 | schwer | bestätigt: nach `OSError` von `os.lstat` (Z. 95) wird der Stempel trotzdem gelesen (Z. 102); gelingt das Lesen und ist der Stempel alt genug, entfällt die Wartezeit. Fertigkriterium „jeder andere `OSError` ergibt genau `ABSTAND`“ damit nicht erfüllt. Praktisch nur bei wechselnden Rechten/flüchtigem Fehler zwischen zwei Zugriffen | Fehlerzweig fällt in den Normalpfad zurück | `rg -n "except OSError:" werkzeuge/datenpflege/abruf.py` → Z. 55, 71 (Dateisperre: Fehler = keine Sperre bzw. Freigabe, kein Rückfall), Z. 95 einzige Instanz; R2-04 (`gesperrt_bis`) außerhalb des Umfangs |
| R2-02 | schwer (Lead: gering) | bestätigt: (a) `KeyboardInterrupt` zwischen Rückkehr von `mkdtemp` und Zuweisung an `bau` (Z. 144) lässt das Verzeichnis unbemerkt liegen; (b) wirft `bau.exists()` (Z. 161, z. B. `PermissionError`), entfällt die Warnung und der neue Fehler überdeckt den ursprünglichen. Betroffen ist nur das eigene `.kb-bau-*`-Verzeichnis, keine fremden Daten | Aufräumen/Melden im Ausnahmepfad nicht vollständig abgesichert | `rg -n "ignore_errors=True" werkzeuge/app_bauen.py` → nur Z. 160 |
| R2-03 | mittel (Lead: gering) | bestätigt: (a) `KeyboardInterrupt` zwischen `os.rmdir(z)` (Z. 149) und dem inneren `try` (Z. 152) lässt das zuvor leere Ziel fehlen; (b) scheitert zusätzlich `z.mkdir` (Z. 156), fehlt das Ziel und der zweite Fehler überdeckt den ersten. Kein Datenverlust (Ziel war leer) | nicht unterbrechungsfester Zwischenzustand | `rg -n "os.rmdir" werkzeuge/` → nur Z. 149 |

**Einschätzung Lead:** A2-01 ist eine echte Logiklücke mit kleiner, eindeutiger Korrektur (bei `OSError` den Stempel nicht lesen, `vergangen = None`). R2-02 und R2-03 betreffen nur Unterbrechungsfenster von wenigen Python-Anweisungen (Strg+C) oder Doppelfehler und berühren nur eigene bzw. leere Verzeichnisse; eine vollständige Absicherung gegen `KeyboardInterrupt` ist unter Windows nicht sauber möglich (keine Signalmaske), höchstens durch Umbau (Ziel nur „neu“, kein `rmdir`).

Vorlage für den Besitzer: STATUS.md, O21.

**Besitzer hat O21 entschieden (24.11.2026): A2-01 beheben, schmale Runde 4; R2-02 und R2-03 als Restrisiko angenommen.**

## Behebung

| Nr. | Korrektur | Probe |
|---|---|---|
| A2-01 | `sperre_holen`: `lstat` mit `try/except/else`; `FileNotFoundError` → keine Wartezeit, jeder andere `OSError` → `warte = ABSTAND` ohne Lesen, nur im `else`-Zweig entscheidet der Stempel | `test_fehler_beim_pruefen_liest_auch_einen_gueltigen_stempel_nicht`: gültiger, alter Stempel + `PermissionError`/`OSError(5)`/`NotADirectoryError` bei `lstat` → [ABSTAND]; ohne Korrektur rot (3 Unterfälle: []), mit Korrektur grün; Gegenprobe ohne Fehler [] |

Selbst geprüft: `tests/test_abruf.py` 26 OK, Sammellauf „Fehler: 0“, `datenbank.py pruefen` „Fehler 0“, `core.bare` false. Nachprüfung: `auftrag-r4.md`.
