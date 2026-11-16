# Stand – Kaufberatung-App

Stand: 16.11.2026 · `main` auf `github.com/<konto>/kaufberatung-app` (öffentlich), Pages aus `gh-pages`. Veröffentlicht: App 14645eebc97d, Inhalt Artifact-Version 29 (16.11.2026, Bedienung neu geordnet: vier Bereiche, Schrittleiste, Verlauf, Antwortzeile, Suche). Ältere Einzelheiten: Git-Verlauf und `docs/pruefungen/`.

## „Für alle“ (seit Artifact-Version 28 veröffentlicht)

- App-Hülle: Besitzerfunktionen (Wunschpreise, Treffer-Karte, „Push einrichten“, Hintergrundprüfung) nur mit lokalem Merker `kb-app:besitzer` (`app/app.js`); ohne Merker `isOwner()` = false, Wunschpreise unsichtbar und nicht setzbar. Sichtbarkeit, keine Sicherheit. Secret-Link aus der Pages-Adresse abgeleitet, keine Konto-URL im Code.
- Benachrichtigungen neutral („Preisalarm: <Modell> ist unter deinem Wunschpreis“; „Push neu einrichten“ ohne Besitzerbezug). Manifest-Beschreibung ohne „Private“.
- Repo-Dateien ohne Namen, lokale Pfade und Konto-URLs (Platzhalter `<arbeitsordner>`, `<privater-ordner>`, `<konto>`); Workflow-Klickziel und VAPID-Subjekt aus `GITHUB_REPOSITORY`.
- Offen: Inhalt (`quelle/`, `dist/`) kommt aus dem neuen Artifact-Bau; der Preiswecker der Seite zeigt ohne Besitzer noch „kein Wunschpreis“ je Zeile (Seiteninhalt, nicht Hülle). Browserprüfung (`pruefe.mjs`) und Codex-Prüfung stehen aus.

## Ablauf und Werkzeuge

- **Inhalt nachziehen:** `Artifact read` → `werkzeuge/app_bauen.py --quelle <datei>` → `tests/alle-tests.ps1` → `werkzeuge/browserpruefung/pruefe.mjs` (lokal und `--url`) → `werkzeuge/veroeffentlichen.py` (nur mit Auftrag). Fallstrick: gespeicherte Live-Seiten mit Pfad > 260 Zeichen vorher nach `%TEMP%` kopieren. App-Kennung kann je Checkout abweichen (CRLF in `icons/icon.svg`).
- **Tägliche Preisabfrage** (O1/O2): `.github/workflows/preise.yml`, Hauptlauf 05:23 UTC plus Nachläufe, `workflow_dispatch` mit Häkchen Test-Benachrichtigung, bis 01.12.2026. Ablauf: Secret prüfen → `preise_aktualisieren.py --meldung` → ntfy → Web Push → `--nur-push` (nur preise.json auf gh-pages). Je Lauf höchstens 16 heise-Anfragen (`ABRUF_JE_LAUF`), älteste Preise zuerst, Rest „Folgt im nächsten Lauf“; HTTP 429 wird einmal wiederholt, Lauffrist 420 s.
- **Preiswecker:** 24 Modelle (5 TV 83/85″, 9 TV-Größenvarianten ohne Meldung, 10 Air Fryer, Preisgrenzen je Modell). Wunschpreise der App nur per `localStorage` auf dem Gerät; für den Server-Push optional Secret `WUNSCHPREISE` (nie in preise.json oder Log).
- **Web Push** (D6): `werkzeuge/webpush.mjs` (RFC 8291/8292, nur node:crypto), Secrets `VAPID_PRIVAT` und `PUSH_ABO`; ntfy (Secret `NTFY_TOPIC`) läuft parallel. Privater Schlüssel und Topic liegen nur beim Besitzer außerhalb des Repos (`<privater-ordner>`).
- **Bekannt:** `pruefe.mjs` „r6.punkte“ meldet `false/false/false`, weil „Entscheiden“ beim Start ausgeblendet ist (Messartefakt). Geplante Läufe können sich um Stunden verspäten (09.11.2026: 8,5 Std.).

## Offen

- **O5:** Wunschpreise als Secret setzen? **O6:** heise-Nutzungsbedingungen ungeklärt (dokumentiert). **O7:** Web Push scharf schalten und Zustellung bestätigen (Stand siehe `docs/offene-punkte.md`).
- Nicht auf echtem Android-Handy geprüft: neue Icons (WebAPK übernimmt verzögert), Push-Zustellung, Besitzer-Merker.

## Nächster Schritt

Neuen Inhalt aus dem Artifact-Bau übernehmen, `pruefe.mjs` lokal (Besitzer- und Fremdansicht), Codex-Prüfung „Veröffentlichung“, dann nach Freigabe veröffentlichen. Besitzergerät danach einmal freischalten (Kommentar Besitzer-Merker in `app/app.js`).
