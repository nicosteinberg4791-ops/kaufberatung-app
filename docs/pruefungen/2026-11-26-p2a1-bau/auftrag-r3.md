# Nachprüfung r3 – P2a-1 gebaut (nur P2A1-03 aus r2)

**Ziel:** P2A1-03 ist geschlossen: Test 21 prüft auf den echten, frisch gebauten Daten jede Note, ohne neue Lücke derselben Klasse.

**Fertigkriterien:**
1. `node --test tests/test_bewertung.mjs` → 63 bestanden, 0 fail.
2. Test „P2A1-03 (21)“ vergleicht für die Vorgabe und jede einzelne Antwort jedes Modell direkt über `bewerteModell` (`note` und `art`), jede Seite mit eigenen `gewichte`. Die Zahl der Vergleiche wird aus den Rohdaten abgeleitet und geprüft (418 Einträge, 5 237 Vergleiche).
3. Werte, Teilpunkte, Belege, Quellen und Testquelle werden vor und nach `datenPruefen` verglichen.

**Dateien:** Diff ab `-Basis`, nur `tests/test_bewertung.mjs` (Test „P2A1-03 (21)“). Der Rest des Diffs ist Dokumentation (`STATUS.md`, `bewertung-r2.md`, `auftrag-r2.md`).

**Selbstprüfung:** Kriterium 1 grün. Mutanten gegen den Test: M4 (Stufenwert nur bis 15 Codepunkte) → rot, M6 (Teilpunkte ab 99,5 verworfen) → rot. Gesamtlauf im Commit-Hook: Fehler 0, Warnungen 0.

**Bekannte Grenzen:** Der Test braucht `python` im Pfad (oder die Umgebungsvariable `PYTHON`) und ein beschreibbares Temp-Verzeichnis. P2A1-R2-01 (Testlinks) ist als O31 außerhalb des Umfangs.

**Prüffragen:**
1. Gibt es ein Ergebnis aus der Rechnung, das der Test weiterhin nicht vergleicht (andere Eingaben, Felder des Ergebnisses neben `note` und `art`)?
2. Kann der Test grün bleiben, obwohl `datenPruefen` auf den echten Daten eine Note ändert?
