# Messung Pilot Bestpreis (D7, Bauplan Schritt 8)

Ziel (Recherche Abschnitt 8, Punkt 8): über 3–5 Tage Trefferquote je Quelle, Abweichung zum Marktbestpreis und Sperren aus Actions-IPs messen. Grundlage für O12 und für Schritt 9 (Anzeige, Ersatz von `preise.json`).

## Belege und Begriffe

| Kürzel | Lauf | Zeit (UTC) | Stand | Beleg |
|---|---|---|---|---|
| **L1** | lokal, Heimrechner | 22.11.2026 09:13:28 | Arbeitskopie auf 4cb3e60 | `messung/pilot/2026-11-22-tag1-lokal.json` und `.log` |
| **A1** | GitHub Actions `pilot-preise.yml` | 22.11.2026 08:46:30 | 4cb3e60, 85 Tests OK | Lauf-ID **45004369763** (Auszug: `messung/pilot/2026-11-22-tag1-actions-45004369763.log`) |
| Z1–Z3 | lokal, `--zeige saturn <url> --modell <id>` (einzelne Seite, kein Teil von L1) | 22.11.2026 09:21–09:24 | 4cb3e60 | `messung/pilot/2026-11-22-tag1-zeige-saturn-*.log` |

- `messung/` ist laut `.gitignore` nur lokal (nicht versioniert), ebenso `pilot-preise.json`. Öffentlich nachprüfbar ist nur die Actions-Lauf-ID.
- A1 wurde nicht in dieser Sitzung ausgelöst; ausgewertet ist nur die Protokollausgabe (`gh run view --log`). Das Artefakt wurde nicht geladen, deshalb fehlt für A1 die Zahl der heise-Angebote.
- **Treffer** = gültige Angebote nach den Regeln der Shopabfrage (EAN passt, Neuware, lieferbar, EUR im Korridor, Verkäufer = Shop). Bei heise: Zahl der gültigen Händlerangebote.
- **Gesamt** = Preis + Versand. **Bestpreis** = günstigstes gültiges Angebot nach Gesamt über alle automatisch abgefragten Quellen.
- **heise-min** = günstigstes heise-Angebot mit bekanntem Versand (Gesamt). Angebote mit unbekanntem Versand sind getrennt genannt. **Abweichung** = Bestpreis − heise-min.
- Kein Marktbestpreis: MediaMarkt und idealo werden nur verlinkt, nicht abgefragt.

## Tag 1 (22.11.2026), lokal (L1)

| Modell | Treffer je Quelle | Bestpreis (Quelle, Händler) | heise-min | Abweichung | Sperren |
|---|---|---|---|---|---|
| LG OLED65C6ELB | Alternate 1 · heise 12 | **1.349,00 €** (heise, Amazon.de, Versand 0) | 1.349,00 € (Amazon.de) | 0,00 € (0,0 %) | keine |
| Samsung GQ65S90H | Saturn 1 · heise 10 | **1.399,00 €** (eigen, Saturn, Versand 0 laut Seitenzustand) | 1.469,00 € (Samsung Shop); 1.399,00 € bei 5 Händlern mit unbekanntem Versand | −70,00 € (−4,8 %) | keine |
| Ninja AF500EU | Saturn 0 (HTTP 302, s. u.) · Proshop 1 (179,41 €) · heise 20 | **164,00 €** (heise, Coolblue, Versand 0) | 164,00 € (Coolblue); 163,99 € euronics-maxi-media ohne Versandangabe | 0,00 € (0,0 %) | keine; Saturn-URL veraltet |
| Dreame Z30 | Saturn 0 (HTTP 302, s. u.) · Proshop 1 | **553,99 €** (eigen, Proshop, 549,00 € + 4,99 €) | keine heise-URL hinterlegt | nicht messbar | keine; Saturn-URL veraltet |
| Samsung Galaxy S26 Ultra 256 GB | Alternate 1 (1.030,99 €) · Proshop 1 · Saturn 0 (nur Marktplatz, Z1) | **969,00 €** (eigen, Proshop, Versand 0) | keine heise-URL hinterlegt | nicht messbar | keine |

Lokal: alle abgefragten Quellen erreichbar, keine 403/429/Captcha.

## Tag 1 (22.11.2026), GitHub Actions (A1, Lauf 45004369763)

| Modell | Status je Quelle | Bestpreis (Quelle, Händler) | Abweichung zu heise-min | Sperren |
|---|---|---|---|---|
| LG OLED65C6ELB | Alternate ok · heise ok | **1.349,00 €** (heise, Amazon.de) | 0,00 € (Bestpreis ist heise-min) | keine |
| Samsung GQ65S90H | Saturn **403** · heise ok | **1.469,00 €** (heise, Samsung Shop) | 0,00 € (Bestpreis ist heise-min) | Saturn: HTTP 403 auf der Produktseite |
| Ninja AF500EU | Saturn **403** · Proshop **403** (robots.txt) · heise ok | **164,00 €** (heise, Coolblue) | 0,00 € (Bestpreis ist heise-min) | Saturn 403; Proshop: robots.txt nicht lesbar (HTTP 403) |
| Dreame Z30 | Saturn **403** · Proshop **403** (robots.txt) | **kein gültiges Angebot** | nicht messbar | Saturn 403; Proshop 403 |
| Samsung Galaxy S26 Ultra 256 GB | Alternate ok · Proshop **403** (robots.txt) · Saturn **403** | **1.030,99 €** (eigen, Alternate) | keine heise-URL | Saturn 403; Proshop 403 |

Gleiches Sperrbild wie im Vortageslauf 44871394260 (21.11.2026, Stand 79daf34, vor Runde 8).

## Vergleich lokal gegen Actions (Tag 1)

| Modell | L1 | A1 | Unterschied | Ursache |
|---|---|---|---|---|
| LG OLED65C6ELB | 1.349,00 € | 1.349,00 € | 0 € | keine (Alternate und heise in beiden) |
| Samsung GQ65S90H | 1.399,00 € | 1.469,00 € | A1 +70,00 € | Saturn in Actions gesperrt |
| Ninja AF500EU | 164,00 € | 164,00 € | 0 € | heise liefert den Bestpreis |
| Dreame Z30 | 553,99 € | – | A1 ohne Preis | Saturn und Proshop in Actions gesperrt, keine heise-URL |
| Galaxy S26 Ultra | 969,00 € | 1.030,99 € | A1 +61,99 € | Proshop in Actions gesperrt |

In Actions kommen nur Alternate und heise durch. Saturn oder Proshop liefern lokal in 3 von 5 Modellen den Bestpreis oder den einzigen Preis.

## Zusatzbelege (Einzelseiten, lokal)

- **Z1 Saturn S26** (`…-zeige-saturn-s26.log`): Angebot mit passender EAN 5715328322677 für 1.115,99 € abgelehnt, Grund „Marktplatzangebot (Seitenzustand)“. Die Regel greift wie vorgesehen.
- **Z2 Saturn AF500EU** (`…-zeige-saturn-af_ninja_af500.log`): Die hinterlegte URL (Artikel 2925590) leitet per 302 auf Artikel 134709790. Die Zielseite enthält ein gültiges Saturn-Angebot mit EAN 0622356270373 für **219,99 €** (Versand 0 laut Seitenzustand). Am Bestpreis 164,00 € ändert das nichts.
- **Z3 Saturn Dreame Z30** (`…-zeige-saturn-sauger_dreame_z30.log`): Die hinterlegte URL (Artikel 2941591) leitet per 302 auf Artikel 142725586. Die Zielseite enthält ein gültiges Saturn-Angebot mit EAN 6976233677231 für **294,99 €** (Versand 0 laut Seitenzustand). Damit liegt der Tag-1-Bestpreis lokal um **259,00 €** zu hoch (553,99 € statt 294,99 €). Ursache ist die veraltete URL in `daten/pilot_modelle.json`, nicht die Auswertung. Die Shopabfrage folgt Weiterleitungen absichtlich nicht.
- heise listet für den GQ65S90H ein Alternate-Angebot (1.399,00 €). In `pilot_modelle.json` steht dazu „Alternate: keine Produktseite gefunden“. Eine Alternate-Seite gibt es also vermutlich. Nicht geprüft.

## Nachtrag 22.11.2026: Saturn-URLs umgestellt (Besitzer: „Ja, umstellen“)

Die Saturn-URLs für AF500EU (alt 2925590 → 134709790) und Dreame Z30 (alt 2941591 → 142725586) in `daten/pilot_modelle.json` zeigen jetzt auf die Ziele der Weiterleitung. `tests/alle-tests.ps1`: Fehler 0. Kontrolllauf **L1b** lokal, 22.11.2026 10:52:11 UTC (`messung/pilot/2026-11-22-nach-url-umstellung.json` und `.log`):

| Modell | Saturn | Bestpreis | Änderung zu L1 |
|---|---|---|---|
| Ninja AF500EU | ok, 1 Treffer, 219,99 € (Versand 0) | 164,00 € (heise, Coolblue) | keine |
| Dreame Z30 | ok, 1 Treffer, 294,99 € (Versand 0) | **294,99 €** (eigen, Saturn) | −259,00 € |

Die übrigen drei Modelle sind unverändert gegenüber L1. Für Tag 1 bleibt L1 der Messwert. Ab Tag 2 gelten die neuen URLs. In Actions ändert sich nichts, solange Saturn dort mit 403 sperrt. Damit Actions die neuen URLs überhaupt nutzt, braucht es außerdem einen Push.

## Messplan Tag 2–5 (23.–26.11.2026)

**Vor Tag 2, Entscheidung des Besitzers:**
1. ~~Saturn-URLs für AF500EU und Dreame Z30 umstellen?~~ Erledigt am 22.11. (Nachtrag oben).
2. Actions-Läufe Tag 2–5 freigeben (je Tag ein `workflow_dispatch`, ohne Push, Ergebnis nur als Artefakt mit 14 Tagen Aufbewahrung)?
3. Optional: heise-URLs für Dreame Z30 und Galaxy S26 ermitteln, damit die Abweichung für alle 5 Modelle messbar wird. Das wären 2 heise-Anfragen mehr je Lauf.

**Ablauf je Tag (gleiches Zeitfenster, ca. 09:00–10:30 MEZ, Abstand lokal zu Actions unter 60 min):**

| Schritt | Befehl | Beleg |
|---|---|---|
| lokal | `python -X utf8 -I werkzeuge/shopabfrage.py --aus messung/pilot/<datum>-lokal.json` (Ausgabe in `<datum>-lokal.log`) | Lauf-Datei |
| Actions (nur mit Freigabe) | `gh workflow run pilot-preise.yml`, danach Ausgabe mit `gh run view <id> --log` lesen | Lauf-ID |
| Auswertung | gleiche Tabelle wie Tag 1, je Umgebung eine Zeile je Modell | dieser Bericht |

**Kennzahlen am Ende (Tag 5, 26.11.):**
- Trefferquote je Quelle und Umgebung = Läufe mit mindestens einem gültigen Angebot ÷ Läufe mit Abfrage (Ziel lokal ≥ 4/5 je Quelle).
- Abweichung Bestpreis zu heise-min je Modell (Mittel und Spanne in € und %). Zusätzlich die Zahl der Tage, an denen eine eigene Abfrage günstiger war als heise.
- Sperren je Quelle und Umgebung (403, robots.txt nicht lesbar, 429, Captcha), Weiterleitungen (302), Marktplatzablehnungen.
- Preisstabilität: Bestpreiswechsel je Modell über die 5 Tage.

**Abbruch:** 429, Captcha oder eine Challenge lokal bei einer Quelle → diese Quelle sofort aus der Messung nehmen und in `quellen.json` vermerken (Leitregel, nie umgehen). heise-Last: Pilot 3 Produktseiten (LG, S90H, AF500EU) plus robots.txt je Lauf, zusätzlich zu höchstens 16 Anfragen aus `preise.yml`.

**Hinweis:** In `messung/pilot/` liegen außerdem `2026-11-22.json` (Stand 08:59:43 UTC) und `verlauf.md`. Beide stammen nicht aus dieser Messung, wahrscheinlich von einer geplanten Aufgabe, die eine andere Sitzung eingerichtet hat (`.gitignore`, Eintrag „tägliche lokale Messung“). Die Preise sind dieselben wie in L1. Vor Tag 2 klären, ob diese Aufgabe den lokalen Lauf übernimmt, damit nicht doppelt abgefragt wird.

**Danach:** Zusammenfassung im Kopf dieses Berichts, Entscheidung zu O12 und zu Schritt 9.

## Vorlage O12 (Besitzer)

**Frage:** Saturn und Proshop sperren Actions-IPs. Läuft der Pilot dort nur mit Alternate und heise, oder vom Heimrechner?

**Beleg Tag 1:** In Actions (45004369763) liefern Saturn (4 von 4 Seiten 403) und Proshop (3 von 3, robots.txt 403) nichts. Lokal (L1) liefern beide. Ohne sie wird S90H um 70,00 € und S26 um 61,99 € teurer angezeigt, der Dreame Z30 bekommt gar keinen Preis.

| Weg | Vorteil | Nachteil |
|---|---|---|
| **A** Actions nur mit Alternate + heise | läuft unabhängig vom Rechner, schon vorhanden, klar regelkonform | 3 von 5 Modellen schlechter oder ohne Preis; der Bestpreis-Mix bringt dann gegenüber heise kaum etwas |
| **B** Lauf vom Heimrechner (geplante Aufgabe) | alle vier Quellen, Tag 1 vollständig | nur wenn der Rechner läuft; Ergebnis muss von lokal nach `gh-pages`/App (neuer Push-Weg, braucht eigene Freigabe); **Rechtsfrage s. u.** |
| **C** Mischung: Actions mit Alternate + heise als Grundlage, Heimrechner ergänzt Saturn/Proshop, wenn er läuft | nie ganz ohne Preis | zwei Wege pflegen, Zusammenführung nötig; Rechtsfrage wie B |

**Offene Rechtsfrage zu B und C (nicht geklärt, keine Rechtsauskunft):** Die Leitregel sagt: „403 … bedeuten: Quelle nicht nutzen, nie umgehen“. Saturn und Proshop sperren erkennbar gezielt Rechenzentrums-IPs, lokal sperren sie nicht, und robots.txt erlaubt die Pfade. Ob ein Lauf vom Heimrechner, *weil* Actions gesperrt ist, als Umgehung einer technischen Schutzmaßnahme gilt, ist nicht belegt. Das muss der Besitzer entscheiden. Lokal gilt die Leitregel unverändert: Sobald dort 403, 429 oder ein Captcha auftritt, die Quelle nicht nutzen.

**Besitzer 22.11.2026:** „Beide messen, Tag 5“. Bis Tag 5 werden lokal und Actions gemessen, endgültig entschieden wird am 26.11. Damit sind die Actions-Läufe für Tag 2–5 freigegeben (je Tag ein `workflow_dispatch`, kein Push). Saturn-URLs am selben Tag umgestellt (Nachtrag oben).

**Empfehlung:** O12 erst nach Tag 5 endgültig entscheiden und bis dahin beide Umgebungen messen. Fachlich spricht Tag 1 für B oder C, regeltreu ist sicher nur A. Wenn die Rechtsfrage für B/C nicht klar mit Ja beantwortet wird, A nehmen und den Nutzen des Bestpreis-Mix ehrlich als gering ausweisen.
