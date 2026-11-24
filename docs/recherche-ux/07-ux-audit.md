# 07 – UX-Audit des Produktfinders

Stand: 24.11.2026 · Gegenstand: Finder (Startseite der App, `app/finder/`) im Zusammenspiel mit dem Ratgeber (`ratgeber.html`) · Vorschau `http://localhost:8790/`, Handybreite 375 × 812, hell und dunkel.

Methode: Heuristiken nach Nielsen (N1–N10), Apple HIG als Grundsätze für Web/Android (Klarheit, Rückmeldung, Navigation, Tippziele, Typografie, Leerzustände, Fehlertoleranz, Barrierefreiheit), Gestaltungshaltung aus `frontend-design`. Hinweis zur Methode: Die Impeccable-Anleitung (`.claude/skills/impeccable/SKILL.md` im Worktree `admiring-pasteur-32f79f`) ist nicht vorhanden; der Ordner enthält nur leere Unterordner `reference/degraded` und `scripts/data`. „Critique“ und „Audit“ sind deshalb sinngemäß angewendet (Critique = Gesamturteil, Hierarchie, Haltung; Audit = prüfbare Einzelbefunde mit Ort und Schwere), nicht nach Impeccables eigenem Raster.

Durchlaufen: Fernseher bis 700 € / Filme; Kopfhörer Over-Ear bis 350 € / Reisen / iPhone; Waschmaschine ohne Angaben. Dazu Vergleich (3 Modelle), Sortierung „Günstigste“, „Wie wir bewerten“, Dunkelmodus, Ratgeber-Vorbild „Fenster im Bild: matt gegen glänzend“.

Schwere: **P0** zerstört Vertrauen oder Zweck · **P1** große Reibung, Besitzerkritik direkt betroffen · **P2** spürbar, aber umgehbar · **P3** Feinschliff.

---

## 1. Kurzurteil (Critique)

Der Finder ist handwerklich sauber (Tippziele ≥ 44 px, Fokusführung, `aria-live`-Status, Adresse als Zustand, sichere Ausgabe), aber er beantwortet die Frage des Käufers nicht: „Was kriege ich für mein Geld, und stimmt das?“ Er zeigt eine einzige Zahl, die aus einer Ausstattungs-Checkliste entsteht, kappt sie bei 84 und lässt dann den Preis entscheiden. Dadurch gewinnt in mehreren Kategorien das billigste vollausgestattete Gerät, und die Begründung dafür liegt ganz unten im Seitenfuß. Es gibt keine Produktseite, keine Bilder, nur einen Preis je Modell und keine Verbindung zum Ratgeber, der genau das „Erlebbare“ schon kann. Die Seite hat keinen Moment, an den man sich erinnert; die große Note ist das Signaturelement, und sie ist zugleich das Unglaubwürdigste auf dem Bildschirm.

Gesamturteil: **Kritische Probleme** (Glaubwürdigkeit der Note, fehlende Produktebene, getrennte Welten).

---

## 2. Befunde (Audit)

### P0 – Vertrauen und Zweck

**B01 · Note misst Ausstattung, nicht Qualität – und klingt wie ein Testurteil**
- Ort: Ergebnis → Empfehlungskarte; `app/finder/bewertung.js:117-157` (Datenblattnote), `app/finder/finder.js:506-513` (Notenanzeige „84 von 100 · sehr gut“).
- Beobachtung: Kopfhörer Over-Ear, bis 350 €, Reisen/iPhone: JBL Tune 770NC (129,99 €) = 84, Marshall Monitor III = 84, Soundcore Space One (65 €) = 84 (gerundet aus 83,88), Sony WH-1000XM6 (327 €) = 80 auf Rang 6. Die Felder der Kategorie sind ANC (ja/nein, Gewicht 20), Akku, Gewicht, Multipoint, App-EQ, Codecs, Kabelbetrieb, faltbar, Transparenzmodus. Klang und ANC-Stärke kommen nicht vor; „ANC: ja“ gibt jedem Modell 100 Teilpunkte. Der Rohwert R liegt bei den Spitzenmodellen zwischen 89 und 98, die Kappung bei 84 schneidet alles ab. Waschmaschinen: 24 Modelle zwischen 57 und 72, Hisense für 399 € gleichauf mit Miele für 977 € (beide 72).
- Wirkung: Wer sich auskennt, sieht sofort, dass die Rangfolge nicht stimmt, und verwirft das ganze Werkzeug. Das ist der Kern der Besitzerkritik.
- Vorschlag: (1) Die Zahl nicht „Note“ und nicht „sehr gut“ nennen, solange keine Tests eingehen; stattdessen „Ausstattung passt zu dir: 9 von 9 Punkten“ als Checkliste und eine getrennte, ehrlich leere Zeile „Klang/Bild im Test: noch keine Daten“. (2) Testdaten (Recherche 03/04) vor jeder weiteren Gestaltung einbinden; erst dann eine Gesamtnote. (3) Bis dahin Rangfolge nicht als „Unsere Empfehlung“ überschreiben, sondern „Erfüllt deine Wünsche am vollständigsten“.

**B02 · Kappung bei 84 macht die oberste Klasse unerreichbar und den Preis zum heimlichen Sieger**
- Ort: `bewertung.js:122` (`Math.min(db.kappung, …)`), Regeln `daten/schema/kategorien.json` (kappung 84, Klasse „hervorragend“ ab 85), `bewertung.js:161-171` (Gleichstand → günstiger zuerst), Skala `finder.js:455-472`.
- Beobachtung: Kein einziges Modell in der Datenbank hat einen Testwert mit Punkten (alle 14 Kategorien: 0 Modelle mit `tests`). Damit kann keine Note über 84 liegen; die Klasse „hervorragend“ wird nie vergeben. Die Skala zeigt die Marke „85“, darunter steht „Ab 84 nur mit unabhängigem Test“ – zwei Zahlen für dieselbe Grenze. Alle Spitzenmodelle stauen sich an der Kappung, danach entscheidet Rundung oder Preis.
- Vorschlag: Kappung und Klassen erst einführen, wenn Testwerte vorhanden sind; bis dahin keine Klassenwörter. Wenn die Skala bleibt: eine Grenze, einheitlich beschriftet, und der schraffierte Bereich bekommt die Beschriftung im Bild („nur mit Test“) statt einer zweiten Zahl.

**B03 · Widersinniger Spar-Hinweis „84 statt 84 Punkte“**
- Ort: Ergebnis Kopfhörer → Hinweiskarte; `bewertung.js:225-251`, Text `daten/schema/kategorien.json:80`.
- Beobachtung: „Für 65 € weniger fast gleich gut (84 statt 84 Punkte).“ Das empfohlene Modell ist also teurer als ein gleich bewertetes. Der Hinweis widerlegt die Empfehlung direkt darüber.
- Vorschlag: Wenn gerundet gleich: Empfehlung tauschen oder beide als „gleichauf“ zeigen („Zwei gleich gute Wahlen – die günstigere spart 65 €“). Text nie mit identischen Zahlen ausgeben.

**B04 · Keine Produktebene: Listeneinträge führen nirgends hin**
- Ort: Rangliste `finder.js:558-579`; Empfehlung `finder.js:483-519`.
- Beobachtung: Ein Eintrag hat nur „Angebot“ (externer Shop) und „Vergleichen“. Es gibt keine Detailansicht mit Bild, allen Werten, Herkunft der Werte, Tests, Preisverlauf. Die einzige Stelle mit allen Werten ist der Vergleich – erst ab zwei Modellen. Kein Modell hat ein Bild (0 von 413).
- Wirkung: „Was man kauft und was man nachher kriegt“ ist nicht darstellbar; der Nutzer verlässt die App zum Shop, um das Produkt überhaupt zu sehen.
- Vorschlag: Produktseite als eigener Schritt (siehe Gegenentwurf §4), erreichbar durch Tippen auf jede Zeile und die Empfehlungskarte.

### P1 – Große Reibung

**B05 · Nur ein Preis je Modell, kein Angebotsvergleich**
- Ort: `finder.js:474-481` (`preisBlock`), Rangliste `finder.js:565`.
- Beobachtung: „449 € bei Alternate, Stand 21.11.2026“ – ein Händler, ein Datum. Preis-Abdeckung lückenhaft: Smartphones 4 von 40 Modellen mit Preis, Fernseher 32 von 75. Bei Budget blendet die Liste Modelle ohne Preis aus („Auch teurere und ohne Preis zeigen (64)“ bei Fernsehern bis 700 €).
- Vorschlag: Angebotsliste je Modell (Händler, Preis, Versand, Stand, sortiert), in der Liste „ab 449 € · 4 Shops“. Ohne Preis nicht stillschweigend ausblenden, sondern eigene Gruppe „Preis gerade unbekannt“ (siehe Recherche 05).

**B06 · „Wie wir bewerten“ ist versteckt, allgemein und ohne Bezug zum Modell**
- Ort: `index.html:28-34` (Fuß, `<details>`), erreichbar erst nach der ganzen Liste und dem Vergleich; im Test zusätzlich von der Vergleichsablage überdeckt.
- Beobachtung: Drei Absätze Prosa, keine Aufschlüsselung „woher kommen die 84 Punkte dieses Modells“. `bewerteModell` berechnet bereits `beitraege` je Feld (`bewertung.js:140`), die Oberfläche nutzt nur die drei größten als „Stärken“.
- Vorschlag: Auf jeder Note ein Tippziel „So entsteht die 84“ → Aufschlüsselung als Balken je Merkmal (Gewicht × Teilpunkte), welche Antwort welches Gewicht hochgesetzt hat, was fehlt, was gekappt wurde. Allgemeine Methode als eigene Seite im Menü, nicht im Fuß.

**B07 · Zwei getrennte Welten: Finder und Ratgeber**
- Ort: Kopfleiste `index.html:16-19`; Ratgeber-Kopf „‹ Finden & Vergleichen“.
- Beobachtung: Der Ratgeber hat eigene Navigation (unten Reiter Fernseher/Sauger/Air Fryer/Handy), eigenen Ablauf (1 Bedarf · 2 Empfehlung · 3 Vergleich · 4 Details), eigene Fragen (Fernseher: 6 Fragen gegenüber 4 im Finder plus Größe), eigene Modellauswahl mit Quellen je Wert, eigene Schrift und eigene interaktive Demonstrationen. Der Finder hat 14 Kategorien, der Ratgeber 4. Zwischen beiden gibt es nur den Textlink „Ausführlicher Ratgeber“ zum Seitenanfang, nie kategorie- oder modellbezogen. Antworten aus dem einen werden im anderen nicht übernommen.
- Vorschlag: siehe §3 – eine Kategorie = ein Ort; Ratgeberinhalte als Abschnitte „Verstehen“ in der Kategorie und als Erklärkarten an den Fragen und Merkmalen.

**B08 · Varianten als eigene Zeilen, „Standard“ und doppelte Typbezeichnungen**
- Ort: `finder.js:147` (`modellName` = Name + Variante), Rangliste und Vergleich.
- Beobachtung: Kopfhörer: jede Zeile „…, Standard“ (alle 17 Modelle haben Variante „Standard“). Waschmaschinen: „Hisense WF5S1045BW, WF5S1045BW“ (Variante = Typnummer). Fernseher bis 700 €: von 11 Zeilen sind 5 dieselbe Serie Hisense E7S in 43/50/55/65/75 Zoll mit gleicher Note 55; die Liste wirkt wie ein Hisense-Katalog.
- Vorschlag: Variante nur zeigen, wenn sie sich vom Namen unterscheidet und nicht „Standard“ ist. Größen einer Serie zu einer Zeile zusammenfassen („Hisense E7S · 43–75″ · ab 279 €“) mit Größenwahl auf der Produktseite; bei gesetzter Größe nur die passende Größe zeigen.

**B09 · Frageführung: doppelte und widersprüchliche Fragen, alles auf einem langen Bildschirm**
- Ort: Budget-Schritt `finder.js:331-359` (Größe), Fragen-Schritt `finder.js:362-392`.
- Beobachtung: Beim Fernseher wird die Größe in Schritt 1 erfragt und der Sitzabstand in Schritt 2 – der Abstand bestimmt die sinnvolle Größe, beide können sich widersprechen, ohne dass etwas passiert. Alle 4–5 Fragen stehen untereinander (Fernseher: rund drei Bildschirmhöhen), jede mit vorausgewählter Option „Egal / weiß nicht“ an erster Stelle; der Nutzer sieht nicht, welche Frage wie viel bewirkt. Die Budget-Schnellwahl bietet Stufen, die nicht zum häufigen Wunsch passen (Fernseher: 600/900/1.200/2.700 €, kein 700/1.000/1.500).
- Vorschlag: Eine Frage je Bildschirm mit sofortiger Rückmeldung („passt zu 31 von 75 Modellen“), „weiß nicht“ als Textlink unten statt vorgewählter erster Option, Sitzabstand → Größenvorschlag statt zweier unabhängiger Fragen, runde Budgetstufen aus den Preisquartilen (auf 50/100 € gerundet) plus Schieberegler.

**B10 · Viele Modelle ohne Note, ohne Erklärung, mitten in der Rangliste**
- Ort: `finder.js:561`, Rangliste Kopfhörer Rang 12–14.
- Beobachtung: „zu wenig Daten für eine Note“ bei Bose QuietComfort Ultra (2. Gen.), Bowers & Wilkins Px7 S3, Sennheiser Accentum – also gerade bei bekannten Spitzenmodellen. Rang-Nummern laufen durch (12, 13, 14), obwohl sie nicht bewertet sind. Welche Angabe fehlt, steht nicht da.
- Vorschlag: Eigene Gruppe „Noch nicht bewertbar“ unter der Rangliste, ohne Rangnummer, mit „fehlt: Akkulaufzeit, Gewicht“. Datenpflege priorisiert Modelle, die Nutzer suchen (Bekanntheit), nicht nur das, was Datenblätter hergeben.

### P2 – Spürbar

**B11 · Vergleich ist ein Abschnitt am Seitenende, „Vergleichen“-Knopf springt im Test nicht**
- Ort: `finder.js:595-629`, Ablage `finder.js:632-646`, Sprung `finder.js:643`.
- Beobachtung: Der Knopf „Vergleichen“ in der Ablage setzt den Fokus auf die Überschrift (`activeElement = vgl-titel`), die Seite blieb im Testbrowser aber stehen (`scrollY` unverändert; `scrollIntoView({behavior:"smooth"})` hatte dort generell keine Wirkung, `"auto"` schon). Auf einem echten Gerät nachprüfen; unabhängig davon ist ein Vergleich am Ende einer 4.500 px langen Seite schwer wiederzufinden. Kopfzeile des Vergleichs klebt oben (gut), aber gleiche Werte in allen Spalten („ja/ja/ja“) werden nicht ausgeblendet, und es fehlen Zeilen für Preis je Shop, Tests, Herkunft.
- Vorschlag: Vergleich als eigener Bildschirm mit eigenem Adressschritt (`s=vergleich`), Schalter „Nur Unterschiede“, Entfernen je Spalte, Preiszeile mit „ab … · n Shops“.

**B12 · Vergleichsablage überdeckt Inhalt**
- Ort: `.ablage` (`finder.css`), sichtbar auf allen Ergebnis-Scrollpositionen.
- Beobachtung: Die feste Ablage (ca. 130 px) liegt über Stärkenliste, Listeneinträgen und dem Methodentext im Fuß; unten fehlt ein Freiraum in Höhe der Ablage.
- Vorschlag: `padding-bottom` des Hauptbereichs um die Ablagenhöhe plus `env(safe-area-inset-bottom)` erhöhen; Ablage kompakter (eine Zeile: „3 gewählt · Vergleichen“).

**B13 · „Vergleich voll (3)“ an jeder Zeile**
- Ort: `finder.js:532-545`.
- Beobachtung: Nach drei Haken steht an jeder weiteren Zeile ein ausgegrautes „Vergleich voll (3)“ – Rauschen in 10+ Zeilen.
- Vorschlag: Haken bleibt aktiv; beim vierten erscheint ein kurzer Hinweis in der Ablage „Höchstens 3 – eins ersetzen?“.

**B14 · iPhone-Antwort ohne sichtbare Wirkung, irrelevante Stärken**
- Ort: Vergleich Kopfhörer, Feld „Beste unterstützte Bluetooth-Codecs“.
- Beobachtung: Nach „iPhone“ wird LDAC als Vorteil hervorgehoben; iPhones nutzen kein LDAC (fachlich zu belegen, Quelle in der Datenbank ergänzen). Der Nutzer erfährt nicht, was seine Antwort verändert hat.
- Vorschlag: Antwortwirkung sichtbar machen („Weil du ein iPhone nutzt, zählt AAC statt LDAC“); feldbezogene Relevanz je Antwort im Schema.

**B15 · Gleiche Rundungsnote, nicht nachvollziehbare Reihenfolge**
- Ort: Fernseher-Rangliste Rang 2–6 (alle 55), `bewertung.js:161-171`.
- Beobachtung: 75 Zoll für 699 € steht vor 43 Zoll für 279 €, beide „55“. Ursache sind Nachkommastellen, die nicht angezeigt werden.
- Vorschlag: Bei gleicher angezeigter Note nach Preis sortieren oder „gleichauf“ gruppieren; Rangnummern bei Gleichstand gleich vergeben.

**B16 · Datenblatt-Herkunft und Stand pro Wert fehlen im Finder, im Ratgeber vorhanden**
- Ort: Vergleich/Stärken; Ratgeber zeigt „Quelle“ je Wert und „nicht belegt (gesucht: …)“.
- Vorschlag: In der Produktseite je Wert eine kleine Herkunftsmarke (Datenblatt, EU-Label, Test, Datum) mit Link.

### P3 – Feinschliff

**B17 · Startseite: 14 gleichwertige Kacheln, kein Einstieg über Bedarf** (`finder.js:241-271`). Kein Suchfeld nach Modellname, kein „zuletzt angesehen“, keine Hilfe für „Ich weiß nicht, welche Kategorie“. Vorschlag: Suchfeld oben, darunter Kategorien, darunter „Zuletzt angesehen / gemerkt“.

**B18 · Kleine Schriftgrößen in der Notenskala** (`finder.css:194-196`, .72rem ≈ 11,5 px; .78rem). HIG-Minimum 11 pt erreicht, aber unter der Lesbarkeit für ältere Nutzer; Skala ist ohnehin schwer lesbar (B02).

**B19 · Leerer Vergleichsabschnitt immer sichtbar** (`finder.js:600-603`) – Hilfetext „Hake bei bis zu drei Modellen …“ steht auch dann, wenn niemand vergleichen will. Nur zeigen, wenn ≥ 1 Modell gewählt ist.

**B20 · Begriffe** – „Antworten ändern“ / „Zurück“ / „Kategorien“ wechseln je Schritt; „Punkte je Euro“ ist eine technische Kennzahl ohne Erklärung; „aus Datenblatt“ ohne Tipp-Erklärung. Einheitlich: „Zurück“ + Schrittanzeige; „Preis-Leistung“ statt „Punkte je Euro“.

### Was gut ist und bleiben soll
- Zustand in der Adresse (`#k=…&s=…`), Zurück-Taste funktioniert, Links teilbar.
- Tippziele ≥ 44 px (`finder.css:57-58, 73, 123, 156, 216`), sichtbarer Fokus, `role="status"` für Ergebniszahl, Fokus auf Titel beim Schrittwechsel.
- Ehrliche Kennzeichnung „aus Datenblatt“, „nicht belegt“, Preisstand mit Datum.
- Dunkelmodus vollständig, Kontrast ausreichend (z. B. `--muted #5a6472` auf `#eef1f5` ≈ 5,3:1, eigene Rechnung).
- Budget live im Ergebnis änderbar, ohne Fokusverlust.
- Klebende Modellzeile im Vergleich.

---

## 3. Informationsarchitektur

### Ist
```
Startseite = Finder (14 Kategorien)          Ratgeber (eigene Seite, 4 Kategorien)
 └ Kategorie                                  ├ Reiter unten: Fernseher · Sauger · Air Fryer · Handy
    ├ 1 Budget (+ Größe/Bauart)              │   ├ 1 Bedarf (6 Fragen, Bildgröße)
    ├ 2 Fragen (alle auf einer Seite)        │   ├ 2 Empfehlung
    └ 3 Ergebnis                              │   ├ 3 Vergleich
       ├ Empfehlung + Hinweis                │   └ 4 Details (Technik, Demos, Quellen)
       ├ Rangliste (keine Produktseite)      └ „‹ Finden & Vergleichen“ → Finder-Start
       ├ Vergleich (Abschnitt unten)
       └ Fuß: „Wie wir bewerten“, Link Ratgeber (Seitenanfang)
```
Probleme: zwei Fragebögen für dieselbe Kategorie mit verschiedenen Fragen und verschiedenen Empfehlungen; keine kategorie- oder modellgenauen Querverweise; die erlebbaren Demonstrationen (Spiegelungen, Bildgröße) liegen tief im Ratgeber unter „Details“, wo der Finder-Nutzer nie hinkommt; Rückweg vom Ratgeber führt immer zur Finder-Startseite, nicht in die eben benutzte Kategorie.

### Soll: eine Kategorie = ein Ort mit drei Ebenen
```
Start
 ├ Suche (Modell oder Kategorie)
 ├ Kategorien
 └ Gemerkt / Zuletzt angesehen
Kategorie (z. B. Fernseher)
 ├ Finden      → Fragen → Ergebnis → Produktseite → Angebote
 ├ Verstehen   → Ratgeber-Kapitel + Erlebnis-Test („So sieht es aus“)
 └ Alle Modelle (Liste mit Filtern)
Produktseite
 ├ Was du kriegst (Erlebnis-Kacheln aus Tests)
 ├ Warum diese Punkte (Aufschlüsselung)
 ├ Angebote (alle Shops)
 └ Datenblatt mit Herkunft
Vergleich (eigener Schritt, max. 3)
```
Regeln: Fragen gibt es einmal je Kategorie (Finder übernimmt die Ratgeberfragen oder umgekehrt). Jede Frage und jedes Merkmal verlinkt die passende Ratgeber-Erklärung („Was heißt das?“) als Blatt von unten, mit Rückkehr an dieselbe Stelle. Untere Navigationsleiste in der ganzen App gleich: Finden · Verstehen · Gemerkt.

---

## 4. Gegenentwurf der Abläufe (Textskizzen, 375 px)

### 4.1 Start
```
┌───────────────────────────────────┐
│ Kaufberatung                      │
│ ┌───────────────────────────────┐ │
│ │ 🔍 Modell oder Gerät suchen    │ │
│ └───────────────────────────────┘ │
│ Was willst du kaufen?             │
│ ┌──────────┐ ┌──────────┐         │
│ │ Fernseher│ │ Kopfhörer│  …      │
│ │ 75 Mod.  │ │ 33 Mod.  │         │
│ │ 4 getest.│ │ 0 getest.│ ← ehrlich│
│ └──────────┘ └──────────┘         │
│ Weitermachen: Fernseher bis 700 € │
│   (3 Antworten, gestern)        > │
├───────────────────────────────────┤
│  Finden     Verstehen    Gemerkt  │
└───────────────────────────────────┘
```

### 4.2 Fragen – eine je Bildschirm, Wirkung sichtbar
```
┌───────────────────────────────────┐
│ ‹ Fernseher           Frage 2 von 4│
│ ▓▓▓▓▓▓▓▓░░░░░░░░                    │
│                                   │
│ Wie weit sitzt du weg?            │
│ ┌───────────────────────────────┐ │
│ │ unter 2 m      → 43–55″        │ │
│ │ 2–2,5 m        → 55–65″        │ │
│ │ 2,5–3,2 m      → 65–77″   ✓    │ │
│ │ über 3,2 m     → 77″+          │ │
│ └───────────────────────────────┘ │
│ ⓘ Warum? Bildgröße erleben  ›     │  ← öffnet Ratgeber-Demo als Blatt
│                                   │
│ 31 von 75 Modellen passen         │  ← Live-Zahl
│ [ Weiter ]          Weiß ich nicht│
└───────────────────────────────────┘
```

### 4.3 Ergebnis – Empfehlung mit Begründung, Liste gruppiert
```
┌───────────────────────────────────┐
│ ‹ Antworten   Fernseher  bis 700 € ✎│
│ Filme · 2,5–3,2 m · 65–77″         │  ← antippbar = ändern
│ ┌───────────────────────────────┐ │
│ │ [Bild]  LG OLED B6 65″         │ │
│ │ Passt am besten zu dir         │ │
│ │ Bild ●●●●○ Test   Ausstatt. 9/9│ │  ← zwei getrennte Achsen
│ │ ab 874 € · 5 Shops        ›    │ │
│ │ Warum? Kontrast für Filme …    │ │
│ └───────────────────────────────┘ │
│ Gleich gut, günstiger: …    65 € ›│
│ ── Weitere 12 passende ──  Sortieren▾│
│ [Bild] Hisense E7S  43–75″  ab 279›│  ← Serie in einer Zeile
│ …                                 │
│ ── Noch nicht bewertbar (3) ──    │
├───────────────────────────────────┤
│ ☐☐☐ 0 im Vergleich                │
└───────────────────────────────────┘
```

### 4.4 Produktseite (neu) – „was man kauft und was man kriegt“
```
┌───────────────────────────────────┐
│ ‹ Ergebnis                ♡  Teilen│
│ [ Produktbild / Schema ]          │
│ LG OLED B6 · 65″  (55 · 77)       │  ← Größenwahl
│ ab 874 € · 5 Shops · Stand 24.11. │
│ [ Angebote ansehen ]  [Vergleichen]│
│                                   │
│ Was du kriegst                    │
│ ┌ Erlebnis-Karte ───────────────┐ │
│ │ Fenster im Bild  ◐ Tageslicht │ │  ← Demo wie im Ratgeber,
│ │ [ Szene: dunkel | hell ]      │ │    mit DIESEM Modell vs.
│ │ dieses Modell  vs.  E7S       │ │    Vergleichsmodell
│ └───────────────────────────────┘ │
│ Spiel-Latenz · Ton · Helligkeit … │
│                                   │
│ Warum 79 Punkte?           ▾      │
│  Kontrast ████████░ 30 % Gewicht  │
│  HDR      ██████░░░ 15 %          │
│  fehlt: HDMI 2.1 (nicht belegt)   │
│                                   │
│ Datenblatt (mit Quelle je Wert) ▾ │
└───────────────────────────────────┘
```

### 4.5 Vergleich (eigener Schritt)
```
┌───────────────────────────────────┐
│ ‹ Ergebnis   Vergleich   ☑ Nur Unterschiede│
│      B6 65″   │ E7S 65″  │ U8099H ✕ │
│      79       │ 55       │ 50       │
│      ab 874 € │ ab 549 € │ ab 679 € │
│ Bild (Test)  ●●●●○ │ ●●○○○ │ –      │
│ Kontrast     OLED  │ QLED  │ LCD    │
│ Spiegelung   [Demo öffnen]          │
│ …                                  │
└───────────────────────────────────┘
```

### 4.6 Angebote
```
┌───────────────────────────────────┐
│ ‹ LG OLED B6 65″      Angebote (5) │
│ Händler      Preis    Versand  Stand│
│ Shop A       874 €    frei   24.11 ›│
│ Shop B       889 €    4,99 € 24.11 ›│
│ Shop C       899 €    frei   23.11 ›│
│ Preisverlauf 30 Tage  ▁▂▃▂▁▁       │
│ ⓘ Preise ohne Gewähr, Stand je Zeile│
└───────────────────────────────────┘
```

### Erlebnis-Test je Kategorie (Vorbild Ratgeber „Fenster im Bild“)
Das Vorbild: Schieberegler „Tageslicht im Raum“, Umschalter „Dunkle Filmszene / Helle Szene“, vier Geräte nebeneinander mit Werten für direkte Spiegelungen und Raumlicht, Hinweis „Schema nach Testerurteilen, keine Messung“. Es übersetzt eine Kennzahl in etwas Sichtbares und ist ehrlich gekennzeichnet. Übertrag (je Kategorie ein bis zwei, nur mit belegten Testwerten):

| Kategorie | Erlebnis | Datengrundlage (Beleg nötig) |
|---|---|---|
| Fernseher | Spiegelung matt/glänzend; Bildgröße aus Sitzabstand | Testerurteile Reflexion; Blickwinkelrechnung |
| Kopfhörer | ANC-Hörprobe: Umgebungsgeräusch (Bahn, Flugzeug) mit Dämpfungskurve je Modell | gemessene Dämpfung aus Tests |
| Waschmaschine | Jahreskosten-Rechner: Strom + Wasser bei deiner Haushaltsgröße | EU-Label kWh/100 Zyklen, Liter |
| Staubsauger/Roboter | Akkulaufzeit als Wohnungsplan, der sich „füllt“ | Laufzeit, Flächenleistung aus Tests |
| Air Fryer | Korbgröße mit realen Portionen (Pommes für 2/4 Personen) | Korbvolumen, Herstellerangaben |
| Smartphone | Nutzungsjahre bis Update-Ende als Zeitleiste | Update-Zusagen der Hersteller |

Keine dieser Zahlen erfinden: Wo der Beleg fehlt, bleibt die Kachel leer mit „noch keine Testdaten“.

---

## 5. Belege (Bildschirmfotos im Test, beschrieben)

1. **Kopfhörer, Empfehlungskarte (hell und dunkel):** „Unsere Empfehlung bis 350 €“, JBL Tune 770NC, darunter grau „Standard“, große „84 von 100 · sehr gut · aus Datenblatt“, Skala mit Punkt kurz vor dem schraffierten Bereich, Marken „45 60 75 85“, darunter „Ab 84 nur mit unabhängigem Test“. Darunter Hinweiskarte „Für 65 € weniger fast gleich gut (84 statt 84 Punkte)“ mit Soundcore Space One. → B01, B02, B03, B08.
2. **Kopfhörer, Rangliste:** Rang 1–3 alle 84, Sony WH-1000XM6 auf Rang 6 mit 80, Rang 12–14 „zu wenig Daten für eine Note“ (Bose QC Ultra 2. Gen., B&W Px7 S3), jede Zeile endet mit „, Standard“. → B01, B08, B10.
3. **Fernseher bis 700 €, Rangliste mit drei Haken:** Rang 2–6 fünfmal „Hisense E7S“ in verschiedenen Zoll, alle 55 „ordentlich“, 75″ für 699 € vor 43″ für 279 €; ab Zeile 4 grau „Vergleich voll (3)“; unten die Ablage „3 von 3 zum Vergleich · Leeren · Vergleichen“, die Zeile 7 halb verdeckt. → B08, B12, B13, B15.
4. **Fernseher, Vergleich:** drei Spalten (E7S PRO, E7S 75″, E7S 43″), Zeilen mit identischen Werten („LCD mit Quantum Dot“, „E“, „4K“), „HDMI 2.1: nicht angegeben“ dreimal. → B11.
5. **Waschmaschinen ohne Angaben:** „Ohne Angaben zu deiner Nutzung bewertet.“, 24 Modelle zwischen 57 und 72, Namen doppelt („Samsung WW11DB8B95GBU2, WW11DB8B95GBU2“), drei Zeilen ohne Preis „–“. → B01, B05, B08.
6. **Fuß „Wie wir bewerten“ (dunkel):** Methodentext unterhalb des Vergleichs, teilweise von der festen Ablage verdeckt. → B06, B12.
7. **Fernseher-Fragen:** „Noch 4 kurze Fragen“, erste Option jeder Frage „Egal / weiß nicht“ schwarz umrandet vorgewählt; Sitzabstand als zweite Frage, obwohl die Größe im Schritt davor gewählt wurde. → B09.
8. **Ratgeber-Fernseher:** eigener Schrittbalken „1 Bedarf · 2 Empfehlung · 3 Vergleich · 4 Details“, eigene Frage „Frage 1 von 6“, untere Reiterleiste mit vier Kategorien, oben „‹ Finden & Vergleichen“. → B07.

---

## 6. Reihenfolge der Umsetzung (Vorschlag)

1. B01–B03 Notenehrlichkeit (Wording, keine Klassen ohne Test, Gleichstand) – klein, sofort.
2. B08, B10, B15 Listenhygiene (Variante, Seriengruppen, „noch nicht bewertbar“).
3. Produktseite mit Aufschlüsselung (B04, B06) – nutzt vorhandene `beitraege`.
4. Angebotsliste (B05) – abhängig von Preisquellen (Recherche 05).
5. Fragen einzeln mit Live-Zahl, Fragen vereinheitlichen mit Ratgeber (B07, B09).
6. Erlebnis-Karten je Kategorie, sobald Testdaten belegt sind.

Offene Grenzen dieses Audits: Kein Test auf echtem Android-Gerät (Sprung zum Vergleich, B11, dort prüfen); keine Messung mit Screenreader; Kontrast nur für `--muted` gerechnet; die LDAC/iPhone-Aussage (B14) braucht einen Beleg in der Datenbank.
