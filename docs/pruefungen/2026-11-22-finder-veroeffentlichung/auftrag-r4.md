# Prüfauftrag: Finder „Finden & Vergleichen“, Nachprüfung r4 (kritisch)

**Ziel:** Prüfen, ob Commit c32bba1 die r3-Befunde R3-01…R3-05 schließt, ohne neue Fehler einzuführen; danach wird nur gh-pages veröffentlicht (`main` folgt später).

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“; `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“.
- Jeder r3-Befund ist geschlossen (Einordnung `bewertung-r3.md`); die Kriterien aus `auftrag.md`, `auftrag-r2.md` und `auftrag-r3.md` gelten weiter.
- `veroeffentlichen.py` committet nur eine `finder-daten.json`, deren Herkunft der geprüfte Stand ist und die dem eigenen Bau gleicht, auch wenn parallel `app_bauen.py` läuft.

**Prüfgegenstand:** Diff `-Basis` (73e2c6c) bis HEAD (c32bba1). Schwerpunkt: `werkzeuge/{veroeffentlichen,app_bauen,herkunft}.py`, `werkzeuge/datenpflege/abruf.py` (`sperre_*`, `_norm`, `robots_erlaubt`), `app/finder/bewertung.js` (`nichtAnwendbar`, `gewichte`, `pruefe`, `datenPruefen`) und die geänderten Tests. Der Merge 83ba81f bringt nur Daten (`daten/produkte/laptop.json`, aus einer Parallelsitzung) sowie STATUS/Übergabe; dafür genügt die Datenbankschranke.

**Selbstprüfung:** Jeder neue Test rot vor der Korrektur (R3-01: 3, R3-02: 3 Node, R3-03: 1, R3-04: 3, R3-05: 2), danach grün; Sammellauf Fehler 0/Warnungen 0 (auch im Commit-Hook); `datenbank.py pruefen` 325 Modelle/413 Varianten, Fehler 0, Warnungen 56; echte `finder-daten.json` besteht `datenPruefen`; `veroeffentlichen.py --trocken`: Bau im temporären Verzeichnis, gespiegelte Datei trägt `herkunft` = HEAD; Geheimnis-Scan 0 Funde.

**Bekannte Grenzen:** Dateisperren (`msvcrt.locking`/`fcntl.flock`) nur gegen Läufe auf demselben Rechner. Die Prüfung der bereitgestellten Datei liest den Index des Seitenbaums (`git show :finder-daten.json`) nach `git add -A`. `finder-daten.yml` nicht live gelaufen (läuft erst auf main).

**Prüffragen**
1. Kann zwischen Prüfung des Index und Commit/Push noch eine andere `finder-daten.json` in den Seitencommit gelangen?
2. Ist `_norm` für Pfad und Regel jetzt in allen Fällen gleich (`*`, `$` in der Mitte und am Ende, `%2a`, `%24`, `$$`)?
3. Hält die Domainsperre in jedem Pfad (Warten, Abruf, Fehler, Abbruch) genau einen Inhaber und wird sie immer freigegeben?
4. Gibt es weitere Nachschlagestellen in `bewertung.js`/`finder.js`/`sw.js`, an denen Kennungen aus fremden Daten den Prototyp treffen?
5. Akzeptiert `herkunft.py` noch einen Stand ohne nachgewiesenes Commit-Objekt?
6. Steht im Diff etwas, das im öffentlichen Repo nicht stehen darf?
