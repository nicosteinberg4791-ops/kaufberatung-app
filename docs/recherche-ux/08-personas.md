# 08 – Usability-Simulation mit acht Nutzertypen (Finder)

Stand 24.11.2026. Gegenstand: Finder der Kaufberatung-App (Startseite `app/finder/`, lokale Vorschau, Bildschirm 375 x 812, Android-Chrome-Emulation), Datenstand 22.11.2026 (14 Kategorien, 75 Fernseher, 40 Smartphones usw.).
Methode: Die Personas sind erfunden und wurden im eingebauten Browser durchgespielt (echte Klicks und Tipp-Eingaben; wo viele Antworten nötig waren, per Skript-Klick auf dieselben Schaltflächen). Zeiten sind Schätzungen aus Schrittzahl und Textmenge, keine Messungen an Menschen. Die Wirkung auf echte Menschen ist damit nicht belegt, es sind begründete Hypothesen, die ein Test mit 5 bis 8 realen Personen bestätigen sollte. Das Impeccable-Skill hat in diesem Checkout keine `SKILL.md` (nur `reference/` und `scripts/`); es gab daher keine Persona-Vorlage, die Personas stammen aus dem Auftrag.

Gemeinsamer Ausgangsbefund (gilt für alle): Der Finder kennt genau einen Einstieg, nämlich „Kategorie wählen“ (`finder.js:241-271`). Es gibt kein Suchfeld (`input[type=search]` fehlt, geprüft), keinen Problem-Einstieg, keine Erklärungen zu Fachbegriffen und keine Liste „beste Angebote“. Der Ablauf ist Kategorie → Budget → Fragen → Ergebnis (`finder.js:9`), das Budget kommt vor den Fragen (`finder.js:332`).

---

## 1. Eilige Pragmatikerin (35) – „guter Air Fryer für 4 Personen, nicht zu teuer“

**Weg:** Kachel „Air Fryer“ → Budget-Schnellwahl „bis 125 €“ → „Weiter zu den Fragen“ → eine Frage beantwortet („3 bis 4“), die drei anderen übersprungen → „Ergebnis zeigen“. **5 Taps, geschätzt 30 bis 45 Sekunden.**

**Ergebnis:** Empfehlung Tefal Dual Easy Fry AG901NS0, 84 von 100, „sehr gut“, 105,90 € bei Proshop, Knopf „Zum Angebot“. Für sie genau richtig: eine Antwort, ein Treffer.

**Zögern / Missverständnisse:**
- Das Budget kommt vor der Frage „für wie viele Personen“. „Nicht zu teuer“ ist für sie keine Zahl, sie rät „bis 125 €“ (Schnellwahl-Stufen kommen aus den Modellpreisen, `B.budgetStufen`).
- „Deine Angaben: 3 bis 4“ (`finder.js:450`) nennt die Einheit nicht, es steht nur der Antworttext ohne Frage.
- Die Notenleiste mit „45 · 60 · 75 · 85“ und „Ab 84 nur mit unabhängigem Test“ (`finder.js:471`) liest sie nicht; „aus Datenblatt“ sagt ihr nichts. Sie braucht es auch nicht, stört aber die Zeile, die sie sucht (Preis, Knopf).
- Die Karte sagt nicht, warum genau dieses Gerät („8,3 l, zwei Garräume, spülmaschinenfest“ sind Stärken, aber ohne Bezug zu „4 Personen“).

**Kauft sie?** Wahrscheinlich ja. Händler Proshop kennt sie vielleicht nicht, das Vertrauen kommt aus der Note „sehr gut“. Abbruchrisiko gering.

**Was fehlt:** Satz „Passt für 3 bis 4 Personen, weil …“; Preis und Knopf oberhalb der Notenskala; Budget als Frage in Alltagssprache („Eher günstig / mittel / egal“).

---

## 2. Unsicherer Einsteiger (68) – Fernseher fürs Wohnzimmer

**Weg:** „Fernseher“ → Budget-Seite mit Betragsfeld, vier Chips bis 2.700 € und „Welche Größe soll er haben?“ (nur in Zoll) → „Egal“ gelassen → „Weiter“ → vier Fragen, nichts beantwortet → „Ergebnis zeigen“. **4 Taps, aber die Seiten dauern wegen Lesen und Zögern (geschätzt 3 bis 5 Minuten).**

**Ergebnis ohne Angaben (Egal/Egal):** Empfehlung ist ein **LG OLED evo C6, 83 Zoll, „Preis unbekannt“**, ohne Angebotsknopf (`finder.js:476`). Darunter eine Liste mit **75 Modellen auf 8.139 px Seitenlänge**, viele mit „–“ statt Preis. Mit „bis 900 €“ wird die Empfehlung brauchbar (LG OLED B6, 55 Zoll, 874 €).

**Zögern / Missverständnisse:**
- „Zoll“ als Größenwahl: Sie weiß nicht, wie groß 55 oder 65 Zoll im Wohnzimmer wirken. Kein cm, kein Vergleich („passt auf Sideboard von 1,40 m“).
- Chips „bis 600 / 900 / 1.200 / 2.700 €“ schrecken ab (die höchste Stufe liegt weit über ihrem Rahmen); sie sieht keinen Bezug zu „was zahlen andere“.
- Begriffe: „Bildtechnik: OLED“, „Native Bildwiederholrate: 120 Hz“, „HDMI-Eingänge mit 4K/120 Hz (HDMI 2.1): 4 Stück“ (`finder.js:498`, Stärken) – ohne Erklärung. Auch die Fragen „Antenne, Kabel oder Satellit“ und „Sitzabstand“ sind lösbar, aber „eARC“ (Soundbar-Kategorie) und HDR wären es nicht.
- Kleine Schrift: Hilfetexte 14,4 px, Chips 14,1 px; sehr dunkle Oberfläche (Dunkelmodus Standard der Vorschau).
- Wenn sie alles auf „egal“ lässt, steht nur „Ohne Angaben zu deiner Nutzung bewertet“ – kein Hinweis, dass Antworten die Empfehlung deutlich verändern würden.

**Kauft sie?** Nein, nicht allein. Sie versteht nicht, warum ein 83-Zoll-Gerät ohne Preis „unsere Empfehlung“ ist, und würde das Gerät nicht als Treffer erkennen. Sie bricht beim Ergebnis ab oder ruft jemanden an.

**Was fehlt:** Erklär-Hilfen in einfachem Deutsch („OLED = sehr dunkles Schwarz, gut fürs abendliche Filmschauen“), Wohnraum-Frage statt Zoll („Wie weit sitzt du?“ an erster Stelle, daraus Größe ableiten), Empfehlungen nur mit Preis, Größenschrift-Option, ein Wort wie „Beratung“ statt „Finder“.

---

## 3. Technik-Enthusiast (28) – Sony WH-1000XM6 gegen Bose QC Ultra

**Weg:** Over-Ear → (Budget egal) → Fragen übersprungen → Ergebnis → in einer Liste von 17 Modellen beide suchen und „Vergleichen“ antippen → Vergleichstabelle. **8 bis 10 Taps, 2 Minuten.** Es gibt kein Suchfeld, er scrollt.

**Ergebnis:** Sony 80 „sehr gut“, 327 €; **Bose QuietComfort Ultra Headphones (2. Gen.): keine Note („–“), 8 von 9 Merkmalen „nicht angegeben“**. Nur „Aktive Geräuschunterdrückung: ja“ und „Kabelbetrieb: ja“ stehen auf beiden Seiten. Der Vergleich, den er wollte, ist leer (`finder.js:619-621`). Ganz oben stehen Marshall Monitor III (84, 189 €) und Soundcore Space One (84, 65 €) vor dem Sony (80).

**Zögern / Missverständnisse:**
- Er misstraut dem Ergebnis, weil die Note ohne Quelle dasteht. Der Fußzeilentext „Wie wir bewerten“ ist eingeklappt. „aus Datenblatt“ und „Ab 84 nur mit unabhängigem Test“ erklären nicht, was genau gewertet wurde.
- Testberichts-Links werden im Datenmodell geladen (`bewertung.js:433`), aber **nirgends angezeigt**. Teilpunkte (`teilpunkte`) werden ebenfalls nicht gezeigt.
- Er möchte „alle Messwerte“: Das Datenblatt liefert ANC ja/nein, Akku, Gewicht, Codecs; keine Messwerte (Frequenzgang, ANC-Dämpfung in dB). Das sagt die App nicht.
- Hinweis „Für 124 € weniger fast gleich gut (84 statt 84 Punkte)“ (Budget-Lauf bis 300 €) wirkt wie ein Rechenfehler.

**Kauft er?** Er kauft nicht anhand der App, nutzt sie als Vorauswahl und geht zu Rtings, Notebookcheck o. Ä. Die unbelegte Note ist für ihn ein Ausschlusskriterium.

**Was fehlt:** Suche/Modellname, eine Quellenzeile je Note (Datenblatt / Test + Link), sichtbare Testberichts-Links, ein Vergleich, der zwei Modelle direkt aus der Liste wählt (auch ohne Fragen), ehrliche Lückenkennzeichnung („Bose: nur Datenblattteil unvollständig, Wert fehlt“) statt „nicht angegeben“ ohne Hilfe.

---

## 4. Schnäppchenjäger (40) – „das Beste bis 300 €“

**Weg:** Er hat keine Kategorie, nur eine Zahl. Er rät „Kopfhörer Over-Ear“ → Budget „300“ eingetippt (Ziffern wirken sofort, Adresse ändert sich) → Weiter → Ergebnis. **5 Taps und eine Eingabe, 1 bis 2 Minuten.** Bei „Das Beste bis 300 € im Haushalt“ gibt es keinen Einstieg.

**Ergebnis:** Empfehlung Marshall Monitor III A.N.C., 84 von 100, 189 €, bei Saturn, Stand 21.11.2026. Darunter die Karte „Für 124 € weniger fast gleich gut (84 statt 84 Punkte)“: Soundcore Space One, 65 €. Sortierung „Günstigste“ ist vorhanden. Das passt zu ihm.

**Zögern / Missverständnisse:**
- „Wo am günstigsten?“: Jedes Modell hat **einen** Händler (hier Saturn), **ein** Datum, keinen Preisvergleich und keine Preisverlauf-Aussage. „Ist der Preis gerade gut?“ bleibt unbeantwortet.
- Ohne Preis gelistete Modelle („–“) sind für ihn unbrauchbar; viele davon stehen im Ergebnis oder hinter „Auch teurere und ohne Preis zeigen (n)“ (`finder.js:585`).
- „Stand 21.11.2026“ ist 3 Tage alt; er will wissen, ob das noch gilt.

**Kauft er?** Er klickt „Zum Angebot“, vergleicht dann aber in einem Preisportal. Die App hilft bei der Vorauswahl, nicht beim Abschluss.

**Was fehlt:** Bestenliste je Preisrahmen als Einstieg („Das Beste bis 300 €“, kategorieübergreifend), Preis-Einordnung („günstiger als …“, Mindestpreis der letzten 30 Tage) nur mit Belegquelle, Mehrere Händler je Modell, Hinweis „Preis kann sich ändern“.

---

## 5. „Ich hab schon ein Modell im Kopf“ (30) – Samsung Galaxy S26

**Weg:** Smartphones → Budget egal → Fragen (iPhone/Android: „Android“) → Ergebnis → 40 Modelle durchsuchen. **Mindestens 5 Taps plus Scrollen über ca. 25 Zeilen.** Es gibt keine Suche und keine Sprungmarke.

**Ergebnis:** Die Empfehlung ist ein Google Pixel 10 Pro 512 GB. Die Galaxy-S26-Varianten stehen auf Platz 25/27 (S26 256 GB, S26 512 GB), 70 Punkte, **ohne Preis („–“)**. Jede Speichergröße ist eine eigene Zeile (S26, S26+, S26 Ultra, S26 FE je 128/256/512 GB), also tauchen sechs bis zehn Galaxy-Zeilen verteilt in der Liste auf.

**Zögern / Missverständnisse:**
- Er wird erst einmal gefragt, wozu er das Handy nutzt, obwohl er schon eins gewählt hat; die Fragen wirken wie Umweg.
- „Passt es?“ kann nur über „Vergleichen“ (max. drei) beantwortet werden; dafür muss er das Modell zuerst finden. Dass die Empfehlung ein anderes Handy ist, deutet er als Kritik an seiner Wahl oder als Werbung.
- Er sieht „70 gut“ für S26 und „73 gut“ für S26 FE, versteht aber nicht, was „gut“ bedeutet, wenn die Empfehlung ebenfalls nur „gut“ ist.

**Kauft er?** Er steigt aus oder sucht außerhalb der App weiter, weil sein Modell ohne Preis und ohne Angebotsknopf dasteht.

**Was fehlt:** Suchfeld „Modell suchen“ auf der Startseite mit Direktsprung zur Modellkarte und Funktion „Das ist besser als dein Modell“ (nur belegte Alternativen), Gruppierung der Speichervarianten, Eintrag mit Hinweis, wenn kein Preis vorliegt.

---

## 6. Familienvater mit Problem statt Produkt (45) – Hundehaare, 90 m², Allergie

**Weg:** Startseite: „Haushalt: Akku-Staubsauger / Saugroboter“ – er weiß nicht, welches. Er probiert „Akku-Staubsauger“ → Budget egal → fünf Fragen (50 bis 90 m², viel Teppich, langhaarige Tiere, Allergie „Ja“; Treppen unbeantwortet) → Ergebnis. **7 Taps, 2 bis 3 Minuten.** Wechsel auf „Saugroboter“ nötig, wenn er beide vergleichen will; dann nochmal alles.

**Ergebnis:** Dyson V16 Piston Animal, 73 „gut“, „Preis unbekannt“, kein Angebotsknopf. „Deine Angaben: 50 bis 90 m², viel Teppich, langhaarige Tiere, **Ja**“ (`finder.js:450`): Das „Ja“ ist ohne Frage unverständlich. Die Stärken nennen „Saugleistung 315 AW“, „Laufzeit 70 min“, „Bürste gegen Haarwicklung“, aber **nicht**, was für Allergie zählt (Filterklasse, HEPA), obwohl er das angab. 22 Modelle in der Liste, 2 ausgeblendet.

**Zögern / Missverständnisse:**
- Die Startseite bietet keinen Satz wie „Ich weiß nicht, ob Akkusauger oder Roboter“. Die Kategorien sind Produkttypen, sein Problem ist ein Alltagsproblem.
- Das Wort „Allergie“ erscheint als Frage („Hausstauballergie?“), aber die Antwort wird im Ergebnis nicht ausdrücklich verwertet.
- Das Ergebnis sagt nicht, ob ein Roboter bei Hundehaaren besser wäre.

**Kauft er?** Eher nein: Er hat keine Entscheidungshilfe zwischen den Gerätearten und der Dyson hat keinen Preis.

**Was fehlt:** Problem-Einstieg („Haare, Teppich, Allergie – was brauche ich?“) mit Empfehlung der Geräteart („Für 90 m² und viele Haare: Akkusauger + ggf. Roboter für täglich“), Beleg warum („HEPA H13 wegen Allergie“), „Deine Angaben“ im Klartext („Allergie: ja“).

---

## 7. Ersatzkäuferin (55) – Waschmaschine kaputt, 60-cm-Nische, schnell

**Weg:** Waschmaschinen → Budget egal → Fragen (Personen „1 bis 2“, Aufstellort „Bad, Küche oder Flur“) → Ergebnis. **6 Taps, 2 Minuten.** Sie muss danach prüfen, ob das Gerät in 60 cm Nische passt und wann es kommt.

**Ergebnis:** Empfehlung Miele WWG880 WCS, 72 „gut“, **977 €** bei Saturn. Hinweis darunter: „Für 698 € weniger etwas schwächer (69 statt 72 Punkte)“: Gorenje WMSG2PS8, 279 €. In der Liste hat Platz 2 (Hisense WF5S1045BW, 399 €) dieselbe Note 72. Ohne Budgetangabe empfiehlt die App also das teuerste von mehreren gleich guten Geräten.

**Zögern / Missverständnisse:**
- Modellname erscheint doppelt: „WWG880 WCS“ als Name und als Untertitel (`finder.js:504-505`). Für sie ist das reiner Typenschlüssel ohne Beschreibung („Frontlader, 8 kg“).
- **Keine Maße** (Breite/Tiefe/Höhe), **keine Liefer- oder Abholinfo**, **keine Lagerangabe**. Die Datenfelder enthalten Energie, Schleudern, Lautstärke, Kapazität, Garantie, aber nicht Breite/Tiefe. Zwei harte Entscheidungskriterien dieser Nutzerin fehlen komplett.
- Sie hat Zeitdruck („heute“), doch die App kennt keinen Lieferstatus.

**Kauft sie?** Nein. Sie kann nicht prüfen, ob das Gerät passt, und weiß nicht, wann es da ist. Sie ruft einen Händler an oder fährt in den Markt.

**Was fehlt:** Maßangabe als Filter („Nische 60 cm, Tiefe max. …“, nur mit Datenblattbeleg), Verfügbarkeit / Lieferzeit je Händler (nur wenn belegbar), „Dringend“-Weg mit Abholmarkt, bei gleichen Noten günstigste empfehlen.

---

## 8. Geschenkkäufer (25) – Kopfhörer für die Freundin bis 150 €

**Weg:** Startseite: „Kopfhörer In-Ear“ oder „Kopfhörer Over-Ear“? Er rät In-Ear → Budget „bis 150 €“ → Weiter → Fragen („Welches Handy hast du?“, „Wofür nutzt du …“) → Ergebnis. **5 Taps, 1 bis 2 Minuten.**

**Ergebnis:** Soundcore Liberty 5, 83 „sehr gut“, 65 € bei Saturn. Passend.

**Zögern / Missverständnisse:**
- Die Kategorienamen verraten nicht den Unterschied zwischen In-Ear und Over-Ear; keine Bilder, keine einzeilige Erklärung.
- Alle Fragen sind in der Du-Form über den Nutzer („Welches Handy hast du?“, „Wie lange hörst du am Stück?“). Er kennt das Handy der Freundin nicht; „verschiedene oder weiß nicht“ gibt es nur bei einer der Fragen und bei den anderen „Egal / weiß nicht“. Die Konsequenz („klappt mit iPhone und Android?“) wird nicht gesagt.
- Dem Ergebnis fehlt Geschenk-Praxis: Farben, Rückgabe, Verpackung, Marke (Wiedererkennung) und die Frage, ob die Funktionen ohne die passende App (Soundcore, Bose Music) nutzbar sind.
- Er wählt den Preis nur als Obergrenze; bei Geschenken ist die Untergrenze („nicht zu billig wirken“) ebenso wichtig.

**Kauft er?** Wahrscheinlich ja; bei 65 € und „sehr gut“ geringes Risiko. Er zögert wegen der Handyfrage und bräuchte „Funktioniert mit jedem Handy“.

**Was fehlt:** Geschenk-Einstieg („Ich suche ein Geschenk für …“), Fragen in der dritten Person oder als „Weiß ich nicht“-Weg, Kompatibilitätsaussage, Rückgabe-/Umtausch-Hinweis.

---

## Muster über alle Personas

1. **Einziger Einstieg „Kategorie“** (alle acht). Sechs der acht Personen kommen nicht von der Kategorie her: Problem (6), Modell (5), Preis (4), Geschenk (8), Zeitdruck (7), Wissensdurst (3). Ohne passenden Einstieg raten sie die Kategorie.
2. **Kein Suchfeld** (3, 5, 7). Wer ein Modell kennt, muss durch 17 bis 75 Zeilen scrollen.
3. **Ergebnis ohne Preis oder Angebot** (2, 5, 6, 7 teilweise): Die Empfehlung kann ein Modell ohne Preis sein (LG 83 Zoll, Dyson). Das widerspricht dem Ziel „kaufen können“.
4. **Fachbegriffe ohne Erklärung** (2, 6, 8): OLED, HDMI 2.1, „Native Bildwiederholrate“, „Filterklasse“, „Multipoint“. Es gibt keine Erklär-Funktion.
5. **Note ohne sichtbare Quelle** (3, 5, 2): „aus Datenblatt“, „Ab 84 nur mit unabhängigem Test“; Testlinks existieren im Datenmodell, werden aber nicht angezeigt. Keine Aussage, wo die Note herkommt, im Ergebnis selbst.
6. **Angaben-Zusammenfassung verwirrend** (1, 6, 7, 8): „Deine Angaben: 3 bis 4“, „…, Ja“. Es fehlt der Fragetext.
7. **Fehlende Entscheidungsdaten je Gruppe**: Maße und Lieferzeit (7), Händlervergleich und Preislage (4), Kompatibilität/Geschenkpraxis (8), Allergie-Beleg (6).
8. **Budget vor Fragen** (1, 2, 4): Fast alle raten die Zahl; die Fragen kämen besser zuerst und das Budget danach mit Orientierung („die meisten zahlen …“).
9. **Lange Listen** (2, 3, 5): 75 Fernseher, 8.139 px Scrolllänge, Speichervarianten als eigene Zeilen.
10. **Gleichstand der Noten** (7): bei gleichen Noten und ohne Budget die teuerste Empfehlung.

### Tabelle Persona × Hürde

| Hürde | 1 Pragm. | 2 Einsteiger | 3 Enthusiast | 4 Schnäppch. | 5 Modell | 6 Problem | 7 Ersatz | 8 Geschenk |
|---|---|---|---|---|---|---|---|---|
| Nur Kategorie als Einstieg | leicht | mittel | mittel | hoch | hoch | hoch | mittel | hoch |
| Kein Suchfeld | – | – | hoch | – | hoch | – | mittel | – |
| Empfehlung ohne Preis/Angebot | – | hoch | – | mittel | hoch | hoch | – | – |
| Fachbegriffe unerklärt | leicht | hoch | leicht | – | mittel | hoch | – | mittel |
| Note ohne Quelle sichtbar | leicht | mittel | hoch | mittel | mittel | – | – | – |
| „Deine Angaben“ unklar | leicht | – | – | – | – | hoch | mittel | mittel |
| Fehlt: Maße/Lieferzeit | – | mittel | – | – | – | – | hoch | – |
| Fehlt: Preisvergleich/Preislage | – | – | – | hoch | mittel | – | – | – |
| Lange Liste / Varianten | – | mittel | mittel | – | hoch | – | – | – |
| Gleichstand → teuerste Empfehlung | – | – | – | mittel | – | – | hoch | – |
| Geschenk-/Fremdperspektive fehlt | – | – | – | – | – | – | – | hoch |

(leicht = stört kaum, mittel = bremst, hoch = führt zu Abbruch oder Kaufunsicherheit; Einschätzung aus der Simulation.)

---

## Vorschläge

Reihenfolge nach Wirkung (Zahl der abgeholten Personas) und Aufwand. Alle Vorschläge verlangen belegte Daten (Projektregel „Nichts erfinden“), keine neuen Aussagen ohne Quelle.

| Nr. | Vorschlag | Hilft | Aufwand | Kern |
|---|---|---|---|---|
| A | **Startseite mit vier Einstiegen** in einfacher Sprache: „Ich suche …“ (Kategorie, wie bisher), „Ich kenne ein Modell“ (Suchfeld), „Ich habe ein Problem / Geschenk“ (geführte Kurzfragen), „Bestenliste ansehen“ | 3, 4, 5, 6, 8 | mittel | Statt eines Einstiegs vier; Kategorien bleiben für 1 und 2 |
| B | **Modell suchen** (Suchfeld oben auf der Startseite, filtert alle Modelle namentlich, springt auf Modellkarte mit „Vergleichen“ und „Was ist besser?“) | 3, 5, 7 | gering bis mittel | Nur Daten, die schon in `finder-daten.json` stehen |
| C | **Problem beschreiben** (Auswahl von 6 bis 8 Alltagsproblemen: „Haare auf Teppich“, „Allergie“, „Geschirr trocknet nicht“ → leitet auf Kategorie plus Vorauswahl der Antworten, bei Staubsauger mit Satz zu Akku vs. Roboter) | 6 | mittel | Statische Zuordnung, redaktionell belegt |
| D | **Bestenliste je Preis** („Das Beste bis 150 / 300 / 500 € in …“): Kachel pro Kategorie und Preisstufe, Top 3 mit Preis und Angebot | 4, 8, 1 | gering (Daten und Sortierung vorhanden) | Nutzt `budgetStufen` und Sortierung |
| E | **Erklär-Hilfen**: kleines „Was heißt das?“ neben jedem Fachbegriff (ein bis zwei Sätze, belegt); Begriffe zuerst bei Fernseher, Kopfhörer, Saugroboter | 2, 6, 8 | mittel | Textliste im Datenmodell, nicht in jedem Gerät neu |
| F | **Ergebnisdarstellung**: Preis und Knopf oben, erst danach Note; Skala unter eine Zeile „So kommt die Note zustande“ einklappen; Quelle sichtbar („aus Datenblatt / aus Test von …“ mit Link); „Deine Angaben“ mit Fragetext („Haustiere: langhaarig“) | 1, 2, 3, 6 | gering bis mittel | `finder.js:450, 506-516` |
| G | **Empfehlung ohne Preis vermeiden**: bevorzugt Modelle mit Preis empfehlen; sonst klar „Aktuell nicht lieferbar/ohne Preis, nächste Empfehlung: …“; bei Gleichstand der Noten günstigsten empfehlen | 2, 5, 6, 7 | gering (Regel in `bewertung.js`) | Rechenregel statt Oberfläche |
| H | **Fragen-Reihenfolge**: Erst „Wofür?“, dann Budget mit Orientierungsstufen; Frage „für wen?“ als Wahlmöglichkeit am Anfang („für mich / als Geschenk“) | 1, 4, 8 | gering | `SCHRITTE` anpassen |
| I | **Spezialdaten gezielt, wo belegbar**: Maße (Waschmaschine, Geschirrspüler, Kühlschrank, Soundbar-Breite ist schon Frage), Liefer- bzw. Abholhinweis nur mit Quelle | 7 | hoch (Datenbeschaffung) | Nur mit Beleg |
| J | **Lesbarkeit**: Schriftgröße-Schalter, hellere Kontraste, größere Tippflächen (Hilfetexte aktuell 14,4 px) | 2 | gering | `finder.css` |

**Empfohlene erste Runde (hilft den meisten, wenig Risiko):** G (Empfehlung ohne Preis vermeiden, Gleichstand), F (Ergebnisdarstellung, Quelle, Angaben mit Fragetext), B (Modell suchen), D (Bestenliste je Preis). Danach A als neue Startseite, die B und D als Einstiege trägt, dann C und E. I nur nach Datenlage.

**Nicht geprüft:** Verhalten mit Screenreader, Hellmodus, Tablet/Desktop, Offline-Betrieb, echte Lesezeiten und Fehlbedienungen realer Personen.
