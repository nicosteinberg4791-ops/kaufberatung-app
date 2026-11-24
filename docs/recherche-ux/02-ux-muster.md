# UX-Muster für Führung, Ergebnis, Note und Preise (Recherche, 24.11.2026)

Stand: Webrecherche am 24.11.2026. Kennzeichnung: **[Q]** = belegt durch die genannte URL, **[A]** = eigene Ableitung, nicht belegt. Hinweis zur Beleglage: NN/g-Artikel zu Vergleichstabellen, Progressive Disclosure, Wizards, Filtern, Satisficing und Baymard (Vergleichstool) waren lesbar. Baymards Guided-Selling-Studie und Mobile-Vergleich liegen hinter der Bezahlschranke, RTINGS-Gewichte hinter dem Login, Stiftung-Warentest-Gewichte hinter der Bezahlschranke, Wirecutter-Original ließ sich nicht abrufen (nur eine Spiegelseite). Das ist unten jeweils vermerkt.

---

## 1. Ideale Führung

**Befund**
- Wizards passen für Neulinge und seltene Aufgaben; wer es oft nutzt, braucht einen schnelleren Weg. Alle Schritte als Liste zeigen, aktuellen hervorheben, vorab sagen, wie viele Schritte es sind, expliziter Zurück-/Weiter-Knopf mit Zielnamen, Verzweigung, damit nur Relevantes erscheint, sinnvolle Voreinstellungen, Abbruch und Wiederaufnahme. Staged Disclosure funktioniert schlecht, wenn Nutzer zwischen Schritten hin und her müssen. [Q] https://www.nngroup.com/articles/wizards/ und https://www.nngroup.com/articles/progressive-disclosure/
- Nutzer geben sich meist mit „gut genug" zufrieden (Satisficing): Kernaussage zuerst, Details danach, Interaktionskosten senken. [Q] https://www.nngroup.com/articles/satisficing/
- Entscheidungszeit steigt mit Zahl und Komplexität der Optionen (Hick); komplexe Aufgabe in kleine Schritte teilen, Empfehlung hervorheben, aber nicht bis zur Sinnlosigkeit vereinfachen. [Q] https://lawsofux.com/hicks-law/
- Filter vs. Tabelle: NN/g ordnet Filter dem „Ausschließen" zu, Vergleichstabellen dem Abwägen mehrerer Eigenschaften. Explorierende Nutzer profitieren von sofort aktualisierten Ergebnissen, Nutzer mit klaren Kriterien von gebündeltem Anwenden („Anwenden"-Knopf, gerade mobil). [Q] https://www.nngroup.com/articles/applying-filters/ (Zuordnung compensatory/noncompensatory aus Suchtreffer-Zusammenfassung zu NN/g, nicht im Volltext geprüft)
- Filterlabels in Kundensprache, nicht in Spezifikationscodes; Fachbegriffe im Kontext erklären (Info-Symbol); Reihenfolge nach Relevanz für die Entscheidung. [Q] https://www.nngroup.com/articles/filter-categories-values/
- Herstellerblogs (parteiisch, nur Richtung): nach Situation fragen statt nach Datenblattwerten, Fortschrittsbalken, kein Jargon. [Q] https://www.uxmatters.com/mt/archives/2012/11/best-practices-for-online-guided-selling-experiences.php
- Käufertypen: Maximizer sind mit ihrer Wahl in einem E-Commerce-Experiment weniger zufrieden als Satisficer. [Q] https://wildlab.cs.washington.edu/Publications_files/Moser_CHI2017.pdf. Die Choice-Overload-Belege sind umstritten (Jam-Studie wird oft überinterpretiert). [Q] https://rd.springer.com/chapter/10.1007/978-1-4899-7637-6_18

**Muster für uns**
1. **Drei Einstiege auf der Kategorieseite** [A], je ein großer Knopf:
   - „Schnell empfehlen" (3 Fragen, ein Ergebnis) für Satisficer/Laien.
   - „Alle Modelle vergleichen" (direkt Liste mit Filtern, Tabelle) für Maximizer/Experten.
   - „Ich kenne schon ein Modell" (Suchfeld/Modellauswahl, dann „Ist das gut? Was gibt es Besseres/Günstigeres?") [A].
2. **Nutzung vor Budget** [A]: Die Frage „Wofür?" erzeugt die Gewichtung der Note, das Budget filtert nur. Budget als letzter Schritt und überspringbar („Egal / Hilf mir einzuschätzen" zeigt typische Preisstufen der Kategorie).
3. **3 bis 4 Fragen, jede einzeln, mit Antwortkarten statt Feldern**, Kopfzeile „Frage 2 von 4", Zurück-Pfeil, „Weiß nicht" als gleichwertige Antwort (setzt Standard und merkt sich das als Unsicherheit). [A, gestützt auf Wizards-Artikel]
4. **Live-Vorschau**: Unter den Fragen ein schmaler Streifen „Aktuell passend: 9 von 14 Modellen · Spitzenreiter: Sony WH-CH720N". Aktualisiert sofort nach jeder Antwort; Knopf „Ergebnis ansehen" ist ab Frage 1 aktiv (Überspringen). [A; Begründung: NN/g empfiehlt Sofortfeedback für Explorierende, Anwenden-Knopf für Zielstrebige]
5. **Zustand merken**: Antworten im lokalen Speicher, „Neu starten" und „Antworten ändern" auf dem Ergebnis (kein Zurück-Zwang). [A]

Textskizze Kategorieseite „Kopfhörer":
```
Kopfhörer
[ Schnell empfehlen   (ca. 1 Min) ]
[ Alle 24 Modelle vergleichen     ]
[ Ich kenne schon ein Modell      ]
```
Textskizze Frage:
```
‹ Zurück      Frage 2 von 4      Überspringen
Wofür brauchst du sie vor allem?
[ Pendeln / Bahn ] [ Sport ] [ Zuhause Musik ]
[ Telefonieren ]  [ Weiß nicht ]
-----------------------------------------
Passt aktuell: 11 von 24 · Vorn: Modell X
[ Ergebnis ansehen ]
```

---

## 2. Ergebnisseite

**Befund**
- Wirecutter-Aufbau: „Warum du uns trauen kannst", „Für wen das ist", „Wie wir ausgewählt haben", Hauptempfehlung („Our pick": das eine Produkt, das die meisten kaufen sollten, nach Test, Ausstattung, Preis-Gegenwert), Budget-Pick, Upgrade-Pick, „Flaws but not dealbreakers" (Warnungen mit Einordnung), weitere gute Optionen, Wettbewerb (warum andere nicht empfohlen). [Q] Spiegelseite https://sonicgame.netlify.app/host-https-www.nytimes.com/wirecutter/blog/anatomy-of-a-guide (Original nytimes.com war nicht abrufbar; Überschriften nicht live geprüft)
- Which? vergibt Siegel nach Prozentschwelle: Best Buy ab 71 %, Great Value ab 65 % und unter dem Preis der meisten TVs derselben Größe, Don't Buy bis 45 %. Der Score selbst ignoriert den Preis ausdrücklich. [Q] https://www.which.co.uk/reviews/televisions/article/how-we-test-televisions
- Stiftung Warentest vermerkt je Gerät das Untersuchungsprogramm und weist darauf hin, dass Noten verschiedener Testprojekte nicht direkt vergleichbar sind (Ehrlichkeit über Unsicherheit/Vergleichbarkeit). [Q] https://www.test.de/Bluetooth-Kopfhoerer-Test-4378783-4378789/ (Treffer der Suche; Text der Hauptseite nicht vollständig geprüft)

**Muster für uns**
1. **Ein „Unsere Wahl" plus zwei Alternativen**, nicht eine Karte allein: *Unsere Wahl* (passt zu deinen Antworten), *Günstiger* (Preisstufe darunter, mit „Das gibst du auf: ..."), *Besser, wenn du magst* (Upgrade, „Das bekommst du extra: ..."). [A, nach Wirecutter-Schema]
2. **Note und Preis getrennt halten**: Die Note misst nur Leistung für deine Nutzung (wie Which?); „Preis-Leistung" ist ein eigenes Kennzeichen. Das löst unseren Eigenbefund (65 € mit 84 vor Sony 81): Note nach Gewichtung der Nutzung bilden, nicht nur Datenblatt-Häkchen zählen, und Preis-Leistung als zweite Achse. [A]
3. **Pflichtblöcke je Karte**: „Passt zu dir, weil ..." (an deine Antworten gebunden), „Passt weniger, wenn ..." (für wen nicht), „Schwächen, die nicht schlimm sind" und „Schwäche, die zählt" (zwei getrennte Zeilen), „Wie sicher ist die Empfehlung?" [A, nach Wirecutter]
4. **Unsicherheit zeigen**: Drei Stufen der Quelle („aus Test", „aus Datenblatt", „geschätzt") als Symbol an der Note; bei Datenblatt-Note der Satz „Nicht selbst getestet; Werte vom Hersteller." Wenn die Spitze knapp ist (Abstand unter 3 Punkte), sagen: „Gleichauf mit Modell Y; Unterschied: ...". [A; gestützt auf Which?/Warentest-Praxis, Gewichte dort nicht vollständig belegt]
5. **Warum nicht die anderen?** Einklappbar „Beliebt, aber nicht empfohlen: ..." mit Grund (nach Wirecutter-Abschnitt Wettbewerb). [A]

Textskizze Ergebnis:
```
Für dich: Pendeln, iPhone, 6 h täglich
┌ UNSERE WAHL ────────────────────┐
│ Sony WH-CH720N   ★ 82 · aus Test│
│ Passt, weil: leichte 192 g, ... │
│ Passt weniger, wenn: ...        │
│ Schwäche, die zählt: Mikro      │
│ ab 99 € · 4 Shops    [Preise ▾] │
└─────────────────────────────────┘
Günstiger: ... (-35 €, du verzichtest auf ...)
Besser:    ... (+120 €, dafür ...)
[ Antworten ändern ]  [ Alle 24 Modelle ]
```

---

## 3. Notentransparenz

**Befund**
- Which? zeigt die Gewichtung offen: TV-Gesamtnote besteht zu 45 % aus Bild, 25 % Ton, je 10 % Bedienung und Smart-Funktionen, je 5 % Anschlüsse und Betriebskosten; die Note wird als Prozent plus Sterne gezeigt, ohne Preis; Kriterien werden jährlich überprüft. [Q] https://www.which.co.uk/reviews/televisions/article/how-we-test-televisions
- RTINGS bewertet je Nutzung (Usage) mit eigenen Gewichten nur aus den relevanten Tests; Testbank-Versionen ändern Gewichte, dokumentiert in Changelogs (z. B. Soundstage von 21 auf 20 %). [Q] https://www.rtings.com/company/scoring-system-overhaul (Snippet) und https://www.rtings.com/headphones/tests/changelog/1-3 und Folge-Changelogs (Ausschnitte aus der Suche; Detailseiten ohne Login nicht lesbar)
- Stiftung Warentest: Teilurteile je Prüfgruppe (Ton, Geräuschreduzierung, Tragekomfort/Handhabung, Akku, Haltbarkeit, Schadstoffe) ergeben das Qualitätsurteil; Prozentgewichte im frei zugänglichen Teil nicht gefunden. [Q] https://www.test.de/Bluetooth-Kopfhoerer-Test-4378783-4378789/
- Progressive Disclosure: wichtigstes zuerst, Spezielles auf zweiter Ebene auf Verlangen; höchstens zwei Ebenen; Auslöser klar beschriften. [Q] https://www.nngroup.com/articles/progressive-disclosure/
- Rechtlich relevant bei Ranglisten: § 5b Abs. 2 UWG verlangt bei Suchfunktionen über Angebote mehrerer Anbieter die Hauptparameter des Rankings und deren Gewichtung, leicht erreichbar von der Ergebnisanzeige. [Q] https://www.gesetze-im-internet.de/uwg_2004/__5b.html (ob unsere App als „Suche" darunter fällt, ist **[A] offen, juristisch klären lassen**; als Transparenzmuster sinnvoll)

**Muster für uns** (drei Ebenen, nicht mehr)
1. **Ebene 1 an der Karte**: Note + Satz „Gute Pendel-Kopfhörer: 82 von 100" + Quellenzeichen.
2. **Ebene 2, ein Tipp auf die Note („Wie entsteht die 82?")**: Bottom-Sheet mit 4 bis 5 Balken, je Teilnote in Alltagssprache („Klang 85 · Geräuschdämpfung 78 · Tragekomfort 90 ..."), daneben das Gewicht für DEINE Nutzung („zählt hier 40 %"). Satz: „Bei Sport zählt Halt mehr, dann wäre die Note 74." [A, nach Which?-Gewichtsdarstellung und RTINGS-Usage-Idee]
3. **Ebene 3, „Messwerte und Quellen"**: je Teilnote die Rohwerte, Quelle mit Datum und Art (Labortest / Datenblatt / eigene Schätzung), Link zur Methodikseite.
4. **Gewichte pro Nutzung festlegen und dokumentieren** (eine Tabelle je Kategorie in `daten/`) und sie auf der Methodikseite zeigen. Stand und Version der Gewichte am Ende des Sheets („Bewertungsstand: Gewichte v3, 11/2026"), wie Stiftung Warentest das Untersuchungsprogramm vermerkt. [A]
5. **Preis nie in die Note** (Which?-Praxis), aber **Deckel statt Häkchen**: Wenn ein Datenblatt-Wert nur „vorhanden/nicht vorhanden" ist, nicht gleich bewerten wie gemessener Wert; Datenblatt-Noten bekommen Abzug oder Spanne („78 bis 86"), damit ein Billigmodell nicht ein getestetes Spitzenmodell überholt. [A; direkt aus unserem Befund]

Textskizze Sheet:
```
Wie entsteht die 82?              (für: Pendeln)
Klang          ████████░  85   zählt 35 %
Geräuschdämpf. ███████░░  78   zählt 30 %
Tragekomfort   █████████  90   zählt 20 %
Akku           ██████░░░  70   zählt 15 %
Quelle: Labortest (rtings.com, 10/2026) ›
Bei „Sport" wäre die Note 74.  [ Nutzung ändern ]
```

---

## 4. „Was bekomme ich wirklich?"

**Befund**
- NN/g: Fachbegriffe in Kundensprache und mit Alltagsmetapher erklären (Beispiel Best Buy „Gehirn des Computers"). [Q] https://www.nngroup.com/articles/filter-categories-values/
- Vergleichstabellen: kurze Zellen, keine ganzen Sätze, gleiche Attributnamen. [Q] https://www.nngroup.com/articles/comparison-tables/
- Spezifische Studien zu Simulationen/Vorher-nachher bei Produktberatern habe ich nicht gefunden. Alles Weitere ist **[A]**.

**Muster für uns** [A]
1. **Messwert in Alltagssprache**: jede Zahl bekommt einen „Heißt für dich:"-Satz („Akku 30 h = etwa eine Woche Pendeln, einmal laden pro Woche"). Format fest in Daten: `wert`, `einheit`, `alltag`.
2. **„Ein Tag damit" als drei Szenen** je Kategorie (Morgen/Tag/Abend), nur aus belegten Werten; vorhanden im Ratgeber, soll in die Ergebniskarte als aufklappbare Zeile.
3. **Vergleichsbild/Simulation nur wo es ehrlich geht**: Fernseher (Bildschirmgröße im Zimmer, Abstand, matt/glänzend), Staubsauger (Lautstärke als Vergleich „wie Gespräch / wie Föhn"), Kopfhörer (Dämpfung in dB als „Bahn wird zu Zimmerlautstärke", nur mit Messwert). Keine erfundenen Simulationen; fehlt der Wert, kein Bild.
4. **„Was du bekommst / was dir fehlt" gegenüber dem Vergleichsgerät** (bereits im Ratgeber „Was sich ändert"): in die Karten „Günstiger/Besser" übernehmen, als zwei Listen mit Plus/Minus.
5. **Reue-Test als Vorabcheck**: „Das wird dich stören, wenn: ..." (bei Wirecutter „Flaws but not dealbreakers" entspricht der entschärfte Teil).

---

## 5. Preisvergleich

**Befund**
- Typische Portale zeigen je Händler Preis, Versandkosten und Lieferzeit als eigene Angaben; Verlauf meist 90 Tage; Preiswecker aus dem Verlauf mit Wunschpreis. Die Preise stammen aus Händlerfeeds und können abweichen („zuletzt übermittelt, nicht garantiert"). [Q] https://www.giga.de/ratgeber/tipps/idealo-preisvergleich-mehr-sparen-mit-allen-funktionen-der-seite/ und https://www.monsterdealz.de/magazin/idealo-test (beide Ratgeber/Anzeige-Charakter, nicht offizielle idealo-Doku; Spaltenaufbau am Original prüfen)
- Recht: Gesamtpreis inkl. USt und aller Bestandteile, zusätzliche Liefer-/Versandkosten angeben oder darauf hinweisen. [Q] https://www.haendlerbund.de/de/wissen/preisangabenverordnung und https://www.gesetze-im-internet.de/uwg_2004/__5b.html; LG Hamburg: Versandkosten bei Preisvergleichslisten nicht nur per Mouseover. [Q] ebenfalls https://www.haendlerbund.de/de/wissen/preisangabenverordnung (Treffertext, Urteil selbst nicht geprüft)
- § 11 PAngV (30-Tage-Tiefstpreis) gilt für Händler, die eine eigene Preisermäßigung bekanntgeben; bei bloßen Preisvergleichen ohne Bezug auf eigene frühere Preise erwachsen daraus laut einer Kommentierung keine Pflichten. Für uns als Vergleichsseite wahrscheinlich nicht direkt einschlägig. [Q] https://www.gesetze-im-internet.de/pangv_2022/__11.html und https://www.it-recht-kanzlei.de/durchgestrichener-preis.html (Suchtreffer, nicht im Volltext geprüft)
- Zu Pflichten speziell für Preisvergleichsportale (Aktualitätshinweis, Stand-Angabe, Affiliate-Kennzeichnung) habe ich **keine** belastbare Quelle gefunden. Keine Rechtsberatung; vor dem Veröffentlichen prüfen lassen.

**Muster für uns**
1. **Angebotsliste statt Bestpreis**: Sheet „Preise" mit jeder Zeile: Shop, Preis (Gesamtpreis inkl. MwSt), Versand („+4,99 €" / „kostenlos" / „unbekannt"), Lieferbarkeit, „Stand: vor 3 Std." — sortiert nach Gesamtpreis inkl. Versand, billigster markiert. Versand sichtbar in der Zeile, nie nur Tooltip. [A, gestützt auf rechtliche Quellen]
2. **Stand-Anzeige** je Preis und je Seite („Preise geprüft am 24.11.2026, 08:00; können sich ändern"); Preise älter als X Stunden werden grau und mit „veraltet" markiert, älter als Y nicht mehr als Angebot gezeigt. [A]
3. **Preisverlauf** als kleine Linie (30/90 Tage) mit „Jetzt: 79 €, Tiefstpreis 72 € (03.11.)"; nur zeigen, wenn wir genug Messpunkte haben, sonst ehrlich „noch zu wenig Daten". [A]
4. **Preiswecker** nur lokal (Wunschpreis in `localStorage`, bleibt Besitzerfunktion laut AGENTS.md), bis Push belegt ist (D4). Für Nutzer: „Merken" und beim App-Öffnen „Preis gefallen" anzeigen. [A]
5. **„Zum Angebot"-Zeilen als Werbung/Provision kennzeichnen**, falls Affiliate-Links kommen; Rechtsprüfung offen. [A]

Textskizze:
```
Preise (Stand 24.11., 08:00)
Shop        Preis    Versand   Lieferung
Saturn      65,00 €  0,00 €    2 Tage     ★ günstigster
Amazon      67,90 €  0,00 €    morgen
Otto        64,00 €  +4,95 €   5 Tage
[ Preisverlauf 90 Tage ▸ ]  [ Preis merken ]
Preise ohne Gewähr; beim Shop gilt der dort angezeigte Preis.
```

---

## 6. Vergleichsansicht auf dem Handy

**Befund**
- Bis 5 Elemente, dynamisch meist 3 bis 4, mobil etwa 2 gleichzeitig; Zeilen wählbar/einklappbar; Spaltenköpfe fixiert; „Unterschiede hervorheben"/gleiche Zeilen ausblenden; Kurzfassung „auf einen Blick" mit Link zur ganzen Tabelle; Alternative: Spalten als Tabs. [Q] https://www.nngroup.com/articles/comparison-tables/
- Baymard: Merkmale nach Gruppen statt langer alphabetischer Liste, einheitliche Attributnamen, fixierte Kopfzeile mit Name/Bild/Preis, Zeilentrennung, „Nur Unterschiede zeigen" fanden Tester am hilfreichsten; die Auswahl der Vergleichsprodukte in der Liste und die Vergleichsseite sind laut Baymard schwer benutzbar. [Q] https://baymard.com/blog/user-friendly-comparison-tools und https://baymard.com/research-articles/provide-comparison-features
- Mobil-spezifische Baymard-Befunde sind kostenpflichtig, nicht gelesen.

**Muster für uns** [A, nach obigen Quellen]
1. **Standard 2 Modelle nebeneinander**, dritte per Wisch/Tab; Kopfzeile bleibt kleben (Bild, Name, Preis).
2. **Voreinstellung „Nur Unterschiede"**; Schalter „Alles zeigen".
3. **Gruppen als Akkordeon**: Klang, Komfort, Akku, Preise; erste Gruppe offen, jede Gruppe mit einem Satz „Gewinner: A, weil ...".
4. **Gewinner je Zeile markieren** (Haken, nicht nur Farbe), unten „Unterm Strich: A für Pendeln, B für Zuhause".
5. **Einstieg**: Auf jeder Karte ein Plus „Zum Vergleich" mit unterem Leiste „2 gewählt · Vergleichen".

Textskizze:
```
[Sony CH720N | Bose QC]  ← fixiert
Nur Unterschiede ●
▾ Klang       Gewinner: Bose
   Note        82 | 86 ✓
   ANC         gut | sehr gut ✓
▸ Komfort     Gewinner: Sony
Unterm Strich: Sony für Sport, Bose fürs Pendeln
```

---

## 7. Vertrauen

**Befund**
- Wirecutter: eigener Abschnitt „Warum du uns trauen kannst". [Q] Spiegelseite (siehe Abschnitt 2)
- Which? kauft fast alle Testprodukte selbst, nutzt dieselben Tests je Kategorie, ignoriert Preise in der Note; Kriterien jährlich überprüft. [Q] https://www.which.co.uk/about-which/testing-and-research/311/which-tests und TV-Seite oben
- Stiftung Warentest: anonymer Einkauf, keine Pressemuster oder Vorserien, Verfahren je Gerät vermerkt. [Q] https://www.test.de/Bluetooth-Kopfhoerer-Test-4378783-4378789/
- RTINGS nennt Finanzierung (Mitgliedschaften, Affiliate-Provisionen) offen. [Q] https://www.rtings.com/headphones/learn/how-we-test

**Muster für uns** [A]
1. **Eine Seite „So kommen die Noten zustande"** (aus jedem Sheet und aus dem Menü erreichbar): Wir testen nicht selbst, sondern bewerten Tests und Datenblätter; Quellenarten; Gewichte je Nutzung; keine Herstellerbezahlung; wie wir verdienen (falls Provision); Aktualisierungsdatum; Änderungslog der Gewichte.
2. **Unabhängigkeit ehrlich**: Nicht „getestet" behaupten, wenn nur Datenblatt. Sprache „aus Test" / „aus Datenblatt" / „geschätzt".
3. **Stand überall**: Preisstand, Notenstand, Datenbankversion im Fuß jeder Ergebnisseite.
4. **Fehler melden** („Stimmt etwas nicht?") als Mail/Link ohne Konto.

---

## Top 10 Änderungen (priorisiert)

| Nr | Änderung | Wirkung | Aufwand |
|---|---|---|---|
| 1 | **Note neu**: Leistung nach Nutzungsgewichten, Preis getrennt (Preis-Leistung als zweite Achse), Datenblatt-Noten mit Abzug/Spanne; löst Billig-vor-Sony-Fehler | Vertrauen, Kernmangel | mittel (bewertung.js, Daten) |
| 2 | **Preisliste mit allen Shops**: Preis, Versand, Lieferung, Stand, nach Gesamtpreis sortiert | Besitzerwunsch, Recht | mittel |
| 3 | **Sheet „Wie entsteht die Note?"** in 3 Ebenen mit Teilnoten und Gewichten | Besitzerwunsch | mittel |
| 4 | **Ergebnis mit 3 Picks** (Wahl / Günstiger / Besser) und Blöcken „Passt zu dir / Passt weniger / Schwäche, die zählt" | Führung, Ehrlichkeit | mittel |
| 5 | **Fragen: Nutzung zuerst, Budget zuletzt**, eine Frage je Bildschirm, Fortschritt, „Weiß nicht", Zurück, Überspringen | Führung | mittel |
| 6 | **Live-Vorschau** („Passt: 11 von 24, vorn: X") unter den Fragen | Führung, Satisficer | klein bis mittel |
| 7 | **Drei Einstiege** (schnell / alle vergleichen / ich kenne ein Modell) | Käufertypen | mittel |
| 8 | **Mobile Vergleichsansicht** mit fixierter Kopfzeile, „Nur Unterschiede", Gruppen, Gewinner je Zeile | Experten | mittel |
| 9 | **Methodik-Seite plus Stand-Angaben** (Preis, Note, Gewichteversion) und Quellenzeichen „aus Test / Datenblatt / geschätzt" | Vertrauen, Recht | klein |
| 10 | **„Heißt für dich"-Sätze** je Messwert und „Ein Tag damit" in der Karte; Modelle ausbauen (mehr Modelle je Kategorie, Daten nur mit Beleg) | „Was bekomme ich", Besitzerwunsch | groß, laufend |

Offene Punkte für Besitzer/Recht: (a) Fällt die App unter § 5b Abs. 2 UWG (Ranking-Transparenz)? (b) Pflichten bei Preisvergleichsangaben und Affiliate-Kennzeichnung klären. (c) Gewichtungen je Nutzung brauchen fachliche Freigabe und Beleg (Which?-Gewichte als Anschauung, nicht übernehmen).
