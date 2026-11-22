# Stand – Kaufberatung-App

Stand: 22.11.2026 · `main` = origin/main (letzter Commit siehe `git log`, Pilot-Abschluss 4792e8b, Namenskorrektur 32e60b0) auf `github.com/<konto>/kaufberatung-app` (öffentlich), Pages aus `gh-pages`. Veröffentlicht: App 090ac453670e, Inhalt Artifact-Version 30. Pilot D7: selbst geprüft bis 4792e8b · unabhängig: Codex 8 Runden, nicht bestanden · Besitzer: Abschluss mit Leitplanke und Push 22.11. freigegeben.

## Ablauf und Werkzeuge

- **Inhalt nachziehen:** `Artifact read` → `werkzeuge/app_bauen.py --quelle <datei>` → `tests/alle-tests.ps1` → `werkzeuge/browserpruefung/pruefe.mjs` (lokal und `--url`) → `werkzeuge/veroeffentlichen.py` (nur mit Auftrag).
- **Tägliche Preisabfrage:** `.github/workflows/preise.yml` (05:23 UTC plus Nachläufe, bis 01.12.2026), höchstens 16 heise-Anfragen je Lauf; ntfy und Web Push (D6). Preiswecker 24 Modelle, Wunschpreise nur per `localStorage` bzw. Secret `WUNSCHPREISE`.
- **Pilot Bestpreis (D7):** `daten/quellen.json`, `daten/pilot_modelle.json` (5 Modelle), `werkzeuge/shopabfrage.py` → `pilot-preise.json` (nicht versioniert), `.github/workflows/pilot-preise.yml` (nur `workflow_dispatch`). Automatisch: Saturn, Alternate, Proshop, heise; nur Link: MediaMarkt, idealo.
- **Bekannt:** Saturn und Proshop sperren Actions-IPs (403 bei robots.txt, Lauf 44871394260); lokal liefern alle. Geplante Läufe können sich um Stunden verspäten. `pruefe.mjs` „r6.punkte“ `false/false/false` ist ein Messartefakt.

## Erledigt seit letzter Übergabe

- Codex r8 bewertet: [bewertung-r8.md](docs/pruefungen/2026-11-21-pilot-bestpreis/bewertung-r8.md); Befunde R8-01..05 klein behoben (Klasse `Runde8`, 85 Tests, Rot-Gegenprobe gegen 5897b2c 5/5).
- Livelauf lokal 22.11.: S90H 1.399 € Saturn eigen, keine Fehlsperre; Saturn-S26 als Marktplatz erkannt.
- Leitplanke und 5 bekannte Grenzen dokumentiert; Vorname in Prüfdateien durch „Besitzer“ ersetzt; gepusht.
- Pilotverlauf r1–r8: [verlauf.md](docs/pruefungen/2026-11-21-pilot-bestpreis/verlauf.md).

## Entscheidungen

- D7 Nachtrag 22.11.2026: Abschluss ohne Runde 9, Leitplanke für die Shopabfrage ([entscheidungen.md](docs/entscheidungen.md)).

## Offen

- **O12** (Besitzer): Saturn/Proshop sperren Actions-IPs: Pilot dort nur mit Alternate+heise oder Lauf vom Heimrechner?
- **O13** (Besitzer): alte Vorlagen mit Shoptexten in öffentlicher Historie (79daf34) belassen?
- **O10** Impressum nötig? · **O5** Wunschpreise als Secret? · **O6** heise-Nutzungsbedingungen ungeklärt · **O7** Web Push scharf schalten (alle Besitzer).
- Nicht auf echtem Android-Handy geprüft: neue Icons, Push-Zustellung, Besitzer-Merker.

## Nächster Schritt

**Pilot messen, Tag 1** (Bauplan Schritt 8): lokalen Lauf `python -X utf8 -I werkzeuge/shopabfrage.py --aus <scratch>` ausführen; einen Actions-Lauf von `pilot-preise.yml` nur nach Besitzerfreigabe auslösen. Ergebnis in `docs/pruefungen/2026-11-21-pilot-bestpreis/messung.md` als Tabelle je Modell und Umgebung (lokal/Actions): Treffer je Quelle, Bestpreis mit Quelle, Abweichung zum günstigsten heise-Angebot, Sperren. Dazu Messplan für Tag 2–5 und O12 dem Besitzer vorlegen.
**Fertig, wenn:** `messung.md` enthält Tag 1 für alle 5 Modelle (mindestens lokal), jede Zahl mit Lauf-Datei oder Actions-Lauf-ID belegt, und der Messplan steht.
**Lesen:** `docs/recherche-eigene-preissuche.md` Abschnitt 8 · `werkzeuge/shopabfrage.py` (Kopf) · `.github/workflows/pilot-preise.yml`.
