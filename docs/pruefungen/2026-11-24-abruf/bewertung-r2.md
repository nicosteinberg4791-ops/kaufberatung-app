# Bewertung Codex r2 – Paket `abruf.py` (24.11.2026)

Bericht: `codex-nach-20261124-084654.json` (Codex gpt-6.2-sol high, Stand 158fde1, Basis 88e026e, 273 s, 0,42 Mio. Eingabe-Tokens, davon 59 Tsd. ungecacht) · Urteil: nicht bestanden · geschlossen: R5-05 (Steuerzeichen), R6-02a, R6-02b, R2-04 (Leerraum).

| ID | Schwere | Einordnung | Klasse | Suche | Behebung | Probe |
|---|---|---|---|---|---|---|
| R2-01 | schwer | bestätigt: Schlüssel bis 253 Zeichen plus `.gesperrt`/`.zeit.neu` ergibt bis 262 Zeichen, NTFS erlaubt 255 je Komponente | Länge der vollständigen Dateinamen | Endungen im Takt-Ordner: `.lock`, `.zeit`, `.zeit.neu`, `.gesperrt` (längste 9 Zeichen) | Klartextschlüssel nur bis 246 Zeichen, sonst Hash; längere Hosts scheiterten schon vor dem Paket an `.zeit.neu` (A2), es gibt also keine nutzbaren alten Stempel dazu | `test_hostschluessel_…`: 246 bleibt (mit beiden langen Endungen ≤ 255), 247 wird Hash |
| R2-02 | schwer | bestätigt: `h%2dNAME.invalid` und `h%2dname.invalid` ergaben getrennte Takte; urllib dekodiert die Authority | Authority wird von `urlsplit` und urllib verschieden gelesen | `grep -n "urlsplit" werkzeuge/datenpflege/abruf.py` → nur `robots_ok` (vor allen Abrufen) und `holen` (danach) | `robots_ok` lehnt `%` in der Authority ab (Host, Port, Nutzerteil, Zonen-ID); die Sonderregel für Zonen-IDs entfällt, der Schlüssel ist wieder ganz klein | `test_port_null_…`: 6 Authority-Fälle mit `%`; `%` im Pfad bleibt erlaubt |
| R2-03 | schwer | bestätigt: `https://h.invalid%3A8443/a` ergab Port 443 für robots, 8443 im HTTP-Client | wie R2-02 | wie R2-02 | wie R2-02 | wie R2-02 (`%3A8443`, `:8%34`) |
| R2-04a | gering | bestätigt: Vermerk nur aus BOM oder U+200B ergab einen unsichtbaren Grund | Grund ohne sichtbare Zeichen | – | Ersatzgrund, wenn kein Zeichen druckbar und kein Leerraum ist | `test_sperrvermerk_…`: BOM, U+200B, Mischung mit U+2060 |

Fehlalarme: 0. Rot gegen 158fde1: 11 Fehlschläge in 3 Tests, grün mit Korrektur (33 Tests). Folge der Entscheidung: IPv6-Zonen-IDs (`%25`) sind für den Abrufhelfer nicht mehr zulässig; die gepflegten Shop-URLs haben keine.
