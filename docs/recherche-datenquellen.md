# Recherche: Datenquellen für vollständige Modelllisten und Datenblattwerte

Stand: 21.11.2026 · Ergänzt `docs/recherche-eigene-preissuche.md` (Shops, Preise, Sperren; dort Gesagtes wird hier nicht wiederholt).
Prüfstand: selbst recherchiert und mit `curl` und Python-Standardbibliothek nachgeprüft (nur GET, kein Konto, kein Formular) · unabhängig: nein · Besitzer: Entscheidung offen. Keine Rechtsberatung.

Alle Zitate wurden am 21.11.2026 gelesen. Sie stehen im Original, gekürzt auf höchstens 15 Wörter.

## Ergebnis in drei Sätzen

1. Eine einzige kostenlose Quelle für **alle** in Deutschland verkauften Modelle **aller 13 Kategorien** gibt es nicht.
2. Für **TV, Smartphones/Tablets, Waschmaschinen, Trockner, Kühlgeräte und Geschirrspüler** ist die EU-Datenbank **EPREL** die beste Quelle: amtlich, vollständig für den EU-Markt (Registrierung ist Pflicht), mit Marktstart- und Marktende-Datum und Weiterverwendung in Vergleichs-Apps ausdrücklich erlaubt. Die Modellliste braucht aber einen API-Schlüssel, den nur der Besitzer mit digital signierter Erklärung beantragen kann.
3. Für **Akku-Sauger, Saugroboter, Air Fryer, Laptops, Kopfhörer und Soundbars** gibt es kein Pflichtregister. Dort bleiben nur Shop-Kategorieseiten (Saturn liefert eine schema.org-`ItemList`) zum Finden der Modelle, Hersteller- und Shop-Produktseiten für die Werte, Open Icecat nur bei Sponsor-Marken und nur mit Konto.

## 1. EPREL (EU-Produktdatenbank für das Energielabel)

### Zugang

- **Es gibt eine öffentliche API.** Laut Text der EPREL-Webanwendung (`https://eprel.ec.europa.eu/assets/i18n/en.json`, Schlüssel `page.public-api-key.information`): „An API key is required when calling the Public API for searching and retrieving models.“
- **So bekommt man den Schlüssel** (Seite „Request Public API Key“, `https://eprel.ec.europa.eu/screen/requestpublicapikey`, Texte aus derselben Datei):
  1. Formular ausfüllen: Antragsteller, E-Mail, Anwendungs-URL, Zweck der Datennutzung.
  2. Die erzeugte „EPREL Declaration“ (PDF) herunterladen.
  3. Das PDF elektronisch siegeln oder digital signieren.
  4. Das signierte PDF über den Link aus der E-Mail hochladen.
  - Kosten werden nirgends genannt, und ein Entgelt ist nirgends erwähnt. Dass der Schlüssel kostenlos ist, gilt damit als **wahrscheinlich, aber nicht ausdrücklich belegt**.
- **Widerspruch bei der Signatur:** Ein Hinweistext sagt „This signature or seal can be of type 'Simple'“. Der Tooltip für Privatpersonen verlangt dagegen „a qualified electronic signature of the below declared individual“. Was wirklich verlangt wird, klärt erst der Antrag. Eine qualifizierte Signatur geht in Deutschland z. B. mit Personalausweis und Signatur-App, ist aber **nicht immer kostenlos** (Lücke).
- **Selbst getestet** (GET, ehrlicher User-Agent, ohne Schlüssel):

| Endpunkt | Ergebnis |
|---|---|
| `https://eprel.ec.europa.eu/api/product-groups` | 200, Liste aller Produktgruppen (s. u.) |
| `https://eprel.ec.europa.eu/api/products/electronicdisplays?_page=1&_limit=1` (Modellliste) | **403** `{"message":"Forbidden"}` |
| `https://eprel.ec.europa.eu/api/products/smartphonestablets20231669?_page=1&_limit=1` | **403** |
| `https://eprel.ec.europa.eu/api/products/smartphonestablets20231669/2179652` (ein Modell, Nummer aus dem QR-Code) | **200**, voller Datensatz |
| `https://eprel.ec.europa.eu/api/products/electronicdisplays/1876823` (ein TV) | **200**, voller Datensatz |

  Daraus folgt: Einzelne Modelle sind über die Registriernummer (aus dem QR-Code des Labels) ohne Schlüssel abrufbar. Diesen Weg nutzt auch die öffentliche Webseite. Für die **vollständige Liste** braucht man den Schlüssel. Die 403 ist eine Zugangssperre und wird nicht umgangen.
- **Ratenlimits:** Weder in den Nutzungsbedingungen noch in der Oberfläche gefunden (**Lücke**). Ein Supplier-Leitfaden von 2024 (Fremdkopie, `inza.blog/.../eprel-user-guide-suppliers-v1.35-manual-2024.pdf`) nennt laut Suchauszug „whitelisted access token“ für Massenabrufe. Das ist nicht selbst gelesen.
- **Verfügbarkeit:** In den Nutzungsbedingungen Art. 6 § 6 steht „strive to maintain 95% of availability“. Das ist nur eine Bemühenszusage.

### Nutzungsbedingungen (Lizenz)

Quelle: `https://ec.europa.eu/assets/move-ener/eprel/EPREL%20Public/Public%20API%20Term%20and%20Conditions/API_TERMS_AND_CONDITIONS_EN.pdf`. Gültig seit 3.6.2024, PDF zuletzt geändert am 6.10.2026. Text mit pypdf ausgelesen.

- **Erlaubt** (Art. 4 § 1):
  - „to reproduce, share and distribute the Data for commercial and non-commercial purposes“
  - „to implement the Data in mobile applications and other comparison tools“
- **Verboten** (Art. 4 § 2):
  - die Rohdaten als solche verkaufen
  - Daten so verändern oder zusammenfassen, dass sie irreführen
  - den Eindruck einer Billigung durch EPREL erwecken
  - **(f)** lokal gespeicherte Daten nicht aktuell halten
- **Für die App relevant:**
  - Pflicht zur Aktualisierung: „fail to ensure that the Data is kept up to date“ ist verboten. Ein regelmäßiger Lauf ist also Pflicht, Änderungen und Löschungen müssen nachgezogen werden.
  - Quellenangabe: „you must preserve all credit and attribution“ (Art. 4 § 3). In der App etwa „Quelle: EU-Datenbank EPREL“ mit Link.
  - Kündigung jederzeit ohne Grund möglich (Art. 5 § 2). Die API kann geändert oder abgeschaltet werden (Art. 6 § 2).
  - Datenqualität: Die Angaben stammen von den Herstellern, ohne Gewähr (Art. 7).

### Produktgruppen

Laut `/api/product-groups`, am 21.11.2026 abgerufen:

| Kategorie der App | EPREL-Gruppe (`url_code`) | Verordnung |
|---|---|---|
| Fernseher | `electronicdisplays` | (EU) 2019/2013 |
| Smartphones, Tablets | `smartphonestablets20231669` | (EU) 2023/1669 |
| Waschmaschinen | `washingmachines2019` (Waschtrockner: `washerdriers2019`) | (EU) 2019/2014 |
| Trockner | `tumbledryers20232534` | (EU) 2023/2534 |
| Kühlschränke | `refrigeratingappliances2019` | (EU) 2019/2016 |
| Geschirrspüler | `dishwashers2019` | (EU) 2019/2017 |
| Akku-Sauger, Saugroboter | **keine** | Das Label für Staubsauger wurde vom EuG gekippt. Eine neue Verordnung ist im Entwurf, Annahme laut BRC-Übersicht frühestens 2026–2028, **nicht** als verabschiedet belegt. |
| Air Fryer, Laptops, Kopfhörer, Soundbars | **keine** | kein Energielabel |

Hinweis: In der Liste stehen auch die alten Gruppen `televisions`, `washingmachines` u. a. aus den Verordnungen vor 2021. Für aktuelle Modelle gelten nur die Gruppen der Tabelle.

### Felder (selbst abgerufen, Beispieldatensätze)

- **Fernseher** (Reg.-Nr. 1876823, TCL):
  - Kennung und Kategorie: `supplierOrTrademark`, `modelIdentifier` („75P79BX1“), `category` (TELEVISION)
  - Bildschirm: `diagonalInch`, `diagonalCm`, `resolutionHorizontalPixels`/`resolutionVerticalPixels`, `panelTechnology` (z. B. LED_LCD), `frequencyRate`
  - Energie: `energyClass`, `energyClassSDR`, `energyClassHDR`, `powerOnModeSDR`/`powerOnModeHDR` (W), `powerStandby`, `powerStandbyNetworked`
  - Ausstattung: `autoBrightnessControlAvailable`, `voiceAvailable`
  - Unterstützung: `minAvailabilitySoftwareUpdatesYears`, `minAvailabilitySparePartsYears`, `minGuaranteedSupportYears`
  - **Fehlt:** die HDR-Formate (Dolby Vision, HDR10+) und Gaming-Angaben wie HDMI 2.1. Es gibt nur die Energieklasse im HDR-Betrieb.
- **Smartphone** (Reg.-Nr. 2179652, Nothing):
  - Kennung und Gerät: `modelIdentifier` („A059“), `deviceType`, `operatingSystem`, `isFoldable`
  - Energie und Akku: `energyClass`, `batteryEndurancePerCycleInHours`, `batteryEnduranceInCycles`, `ratedBatteryCapacity` (mAh), `batteryUserReplaceable`
  - Haltbarkeit: `repeatedFreeFallReliabilityClass`, `fallsWithoutDefect`, `ingressProtectionRating`
  - Reparierbarkeit: `repairabilityClass`, `repairabilityIndex`
  - Unterstützung: `minYearsSoftwareUpdates`, `guaranteeDuration`
  - Laden: `chargerRequiredOutputPower`
- **Bei beiden:**
  - Marktdaten: `onMarketStartDate`, `onMarketFirstStartDate`, `onMarketEndDate` (Marktstart und -ende), `firstPublicationDate`
  - Verfügbarkeit: `availabilityInEUEEACountries` bzw. `modelAvailabilityInEUEEACountries`
  - Weiteres: `eprelRegistrationNumber`, `status`, `lastVersion`
- **Waschmaschinen, Trockner, Kühlgeräte, Geschirrspüler:** Feldnamen **nicht abgerufen** (keine Registriernummer zur Hand). Laut den Label-Verordnungen enthalten sie mindestens Energieklasse, Verbrauch, Kapazität bzw. Volumen, Programmdauer und Geräuschklasse.
- **Wichtige Lücke:**
  - **Kein Handelsname und keine EAN/GTIN im Datensatz.** Das Smartphone heißt dort „A059“, nicht „Nothing Phone (…)“, der TV „75P79BX1“. Die Zuordnung zu Shop-Angeboten muss über Marke und Modellkennung (MPN) laufen und braucht teils Pflege von Hand.
  - Die Kennungen weichen von den Shopbezeichnungen ab, z. B. ein Ländersuffix wie „…BX1“.

## 2. Open Icecat

- **Kostenlos, aber mit Konto.** Open Content License (`https://iceclog.com/open-content-license/`, „Version 1.4, February 11, 2026“), Ziffer 7: „you will register for a free Open Icecat account“. **Das Konto müsste der Besitzer anlegen.**
- **Lizenz:**
  - Copyright- bzw. Datenbankvermerk auf jeder Kopie (Ziffer 1).
  - Kein Entgelt für den Zugang zu den Inhalten (Ziffer 1).
  - Kein Einsatz für KI-Training (Ziffer 10).
  - robots.txt einhalten (Fair-Use-Policy, `https://iceclog.com/open-icecat-fair-use-policy/amp/`: „Compliance with the directives in Icecat's robots.txt file is a mandatory condition“).
  - Grenze: „more than 1 million data-sheet downloads per month“ gilt als übermäßig.
  - Eine kostenlose öffentliche Nicht-Affiliate-App ist damit **grundsätzlich vereinbar**.
- **Abdeckung:** nur Marken, die Open Icecat **sponsern**. Laut Icecat-Vergleichsseite (`https://icecat.com/full-icecat-upgrade/`) sind das „400+ Sponsor Brands“, die volle Datenbank kostet Geld.
  - Belegte Sponsoren laut Icecat-Blog: u. a. HP, Sony, Microsoft, Tefal, Whirlpool, Intel, BenQ.
  - **Nicht belegt** für Samsung, LG, Apple, Dyson, Bosch, Ninja.
  - Daraus folgt: Laptops (HP) und Teile von Kopfhörer und Soundbar (Sony) sind brauchbar. Für Air Fryer, Sauger und die großen TV- und Smartphone-Marken ist es **unsicher bis unbrauchbar**.
  - Bilder: Rechte je Marke eingeschränkt, Bilder deshalb nicht übernehmen.
- **Massenabruf:** In den Nutzungsbedingungen für Nutzer steht laut Suchauszug „automated access … via its documented APIs is granted“. Die Indexdateien je Sprache sind dokumentiert (OCI-Handbuch). Nicht selbst geprüft, weil `icecat.biz` hinter einer Bot-Prüfung (Anubis) liegt. Gemäß unserer Regel wurde sie nicht umgangen.

## 3. Kategorieseiten und Sitemaps der freigegebenen Shops

### robots.txt (selbst abgerufen 21.11.2026)

| Shop | Kategorie- und Listenseiten | Sitemaps |
|---|---|---|
| Saturn | Erlaubt für `User-agent: *`: `/de/category/…` ist nicht gesperrt. Gesperrt sind u. a. `*de/search`, `*de/list/*_*`, `*de/promo-list/*`, `/*storeId=*`. | `sitemap-index.xml` mit 159 Produkt-Sitemaps zu je 10.000 URLs (etwa 1,6 Mio. Produkte, **ohne Kategorie in der URL, ohne lastmod**), dazu `sitemap-productlistpages.xml` (Kategorien) |
| Alternate | Erlaubt (gesperrt nur `*.json`, `*.pdf`, `/rest/`, Formulare) | `sitemap.xml.gz` → `sitemap_article1/2`, `sitemap_listings1` (lastmod 2026-11-21) |
| Proshop | Erlaubt, aber `Disallow: /*?*` mit Ausnahmen `Allow: /*?pn=` (Blättern) und `/?s=` | `sitemap.xml` → `sitemap1…n.xml` |

- **Selbst getestet:** Saturn `https://www.saturn.de/de/category/4k-fernseher-2301.html` liefert 200 und ein JSON-LD `ItemList`. Darin stehen 12 Produkte je Seite mit Name, Preis, Bewertung und URL, insgesamt „1197 Artikel“, also etwa 100 Seiten über `?page=N`. **Datenblattwerte stehen dort nicht** (nur im Namen, z. B. „65 Zoll / 165 cm, OLED 4K“). Die Kategorieseiten von Alternate und Proshop wurden nicht geprüft (**Lücke**).
- **Nutzen:** Kategorieseiten eignen sich, um **neue Modelle zu entdecken**, nicht als vollständige Quelle für Datenblätter. Darin stehen auch Marktplatz- und Zubehörangebote.

### Recht: Datenbankherstellerrecht (§§ 87a/87b UrhG)

- Ein Shopkatalog ist sehr wahrscheinlich eine geschützte Datenbank (wesentliche Investition).
- Verboten ist das Entnehmen oder Weiterverwenden eines **wesentlichen Teils**. Auch **wiederholte und systematische** Entnahmen unwesentlicher Teile sind verboten, wenn sie der normalen Auswertung zuwiderlaufen (§ 87b Abs. 1 S. 2).
- **EuGH C-762/19 „CV-Online Latvia“ (3.6.2021):** Ein Verstoß setzt voraus, dass die Entnahme die Investition des Herstellers gefährdet. Bird & Bird fasst zusammen: Ein wesentlicher Teil ohne Nachteil für die Investition „will not be considered an infringement“ (`https://www.twobirds.com/en/insights/2021/global/database-rights-infringement-by-reutilisation-and-extraction`).
- **BGH I ZR 159/10 „Automobil-Onlinebörse“ (22.6.2011):** Die Summe einzeln unwesentlicher Entnahmen kann einen wesentlichen Teil ergeben (Leitsatz laut Betriebs-Berater). Volltext nicht selbst gelesen.
- **EuGH C-30/14 „Ryanair“ (15.1.2015):** Ist eine Datenbank **nicht** geschützt, darf der Betreiber die Nutzung per AGB vertraglich beschränken. Die AGB bleiben also auch dann maßgeblich. Hier aus dem Fachwissen, am 21.11. nicht neu nachgelesen.
- **Einschätzung für einen sicheren Umfang:**
  1. Nur Fakten übernehmen (Modell, Preis, Link, Lieferbarkeit), keine Texte und Bilder.
  2. Kein Spiegeln ganzer Kategorien mit Datenblättern.
  3. Kategorieseiten höchstens wöchentlich und nur zum Entdecken lesen. Gespeichert werden nur Name, URL und MPN, und nur von Modellen, die in die kuratierte Liste aufgenommen werden.
  4. Täglich nur die Produktseiten der kuratierten Modelle abrufen (Größenordnung 100–300 am Tag).
  5. Jedes Angebot verlinkt auf den Shop. Das lenkt Kunden zum Shop und gefährdet dessen Investition nicht, was im Sinne von CV-Online spricht.
  6. Datenblattwerte vorrangig aus EPREL oder vom Hersteller, nicht aus dem Shopkatalog.
  7. AGB-Stand je Shop in `daten/quellen.json` dokumentieren.
  - Ein Restrisiko bleibt, weil zu „wöchentlich ganze Kategorie“ keine Rechtsprechung gefunden wurde.

## 4. Weitere Quellen (kurz)

- **Herstellerseiten und Presse-Datenblätter:** Am verlässlichsten für Werte, die EPREL nicht hat (HDR-Formate, HDMI, Saugleistung, Korbvolumen, Akkulaufzeit bei Kopfhörern). Fakten sind nicht urheberrechtlich geschützt, Texte und Bilder schon. robots.txt je Hersteller prüfen (Dyson sperrt laut früherer Recherche Produktseiten). Kein einheitliches Format, deshalb Pflege von Hand oder ein Parser je Hersteller. Realistisch für die kuratierte Liste.
- **Wikidata:** Lizenz CC0, Abfrage frei. Selbst getestet: Nur **11** Einträge vom Typ „Smartphonemodell“ (Q19723451) haben ein Veröffentlichungsdatum ab 2025. Für Vollständigkeit unbrauchbar, höchstens für Zusatzangaben wie Marketingname oder Erscheinungsjahr.
- **GS1 („Verified by GS1“):** liefert zur GTIN Firma und Basisangaben, keine Datenblattwerte. Laut GS1-Support sind es „up to 30 single GTIN queries in any 24-hour period“ (`https://support.gs1.org/support/solutions/articles/43000734075`). Nur zum Prüfen einer EAN, nicht als Katalog.
- **Stiftung Warentest:** Die Noten sind geschützt. test.de (`https://www.test.de/presse/rechtliches-5041757-0/`) sagt „grundsätzlich nur mit unserer Zustimmung zulässig“, das Bündeln von Ergebnissen aus mehreren Tests ist ausdrücklich ausgeschlossen. Ein Link aufs Thema ist ohne Genehmigung erlaubt. **Daraus folgt: keine Noten übernehmen, nur „Test bei test.de“ verlinken.**
- **RTINGS:** Die vollen Testergebnisse liegen seit 2025 hinter einer Mitgliedschaft, ausdrücklich gegen Scraping (`https://rtings.com/company/revamping-our-membership-program`, laut Suchauszug). Den Text der Nutzungsbedingungen (`/company/terms-of-use`) konnte das Werkzeug nicht lesen (**Lücke**). **Nicht automatisch nutzen**, nur verlinken.

## 5. Empfehlung je Kategorie

Legende Risiko: R = rechtlich, T = technisch, A = Ausfall.

| Kategorie | (a) Modellliste | (b) Datenblattwerte | (c) Preis + Link | Risiko | Besitzer muss |
|---|---|---|---|---|---|
| Fernseher | EPREL `electronicdisplays` (Filter TELEVISION, Marktende leer oder in der Zukunft) | EPREL (Diagonale, Auflösung, Panel, Energie SDR/HDR, Hz), Rest (HDR-Formate, HDMI 2.1) vom Hersteller | Shop-Produktseiten (Saturn, Alternate, Proshop) + heise/idealo laut Pilot | R gering · T mittel (Zuordnung MPN↔EPREL, Marketplace) · A mittel (EPREL-Schlüssel kündbar) | EPREL-API-Schlüssel beantragen (signierte Erklärung) |
| Smartphones, Tablets | EPREL `smartphonestablets20231669` (seit 20.6.2025 Pflicht) | EPREL (Akku h/Zyklen, Falltest, IP, Reparierbarkeit, Updates), Rest (SoC, Speicher, Kamera) vom Hersteller | wie oben | R gering · T hoch (kein Handelsname: „A059“) · A mittel | wie oben |
| Waschmaschinen | EPREL `washingmachines2019` | EPREL | wie oben | R gering · T mittel · A mittel | wie oben |
| Trockner | EPREL `tumbledryers20232534` | EPREL | wie oben | wie oben | wie oben |
| Kühlschränke | EPREL `refrigeratingappliances2019` | EPREL | wie oben | wie oben | wie oben |
| Geschirrspüler | EPREL `dishwashers2019` | EPREL | wie oben | wie oben | wie oben |
| Akku-Sauger, Saugroboter | keine vollständige Quelle; Saturn-Kategorie-`ItemList` wöchentlich zum Entdecken, dann kuratieren | Hersteller-Datenblatt von Hand (Dyson: robots.txt beachten) | Shop-Produktseiten + heise/idealo | R mittel (§ 87b bei Kategorieabruf) · T mittel · A mittel | Umfang der Kategorieabrufe freigeben |
| Air Fryer | wie Sauger | Hersteller (Volumen, Leistung) von Hand | wie oben | wie Sauger | wie Sauger |
| Laptops | Saturn-/Alternate-Kategorien zum Entdecken | Open Icecat (HP, Lenovo u. a. nur falls Sponsor) + Hersteller | wie oben | R gering bis mittel · T hoch (Konfigurationsvielfalt) · A gering | Open-Icecat-Konto anlegen (kostenlos) |
| Kopfhörer, Soundbars | Kategorien zum Entdecken | Open Icecat (Sony belegt) + Hersteller | wie oben | wie Laptops | wie Laptops |

Leitlinie: „Alle Modelle“ geht verlässlich nur in den sechs EPREL-Kategorien. In den anderen sechs ist es eine kuratierte Auswahl, ergänzt durch eine wöchentliche Meldung „neue Modelle in Kategorie X entdeckt“ zur Prüfung von Hand.

## Lücken und Risiken

1. **EPREL-Schlüssel:** Die Beantragung verlangt eine digital signierte Erklärung mit Name und E-Mail (die Angaben zur Signaturstufe widersprechen sich, qualifiziert kann kosten). Ratenlimits sind unbekannt, der Zugang ist jederzeit kündbar. Daten müssen laut Bedingungen aktuell gehalten werden.
2. **Zuordnung:** EPREL enthält keinen Handelsnamen und keine EAN. Die Verbindung zu Shop-Angeboten (EAN-basiert) braucht Marke und Modellkennung (MPN) und teils Pflege von Hand. Ohne Schlüssel ist sie nicht im Großen testbar.
3. **Sechs Kategorien ohne Register:** Sauger, Air Fryer, Laptops, Kopfhörer und Soundbars haben keine legale, kostenlose und vollständige Quelle. Shop-Kategorieabrufe tragen ein Restrisiko nach § 87b UrhG, Open Icecat deckt nur Sponsor-Marken ab und braucht ein Konto.
