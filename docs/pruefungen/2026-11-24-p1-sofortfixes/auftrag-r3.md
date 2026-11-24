# Nachprüfung P1 r3 (Codex medium, sehr schmal)

**Ziel:** Prüfen, ob der r2-Befund P1-03/P1-04 (schwer) geschlossen ist. Keine Vollprüfung.

**Umfang:** nur der Diff ab `268fb06`: `app/finder/finder.js` Funktion `ohneEmpfehlungText` und der neue Test am Ende von `tests/test_finder_dom.mjs`. Bewertung: `bewertung-r2.md` (P1-01-Rest ist dort als bewusste Entscheidung begründet). Andere Dateien nur lesen, wenn eine Prüffrage es verlangt (`app/finder/bewertung.js` `auswerten`, Z. 260–300).

**Fertigkriterien**
- `node --test tests/test_finder_dom.mjs` → 0 fail
- Ohne Empfehlung nennt die Meldung den tatsächlichen Notengrund (Datenblatt / kein Merkmal / gemischt) und, wenn kein Modell eine Note hat, den Preisgrund (kein Preis / alle über Budget / gemischt).

**Selbstprüfung:** `tests/alle-tests.ps1` → Fehler 0, Warnungen 0. Gegenprobe: `finder.js` aus 268fb06 → neuer Test rot.

**Prüffragen**
1. Gibt es eine Kombination aus Note, Preis, Budget und `art`, bei der `ohneEmpfehlungText` einen falschen oder unvollständigen Grund nennt (gemessen an den Bedingungen von `auswerten`, unter denen keine Empfehlung entsteht)?
