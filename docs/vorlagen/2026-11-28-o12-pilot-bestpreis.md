# Entscheidungsvorlage O12: Pilot Bestpreis (D7), Stand 28.11.2026

**Frage:** Saturn und Proshop sperren GitHub-Actions-IPs (403). Läuft der Pilot nur mit den Quellen, die in Actions liefern (Alternate, heise), oder vom Heimrechner?
Quellen: `docs/pruefungen/2026-11-21-pilot-bestpreis/messung.md` (M), lokale Messdateien `messung/pilot/2026-11-22…27.json` und `verlauf.md` (V, nicht versioniert, nur beim Besitzer), `gh run list --workflow pilot-preise.yml` (G).

## Datenlage je Tag und Umgebung

| Tag | Actions | Lokal (Heimrechner) |
|---|---|---|
| 1 (22.11.) | Lauf 45004369763: Saturn 403 (4 von 4), Proshop 403 (3 von 3, robots.txt); Alternate, heise ok (M) | alle 5 Modelle mit Preis, keine Sperre (M, L1) |
| 2–5 (23.–26.11.) | **nicht gemessen:** G zeigt nur 2 Pilotläufe (44871394260 am 21.11., 45004369763 am 22.11.), keine an Tag 2–5, obwohl freigegeben (M) | 23.–25.11. Saturn 3 von 4 Seiten ok (die vierte, S26, ohne gültiges Angebot), Proshop 2–3 von 3 ok (V, JSON) |
| 5 (26.11.) | nicht gemessen | **Saturn 0 von 4: robots.txt HTTP 403 auch lokal**; Bestpreis wechselte bei S90H, Ninja, Dreame (V) |
| 6 (27.11.) | nicht gemessen | Saturn wieder 3 von 4 ok (V) |

- Die lokalen Läufe 23.–27.11. stammen von einer geplanten Aufgabe (V, M Hinweis), nicht aus dem Messplan; Zeit etwa 09:12 UTC, aber ohne gleichzeitigen Actions-Lauf. Der Vergleich beider Umgebungen am selben Tag liegt daher nur für Tag 1 vor.
- Wirkung Tag 1: ohne Saturn/Proshop kostet S90H +70,00 € (1.469 statt 1.399), S26 +61,99 € (1.030,99 statt 969), Dreame Z30 ohne Preis (M).
- Seit der URL-Umstellung (22.11.) liefert Saturn lokal für Dreame Z30 294,99 € statt Proshop 553,99 € (V, 23.–25. und 27.11.); am 26.11. fiel der Preis wegen der Saturn-Sperre zurück auf 553,99 € (V).
- Bestpreis liegt an 6 Tagen nur teils bei eigener Abfrage (Saturn/Proshop/Alternate), teils bei heise (V). Die Kennzahlen aus M (Trefferquote, Spanne zu heise-min) sind noch nicht berechnet.

## Optionen

- **A: Actions mit Alternate + heise.** Folge: regelkonform, läuft ohne Rechner; 3 von 5 Modellen teurer oder ohne Preis (M, Tag 1), Dreame Z30 und S26 ohne heise-URL, also ohne Ersatz.
- **B: Lauf vom Heimrechner.** Folge: alle Quellen, aber nur bei laufendem Rechner, eigener Push-Weg nötig, Rechtsfrage offen. Lokal sperrt Saturn nicht verlässlich (26.11., V): Ausfälle sind einzuplanen, nach Leitregel nicht zu umgehen.
- **C: Actions als Grundlage, Heimrechner ergänzt Saturn/Proshop.** Folge: nie ganz ohne Preis; zwei Wege, Zusammenführung, gleiche Rechtsfrage wie B.

## Empfehlung

**Zunächst A beschließen, C nur bei positiver Rechtsklärung.** Grund: Nur A ist belegt regelkonform; B/C hängen an der offenen Rechtsfrage und an einem Rechner, der nicht garantiert läuft. Der Mehrwert von Saturn/Proshop ist lokal belegt (V), in Actions für Tag 2–5 aber nicht gemessen. Für eine belastbare Entscheidung zwischen A und C fehlen Actions-Läufe an Tag 2–5; einen Lauf je Tag nachholen ist nicht möglich (Tage vorbei), wohl aber 3–5 weitere Tage mit täglichem `workflow_dispatch` plus lokalem Lauf (Besitzerfreigabe nötig).

## Offene Rechtsfrage (keine Rechtsauskunft)

Gilt ein Lauf vom Heimrechner, *weil* Actions-IPs gesperrt sind, als Umgehung einer Schutzmaßnahme? Leitregel: 403 bedeutet Quelle nicht nutzen. robots.txt erlaubt die Pfade (M). Zusätzlich offen: O6 (heise-Nutzungsbedingungen). Entscheidung liegt beim Besitzer.
