# Bewertung Runde 1 – Codex-Erstprüfung Pilot Bestpreis-Mix (21.11.2026)

Bericht: `codex-erst-20261121-063325.json` (Urteil nicht bestanden, Stand 79daf34). Bewertet vom Lead (Claude).

| ID | Schwere | Einordnung | Begründung / Maßnahme |
|---|---|---|---|
| D7-01 | schwer | bestätigt | `urlopen()` folgt 3xx vor der Prüfung von `geturl()`. Korrektur: eigener Opener ohne Weiterleitung, 3xx → `Weitergeleitet`; Test mit lokalem HTTP-Server zählt, dass kein zweiter Request erfolgt. |
| D7-02 | schwer | bestätigt | robots.txt wurde ungeprüft geparst. Korrektur: `robots_gueltig()` verlangt Zeilen der Form `Feld:`/Kommentar und mindestens eine `User-agent`-Zeile; HTML, Fließtext oder leere Antwort = nicht lesbar (Quelle wird nicht abgefragt). |
| D7-03 | schwer | bestätigt | JSON-LD hob jede Sperrerkennung auf. Korrektur: eindeutige Sperrmerkmale (aktives Cloudflare-Challenge-Skript `…/orchestrate`, `cf-chl`, `Access Denied`, Incapsula, PerimeterX, `Just a moment`) sperren immer; nur der passive Verweis `challenge-platform`/`captcha` wird bei Seiten mit JSON-LD toleriert. Test angepasst. |
| D7-04 | schwer | bestätigt | Fenster von 1.500 Zeichen konnte in das nächste Preisobjekt reichen. Korrektur: Objekt endet am nächsten `{"id":"`; Preisobjekt (`CofrPriceFeaturePrice`) wird mit `json.JSONDecoder.raw_decode` innerhalb dieses Objekts gelesen. Test mit Codex-Szenario. |
| D7-05 | schwer | ungeklärt → Besitzer | heise ist laut Besitzerentscheid (O8) eine Vergleichsquelle: Händlerrolle ist dort der jeweilige Händler, Produktidentität über die feste heise-Produktseite. Zustand und Lieferbarkeit liefert heise nicht belegt als Feld (nur Freitext `delivery_time`, keine Vorlage mit Werten). Frage an Besitzer: heise-Treffer weiter als Bestpreis zulassen (wie im Preiswecker) oder nur als „Vergleichspreis heise“ anzeigen? Keine Codeänderung ohne Entscheid. |
| D7-06 | kritisch | bestätigt | Reproduziert (Vorauswahl `sicher`/`roh`). Korrektur: `heise_auswerten()` gibt alle Angebote im Korridor zurück (nutzt `preiswecker.angebote`/`versand`, preiswecker unverändert); Auswahl erst nach Dublettenbereinigung. Test mit Codex-Zahlen. |
| D7-07 | schwer | bestätigt | Schlüssel nur 8 Zeichen, Reihenfolge entschied bei gleichem Händler. Korrektur: volle normalisierte Händleridentität, Aliase nur aus `quellen.json` (`name`, `verkaeufer`); bei gleichem Vorrang gewinnt der niedrigere belegte Gesamtpreis. Tests für beide Fälle. |
| D7-08 | schwer | bestätigt | `zahl(".00")` = None. Korrektur: Dezimalwert ohne führende Null; Vorlagentest erwartet jetzt Versand 0,00 € (json-ld), gesamt 969,00 €. |
| D7-09 | schwer | bestätigt | `saturn_s90h.html` enthielt Service-/Garantie-Angebote (`addOn`) samt Konto-URL. Korrektur: `addOn` entfernt, Kopfkommentar angepasst; Test prüft, dass keine Vorlage `myaccount` oder `addOn` enthält. Hinweis: Die alte Fassung bleibt in der öffentlichen Git-Historie (79daf34); keine persönlichen Daten, öffentliche Shop-URL. |

Fehlalarme: 0 von 9.
