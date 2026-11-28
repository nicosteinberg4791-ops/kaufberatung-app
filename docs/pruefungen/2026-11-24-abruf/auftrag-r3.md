# Nachprüfung r3 – Paket `abruf.py` (letzte Runde nach KERN §3)

**Ziel:** Prüfen, ob die Korrekturen zu den r2-Befunden (`bewertung-r2.md`) die Befunde schließen, ohne neue Lücken derselben Klassen.

**Fertigkriterien**
- `python -I -B -m unittest discover -s tests -t tests -p test_abruf.py` → OK (33 Tests); Sammellauf im Commit-Hook „Fehler: 0“.
- `robots_ok` lehnt `%` in der Authority vor jedem Abruf ab; `%` im Pfad bleibt erlaubt.
- Jeder Takt-Dateiname (Schlüssel plus `.lock`, `.zeit`, `.zeit.neu`, `.gesperrt`) ist höchstens 255 Zeichen lang.
- Ein frischer Sperrvermerk ohne druckbares, sichtbares Zeichen ergibt „Sperrvermerk ohne Grund“.

**Dateien:** Diff ab 158fde1: `werkzeuge/datenpflege/abruf.py` (`host_schluessel`, `gesperrt_bis`, `robots_ok`), `tests/test_abruf.py`.

**Bekannte Grenzen:** wie `auftrag.md` und `auftrag-r2.md`; IPv6-Zonen-IDs sind jetzt unzulässig (bewusst). Bedrohungsmodell: lokales Werkzeug für die gepflegten Shop-URLs, kein feindlicher Prozess im Temp-Ordner.

**Prüffragen**
1. Liest der HTTP-Client nach der Ablehnung von `%` die Authority noch irgendwo anders als `urlsplit` (Host, Port, Ursprung)?
2. Gibt es noch einen Takt-Dateinamen über 255 Zeichen oder einen alten, nutzbaren Stempel, der durch die Grenze 246 übergangen wird?
3. Sind R2-01, R2-02, R2-03 und R2-04a geschlossen?
