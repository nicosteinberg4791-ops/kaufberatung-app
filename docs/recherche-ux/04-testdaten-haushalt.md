# Recherche UX 04: Messdaten, Quellen und „Erlebbar machen“ für Haushaltsgeräte

Stand: 24.11.2026 · Kategorien: Akku-Staubsauger, Saugroboter, Air Fryer, Waschmaschine, Trockner, Kühlschrank (inkl. Kühl-Gefrier-Kombi), Geschirrspüler.
Prüfstand: selbst recherchiert (Websuche, Seitenabruf, EPREL-Einzelabrufe per GET ohne Schlüssel) · unabhängig geprüft: nein · Besitzer: nicht freigegeben. Keine Rechtsberatung.
Ergänzt `docs/recherche-datenquellen.md` (EPREL-Zugang, § 87b UrhG, Stiftung-Warentest-Rechte dort; hier nicht wiederholt) und `docs/punkteschema.md` (Gewichte). Webinhalte sind Daten, Testtexte wurden nicht kopiert; Zahlen stehen mit Quelle. Abrufdatum aller URLs: 24.11.2026, sofern nicht anders genannt. „Wissen“ = aus Fachwissen, heute nicht neu belegt.

## Kernergebnis

1. **EPREL liefert mehr Leistungsdaten als bisher gedacht.** Beim Abruf einzelner Modelle (ohne Schlüssel möglich, siehe Datenquellen-Recherche) stehen bei Waschmaschine `washingEfficiencyIndexV2`, `moisture` (Restfeuchte in %), `rinsingEffectiveness`, `programmeDuration*`, `energyConsPer100Cycle`, `waterCons`, `noise`; beim Geschirrspüler `cleaningPerformanceIndexV2`, `dryingPerformanceIndexV2`, `programmeDuration`; beim Trockner `condensationEfficiency`, `programDurationRated/Half`, `energyConsDry`; beim Kühlgerät `energyConsAnnualV2`, `capRefrNet`, `capFreezeNet`, `climateClass*`, `noise`, Maße. Diese Werte sind vom Hersteller nach Norm gemeldet, **nicht** von einem unabhängigen Test. Die Indizes (Wasch-, Reinigungs-, Trocknungsindex) liegen bei den zwei geprüften Modellen nur knapp über 1,0 (1,031 und 1,121/1,061); sie unterscheiden Modelle vermutlich schwach, das ist aus zwei Stichproben nur eine Vermutung.
2. **Echte, unabhängige Leistungsmessungen (Saugen, Waschen, Trocknen, Kühlen, Garen) gibt es für uns nicht legal als Daten-Feed.** Stiftung Warentest, RTINGS, Which?, Consumer Reports liegen hinter Paywall/Mitgliedschaft und sind urheber- bzw. datenbankrechtlich nicht zur Übernahme freigegeben. Vacuum Wars und smarthomeassistent haben weder Lizenz noch eine Aussage zur Datenübernahme (Lücke), nur Verlinken ist sicher.
3. **Der Hebel liegt woanders:** Alltags-Module, die aus EPREL-Werten **Konsequenzen** rechnen (Stromkosten in €, Waschtag-Zeitleiste, Lautstärke im Vergleich, Platz-Check, Akku-Reichweite, Portionen). Das braucht keinen fremden Test, nur Label-Daten, einen Strompreis (BDEW, 37,3 ct/kWh) und ehrliche Beschriftung „aus Herstellerangaben“.
4. **Bewertungsmodell:** Datenblatt-Note bleibt, Leistung wird als **getrennte, klar gekennzeichnete Ebene** ergänzt (eigene Messung mit Quelle · Testurteil verlinkt · nichts bekannt). Ein „hervorragend“ in Leistung gibt es nur mit Messbeleg.

## Herkunft der „Direkten Teppichmessungen“ im Akkusauger-Ratgeber

- Quelle ist **smarthomeassistent.de**: Der Ratgeber (`dist/ratgeber.html`, Suche „Teppich“, „Quellen“) nennt „Teppich/Hartboden aus smarthomeassistent-Messwerten“ (z. B. Teppich 63 ≈ 66, 75–77 ≈ 72–74, 82 ≈ 76; Laminat ≥ 99 ≈ 80–82) und Laufzeit „aus gemessenen Auto-/Standardminuten“. Einzelwerte, jeweils mit Produktlink in den Quellen (z. B. Bosch BKS1051POW: Teppich 64,78 gegen Shark Stratos 80,03).
- Der Ratgeber warnt selbst: „nicht mit RTINGS oder Stiftung Warentest vergleichbar; Einheit laut Quelle unklar“. Teppichmessungen sind also **Einzelbelege mit Quelle, kein einheitlicher Maßstab**. Das ist die ehrliche Messlatte für alles, was wir übernehmen.
- Methodik von smarthomeassistent bei Saugrobotern (nur aus dem Artikel, nicht für Akkusauger): Haaraufnahme 0,5 g kurz + 0,5 g lang, max. 10 Punkte; vier Teppiche; 16 Hindernisse mit Punktwerten (Quelle: https://www.smarthomeassistent.de/neue-saugroboter-tests-wir-entwickeln-uns-weiter/). Eine Methodikseite für Akkusauger wurde **nicht gefunden** (Lücke).

## Gemeinsame Bausteine (für alle Kategorien)

- **Strompreis:** BDEW-Strompreisanalyse Herbst 2026 (28.10.2026): Durchschnitt Haushalte 2026 bisher **37,3 ct/kWh**, Steuern/Abgaben/Umlagen 12,6 ct/kWh (https://www.bdew.de/service/daten-und-grafiken/bdew-strompreisanalyse/). Die August-Ausgabe nannte 37,0 ct/kWh (über Suchauszug). Basis laut Suchauszug: 3.500 kWh Jahresverbrauch. Die BDEW-Seite warnt vor steigenden Neukundentarifen seit 1.10.2026, daher **Eingabefeld für den eigenen Preis** mit Voreinstellung 37 ct und Vermerk „Stand BDEW 10/2026“. Datenbankrecht: eine einzelne Zahl als Fakt mit Quelle, geringes Risiko.
- **Lautstärke-Vergleich:** Flüstern etwa 30 dB(A), ruhiges Zimmer am Tag in derselben Reihe (Umweltbundesamt-Diagramm laut Suchauszug, https://www.umweltbundesamt.de/themen/laerm/verbraucherservice-laerm/grundlagen-der-akustik); Kühlschrankbrummen etwa 40 dB(A) (Schweizer Infotafel; Sengpiel nennt 50 dB, Werte schwanken). Pegel addieren sich logarithmisch (UBA-Beispiel: 50 dB + 50 dB = 53 dB). **Lücke:** eine amtliche Einordnungstabelle mit Alltagsgeräuschen wurde nicht gelesen; vor Einsatz eine Tabelle mit Quelle (UBA oder BZgA) festlegen. EU-Label-dB sind Schallleistung, keine Raumlautstärke; das muss im Text stehen („so laut ist das Gerät an der Quelle“).
- **Label-Lesart:** Alle EU-Labelwerte sind Normwerte mit Normbeladung, nicht Alltag. Jede Modulzeile trägt „laut EU-Label/Herstellerangabe“.

## 1. Akku-Staubsauger

### 1.1 Was zählt wirklich
- **Stiftung Warentest** (Gewichte aus `punkteschema.md`: Saugen 45, Handhabung 30, Umwelt 15, Haltbarkeit 10): Saugprüfung auf automatisierter Prüfeinrichtung, Düse über den Boden gezogen, Staubbehälter teilbeladen bis 60 % des maximalen Unterdrucks; Hauptbodendüse mit Elektrobürste; Linsen-Reis-Gemisch und Prüfstaub auf Teppich und Hartboden; Ecken, Kanten, Ritzen; Tierhaar in den Teppich eingearbeitet, Zeit bis zur Entfernung; 75 Stunden Belastungstest über Teppich mit Stolperstelle (Suchauszug aus https://www.test.de/Staubsauger-im-Test-1838262-0/). Laufzeit: **nicht belegt gefunden**.
- **RTINGS** (Suchauszug): Haftung je Oberfläche mit drei Schmutzarten (Tierhaar, feiner Schmutz, grober Schmutz), Teppich: je 5 g Sand und Backpulver, 1 g Tierhaar, Schmutz in die Fasern eingearbeitet; in der „House“-Wertung zählt die Laufzeit mit 35 % am meisten (https://www.rtings.com/vacuum/learn/how-we-test; Seite selbst blieb mir beim Abruf leer, Mitgliedschaftssperre). Unterschied zu uns: RTINGS bewertet US-Modelle, deutsche Modelle teils nicht gelistet (nicht geprüft).
- **Consumer Reports** (Suchauszug): Geräusch mit Dezibelmesser auf Ohrhöhe bei Maximalstufe (https://www.consumerreports.org/vacuum-cleaners/how-consumer-reports-tests-vacuums).
- **Ärgernisse im Alltag (aus den Ratgeber-Quellen und Testbeschreibungen, keine neue Erhebung):** Haare wickeln sich um die Bürste, Teppich „gut, nicht perfekt“, Krümel bleiben, Hochflor schwierig, Laufzeit in Turbo nur ~10–11 min.
### 1.2 Messbare Größen
Staubaufnahme Teppich und Hartboden in % (Einheit je Quelle verschieden!), Ritzen/Ecken in %, Haar-Entfernung/Haar-Verheddern, gemessene Laufzeit je Stufe (Auto, Turbo), Schallpegel dB(A), Ladezeit, Gewicht. Aus dem Label: **kein** EU-Energielabel (siehe 5).
### 1.3 Quellen
Siehe Quellentabelle: smarthomeassistent (Einzelmessungen, Ampel gelb), Vacuum Wars (rot, nur verlinken), RTINGS (rot), WT (rot, nur verlinken), Hersteller-Datenblatt (grün für Fakten).
### 1.4 Module „Erlebbar machen“
1. **„Reicht der Akku für deine Wohnung?“** Eingabe m², Teppichanteil, Etagen. Rechnung: Reinigungsleistung ca. m²/min je Stufe × Laufzeit (Auto/Turbo, je Akku). Datenbedarf: Laufzeit je Stufe (Datenblatt, wo vorhanden `rechner` im Ratgeber), **Arbeitsbreite oder Fläche je Minute: nicht belegt, Annahme sichtbar machen** und mit Nutzereingabe „Wie lange saugst du?“ statt Fläche rechnen, damit nichts erfunden wird. Ratgeber hat die Mechanik schon (`rechner`: akkus, minNormal, minTurbo).
2. **Lautstärke-Streifen:** dB(A) des Geräts auf der gemeinsamen Vergleichsleiter (Flüstern, Kühlschrank, Gespräch). Daten: Herstellerangabe oder Messwert, mit Quelle.
3. **Gewicht und Handhabung:** „So schwer fühlt es sich an“ (Gewicht + Etagenzahl, Treppen). Datenblattgewicht, ehrlich ohne Wirkungsversprechen.
### 1.5 Bewertungsmodell
Datenblatt-Note wie bisher (Laufzeit, Gewicht, Behälter, Filter). Leistung nur als Ebene „Messbefund“ mit Quelle, wo vorhanden (Teppich in der Einheit der Quelle, kein Vergleich über Quellen). Saugleistung in AW/Pa **nicht** als Leistung werten (nicht genormt, `punkteschema.md` 5.2). Ehrlich: ohne Test keine Aussage „saugt besser“.

## 2. Saugroboter

### 2.1 Was zählt wirklich
- **Stiftung Warentest** (https://www.test.de/Saugroboter-im-Test-4806685-6071911/, paraphrasiert): Hartboden-Saugen 35 %, Teppich 20 %, Wischen 0 % bei reinen Saugrobotern, Praxis 10 % (enge Stellen, Schwellen, Geschwindigkeit, Akkureichweite, Kabel, lange Haare, Objekterkennung, Spot-Reinigung, No-Go-Zonen), Handhabung 20 %, Umwelt 10 % (Geräusch auf Teppich und Hartboden, Staub in der Luft, Jahresstrom für tägliche Reinigung von 20 m²), App-Datenübertragung 5 %. Abwertung bei Haar- oder Praxisproblemen. Das Datenverhalten kann die Gesamtnote um eine halbe Note senken.
- **smarthomeassistent** (s. o.): Haaraufnahme/Verheddern, Teppichnavigation (vier Teppiche), Hinderniserkennung (16 Alltagsobjekte, Verschieben kostet 50 % der Punkte), Wischleistung.
- **RTINGS Robot Vacuums** (Suchauszug): Restschmutz an Kanten und Ecken subjektiv bewertet.
- **Ärgernisse:** Verheddern von Kabeln und Socken, Festfahren auf Hochflor/Schwelle, Hundekot (Hinderniserkennung), App-Zwang und Datenversand, Mopp auf Teppich, Wartungsaufwand der Station.
### 2.2 Messbare Größen
Abdeckung (% der Fläche), Staub- und Haaraufnahme (% oder g), Hindernisse (n von 16), Schwellenhöhe (Datenblatt), Teppichnavigation (Punkte), Reichweite (m² je Ladung), dB(A). **Abdeckung/Reichweite je Wohnung nicht belegbar ohne eigene Messung.**
### 2.3 Quellen
Hersteller-Datenblatt (Schwelle, Höhe, Akku, Pa: Fakten, grün), smarthomeassistent und Vacuum Wars (gelb/rot, nur verlinken oder Einzelwert mit Quelle), WT (rot). EPREL hat **keine** Gruppe.
### 2.4 Module
1. **„Passt der Roboter unter dein Sofa?“** Eingabe Sofahöhe/Spalt, Schwellenhöhe: Vergleich mit `hoehe_cm` und `schwelle_mm` (Datenblatt). Daten schon im Schema (`hoehe_cm`, `schwelle_mm`).
2. **Haustier- und Kabel-Check:** Fragen (Haustier, Kabel, Hochflor) → Hinweis „braucht Hinderniserkennung“ mit Feld `hinderniserkennung` (Datenblatt) und Link zum Messbefund (smarthomeassistent, falls vorhanden). Ohne Messbefund: „Hersteller sagt X, nicht unabhängig gemessen“.
3. **Wartungsaufwand-Zeitleiste:** „Station leert nach X Tagen, Mopp alle Y“ aus Datenblatt (Absaugstation, Beutelvolumen). Datenlage: nicht belegt für viele Modelle; Feld nur zeigen, wenn belegt.
### 2.5 Bewertungsmodell
Wie 1.5, zusätzlich: Datenschutz/App-Verhalten **nicht bewerten** (kein Datenblattwert), nur Hinweis „Test prüft das; Ergebnis dort“. Teppichnavigation/Hindernisse nur als Messbefund mit Quelle.

## 3. Air Fryer

### 3.1 Was zählt wirklich
- **Stiftung Warentest** (https://www.test.de/Heissluftfritteusen-im-Test-5115675-5414916/): Zubereitung 60 %, Handhabung 30 %, Sicherheit und Umwelt je 5 %. Geprüft: Pommes (kleine und große Portion je nach Korbvolumen), Hähnchenkeulen, Gemüse, Brötchen, Muffins. Gleichmäßigkeit: Genauigkeit der eingestellten Temperatur, Temperaturkonstanz, Verteilung im Garraum. Strom beim Garen und im Standby, Modellrechnung mit festem Monatsprofil und 700 Stunden Standby. Geräusch von drei Experten subjektiv. Ergebnis der Pressemeldung 1/2025: 20 Geräte; Pommes im Airfryer etwa dreimal schneller gar als im Backofen (Suchauszug, https://www.test.de/presse/pressemitteilungen/Dreimal-schneller-als-ein-Backofen-Mit-Heissluftfritteusen-Fett-Strom-und-Zeit-sparen-6185203-0/). Jüngere Berichte sprechen von 42 Geräten; Widerspruch, daher keine Zahl übernehmen.
- **Ärgernisse:** schlechtes Reinigen (Beschichtung), Rauch/Geruch, ungleich garende Ecken, Lautstärke, Platzbedarf auf der Arbeitsplatte, Korb zu klein für Familie.
### 3.2 Messbare Größen
Garzeit Pommes (Min), Gleichmäßigkeit (Bräunung), Strom je Portion (kWh), Aufheizzeit, Geräusch, Korbvolumen (l) und nutzbare Portionen. **Nur Korbvolumen und Watt sind aus dem Datenblatt belegbar.**
### 3.3 Quellen
Hersteller-Datenblatt (Volumen, Watt, Temperatur, Maße), smarthomeassistent (im Ratgeber genutzt für Modelle, Messwerte in dieser Recherche nicht geprüft), WT/Which? (nur verlinken).
### 3.4 Module
1. **Portionen für X Personen:** Korbvolumen (l) → Portionen (z. B. Pommes), Zwei-Korb-Modelle getrennt. **Umrechnung l → g Pommes ist nicht belegt**; WT skaliert Portionen nach Volumen, nennt die Gramm aber im abgerufenen Text nicht. Nutzbar: „Reicht für X Personen“ nur als Mindestvolumen-Regel aus `punkteschema.md` (3/5/7 l), klar als Faustregel.
2. **Strom je Gericht in €:** Leistung (W) × Annahme Garzeit (Nutzer wählt 15 oder 25 min) × Strompreis. Rechenbeispiel (Annahme, nicht gemessen): 1,5 kW × 0,25 h = 0,375 kWh × 0,373 €/kWh ≈ 0,14 € (Wert der Rechnung; Garzeit ist die Annahme). Vergleich zum Backofen nur, wenn Backofenleistung mit Quelle (Lücke).
3. **Platz-Check:** Maße (B × T × H) gegen Stellfläche und Steckdose; Datenblatt.
### 3.5 Bewertungsmodell
Datenblattnote (Volumen, Spülmaschine, Körbe) bleibt; Hinweis, dass die WT-Hauptdisziplin (Zubereitung, 60 %) nicht ablesbar ist, ein Garergebnis wird nicht benotet. Optional Ebene „Messbefund“ nur mit verlinktem Test.

## 4. Waschmaschine

### 4.1 Was zählt wirklich
- **Stiftung Warentest** (https://www.test.de/Waschmaschinen-im-Test-4296800-0/): Waschen 40 % (Eco 40–60 bei Teillast, Buntwäsche 40/60 °C, Pflegeleicht, Kurzprogramm, 2 kg; Verschmutzungsstreifen; Sauberkeit, Spülen, Schleudern, Faserschonung seit 2024 über gelockerte Fäden), Programmdauer, Dauerprüfung 20 % (3 Geräte, 1.200 Zyklen), Handhabung 15 %, Umwelt 15 % (Wasser, Strom, Standby, Geräusch Hauptwaschen und Schleudern), Wasserschutz 10 %. Restfeuchte nicht ausdrücklich beschrieben.
- **Which?** (Suchauszug): 280 Prüfungen je Maschine, kauft alle Geräte selbst (https://www.which.co.uk/reviews/washing-machines/article/how-we-test-washing-machines). UK-Modelle, deutsche Modellnamen weichen ab.
- **Ärgernisse:** Eco-Programm dauert 3–4 Stunden, Wäsche bleibt nass (Restfeuchte → Trocknerlast), Geräusch beim Schleudern, Fremdgeruch/Schimmel an der Dichtung, Wasserschaden.
### 4.2 Messbare Größen (EPREL-Abruf einer Electrolux EW6SM426BE, Reg.-Nr. 2036995, https://eprel.ec.europa.eu/api/products/washingmachines2019/2036995)
Energie je Zyklus (`energyConsPerCycle` 0,484 kWh; `energyConsPer100Cycle` 48), Wasser (`waterCons` 40 l), Geräusch (`noise` 74 dB, Klasse B), Programmdauer Eco 40-60 (`programmeDurationRated` 197 min bei Nennlast, `programmeDurationHalf` 155, `programmeDurationQuarter` 145), **Restfeuchte** (`moisture` 53,5 % bei Nenn-Schleuderdrehzahl 1151), Schleuderklasse, **Waschwirkungsindex** (`washingEfficiencyIndexV2` 1,031), Spülwirkung (`rinsingEffectiveness` 4,9 g/kg), Kapazität (`ratedCapacity` 6 kg), Maße, Garantie (`guaranteeDuration`). Hinweis: Das Beispiel ist eine einzelne Probe; die Feldnamen sind belegt, die Wertebereiche über alle Modelle nicht.
### 4.3 Quellen
EPREL einzeln per Reg.-Nr. (grün, Lizenz siehe Datenquellen-Recherche), WT/Which? nur verlinken.
### 4.4 Module
1. **Waschtag-Zeitleiste:** „Eco 40-60 bei Vollast dauert 3:17 h (197 min), bei halber Last 2:35 h (155 min), Viertel 2:25 h (145 min).“ Datenbedarf: `programmeDuration*` aus EPREL. Direkt aus dem Datensatz, keine Annahme.
2. **Stromkosten über 10 Jahre:** `energyConsPer100Cycle` ÷ 100 × Zyklen pro Jahr × 10 × Strompreis, plus Wasser (Preis je m³ **nicht belegt**; nur „Liter je Zyklus“ zeigen, ohne €). Beispiel EW6SM426BE: 0,484 kWh × 0,373 €/kWh ≈ 0,18 € je Zyklus; bei Nutzereingabe 4 Wäschen/Woche (208/Jahr, Annahme des Nutzers) ≈ 38 €/Jahr, ≈ 380 € in 10 Jahren (Rechnung, Strompreis konstant angenommen, Hinweis!).
3. **Restfeuchte → Trocknerlast:** `moisture` % × Beladung = Wasser, das der Trockner verdampfen muss (Kapazität 6 kg × 53,5 % ≈ 3,2 kg Wasser **nach Label-Norm, bezogen auf Trockenwäsche**; Rechnung nur sinnvoll, wenn die Normdefinition der Restfeuchte geprüft ist, Lücke). Nutzen: Vergleich zweier Maschinen („weniger Wasser im Trockner“).
4. **Lautstärke:** Schleuder-dB(A) auf der Vergleichsleiter; Hinweis für Küche/offenen Wohnraum.
### 4.5 Bewertungsmodell
Datenblatt/Label-Ebene: Energie, Wasser, Schleuderklasse, Restfeuchte (neu!), Dauer, Geräusch, Garantie. Waschwirkungsindex nur anzeigen, nicht stark gewichten (Norm-Mindestwert, geringe Streuung vermutet). Sauberkeit „hervorragend“ nur mit WT-Test (verlinken). Die Dauerprüfung (20 %) bleibt unbewertet; Garantie bleibt schwacher Ersatz.

## 5. Trockner

### 5.1 Was zählt wirklich
- **Stiftung Warentest** (https://www.test.de/Waeschetrockner-im-Test-4735809-0/): Trocknen 45 % (DIN EN 61121; Schranktrocken Eco Voll/Halb, Bügeltrocken, Pflegeleicht; Gleichmäßigkeit; Türöffnung bei Vollast; Dauer), Handhabung 30 % (Restzeitanzeige, Kondensatbehälter, Flusenfilter, Wärmepumpenfach), Umwelt 20 % (Modell 4 Personen, 1.000 kg Wäsche/Jahr, 10 Jahre Strom, Kältemittel, Schallleistung, Kondensationseffizienz), Sicherheit 5 %. Der abgerufene Test (2026) wählt ein Modell je Marke mit 8 kg.
- **Which?** (Suchauszug): Trockenheit durch Wiegen vor/nach; testet Eco-Programme **nicht** (https://www.which.co.uk/reviews/tumble-dryers/article/how-we-test-tumble-dryers).
- **Ärgernisse:** Dauer, Wäsche teils feucht oder übertrocknet (Knitter), Filterpflege, Kondensatbehälter leeren, Geräusch im Hauswirtschaftsraum, Abwärme.
### 5.2 Messbare Größen (EPREL Miele TSL683WP 125, Reg.-Nr. 2187097, https://eprel.ec.europa.eu/api/products/tumbledryers20232534/2187097)
`energyConsDry` 1,01 (kWh, Bedeutung der Bezugsmenge **nicht in dieser Recherche geprüft**), `programDurationRated` 184 min, `programDurationHalf` 108 min, `condensationEfficiency` 94 % und -klasse A, `noise` 62 dB (Klasse B), `ratedCapacity` 9 kg, Energieklasse C, Technologie, Kältemittel (`refrigerantName` R290), Maße, Garantie, Reparaturlinks. **Hinweis:** Das Modell hat Marktende-Datum in der Vergangenheit (`onMarketEndDateTS` 1774396800 = 24.03.2026, aus dem Zeitstempel umgerechnet), eine Stichprobe mit Auslaufmodell, EPREL-Filter nach Marktende ist nötig.
### 5.3 Quellen
EPREL (grün), WT/Which? (rot, verlinken).
### 5.4 Module
1. **Wäsche-Takt:** „Eco bei Volllast 3:04 h, bei halber Last 1:48 h“ (Datenfelder oben) → Zeitleiste „bis Wäsche im Schrank ist“. Direkt aus EPREL.
2. **Stromkosten pro Jahr und 10 Jahre:** Nutzer wählt Trockenvorgänge pro Woche; kWh je Zyklus aus `energyConsDry`, sobald die Bezugsmenge im Verordnungstext (VO 2023/2534) geprüft ist (**Lücke**, nicht erfinden). Alternativ aus Jahresverbrauch laut Label, falls EPREL ihn liefert (Feld nicht gefunden).
3. **Aufstellort-Check:** Geräusch (62 dB) und Kondensationsklasse (Raumklima), Abfluss-Anschluss; Fragen schon im Schema.
### 5.5 Bewertungsmodell
Label-Ebene (Klasse, Kondensationsklasse, Dauer, Geräusch). Trocknungsqualität nicht bewertbar ohne Test; **keine Note** dafür. `punkteschema.md` führt die Stufen der Kondensationsklasse als Lücke; EPREL liefert die Zahl `condensationEfficiency` (%) direkt, damit ist die Lücke schließbar.

## 6. Kühlschrank (inkl. Kühl-Gefrier-Kombi)

### 6.1 Was zählt wirklich
- **Stiftung Warentest** (https://www.test.de/Kuehlschraenke-im-Test-4735177-0/): Energie 30 %, Kühlen (12,5 % Kombis / 25 % Kühlschränke), Einfrieren 12,5 % (Kombis), Temperaturstabilität 10/15 % (23 °C und 35 °C; Klimakammer), Geräusch 5 % (Langzeitaufnahmen, Geräuschqualitätsindex), Handhabung 25 %, Störverhalten 5 % (Kombis: Aufwärmzeit bei Stromausfall, Alarm). Methode seit 02/2024 geändert (u. a. 23/35 °C statt 25/32 °C). **Alte und neue Testwerte sind nicht vergleichbar**: Beleg, dass Fremdnoten nicht mischbar sind.
- **Ärgernisse:** Brummen in der offenen Küche, Eisbildung ohne NoFrost, Gemüse trocknet aus, zu enge Nische (Maße), warme Ecken im Fach, Türanschlag.
### 6.2 Messbare Größen (EPREL LORD R12 2.GN, Reg.-Nr. 1874994, https://eprel.ec.europa.eu/api/products/refrigeratingappliances2019/1874994)
Jahresverbrauch (`energyConsAnnualV2`, kWh/Jahr), Nettovolumen Kühlen/Gefrieren (`capRefrNet`, `capFreezeNet`), Gesamtvolumen, Geräusch (`noise` dB, `noiseClass`), Klimaklassen (`climateClassST`, `climateClassN`), minimale/maximale Umgebungstemperatur (`minAmbientTemp`, `maxAmbientTemp`), Energieeffizienzindex, `fastFreeze`, `numberCompartments`, Maße, Einbauart (`designType`), Garantie. Das Beispiel ist ein Nischenmodell; typische Haushaltsgeräte nicht abgerufen.
### 6.3 Quellen
EPREL (grün), WT (rot, verlinken). `refrigeratingappliances2019` liegt unter derselben Gruppe wie Weinkühler; Filter auf `applianceType`.
### 6.4 Module
1. **Stromkosten über 10 Jahre in €:** `energyConsAnnualV2` × Strompreis × 10. Beispiel: 150 kWh/Jahr × 0,373 € × 10 ≈ 560 € (Rechenbeispiel, kein Modellwert); Vergleich zweier Geräte als Differenz („A spart in 10 Jahren X €“) mit Hinweis auf Preisschwankung.
2. **Platz-Check mit Maßen:** Nische (B/H/T) + Türschwenk + Lüftungsabstand (**Abstand je Modell Herstellerangabe, nicht in EPREL**; als Eingabe/Datenblatt, nicht erfinden).
3. **Lautstärke im Vergleich:** `noise` dB(A) auf der Leiter (Flüstern 30, Kühlschrank 40, …) mit Hinweis auf offene Küche/Schlafzimmer. Normwert gilt bei Prüfbedingungen.
4. **Aufstellort-Ampel:** Klimaklasse (`climateClass*`, `minAmbientTemp`) gegen Standort (Keller/Garage kalt). Beleg direkt im Datensatz.
### 6.5 Bewertungsmodell
Label-Ebene dominiert (Energie, Volumen, Geräusch, Klimaklasse). Kühlleistung/Temperaturstabilität **nicht benotet**; stattdessen Befund-Link auf WT. Besonderheit: WT-Methodikwechsel 02/2024 beachten, ältere Verlinkungen markieren.

## 7. Geschirrspüler

### 7.1 Was zählt wirklich
- **Stiftung Warentest** (https://www.test.de/Geschirrspueler-im-Test-4685888-0/): Eco, Automatik und Kurzprogramm je 20 % (Reinigung 30 min nach Programmende, Trocknung, Dauer, Strom, Wasser; Automatik reagiert auf Verschmutzung und Halblast), Handhabung 20 %, Sicherheit 10 %, Geräusch 10 % (Schallleistung im Labor), Standby 0 % seit 2026.
- **Which?** (Suchauszug): mehr als 25.000 verschmutzte Teile pro Jahr, Labor (https://www.which.co.uk/reviews/dishwashers/article/how-we-test-dishwashers).
- **Ärgernisse:** Eco dauert 3–4 Stunden, Plastik bleibt nass, Besteck nicht sauber, Geräusch (offene Küche), Salz/Klarspüler.
### 7.2 Messbare Größen (EPREL Bosch SMS6ECI12E, Reg.-Nr. 1940713, https://eprel.ec.europa.eu/api/products/dishwashers2019/1940713)
**`cleaningPerformanceIndexV2` 1,121, `dryingPerformanceIndexV2` 1,061** (Hersteller-Normwerte), `programmeDuration` 270 min (Eco), `energyCons100` 54 kWh/100 Zyklen, `waterCons` 9 l, `noise` 42 dB(A), `ratedCapacity` 14 Maßgedecke, Energieklasse, Geräuschklasse, Maße, Garantie.
### 7.3 Quellen
EPREL (grün), WT/Which? (verlinken).
### 7.4 Module
1. **Eco-Dauer-Zeitleiste:** „Startet 21:00, fertig 01:30 (270 min)“, Eingabe Startzeit/Zeitvorwahl. Direkt `programmeDuration`.
2. **Stromkosten und Wasser:** `energyCons100` ÷ 100 × Spülgänge/Jahr (Nutzer: 3–7 pro Woche) × 10 × Strompreis; Wasser nur in Litern (kein belegter Wasserpreis).
3. **Platz-Check:** Breite 45/60, Höhe (Einbaunische 82/87 cm als Faustregel: **Wissen, nicht neu belegt**), Tür-Schwenkraum.
4. **Lautstärke:** `noise` auf Leiter („42 dB(A): wie ein leiser Kühlschrank“, Vergleichswert aus UBA/BZgA-Tabelle vor Einsatz belegen).
### 7.5 Bewertungsmodell
Reinigungs-/Trocknungsindex anzeigen (neu, aus EPREL), aber nur schwach gewichten und mit Beschriftung „Herstellerangabe nach Norm“. Eine echte Leistungsnote (Eco/Automatik/Kurz) gibt es nur durch WT; ohne Test keine Note.

## Bewertungsmodell übergreifend (Punkt 5)

| Ebene | Inhalt | Quelle | Wird benotet? |
|---|---|---|---|
| A Label und Datenblatt | Energie, Wasser, Dauer, dB, Maße, Kapazität, Restfeuchte, Kondensation | EPREL, Hersteller | ja (wie heute, Punkte und Abschlag) |
| B Normindizes | Wasch-, Reinigungs-, Trocknungsindex | EPREL | anzeigen, schwach oder gar nicht gewichten |
| C Messbefund | Einzelmessungen (Teppich %, Haare, Hindernisse) | smarthomeassistent u. ä., nur Einzelwert mit Quelle und Einheit | nur als Zusatzzeile, nicht in Gesamtnote, solange Einheiten unvergleichbar |
| D Testurteil | Note anderer Tester | verlinken | nein, nur Link „Test bei test.de“ |
| E Alltagsmodule | Kosten, Zeit, Platz, Lautstärke | Rechnung aus A + Nutzereingabe | nein, Anschauung |

Grenzen, ehrlich: **Ohne bezahlte Tests geht keine echte Leistungsbewertung** (Waschen, Trocknen, Spülen, Kühlen, Garen, Saugen). WT-Gewichte 40–60 % für Leistung bleiben ungedeckt; der Abschlag im Schema (`datenblatt_abschlag`) trägt das weiter. Eigene Messungen im Labor wären das Einzige, was echte Leistungsdaten liefert, wären aber ein eigenes Projekt (Besitzerentscheidung, Kosten).

## Quellen-Tabelle

Ampel: grün = Fakten übernehmbar mit Quellenangabe, gelb = Einzelwerte mit Quelle möglich, Risiko prüfen, rot = nur verlinken.

| Quelle | URL | Abdeckung DE-Modelle | Lizenz / AGB (belegt?) | Paywall | Risiko § 87b / Urheber | Ampel |
|---|---|---|---|---|---|---|
| EPREL (öffentliche Webseite/API, Einzelabruf) | https://eprel.ec.europa.eu/api/products/&lt;Gruppe&gt;/&lt;Nr&gt; | Waschmaschine, Trockner, Kühl, Spüler vollständig (Pflichtregister); keine Sauger, kein Air Fryer | API-Bedingungen: Weiterverwendung in Vergleichs-Apps erlaubt, Aktualisierungspflicht, Quellenangabe (siehe Datenquellen-Recherche) | Liste nur mit Schlüssel (403), Einzelabruf ohne | gering | grün |
| BDEW Strompreisanalyse | https://www.bdew.de/service/daten-und-grafiken/bdew-strompreisanalyse/ | Strompreis (Zahl) | keine Lizenz geprüft; Einzelzahl mit Quellenangabe | nein | gering (Einzelfakt) | grün |
| Hersteller-Datenblätter | je Hersteller | Maße, Watt, Volumen, Laufzeit | Fakten nicht geschützt, Texte/Bilder schon (`recherche-datenquellen.md`) | nein | gering | grün |
| Umweltbundesamt (Lärm) | https://www.umweltbundesamt.de/themen/laerm/verbraucherservice-laerm/grundlagen-der-akustik | dB-Einordnung | Nutzungsbedingungen nicht geprüft | nein | gering (Einzelfakt) | gelb |
| smarthomeassistent.de | https://www.smarthomeassistent.de/ | Roboter, Akkusauger, Air Fryer | AGB/Impressum **nicht geprüft** (Lücke); Messwerte im Ratgeber als Einzelbelege mit Link | nein (in den abgerufenen Seiten) | mittel (Einzelwerte ja, Massenübernahme nein) | gelb |
| Vacuum Wars | https://vacuumwars.com/about/terms-of-use | US-Fokus, einzelne EU-Modelle (nicht geprüft) | Terms: Inhalte nur zur persönlichen Nutzung; Scraping/Daten nicht ausdrücklich geregelt | nein | mittel bis hoch | rot (nur verlinken) |
| RTINGS Vacuums | https://www.rtings.com/vacuum/learn/how-we-test | US-Modelle; DE-Abdeckung nicht geprüft | Mitgliedschaft für Volldaten; Terms-Text nicht lesbar (Lücke) | ja | hoch | rot |
| Stiftung Warentest | https://www.test.de/presse/rechtliches-5041757-0/ | sehr gut, aber nur getestete Modelle | Weiterverwendung nur mit Zustimmung/Lizenz (PMG) | teilweise ja | hoch | rot |
| Which? | https://www.which.co.uk/ | UK-Modelle, DE nur teilweise | Terms nicht geprüft | ja | hoch | rot |
| Consumer Reports | https://www.consumerreports.org/ | US | Terms nicht geprüft | ja | hoch | rot |
| K-Tipp, Konsument (CH/AT) | https://www.ktipp.ch/ , https://www.konsument.at/ | CH/AT-Märkte | Terms nicht gefunden (Lücke) | ja | hoch | rot |

## Offene Lücken (nicht erfunden)

1. Gramm-Pommes je Liter Korb, Garzeit-Daten Air Fryer: nicht belegt.
2. Bezugsmenge von `energyConsDry` (Trockner) und Jahreszyklen der Labelverordnungen (Wasch 220, Spüler 280, Trockner 160 laut Wissen, hier nicht neu belegt): vor Einsatz in Verordnungstext prüfen; Nutzereingabe als Zyklen/Woche vermeidet das Problem.
3. Wasser- und Abwasserpreis je m³: keine Quelle gelesen.
4. Typische Wertebereiche der EPREL-Indizes über alle Modelle: nur je ein Modell abgerufen.
5. smarthomeassistent: AGB, Methodik für Akkusauger, Einheit der Teppichwerte.
6. Lärm-Einordnungstabelle mit amtlichem Beleg.
7. Verifikation der Abdeckung deutscher Modelle bei RTINGS und Vacuum Wars; Lizenztexte von RTINGS, Which?, K-Tipp, Konsument, Consumer Reports.
8. EPREL-Liste benötigt Schlüssel (Besitzer, siehe Datenquellen-Recherche); Einzelabruf nur mit bekannter Registriernummer.
