# Prüfauftrag: Veröffentlichung App-Icon „Glas“ (Variante J)

**Ziel:** Das neue App-Icon (SVG + PNG) kann ohne Risiko für die laufende App auf GitHub Pages veröffentlicht werden (Prüfpunkt „Veröffentlichung“, kritisch).

**Fertigkriterien**
- Zwischen `origin/main` und `main` gehen nur Icon-Dateien, `werkzeuge/symbole.py` und STATUS.md mit (`git log origin/main..main`, `git diff --stat`).
- Manifest-Icons: jede in `app/manifest.webmanifest` genannte Datei existiert, Pixelmaß = `sizes`, `type` stimmt, je 192/512 für `any` und `maskable`; `apple-touch-icon.png` 180×180 ohne Alpha.
- Maskable-Icons: Motiv in der sicheren Zone (Kreis mit 40 % Radius um die Mitte), Hintergrund vollflächig deckend.
- SVGs enthalten keine externen Verweise, Skripte oder Fremd-URLs; PNGs ohne auffällige Metadaten.
- `werkzeuge/symbole.py`: Rendern mit Gerätefaktor 2, Größenprüfung und Verkleinerung korrekt; erzeugt alle fünf PNGs.
- Build übernimmt alle Icons (`werkzeuge/app_bauen.py`, Liste `STATISCH`), App-Stand/Cache des Service Workers ändert sich dadurch, sodass installierte Apps die neuen Dateien bekommen.

**Betroffene Dateien:** app/icons/icon.svg, app/icons/icon-maskable.svg, app/icons/*.png, werkzeuge/symbole.py, STATUS.md. Referenz: app/manifest.webmanifest, werkzeuge/app_bauen.py, app/sw.js (Cache, Benachrichtigungs-`icon`/`badge`), werkzeuge/veroeffentlichen.py (Kopf).

**Selbstprüfung:** `powershell -File tests/alle-tests.ps1` → Fehler 0, Warnungen 0. PNG-Maße per PIL: 192/512 RGBA, apple-touch 180 RGB. PNGs angesehen; Prüfstand 192/48 px mit Kreis- und Rundquadrat-Maske, hell/dunkel; `pruefe.mjs` ohne Meldungen.

**Bekannte Grenzen:** Gestaltung ist von Nico gewählt (keine Geschmacksprüfung). Android übernimmt neue WebAPK-Icons verzögert. Nicht auf echtem Handy geprüft. `badge` in sw.js nutzt schon vor dieser Änderung das Maskable-Icon.

**Prüffragen**
1. Geht mit dem Push etwas Unerwartetes mit (Commits, Dateien, Geheimnisse, persönliche Daten)?
2. Stimmen Manifest-Angaben und tatsächliche Dateien (Maß, Typ, purpose) überein; verletzt ein Icon die Maskable-Sicherzone?
3. Ist `symbole.py` korrekt (Faktor, Assert, Resize-Reihenfolge, RGB für apple-touch) und reproduzierbar?
4. Bekommt eine bereits installierte PWA die neuen Icons über Build-Hash/Service-Worker-Cache, oder bleibt alter Cache hängen?
5. Fehlt ein Test für ein im Betrieb kritisches Verhalten dieser Änderung?
