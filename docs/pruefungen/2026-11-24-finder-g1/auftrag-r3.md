# Nachprüfung Finder G1 r3 (medium, schmal)

**Ziel:** Prüfen, ob die Hinweise G1-R2-01 bis G1-R2-04 aus r2 behoben sind und die Korrekturen keine neue Instanz derselben Klasse lassen.

**Prüfgegenstand:** nur der Diff b7f5b24..a70332c in `app/finder/finder.js` und `tests/test_finder_dom.mjs` (Doku-Dateien dazwischen sind kein Prüfgegenstand); Einordnung, Klasse, Suche und Probe je Befund in `bewertung-r2.md`.

**Fertigkriterien**
- `node --test tests/test_finder_dom.mjs tests/test_bewertung.mjs` → 70/70 grün
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“ (Lead: Pre-commit-Hook auf a70332c „Fehler: 0 · Warnungen: 0“)
- Mit `finder.js` aus b7f5b24 sind G1-R2-01 und G1-R2-02 rot (Lead: 32 grün, 2 rot); Mutante „`disconnect()` hinter den Rücksprung“ in `glasBeobachten` → G1-04 rot; Mutante `const fehlt = !z.tp` in `punkteHerkunft` → G1-02 rot.

**Bekannte Grenzen:** Der Vergleichssprung (`scrollIntoView`, smooth) fragt die Bewegungseinstellung nur beim Start; eine während des Sprungs eingeschaltete Reduktion steuert der Browser. Offene Bereiche werden nach ihrer Klasse übernommen, nicht nach Inhalt.

**Prüffragen (je Klasse)**
1. G1-R2-01: Gibt es weitere Neuaufbauten (Schirm, Körper, Liste), nach denen ein aufgeklappter Bereich zugeht oder ein vorhandenes Fokusziel den Fokus nicht bekommt? Kann `bereicheOeffnen` einen Bereich öffnen, den niemand geöffnet hatte (z. B. bei Schirmwechsel)?
2. G1-R2-02: Bleibt nach dem Einschalten der Reduktion oder nach Schirmwechsel irgendeine Gleitbewegung aktiv? Ist der `change`-Hörer bei fehlendem `addEventListener` (ältere Browser) und fehlendem `matchMedia` sicher?
3. G1-R2-03/04: Erreichen die nachgeschärften Proben jetzt den gemeinten Zustand (0 Karten auf demselben Schirm; vorhandener Wert mit 0 Teilpunkten), und würden sie die genannten Rückfälle erkennen?
