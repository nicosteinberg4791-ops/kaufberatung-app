# Prüfauftrag: Abgleich der Finder-Linien, Befunde A1–A3 (Erstprüfung, schmal)

**Ziel:** Prüfen, ob die drei Korrekturen A1–A3 in der veröffentlichten Finder-Linie (Basis `origin/main` ca9eacc) vollständig und ohne neue Lücke sind.

**Prüfgegenstand:** nur der Diff `-Basis` bis HEAD.

**Fertigkriterien:**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“
- `python -I -X utf8 werkzeuge/datenbank.py pruefen` → „Fehler 0“
- A1: `app_bauen.py --ziel <Pfad>` bricht bei vorhandenem, nicht leerem Ziel (auch einer Datei) vor jedem Löschen ab; ein eigenes Ziel wird nie aufgeräumt, nur `dist/` (Standard) mit `BEHALTEN`.
- A2: Der Domain-Abstand (61 s) zählt nur ab einem Abschlussstempel genau in der Schreibweise von `stempel_setzen` (`repr` von Wanduhr und monotoner Uhr, ein Leerzeichen); es zählt die kleinere vergangene Zeit beider Uhren; alles andere (leer, unlesbar, alte Einzelwerte wie `0`/`-1e308`, Markierung `laeuft`, nan/inf, unmögliche Werte, fremde Schreibweise) ergibt den vollen Abstand.
- A3: Der Push nach gh-pages läuft mit `--no-follow-tags`; mit `push.followTags=true` und annotiertem Tag am Elterncommit landet kein Tag im Ursprung.

**Betroffene Dateien:**
- `werkzeuge/app_bauen.py` `baue()` Z. 127–147
- `werkzeuge/datenpflege/abruf.py` `sperre_holen` Z. 77–104, `LAEUFT`/`verstrichen`/`stempel_setzen` Z. 107–145, `holen` Z. 155–175
- `werkzeuge/veroeffentlichen.py` `main` Z. 354–358
- `tests/test_app.py` `Bau.test_ziel_muss_neu_oder_leer_sein`, `BauZiel`, `Veroeffentlichen.test_follow_tags_veroeffentlicht_keine_tags`
- `tests/test_abruf.py` Klasse `Domainsperre` Z. 204–358

**Selbstprüfung:** Neue Tests vor der Korrektur rot (A2: Stempel `0`, `-1e308`, Uhrsprung, fehlendes `stempel_setzen`; A1: `--ziel .` löscht; A3: Tag auf dem Server), danach grün. `BauZiel` ist gegen main grün (dort nur ein Verzeichniszugriff) und rot gegen die Mutante „Leerprüfung ohne Nie-Aufräumen“. Sammellauf 0 Fehler, Datenbank 0 Fehler, `core.bare` danach `false`. Vorprüfung (Sonnet, medium): 0 kritisch/schwer/mittel, 3 gering (Dateifall-Meldung im Test ergänzt; Überschreiben bei Rennen nach der Leerprüfung und Abbruch bei `--ziel dist` mit Inhalt angenommen).

**Bekannte Grenzen:** Die Markierung `laeuft` vor dem Versuch (statt eines gültigen Startstempels) stammt aus der Vorlage; ein hart beendeter Abruf lässt dem nächsten den vollen Abstand ab Übernahme der Sperre. Alte Einzelwert-Stempel führen einmalig zu 61 s Wartezeit. Die monotone Uhr wird als systemweit seit Start angenommen (Windows: QueryPerformanceCounter, Linux: CLOCK_MONOTONIC).

**Prüffragen:**
1. Gibt es eine Eingabe oder Uhrkonstellation, bei der `sperre_holen` weniger als den Restabstand seit dem letzten tatsächlichen Versand wartet?
2. Kann `baue(ziel=…)` über irgendeinen Weg (Datei, Symlink, Rennen nach der Leerprüfung) vorhandene Dateien löschen oder überschreiben, die nicht vom Bau stammen?
3. Gibt es außer `--no-follow-tags` weitere Wege, auf denen der gh-pages-Push mehr als `refs/heads/gh-pages` überträgt (z. B. Konfiguration `remote.origin.push`, `push.default`)?
4. Sind die Tests stark genug, um eine Rücknahme jeder Korrektur zu erkennen?
