# Prüfauftrag: Eigene Benachrichtigung per Web Push (D6)

**Ziel:** Der tägliche Actions-Lauf schickt Treffer (neuer Tiefstpreis, Wunschpreis) per Standard-Web-Push (VAPID, RFC 8291/8292, ohne Fremdbibliothek) an die installierte PWA; Abo und privater Schlüssel nur als Secrets.

**Fertigkriterien**
- `werkzeuge/webpush.mjs` verschlüsselt korrekt (RFC 8291 Anhang A), VAPID-JWT gültig, Exitcodes 0/1/4/5 wie im Dateikopf, gibt nie Endpoint-Pfad, p256dh, auth, JWT oder privaten Schlüssel aus.
- App: „Push einrichten“ abonniert mit `userVisibleOnly` und dem öffentlichen Schlüssel, zeigt den Code für das Secret `PUSH_ABO`; Abo mit fremdem Schlüssel wird ersetzt.
- `sw.js`: jede Push-Nachricht zeigt eine Benachrichtigung (waitUntil), Ziel nur innerhalb der App.
- Workflow: Web Push nach ntfy und vor `--nur-push`; fehlende Secrets → übersprungen; falscher Schlüssel → rot; 404/410 (Exit 4) blockiert die Preise nicht, Lauf am Ende rot; andere Fehler brechen vor dem Push ab. Keine Secrets in `run:`-Zeilen oder Logs.
- Anleitung `docs/anleitung-handy.md` beschreibt Einrichtung und Grenzen ohne unbelegte Zusagen.

**Betroffene Dateien:** werkzeuge/webpush.mjs, tests/webpush.test.mjs, app/app.js, app/sw.js, app/app.css, .github/workflows/preise.yml, tests/test_app.py, docs/anleitung-handy.md, docs/entscheidungen.md (D6). Referenz: werkzeuge/preise_aktualisieren.py (erzeugt die Meldungsdatei), RFC 8291 (Anhang A).

**Selbstprüfung:** `powershell -File tests/alle-tests.ps1` → Fehler 0 (31 Tests, darunter `node --test tests/webpush.test.mjs` 23/23 und `--selbsttest`). Gegenprobe: verfälschter Testvektor → rot. Browser (375 px, hell/dunkel): Einrichtung mit nachgestellter Erlaubnis und Abo, Code angezeigt, kein Querscrollen, Konsole leer. Geheimnis-Scan 0 Funde; privater Schlüssel liegt außerhalb des Repos.

**Bekannte Grenzen:** Nicht gegen einen echten Push-Dienst getestet (erst mit Nicos Handy möglich). Zustellung bei zwangsbeendetem Chrome/Akku-Optimierung nicht steuerbar. `pushsubscriptionchange` in Chrome nicht belegt; Abo muss bei Ungültigkeit von Hand erneuert werden. ntfy läuft parallel weiter.

**Prüffragen**
1. Ist die Verschlüsselung/VAPID-Kopfzeile so, dass FCM (fcm.googleapis.com) sie annimmt (aud, exp, `vapid t=…, k=…`, TTL, Urgency, Content-Encoding)?
2. Kann ein Geheimnis (Abo, auth, privater Schlüssel) in Actions-Logs, stdout/stderr oder Fehlertexten landen?
3. Stimmt die Fehlerlogik im Workflow (bash `-e`, `exit "$rc"` in der Funktion, GITHUB_OUTPUT), auch bei Treffer plus Testnachricht?
4. Kann die App in einen Zustand geraten, in dem sie ein Abo zeigt, das nicht zum Schlüssel passt, oder bei verweigerter Erlaubnis hängt?
5. Fehlen Tests für ein Verhalten, das im Betrieb kritisch ist?
