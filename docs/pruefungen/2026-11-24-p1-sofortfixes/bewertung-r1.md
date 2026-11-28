# Bewertung Codex P1 r1 (Erstprüfung, medium, 0fd3e8b)

Bericht: `codex-erst-20261124-084611.json` · Urteil: nicht bestanden (schwer 1, mittel 3, gering 1) · bewertet 24.11.2026 (Claude, Lead).

| ID | Schwere | Einordnung | Klasse | Suche | Korrektur | Probe |
|---|---|---|---|---|---|---|
| P1-01 | schwer | bestätigt: Rangnummer nur bei Sortierung „note“ an die angezeigte Zahl gebunden, sonst Position; Effizienz mit ungerundeter Note | Rang/Reihenfolge aus ungerundeter Note oder aus der Listenposition statt aus der angezeigten Zahl | `rg -n "e\.note \/\|Math.round\(.*note\)\|nummern" app/finder` → `effizienz()` (bewertung.js), `nummern` (finder.js); Aufpreis/Spar rechnen bewusst ungerundet (Schema §7), Anzeige dort gerundet | Rang = Notenrang aus der angezeigten Zahl in jeder Sortierung (1 + Anzahl mit höherer angezeigter Note); `effizienz()` mit `anzeige(e)` | `test_bewertung.mjs` „P1-01: Punkte je Euro …“ (84,6/100 € vs. 85,4/100,50 €, plus Dreierfall); `test_finder_dom.mjs` „P1-01: … gleicher Rang in jeder Sortierung“ (note/preis/effizienz) |
| P1-02 | mittel | bestätigt: `.haupt` war Layout- und Knopfklasse; trifft Angebotslink, „Neu laden“ (finder.js, finder-app.js), „Weiter“/„Ergebnis zeigen“ (dort von `.weiter .knopf` überdeckt) und Ablage | doppelt belegter Klassenname | `rg -n "\bhaupt\b" app/` → index.html `main`, finder.css Z. 52/59/150, 5 Knöpfe in finder.js, 1 in finder-app.js | Layoutklasse in `.hauptspalte` umbenannt (index.html, finder.css); Rückstell-Workaround in `.ablage .knopf` entfernt | `test_finder_dom.mjs` „P1-02 …“: jeder CSS-Selektor mit `.haupt` ist genau `.knopf.haupt`; jede Klassenangabe mit `haupt` in finder.js/finder-app.js enthält `knopf`; `main` trägt `hauptspalte` |
| P1-03 | mittel | bestätigt: Meldung prüfte nur „irgendein Modell hat Note“ | Meldung ohne Empfehlung aus zu grober Bedingung | `rg -n "kennen wir gerade keinen Preis" app/` → nur finder.js | `ohneEmpfehlungText(r)`: keine Note → Datenblatt bzw. kein Merkmal; kein Preis → „kein Preis“; sonst gemischter Text (Modelle mit Note ohne Preis, mit Preis über Budget ohne Note) | `test_finder_dom.mjs` „P1-03 …“ (Budget 95 €, ein Modell 100,50 € ohne Note; plus Gegenfall ganz ohne Preis) |
| P1-04 | mittel | bestätigt: alle wirksamen Gewichte 0 → keine Note, `fehlend` leer, Ansicht nennt fehlende Datenblattwerte | Ursache „keine Note“ nicht unterschieden | `rg -n "Datenblattwerte\|zu wenig Daten" app/finder` → Gruppenhilfe, Zeilenmarke, Notenblock der Empfehlung, Warnung `ohne_note`, Statusansage | `bewerteModell`: `art = "keine_merkmale"` bei Gewichtssumme 0; alle fünf Stellen unterscheiden den Grund. Abweisen in `datenPruefen` verworfen: Antworten können Gewichte auf 0 setzen, das ist statisch nicht vollständig prüfbar | `test_bewertung.mjs` „P1-04 …“ (Feldgewichte 0, Antwort setzt 0, Gegenfall Lücke); `test_finder_dom.mjs` „P1-04 …“ (keine „Datenblattwerte“/„zu wenig Daten“, Gegenfall „fehlen zu viele Datenblattwerte“) |
| P1-05 | gering | bestätigt: Formel mit `min(84, …)`, Klassensprung und „gleiche Klasse“ in §6/§7 | veraltete Doku nach D12 | `rg -n "84\|Klasse" docs/punkteschema.md` → §6 Formel/Beispiele, §7 Effizienz, Text, Spar, Beispiele | Formel, Beispiele, Bezug A, Aufpreis-/Spar-Regeln auf D12; `text_gleichauf` ergänzt; Beispielblock als Vorgeschichte gekennzeichnet | Doku, keine Testprobe (Abgleich mit `bewertung.js` Z. 107–245 von Hand) |

## Probe rot → grün

- Rot: App-Dateien `bewertung.js`, `finder.js`, `finder.css`, `index.html` auf 0fd3e8b, neue Tests: 6 von 55 scheitern (genau die sechs P1-Tests oben).
- Grün: `node --test tests/test_bewertung.mjs tests/test_finder_dom.mjs tests/test_sw_daten.mjs` → 57 pass, 0 fail.

## Gestaltungsentscheidung zu P1-01

Die Rangnummer bedeutet jetzt in jeder Sortierung „Platz nach Note“. Unter „Günstigste“ und „Punkte je Euro“ stehen die Nummern deshalb nicht aufsteigend. Alternative wäre, die Nummern dort auszublenden. Gewählt nach Codex-Vorschlag und Fertigkriterium; der Besitzer kann umentscheiden.

## Selbstprüfung nach Korrektur

- `powershell -File tests/alle-tests.ps1` → `Fehler: 0 · Warnungen: 0`.
- `python -I werkzeuge/app_bauen.py` → App 76b1d4d68b99 (Inhalt Version 30).
- Browser (eigener Port 8791, Fernseher bis 700 €): `main.hauptspalte`; bei 768 px stehen Preis und „Zum Angebot“ in einer Zeile (beide oben bei 529 px), bei 375 px bricht der Knopf berechtigt um (Preis plus 10rem passen nicht in 306 px).
