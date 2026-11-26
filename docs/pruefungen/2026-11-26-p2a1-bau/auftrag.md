# Erstprüfung – P2a-1 gebaut (Rechnung, Schnittstelle, Vertrag), Stand dda4d33

**Ziel:** Prüfen, ob der Bau von P2a-1 (Diff ab `-Basis` bis `dda4d33`) den Entwurf `docs/recherche-ux/p2-entwurf.md` erfüllt: §1–§8 ohne §2.1, §9.2, §9.4–§9.7 und die Tests 1–5 (ohne den P2a-2-Anteil), 7–36, 43–46.

**Fertigkriterien:**
1. `python -I -B -m unittest discover -s tests -t tests -p test_datenbank.py` → OK.
2. `node --test tests/test_bewertung.mjs` → 0 fail.
3. `python -I werkzeuge/datenbank.py pruefen` → 0 Fehler.
4. Jeder Test 1–5, 7–36, 43–46 aus §6/§9.9 hat einen Testfall mit den dort genannten Fällen (Testnamen tragen die Nummer).
5. Vertrag §9.6: Der Client verwirft nichts, was der Bau annimmt (Datum, URL, Namen, Quellen-ID, Stufenwerte); der Bau prüft mit `fullmatch`.
6. §9.4 Belege aus derselben Ebene wie der Wert; §9.5 `notenblatt` (Nenner, `beitrag_r`, fehlende Zeilen nach R4-01); §9.2 `alternativen` gleich dem Orakel; §9.7 Maße und „Wert und Teilpunkte gemeinsam“.
7. Bei gültigen Live-Daten ändert sich keine Note.

**Dateien (Stand dda4d33):** `werkzeuge/datenbank.py` Z. 40–48 (Konstanten), 61–178 (`name_ok` … `feld_ok`), 269–417 (`pruefe_datei`, `alle_pruefen`), 418–462 (`bauen`) · `app/finder/bewertung.js` Z. 12–14, 264–265, 308, 315–439 (`alternativen`, `belegFuer`, `reglerWirken`, `notenblatt`, `methodik`), 497–627 (`quellDatum` … `datenPruefen`) · `daten/schema/kategorien.json` · `tests/test_datenbank.py` ab Z. 135 · `tests/test_bewertung.mjs` ab Z. 556 · `docs/punkteschema.md` §7a, `daten/produkte/FORMAT.md`.

**Nicht im Umfang (P2a-2, eigene Runde):** Referenzvergleich der Gewichtsfassung (§9.3), Pflicht und Fassung 1 von `gewichte_version` (§2.1, §9.1; heute nur Form, wenn vorhanden), Freigabeschranke, Tests 6, 37–42, 47, 48. Offene Besitzerentscheidungen F-1 (Gewichte) und F-4 (Quellen in eigener Datei) sind keine Befunde.

**Selbstprüfung:** Sammellauf `tests/alle-tests.ps1` 0 Fehler. Mutanten: Bau 15/15 rot, Client 19/20 rot (1 äquivalent). Gegenprobe: 4 536 Noten alt gegen neu, 0 Abweichungen. `finder-daten.json` 330 436 → 582 760 Byte (465 Quellen, 4 043 Belege).

**Bekannte Grenzen:** Test 44: Bau und Client bekommen dieselben Vertragsfälle, aber getrennt (`VertragMetadaten` in `test_datenbank.py`, Test „44, Client“ in `test_bewertung.mjs`); ein gemeinsamer Lauf über eine Fallliste fehlt noch. Den Ursprung eines Belegs prüft nur der Bau (§9.4).

**Prüffragen:**
1. Gibt es einen Wert, den der Bau annimmt und der Client verwirft (oder der eine Note ändert), oder einen, der an beiden Schranken vorbeikommt (§9.6, §9.7, Stufenwerte)?
2. Weicht `alternativen` in einem Fall vom Orakel §9.2 ab (Regler, `egal`, `mindest`/`hoechst`, `zu_wenig_daten`, `keine_merkmale`, Reihenfolge)?
3. Stimmen in `notenblatt` Nenner, `anteil`, `beitrag_r`, `R` und fehlende Zeilen in allen Sonderfällen (Σ g = 0, kein belegtes Feld, verworfene Teilpunkte)?
4. Kann im Bau ein Beleg aus einer anderen Ebene als der Wert, ein Beleg ohne Wert oder einer auf eine unbekannte Quelle in `finder-daten.json` landen?
5. Gibt es eine Regel aus dem Umfang ohne Test, oder einen Test, der bei einer naheliegenden Mutante grün bliebe?
