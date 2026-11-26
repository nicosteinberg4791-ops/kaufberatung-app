# Nachprüfung r2 – P2a-1 gebaut (nur Korrekturen aus r1)

**Ziel:** Die vier Befunde aus r1 (`bewertung-r1.md`) sind am Code geschlossen, ohne neue Lücke derselben Klassen.

**Fertigkriterien:**
1. `node --test tests/test_bewertung.mjs` → 63 bestanden, 0 fail; `python -I -B -m unittest discover -s tests -t tests -p test_datenbank.py` → OK (32).
2. P2A1-01: `sichereQuelle` gibt die geprüfte Zeichenfolge zurück; eine gültige URL (auch 2000 Zeichen mit `'`, `"`, `{`) bleibt nach `datenPruefen`, in `methodik`, `notenblatt` und nach einem zweiten `datenPruefen` gleich.
3. P2A1-02: Test 44 enthält auf beiden Seiten „Freigabe nach dem Produktdatenstand → gültig“.
4. P2A1-03: Test 21 prüft automatisch die echten, frisch gebauten Daten (Werte, Teilpunkte, Belege, Quellen, Testquelle, Noten für Vorgabe und jede einzelne Antwort).
5. P2A1-04: `persoenlich` ist nur `true`, wenn ein Regler ≠ 1 auf ein Feld wirkt, das für dieses Modell anwendbar ist.

**Dateien:** Diff ab `-Basis` (`app/finder/bewertung.js`: `reglerWirken`, Aufruf in `notenblatt`, `sichereQuelle`; `tests/test_bewertung.mjs`: Importe und die Tests „P2A1-01“ bis „P2A1-04“ am Ende; `tests/test_datenbank.py`: `test_url`, `test_fassung_und_testquelle`).

**Selbstprüfung:** Kriterium 1 grün. Mutanten M1–M5 je einzeln rot (Tabelle in `bewertung-r1.md`). Gesamtlauf im Commit-Hook.

**Bekannte Grenzen:** `sichereUrl` (Testlinks, Preise) speichert weiter `href`; §9.6 legt sie als unverändert fest, ein zweiter Lauf auf demselben Objekt kommt in App und Service Worker nicht vor (Einordnung in `bewertung-r1.md`). Der Live-Test braucht `python` im Pfad (Umgebungsvariable `PYTHON` möglich). Test 44 läuft weiter getrennt in Bau und Client, mit denselben Fällen.

**Prüffragen:**
1. Öffnet die Rückgabe der Originalzeichenfolge in `sichereQuelle` eine Lücke (z. B. ein Zeichen, das `new URL` anders liest als die Textprüfung)?
2. Gibt es eine weitere Stelle, an der ein geprüfter Wert normalisiert gespeichert und später erneut geprüft wird?
3. Bleibt eine weitere Angabe im Notenblatt modellunabhängig, obwohl sie sich auf das Modell bezieht?
