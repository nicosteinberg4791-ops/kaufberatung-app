# Recherche: eigene Bestpreis-Suche ohne Preisvergleicher

Stand: 20.11.2026 · Auslöser: Feedback des Besitzers („Link zum besten Preis je Modell, immer aktuell; nicht heise, keine Abhängigkeit von Dritten, notfalls selbst bauen“).
Prüfstand: drei Recherche-Subagenten (Shops, Recht/Betrieb, Technik) · selbst nachgeprüft mit Python-Standardbibliothek (siehe 2.) · unabhängig: nein · Besitzer: Entscheidung offen.

## 1. Ergebnis in einem Satz

Eine eigene Preissuche ist baubar: direkt bei Shops, die ihren Preis als schema.org-Daten ausliefern, Zuordnung über die EAN, einmal am Tag. Sie findet aber nur den **günstigsten Preis unter den abfragbaren Shops**. Die Shops, die am häufigsten den Marktbestpreis stellen (Amazon, Cyberport, computeruniverse, Galaxus, Coolblue), sperren einfache Abrufe.

## 2. Selbst nachgeprüft (Python `urllib`, ein Abruf je Seite, ehrlicher User-Agent)

| Shop | Seite | Ergebnis |
|---|---|---|
| MediaMarkt | Ninja AF500EU | 200, JSON-LD: 219,99 €, EUR, InStock, NewCondition, EAN 0622356270373 |
| MediaMarkt | LG OLED65C6ELB.AEUD | 200, JSON-LD: 3.685,91 €, Versand 0, **Verkäufer JB-Vertrieb-GmbH (Marktplatz)**, EAN 8806096835395 |
| Saturn | Ninja AF500EU | 200, gleiche Daten wie MediaMarkt (gleiche Plattform) |
| Alternate | LG OLED65C6ELB.AEUD | 200, JSON-LD: 1.599 €, **Versand 69,99 €**, Verkäufer Alternate GmbH, EAN 8806096835395, MPN |
| Coolblue | Suche, robots.txt | 403 |
| Otto | Suche | 400 (robots.txt erlaubt Produktseiten für alle) |

Die EAN passt shopübergreifend (LG 65″: 8806096835395 bei MediaMarkt und Alternate). Der Abruf läuft ohne Browser. Auf der Suchseite von MediaMarkt steht auch Unpassendes, etwa eine „Bosch … AF500EU … Waschmaschine“ eines Marktplatzhändlers. Treffer zählen deshalb nur, wenn die EAN passt.

## 3. Stichprobe der Shops (Subagent, curl/WebFetch, nicht alles selbst geprüft)

- **Abfragbar** (Produktseite ohne Bot-Prüfung, Preis im JSON-LD): MediaMarkt, Saturn, Alternate, Proshop.
- **Unklar:** Otto, expert, Lidl, LG-Shop und Samsung-Shop. Dort sind die Produktseiten laut robots.txt erlaubt, Preis-JSON-LD wurde aber nicht geprüft. Berlet hat kein JSON-LD.
- **Gesperrt** (403, Cloudflare, Captcha, 503): Amazon, Cyberport, notebooksbilliger, computeruniverse, alza, Kaufland, Euronics, Galaxus, eBay-Suche, Coolblue.
- **robots.txt verbietet es:** Dyson (Produkte und Suche). Bei Saturn, expert, Galaxus, LG und Samsung ist nur die Suche gesperrt, also dort feste Produkt-URLs verwenden.

## 4. Was das für den Preis bedeutet (eigene Auswertung, preise.json 08.–16.11.2026)

- Im heise-Verlauf gibt es 114 Tagesbestpreise über alle 24 Modelle. Davon stellte **Amazon 27**, Cyberport 8, Galaxus 8, computeruniverse 6 und Coolblue 5. Von den sicher abfragbaren Shops war nur Saturn dabei, mit 6 Tagen (etwa 5 %). Dazu kommen viele kleine Händler, die man ohne Vergleichsportal gar nicht findet (deltatecc-home 13, Future-X, EDV-Service).
- Zwei Beispiele vom 16. bzw. 20.11.: LG OLED65C6ELB eigene Suche 1.599 € + 69,99 € Versand (Alternate), heise-Bestpreis 1.349 € (Cyberport). Ninja AF500EU eigene Suche 219,99 € (MediaMarkt/Saturn), heise-Bestpreis 169 € (Coolblue).
- Ehrliche Anzeige deshalb: „Günstigster Preis bei den geprüften Shops (MediaMarkt, Saturn, Alternate, Proshop …)“, nicht „Bestpreis am Markt“.

## 5. Recht und Betrieb (Recherchestand, keine Rechtsberatung)

- Öffentlich sichtbare Preise automatisch zu lesen, ist nach BGH I ZR 224/12 („Flugvermittlung“) nicht von sich aus unlauter. Verboten ist das Überwinden technischer Schutzmaßnahmen. Daraus folgt: Bot-Prüfungen nie umgehen, robots.txt beachten, nur Fakten übernehmen (Preis, Lieferbarkeit), keine Texte und Bilder.
- Deep Links auf Produktseiten sind zulässig (BGH I ZR 259/00 „Paperboy“).
- Aktualität: Für Preissuchmaschinen gelten strenge Maßstäbe (BGH I ZR 123/08 „Espressomaschine“), ein „ohne Gewähr“ allein schützt nicht. Daraus folgt: Zu jedem Preis Uhrzeit und Shop zeigen, Preise älter als etwa 36 Stunden ausblenden und den Versand nennen, falls bekannt.
- Impressum (§ 5 DDG): Eine rein private Seite ist ausgenommen, die Abgrenzung ist aber unscharf. Ohne Affiliate-Links ist der private Charakter eher gegeben. Offen, gegebenenfalls fachlich prüfen lassen.
- GitHub Actions: Die Nutzungsbedingungen verbieten „excessive bulk activity“. Etwa 100–200 Abrufe am Tag liegen weit darunter. **Offen:** Shops sperren Rechenzentrums-IPs (Azure) teils strenger als Heimanschlüsse. Das klärt nur ein Testlauf in Actions.
- Offizielle Schnittstellen passen nicht: Amazon Creators API braucht ein Partnerkonto mit Verkäufen. Die eBay Buy API ist nur für Partner gedacht und eBay ist ein Marktplatz. Awin-Feeds (Otto u. a.) wären wieder ein Dritter mit Affiliate-Vertrag.
- Live-Abruf in der App beim Öffnen geht nicht: Shops senden keine CORS-Freigabe, ein eigener Proxy wäre Betrieb und Abhängigkeit. „Immer aktuell“ heißt deshalb: täglich (oder mehrmals täglich) frisch, mit Uhrzeit.

## 6. Vorgeschlagene Architektur (falls der Besitzer zustimmt)

1. `daten/modelle.json` (gepflegt): je Modell `id`, `name`, `kategorie`, `eans[]`, `mpn[]`, Preiskorridor sowie je Shop die feste Produkt-URL. Die URL wird einmal über die erlaubte Shopsuche gefunden oder von Hand eingetragen.
2. `daten/shops.json`: Name, Domain, Datum der robots.txt-Prüfung, Versandregel als Rückfall (z. B. „frei ab X €“, mit Quelle) und ob es ein Marktplatz ist.
3. Täglicher Lauf in Actions: je URL ein GET, 3 s Pause je Shop, Timeout, höchstens eine Wiederholung. Bei 403, Captcha oder Challenge wird der Shop für diesen Lauf als „nicht abrufbar“ markiert, nie umgangen.
4. Parser (Standardbibliothek): alle JSON-LD-Blöcke lesen, rekursiv nach `Product` suchen (MediaMarkt verschachtelt BuyAction → ProductGroup → Product) und `offers` normalisieren.
5. Regeln für ein gültiges Angebot:
   - EAN passt
   - `NewCondition` (oder die Angabe fehlt)
   - `InStock`
   - EUR
   - Preis im Korridor
   - Verkäufer ist der Shop selbst, kein Marktplatzhändler
6. Gesamtpreis = Preis + Versand. Der Versand kommt aus dem JSON-LD oder der Shopregel, sonst steht „zzgl. Versand“. Die Herkunft des Versands wird mitgespeichert.
7. In `preise.json` bekommt jedes Modell den besten Shop (Preis, Versand, Link, Zeit), die anderen geprüften Shops und einen Status je Shop.
8. Anzeige im Inhalt bei jedem Modell, zum Beispiel: „1.668,99 € bei Alternate (inkl. 69,99 € Versand) · heute 06:30 · Zum Angebot“, aufklappbar mit allen geprüften Shops.
9. Pflegeaufwand: etwa 10–20 Minuten je neuem Modell (EAN, 3–5 URLs), etwa 1–2 Stunden je neuem Shop (robots.txt, Test, Versandregel).

## 7. Offene Entscheidungen des Besitzers

1. Ist „günstigster Preis bei den abfragbaren Shops“ (oft 15–25 % über dem Marktbestpreis, siehe 4.) als Ergebnis akzeptabel?
2. heise-Abfrage: sofort ersetzen oder bis zum Nachweis der eigenen Suche parallel weiterlaufen lassen? Der Preiswecker, der Verlauf und die Push-Meldungen hängen heute daran.
3. Testlauf in GitHub Actions: Das braucht einen Push eines Test-Workflows ins öffentliche Repo und damit eine Freigabe.
4. Umfang des Pilots: Vorschlag 5 Modelle (je Kategorie 1–2) × MediaMarkt, Saturn, Alternate, Proshop, Trefferquote über 3–5 Tage messen.

## 8. Beschluss 20.11.2026 und Bauplan Pilot

Besitzer: „Pilot bauen, Mix aus heise, idealo und Selbstabfrage, damit wir alle Shops **legal** reinbekommen, ohne gegen geltendes Recht zu verstoßen.“ (ersetzt die frühere Vorgabe „nicht heise“)

**Leitregel (Quellenfreigabe):** Jede Quelle (Shop, heise, idealo) wird erst nach dokumentierter Prüfung automatisch abgefragt. Die Prüfung umfasst:
- robots.txt für die genutzten Pfade
- Nutzungsbedingungen bzw. AGB (Klausel zum automatischen Abruf)
- keine technische Schutzmaßnahme im Weg (403, Captcha oder Challenge bedeuten: Quelle nicht nutzen, nie umgehen)

Ergebnis und Datum stehen je Quelle in `daten/quellen.json`. Eine nicht freigegebene Quelle erscheint nur als normaler Link (z. B. „bei idealo vergleichen“); Deep Links sind zulässig, siehe 5. Für heise ist O6 (Nutzungsbedingungen) damit Teil des Piloten. Bei idealo sind die Bedingungen noch **nicht geprüft**; nichts davon annehmen.

**Pilot (Umfang):** Die Modelle stehen noch nicht fest. Vorschlag: 5 Modelle, zum Beispiel LG OLED65C6ELB, Samsung GQ65S90H, Ninja AF500EU, einen empfohlenen Akkusauger und das Samsung Galaxy S26. Bei Bosch/Dyson-Saugern den Hersteller-Shop wegen robots.txt nicht abfragen. Quellen: MediaMarkt, Saturn, Alternate, Proshop (eigene Abfrage), dazu heise und idealo, falls freigegeben.

**Bauteile:**
1. `daten/quellen.json` (Freigabe je Quelle, Versandregel als Rückfall mit Beleg)
2. `daten/pilot_modelle.json` (je Modell: EANs, MPN, Preiskorridor und je Shop die feste Produkt-URL)
3. `werkzeuge/shopabfrage.py` (nur Standardbibliothek): JSON-LD rekursiv lesen, Regeln aus 6., `itemCondition`, Verkäufer gleich Shop, EAN-Abgleich. Je Angebot werden `quelle` (eigen/heise/idealo), `haendler`, `preis`, `versand`, `versand_herkunft`, `link` und `zeit` gespeichert.
4. Zusammenführung: Bestpreis = günstigstes gültiges Angebot über alle freigegebenen Quellen, ohne Dubletten (gleicher Händler, gleicher Preis). Bei heise/idealo-Treffern führt der Link auf deren Seite, nicht auf eine Weiterleitung hinter einer Bot-Prüfung.
5. Ausgabe zunächst getrennt als `pilot-preise.json`, ohne Wirkung auf die live genutzte `preise.json`, den Preiswecker und Push.
6. Tests (`tests/test_shopabfrage.py`) mit gespeicherten Seiten als Vorlage (die Proben MediaMarkt, Saturn und Alternate aus 2. neu speichern)
7. Testlauf in GitHub Actions (eigener Workflow, nur `workflow_dispatch`, Ergebnis als Actions-Artefakt). Das braucht einen Push auf `main` und damit eine Freigabe des Besitzers.
8. Messen über 3–5 Tage: Trefferquote je Quelle, Abweichung zum Marktbestpreis, Sperren aus Actions-IPs.
9. Erst danach: Anzeige im Inhalt (Artifact-Projekt), Codex-Prüfung, Entscheidung über das Ersetzen von `preise.json`.
