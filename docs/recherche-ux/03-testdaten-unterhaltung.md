# Recherche 03: Testdaten und „erlebbarer Test“ (Fernseher, Soundbar, Kopfhörer, Smartphone, Tablet, Laptop)

Stand: 24.11.2026. Nur gelesen, nichts heruntergeladen oder installiert. Webinhalte sind Daten. Kennzeichnung: **[belegt]** = Quelle abgerufen 24.11.2026; **[Hinweis]** = nur Suchergebnis-Zusammenfassung oder Sekundärquelle; **[offen]** = nicht belegt, vor Nutzung klären. Keine Rechtsberatung.

## 0. Querschnitt

**Problem-Diagnose.** Das heutige Schema (docs/punkteschema.md) bewertet nur Datenblatt-Werte. Stiftung Warentest gewichtet laut eigenem Schema-Beleg bei Bluetooth-Kopfhörern Ton 50, ANC 10, Akku 10, Komfort/Handhabung 25, Haltbarkeit 5, bei Soundbars Ton 70, bei Fernsehern Bild 45 (Quellen in punkteschema.md Abschnitt 9, dort verlinkt). Ton und Bild, also die größten Blöcke, sind im Datenblatt nicht ablesbar. Darum kann ein 65-€-Gerät mit langer Ausstattungsliste vor einem Spitzenmodell landen. Das ist kein Rechenfehler, sondern eine Datenlücke.

**Rechtliche Leitplanke (§ 87b UrhG).** Der Datenbankhersteller hat das ausschließliche Recht an der ganzen Datenbank oder einem nach Art oder Umfang wesentlichen Teil; auch die systematische Nutzung unwesentlicher Teile ist erfasst, wenn sie der normalen Auswertung zuwiderläuft oder berechtigte Interessen unzumutbar beeinträchtigt (https://www.gesetze-im-internet.de/urhg/__87b.html, über Suchergebnis zusammengefasst, **[Hinweis]**; abgerufen 24.11.2026). Einzelne Messwerte als Fakt sind in der Regel kein wesentlicher Teil, ein systematisches Abgreifen einer ganzen Kategorie dagegen sehr wohl ein Risiko. Praktische Regel für die App: **je Modell wenige Fakten mit Quellenangabe und Link, nie ein Massenabzug fremder Tabellen, keine Kurven/Grafiken kopieren**.

**Offene Daten gibt es fast nur bei Kopfhörer-Frequenzgängen** (AutoEq, MIT). Für Fernseher, Smartphone und Laptop gibt es keine offen lizenzierte Messdatenbank. Dort bleibt: (a) Fakt mit Quelle und Link in kleinem Umfang, (b) Zusammenarbeit/Anfrage beim Anbieter, (c) eigene Berechnung aus öffentlichen Normwerten (EU-Label, EPREL), (d) nur verlinken.

**Geprüft und gescheitert (Transparenz):** RTINGS-Terms und -„How we test“ ließen sich nicht lesen (Login-Wand bzw. nur Navigation); DXOMARK-/SoundGuys-Terms-URLs lieferten 404. Aussagen dazu stützen sich auf Suchergebnisse und sind **[Hinweis]**.

---

## 1. Kopfhörer Over-Ear

### 1.1 Was zählt wirklich
- Stiftung Warentest: bis zu sechs Disziplinen (Klang, aktive Geräuschreduzierung, Tragekomfort/Handhabung, Akku, Haltbarkeit, Schadstoffe); Gewichte in punkteschema.md: Ton 50, ANC 10, Akku 10, Komfort 25, Haltbarkeit 5 (https://www.test.de/Bluetooth-Kopfhoerer-Test-4378783-0/, über Suchergebnis bestätigt: Disziplinen, ANC wirkt zuverlässig, belastet Akku **[Hinweis]**, Prozentwerte selbst hinter Paywall, also aus dem bestehenden Schema übernommen).
- RTINGS wechselt von einer Gesamtnote zu Einsatz-Noten (Usage Scores) mit eigenen Gewichten je Einsatz; Gewichte werden mit Test-Bench-Versionen geändert (https://www.rtings.com/company/scoring-system-overhaul und Test-Bench-Changelogs, **[Hinweis]**). Konkrete Gewichte nicht gefunden **[offen]**.
- Für Pendler/Büro faktisch: ANC-Wirkung im Tieffrequenzbereich (Bahn, Flugzeug, Büro-Brummen), Klangcharakter nah an einer akzeptierten Zielkurve, Komfort/Gewicht, echte Laufzeit, Mikrofon-Qualität für Telefonate.

### 1.2 Messbare Größen
| Dimension | Größe | Hinweis |
|---|---|---|
| ANC / Isolation | Dämpfung in dB in Bändern (z. B. Bass ≈ 100–500 Hz, Mitten, Höhen), plus Gesamt-„Bahn-Dämpfung“ | Messmethoden unterscheiden sich je Labor, nur innerhalb einer Quelle vergleichen |
| Klang | Abweichung des Frequenzgangs von Zielkurve (Harman), in dB RMS bzw. je Band (Bass/Mitten/Höhen ±dB) | Zielkurven sind in AutoEq als Zahlenwerte enthalten (https://github.com/jaakkopasanen/AutoEq, abgerufen 24.11.2026) |
| Akku | gemessene Laufzeit (ANC an, feste Lautstärke), Ladezeit | Herstellerwerte nur als Hilfe |
| Mikrofon | SNR/Verständlichkeit, Subjektiv-Note | selten frei verfügbar |
| Komfort | Gewicht (Datenblatt), Anpressdruck (nur bei Testern) | Subjektiv, schwer messbar |

### 1.3 Quellen
- **AutoEq (GitHub, MIT, Copyright Jaakko Pasanen 2018–2022)**: Messdaten von oratory1990, crinacle, InnerFidelity, RTINGS und (alt) headphone.com sowie Zielkurven und fertige EQ-Einstellungen; Modellzahl auf der Seite nicht genannt; Messungen stammen von Dritten, deren Quellen verlinkt sind und genannt werden sollten (https://github.com/jaakkopasanen/AutoEq, https://raw.githubusercontent.com/jaakkopasanen/AutoEq/master/LICENSE, beide 24.11.2026). **Wichtig:** MIT deckt den Code des Repos. Ob die darin eingebetteten Fremdmessungen (z. B. RTINGS-Kurven) frei weiterverwendbar sind, ist damit nicht belegt **[offen]**; sicherer sind Messungen eines Autors, der ausdrücklich freigibt. Frequenzgänge (Klang) sind verfügbar, ANC-Dämpfung nicht belegt.
- **squig.link / CrinGraph (crinacle-Ökosystem)**: kein Lizenz-/Nutzungshinweis gefunden; die Lab-Seite von squiglink weist darauf hin, dass die Beispielkurven synthetisch sind und Crinacles echte Messungen nicht öffentlich liegen (https://github.com/squiglink/lab via Suchergebnis, **[Hinweis]**). Ampel: rot für Übernahme, nur verlinken.
- **RTINGS**: Terms verbieten Reproduktion/Ableitungen und „screen/database scraping“ (Suchergebnis-Zusammenfassung von https://rtings.com/company/terms-of-use, **[Hinweis]**). Seit 31.03.2026 sind vollständige Testergebnisse Mitgliedern vorbehalten, ausdrücklich auch als Maßnahme gegen KI-Scraping (https://www.rtings.com/company/revamping-our-membership-program, Details über Sekundärberichte, **[Hinweis]**). robots.txt (24.11.2026): nur /user_reviews/ und /admin/ gesperrt (https://www.rtings.com/robots.txt). Ampel: rot (nur verlinken, ggf. schriftliche Anfrage).
- **Stiftung Warentest (test.de)**: Noten/Urteile nur mit Quelle zitierbar, Details Paywall; Übernahme der Note je Modell als Fakt plausibel, Umfang klein halten. Ampel: gelb.
- **SoundGuys, c't, Which?**: Nutzungsbedingungen nicht abrufbar (404 bzw. nicht geprüft) **[offen]**. Ampel: gelb/grau, nur verlinken.

### 1.4 Erlebbar machen (Module)
1. **„Wie viel leiser wird die Bahn?“** Balken vor/nach ANC über drei Bänder in Alltagssprache (Bass „Zugrollen“, Mitten „Stimmen“, Höhen „Zischen“). Datenbedarf: ANC-dB je Band je Modell, Alltagszuordnung als eigene, belegte Übersetzungstabelle (Dezibel-Differenz, z. B. 10 dB ≈ wahrgenommen halb so laut; Faustregel, **[offen]** Beleg ergänzen).
2. **Klangcharakter-Karte**: Kurve gegen Harman-Ziel als drei Schieberegler/Balken „Bass +2 dB, Mitten ±0, Höhen −1 dB“ plus Text („wärmer“, „neutral“, „hell“). Datenbedarf: Frequenzgang je Modell (AutoEq-Daten), Zielkurve.
3. **Hörprobe-Simulation (optional, Aufwand hoch)**: kurzer Musikausschnitt mit EQ-Kurve des Modells über Web Audio. Datenbedarf: Frequenzgang, eigene lizenzfreie Musik. Hinweis: simuliert nur den Frequenzgang des Kopfhörers (kein Treiber-, Dämpfungs-, Raumverhalten), nicht den Hörer des Nutzers.

### 1.5 Bewertungsmodell
Zwei Noten: **„Gemessen“** (nur mit Messwerten: Klang-Abweichung, ANC-Dämpfung, gemessene Laufzeit) und **„Ausstattung“** (Datenblatt: Multipoint, App-EQ, Codecs, Gewicht, faltbar, Kabel). Gesamtnote nur, wenn „Gemessen“ vorhanden ist; sonst Hinweis „nicht getestet“. Vorschlag nach RTINGS-Muster: Einsatz-Noten (Pendeln, Büro, Sport, Musik) mit unterschiedlichen Gewichten; Gewichte am Warentest-Schema orientieren (Klang 50, ANC 10 plus Gewichtsverschiebung für Pendler). Das passt zum schon im Schema vorgesehenen Mischmodell 0,6 Test + 0,4 Rohwert für getestete Modelle.

---

## 2. Kopfhörer In-Ear

### 2.1 Was zählt wirklich
Wie bei Over-Ear (Warentest-Gewichte Ton 50, ANC 10, Akku 10, Komfort 25, Haltbarkeit 5), zusätzlich Sitz/Dichtigkeit (wirkt auf Bass und ANC), Telefonieren und Wasserschutz (IP). Der Sitz hängt stark vom Ohr ab; deshalb Streuung betonen.

### 2.2 Messbare Größen
Frequenzgang gegen In-Ear-Zielkurve (Harman IE), ANC-dB je Band, Laufzeit je Ladung und mit Case (gemessen), Mikrofon-Qualität, Latenz (Spiele/Video).

### 2.3 Quellen
AutoEq enthält In-Ear-Messungen, genaue Abdeckung nicht belegt **[offen]**; sonst wie Abschnitt 1.3. Lizenz-Ampel gleich.

### 2.4 Erlebbar machen
1. **ANC-Bänder-Balken** wie Over-Ear.
2. **„Ein Tag mit dem Case“**: Zeitleiste aus gemessener Laufzeit je Ladung plus Case-Ladungen (Datenbedarf: Laufzeit gemessen oder Herstellerwert als Hinweis).
3. **Klangkarte** wie Over-Ear.

### 2.5 Bewertungsmodell
Wie Over-Ear; bei In-Ear „Sitz-Unsicherheit“ als Hinweis statt Score.

---

## 3. Fernseher

### 3.1 Was zählt wirklich
Stiftung Warentest: Bild 45, Handhabung 25, Ton 20, Strom 10 (https://www.test.de/Fernseher-im-Test-1629201-0/, Gewichte übernommen aus punkteschema.md). RTINGS legt in seiner Test-Bench 2.0 mehr Gewicht auf Hell-Raum-Verhalten und arbeitet mit festen Testmustern plus echtem Inhalt; Kontrast wurde auf einen angepassten Real-Scene-Test umgestellt, Local Dimming in vier Tests geteilt, Input-Lag vereinfacht; der Bewegungsteil ist laut Changelog zeitweise nicht aussagekräftig (https://www.rtings.com/tv/tests/changelogs/2-0 u. a., über Suchergebnis, **[Hinweis]**).

### 3.2 Messbare Größen
Spitzenhelligkeit HDR (nits, kleine/große Fenster), SDR-Helligkeit, nativer Kontrast bzw. Schwarzwert, Local-Dimming-Qualität (Blooming), Reflexion bzw. Hell-Raum-Leistung (z. B. Reflexionsgrad in %), Blickwinkel, Bewegungsschärfe/Reaktionszeit, Input-Lag (ms), Farbgenauigkeit/Farbraumabdeckung (DCI-P3 %), Upscaling/Sub-Black-Verhalten. Fachliche Schwellen nicht belegt **[offen]**.

### 3.3 Quellen
RTINGS (rot, siehe 1.3) und Notebookcheck-TV-Tests (Terms für Messwerte nicht auffindbar; Impressum: Inhalte urheberrechtlich geschützt, Namensnennung, Nicht-Kommerzielle dürfen ein Foto nutzen, Logos genehmigungspflichtig, https://www.notebookcheck.com/Impressum.45.0.html via Suchergebnis, **[Hinweis]**; robots.txt sperrt nur /nbcbattery/ und /cdn-cgi/, https://www.notebookcheck.net/robots.txt, 24.11.2026). Warentest-Noten als Fakt mit Link. Eigene Messung: nicht machbar. EU-Label (EPREL) für Strom: offene Daten, aber ohne Bildqualität. Keine freie TV-Messdatenbank gefunden.

### 3.4 Erlebbar machen
1. **Wohnzimmer-Simulator**: gleiche Szene (Film-Standbild, Eigenmaterial) in „heller Raum“ und „abgedunkelt“, Helligkeit und Reflexionsgrad des Modells als Überlagerung. Datenbedarf: Peak-nits, SDR-Helligkeit, Reflexion/Bright-Room-Wert, Raumhelligkeit als Regler.
2. **Matt vs. glänzend** (bestehende Idee der App): Reflexionsbild mit Fensterspiegelung, Intensität aus Reflexionsmessung.
3. **Schwarzwert-/Blooming-Szene**: Sternenhimmel mit hellem Objekt, Halo-Stärke aus Local-Dimming-Bewertung. Plus **„Ein Abend damit“** (bereits vorhanden): Szenarien Tagsüber-Sport, Abend-Film, Gaming; Ausgabe „besser/gleich/schlechter als dein Ausgangsmodell“.

### 3.5 Bewertungsmodell
„Getestet“-Note nur mit mindestens Helligkeit, Kontrast, Reflexion, Input-Lag aus einer Quelle; Datenblatt trägt nur Ausstattung (HDMI 2.1, Panelart, Smart-TV, Energieklasse). RTINGS-Usage-Muster: Noten je Einsatz (Film dunkel, Film hell, Sport, Gaming). Bei fehlenden Messwerten: „Noch nicht getestet“, nicht aus Datenblatt hochrechnen.

---

## 4. Soundbar

### 4.1 Was zählt wirklich
Stiftung Warentest: Ton 70, Handhabung 20, Strom 10 (https://www.test.de/Test-Soundbars-und-Soundplates-4931024-0/, aus punkteschema.md). Käufer spüren: Sprachverständlichkeit, Bass (mit/ohne Subwoofer), Raumklang/Höhenkanäle (Dolby Atmos), Lautstärke ohne Verzerrung.

### 4.2 Messbare Größen
Frequenzgang (Bassgrenze −6 dB Hz), maximaler Pegel (dB SPL) bei akzeptabler Verzerrung, Sprach-Tonalität (Mitten), Surround-Eindruck (nur Hörtest), Stromverbrauch Standby/Betrieb (Datenblatt/EPREL).

### 4.3 Quellen
RTINGS Soundbar-Tests (rot), Warentest (gelb), Herstellerangaben (Ausstattung). Keine offene Messdatenbank gefunden **[offen]**.

### 4.4 Erlebbar machen
1. **„Wie tief geht der Bass?“**: Balkenskala mit Alltagsmarken (Dialog, E-Gitarre, Explosion), Datenbedarf: Bassgrenze Hz.
2. **Sprachverständlichkeit-Vorher/Nachher**: Hörprobe mit Fernseher-Ton, Modell als EQ-Näherung (Hinweis: Näherung).
3. **Raum-Karte** (Grundriss mit Positionen): Schon vorhandene Fragen (Nachbarn, eARC, Höchstbreite) mit Hinweisen verbinden.

### 4.5 Bewertungsmodell
Ton-Anteil nur bei Messdaten; sonst zählt Ausstattung (Kanäle, Subwoofer, eARC) maximal ein Teil der Note, mit deutlichem Hinweis. Ohne Messdaten keine „sehr gut“-Note.

---

## 5. Smartphone

### 5.1 Was zählt wirklich
Stiftung Warentest: Grundfunktionen 30, Kamera 20, Display 15, Akku 15, Handhabung 15, Stabilität 5 (https://www.test.de/Handys-und-Smartphones-im-Test-4222793-0/, aus punkteschema.md). Käufer spüren: Akku über den Tag, Kamera bei schlechtem Licht, Display im Sonnenlicht, Update-Dauer, Alltagsgeschwindigkeit.

### 5.2 Messbare Größen
Gemessene Akkulaufzeit (Standardtest, Stunden), Display: Spitzenhelligkeit (nits, Sonnenlicht), Farbgenauigkeit, PWM-Flimmern; Benchmark (Geekbench, nur als grober Leistungswert); Kamera-Score (DXOMARK) oder Testfotos; Ladegeschwindigkeit (0–100 %, Minuten); EU-Label (Akkuausdauer pro Zyklus, Reparierbarkeit, Sturzfestigkeit; VO 2023/1669, https://energy-efficient-products.ec.europa.eu/product-list/smartphones-and-tablets_en, aus punkteschema.md).

### 5.3 Quellen
- **DXOMARK**: Seitennutzung nur privat oder begrenzt beruflich („Fair Use“, begrenzte Auszüge unverändert), Daten, Tabellen und Graphen ausdrücklich eingeschlossen, alles andere nur mit ausdrücklicher Erlaubnis; Kontakt contact@dxomark.com (https://dxomark.com/terms-and-conditions/ via Suchergebnis, **[Hinweis]**; widersprüchliche Fassungen gesehen). Ampel: rot für Übernahme ohne Erlaubnis, gelb für kleine Zitate mit Link.
- **Notebookcheck** (Smartphone-Tests, Akku-Test, Display-Messungen): siehe 3.3, gelb.
- **Geekbench Browser**: kein eigener Scraping-/Nutzungshinweis gefunden; die EULA sichert Primate Labs „sole and exclusive right to use, … distribute and otherwise exploit“ der Benchmark-Ergebnisse (https://www.primatelabs.com/legal/eula-v6.html via Suchergebnis, **[Hinweis]**). Ampel: gelb, einzelne Werte mit Link, kein Massenabzug.
- **displayspecifications.com, GSMArena** u. a.: nicht geprüft **[offen]**.
- **EU-EPREL**: offene Daten, Behörde, geringes Risiko, Ampel grün (Nutzungsbedingungen noch ausdrücklich nachzulesen **[offen]**).

### 5.4 Erlebbar machen
1. **„Akku-Tag“-Zeitleiste**: 7:00–23:00 mit Nutzungsprofil (Messenger, Video, Navigation, Spiel) und Balken, wann der Akku bei Standardnutzung leer wäre; Datenbedarf: gemessene Laufzeit je Testprofil oder Mischberechnung (Annahme offen legen).
2. **Sonnenlicht-Display-Vergleich**: Bildschirmschnitt bei 500/1000/2000 nits mit Umgebungslicht-Regler.
3. **Zoom-/Nachtfoto-Beispiele**: nur mit eigenen oder frei lizenzierten Bildern (Wikimedia Commons, CC), sonst nur Link zum Test. Datenbedarf: Kamera-Score als Fakt, Beispiele rechtefrei.

### 5.5 Bewertungsmodell
Notenbereiche nur aus Messwerten (Akku gemessen, Display-nits gemessen) plus Warentest-Note als getestet-Anker; Datenblatt-Werte (RAM, Speicher, Updates) nur Ausstattung. Ohne Messwert: Label-Akkuausdauer (Norm) statt Herstellerangabe.

---

## 6. Tablet

### 6.1 Was zählt wirklich
Warentest: Funktionen 30, Bildschirm 20, Akku 20, Handhabung 20, Vielseitigkeit 10 (https://www.test.de/Tablets-im-Test-4627215-0/, aus punkteschema.md). Käufer spüren: Display (Helligkeit, Reflexion, Schärfe), Akku (Video, Surfen), Stift/Tastatur, Update-Dauer.

### 6.2 Messbare Größen
Display-Helligkeit (nits), Farbraum, Reflexion, Laufzeit im Videotest, Gewicht, Lautsprecher (Notebookcheck-Messwerte), Benchmark.

### 6.3 Quellen
Notebookcheck (Tablet-Tests, gelb), Warentest (gelb), EU-Label (grün). DXOMARK Display-Scores bei einigen Tablets **[offen]**.

### 6.4 Erlebbar machen
1. **Couch-Display-Simulator**: Helligkeit gegen Raumlicht, Reflexionsgrad.
2. **„Ein Wochenende mit dem Tablet“**: Laufzeit in Stunden (Video) auf einer Zeitleiste mit Ladezeit.
3. **Stift/Tastatur-Check**: Ausstattungsliste (Stift im Lieferumfang, Tastaturfall) in „Passt zu deinem Einsatz“-Form.

### 6.5 Bewertungsmodell
Wie Smartphone: Messwerte tragen Display und Akku, Datenblatt nur Ausstattung/Vielseitigkeit.

---

## 7. Laptop

### 7.1 Was zählt wirklich
Warentest: Funktionen 30, Bildschirm 20, Akku 20, Handhabung 20, Vielseitigkeit 10 (aus punkteschema.md). Käufer spüren: Laufzeit im Alltag, Display (Helligkeit, Farbabdeckung, Matt/Glanz), Lautstärke und Wärme, Tastatur, Leistung für die eigene Aufgabe.

### 7.2 Messbare Größen
Laufzeit im WLAN-Test: Notebookcheck nutzt den Wi-Fi-Test als Basis mit Display auf 150 cd/m² und Skript, das wechselnde Webseiten lädt, teils mit Video (https://www.notebookcheck.net/Office-laptops-2026-compared-this-should-be-the-standard-battery-life-today.1322802.0.html via Suchergebnis, **[Hinweis]**); andere Labs nutzen andere Helligkeitsziele (z. B. 200 cd/m² bei UL Procyon), also nur innerhalb einer Quelle vergleichbar. Display: Helligkeit (cd/m²), sRGB-/P3-Abdeckung, Kontrast, PWM; Lautstärke (dB) unter Last, Oberflächentemperatur, CPU-/GPU-Benchmark, Tastaturgefühl (subjektiv).

### 7.3 Quellen
Notebookcheck (Messwerte, große Abdeckung, aber ohne explizite Nutzungslizenz für Messwerte, Namensnennung verlangt, gelb); RTINGS Laptop (rot, Mitgliedsmodell); c't und Warentest (gelb); Geekbench Browser für Leistung (gelb). Offen lizenzierte Laptop-Messdaten nicht gefunden.

### 7.4 Erlebbar machen
1. **Laufzeit-Balken in Alltagssprache**: „Ein Arbeitstag Büro“, „Zug Berlin–München“, „Streaming-Abend“; Balkenlänge aus gemessenen Stunden je Profil, Annahme sichtbar (Helligkeit).
2. **Lautstärke-Vergleich**: Alltagsmarken (Flüstern, Büro, Staubsauger) mit dB-Wert unter Last.
3. **„Schaffe ich das?“-Leistungsampel**: Aufgaben (Büro, Foto, 4K-Schnitt, Spiele) grün/gelb/rot aus Benchmark-Klassen, Schwellen als Annahme gekennzeichnet.

### 7.5 Bewertungsmodell
Laufzeit und Display-Qualität nur aus Messwerten; Hersteller-Laufzeit zählt gering (im Schema bereits so). Leistungs-Note nur aus Benchmark-Klassen, Filter statt Punkte bei GPU.

---

## 8. Bewertungsmodell gesamt (Vorschlag)

1. **Zwei Spuren je Modell:** „Ausstattung“ (Datenblatt, sicher) und „Getestet“ (Messwerte/Test, nur mit Quelle). Gesamtnote erscheint nur mit Spur 2 und bleibt sonst als „Vorläufig, nicht getestet“ gekennzeichnet.
2. **Einsatz-Noten** (RTINGS-Muster): je Einsatz eigene Gewichte (TV: Film dunkel/hell/Sport/Gaming; Kopfhörer: Pendeln/Büro/Sport/Musik; Laptop: Büro/Unterwegs/Kreativ/Spiele).
3. **Mischung:** Schema-Vorschlag 0,6 × Test + 0,4 × Rohwert bleibt für getestete Modelle; Warentest-Umrechnung `T = 100 − (Note − 0,5) × 20`, RTINGS-0–10-Skala `T = Wert × 10` (beide sind Vorschläge laut punkteschema.md).
4. **Quellenvermischung vermeiden:** keine Messwerte verschiedener Labore addieren (Akku, Helligkeit, ANC-dB sind labor-abhängig); je Kategorie ein Primärlabor, andere nur als Gegenprobe.
5. **Sichtbare Unsicherheit:** Quelle, Testdatum, Messversion neben jedem Wert; Vorsicht bei Test-Bench-Wechsel (RTINGS ändert Gewichte zwischen Versionen **[Hinweis]**).

---

## 9. Quellen-Tabelle

| Quelle | Daten | Abdeckung | Lizenz/AGB | Paywall | robots.txt | Risiko § 87b | Nutzung | Ampel |
|---|---|---|---|---|---|---|---|---|
| AutoEq (GitHub) | Kopfhörer-Frequenzgänge, Zielkurven | Hoch (Zahl nicht belegt) | MIT für Repo; Fremdmessungen einzeln prüfen [offen] | nein | n. a. (GitHub) | gering bis mittel, wenn nur ausgewählte Modelle mit Quelle | Fakt mit Quelle, Link | grün/gelb |
| oratory1990 | Frequenzgänge | hoch | nicht geprüft [offen] | teils Patreon | nicht geprüft | mittel | nur über AutoEq, mit Namensnennung | gelb |
| squig.link/CrinGraph | Frequenzgänge | hoch | keine Hinweise gefunden [Hinweis] | nein | nicht geprüft | mittel | nur verlinken | rot |
| RTINGS | alle Kategorien | hoch | Terms verbieten Kopie/Scraping [Hinweis] | seit 31.03.2026 Mitglieder [Hinweis] | /user_reviews/, /admin/ gesperrt | hoch | nur verlinken, ggf. Anfrage | rot |
| Notebookcheck | Laptop/Smartphone/Tablet/TV | hoch | Impressum: Urheberrecht, Namensnennung [Hinweis] | nein | /nbcbattery/, /cdn-cgi/ gesperrt | mittel | wenige Fakten mit Namen und Link | gelb |
| DXOMARK | Kamera/Display/Akku/Audio | hoch (Smartphone) | Fair Use nur, Daten eingeschlossen [Hinweis] | teils | nicht geprüft | hoch | nur Zitat/Link | rot |
| Stiftung Warentest | Noten, Gruppenurteile | mittel | Noten zitierbar, Details Paywall | ja | nicht geprüft | gering bei Einzelnoten | Note je Modell mit Link | gelb |
| c't / Which? | Tests | mittel | nicht geprüft [offen] | ja | nicht geprüft | offen | nur verlinken | grau |
| SoundGuys | Kopfhörer-Tests | mittel | Terms 404 [offen] | nein | nicht geprüft | offen | nur verlinken | grau |
| Geekbench Browser | Benchmarks | hoch | EULA-Rechte bei Primate Labs [Hinweis] | nein | nicht geprüft | mittel | einzelne Werte mit Link | gelb |
| displayspecifications / GSMArena | Datenblätter | hoch | nicht geprüft [offen] | nein | nicht geprüft | offen | nur verlinken | grau |
| EU-Label/EPREL | Energie, Akkuausdauer, Reparierbarkeit | hoch | Behördendaten, Bedingungen noch ablesen [offen] | nein | nicht geprüft | gering | als Fakt | grün |

## 10. Empfehlung: Pilot-Kategorie

**Kopfhörer Over-Ear als Pilot.**
- Einzige Kategorie mit offen lizenzierter Datenbasis (AutoEq, MIT) für Klangcharakter; ANC-Dämpfung braucht zusätzlich eine Quelle (RTINGS/SoundGuys nur verlinken, ggf. Anfrage).
- Das Problem aus dem Auftrag (65-€-Soundcore vor Sony XM6) ist dort am sichtbarsten und mit Frequenzgang und ANC-Dämpfung unmittelbar lösbar.
- Die „erlebbaren“ Module (ANC-Bänder-Balken, Klangkarte) sind rein datenbasiert, ohne Rechte an Fotos oder Videos.
- Vorbedingungen vor dem Bau: (1) Lizenz der Fremdmessungen in AutoEq je Quelle klären, (2) Quelle für ANC-Dämpfung in dB festlegen, (3) Übersetzungstabelle dB zu Alltagsaussage belegen.

Zweite Wahl: **Laptop** (Notebookcheck-Laufzeit und Display-Werte als Fakt mit Link, Laufzeit-Balken, kein Medienbedarf), aber Lizenz für Massenübernahme ungeklärt; Fernseher hat den größten Nutzen, aber die schwächste freie Datenlage und den höchsten Gestaltungsaufwand.

## 11. Offene Punkte (vor Umsetzung)
1. Nutzungsbedingungen von RTINGS, SoundGuys, DXOMARK, Notebookcheck im Volltext lesen (hier nur über Suchergebnisse oder gar nicht).
2. AutoEq: Lizenzlage je Messquelle (oratory1990, crinacle, RTINGS) klären, Modellzahl und Aktualität prüfen.
3. Schriftliche Anfrage an einen Anbieter (Notebookcheck, RTINGS) zur Nutzung einzelner Messwerte mit Quelle und Link.
4. Warentest-Gewichte für Kopfhörer stammen aus dem bestehenden Schema, hier nicht neu geprüft.
5. Alle Schwellen und Alltagsübersetzungen (dB zu „leiser“, nits zu Raumhelligkeit) sind Vorschläge und brauchen Beleg.
