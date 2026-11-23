# Bewertung Codex r10 – Finder-Veröffentlichung, schmale Nachprüfung (23.11.2026)

Bericht: `codex-nach-20261123-072651.json`
- Prüfer: Codex gpt-6.2-sol high, Stand 7ce30d7, Basis 4d88574, 321 s.
- Verbrauch: 0,64 Mio. Eingabe-Tokens, davon 58 Tsd. ungecacht.
- Urteil: **bestanden mit Hinweisen**. Geschlossen: R9-01, R9-02. Im Umfang offen: nichts. Die Testkorrektur `core.bare` hat Codex in einer simulierten Hook-Umgebung bestätigt (Konfiguration bytegleich).

| ID | Schwere | Einordnung | Beleg |
|---|---|---|---|
| R10-01 | mittel, außerhalb des Prüfumfangs | bewusste Entscheidung: als Restrisiko angenommen, Hinweis für ein späteres Paket. Nachgestellt: `windows_pfad_fehler(["app/a", "app/a/b.txt"])` liefert `[]`. Ein solcher Baum (Datei und Ordner gleichen Namens) entsteht nur durch fehlerhafte Plumbing-Objekte. Das Auspacken bricht dann nach dem ersten Schreiben in die Wegwerf-Kopie ab, veröffentlicht wird nichts. | Korrektur später: Dateipfad darf nicht Verzeichnispräfix eines anderen Pfads sein. |

Fehlalarme: 0 von 1. Nach KERN §3 ist die Runde bestanden: keine kritischen oder schweren Befunde im Umfang offen. Freigabe zur Veröffentlichung nur auf gh-pages (O14 = C, O20).
