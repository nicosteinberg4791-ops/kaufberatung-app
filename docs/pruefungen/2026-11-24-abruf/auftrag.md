# Prüfauftrag Paket `abruf.py` (Erstprüfung)

**Ziel:** Prüfen, ob die vom Besitzer geschnittenen offenen Befunde zum lokalen Abrufhelfer der Datenpflege vollständig und ohne neue Lücken behoben sind.

**Umfang (Besitzer, 24.11.2026):** R5-05 und R6-02 (`docs/pruefungen/2026-11-22-finder-veroeffentlichung/bewertung-r6.md`), R2-04 (`docs/pruefungen/2026-11-23-finder-abgleich/bewertung-r2.md`), Kodierung der Git-Test-Helfer in `tests/test_app.py`. R5-01 gilt als durch A2 behoben (Markierung `laeuft`, Tests `test_zeitstempel_vor_dem_http_versuch`, `test_abbruch_nach_verzoegertem_versand_haelt_den_abstand`); bitte bestätigen oder widerlegen. Nicht im Umfang: R10-01 (`veroeffentlichen.py`).

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“ (ohne `GIT_*`-Umgebung).
- `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“.
- Port 0 wird abgelehnt, nur ein fehlender Port heißt Standardport; die robots-Ablage ist eindeutig je (Schema, Host, Port) und unter Windows zulässig.
- Sperr-, Zeit- und Sperrvermerkdatei teilen einen Windows-tauglichen, eindeutigen Schlüssel je Host; vorhandene Stempel gewöhnlicher Hostnamen gelten weiter.
- `gesperrt_bis` gibt `None` nur bei sicher fehlendem oder über 30 min altem, normalem Sperrvermerk zurück; alles andere sperrt mit nicht leerem Grund.
- Git-Helfer der Veröffentlichungstests dekodieren UTF-8 (Test mit Umlaut im Seiteninhalt).

**Dateien:** `werkzeuge/datenpflege/abruf.py` Z. 15–67 (Schlüssel), 69–110 (Sperre/Stempel), 180–235 (`gesperrt_bis`, `holen`), 340–378 (Ursprung, Ablage) · `tests/test_abruf.py` Z. 128–200, 453–560 · `tests/test_app.py` Git-Helfer (`g`, `zeige`, `encoding="utf-8"`).

**Selbstprüfung:** neue Tests vor der Korrektur rot (fehlende Funktionen, Port 0 ohne `ValueError`, Link ohne Ziel/leerer/unlesbarer Vermerk = frei, `gepr�ft` statt `geprüft`), danach grün; Sammellauf und Datenbankprüfung siehe Fertigkriterien.

**Bekannte Grenzen:** Ein Sperrvermerk mit Änderungszeit in der Zukunft sperrt bis zu dieser Zeit plus 30 min (fail-closed). Ein nicht normaler Sperrvermerk sperrt dauerhaft, bis er von Hand entfernt wird. Gleiche Server unter verschiedenen Schreibweisen (z. B. Punkt am Ende) haben getrennte Takte (wie bisher). Bedrohungsmodell: lokales Werkzeug, kein feindlicher Prozess mit Schreibrecht im Temp-Ordner (Besitzer, A1-01/R2-01).

**Prüffragen**
1. Kann ein Host-Schlüssel zweier verschiedener Hosts gleich sein oder unter Windows unzulässig werden (Gerätenamen, Länge, Zeichen)?
2. Gibt es außer Port 0 weitere Port-Schreibweisen, die still auf den Standardport fallen oder Ursprünge vermischen?
3. Gibt es einen Zustand des Sperrvermerks, der weiterhin als „nicht gesperrt“ gilt, obwohl er nicht sicher fehlt oder abgelaufen ist?
4. Liest oder schreibt noch eine Stelle Dateien im Takt-Ordner am gemeinsamen Schlüssel vorbei?
5. Ist R5-01 im heutigen Stand geschlossen?
