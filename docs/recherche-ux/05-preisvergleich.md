# Recherche UX 05: Angebotsliste statt Bestpreis (Preisvergleich)

Stand: 24.11.2026 · Ziel: je Modell zeigen, wo man es zu welchem Preis kaufen kann.
Prüfstand: selbst gelesen (Repo-Dokumente, eigene Dateien, robots.txt-Abrufe) bzw. per Websuche/WebFetch, Quellen mit Abrufdatum 24.11.2026 · unabhängig geprüft: nein · Besitzer: Entscheidung offen. Keine Rechtsberatung. Marker: **[belegt]** = Seite gelesen, **[Suche]** = nur Suchtreffer/Drittseite, **[Vorwissen]** = nicht neu abgerufen.

## 1. Was mit dem Bestehenden sofort geht

**Befund (pilot-preise.json, Lauf 21.11.2026, 5 Modelle):** Je Modell steht schon eine Liste `angebote` (1–3 Zeilen) neben `bestpreis`; je Quelle gibt es `quellen.<id>.status` und `angebote`. Felder je Angebot: `quelle, shop, haendler, preis, versand, versand_herkunft, gesamt, link, zeit`. Das reicht für eine einfache Liste.

**Lücken in den Daten:**
- Der Finder liest nur `m.preis` (ein Händler, ein Preis, `stand`, `url`; `finder.js` Zeilen 474–500, 735 `finder-preise.json`). Eine Liste braucht ein Feld `angebote[]` je Modell in `finder-preise.json` und eine Oberfläche dafür.
- **heise liefert mehr, als gespeichert wird:** `preiswecker.auswerten` liest je Händler Artikelpreis, Versand, `gesamt` (oft `None`, wenn der Versand nicht belegt ist), Händlername, Sterne, Lieferzeit (`lieferung`) und Versandtext. Im Pilot landen davon nur wenige Zeilen in `angebote`. Die ganze heise-Händlerliste (alle Treffer im Korridor) wäre ohne neue Quelle und ohne neue Rechtsfrage speicherbar. Das ist die größte Abdeckung zum geringsten Aufwand (heise-Händler = Händler am Markt, auch Amazon, Cyberport, Coolblue).
- Es fehlen in `angebote`: **Lieferzeit/Verfügbarkeit** (bei eigener Abfrage nur als Filter `InStock`, nicht gespeichert; bei heise `lieferung` vorhanden), **Marktplatz-Kennzeichen** (eigene Abfrage schließt Marktplatz aus, heise-Händler sind teils Marktplatzhändler und nicht gekennzeichnet), **Versandstatus** „unbekannt“ (`gesamt: null`) muss sichtbar als „zzgl. Versand“ erscheinen, **Zustand** (heise filtert Neuware nicht belegt), **Stand je Zeile** (vorhanden als `zeit`).
- Die Quellen-Reihenfolge ist durch Sperren lückenhaft: Saturn/Proshop sperren Actions-IPs (O12), MediaMarkt/idealo nur Link. Eine Liste zeigt dann „bei MediaMarkt prüfen“ als Linkzeile ohne Preis (ehrlich, rechtlich unkritisch).

**Ergebnis:** Ja, „alle gefundenen Angebote statt nur das günstigste“ reicht als Stufe 1 und ist ohne neue Quelle machbar. Rechtlich ändert sich nur, dass mehr Händlerpreise stehen; die Aktualitäts- und Versandregeln (Abschnitt 4) gelten dann für jede Zeile.

## 2. Affiliate- und Partnerfeeds (Recherche)

Allgemein: Affiliate-Programme sind keine reine „Datenquelle“, sondern ein Vertrag mit Provision. Mit Links entsteht Werbekennzeichnung (Abschnitt 4), Tracking (Datenschutz) und vermutlich Impressum (O10 wird dann praktisch entschieden). Feeds sind für Preisvergleichsseiten gedacht, aber je Händler einzeln freizuschalten. Konto-Anlage entscheidet der Besitzer; hier wurde nichts angelegt.

| Option | Kosten / Voraussetzungen | Preise öffentlich anzeigen? | Aktualität | Abdeckung | Kennzeichnung, Datenschutz | Quellen |
|---|---|---|---|---|---|---|
| **Awin** (Otto, Cyberport, notebooksbilliger, Coolblue, Euronics u. a.) | 5 £-Einzahlung bei Anmeldung, wird mit erster Auszahlungsschwelle erstattet; manuelle Prüfung des Antrags inkl. Identität, Website/URLs und Beschreibung der Werbung angeben; Gewerbe nicht als formale Voraussetzung genannt **[belegt]**. Je Händler eigener Beitritt, Freigabe durch den Händler (Otto prüft Seiten, Mindestalter 18, deutsches Bankkonto, eigene Website/Newsletter) | Feeds sind dafür gedacht; Details je Händler in Programmbedingungen (nicht gelesen) | Feeds meist täglich, abrufbar über Awin; konkret je Händler **[Suche]** | Viele deutsche Händler; MediaMarkt/Saturn DE nicht gefunden (nur AT/CH) **[Suche]** | Pflicht, Affiliate-Beziehung klar zu kennzeichnen; Tracking-Links, Cookies 28–30 Tage | [Awin Beitritt](https://www.awin.com/gb/compliance-and-regulations/application-process-and-joining-fee) · [Otto FAQ](https://www.otto.de/partnerprogramm/faq/) · [Awin Publisher-Bedingungen 2025](https://awin.com/docs.awin.com/Legal/Publisher+Terms/2025/DE_Awin+AG+Publisher+terms_2025.pdf) · [Cyberport/Coolblue/nbb Suche] |
| **Tradedoubler** (Galaxus, bis 12 %) | Netzwerk-Anmeldung, Programm-ID 302027 **[Suche]** | nicht geprüft | nicht geprüft | Galaxus | wie Awin | [Galaxus](https://www.galaxus.de/en/page/become-an-affiliate-partner-17259) |
| **Adtraction, belboon, Webgains** | nicht recherchiert (Zeit); gleiche Struktur wie Awin, kleinere Händlerauswahl für Elektronik | offen | offen | offen | wie Awin | keine Quelle gelesen |
| **Amazon (PartnerNet, Creators API / PA-API)** | Konto mit endgültiger Aufnahme **und** „qualifizierte Verkäufe“ nötig; Schwelle abweichend genannt (3 Verkäufe/180 Tage laut Drittseite, 10 in 30 Tagen auf der japanischen Seite) – **nicht verbindlich geklärt**; ohne Verkäufe kein API-Zugang. Kosten laut Seite keine **[belegt: kein Preis genannt]** | Ja, aber nur über die API, mit **Zeitstempel**, wenn seltener als stündlich abgerufen, Pflichttext „Produktpreise und Verfügbarkeit entsprechen dem angegebenen Stand (Datum/Uhrzeit) und können sich ändern“, **Versandkosten deutlich nennen**, Preisvergleiche: niedrigster Neupreis, Hinweis auf möglichen Anstieg, Zeit der letzten Aktualisierung **[belegt]**. **Keine Preis-Tracking-/Preiswecker-Funktion ohne Genehmigung**, keine Aggregation/Analyse der Daten, Cache max. 24 h **[belegt]** | max. 24 h gecacht | Nur Amazon (27 von 114 Tagesbestpreisen im Verlauf, also oft der Bestpreis) | Pflichtsatz „Als Amazon-Partner verdiene ich an qualifizierten Verkäufen“ **[belegt]** | [Registrierung](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/onboarding/register-for-creators-api) · [Programmrichtlinien](https://partnernet.amazon.de/help/operating/policies) · [Vertrag](https://partnernet.amazon.de/help/operating/agreement) |
| **idealo** | Offizielles Publisher-Programm/API nicht gefunden; Drittseite nennt Pay-per-Click 14–16 ct, Widget nach Absprache **[Suche, unbestätigt]**; die idealo-API ist für Händler, nicht für Publisher **[Suche]** | nach Absprache | offen | idealo breit | wie Affiliate | [idealo Partner-API-Doku (Händler)](https://idealo.github.io/partner-web-service/docs/v2) – direkt bei idealo anfragen |
| **heise/Geizhals-Publisher** | Anfrageformular, keine Voraussetzungen genannt, Vergütung per Klick (CPC), Zugang zu ca. 3 Mio. Produkten, Lieferweg laut Seite WordPress-Plugin; API/Feed nicht belegt **[belegt: Seite unternehmen.geizhals.at/publisher]**; Kontakt bd@geizhals.at | Regeln nicht geprüft (AGB offen) | offen | Geizhals/heise-Händler (die Quelle, die wir ohnehin lesen) | CPC-Tracking | [Geizhals Publisher](https://unternehmen.geizhals.at/publisher/) |
| **Otto** | über Awin; Provision Multimedia ca. 2 %, Haushaltselektronik 7 % **[Suche]** | nicht geprüft | Feed über Awin | Otto | wie Awin | [Otto Partnerprogramm](https://www.otto.de/partnerprogramm/faq/) |
| **MediaMarkt/Saturn** | DE-Programm nicht gefunden; AT/CH laufen auf Awin, Cookies 14 Tage **[Suche]**; Drittseite nennt 5–10 % unbestätigt | offen | offen | MediaMarkt, Saturn | wie Awin | [MediaMarkt CH auf Awin](https://ui.awin.com/merchant-profile/14040) |

Fazit zu Affiliate: Kein Weg liefert „Preise vieler Shops“ kostenlos, ohne Vertrag und ohne Kennzeichnung. Die Amazon-Schnittstelle schließt den Preiswecker/Verlauf für Amazon-Daten ausdrücklich aus (Preisalarme nur mit Genehmigung), was zum bestehenden Preiswecker (D4–D6) kollidiert. Die Voraussetzung „Verkäufe schon vorhanden“ ist für eine neue App nicht erfüllbar.

## 3. Direkte Shops (robots.txt je einmal, Abruf 24.11.2026, ehrlicher User-Agent, 2 s Pause)

| Shop | robots.txt | Bewertung |
|---|---|---|
| Otto | 200; `*` sperrt nur /gate/, /onex/, /cdn-cgi/ (Produktseiten erlaubt) | erlaubt; JSON-LD nicht geprüft, Suche lieferte früher 400 (Doku 20.11.) |
| expert | 200, sehr lang (417 KB); `*` sperrt u. a. /api/ | Produktseiten vermutlich erlaubt, JSON-LD nicht geprüft |
| Euronics | 405, Seite „Human Verification“ | gesperrt, nicht umgehen |
| Cyberport | 403 „Just a moment“ (Cloudflare) | gesperrt |
| notebooksbilliger | 403 „bot detected“ | gesperrt |
| Galaxus | robots.txt 200; eine Produktseite 403 | Seite gesperrt, nicht umgehen |
| Coolblue | 403 | gesperrt |
| Lidl | 200; sperrt u. a. Suche, `*id=*`, `*sort=*` | Produktseiten ohne Query erlaubt, JSON-LD nicht geprüft |
| Kaufland | 403 „Zugriff blockiert“ | gesperrt |
| Samsung | 200; `*` erlaubt (nur Business-Suche u. ä. gesperrt) | erlaubt; Preis nicht geprüft |
| LG | 200; `*` erlaubt, Suche mit Query gesperrt | erlaubt; Preis nicht geprüft |
| Sony | 403 Access Denied | gesperrt |
| Philips | 200; sperrt nur /crsc/, /content/ | erlaubt; Preis nicht geprüft |
| Baur (zusätzlich) | 200; `*` sperrt u. a. `*.htm$`, Merkzettel | Produktseite 200, JSON-LD mit **EAN, aber ohne `offers`/Preis** (Ninja AF500EU) – für Preise unbrauchbar |

Ergebnis: Von den gewünschten Shops sind nur **Otto, expert, Lidl, Samsung, LG, Philips** per robots.txt grundsätzlich erreichbar; ob dort Preis-JSON-LD steht, wurde nicht geprüft (nur eine Produktseite je Shop war erlaubt; zum Auffinden fester URLs fehlte die erlaubte Suche, ein Pilotaufwand je Shop wäre 1–2 Stunden laut Doku 20.11.). Die „großen Preisbrecher“ (Cyberport, Coolblue, Galaxus, Amazon) sind gesperrt, also nur über Affiliate/Vergleichsportal. AGB/Nutzungsbedingungen der neuen Shops wurden **nicht** gelesen, sie wären nach der Leitregel (D7) vor Freigabe nötig.

## 4. Recht (Recherchestand, keine Rechtsberatung)

- **Preisangaben / Versand:** Wer Preise bewirbt, muss den Gesamtpreis und Liefer-/Versandkosten klar nennen oder darauf hinweisen (PAngV). Amazon verlangt dasselbe vertraglich (s. o.). [Vorwissen: PAngV §§ 3, 6; Paragrafenstand nicht neu abgerufen] Konsequenz: Zeile mit Versand oder „zzgl. Versand“, nie einen Preis ohne Versandangabe als „Gesamt“.
- **Aktualität:** BGH I ZR 123/08 „Espressomaschine“ (Preisvergleich, Preisangaben müssen aktuell sein; Hinweis auf möglichen Preisänderungen genügt nur bei klarer Erkennbarkeit des Standes) – aus eigener Doku (`recherche-eigene-preissuche.md` Abschnitt 5), hier nicht neu geprüft. Praxis: Datum/Uhrzeit je Zeile, Preise älter als ca. 36 h ausblenden oder grau mit „Stand veraltet“, Hinweis „Preise können sich seit dem Abruf geändert haben“.
- **Vergleichsportal-Pflichten (UWG § 5b):** Rangfolge und Hauptparameter der Reihenfolge angeben, entgeltliche Beeinflussung der Reihenfolge nennen, Hinweis, ob der Anbieter Unternehmer ist (Marktplatz). [Vorwissen: UWG § 5b Abs. 2–3, Nr. 6; nicht neu abgerufen] Konsequenz: „Sortiert nach Gesamtpreis (inkl. bekanntem Versand)“; wird je Affiliate-Link provisioniert, im Hinweis nennen, auch wenn die Reihenfolge davon unabhängig ist.
- **Kennzeichnung (Affiliate):** Awin verlangt klare Offenlegung der Affiliate-Beziehung (Storefront-Zusatz, sinngemäß für alle Publisher), Amazon den festen Satz „Als Amazon-Partner verdiene ich an qualifizierten Verkäufen“ **[belegt]**. Zusätzlich „Werbung“/„Anzeige“ nach UWG § 5a [Vorwissen].
- **Impressum (O10):** Mit Affiliate-Provision ist der Charakter „rein privat“ kaum noch vertretbar; Impressum/Gewerbeanmeldung sollten dann behandelt werden (Steuer/Gewerbe: Steuerberater). Awin nennt Gewerbe nicht formal als Voraussetzung **[belegt]**, Otto verlangt Prüfung der Seite **[belegt]**.
- **Datenschutz:** Tracking-Links/Cookies der Netzwerke erfordern Information in der Datenschutzerklärung; ein Redirect über das Netzwerk ist ein Auftritt Dritter. Ohne Affiliate-Links (reine Deep Links ohne Parameter) entfällt das.
- **Scraping:** Leitregel D7 bleibt (robots.txt, AGB, keine Sperren umgehen). Zusätzliche Vorsicht bei einer **Liste** statt Bestpreis: Mehr Händlerdaten pro Quelle bedeutet mehr Übernahme; nur Fakten (Preis, Händlername, Versand, Lieferzeit), keine Texte/Bilder.

## 5. Angebotsliste: was je Zeile stehen muss

Pflicht je Zeile: **Händlername** · **Artikelpreis** · **Versand** (Betrag, „kostenlos“ oder „zzgl. Versand“, mit Herkunft „laut Shop/Vergleichsportal“) · **Gesamt** (nur bei belegtem Versand, sonst Artikelpreis mit „zzgl. Versand“) · **Stand** (Datum, bei Quelle seltener als stündlich auch Uhrzeit) · **Zum Angebot**-Link (Deep Link, neues Fenster) · **Quelle** (eigene Abfrage / heise).
Sinnvoll: **Lieferzeit/Verfügbarkeit** (heise `lieferung` bzw. InStock), **Marktplatz-/Drittanbieter-Hinweis** („Verkauf durch Händler X über Plattform Y“), bei Gebrauchtware nur mit Kennzeichnung (derzeit Neuware-Filter), Händlerbewertung nur wenn belegt (heise Sterne), Hinweis „Preis kann sich seit Stand geändert haben“ einmal oberhalb der Liste.
Verhalten: Sortierung nach Gesamtpreis, Zeilen ohne Versandbeleg nach hinten oder markiert; höchstens 5 Zeilen sichtbar, Rest einklappbar; Quellen ohne freigegebene Abfrage als Linkzeile („bei MediaMarkt/idealo prüfen“) ohne Preis; leere Liste: „Kein aktueller Preis gefunden“ statt Altwert; Zeilen älter als ca. 36 h ausblenden. Barrierefreiheit: Tabelle mit Spaltenköpfen oder Liste mit sichtbarer Beschriftung je Wert, Preis nicht nur per Farbe hervorheben.

## 6. Optionen im Vergleich

| Option | Abdeckung | Aufwand | Kosten | Recht | Risiko |
|---|---|---|---|---|---|
| A. Bestehendes zeigen (eigene Shops + komplette heise-Händlerliste) | mittel bis hoch (heise-Händler inkl. Amazon, Cyberport) | gering (Daten + Oberfläche, Tests) | 0 | wie bisher, plus Aktualitätsregeln je Zeile | heise-AGB (O6) unbestätigt; Versand oft unbekannt; Händlernamen fremde Daten (nur Text ausgeben) |
| B. Weitere direkte Shops (Otto, expert, Lidl, LG, Samsung, Philips) | gering ergänzend | je Shop 1–2 h, JSON-LD offen | 0 | AGB je Shop prüfen | kann sich still ändern, Sperren aus Actions-IPs wie O12 |
| C. Awin-Konto + Händlerfeeds (Otto u. a.) | hoch für Awin-Händler, viele Preisbrecher (Cyberport, nbb, Coolblue) | mittel (Feed-Import, Freigaben je Händler) | 5 £ Einzahlung, Provision als Einnahme | Impressum, Kennzeichnung, Datenschutz, Programmbedingungen je Händler | Bewerbung kann abgelehnt werden; Feeds haben Händlerbedingungen, vor Nutzung lesen |
| D. Amazon Creators API | nur Amazon | mittel | 0, aber Verkäufe nötig | Zeitstempel, 24-h-Cache, kein Preiswecker/Alarm ohne Genehmigung | Zugang für neue Konten ohne Verkäufe unklar bis unerreichbar |
| E. idealo/Geizhals-Publisher | hoch (Vergleichsdaten) | offen, erst Anfrage | offen (CPC-Modell) | AGB offen | Konditionen unbekannt, Abhängigkeit von Dritten (Besitzerwunsch: eher Mix) |
| F. Nur Links („bei idealo/heise vergleichen“) | – | minimal | 0 | unkritisch (Deep Link, Paperboy) | keine Preise im Produkt |

## 7. Empfehlung in Stufen

**Sofort (ohne neue Entscheidung außer „Liste statt Bestpreis“):**
1. heise-Händlerliste vollständig speichern (Händler, Artikelpreis, Versand, Lieferzeit, Stand) und mit den eigenen Shopangeboten in `finder-preise.json` als `angebote[]` führen; Oberfläche mit Zeilen nach Abschnitt 5; Bestpreis bleibt als Kopfzeile.
2. Hinweistext zu Stand und Versand, Sortierkriterium, „Quelle“; Datenschutz/Impressum prüfen, ob die Seite ohne Affiliate unverändert bleibt.
3. Tests: Zeile ohne Versand, veraltete Zeile (>36 h), leerer Händlername, Marktplatzhinweis, fremde Daten nur als Text.

**Mit Besitzer-Entscheidung:**
4. O6 klären (heise-Endnutzerbedingungen; Anfrage an Geizhals bd@geizhals.at, zugleich nach Publisher-/Widget-Konditionen fragen). O12 (Saturn/Proshop und Actions-IPs) entscheiden.
5. Entscheiden, ob Affiliate gewollt ist. Wenn ja: Impressum/Datenschutz zuerst, dann Awin-Konto (5 £) und Bewerbung bei Otto/Cyberport/notebooksbilliger/Coolblue. Die Programmbedingungen je Händler (Feed-Nutzung, Preisanzeige, Kennzeichnung) vorher lesen. Wenn nein: Stufe 1 plus Stufe B.
6. B: Otto, expert, LG, Samsung, Lidl, Philips einzeln prüfen (AGB, JSON-LD, feste URL je Modell); Baur ist ungeeignet (kein `offers`).

**Später:**
7. Amazon Creators API nur, wenn ein Partnerkonto mit Verkäufen vorhanden ist; Preisalarm-Verbot beachten (Preiswecker nicht aus Amazon-API-Daten speisen).
8. idealo-Partnerkonditionen anfragen; Adtraction, belboon, Webgains und Tradedoubler erst, wenn ein Händler nur dort ist.

## 8. Lücken

- Kein Amazon-Zahlenbeleg zur Schwelle (Drittseiten widersprechen sich); idealo-Publisher-Programm nicht auffindbar; Adtraction/belboon/Webgains nicht recherchiert; MediaMarkt/Saturn DE-Programm nicht gefunden.
- JSON-LD/AGB der Shops in Abschnitt 3 wurden nicht geprüft (nur robots.txt, bei Baur und Galaxus je eine Produktseite).
- Rechtsquellen (PAngV, UWG) nicht neu abgerufen; Wortlaut bei Umsetzung am Gesetz prüfen oder fachlich prüfen lassen.
