# Bewertung Codex r1 – Paket `abruf.py` (24.11.2026)

Bericht: `codex-erst-20261124-083540.json` (Codex gpt-6.2-sol high, Stand 88e026e, Basis 280ab3d, 311 s, 1,14 Mio. Eingabe-Tokens, davon 70 Tsd. ungecacht) · Urteil: nicht bestanden · geschlossen: R5-01 (durch A2), R5-05 (Port 0, Ablage), Takt-Dateien am gemeinsamen Schlüssel, Git-Test-Helfer.
Vorprüfung (Sonnet medium, vor r1): 3 gering; behoben: Schlüssellänge (in r1 wieder zurückgenommen, siehe R6-02b), Fehler beim Abschlussstempel verdrängt eine 403 nicht mehr; IDN/Punkt am Ende als bekannte Grenze.

| ID | Schwere | Einordnung | Klasse | Suche | Behebung | Probe |
|---|---|---|---|---|---|---|
| R5-05 | schwer | bestätigt: `urlsplit` entfernt Tab/CR/LF still, `https://h.invalid:\t/a` ergab Port 443 | Normalisierung vor der Prüfung weicht vom gesendeten Wert ab | `grep -n "urlsplit" werkzeuge/datenpflege/abruf.py` → `holen` (nur Hostname, nach `robots_ok`), `robots_ok` | `robots_ok` lehnt URLs mit Zeichen ≤ 0x20 oder 0x7F vor `urlsplit` ab | `test_port_null_ist_kein_standardport`: 6 URLs (Tab im Port und Host, CR/LF, Leerzeichen, DEL, LF am Ende) |
| R6-02a | schwer | bestätigt: `host.lower()` faltete die IPv6-Zonen-ID | Normalisierung zu weit | – | nur die Adresse vor `%` klein, Zonen-ID unverändert in den Hash | `test_hostschluessel_…`: `%25ethA` ≠ `%25etha`, `FE80::1%25etha` = `fe80::1%25etha` |
| R6-02b | schwer | bestätigt: Grenze 100 Zeichen (aus der Vorprüfung) machte gewöhnliche Hostnamen 101–253 zu Hash-Namen, alte Stempel wären übergangen worden | Übergang alter Dateinamen | – | Grenze wieder DNS-Maximum 253; ein Pfad über MAX_PATH scheitert beim Öffnen der Sperrdatei vor jedem Abruf (fail-closed) | `test_hostschluessel_…`: 101 und 253 Zeichen bleiben, 254 wird Hash |
| R2-04 | schwer | teils bestätigt, teils bewusste Entscheidung: ein über 30 min alter, normaler Vermerk ist abgelaufen, sein Inhalt (leer, unlesbar) ändert daran nichts; eine Freigabe hängt nur am Alter aus `lstat`. Bestätigt: Vermerk nur aus Leerraum ergab einen unsichtbaren Grund (gering) | Grund ohne sichtbare Zeichen | – | Leerraum ergibt „Sperrvermerk ohne Grund“; Testtext „lesbarer“ → „normaler (Inhalt egal)“ | `test_sperrvermerk_…`: `b" \n\t"` |

Fehlalarme: 0. Bewusste Entscheidung: R2-04 (alter Vermerk, siehe oben). Rot gegen 88e026e: 9 Fehlschläge in 3 Tests, grün mit Korrektur (33 Tests).
