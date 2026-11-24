# Bewertung Codex r4 – Paket `abruf.py` (24.11.2026, über dem Rundenlimit nach KERN §3)

Bericht: `codex-nach-20261124-100235.json` (Codex high, Stand 7dfd108, Basis 10d405f) · Urteil: nicht bestanden · geschlossen: R3-01. Codex konnte die Tests mangels Python-Interpreter nicht selbst ausführen. **Noch nichts behoben** (Entscheidung beim Besitzer, O23).

| ID | Schwere | Einordnung | Klasse | Suche | Wirkung | Korrekturvorschlag |
|---|---|---|---|---|---|---|
| R2-04a | schwer (laut Bewertung gering) | bestätigt: `unicodedata.category("⠀")` = `So`, nicht in `_FUELLER`, also zählt `_sichtbar` das leere Braille-Muster als sichtbar | Zeichen mit sichtbarer Kategorie, aber ohne Zeichenbild | `python -I -c` über bekannte Leerzeichen: U+2800 (So) und U+1D159 MUSICAL SYMBOL NULL NOTEHEAD (So) treffen zu; U+3164/U+115F sind schon ausgenommen, U+2063, U+180E und U+1D173 sind Cf und schon ausgeschlossen | Sperre wirkt (Exit 3, kein Abruf); nur der Meldungstext hinter „Domain gesperrt …:“ bleibt leer | U+2800 und U+1D159 in `_FUELLER` aufnehmen (Name allgemeiner: Zeichen ohne Zeichenbild); Test mit beiden als einzigem Inhalt |
| R4-01 | mittel | bestätigt, außerhalb des Umfangs (vor dem Paket vorhanden): `urlsplit("https://[v1.invalid]/a").hostname` = `v1.invalid`; `robots_text` setzt Klammern nur bei `:` im Host, die robots-Anfrage geht also an `v1.invalid`, die Produktanfrage mit Host-Header `[v1.invalid]` | Authority wird von `urlsplit` und urllib verschieden gelesen (wie R2-02, R2-03, R3-01) | `grep -n "urlsplit\|hostname" werkzeuge/datenpflege/abruf.py` → nur `robots_ok`/`robots_ursprung` (vor dem Abruf) und `holen`; sonst keine Stelle baut die Authority neu | robots.txt und Produktanfrage können unterschiedlich beantwortet werden; die gepflegten Shop-URLs haben keine Klammern | In `robots_ok` Klammern in der Authority nur mit gültiger IPv6-Adresse zulassen (`ipaddress.IPv6Address`), sonst Abbruch ohne Abruf; Test mit `[v1.invalid]` und `[h.invalid]` |

Fehlalarme: 0. Beide Befunde sind fail-closed bzw. ohne Bezug zu den gepflegten URLs; jede Korrektur ist eine Zeile plus Test.

Muster: R2-04a ist die dritte Runde derselben Klasse (Leerraum → Format-/kombinierende Zeichen → Symbol ohne Zeichenbild). Eine Liste von Unicode-Kategorien kann „ohne Zeichenbild“ nicht vollständig abdecken. Die Sperre selbst hing nie daran.

**Vorlage O23 (Besitzer, Rundenlimit überschritten):**
- **(A)** beide beheben, Tests rot→grün, schmale Runde 5;
- **(B)** beide beheben, Tests rot→grün, ohne weitere Runde, als „selbst geprüft“ vermerken;
- **(C)** beide als Restrisiko annehmen, nichts ändern.

Empfehlung: B. Beide Korrekturen sind klein und mit Test belegbar, keine berührt die Sperrwirkung, und eine weitere Runde würde nach dem Muster oben wahrscheinlich nur das nächste exotische Zeichen finden.

## Behebung (O23 = B, Besitzer 24.11.2026: beheben ohne weitere Runde, selbst geprüft)

| ID | Behebung | Probe |
|---|---|---|
| R2-04a | `_FUELLER` um U+2800 und U+1D159 ergänzt; ein Vermerk nur aus diesen Zeichen (auch gemischt mit Leerraum und U+FE0F) ergibt „Sperrvermerk ohne Grund“ | `test_sperrvermerk_…`: U+2800, U+1D159, „U+2800 U+2800 U+FE0F“ (vorher rot) |
| R4-01 | `robots_ok` lässt Klammern in der Authority nur mit gültiger IPv6-Adresse (`ipaddress.IPv6Address`, optional mit Port) zu; lehnt `urlsplit` die URL selbst ab, endet `robots_ok` ohne Abruf (mit Klammern: eigener Text, sonst „URL nicht lesbar“) | `test_port_null_…`: `[v1.invalid]`, `[h.invalid]`, `[v1.fe80::1]`, `[127.0.0.1]`, `[]`, `[2001:db8::1]x`; `holen` bleibt unaufgerufen (vorher rot: 7 Fehlschläge, 3 Fehler, `holen` 3-mal aufgerufen); `[2001:db8::1]` bleibt erlaubt |

Rot vor der Korrektur: 7 Fehlschläge und 3 Fehler in 2 Tests, grün danach (33 Tests). Prüfstufe: selbst geprüft · unabhängig: Codex r1–r4 nicht bestanden, keine Runde 5 (O23 = B).
