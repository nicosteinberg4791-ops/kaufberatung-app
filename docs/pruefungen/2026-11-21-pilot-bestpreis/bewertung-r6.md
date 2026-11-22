# Bewertung Runde 6 – Codex-Nachprüfung Pilot Bestpreis-Mix nach Umbau (22.11.2026)

Bericht: `codex-nach-20261122-061137.json` (nicht bestanden; **geschlossen D7-02, -11, -15, -16, -18**). Stand 31b3073.
Noch nicht korrigiert (Kontext-Haltepunkt); Korrektur und Runde 7 in neuer Sitzung.

| ID | Schwere | Einordnung | Maßnahme (geplant) |
|---|---|---|---|
| D7-R6-01 | schwer | bestätigt | Saturn-Zustand nur aus einem aktiven `<script>` nehmen (Zuweisung über `_Seitenteile` bzw. Skriptinhalt, nicht im Kommentar/Template); Rest des Befunds („teilweise gelesen“) im JSON nachlesen. Test. |
| D7-17 | schwer | bestätigt | `_cf_chl_opt = {` innerhalb eines JS-Strings sperrt; ohne JSON-LD sperrt der schwache Zweig auf Rohtext (Template). Schwachen Zweig auf Attribute/sichtbaren Text/aktive Skripte umstellen; Skriptprüfung nur außerhalb von String-Literalen. Test. |
| D7-R6-02 | schwer | bestätigt | `^\s*Just a moment` greift nur am Textanfang: Titel getrennt erfassen (`<title>`-Inhalt) und dort prüfen. Test. |
| D7-R6-03 | schwer | bestätigt | Gültige robots.txt mit Erweiterungsfeld (`X-…:`) gilt nicht als robots → Kommentartext sperrt. `ist_robots` an `robots_gueltig` angleichen (jedes Feld `Name: Wert`), Kommentare vor der Sperrprüfung ignorieren. Test. |
| D7-R6-04 | schwer | bestätigt | `isdigit()` akzeptiert `²` → Absturz statt NichtAbrufbar. Nur ASCII-Ziffern (`re.fullmatch(r"[0-9]{1,15}")`) an allen Content-Length-Stellen; Test. |

Fehlalarme: 0 von 5. Konvergenz: Der Umbau schloss 5 von 6 r5-Befunden; die neuen Befunde sind kleiner und lokal behebbar.
