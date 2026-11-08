# Kaufberatung als App auf dem Android-Handy

Adresse: **https://nicosteinberg4791-ops.github.io/kaufberatung-app/**

## Installieren (einmal)

1. Die Adresse in **Chrome** auf dem Handy öffnen.
2. Menü **⋮** oben rechts → **„App installieren“** (je nach Chrome-Fassung auch „Zum Startbildschirm hinzufügen“ → „Installieren“).
3. Das Symbol „Kaufberatung“ liegt danach auf dem Startbildschirm bzw. in der App-Übersicht. Die App öffnet ohne Adressleiste.

Die App funktioniert danach auch ohne Netz (zuletzt geladene Fassung und zuletzt geladene Preise).

## Neue Fassung

Wird die Kaufberatung überarbeitet, lädt die App die neue Fassung beim nächsten Öffnen im Hintergrund. Unten erscheint dann **„Neue Fassung bereit“** → **„Neu laden“** tippen. „Später“ behält die alte Fassung bis zum nächsten Öffnen.

## Preise und Preiswecker

- Die Preise kommen aus der Abfrage beim heise-Preisvergleich (günstigster Gesamtpreis mit belegtem Versand) und stehen in `preise.json` auf der Seite. GitHub fragt sie **täglich gegen 6:30 Uhr** ab (geplant 6:23 Uhr MEZ, GitHub startet oft einige Minuten später), bis zum 01.12.2026. Stand und Status des letzten Laufs stehen im Preiswecker.
- **Wunschpreise** (ab der Fassung mit Preiswecker) speichert die App **nur auf diesem Handy**. Sie gehen nicht ins Internet und nicht auf andere Geräte. Wer die App-Daten löscht oder die App entfernt, verliert sie.
- Ist ein Wunschpreis erreicht, erscheint beim Öffnen der App oben bzw. unten die Karte **„Wunschpreis erreicht“**. Das ist der verlässliche Weg.
- **Push aufs Handy über ntfy:** siehe unten. Kommt bei neuem Tiefstpreis (und bei Wunschpreis, falls auf GitHub hinterlegt), je Ereignis einmal.
- **Benachrichtigung im Hintergrund nur als Versuch:** Im Preiswecker „Benachrichtigung versuchen“ tippen und erlauben. Chrome entscheidet selbst, ob und wann die installierte App im Hintergrund prüft (oft nur gelegentlich, manchmal gar nicht). Darauf nicht verlassen.

## Push-Benachrichtigung über ntfy (einmal einrichten)

Die tägliche Abfrage schickt eine Nachricht über den kostenlosen Dienst ntfy.sh, wenn ein Fernseher einen **neuen Tiefstpreis** erreicht (seit Beginn der Abfrage) oder unter einen **auf GitHub hinterlegten Wunschpreis** fällt. Ein Ereignis wird einmal gemeldet; beim Wunschpreis kommt die nächste Meldung erst, wenn der Preis wieder darüber steigt und erneut fällt. Klappt der Versand an ntfy nicht, werden die Preise an dem Tag nicht fortgeschrieben, der Lauf erscheint auf GitHub als fehlgeschlagen und der nächste Lauf meldet das Ereignis erneut, sofern es dann noch gilt (ist der Preis inzwischen wieder gestiegen, wird die verpasste Meldung nicht nachgereicht); selten kann eine Meldung doppelt kommen.

1. Auf dem Handy die App **„ntfy“** aus dem Google Play Store installieren (kostenlos).
2. Am PC die Datei `C:\Users\Nico\Documents\Claude\Kaufberatung-App-privat\ntfy-topic.txt` öffnen. Darin steht der **Themenname** (beginnt mit `kb-`, lange Zufallsfolge). Er ist das einzige Kennwort: nicht weitergeben, nicht in Chats kopieren.
3. In ntfy auf **„+“** tippen, den Themennamen genau übertragen (z. B. über die eigene Notiz-App), Server **ntfy.sh** lassen, **„Abonnieren“**.
4. Test: Auf GitHub unter *Actions → Preisabfrage → Run workflow* das Häkchen **„Zusätzlich eine Test-Benachrichtigung …“** setzen und starten. Nach ein bis zwei Minuten kommt „Test: Benachrichtigungen der Kaufberatung-App kommen an“.

Tippt man auf eine Meldung, öffnet sich die Kaufberatung. Kommen Meldungen verspätet: in den Android-Einstellungen die Akku-Optimierung für ntfy ausschalten.

**Wunschpreise auf GitHub (optional):** Die Wunschpreise in der App bleiben auf dem Handy und lösen keinen Push aus. Soll ntfy auch bei Wunschpreisen melden, müssen sie zusätzlich als geheimes GitHub-Secret `WUNSCHPREISE` hinterlegt sein (nicht öffentlich, nicht im Repo, nicht in preise.json oder den Lauf-Protokollen), z. B. `{"lg_c6elb": 2500, "tcl_c8l": 1900}`. Kennungen: `lg_c6elb`, `lg_c69lb`, `sam_s90h`, `tcl_c8l`, `sam_qn90f`.

**Wenn nichts mehr kommt:** Schlägt die Abfrage fehl (z. B. heise sperrt die GitHub-Rechner), meldet GitHub den fehlgeschlagenen Lauf (je nach GitHub-Benachrichtigungseinstellung per E-Mail), und im Preiswecker steht der Laufstatus mit dem Fehler. Am 01.12.2026 endet die Abfrage von selbst.

## Entfernen

App-Symbol lange drücken → „Deinstallieren“ bzw. „App-Info“ → „Deinstallieren“. Damit sind auch die Wunschpreise weg.

## Was die App nicht kann

- Keine Anmeldung, kein Abgleich zwischen Geräten.
- Die Seite ist öffentlich erreichbar (aber nicht in Suchmaschinen gelistet: `noindex`). Persönliche Daten gibt es dort nicht, Wunschpreise bleiben auf dem Handy.
