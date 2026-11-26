# Stand – Kaufberatung-App

Stand: 26.11.2026 · Branch main, P2a-2 gebaut (Zwischenstand, selbst geprüft, nicht gepusht; letzter Commit siehe `git log`) · P2a-1 unabhängig geprüft bis d062392 (Korrektur r3 nur selbst geprüft) · Vollständiger Verlauf: [docs/status-verlauf.md](docs/status-verlauf.md).

## Lage

- **Live auf gh-pages:** App 1045baedfc64 (Herkunft 7339711, Inhalt Artifact-Version 30). Finder G1, Datenbank, UX-P1, P2a-1 und P2a-2 sind auf `main`, nicht gepusht und nicht live. `main` und origin/main (Paket `abruf.py`, 40cf73f) sind auseinandergelaufen; Merge nur mit Auftrag.
- **Pilot Bestpreis (D7):** Entscheidung O12 stand am 26.11. an.

## Erledigt (26.11.2026)

- **Entscheidungen F-1, F-4, O31** (Besitzer): [D27](docs/entscheidungen.md).
- **P2a-2 gebaut:** `gewichte_version` ist Pflicht, Fassung 1 ({nummer 1, stand 2026-11-26}) steht in allen 14 Kategorien ([kategorien.json](daten/schema/kategorien.json)). [datenbank.py](werkzeuge/datenbank.py): `vorbedingung_fehler` (eindeutige IDs, Schema wie im Client, Kurven), `projektion`, `fassung_gegen_fehler`, `pruefen --gegen [<commit>]`. Neu ist [freigabe.py](werkzeuge/freigabe.py): strenge Referenz aus `<eltern>:finder-daten.json`, lokale Prüfung über `ls-remote`, Workflow-Schritt `daten-push` mit Lease. Angebunden in [veroeffentlichen.py](werkzeuge/veroeffentlichen.py) (vor dem Bau) und [finder-daten.yml](.github/workflows/finder-daten.yml).
- **Tests:** 3, 6, 38–41, 48 in `tests/test_datenbank.py` (Klasse `Gewichtsfassung`), 47(a), (c)–(h) in [tests/test_freigabe.py](tests/test_freigabe.py), 47(b), (c) in `tests/test_app.py` (`Veroeffentlichen`), 37, 40 (R2-01), 42 in `tests/test_bewertung.mjs`. Vor der Änderung rot: 3, 6, 38–41, 47, 48, 42. Schon vorher grün (Regressionsschutz): 37, 40-R2-01. Sammellauf `tests/alle-tests.ps1`: Fehler 0, Warnungen 0. `pruefen --gegen` gegen das echte gh-pages (Herkunft 7339711, Schema 1): 0 Fehler.

## Nächster Schritt

**P2a-2 abschließen und Codex-Erstprüfung starten.** Reihenfolge:
1. **Test 37 umstellen:** Der Vergleich gegen „neue Datei ohne P2a-Angaben“ kann nur rot werden, wenn eine alte App neue Schlüssel liest. Neu: Vergleichsdatei = Bau mit `werkzeuge/datenbank.py` und Schema der Live-Herkunft (herkunft aus `origin/gh-pages:finder-daten.json`, heute 7339711), dazu die heutigen Produktdaten. `bauMitStand(commit, …)` gibt es schon in `tests/test_bewertung.mjs`. Belegt: Das alte Werkzeug baut die heutigen Daten mit 0 Fehlern und 418 Varianten.
2. **Mutanten** (je rot, danach `git checkout -- <datei>`): Pflicht entfernt → Test 3; Zweig „gleich und andere Nummer“ entfernt → 38; Felder in der Projektion sortiert → 40; `_doppelt` für Felder entfernt → 48; `online_eltern` liest `origin/gh-pages` → 47(h); Push ohne Lease → 47(e); `seiten_fehler` in veroeffentlichen.py entfernt → 47(b); `eltern` nur einmal vor der Schleife → 47(d)/(f); Gewicht im Schema geändert → 42 und 37 (neu).
3. **Doku:** [docs/punkteschema.md](docs/punkteschema.md) §7a (Satz „Pflicht … stehen noch aus“ ersetzen), Kopf von `docs/recherche-ux/p2-entwurf.md` (P2a-2 gebaut, Abweichungen: neues Modul `werkzeuge/freigabe.py` außerhalb der Dateihoheit §5; neue Kategorie ohne Referenz nur auf Form geprüft; Test 37 wie oben).
4. Sammellauf, Commit, Auftrag `docs/pruefungen/2026-11-26-p2a2-bau/auftrag.md` (Vorlage `docs/pruefungen/2026-11-26-p2a1-bau/auftrag.md`), dann `pruefe.ps1 -Pruefer codex -Stufe medium -Art erst -Basis dbfdca6` (Sol 6.2 medium, im Hintergrund).
**Fertig, wenn** Test 37 umgestellt ist, die Mutanten rot und das Original grün sind, `tests/alle-tests.ps1` Fehler 0 meldet, committet ist (nicht gepusht) und die Erstprüfung läuft. Lesen: dieser Abschnitt, `docs/recherche-ux/p2-entwurf.md` §9.3 und §9.9, `werkzeuge/freigabe.py`.

## Offen für Nico

- Fotos Finder G1 freigeben; P2 GS-1, „gleichauf“ im Vergleich (`docs/pruefungen/2026-11-24-finder-g1/gestaltung-r3.md`).
- Push und gh-pages nach Merge; Impeccable installieren (D21). Ein Push von `main` mit P2a-2 bringt die Schranke in den Datenworkflow (Auslöser `daten/schema/**`).
- P2: F-2 (Maße), F-3 (Testquelle), F-5 (Umfang der Projektion; gebaut nach Vorschlag „ja“: Kurven und Abschlag gehören dazu).
- O12, O13, O10, O5, O6, O7: Wortlaut im Verlauf.
- Nicht auf echtem Android-Handy geprüft: Icons, Push-Zustellung, Besitzer-Merker.

## Wegweiser

Tests `powershell -File tests/alle-tests.ps1` · Bau `python -I werkzeuge/app_bauen.py` · Schranke `python -I werkzeuge/datenbank.py pruefen --gegen` · Entscheidungen [docs/entscheidungen.md](docs/entscheidungen.md) · Finder [docs/uebergabe-finder.md](docs/uebergabe-finder.md).
