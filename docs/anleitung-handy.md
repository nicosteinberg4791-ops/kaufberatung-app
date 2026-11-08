> Stand 08.11.2026: Die Adresse ist erst erreichbar, wenn das öffentliche Repo angelegt und Pages eingeschaltet ist.

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

- Die Preise kommen aus der Abfrage beim heise-Preisvergleich (günstigster Gesamtpreis mit belegtem Versand) und stehen in `preise.json` auf der Seite. Die tägliche automatische Abfrage über GitHub Actions wird gerade eingerichtet; bis dahin gelten die zuletzt veröffentlichten Preise (Stand steht im Preiswecker).
- **Wunschpreise** (ab der Fassung mit Preiswecker) speichert die App **nur auf diesem Handy**. Sie gehen nicht ins Internet und nicht auf andere Geräte. Wer die App-Daten löscht oder die App entfernt, verliert sie.
- Ist ein Wunschpreis erreicht, erscheint beim Öffnen der App oben bzw. unten die Karte **„Wunschpreis erreicht“**. Das ist der verlässliche Weg.
- **Push aufs Handy über ntfy** (in Vorbereitung): Die Anleitung zum Abonnieren folgt, sobald die tägliche Abfrage läuft.
- **Benachrichtigung im Hintergrund nur als Versuch:** Im Preiswecker „Benachrichtigung versuchen“ tippen und erlauben. Chrome entscheidet selbst, ob und wann die installierte App im Hintergrund prüft (oft nur gelegentlich, manchmal gar nicht). Darauf nicht verlassen.

## Entfernen

App-Symbol lange drücken → „Deinstallieren“ bzw. „App-Info“ → „Deinstallieren“. Damit sind auch die Wunschpreise weg.

## Was die App nicht kann

- Keine Anmeldung, kein Abgleich zwischen Geräten.
- Die Seite ist öffentlich erreichbar (aber nicht in Suchmaschinen gelistet: `noindex`). Persönliche Daten gibt es dort nicht, Wunschpreise bleiben auf dem Handy.
