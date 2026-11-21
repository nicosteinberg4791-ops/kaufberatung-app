# Punkteschema aus Datenblattwerten

Stand: 21.11.2026 · Entwurf für die Kaufberatung-App · maschinenlesbar in `daten/schema/kategorien.json`

## 1. Worum es geht

Die App soll aus Kategorie, wenigen Fragen und einem Preisrahmen die passenden Modelle zeigen. Getestete Modelle tragen „getestet“, alle anderen bekommen Punkte nur aus belegten Datenblattwerten und tragen „aus Datenblatt“. Dieses Dokument legt fest, welche Datenblattfelder zählen, wie sie in Teilpunkte (0–100) umgerechnet werden, wie Fragen die Gewichte verschieben, wie Datenblatt-Noten abgeschlagen werden und wann die App „Für X € mehr …“ oder „Für X € weniger …“ zeigt.

**Ehrlich vorweg:** Die Schwellen der Kurven und die Gewichte sind **begründete Vorschläge, keine Messwerte**. Belegt sind (a) welche Werte auf den EU-Energielabels stehen und (b) wie Stiftung Warentest ihre Prüfbereiche gewichtet (Quellen in Abschnitt 9). Die Zahlenbereiche der Kurven beruhen auf üblichen Marktspannen und müssen vor dem Einsatz mit echten Datenblattwerten (EPREL-Auszüge, Pilotdaten in `daten/pilot_modelle.json`) kalibriert werden.

## 2. Was aus der bestehenden App übernommen wird

Gezielt in `quelle/kaufberatung.html` nachgesehen (Fernseher-Bericht, Staubsauger-Einstieg):

| Bestehendes Muster | Übernahme |
|---|---|
| Kriterien mit Gewicht, Summe 100; `Note = Σ(Gewicht × Punkte) ÷ Σ Gewichte` | identisch |
| Spanne je Kriterium (unten/oben), Gesamtspanne als Worst/Best Case | als `spanne_plus_minus` für Datenblatt-Noten |
| „Unter ~3 Punkten Abstand gibt es keinen echten Unterschied“ | globale `unterschiedsschwelle_punkte: 3`, Grundlage für Aufpreis- und Spar-Hinweis |
| Einstieg Staubsauger: Fläche, Teppich, Tiere, Etagen, Budget verschieben Gewichte | gleiche Fragen; statt additiver Verschiebung (`"laufzeit": -4`) jetzt Faktoren mit anschließender Normierung auf 100, damit es für alle Kategorien gleich funktioniert |
| Budget als `limit` je Antwort | Budget ist eine globale Eingabe, nicht Teil der Kategoriefragen |
| Größe zählt beim Fernseher nicht in den Punkten, sondern über den Sitzabstand | Diagonale ist Filterfeld (Gewicht 0) mit Mindestwert aus der Abstandsfrage |
| Kennzeichnung geschätzter Werte (`[E]`, „Erfahrungswert, nicht gemessen“) | Kennzeichnung „aus Datenblatt“ plus Abdeckungsanteil |
| Mehrwert je 1.000 € gegenüber Vergleichsgerät | Punkte je 100 € Aufpreis (Abschnitt 7) |

## 3. Rechenregeln

1. **Teilpunkte je Feld** über die Kurve:
   - `linear`: Stützpunkte `[wert, teilpunkte]`, dazwischen linear, außerhalb begrenzt auf den ersten/letzten Stützpunkt.
   - `stufen`: feste Zuordnung (z. B. Energieklasse A–G). Unbekannter Wert = Feld fehlt.
   - `ja_nein`: true/false.
2. **Gewichte nach Fragen:** Jede Antwort liefert Faktoren je Feld (`gewichte`). Faktoren mehrerer Antworten werden multipliziert, Faktor 0 schaltet ein Feld ab, danach wird auf Summe 100 normiert.
3. **Mindestanforderungen** (`mindest`, `hoechst`): Zahl = Grenzwert, `true` = muss vorhanden sein, Liste = erlaubte Stufen. Ist der Wert im Datenblatt nicht angegeben, bleibt das Modell in der Liste, trägt aber „Anforderung nicht belegt“. Passt nach allen Filtern nichts ins Budget, zeigt die App das beste Modell, das alle Anforderungen erfüllt, mit seinem Preis und dem Hinweis, dass es über dem Budget liegt.
4. **Filterfelder** (Gewicht 0: Diagonale, Bauart, Betriebssystem, Breite) zählen nie in die Note.
5. **Fehlende Felder** entfallen aus Zähler und Nenner; wie viel fehlt, steckt in der **Abdeckung** (Abschnitt 6).
6. **Nicht anwendbare Felder** (Sync-Funktion bei einem Korb) entfallen ohne Abdeckungsverlust.

## 4. Notenklassen (alle Kategorien gleich)

| Punkte | Klasse |
|---|---|
| ab 85 | hervorragend |
| ab 75 | sehr gut |
| ab 60 | gut |
| ab 45 | ordentlich |
| darunter | einfach |

Die App zeigt ganze Punkte und die Klasse. Der Notenabstand innerhalb einer Klasse unter 3 Punkten gilt als „gleich gut“.

## 5. Kategorien

Je Kategorie: die Felder mit Gewicht und Kurve in Kurzform (vollständig im JSON), die Begründung und die Fragen. Abkürzung „WT“ = Gewichtung der Stiftung Warentest für die Kategorie (Quelle in Abschnitt 9).

**Grundproblem aller Kategorien:** Die von WT am stärksten gewichteten Leistungen (Bild 45 %, Ton 50–70 %, Saugen 45 %, Waschen 40 %, Trocknen 45 %, Zubereitung 60 %) lassen sich **nicht** aus Datenblättern ablesen. Datenblatt-Punkte bewerten deshalb Ausstattung, Effizienz, Haltbarkeitsangaben und Bedienkomfort. Das ist der Hauptgrund für den Abschlag in Abschnitt 6.

**Kurven für EU-Klassen:** Für Haushaltsgeräte A 100 · B 90 · C 78 · D 64 · E 48 · F 30 · G 12; für Reparierbarkeit und Fallfestigkeit (A–E) A 100 · B 80 · C 60 · D 35 · E 10. Begründung: Seit der Neuskalierung (2021 für Waschmaschinen, Geschirrspüler, Kühlgeräte, Bildschirme; 07/2025 für Trockner) sind die oberen Klassen bewusst dünn besetzt; eine Stufe soll deshalb spürbar, aber nicht übermächtig zählen. Für Fernseher ist die Kurve flacher nach oben (A–B 100, C 95, D 85, E 70, F 50, G 30), weil viele Geräte im unteren Bereich liegen dürften. **Lücke:** Die tatsächliche Klassenverteilung je Kategorie ist hier nicht belegt; vor dem Einsatz per EPREL-Auszug prüfen und die Kurve so legen, dass der Marktmedian bei etwa 60–70 Teilpunkten liegt.

### 5.1 Fernseher
| Feld | Gewicht | Kurve (Kurzform) |
|---|---|---|
| Bildtechnik (OLED / Mini-LED / LCD mit Local Dimming / QLED / LCD) | 30 | 100 / 85 / 65 / 50 / 40 |
| Native Bildwiederholrate | 15 | 60 Hz 40 · 100–120 Hz 85 · 144 Hz 100 |
| HDR-Formate über HDR10 hinaus | 10 | nur HDR10 40 · eines 75 · beide 100 |
| Energieklasse SDR (EU-Label) | 10 | TV-Kurve, siehe oben |
| HDMI-Eingänge mit 4K/120 | 10 | 0 → 0 · 1 → 50 · 2 → 80 · 4 → 100 |
| Auflösung | 8 | Full HD 40 · 4K 100 |
| VRR | 5 | ja/nein |
| Lautsprecherleistung | 5 | 10 W 20 · 20 W 50 · 40 W 80 · 60 W 100 |
| eARC | 4 | ja/nein |
| Empfang Antenne/Kabel/Sat | 3 | ja 100 · nein 30 |
| Diagonale | 0 | Filter |

Begründung: Bild wiegt bei WT 45 %; aus dem Datenblatt ist dafür nur die Bildtechnik ein brauchbarer Stellvertreter (RTINGS bewertet Geräte ohne Local Dimming im Test „Lighting Zone Precision“ mit 0). Spitzenhelligkeit, Kontrast und Entspiegelung stehen selten verlässlich im Datenblatt und sind deshalb **nicht** enthalten. Lautsprecher-Watt ist ein schwacher Hinweis auf den Ton (WT 20 %), daher nur 5. Stromverbrauch WT 10 % ↔ Energieklasse 10.
Fragen: Wofür (Filme · Sport · Spiele · Alltag), Sitzabstand (Mindestdiagonale 32″ / 48″ / 55″ / 75″, abgeleitet aus dem in der App schon genutzten 30°-Sichtwinkel: Diagonale ≈ 0,615 × Abstand, auf die nächstkleinere übliche Größe abgerundet; das 30°-Maß ist laut bestehender App-Notiz „oft als SMPTE-Empfehlung zitiert“, ohne direkte SMPTE-Veröffentlichung), Soundbar vorhanden, Empfangsweg.

### 5.2 Akku-Staubsauger
Laufzeit kleinste Stufe 20 · Saugleistung AW 15 · Gewicht 15 · Wechselakku 10 · Behälter 8 · Filterklasse 8 · Anti-Haar-Bürste 8 · Geräusch 6 · Ladezeit 5 · Polsterdüse 5.
Begründung: WT gewichtet Saugen 45 %, Handhabung 30 %, Umwelt 15 %, Haltbarkeit 10 %. Saugleistung in Air-Watt ist **nicht genormt** und zwischen Marken kaum vergleichbar, daher nur 15 statt 45. Handhabung wird über Gewicht, Behälter, Bürste und Laufzeit abgebildet; Haltbarkeit über den Wechselakku.
Fragen (wie bestehender App-Einstieg): Wohnfläche (Mindestlaufzeit 25 / 35 / 50 min), Teppichanteil, Haustiere (lang: Anti-Haar-Bürste Pflicht), Treppen, Hausstauballergie (HEPA Pflicht).

### 5.3 Saugroboter
Navigation 18 · Saugleistung Pa 14 · Hinderniserkennung 12 · Wischsystem 12 · Absaugstation 10 · Laufzeit 8 · Schwellenhöhe 8 · Mopp-Anhebung 6 · Geräusch 6 · Bauhöhe 6.
Begründung: WT bewertet Saugen Hartboden/Teppich (40–55 %) und Wischen (bis 15 %) als Leistung, Praxistauglichkeit 10 % (darin Hindernisse, Reichweite), Handhabung 20 %, App-Datensendeverhalten 5 %. Das Datensendeverhalten steht in keinem Datenblatt → **Lücke**. Pascal-Angaben sind ebenfalls nicht genormt.
Fragen: Wischen ja/nein, Teppich, herumliegende Kabel/Spielzeug, Haustiere, Türschwellen (Mindesthöhe 20 mm).

### 5.4 Air Fryer
Fassungsvermögen 25 · spülmaschinenfest 15 · Garräume 10 · Leistung 10 · Sichtfenster 10 · Material Garfläche 10 · Sync-Funktion 10 · Höchsttemperatur 5 · Dörrfunktion 5.
Begründung: WT gewichtet die Zubereitung mit 60 % (Suchauszug, ältere Ausgabe); sie ist aus dem Datenblatt nicht ablesbar. Mehr Watt garantiert kein besseres Ergebnis, daher nur 10. Das Material zählt, weil manche Käufer PTFE meiden wollen; Beleg für einen gesundheitlichen Unterschied wird **nicht** behauptet.
Fragen: Personen (Mindestvolumen 3 / 5 / 7 l), zwei Dinge gleichzeitig (2 Garräume Pflicht), einfaches Putzen, ohne PTFE.

### 5.5 Smartphones
Akkuausdauer je Ladung (EU-Label) 15 · Update-Zusage 14 · Ladezyklen (EU-Label) 8 · Reparierbarkeit (EU-Label) 8 · Speicher 8 · IP-Schutz 7 · optischer Zoom 7 · Fallklasse (EU-Label) 6 · RAM 6 · Display-Hz 6 · Energieklasse 5 · Ladeleistung 4 · kabellos laden 3 · 5G 3.
Begründung: Seit 20.06.2025 trägt jedes neue Smartphone das EU-Label mit sechs Angaben (Energieklasse, Ausdauer je Ladung, Ladezyklen bis 80 %, Fallfestigkeit A–E, Reparierbarkeit A–E, IP-Schutz) – das ist die beste, einheitliche Datenblattquelle aller Kategorien. WT: Grundfunktionen 30 %, Kamera 20 %, Display 15 %, Akku 15 %, Handhabung 15 %, Stabilität 5 %. Kameraqualität ist nicht ablesbar (Megapixel bewusst **nicht** bewertet), nur der optische Zoom als Ausstattungsmerkmal. Rechenleistung (Benchmark) steht nicht im Datenblatt → **Lücke**.
Kurve Akkuausdauer (25 h → 20 … 70 h → 100) ist **vorläufig**; die übliche Spanne der Labelwerte ist hier nicht belegt und muss aus EPREL kalibriert werden.
Fragen: Nutzung (Basis · Fotos · Spiele · draußen), Behaltedauer (Mindest-Updates 4 / 6 Jahre), Speicherbedarf, Größe, iPhone oder Android.

### 5.6 Tablets
Akkuausdauer 18 · Update-Zusage 12 · Pixeldichte 12 · Speicher 10 · RAM 8 · Reparierbarkeit 6 · Stift 6 · Display-Hz 5 · Ladezyklen 5 · Energieklasse 4 · Mobilfunk 4 · Lautsprecher 4 · Fallklasse 3 · IP 3.
Begründung: Gleiches EU-Label wie Smartphones (Slate-Tablets). WT: Funktionen 30 %, Bildschirm 20 %, Akku 20 %, Handhabung 20 %, Vielseitigkeit 10 %.
Fragen: Wofür (Medien · Stift-Notizen · Arbeiten mit Tastatur · Kinder), Mobilfunk, Größe, Behaltedauer.

### 5.7 Laptops
Akku Wh 18 · RAM 14 · SSD 10 · Gewicht 10 · Helligkeit 8 · Displaytechnik 6 · Auflösung 6 · USB-C-Laden 5 · USB4/Thunderbolt 4 · WLAN 4 · Display-Hz 3 · HDMI 3 · Webcam 1080p 3 · Tastaturbeleuchtung 3 · RAM erweiterbar 3.
Begründung: WT: Funktionen 30 %, Bildschirm 20 %, Akku 20 %, Handhabung 20 %, Vielseitigkeit 10 %. Herstellerangaben zur Akkulaufzeit beruhen auf unterschiedlichen Verfahren; die Kapazität in Wh ist vergleichbarer, sagt aber ohne Verbrauch nichts Sicheres über die Laufzeit. CPU-/GPU-Leistung steht nicht als vergleichbarer Wert im Datenblatt → **Lücke** (eigene Grafikkarte nur als Filter für „Spiele“).
Fragen: Wofür (Office · unterwegs · Foto/Video · Spiele), oft mitnehmen (höchstens 1,6 kg), Bildschirmgröße, Betriebssystem.

### 5.8 Kopfhörer In-Ear und Over-Ear (zwei Kategorien)
Getrennt, weil Laufzeiten und Gewicht völlig andere Bereiche haben.
In-Ear: ANC 18 · Akku je Ladung 18 · Multipoint 10 · IP 10 · App-EQ 10 · Transparenzmodus 10 · Laufzeit mit Case 8 · Codecs 8 · kabellos laden 4 · Bluetooth-Version 4.
Over-Ear: ANC 20 · Akku 18 · Gewicht 14 · Multipoint 10 · App-EQ 10 · Kabelbetrieb 10 · Codecs 8 · faltbar 5 · Transparenzmodus 5.
Begründung: WT (Bluetooth, seit 06/2026): Ton 50 %, ANC 10 %, Akku 10 %, Tragekomfort/Handhabung 25 %, Haltbarkeit 5 %. Ton und Tragekomfort sind nicht ablesbar; ANC ist im Datenblatt nur „vorhanden ja/nein“, nicht seine Wirksamkeit. Codecs zählen wenig und beim iPhone gar nicht (Faktor 0), weil iPhones aptX/LDAC nicht nutzen.
Fragen: Wofür (Pendeln · Sport · Telefonate · Musik / Spielen), welches Handy, Hör- bzw. Tragedauer.

### 5.9 Soundbars
Kanäle 25 · Subwoofer 15 · Dolby Atmos 12 · eARC 12 · Raumanpassung 8 · WLAN-Streaming 8 · Sprachverstärkung 6 · nachrüstbar 6 · DTS:X 4 · Leistung 4 · Breite 0.
Begründung: WT: Ton 70 %, Handhabung 20 %, Stromverbrauch 10 %. Ton ist nicht ablesbar; Kanalzahl und Subwoofer sind die belastbarsten Stellvertreter. Watt-Angaben sind nicht vergleichbar, daher 4. Stromverbrauch steht selten einheitlich im Datenblatt → nicht bewertet (**Lücke**).
Fragen: Was soll besser werden (Sprache · Kino · Musik), Nachbarn, eARC am Fernseher, Höchstbreite.

### 5.10 Waschmaschinen
Energieklasse 20 · Wasserschutz 12 · Schleuderklasse 10 · Kapazität 10 · Dosierautomatik 10 · Wasser je kg 8 · Schleudergeräusch 8 · Garantie 8 · Dauer Eco 40-60 6 · Dampf/Allergie 4 · Startvorwahl 4.
Begründung: Das EU-Label (VO 2019/2014) liefert Energieklasse, kWh/100 Zyklen, Kapazität, Schleuderklasse, Programmdauer, Wasser je Zyklus und Geräusch beim Schleudern. WT: Waschen 40 %, Dauerprüfung 20 %, Handhabung 15 %, Umwelt 15 %, Schutz vor Wasserschäden 10 %. Waschleistung und Dauerhaltbarkeit sind nicht ablesbar; die Garantiedauer ist ein schwacher Stellvertreter für Haltbarkeit. Wasserschutz übernimmt WT-Gewicht fast 1:1.
Fragen: Personen (Mindestkapazität 6 / 7 / 9 kg), Aufstellort, Wasserschaden-Risiko (Vollschutz Pflicht), Besonderes (Allergie · Bequemlichkeit).

### 5.11 Trockner
Energieklasse 22 · Kondensationsklasse 10 · Geräusch 10 · Kapazität 10 · Restfeuchte-Sensor 10 · wartungsarmer Filter 8 · Reparierbarkeit 8 · Dauer Eco 6 · Abfluss-Anschluss 6 · Garantie 6 · Knitterschutz 4.
Begründung: Neues Label A–G seit 01.07.2025 (VO 2023/2534) mit Energieklasse, kWh/100 Zyklen, Kondensationsklasse, Geräusch, Kapazität, Eco-Dauer; Reparierbarkeitsklasse freiwillig ab 24.11.2025, Pflicht ab 01.01.2027 (VO 2025/1353). WT: Trocknen 45 %, Handhabung 30 %, Umwelt 20 %, Sicherheit/Verarbeitung 5 %. **Lücke:** Die Stufen der Kondensationsklasse auf dem neuen Label sind hier nicht nachgelesen; die Kurve deckt A–G ab und ist vor Einsatz zu prüfen.
Fragen: Personen, Aufstellort, Häufigkeit, Filterpflege.

### 5.12 Kühlschränke
Energieklasse 30 · NoFrost 12 · Geräusch 10 · Null-Grad-Zone 10 · Kühlinhalt 8 · Gefrierinhalt 6 · Türalarm 6 · Klimaklasse 6 · Garantie 6 · Türanschlag wechselbar 6.
Begründung: EU-Label (VO 2019/2016): Klasse, kWh/Jahr, Gefrier- und Kühlvolumen, Geräusch mit Klasse. WT: Energieeffizienz 30 % (übernommen), Handhabung 25 %, Kühlen/Einfrieren 25 %, Temperaturstabilität 10–15 %, Geräusch 5 %. Kühlleistung und Temperaturstabilität sind nicht ablesbar. Die Klimaklasse entscheidet, ob ein Gerät im kalten Keller oder in der Garage zuverlässig läuft.
Fragen: Personen (Mindest-Kühlinhalt 120 / 200 / 280 l, Vorschlag), Gefrierbedarf, Aufstellort (kalt: Klimaklasse mit SN Pflicht), Einbau.

### 5.13 Geschirrspüler
Energieklasse 18 · Geräusch 14 · Wasserschutz 12 · Besteckschublade 10 · automatische Türöffnung 10 · Maßgedecke 10 · Wasser 8 · Garantie 8 · Dauer Eco 6 · Startvorwahl 4.
Begründung: EU-Label (VO 2019/2017): Klasse, kWh/100 Zyklen, Maßgedecke, Eco-Dauer, Wasser je Zyklus, Geräusch. WT: Eco-, Automatik-, Kurzprogramm je 20 %, Handhabung 20 %, Sicherheit/Verarbeitung 10 %, Geräusch 10 %. Reinigung und Trocknung sind nicht ablesbar; die automatische Türöffnung ist ein Ausstattungshinweis für bessere Trocknung, kein Messwert.
Fragen: Personen, Breite (45/60 cm), Einbauart, offene Küche, nasses Plastik.

## 6. Abschlag für Datenblatt-Noten

**Vorschlag:**

```
R          = Rohwert aus Datenblattfeldern (0–100)
Abdeckung  = Anteil der (nach Fragen gewichteten) Gewichte mit belegtem Wert
N_db       = min(84, 50 + (R − 50) × 0,85 − 3 − (1 − Abdeckung) × 20)
Spanne     = N_db ± 8
Abdeckung < 0,7 → keine Note, Anzeige „zu wenig Daten“
```

Begründung:
1. **Schrumpfen zur Mitte (Faktor 0,85):** Datenblätter messen Ausstattung, nicht Leistung (Abschnitt 5). Extreme Rohwerte sind deshalb unsicherer als mittlere; ein Gerät mit voller Ausstattung kann im Test trotzdem schwach sein.
2. **Pauschalabzug 3 Punkte:** genau eine Unterschiedsschwelle der bestehenden App. Bei gleicher Rohnote steht ein getestetes Modell damit sichtbar vorn.
3. **Kappung bei 84:** Ohne unabhängigen Test kann kein Modell „hervorragend“ sein. Das schützt vor Datenblatt-Werbung.
4. **Abdeckungsabzug:** Jeder fehlende Datenblattwert kostet anteilig (bei 80 % Abdeckung 4 Punkte), damit lückenhafte Angaben sich nicht lohnen.
5. **Spanne ± 8:** etwas mehr als eine halbe Klassenbreite; macht sichtbar, dass die Note unsicher ist.

Beispiele: R 90, voll belegt → 81 („sehr gut“). R 95 → 85,25 → gekappt auf 84. R 70 → 64 („gut“). R 80 bei 80 % Abdeckung → 68,5.

**Getestete Modelle:** Note = 0,6 × Testpunkte + 0,4 × Rohwert R (mit Nutzergewichten), kein Abschlag, keine Kappung. So wirken die Fragen auch bei getesteten Modellen, der Test bleibt aber bestimmend. Umrechnung Warentest-Note (Skala 0,5 bis 5,5): `T = 100 − (Note − 0,5) × 20` (Note 1,5 → 80, 2,5 → 60). Für 0–10-Skalen (z. B. RTINGS): `T = Wert × 10`. Beides ist ein Vorschlag.

**Kalibrierung:** Sobald in einer Kategorie mindestens 15 Modelle Test- und Datenblattwert haben: Abzug = mittlere Abweichung (Test − Datenblatt), Spanne = 1,5 × Standardabweichung. Bis dahin gelten die Startwerte oben.

## 7. Aufpreis- und Spar-Hinweis

Bezug **A** = bestes Modell (höchste angezeigte Note) mit Preis ≤ Budget, das alle Mindestanforderungen erfüllt. Verglichen wird immer mit der angezeigten Note (also nach Abschlag).

**Aufpreis-Hinweis für Modell B**, wenn alle Bedingungen gelten:
- Preis_B ≤ Budget × 1,25 (höchstens 25 % über Budget)
- Aufpreis Δp = Preis_B − Preis_A ≥ 20 €
- Punktgewinn ΔN = N_B − N_A ≥ 3 (ist A oder B „aus Datenblatt“: ≥ 5)
- B erfüllt alle Mindestanforderungen
- **Effizienz E = ΔN ÷ Δp × 100 ≥ 3 Punkte je 100 €**, oder Klassensprung und E ≥ 1,5

Höchstens ein Hinweis: das B mit dem größten E, bei Gleichstand der kleinere Aufpreis.
Text: „Für {Δp} € mehr bekommst du +{ΔN} Punkte (Klasse „{B}“ statt „{A}“).“ Der Klammerteil nur bei Klassensprung.

**Spar-Hinweis für Modell C**:
- Ersparnis S = Preis_A − Preis_C ≥ max(30 €, 10 % von Preis_A)
- N_A − N_C ≤ 3 und gleiche Klasse → „Für {S} € weniger fast gleich gut ({N_C} statt {N_A} Punkte).“
- oder N_A − N_C ≤ 5 und S ≥ 25 % von Preis_A → „Für {S} € weniger etwas schwächer ({N_C} statt {N_A} Punkte).“
- C erfüllt alle Mindestanforderungen. Höchstens ein Hinweis, größte Ersparnis zuerst.

Begründung: Die Schwelle 3 Punkte ist die Unterschiedsschwelle der App; bei Datenblatt-Modellen 5, weil die Spanne größer ist. 3 Punkte je 100 € bedeutet: 100 € mehr müssen mindestens einen spürbaren Unterschied bringen. Die 25-%-Grenze hält den Hinweis im Rahmen dessen, was ein Budget-Käufer noch ernsthaft erwägt. Der Prozentanteil in den Spar- und Aufpreisregeln sorgt dafür, dass die Regeln für 100-€-Geräte (Air Fryer) und 1.500-€-Geräte (Fernseher) gleichermaßen funktionieren.

**Beispiele** (Fernseher, Budget 500 €):
- A: 489 €, 68 Punkte („gut“). B: 589 €, 77 („sehr gut“). Δp 100, ΔN 9, E 9, 589 ≤ 625 → „Für 100 € mehr bekommst du +9 Punkte (Klasse „sehr gut“ statt „gut“).“
- D: 649 €, 82 → über 625 €, kein Hinweis.
- E: 539 €, 70 → ΔN 2 < 3, kein Hinweis.
- C: 409 €, 66 → S 80 ≥ max(30; 48,90), Verlust 2, gleiche Klasse → „Für 80 € weniger fast gleich gut (66 statt 68 Punkte).“

Air Fryer, Budget 100 €: A 99 € mit 62, B 119 € mit 67 → Δp 20, ΔN 5, E 25, 119 ≤ 125 → Hinweis „Für 20 € mehr bekommst du +5 Punkte.“

## 8. Offene Punkte und Lücken

1. **Kurven kalibrieren:** Alle Schwellen sind Vorschläge. Vor dem Einsatz je Kategorie 20–50 echte Datenblätter (EPREL, Shops) auswerten; Ziel: Marktmedian bei 60–70 Teilpunkten, Spitzenmodelle bei 90–100.
2. **EU-Klassenverteilung** je Kategorie nicht belegt (beeinflusst die Klassenkurven).
3. **Smartphone/Tablet-Label:** übliche Spannen von Akkuausdauer und Ladezyklen nicht belegt.
4. **Trockner:** Stufen der Kondensationsklasse auf dem Label 2023/2534 nicht nachgelesen.
5. **Nicht ablesbar, aber in Tests wichtig:** Bild- und Tonqualität, Saug-, Wasch-, Spül-, Trocken- und Kühlleistung, Kameraqualität, Rechenleistung, ANC-Wirksamkeit, Tragekomfort, App-Datenschutz. Diese Lücke trägt der Abschlag; ein „hervorragend“ gibt es nur mit Test.
6. **Herstellerangaben ohne Norm:** Saugleistung (AW, Pa), Lautsprecher-Watt, Laufzeitangaben von Laptops und Saugern. Sie zählen deshalb nur mäßig.
7. **WT-Gewichte** sind von test.de (Abschnitt 9) abgelesen; die Air-Fryer-Angabe (60 % Zubereitung) stammt nur aus einem Suchauszug einer älteren Ausgabe. Die Grenzen der WT-Notenstufen (z. B. „gut“ bis 2,5) sind nicht nachgelesen; die Umrechnungsformel hängt nicht davon ab.
8. **RTINGS:** Die Methodikseiten ließen sich nicht direkt lesen (Fehler 404 bzw. leere Seite); verwendet ist nur der Hinweis aus dem Changelog zu Test Bench 2.0 (Geräte ohne Local Dimming erhalten 0 im Test „Lighting Zone Precision“), gelesen über Suchauszug.
9. **Mindestwerte aus Fragen** (Kühlinhalt je Person, Volumen je Person, Laufzeit je Fläche) sind Erfahrungsvorschläge ohne Quelle.
10. **Gewichte nicht unabhängig geprüft**; Fremdprüfung (Codex) vor Übernahme empfohlen.
11. **Tablet-Frage „Arbeiten mit Tastatur“** setzt ein Filterfeld `tastatur_anschluss` voraus, das in Datenblättern uneinheitlich angegeben ist.

## 9. Quellen (gelesen am 21.11.2026)

EU-Energielabel und Ökodesign (Europäische Kommission):
- Smartphones und Tablets, Label VO (EU) 2023/1669, Ökodesign 2023/1670, gilt seit 20.06.2025: https://energy-efficient-products.ec.europa.eu/product-list/smartphones-and-tablets_en
- Elektronische Displays, VO 2019/2013 und 2019/2021, seit 01.03.2021: https://energy-efficient-products.ec.europa.eu/product-list/electronic-displays_en
- Waschmaschinen, VO 2019/2014 und 2019/2023, seit 01.03.2021: https://energy-efficient-products.ec.europa.eu/product-list/washing-machines_en
- Wäschetrockner, VO 2023/2534 und 2023/2533, seit 01.07.2025; Reparierbarkeit VO 2025/1353: https://energy-efficient-products.ec.europa.eu/product-list/tumble-dryers_en
- Meldung zum Trockner-Label 01.07.2025: https://energy.ec.europa.eu/news/new-measures-more-energy-efficient-household-tumble-dryers-1-july-2025-07-01_en (nur Suchauszug)
- Kühl- und Gefriergeräte, VO 2019/2016 und 2019/2019, seit 01.03.2021: https://energy-efficient-products.ec.europa.eu/product-list/fridges-and-freezers_en
- Geschirrspüler, VO 2019/2017 und 2019/2022, seit 01.03.2021: https://energy-efficient-products.ec.europa.eu/product-list/dishwashers_en
- Übersicht Produktgruppen (Staubsauger: nur Ökodesign, kein Label): https://energy-efficient-products.ec.europa.eu/product-list_en

Stiftung Warentest, Abschnitte „So haben wir getestet“:
- Fernseher (Bild 45, Handhabung 25, Ton 20, Strom 10): https://www.test.de/Fernseher-im-Test-1629201-0/
- Staubsauger/Akku-Sauger (Saugen 45, Handhabung 30, Umwelt 15, Haltbarkeit 10): https://www.test.de/Staubsauger-im-Test-1838262-0/
- Saugroboter (Hartboden 30/40, Teppich 10/15, Wischen 15/0, Praxis 10, Handhabung 20, Umwelt 10, Daten 5): https://www.test.de/Saugroboter-im-Test-4806685-0/
- Heißluftfritteusen (Zubereitung 60 %, nur Suchauszug): https://www.test.de/Heissluftfritteusen-im-Test-5115675-5414916/
- Smartphones (Grundfunktionen 30, Kamera 20, Display 15, Akku 15, Handhabung 15, Stabilität 5): https://www.test.de/Handys-und-Smartphones-im-Test-4222793-0/
- Tablets (30/20/20/20/10): https://www.test.de/Tablets-im-Test-4627215-0/
- Laptops (30/20/20/20/10): https://www.test.de/Tablets-mit-Tastatur-Notebooks-Ultrabooks-Convertibles-im-Test-4734961-0/
- Bluetooth-Kopfhörer (Ton 50, ANC 10, Akku 10, Komfort/Handhabung 25, Haltbarkeit 5): https://www.test.de/Bluetooth-Kopfhoerer-Test-4378783-0/
- Soundbars (Ton 70, Handhabung 20, Strom 10): https://www.test.de/Test-Soundbars-und-Soundplates-4931024-0/
- Waschmaschinen (Waschen 40, Dauer 20, Handhabung 15, Umwelt 15, Wasserschutz 10): https://www.test.de/Waschmaschinen-im-Test-4296800-0/
- Wäschetrockner (Trocknen 45, Handhabung 30, Umwelt 20, Sicherheit 5): https://www.test.de/Waeschetrockner-im-Test-4735809-0/
- Kühlschränke (Energie 30, Handhabung 25, Kühlen/Einfrieren 25, Temperaturstabilität 10–15, Geräusch 5, Störungen 0–5): https://www.test.de/Kuehlschraenke-im-Test-4735177-0/
- Geschirrspüler (Eco/Automatik/Kurz je 20, Handhabung 20, Sicherheit 10, Geräusch 10): https://www.test.de/Geschirrspueler-im-Test-4685888-0/

RTINGS:
- TV Test Bench 2.0 Changelog (nur Suchauszug): https://www.rtings.com/tv/tests/changelogs/2-0

Bestehende App: `quelle/kaufberatung.html` (Fernseher-Bericht mit 13 Kriterien, Staubsauger-Einstieg), gezielt durchsucht am 21.11.2026.
