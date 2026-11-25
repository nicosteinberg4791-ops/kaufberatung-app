# Erstprüfung – P2a-2 Gewichtsfassung und Freigabeschranke (Architektur, high)

**Ziel:** Prüfen, ob der Entwurf für Gewichtsfassung und Referenzvergleich sicherstellt, dass keine notenwirksame Schemaänderung ohne neue Fassungsnummer auf gh-pages gelangt.

**Schnitt (Besitzer, 25.11.2026, O24):** Aus P2 abgetrennt, weil R2-01 und R2-02 aus der r1-Korrektur stammen (KERN §3). Rechnung und Schnittstelle (P2a-1) prüft eine eigene Runde, bitte hier nicht.

**Prüfgegenstand:** in `docs/recherche-ux/p2-entwurf.md` §2.1, §5 (Dateihoheit Freigabeschranke), §9.1, §9.3 sowie die Tests 6, 37–42 und 47 (§6, §9.9). Code als Grundlage: `app/finder/bewertung.js:41–67`, `:118–153` (Summen in Feldreihenfolge), `werkzeuge/datenbank.py` (`lade_schema`, `pruefen`, `bauen`), `.github/workflows/finder-daten.yml`, `werkzeuge/veroeffentlichen.py:302–366`, `werkzeuge/herkunft.py`, `werkzeuge/app_bauen.py:175–190`, `daten/schema/kategorien.json`. Vorgeschichte: `bewertung-r1.md` (P2-01, P2-04), `bewertung-r2.md` (R2-01, R2-02).

**Fertigkriterien**
- Kein Weg, die Projektion (§9.3) zu ändern, ohne dass die Nummer steigen muss: Datenworkflow, App-Publish (`veroeffentlichen.py`) und lokale Prüfung, jeweils auch nach einem Wechsel des gh-pages-Elternstands.
- Die Projektion enthält alles, was die angezeigte Zahl bestimmt, einschließlich der Reihenfolge, in der gerechnet wird. Was fehlt (`NICHT_ANWENDBAR`, `PRIO_FAKTOREN` im Code), ist benannt und durch Tests festgeschrieben.
- Fehlt die Referenz, ist sie unlesbar oder nicht erreichbar, bricht jeder Weg ab.
- Der erste Lauf (Referenz ohne `gewichte_version`) ist bestehbar und erzwingt Nummer 1 mit gleicher Projektion.
- Die Tests 6, 37–42 und 47 würden ohne die jeweilige Regel rot.

**Selbstprüfung (Lead):** R2-01 mit Node nachgerechnet (konstruierter Fall 39↔38, Test 40). Schreibwege auf gh-pages per `grep` erhoben: nur `finder-daten.yml` und `veroeffentlichen.py`. Gebaut ist nichts.

**Bekannte Grenzen:** F-1 … F-5 (insbesondere F-5: Umfang der Projektion) sind beim Besitzer offen. `herkunft.py` soll unverändert bleiben. `app_bauen.py` gehört zu P0.

**Prüffragen:**
1. Gibt es einen dritten Weg, auf dem `finder-daten.json` oder das Schema notenwirksam live geht (Routine `datenpflege`, Merge, manueller Push auf gh-pages)?
2. Ist die Prüfung in `veroeffentlichen.py` vor `baue_aus_stand` an denselben Elterncommit gebunden, gegen den der Push mit Lease läuft?
3. Ist die Prüfung in jedem Versuch der Workflow-Schleife umsetzbar, ohne dass ein Lauf nach einem Preis-Push dauerhaft rot bleibt?
4. Ist der Vergleich über `json.loads`-Gleichheit eindeutig genug (Zahl gegen Zahl, Reihenfolge, Unicode), oder gibt es einen Fall, der die Note ändert und gleich bleibt?
