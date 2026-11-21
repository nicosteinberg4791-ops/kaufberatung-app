# Stand – Kaufberatung-App

Stand: 20.11.2026 · `main` ab7e705 (Doku-Änderungen unten nicht committet) auf `github.com/<konto>/kaufberatung-app` (öffentlich), Pages aus `gh-pages`. Veröffentlicht: App 090ac453670e, Inhalt Artifact-Version 30. Neu: Recherche Bestpreis-Link (D7) und Pilot lokal (21.11.2026), Prüfstand selbst geprüft · unabhängig nein · Besitzer: Pilot beauftragt, Push (O9) offen.

## Finder „Finden & Vergleichen“ (Zweig `datenbank`, 21.11.2026)

Neue Startseite mit Preisrahmen, Aufpreis-/Spar-Hinweis und Produktdatenbank (14 Kategorien, 278 Modelle). Stand c20480f, selbst geprüft (datenbank.py 0 Fehler, node --test 30/30), unabhängig nein, noch nicht eingebaut und nicht live. Übergabe, Entscheidungen D8–D11, offene Punkte O11–O13 und nächste Schritte: `docs/uebergabe-finder.md`.

## „Für alle“ (seit Artifact-Version 28 veröffentlicht)

- App-Hülle: Besitzerfunktionen (Wunschpreise, Treffer-Karte, „Push einrichten“, Hintergrundprüfung) nur mit lokalem Merker `kb-app:besitzer` (`app/app.js`); ohne Merker `isOwner()` = false, Wunschpreise unsichtbar und nicht setzbar. Sichtbarkeit, keine Sicherheit. Secret-Link aus der Pages-Adresse abgeleitet, keine Konto-URL im Code.
- Benachrichtigungen neutral; Repo ohne Namen, Pfade, Konto-URLs (Platzhalter `<konto>` usw.).
- Inhalt (`quelle/`, `dist/`) kommt aus dem Artifact-Bau (zuletzt Version 30). Ohne Besitzer zeigt der Preiswecker der Seite je Zeile „kein Wunschpreis“ (Seiteninhalt, nicht Hülle). Geprüft: Codex (V28, V29 und V30 bestanden), `pruefe.mjs --url` live ohne Meldungen und ohne Tippziele unter 44 px.

## Ablauf und Werkzeuge

- **Inhalt nachziehen:** `Artifact read` → `werkzeuge/app_bauen.py --quelle <datei>` → `tests/alle-tests.ps1` → `werkzeuge/browserpruefung/pruefe.mjs` (lokal und `--url`) → `werkzeuge/veroeffentlichen.py` (nur mit Auftrag).
- **Tägliche Preisabfrage** (O1/O2): `.github/workflows/preise.yml`, Hauptlauf 05:23 UTC plus Nachläufe, bis 01.12.2026. Ablauf: Secret prüfen → `preise_aktualisieren.py --meldung` → ntfy → Web Push → `--nur-push` (nur preise.json auf gh-pages). Je Lauf höchstens 16 heise-Anfragen (`ABRUF_JE_LAUF`), älteste Preise zuerst, Rest „Folgt im nächsten Lauf“.
- **Preiswecker:** 24 Modelle (5 TV 83/85″, 9 TV-Größenvarianten ohne Meldung, 10 Air Fryer, Preisgrenzen je Modell). Wunschpreise der App nur per `localStorage` auf dem Gerät; für den Server-Push optional Secret `WUNSCHPREISE` (nie in preise.json oder Log).
- **Web Push** (D6): `werkzeuge/webpush.mjs` (RFC 8291/8292, nur node:crypto), Secrets `VAPID_PRIVAT` und `PUSH_ABO`; ntfy (Secret `NTFY_TOPIC`) läuft parallel.
- **Bekannt:** `pruefe.mjs` „r6.punkte“ meldet `false/false/false`, weil „Entscheiden“ beim Start ausgeblendet ist (Messartefakt). Geplante Läufe können sich um Stunden verspäten (09.11.2026: 8,5 Std.).

## Bestpreis-Link je Modell (Feedback 20.11.2026, D7)

- Recherche fertig: `docs/recherche-eigene-preissuche.md`. Eigene Abfrage (JSON-LD, EAN) belegt bei MediaMarkt, Saturn, Alternate (selbst geprüft) und Proshop (Subagent). Amazon, Cyberport, computeruniverse, Galaxus, Coolblue u. a. sperren einfache Abrufe (nicht umgehen).
- Besitzer: Pilot mit Quellen-Mix heise + idealo + eigene Abfrage, jede Quelle nur nach Rechtsprüfung (Abschnitt 8 des Berichts).
- **Pilot lokal gebaut (21.11.2026, nicht committet):** `daten/quellen.json` (Freigabe mit Datum und Beleg), `daten/pilot_modelle.json` (5 Modelle: LG OLED65C6ELB, Samsung GQ65S90H, Ninja AF500EU, Dreame Z30, Galaxy S26 Ultra 256 GB), `werkzeuge/shopabfrage.py` → `pilot-preise.json` (in .gitignore), `tests/test_shopabfrage.py` mit gekürzten echten Vorlagen `tests/vorlagen/`, Workflow-Entwurf `.github/workflows/pilot-preise.yml` (nur `workflow_dispatch`, Artefakt, nicht gepusht).
- Freigegeben (automatisch): Saturn, Alternate, Proshop (robots.txt erlaubt Produktseiten, AGB ohne Abrufverbot, selbst gelesen) und heise (Besitzer 21.11.2026, O8; Händler-AGB Ziffer 6.8 „Spidering“ richtet sich an Händler). Nur Link: MediaMarkt (robots.txt und AGB 403 Cloudflare, am 20.11. noch erreichbar), idealo (403 Akamai).
- Saturn nennt im JSON-LD keinen Verkäufer; eigenes Angebot nur mit Nachweis aus dem eingebetteten Preisfeld (`isProductOfTypeMarketplace=false`, gleicher Preis). Beleg: S26 Ultra bei Saturn 1.115,99 € war Marktplatzhändler.
- Livelauf 21.11.2026: alle 5 Modelle mit Preis, Quelle, Link, Zeit (LG 1.668,99 € Alternate inkl. 69,99 € Versand; S90H 1.399 € Saturn; Ninja 179,04 € Proshop; Dreame 279 € Saturn; S26 Ultra 1.030,99 € Alternate, Hinweis Proshop 969 € zzgl. Versand). Prüfstand: selbst geprüft (Tests, Livelauf) · unabhängig nein.

## Offen

- **O8:** erledigt (21.11.2026): heise automatisch; idealo und MediaMarkt technisch gesperrt (403), bleiben Link. **O9:** Push von `pilot-preise.yml` + Pilotdateien auf `main` und ein manueller Testlauf braucht Freigabe Besitzer (vorgelegt 21.11.2026). **O10:** Impressum nötig? (Recherche 5., Besitzer)
- **O5:** Wunschpreise als Secret setzen? **O6:** heise-Nutzungsbedingungen ungeklärt (dokumentiert). **O7:** Web Push scharf schalten und Zustellung bestätigen.
- Nicht auf echtem Android-Handy geprüft: neue Icons (WebAPK übernimmt verzögert), Push-Zustellung, Besitzer-Merker.

## Nächster Schritt

Codex-Prüfung `docs/pruefungen/2026-11-21-pilot-bestpreis/` abschließen, dann entscheidet der Besitzer O9 (Commit + Push der Pilotdateien auf `main`, `pilot-preise.yml` einmal manuell starten). Danach: Actions-Artefakt auswerten (Sperren aus Rechenzentrums-IPs?), 3–5 Tage messen (Bericht Abschnitt 8, Schritt 8). Vor dem Push: Codex-Prüfung der Pilotdateien empfohlen (Prüfpunkt Veröffentlichung).
