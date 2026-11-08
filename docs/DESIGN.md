# DESIGN – App-Hülle

Gestaltung der Seite: DESIGN.md der Kaufberatung (Runden 2–6, „Tageslicht und Abend“, Geist, Tokens). Die Hülle fügt nur hinzu und nutzt dieselben Tokens.

- **Symbol:** dunkler Abendraum (Bühnenfarben `--stage-2` #0d1219 → `--stage` #05070b), Fensterlicht oben links (`--stage-beam`), Bildschirm 16:9 mit Haken (= entschieden), Fuß in `--stage-muted`. Keine Modellfarbe, weil die je einem Hersteller gehören. Maskierbar: Motiv auf 80 %.
- **Hinweiskarten** unten über der Safe-Area: Treffer mit 2-px-Rand `--good`, „Neue Fassung“ neutral. Eintritt 220 ms `--ease-out`, 12 px hoch plus Deckkraft (`@starting-style`); reduzierte Bewegung nur Deckkraft. Knöpfe 44 px, `:active` scale(.97).
- **Touch (`pointer: coarse`):** Reiter, Segmentknöpfe, Chips, Navigationslinks, Regler mind. 44 px; `--nav-h` 60 px. Hover der Seite ist schon an `(hover:hover) and (pointer:fine)` gebunden.
- **Farben im Manifest:** `#eef1f5` (`--bg` hell); Statusleiste über `theme-color` mit `prefers-color-scheme` hell #eef1f5 / dunkel #000000.
