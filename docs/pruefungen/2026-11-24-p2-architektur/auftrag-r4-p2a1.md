# Nachprüfung r4 – P2a-1 Rechnung und Schnittstelle (high, nach, O25 = B)

**Ziel:** Prüfen, ob die Korrekturen zu R2-04, R3-01, R2-06, R2-07 und R3-02 (`bewertung-r3-p2a1.md`) im Entwurf `docs/recherche-ux/p2-entwurf.md` die Befunde samt Klasse schließen, ohne neue Widersprüche zu erzeugen. R2-03 war ein Fehlalarm (dort begründet).

**Prüfgegenstand:** nur der Diff von `docs/recherche-ux/p2-entwurf.md` ab `5756026`, soweit er §1 (Z. 8–12), §2.6 (Z. 83–87), §4 (Z. 115, 126), §8 A-1/A-4 und Tests 33/35 (Z. 178, 181, 193), §9.2 (Z. 207), §9.5 (Z. 239), §9.6 (Z. 248–258), §9.7 (Z. 263) und die Tests 21 und 44 betrifft. Code nur, wo der Entwurf sich darauf stützt: `app/finder/bewertung.js` (`gewichte`, `bewerteModell`, `datenPruefen`, `kennungOk`, `wertOk`, `istName`), `werkzeuge/datenbank.py:20`, `:44–62`, `:300–330`, `daten/schema/kategorien.json`. **Nicht** Gegenstand: P2a-2 (§2.1, §5 Zeile `preise_aktualisieren.py`, §7 R6, §9.1, §9.3, Tests 6, 38–42, 47, 48; eigene Runde) und F-1 … F-5.

**Ersetzte Regeln (alt, gelten nicht mehr):**
- alt §9.6 Host: nur Textprüfung (kein `@`, kein `:`) und dann `kanon_host`; IP-Adressen kamen durch. Neu: DNS-Hostsyntax, nur druckbares ASCII.
- alt Namen: Quellen-`titel` „1..200 Zeichen“ bzw. `istName(…, 200)`, `testquelle.name` `istName(name, 80)`. Neu: Namensregel in Codepunkten, Bau ohne Cc/Cf/Cs/Zl/Zp und nicht nur Zs, Client `quellName` (Länge und `trim() ≠ ""`).
- alt Quellen-ID: im Bau nur `ID`. Neu: `ID` plus Sperrliste (`Object.prototype`-Namen, `prototype`).
- alt §2.6/§9.7: Wert und Teilpunkte gemeinsam nur für Maßfelder und für Werte, die `wertOk` verwirft. Neu: Typprüfung nach `typ` für jedes Schemafeld, Wert, Teilpunkte und Beleg entfallen gemeinsam.
- alt §1/§4/§9.5: „Summe 100“ unbedingt. Neu: nur bei Σ g > 0, sonst `keine_merkmale` und `merkmale` leer.
- alt A-1 „Neuer Test …“, alt A-4 „einen Test, der die fünf Werte festschreibt“. Neu: Verweis auf Test 33 bzw. 35.

**Fertigkriterien**
- Jede der fünf Korrekturen schließt ihren Befund, oder der Rest ist benannt.
- §9.6: Für Host, Namen, Titel und Quellen-ID nimmt der Client alles an, was der Bau annimmt; Abweichungen nur in der sicheren Richtung (Client weiter) und begründet.
- §9.7: Bei gültigen Daten ändert die Typprüfung keine Note; jeder typfalsche Wert verliert Teilpunkte und Beleg.
- Keine „alt“-Regel steht noch irgendwo in §1–§9 ohne Änderung oder Verweis. Jeder Test steht genau einmal.

**Selbstprüfung (Lead):** Gegenproben je Befund in `bewertung-r3-p2a1.md` (Python `kanon_host`, Node `new URL`, `datenPruefen` mit `leistung_w: "1400"`, `gewichte` mit allen Reglern 0); Scan der 465 Quellen auf die neuen Regeln ohne Treffer. Gebaut ist nichts.

**Bekannte Grenzen:** Datum ohne obere Grenze im Client (bewusst, r2). Die Gleichheit Bau↔Client belegen erst die Tests 21, 33, 44 am Code.

**Prüffragen (Klassenfragen):**
1. R2-04/R3-01 (Grenze nur einseitig): Gibt es in `quellen`, `belege`, `testquelle` oder `gewichte_version` noch einen Wert, dessen Grenze nur eine Seite festlegt oder den die Seiten verschieden zählen?
2. R2-06 (getrennt gefiltert): Gibt es nach der Typprüfung noch ein Paar (Wert, Teilpunkte, Beleg, Abdeckung), das getrennt gefiltert wird? Stimmt die `stufe`-Regel (Text ≤ 200) mit dem Bau überein?
3. R2-07 (bedingte Ist-Aussage): Gibt es weitere unbedingte Aussagen zu Summen oder Anteilen, die bei Σ g = 0 oder ohne belegtes Feld nicht gelten?
4. Stimmt die Begründung in §9.6, dass `trim` nur Zeichen der verbotenen Klassen entfernt?
