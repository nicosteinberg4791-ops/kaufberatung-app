# Prüfauftrag Finder G1 (Erstprüfung, medium)

**Ziel:** Prüfen, ob der Finder-Umbau G1 (Look wie der Ratgeber, Punkte als Balken, Prioritäten-Regler) richtig rechnet, sicher mit der Adresse umgeht, zugänglich bleibt und nichts kaputt macht.

**Prüfgegenstand:** Diff ab Basis 33fa490 bis HEAD auf `main`. Plan und Grenzen: `docs/DESIGN.md` Abschnitt „G1 Bauplan“, Entscheidung D26 in `docs/entscheidungen.md`.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“
- `node --test tests/test_bewertung.mjs tests/test_finder_dom.mjs` → alle grün
- Regler ändern nur Gewichte vorhandener Felder mit `gewicht > 0`; der Preis geht nie in die Note ein; D12 (eine Note, kein Testwert) bleibt.
- Adresse `p=feld.stufe~…` wird beim Lesen geprüft (nur bewertbare Felder der Kategorie, Stufe 0–4, „normal“ nie geschrieben); fremde Werte gelangen nur als Text ins DOM.

**Betroffene Dateien:** `app/finder/bewertung.js` (Z. 39–65, 257–267, 450–455) · `app/finder/finder.js` (Z. 69–90, 181–215, 422–570, 616–930, 963–966) · `app/finder/finder.css` · `app/finder/index.html` (Z. 9–14, 32–36) · `tests/test_bewertung.mjs`, `tests/test_finder_dom.mjs`.

**Selbstprüfung (Lead):** Sammellauf „Fehler: 0 · Warnungen: 0“; `pruefe.mjs` lokal (über Lastsperre): 14 Kacheln, keine Meldungen, offline in Ordnung, 0 Tippziele unter 44 px, Breite 375 ohne Querrollbahn; Mutantenproben laut STATUS rot→grün; Fotos hell/dunkel angesehen.

**Bekannte Grenzen**
- Vergleichsfarbe folgt dem Platz in der Auswahl; wird ein Modell entfernt, wechseln die übrigen die Farbe.
- „gleichauf“ im Vergleich vergleicht nur die zwei Besten (Ratgeber-Regel); ein klar zurückliegendes drittes Modell ändert das nicht.
- Geist wird wie im Ratgeber von Google Fonts geladen; offline gilt die Ersatzschrift.

**Prüffragen**
1. `gewichte(kat, antworten, prio)`: Was passiert, wenn alle Regler auf „aus“ stehen (Summe 0)? Gibt es Division durch 0, NaN in Anteilen oder eine irreführende Empfehlung?
2. Adressleser für `p`: Lässt er Prototyp-Schlüssel, doppelte Felder, Filterfelder oder Felder einer anderen Kategorie durch?
3. Fokus und Ziehen: Bleibt der Regler beim Neurechnen bedienbar (Panel wird nicht neu gebaut), und stimmt `aria-valuetext` mit der Anzeige überein?
4. Vergleichen-Knopf (`aria-pressed`, deaktiviert bei voll): ist der Zustand für Screenreader eindeutig, und bleibt `data-fokus` nach dem Neurechnen erhalten?
5. FLIP und IntersectionObserver: Lecks oder doppelte Beobachter bei häufigem Neurechnen; reduzierte Bewegung respektiert?
6. Stimmen „Vorn/gleichauf“ in Rangliste und Vergleich mit den angezeigten (gerundeten) Noten bzw. Teilpunkten überein?
