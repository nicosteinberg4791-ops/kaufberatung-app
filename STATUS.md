# Stand – Kaufberatung-App

Stand: 08.11.2026, ca. 12:35 · `main` auf github.com/nicosteinberg4791-ops/kaufberatung-app (öffentlich), Pages aus `gh-pages` (App c68a0d42d414) · Prüfstufe: selbst geprüft + unabhängig geprüft (Codex medium, bestanden mit Hinweisen, Hinweis behoben) + von Nico freigegeben (Veröffentlichung, 08.11.2026 direkt in der Sitzung)

## Erledigt

- Hülle `app/` (Manifest, Service Worker, Ersatz `window.claude.use`, Treffer- und Update-Karte, Touch 44 px), Werkzeuge, Inhalt Version 8 unverändert.
- Tests `tests/test_app.py` (19): Build, Manifest, SW-Dateiliste, Symbole, Inhalt unverändert, Rahmen der Live-Seite, Preisfortschreibung, Push-Schutz. `tests/alle-tests.ps1` → Fehler 0.
- Browser (Chrome headless über DevTools-Protokoll, `werkzeuge/browserpruefung/*.mjs`; die eingebaute Browser-Leiste der Claude-App lässt keine Service Worker zu): 375 px hell/dunkel ohne Querscrollen, Konsole leer, `getInstallabilityErrors` leer, SW aktiv ab erstem Besuch ohne Doppel-Laden, Offline-Neuladen mit 5 Preisen, Treffer-Karte, Update-Ablauf (Klick und von außen), Preis-Cache übersteht HTML/ungültige Antworten. Mit Runde-6-Inhalt (Kopie in %TEMP%\kbapp-r6): Preiswecker zeigt preise.json („Lauf in Ordnung“), Wunschpreis setzen/löschen, Touch-Ziele ≥ 44 px (Schrittpunkte per unsichtbarer Trefferfläche).
- Korrekturen dabei: unnötiges Neuladen beim ersten Besuch, Wunschpreis löschen (`preis: null`), Datum deutsch, Touch Runde 6, LF in `.gitattributes`.
- Codex (`docs/pruefungen/2026-11-08-app-huelle/`): R1 nicht bestanden (B1–B3 schwer, B4 mittel), alle bestätigt und behoben; R2 bestanden mit Hinweisen (B4 Rest), behoben und im Browser belegt.
- `docs/anleitung-handy.md` geschrieben; veröffentlicht nach Nicos Freigabe („Ja, veröffentlichen“, 08.11.2026).

## Offen / blockiert

- Live-URL https://nicosteinberg4791-ops.github.io/kaufberatung-app/ geprüft (Chrome headless, `pruefe.mjs --url`): Manifest/Installierbarkeit ok, SW aktiv, 375 px hell/dunkel ohne Querscrollen, offline 5 Preise. **Offen:** Konsole zeigte Ladefehler der Google-Schrift (ERR_CONNECTION_CLOSED, zeitgleich Netzabbrüche zur GitHub-API) → wiederholen; bleibt er, sw.js `schriftCache` ohne Cache-Treffer prüfen. Nicht auf echtem Android-Handy installiert.
- O1/O2 (Nicos Entscheidung 08.11.2026): GitHub Actions + ntfy umsetzen, siehe docs/offene-punkte.md.
- Version 9/10 nachziehen, sobald veröffentlicht (`app_bauen.py --quelle`, dann `browserpruefung/pruefe.mjs`).

## Nächster Schritt

Tägliche Preisabfrage über GitHub Actions mit ntfy-Push (Nicos Entscheidung O1/O2), vorher `werkzeuge/preiswecker_r4.py` (Codex-geprüft, Runde 6) einbinden. Fertig, wenn: erster `workflow_dispatch`-Lauf grün (oder heise-Sperre belegt und Nico gemeldet), preise.json auf gh-pages aktualisiert, Test-Benachrichtigung über ntfy angekommen, Tests Fehler 0, Codex bestanden. Lesen: docs/offene-punkte.md, werkzeuge/preise_aktualisieren.py, Übergabe `C:\Users\Nico\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\side-session-notes\local_e276910c-558e-4959-bd8b-1e3edd860adb\kaufberatung-app-uebergabe-2.md`.
Danach: Version 9 nachziehen (laut Runde 6 live: `Artifact read` → Kopie → `app_bauen.py --quelle … --version "Artifact-Version 9"` → `browserpruefung/pruefe.mjs` → `veroeffentlichen.py`).
