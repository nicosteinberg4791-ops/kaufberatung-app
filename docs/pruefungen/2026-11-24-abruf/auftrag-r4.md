# Nachprüfung r4 – Paket `abruf.py` (schmal, Besitzer O22 = A)

**Ziel:** Prüfen, ob R2-04a und R3-01 (`bewertung-r3.md`) geschlossen sind, ohne neue Lücke derselben Klasse. Nur der Diff ab 10d405f.

**Fertigkriterien**
- `python -I -B -m unittest discover -s tests -t tests -p test_abruf.py` → OK (33 Tests); Sammellauf im Commit-Hook „Fehler: 0“.
- Ein frischer Sperrvermerk ohne Zeichen mit eigenem Zeichenbild ergibt „Sperrvermerk ohne Grund“.
- `robots_ok` lehnt `@` in der Authority vor jedem Abruf ab.

**Dateien:** `werkzeuge/datenpflege/abruf.py` (`_sichtbar`, `gesperrt_bis`, `robots_ok`), `tests/test_abruf.py`.

**Bekannte Grenzen:** wie `auftrag.md`, `auftrag-r2.md`, `auftrag-r3.md`. Die Sichtbarkeit ist eine Näherung über Unicode-Kategorien; der Grund ist nur Meldungstext, die Sperre wirkt unabhängig davon.

**Prüffragen**
1. Liest der HTTP-Client nach der Ablehnung von `%` und `@` die Authority noch anders als `urlsplit`?
2. Gibt es noch einen frischen Sperrvermerk, dessen Grund ohne sichtbares Zeichen ausgegeben wird (praktisch relevante Fälle, keine Schriftart-Fragen)?
3. Sind R2-04a und R3-01 geschlossen?
