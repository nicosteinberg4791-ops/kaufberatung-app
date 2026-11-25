# Nachprüfung r3 – P2a-2 Gewichtsfassung, schmal (high, nach)

**Ziel:** Prüfen, ob die Korrekturen zu P2A2-04 und P2A2-R2-02 (`bewertung-p2a2-r2.md`) im Entwurf `docs/recherche-ux/p2-entwurf.md` beide Befunde samt Klasse schließen, ohne neue Widersprüche zu erzeugen.

**Prüfgegenstand:** nur der Diff von `docs/recherche-ux/p2-entwurf.md` ab `546ded4`, soweit er §9.3 „Vorbedingungen“ (Punkte „Schema wie im Client“ und „Typ und Normalform“, Z. 215–218) sowie Test 40 (§9.9, Z. 284) betrifft. Code nur, wo der Entwurf sich darauf stützt: `app/finder/bewertung.js:379–420`, `:423–435`, `werkzeuge/datenbank.py:39–82`, `daten/schema/kategorien.json`.
**Nicht Gegenstand:** der Preis-Push (§9.3 „Preis-Push“ und „Strikt“, Test 47; eigenes Paket am Code nach O27), alles zu P2a-1 (§1, §2.6, §9.5, §9.6, Tests 21, 34, 44; nach O26 Restrisiko bis zum Bau) und die offenen Fragen F-1 … F-5.

**Ersetzte Regeln (alt, gelten nicht mehr):**
- alt: Typ- und Grenzprüfung nur für die Zahlen der Projektion. Neu: das ganze Schema wie im Client, auch Felder mit Gewicht 0.
- alt: „alle Zwischenwerte exakt als `float`“. Neu: „jeder Operand exakt als `float` darstellbar“.
- alt (Test 40): `1200` gegen `1200.0` ohne Kurve und Erwartung. Neu: konkrete Kurve mit Erwartung 34,8 und direkte Typprüfung.

**Fertigkriterien**
- P2A2-04 und P2A2-R2-02 sind durch die genannte Korrektur geschlossen, oder der Rest ist benannt.
- Es gibt kein Schema, das die Vorbedingungen annehmen und bei dem `datenPruefen` die ganze Datei verwirft (Regeln, Kategorien, Felder, Fragen, Antworten), und umgekehrt keines, das der Client annimmt und der Bau ablehnt, außer mit genannter Begründung.
- Jeder Fall in Test 40 wäre ohne die zugehörige Regel rot.

**Selbstprüfung (Lead):** Gegenproben in `bewertung-p2a2-r2.md` (Node: `gewicht: false` an `diagonale_zoll` → Wurf `feld`; Python: Kurve `[[1200, 20], [1204, 79]]` bei 1201, int und float → 34,75). Scan des heutigen Schemas mit den Client-Regeln: keine Verletzung. Eigenbefund vor dem Einfrieren: Die Aufzählung in „Schema wie im Client“ nannte die Kategorieprüfung aus `datenPruefen` (`:430–435`) nicht, jetzt ergänzt. Gebaut ist nichts.

**Bekannte Grenzen:** `stand` und `herkunft` der Datei setzt der Bau, sie sind kein Schema. Ein Push von Hand umgeht die Schranke (§7 R6).

**Prüffragen (Klassenfrage je Korrektur):**
1. Bleibt eine Wurfprüfung in `datenPruefen` (`:423–435`), die ein Schema betrifft und von „Schema wie im Client“ nicht erfasst wird, etwa Längen, Leerzeichen-Namen, Sperrliste oder Schlüssel in `gewichte`/`mindest`/`hoechst`?
2. Zählen Bau und Client Textlängen und IDs gleich (UTF-16-Einheiten, `fullmatch`, Sperrliste), auch bei Zeichen außerhalb der BMP und abschließendem Zeilenumbruch?
3. Reichen Grenzen und `float`-Normalform, damit Python-Gleichheit der Projektion gleiche Rechnung im Client bedeutet (`-0.0`, große ganze Zahlen)?
4. Würde jeder Fall in Test 40 ohne seine Regel rot?
