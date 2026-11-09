# Bewertung Codex R1 (high, erst) – Veröffentlichung App-Icon „Glas“

| Befund | Schwere | Einordnung | Begründung / Korrektur |
|---|---|---|---|
| B1 Maskable-SVG fehlt im Veröffentlichungspaket | schwer | Fehlalarm | `app/icons/icon-maskable.svg` ist nur die Vorlage, aus der `werkzeuge/symbole.py` (Zeile 35) die Maskable-PNGs und `apple-touch-icon.png` rendert. Zur Laufzeit verweist nichts darauf: Manifest nennt nur PNGs (`purpose maskable` → `icon-maskable-192/512.png`), Seite nutzt `icons/icon.svg` (Favicon) und `apple-touch-icon.png` (`app_bauen.py` Zeilen 72–73), `sw.js` nur PNGs. Suche nach `icon-maskable.svg` in *.py/*.js/*.mjs/*.html/*.webmanifest: einziger Treffer `symbole.py:35`. `STATISCH` ist seit der geprüften App-Hülle (ea41852) unverändert und nicht Teil dieses Diffs. Ursache: Fertigkriterium im Auftrag ungenau („alle Icons“); gemeint war: alle zur Laufzeit verwendeten Icon-Dateien. Keine Änderung. |
