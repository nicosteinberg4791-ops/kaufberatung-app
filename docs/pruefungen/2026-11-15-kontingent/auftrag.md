# Prüfauftrag: heise-Kontingent im Preiswecker (Stand e6eaceb, Basis 2488a7e)

Ziel: Jeden Tag alle 24 Preise lesen, obwohl heise je Zeitfenster nur etwa 18 Abrufe zulässt (gemessen im Livelauf 15.11.2026). Das soll kostenlos bleiben und ohne Umgehung der Drosselung auskommen.

Fertigkriterien:
- Jeder Lauf ruft höchstens `ABRUF_JE_LAUF` (16) Seiten ab. Abgerufen werden nur Modelle ohne Preis von heute, die ältesten zuerst. Die übrigen gelten als „verschoben“; die Meldung zeigt sie unter „Folgt im nächsten Lauf“ mit Status „teilweise“.
- Modelle mit Preis von heute werden nicht abgerufen und zählen als gelesen. Ein Nachlauf, in dem alles schon da ist, ruft nichts ab und lässt preise.json byte-gleich (`--nur-push` committet dann nichts).
- Eine Markierung „heute_schon“ ohne echten Preis von heute in preise.json gilt als Abruffehler (Schutz).
- `preise.yml` enthält zwei Nachläufe (06:23 und 08:23 UTC). Reihenfolge, Secrets und ntfy/Push-Schritte bleiben unverändert.
- Bei 429 stehen „Retry-After“ und die Anfragenummer im Fehlertext. Die Meldung „Abruf fehlgeschlagen…“ funktioniert weiter.
- Befehl `powershell tests/alle-tests.ps1` muss melden: „Fehler: 0“.

Dateien: `werkzeuge/preiswecker.py` (ABRUF_JE_LAUF, abruf_alle, abgleich: heute_schon, verschoben, offen), `werkzeuge/preise_aktualisieren.py` (lies_alt, preis_datum, abrufreihe, aktualisiere-Schutz, main-Nachlauf, uebersicht), `.github/workflows/preise.yml` (cron), `tests/test_app.py` (Klasse Kontingent, Anpassung test_grenzen_exakt_und_abruf_alle).

Selbstprüfung: alle-tests Fehler 0. Rot-Probe: Klasse Kontingent am Stand 2488a7e ergab 4 Fehlschläge und 3 Fehler, am neuen Stand ist sie grün.

Bekannte Grenzen:
- Die Fensterlänge ist unbekannt; die Annahme ist, dass sie unter 1 h liegt. Hält diese Annahme nicht, bleiben Modelle „teilweise“, rücken aber am nächsten Tag als älteste nach vorn.
- GitHub startet geplante Läufe manchmal stark verspätet. `concurrency` verhindert, dass Läufe parallel laufen.
- Der Datumsvergleich nutzt die Ortszeit Europe/Berlin (TZ im Workflow).

Prüffragen:
1. Kann ein Modell dauerhaft ausgehungert werden oder doppelt abgerufen werden?
2. Status und Meldung über mehrere Läufe am Tag: Können Status oder Text falsch sein, zum Beispiel ein falsches „ok“?
3. Tagesgrenze und Zeitzone: Kann ein Lauf um Mitternacht oder bei verspätetem Start falsch entscheiden?
4. Gehen Tiefstpreis, Verlauf oder Treffer verloren, oder wird ein Treffer doppelt gemeldet, wenn ein Modell erst im Nachlauf kommt?
5. Ist der Fall „nichts abzurufen“ im Workflow sauber, also kein rotes Ergebnis, keine Nachricht und kein Commit?
