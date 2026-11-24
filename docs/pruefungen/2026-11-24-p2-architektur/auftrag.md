# Architekturprüfung P2 Notenmodell (high, erst)

**Ziel:** Prüfen, ob der Entwurf `docs/recherche-ux/p2-entwurf.md` (P2a Daten und Rechnung, Schnittstelle P2b) widerspruchsfrei, abwärtsverträglich und mit dem gebauten Finder G1 vereinbar ist, bevor gebaut wird.

**Prüfgegenstand:** nur `docs/recherche-ux/p2-entwurf.md` (§1–§8). Abgleichen mit dem Code auf dem eingefrorenen Stand: `app/finder/bewertung.js` (ganz), `app/finder/finder.js:185–217`, `:450–500`, `:570–580`, `:730–760`, `:900–915`, `app/sw.js`, `werkzeuge/datenbank.py`, `daten/schema/kategorien.json`, `.github/workflows/finder-daten.yml`, `werkzeuge/herkunft.py`. Rahmen: `docs/recherche-ux/p2-plan.md`, D12, D13, D25, D26 in `docs/entscheidungen.md`.

**Fertigkriterien**
- Jede Ist-Aussage in §1 und §8 stimmt am Code, mit Zeilenangabe. §1 nennt Zeilen von `33fa490`, §8 Zeilen von `0996e86`.
- §2.5/A-6: Der Nachweisweg deckt jede `bewertung.js` ab, die beim P2a-Push im Service-Worker-Cache liegen kann.
- §3/A-1 und §4/A-2: Die Rechnungen für Alternativen und Notenblatt stimmen mit der angezeigten Note überein, auch mit Prioritäten-Reglern.
- §6 plus §8: Die Testliste erkennt zu jeder Regel den gemeinten Rückfall.
- Keine Regel verspricht etwas, das Daten oder Code nicht belegen (AGENTS.md).

**Selbstprüfung (Lead):** Ist-Aussagen in §8 am Code nachgelesen. `grep -n "gewichte(\|auswerten(" app/finder/*.js` ergibt 5 Treffer, alle mit `prio` außer `reglerFelder` (gewollt). `git diff --stat 33fa490 HEAD -- app/finder/bewertung.js` zeigt nur `gewichte` und `auswerten` geändert. Nichts gebaut, keine Tests betroffen.

**Bekannte Grenzen:** Offen beim Besitzer sind F-1 bis F-5 (Gewichtstabelle, Maße A/B, Testquelle, Quellen in eigener Datei, Umfang der Prüfsumme). Bitte Optionen bewerten, nicht entscheiden. Der Wortlaut der Ansicht gehört zu P2b und ist kein Prüfgegenstand. Die Zeilenangaben in §1 stammen von `33fa490`.

**Prüffragen:** P-1 bis P-8 (§7) und P-9 bis P-11 (§8). Zusätzlich:
1. Fehlt ein Weg, auf dem ein Push von `daten/schema/**` mit P2a eine laufende App (alt oder G1) bricht oder still andere Noten zeigt?
2. Ist die Dateihoheit in §5 und A-7 frei von Überschneidungen mit P0 (`finder.js`, Router, `tests/vorlagen/`) und P6 (Maßfelder)?
3. Gibt es eine einfachere Architektur mit demselben Nutzen? Zum Beispiel ohne Prüfsumme, mit Fassung nur von Hand und Test. Bitte mit Kosten und Risiko.
