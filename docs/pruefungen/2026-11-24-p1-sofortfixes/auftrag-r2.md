# Nachprüfung P1 Sofortfixes r2 (Codex medium, schmal)

**Ziel:** Prüfen, ob P1-01…P1-05 aus r1 geschlossen sind und die Korrekturen keine neue Instanz derselben Klasse lassen. Keine Vollprüfung.

**Umfang:** nur der Diff ab `0fd3e8b` in `app/finder/bewertung.js` (`effizienz`, `bewerteModell` Z. 137–147), `app/finder/finder.js` (`ohneEmpfehlungText`, `notenBlock`, Warnung `ohne_note`, `rangZeile`, `offenText`, `rangliste`/`nummern`, Statusansage), `app/finder/finder.css` (Z. 52–60, `.ablage .knopf`), `app/finder/index.html` (Z. 21), `docs/punkteschema.md` §6–§7, Tests am Ende von `tests/test_bewertung.mjs` und `tests/test_finder_dom.mjs` sowie deren P1-02-Test. Bewertung: `bewertung-r1.md`. Andere Dateien nicht lesen.

**Fertigkriterien**
- `node --test tests/test_bewertung.mjs tests/test_finder_dom.mjs tests/test_sw_daten.mjs` → 0 fail
- Gleiche angezeigte Note → gleicher Rang unter „Beste Note“, „Günstigste“ und „Punkte je Euro“; „Punkte je Euro“ rechnet mit der angezeigten Note.
- CSS-Klasse `haupt` trifft nur noch Knöpfe (`.knopf.haupt`); Layout über `.hauptspalte`.
- Meldung ohne Empfehlung und Gruppe „Noch nicht bewertbar“ nennen den tatsächlichen Grund (keine Note / kein Preis / gemischt / kein Merkmal zählt).
- Punkteschema §6–§7 ohne Kappung und Klassenbedingungen.

**Selbstprüfung:** `tests/alle-tests.ps1` → Fehler 0, Warnungen 0. Gegenprobe: App-Dateien auf 0fd3e8b → 6 neue Tests rot. Browser 768 px: Preis und „Zum Angebot“ in einer Zeile.

**Bewusste Entscheidung:** Rangnummer ist in jeder Sortierung der Notenrang (unter „Günstigste“ nicht aufsteigend).

**Prüffragen**
1. Bleibt eine Stelle, an der Rang oder Reihenfolge an der ungerundeten Note oder der Listenposition statt an der angezeigten Zahl hängt?
2. Kann `ohneEmpfehlungText` bei einer Kombination aus Note, Preis, Budget einen falschen Grund nennen?
3. Bleibt eine Stelle mit „Datenblattwerte“/„zu wenig Daten“, die bei `art = "keine_merkmale"` erscheint?
