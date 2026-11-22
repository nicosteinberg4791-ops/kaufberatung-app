# Stand – Kaufberatung-App

Stand: 22.11.2026 · `main` 1 Commit vor origin/main (Messung Tag 1, 9dadd61, nicht gepusht; letzter Commit siehe `git log`) auf `github.com/<konto>/kaufberatung-app` (öffentlich), Pages aus `gh-pages`. Veröffentlicht: App 090ac453670e, Inhalt Artifact-Version 30. Pilot D7: selbst geprüft bis 4792e8b · unabhängig: Codex 8 Runden, nicht bestanden · Besitzer: Abschluss mit Leitplanke und Push 22.11. freigegeben.

## Ablauf und Werkzeuge

- **Inhalt nachziehen:** `Artifact read` → `werkzeuge/app_bauen.py --quelle <datei>` → `tests/alle-tests.ps1` → `werkzeuge/browserpruefung/pruefe.mjs` (lokal und `--url`) → `werkzeuge/veroeffentlichen.py` (nur mit Auftrag).
- **Tägliche Preisabfrage:** `.github/workflows/preise.yml` (05:23 UTC plus Nachläufe, bis 01.12.2026), höchstens 16 heise-Anfragen je Lauf; ntfy und Web Push (D6). Preiswecker 24 Modelle, Wunschpreise nur per `localStorage` bzw. Secret `WUNSCHPREISE`.
- **Pilot Bestpreis (D7):** `daten/quellen.json`, `daten/pilot_modelle.json` (5 Modelle), `werkzeuge/shopabfrage.py` → `pilot-preise.json` (nicht versioniert), `.github/workflows/pilot-preise.yml` (nur `workflow_dispatch`). Automatisch: Saturn, Alternate, Proshop, heise; nur Link: MediaMarkt, idealo.
- **Bekannt:** Saturn und Proshop sperren Actions-IPs (Saturn 403 auf der Produktseite, Proshop 403 bei robots.txt; Läufe 44871394260, 45004369763); lokal liefern alle. Saturn-URLs für AF500EU und Dreame Z30 leiteten per 302 auf neue Artikelnummern um; am 22.11. umgestellt. Geplante Läufe können sich um Stunden verspäten. `pruefe.mjs` „r6.punkte“ `false/false/false` ist ein Messartefakt.

## Erledigt seit letzter Übergabe

- Pilot D7 abgeschlossen (Codex r8 bewertet, Leitplanke, gepusht 22.11.); Verlauf r1–r8: [verlauf.md](docs/pruefungen/2026-11-21-pilot-bestpreis/verlauf.md).
- Messung Tag 1 (22.11.): [messung.md](docs/pruefungen/2026-11-21-pilot-bestpreis/messung.md), lokal alle 5 Modelle mit Preis, Actions (45004369763) nur Alternate und heise; Messplan Tag 2–5 und Vorlage O12 stehen dort.
- Saturn-URLs AF500EU/Z30 auf neue Artikelseiten umgestellt (alte leiteten per 302 um); Kontrolllauf: Z30 294,99 € statt 553,99 €; Tests Fehler 0 (9dadd61).

## Entscheidungen

- D7 Nachtrag 22.11.2026: Abschluss ohne Runde 9, Leitplanke für die Shopabfrage ([entscheidungen.md](docs/entscheidungen.md)).

## Offen

- **O12** (Besitzer): Saturn/Proshop sperren Actions-IPs: Pilot dort nur mit Alternate+heise oder Lauf vom Heimrechner? Vorläufig beide messen, Entscheidung am 26.11. (Tag 5); Rechtsfrage Heimrechner offen (`messung.md`).
- **O13** (Besitzer): alte Vorlagen mit Shoptexten in öffentlicher Historie (79daf34) belassen?
- **O10** Impressum nötig? · **O5** Wunschpreise als Secret? · **O6** heise-Nutzungsbedingungen ungeklärt · **O7** Web Push scharf schalten (alle Besitzer).
- Nicht auf echtem Android-Handy geprüft: neue Icons, Push-Zustellung, Besitzer-Merker.

## Nächster Schritt

**Pilot messen, Tag 2–5** (23.–26.11., Bauplan Schritt 8) nach dem Messplan in `messung.md`. Besitzer 22.11.: O12 vorläufig „beide messen, Entscheidung Tag 5“, damit Actions-Läufe Tag 2–5 freigegeben (je Tag ein `workflow_dispatch`). Saturn-URLs AF500EU/Z30 am 22.11. umgestellt (9dadd61). Für Actions mit neuen URLs vorher Push nötig (Besitzer). Klären, ob die geplante lokale Messung (`messung/pilot/`, andere Sitzung) den lokalen Lauf übernimmt.
**Fertig, wenn:** `messung.md` enthält Tag 2–5 je Umgebung, die Kennzahlen am Ende und eine Entscheidungsvorlage für O12 und Schritt 9.
**Lesen:** `docs/pruefungen/2026-11-21-pilot-bestpreis/messung.md` (Messplan) · `daten/pilot_modelle.json`.
