# Bewertung Codex P1 r3 (Nachprüfung, medium, 913490d)

Bericht: `codex-nach-20261124-102517.json` · Urteil: nicht bestanden (schwer 1) · alle 21 DOM-Tests grün · bewertet 24.11.2026 (Claude, Lead). **Rundenlimit erreicht (KERN §3); Besitzer hat am 24.11.2026 entschieden: beheben und schmale Runde 4.**

| ID | Schwere | Einordnung | Klasse | Suche | Korrektur | Probe |
|---|---|---|---|---|---|---|
| P1-03/P1-04 (Rest) | schwer (laut Bewertung eher gering: Hinweistext unvollständig, nicht falsch; Liste und Zeilenmarken nennen den Grund je Modell) | bestätigt: Wenn manche Modelle eine Note haben, keins davon aber einen Preis, und die Modelle mit Preis keine Note haben, sagt der Zweig „haben keine Note“. Er nennt nicht, warum (Datenblatt, kein Merkmal oder gemischt). | Meldung ohne Empfehlung zu grob (dritte Instanz) | `ohneEmpfehlungText` Zweig „mit Note“ in finder.js; andere Stellen sind je Modell eindeutig (r2-Suche) | Besitzer 24.11.: beheben, schmale r4. Der gemischte Zweig hängt „…, weil <Grund>“ an. Der Grund gilt für die Modelle mit Preis: Datenblattwerte fehlen, kein Merkmal zählt oder beides. | `test_finder_dom.mjs` „P1-03/P1-04 r3 …“ (kein Merkmal; beides) und die angepasste P1-03-Erwartung (Datenblatt). Mit finder.js aus 913490d sind beide rot, danach 59 von 59 grün. |

## Stand

Geschlossen über r1–r3: P1-01 (Rest bewusste Entscheidung, `bewertung-r2.md`), P1-02, P1-05; P1-03/P1-04 bis auf diesen Rest.
Verbrauch Codex: r1 831 Tsd., r2 263 Tsd., r3 395 Tsd. Tokens Eingabe (ungecacht 51 Tsd. bzw. 36 Tsd. in r2/r3).
