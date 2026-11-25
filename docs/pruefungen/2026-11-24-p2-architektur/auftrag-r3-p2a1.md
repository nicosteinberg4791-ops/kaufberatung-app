# Nachprüfung r3 – P2a-1 Rechnung und Schnittstelle (high, nach)

**Ziel:** Prüfen, ob die Korrekturen zu R2-03 … R2-07 (`bewertung-r2.md`) im Entwurf `docs/recherche-ux/p2-entwurf.md` die Befunde schließen, ohne neue Widersprüche zu erzeugen.

**Schnitt (Besitzer, 25.11.2026, O24):** Das Paket ist geteilt. **Nicht** Gegenstand dieser Runde sind Gewichtsfassung und Freigabeschranke (§2.1, §9.1, §9.3, R2-01, R2-02, Tests 6, 38–42, 47, `finder-daten.yml`, `veroeffentlichen.py`). Dafür läuft eine eigene Erstprüfung (P2a-2).

**Prüfgegenstand:** nur der Diff von `docs/recherche-ux/p2-entwurf.md` ab `417f8b5`, soweit er §1, §2.2–§2.6, §3, §4, §5 (ohne die Zeile zu `veroeffentlichen.py`), §6, §7, §8, §9.2, §9.4–§9.9 betrifft. Code nur, wo der Entwurf sich darauf stützt: `app/finder/bewertung.js` (`gewichte`, `bewerteModell`, `datenPruefen`, `sichereUrl`), `app/sw.js:80–84`, `werkzeuge/datenbank.py:44–50`, `:105–115`, `:300–330`, `daten/schema/kategorien.json`.

**Fertigkriterien**
- R2-03 bis R2-07 sind durch die genannte Korrektur geschlossen (oder der Rest ist benannt).
- §2–§8 enthalten keine ersetzte Regel mehr ohne Änderung oder Verweis (Prüfsumme, `DATUM`/`sichereUrl` für neue Felder, Orakel ohne Ein-Modell-Kopie, `fehlend` als Objektliste, Nachweis nur mit `33fa490`).
- §9.6: Für jeden Wert der Tabelle nimmt der Client alles an, was der Bau annimmt. Die einzige gewollte Abweichung (Datum ohne obere Grenze im Client) ist begründet.
- §9.5: `anteil` ergibt in Prozent 100, `beitrag_r` ist ohne belegtes Feld `null`.
- §9.7: Teilpunkte bleiben nur bei gültigem Wert; bei gültigen Daten ändert sich keine Note.
- Jeder Test steht genau einmal (§6 bzw. §8/§9.9).

**Selbstprüfung (Lead):** Gegenproben je Befund in `bewertung-r2.md` (Node/Python am Code und an `origin/gh-pages:finder-daten.json`). Volltextsuche nach den Altbegriffen ohne stillen Treffer. Hook beim Commit `df20d84`: „Fehler: 0 · Warnungen: 0“. Gebaut ist nichts.

**Bekannte Grenzen:** F-1 … F-5 sind beim Besitzer offen, bitte nicht entscheiden. Der Wortlaut der Ansicht gehört zu P2b.

**Prüffragen (Klassenfrage je Korrektur):**
1. R2-04 (Grenzen nur einseitig): Gibt es weitere Werte in `quellen`, `belege`, `testquelle`, deren Grenze nur auf einer Seite steht?
2. R2-06 (Wert und Teilpunkte getrennt): Gibt es weitere Paare in `datenPruefen`, die getrennt gefiltert werden und gemeinsam gelten müssten (etwa `belege` gegen `werte`)?
3. R2-07 (bedingte Ist-Aussagen): Gibt es weitere unbedingte Ist-Aussagen in §1, die nur unter Bedingungen gelten?
4. R2-03: Verweist jede geänderte Stelle auf den richtigen Absatz in §9?
