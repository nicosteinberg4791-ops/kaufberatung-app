# Nachprüfung P1 r4 (Codex medium, sehr schmal, vom Besitzer nach Rundenlimit freigegeben)

**Ziel:** Prüfen, ob der Rest von P1-03/P1-04 aus r3 geschlossen ist. Keine Vollprüfung.

**Umfang:** nur der Diff ab `913490d`: `app/finder/finder.js` Funktion `ohneEmpfehlungText` (Zweig „mit Note“, Helfer `grund`) und die Tests am Ende von `tests/test_finder_dom.mjs`. Bewertung: `bewertung-r3.md`. Andere Dateien nicht lesen.

**Fertigkriterien**
- `node --test tests/test_finder_dom.mjs` → 0 fail
- Haben manche Modelle eine Note, keins davon aber einen Preis, und haben die Modelle mit Preis keine Note, nennt die Meldung deren Grund: Datenblattwerte fehlen, kein Merkmal zählt oder beides.

**Selbstprüfung:** `tests/alle-tests.ps1` → Fehler 0. Gegenprobe: `finder.js` aus 913490d → 2 Tests rot.

**Prüffrage**
1. Nennt `ohneEmpfehlungText` jetzt in jedem Zweig, in dem keine Empfehlung entsteht, den Noten- und den Preisgrund vollständig und richtig?
