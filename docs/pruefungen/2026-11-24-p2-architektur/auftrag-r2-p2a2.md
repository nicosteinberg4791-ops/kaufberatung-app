# Nachprüfung r2 – P2a-2 Gewichtsfassung und Freigabeschranke (high, nach)

**Ziel:** Prüfen, ob die Korrekturen zu P2A2-01 … P2A2-07 (`bewertung-p2a2-r1.md`) im Entwurf `docs/recherche-ux/p2-entwurf.md` die Befunde samt Klasse schließen, ohne neue Widersprüche zu erzeugen.

**Prüfgegenstand:** nur der Diff von `docs/recherche-ux/p2-entwurf.md` ab `5756026`, soweit er §2.1, §5, §7 R6, §9.1, §9.3 und die Tests 6, 37–42, 47 und 48 (§6, §9.9) betrifft. Code nur, wo der Entwurf sich darauf stützt: `werkzeuge/datenbank.py:39–82`, `:299–330`, `.github/workflows/finder-daten.yml:57–80`, `werkzeuge/veroeffentlichen.py:302–360`, `werkzeuge/preise_aktualisieren.py:198–226`, `app/finder/bewertung.js:46–67`, `:388–420`, `daten/schema/kategorien.json`. Nicht Gegenstand sind P2a-1 (§2.2–§2.6, §3, §4, §9.2, §9.4–§9.7, eigene Runde r3 abgeschlossen) und die offenen Fragen F-1 … F-5.

**Fertigkriterien**
- P2A2-01 … P2A2-07 sind durch die genannte Korrektur geschlossen, oder der Rest ist benannt.
- Für das Schema gibt es keinen Fall, der die angezeigte Note ändert, während Projektion und Nummer gleich bleiben. Das umfasst doppelte IDs, Zahlendarstellung und Wahrheitswerte.
- Jeder Push auf gh-pages durch ein Werkzeug (Datenworkflow, App-Publish, Preis-Push) läuft mit Lease auf genau den Eltern-SHA, gegen dessen Herkunft geprüft wurde. Ist der Zweig gelöscht oder versetzt, folgt kein Push ohne neue Prüfung.
- Die lokale Prüfung liest die Referenz nur aus dem frisch abgefragten Remote-SHA.
- Test 41 wird rot, wenn die Prüfung jede Referenz mit Schema 1 ablehnt oder die Startnummer nicht prüft. Test 47(c) deckt jeden Strikt-Fall in allen drei Wegen ab.

**Selbstprüfung (Lead):** Gegenproben je Befund in `bewertung-p2a2-r1.md`: Node `hisense-e7s-43` 55,07 → 52,12, Python Interpolation 34,8 gegen 34,7. Scan des echten Schemas: keine doppelte ID, alle Zahlen in den neuen Grenzen. Push-Wege per `grep -rn "git push"`. Gebaut ist nichts.

**Bekannte Grenzen:** Ein Push oder Merge von Hand auf gh-pages umgeht die Schranke (§7 R6, bewusste Entscheidung). F-5 (Umfang der Projektion) ist beim Besitzer offen. `herkunft.py` und `app_bauen.py` bleiben unverändert.

**Prüffragen (Klassenfrage je Korrektur):**
1. P2A2-01: Gibt es außer den genannten Listen (Kategorien, Felder, Fragen, Antworten, Stufenwerte) noch eine Stelle, an der Bau und Client bei gleicher ID verschiedene Einträge nehmen?
2. P2A2-02/-05: Bleibt ein Weg, auf dem ein Werkzeug einen anderen als den geprüften Elternstand auf gh-pages schiebt?
3. P2A2-04: Reichen Typprüfung und `float`-Normalform, damit Python-Gleichheit der Projektion auch gleiche Rechnung im Client bedeutet (etwa `-0.0`, große ganze Zahlen in den Faktoren)?
4. P2A2-06/-07: Würde jeder der neuen Tests ohne die jeweilige Regel rot?
