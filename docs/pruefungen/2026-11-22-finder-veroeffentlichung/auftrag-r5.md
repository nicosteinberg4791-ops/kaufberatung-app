# Prüfauftrag: Finder „Finden & Vergleichen“, Nachprüfung r5 (kritisch)

**Ziel:** Prüfen, ob der eingefrorene Stand die r4-Befunde R4-01…R4-07 (mit R3-01/R3-05) schließt, ohne neue Fehler einzuführen; danach wird nur gh-pages veröffentlicht (`main` folgt später, O14).

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“.
- Jeder r4-Befund ist geschlossen (Einordnung `bewertung-r4.md`); die Kriterien aus `auftrag.md` und `auftrag-r2.md` bis `auftrag-r4.md` gelten weiter.
- `veroeffentlichen.py` pusht genau einen Commit, dessen Baum er selbst geprüft hat (gleich dem eigenen Bau, Preisdateien aus dem Elterncommit, `finder-daten.json` mit geprüfter Herkunft), auf dem geprüften gh-pages-Elterncommit; ein aktiver Commit-Hook verhindert das nicht.

**Prüfgegenstand:** Diff `-Basis` (c32bba1) bis HEAD. Schwerpunkt: `werkzeuge/veroeffentlichen.py` (`main`, `bau_erwartet`, `baum_eintraege`, `baum_fehler`), `werkzeuge/herkunft.py` (`git_vorfahr`), `werkzeuge/datenpflege/abruf.py` (`holen`, `stempel_schreiben`, `robots_erlaubt`), `app/finder/bewertung.js` (`fuelle`), `app/sw.js` (`pruefePreise`) und die geänderten Tests. c21623c ändert nur STATUS.md.

**Selbstprüfung:** Jeder neue Test rot vor der Korrektur und danach grün (R4-01: Indexänderung nach der Prüfung und `baum_fehler`; R4-02: ablehnender Hook; R4-03, R4-04, R4-05, R4-06, R4-07 je einer); Sammellauf Fehler 0; `datenbank.py pruefen` 325 Modelle/413 Varianten, Fehler 0, Warnungen 56; `pruefe.mjs` lokal: 14 Kacheln, keine Fehler, nur erwartete 503 für das lokal fehlende `preise.json`; `veroeffentlichen.py --trocken` gegen das echte gh-pages: Baum geprüft, nichts committet.

**Bekannte Grenzen:** `git commit-tree` umgeht Commit-Hooks bewusst (R4-02, Begründung in `bewertung-r4.md`). Dateisperren und Zeitstempel nur gegen Läufe auf demselben Rechner; `fsync` schützt gegen Prozessabbruch, nicht gegen jeden Datenträgerfehler. `finder-daten.yml` nicht live gelaufen (läuft erst auf main).

**Prüffragen**
1. Kann noch irgendein Inhalt in den gepushten Seitencommit gelangen, den der Lauf nicht mit dem eigenen Bau verglichen hat (Index, Arbeitsdateien, Elterncommit, Push-Ziel)?
2. Ist das Umgehen des Hooks für den Seitencommit vertretbar, oder fehlt eine Prüfung, die der Hook sonst geleistet hätte?
3. Gilt der Mindestabstand je Domain jetzt in jedem Abbruchpfad (vor, während, nach dem HTTP-Versuch)?
4. Prüft `robots_erlaubt` in allen Fällen genau das gesendete Request-Target (leere Query, Fragment, kodierte Zeichen)?
5. Gibt es weitere Stellen in `sw.js`, `finder.js`, `finder-app.js`, an denen Schlüssel aus fremden Daten auf den Prototyp treffen?
6. Steht im Diff etwas, das im öffentlichen Repo nicht stehen darf?
