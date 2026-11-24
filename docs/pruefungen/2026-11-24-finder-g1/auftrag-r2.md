# Nachprüfung Finder G1 r2 (medium, schmal)

**Ziel:** Prüfen, ob G1-01 bis G1-05 aus r1 behoben sind und die Korrekturen keine neue Instanz derselben Klasse lassen.

**Prüfgegenstand:** nur der Diff 54052c3..b7f5b24 (`app/finder/finder.js`, `tests/test_finder_dom.mjs`); Befunde und Einordnung in `bewertung-r1.md`.

**Fertigkriterien**
- `node --test tests/test_finder_dom.mjs tests/test_bewertung.mjs` → 68/68 grün
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“
- Die Proben G1-01…G1-05 sind gegen `finder.js` aus 54052c3 rot (Lead: 27 grün, 5 rot).

**Selbstprüfung:** wie oben, Pre-commit-Hook auf b7f5b24 „Fehler: 0 · Warnungen: 0“.

**Prüffragen (je Klasse)**
1. G1-01: Gibt es weitere Wege, auf denen sich die bewerteten Felder ändern, ohne dass das Regler-Panel neu gebaut wird (z. B. Fragenschirm → Ergebnis, Filter, Kategorie)? Geht beim Neuaufbau Fokus oder Reglerstufe verloren?
2. G1-02: Liest irgendeine andere Stelle einen fehlenden Wert als 0 Punkte vor (Rangliste, Vergleich)?
3. G1-03: Vergleichen Rangliste und Vergleich jetzt überall die angezeigten (gerundeten) Zahlen?
4. G1-04/G1-05: Bleiben Beobachter oder Animationen nach Schirmwechsel oder geänderter Bewegungseinstellung irgendwo hängen?
