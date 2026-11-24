# P2 Notenmodell – Plan zur Freigabe

Stand: 24.11.2026 · Lead: Claude · Grundlage: `00-konzept.md` §2.4, §4 (Zeile P2), §5 mit D12/D13 (`docs/entscheidungen.md`).
Status: **vom Besitzer freigegeben wie vorgeschlagen (24.11.2026, D25).** Nichts davon ist gebaut.

## 1. Zuschnitt nach D12 und D13

D12 behält die eine Gesamtnote; P2 baut **keine zwei Achsen** („Ausstattung“/„Getestet“ als getrennte Noten). D13: Tests vorerst nur als Link, also bleibt die Mischung 0,6 Test + 0,4 R in der Praxis ungenutzt.

| Teil aus §4 P2 | nach D12/D13 | Inhalt |
|---|---|---|
| Zwei Achsen | **entfällt** | – |
| Nutzungsgewichte mit Version | bleibt | Antwortfaktoren (`antworten[].gewichte`) gibt es schon. Neu: Version je Kategorie (`gewichte_version`, Datum) und Ausgabe der Version in Note, Notenblatt und Methodik, damit eine Note mit ihrer Gewichtsfassung nachvollziehbar bleibt. Fachliche Freigabe der Gewichte durch dich (Bericht 02 c). |
| Schemafelder Testquelle | bleibt, schmal | je Kategorie höchstens eine Primärquelle `testquelle {name, url, methodik_url, stand}`. `tests[]` am Modell bleibt Link (D13). Die Rechenstelle für `punkte` bleibt wie heute gesperrt, bis eine Quelle mit Nutzungsrecht da ist. |
| Maße B/H/T für P6 | bleibt | einheitliche Felder `breite_cm`, `hoehe_cm`, `tiefe_cm`, je Kategorie als Filter- oder Bewertungsfeld (Gewicht 0 = nur Filter). Teilweise vorhanden (Saugroboter `hoehe_cm`, Fernseher/Spülmaschine `breite_cm`), wird vereinheitlicht. Werte trägt erst P6 ein, nur mit Beleg. |
| Blatt „Warum diese Punkte“ (3 Ebenen) | bleibt | Ebene 1 Zahl auf der Karte · Ebene 2 Blatt mit Balken je Merkmal, Gewicht für deine Antworten, „bei Nutzung Y wäre es Z“, was fehlt (aus vorhandenem `beitraege`/`fehlend`) · Ebene 3 Werte mit Quelle, Datum, Link zur Methodik. Ersetzt die heutige Liste „Stärken laut Datenblatt“ (`finder.js:552`). |
| Methodikseite | bleibt | eigenes Ziel `s=methodik`: Abschlag ×0,85 − 3, Abdeckungsabzug, unter 70 % keine Note, Gleichstand → günstiger, Preis nie in der Note, Gewichtsfassung je Kategorie, was „getestet“ hieße. Im Menü, nicht im Fuß. |

## 2. Abhängigkeit P0 und vorgeschlagene Teilung

P0 (Aufteilung von `finder.js`, heute 832 Zeilen, noch kein `ansichten/`) ist nicht gebaut. Notenblatt und Methodik sind Ansichten und gehören nach `ansichten/notenblatt.js`, `methodik.js`. Vorschlag:

- **P2a Daten und Rechnung** (ohne P0, parallel möglich): `daten/schema/kategorien.json` (Version, `testquelle`, Maße), `werkzeuge/datenbank.py` (Prüfung der neuen Felder), `app/finder/bewertung.js` (Version durchreichen, Funktion „Note bei anderer Antwort“ für Ebene 2), `docs/punkteschema.md`, Tests `test_bewertung.mjs`, `test_datenbank.py`. Keine sichtbare Änderung außer Version im Datenstand.
- **P2b Ansichten** (nach P0): Notenblatt in 3 Ebenen, Methodikseite, Router-Ziel; Browsertest mit `pruefe.mjs`, Design-Kritik per Bildschirmfoto (Skill `frontend-design`).

## 3. Ablauf und Prüfpunkte

1. **Entwurf** (Opus 5.5 high): `docs/recherche-ux/p2-entwurf.md` mit Schemaänderung (JSON-Beispiel je neuem Feld), Rechenregel „bei Nutzung Y“, Datenfluss bis zur Ansicht, Testliste.
2. **Architekturprüfung vor Umsetzung** (Konzept §4: Codex high, Skill `pruefschleife`) auf den Entwurf.
3. **Gewichte fachlich freigeben** (du): Tabelle je Kategorie mit Feld, Grundgewicht, Faktoren je Antwort; heutige Werte als Vorschlag, Änderungen nur von dir.
4. P2a bauen (medium), Tests rot→grün, `datenbank.py pruefen` 0 Fehler, Codex medium.
5. P0 (eigenes Paket), danach P2b bauen, Browsertest, Codex medium.
6. Veröffentlichung gesammelt am Ende (Konzept §4) oder nach P2b, wie du entscheidest.

**Fertig (P2), wenn:** jede Note nennt ihre Gewichtsfassung; Schema hat `testquelle` und B/H/T mit Prüfung; Notenblatt zeigt alle 3 Ebenen mit Quelle und Datum; Methodikseite erreichbar; Tests, Sammellauf und Datenbank 0 Fehler; Codex bestanden.

## 4. Grenzen

- Kein neuer Notenwert ohne Test (D12/D13 und §3); „bei Nutzung Y wäre es Z“ ist eine Rechnung aus denselben Datenblattwerten, keine neue Aussage.
- Keine Labore mischen; Testquelle nur als Link mit Datum.
- Maße nur mit Beleg (P6); fehlende Maße bleiben leer.

## 5. Zu entscheiden (Besitzer)

- **E-P2-1:** Teilung P2a (sofort, parallel zu P0) / P2b (nach P0) – Vorschlag: ja.
- **E-P2-2:** Gewichte: heutige Werte als Fassung 1 übernehmen und nur offensichtliche Lücken vorschlagen – Vorschlag: ja.
- **E-P2-3:** Methodikseite verlinkt aus Notenblatt und Menü; Fuß-Hinweis entfällt – Vorschlag: ja.
