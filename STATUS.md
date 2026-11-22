# Stand – Kaufberatung-App

Stand: 22.11.2026 · `main` (nach 8caf11b) lokal (origin/main 79daf34 gepusht) auf `github.com/<konto>/kaufberatung-app` (öffentlich), Pages aus `gh-pages`. Veröffentlicht: App 090ac453670e, Inhalt Artifact-Version 30. Pilot Bestpreis-Mix (D7) gepusht und einmal auf Actions gelaufen; Prüfstand selbst geprüft · unabhängig: Codex 7 Runden, nicht bestanden (Rundenlimit überschritten) · Besitzer: Push/Livegang 21.11. freigegeben.

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
- **Pilot (21.11.2026):** `daten/quellen.json` (Freigabe mit Datum und Beleg), `daten/pilot_modelle.json` (5 Modelle), `werkzeuge/shopabfrage.py` → `pilot-preise.json` (in .gitignore), `tests/test_shopabfrage.py` (59 Tests, synthetische Vorlagen `tests/vorlagen/`), `.github/workflows/pilot-preise.yml` (nur `workflow_dispatch`, Ergebnis als Artefakt). 79daf34 gepusht (Besitzer 21.11.), Korrekturen 10b8897 und c36205f nur lokal.
- Automatisch: Saturn, Alternate, Proshop, heise (O8). Nur Link: MediaMarkt, idealo (403). Saturn: eigenes Angebot nur mit Nachweis im eingebetteten Preisfeld; Weiterleitungen werden nicht verfolgt (Saturn leitet Ninja/Dreame auf Marktplatz-Varianten um).
- **Actions-Lauf 44871394260** (21.11. 05:33 UTC): Alternate ok, heise ok; **Saturn 403 und Proshop 403 schon bei robots.txt** (Rechenzentrums-IP gesperrt, nicht umgehen). Lokal (Heim-IP) liefern alle vier. Bestpreise Actions: LG 1.349 € (heise), S90H 1.469 € (heise), Ninja 164 € (heise), Dreame keiner, S26 1.030,99 € (Alternate).
- **Codex-Prüfung** `docs/pruefungen/2026-11-21-pilot-bestpreis/`: r1 9 Befunde (1 kritisch), r2 9 (1 kritisch, neu durch Korrektur), r3 5 schwer offen (D7-02 gekürzte 200-Antwort, D7-05 heise ohne Gültigkeitsnachweis = Besitzerentscheid „Bestpreis zulassen“, D7-09 Shoptexte in Alternate-Vorlage und Prüfprotokollen, D7-11 Captcha-Text, D7-14 doppelter Marktplatz-Schlüssel); r3 behoben in fc94934. r4: D7-09, D7-14 geschlossen, 3 schwer offen (D7-02 chunked-Abschluss, D7-11 Captcha-Text mit HTML/Fehlsperren, D7-15 zweites Saturn-Objekt mit anderer Feldfolge). r4 behoben in 37f72a8. r5: 6 schwer offen (D7-02, -11, -15 bis -18, alle künstliche Randfälle; 4 unsicher, 2 sicher), Architektursignal. Umbau nach r5 in 86166a1 (strenger Übertragungsrahmen, Saturn-Zustand strukturell, html.parser). r6: geschlossen D7-02, -11, -15, -16, -18; 5 schwer offen (D7-17, D7-R6-01..04), behoben in 8caf11b (Klasse `Runde6`, 75 Tests, Rot-Gegenprobe gegen 9113b9f, Livelauf 22.11. ok: S90H 1.399 € Saturn eigen, keine Fehlsperre). r7: geschlossen D7-R6-02..04; offen 4 schwer und 1 mittel (D7-R7-01..05), alle künstliche Randfälle der JS-Auswertung per Regex (leeres `src`, Template-Literal, fremdes Zuweisungsziel, `<!--` im Skript, Titel mit Zeilenumbruch, JSON-LD-Text im Kommentar). Nicht korrigiert (Rundenlimit). Bewertungen `bewertung-r1..r7.md`, Fehlalarme 0.

## Offen

- **O8:** erledigt (21.11.2026): heise automatisch; idealo und MediaMarkt technisch gesperrt (403), bleiben Link. **O9:** erledigt (Push und Testlauf 21.11.2026). **O11:** erledigt (21.11.2026): heise-Treffer dürfen den Bestpreis stellen (D7-05 bewusste Entscheidung, D7 Nachtrag). **O12:** Saturn/Proshop sperren Actions-IPs: Pilot dort nur mit Alternate+heise oder Lauf vom Heimrechner? **O13:** alte Vorlagen mit Shoptexten in öffentlicher Historie (79daf34) belassen? **O10:** Impressum nötig? (Recherche 5., Besitzer)
- **O5:** Wunschpreise als Secret setzen? **O6:** heise-Nutzungsbedingungen ungeklärt (dokumentiert). **O7:** Web Push scharf schalten und Zustellung bestätigen.
- Nicht auf echtem Android-Handy geprüft: neue Icons (WebAPK übernimmt verzögert), Push-Zustellung, Besitzer-Merker.

## Nächster Schritt

Besitzer entscheidet nach `bewertung-r7.md`: Option 1 Paket schneiden (R7-01/-04/-05 klein beheben, R7-02 enge Positivliste nach echter Saturn-Seite, R7-03 Fehlsperre durch passiven Skripttext als Leitplanke zulassen, dann letzte schmale Runde 8 mit `-Vorbericht codex-nach-20261122-063019.json -Bewertung bewertung-r7.md -Basis 8caf11b`) oder Option 2 Leitplanke ohne weitere Runde. Push von c36205f+ erst nach bestandener Prüfung bzw. Besitzerentscheid. Außerdem O12, O13. Danach 3–5 Tage messen (Bericht Abschnitt 8, Schritt 8).
