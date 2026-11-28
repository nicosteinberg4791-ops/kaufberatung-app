# Bewertung Codex r3 – Paket `abruf.py` (24.11.2026, letzte Runde nach KERN §3)

Bericht: `codex-nach-20261124-090915.json` (Codex gpt-6.2-sol high, Stand 8bb2ec2, Basis 158fde1, 456 s, 1,72 Mio. Eingabe-Tokens, davon 76 Tsd. ungecacht) · Urteil: nicht bestanden · geschlossen: R2-01, R2-02, R2-03. **Noch nichts behoben** (Rundenlimit erreicht, Entscheidung beim Besitzer).

| ID | Schwere | Einordnung | Klasse | Wirkung | Korrekturvorschlag |
|---|---|---|---|---|---|
| R2-04a | schwer (laut Bewertung gering) | bestätigt: ein frischer Vermerk nur aus U+FE0F ergibt einen unsichtbaren Grund; `isprintable()` erfasst Zeichen ohne Zeichenbild nicht | Sichtbarkeit nach Unicode-Kategorie | Die Sperre wirkt (Exit 3, kein Abruf); nur der Meldungstext ist unsichtbar | Zeichen der Kategorien Mn, Me, Cf und Default-Ignorable (z. B. U+FE00–FE0F, U+E0100–E01EF) nicht als sichtbar zählen; Test mit U+FE0F und U+20E3 |
| R3-01 | mittel | bestätigt: `https://u:p@h.invalid/a` passiert die Prüfung; urllib liest `p@h.invalid` als Port | Authority wird verschieden gelesen (wie R2-02/R2-03) | Abbruch mit `InvalidURL` vor dem Senden; kein Abruf an einem anderen Ursprung | `@` in der Authority in `robots_ok` ablehnen; Test, dass `holen` unaufgerufen bleibt |

Fehlalarme: 0. Beide Befunde sind fail-closed (kein unerlaubter Abruf), die Korrekturen sind je eine Zeile plus Test.

**Vorlage O22 (Besitzer):** (A) beide beheben, Tests rot→grün, schmale Runde 4 nur auf diesen Diff; (B) beide beheben ohne weitere Runde und als selbst geprüft vermerken; (C) als Restrisiko annehmen. Empfehlung: A, weil es eine bestätigte, offene „schwer“-Einstufung gibt und die Runde klein bleibt.

## Behebung (O22 = A, Besitzer 24.11.2026)

| ID | Behebung | Probe |
|---|---|---|
| R2-04a | `_sichtbar`: als sichtbar zählen nur Zeichen der Kategorien L, N, P, S ohne die Hangul-Füller (U+115F, U+1160, U+3164, U+FFA0); Mn/Me (U+FE0F, U+20E3, U+034F, U+E0100), Cf, Leerraum und Steuerzeichen ergeben „Sperrvermerk ohne Grund“ | `test_sperrvermerk_…`: U+FE0F, U+20E3, Hangul-Füller, U+034F + U+E0100 (vorher rot) |
| R3-01 | `robots_ok` lehnt `@` in der Authority ab (nach der `%`-Prüfung), `main` endet mit Exit 4 ohne Abruf | `test_port_null_…`: `u:p@`, `u@`, leerer Nutzerteil; `main` ruft `holen` nicht auf (vorher rot) |

Rot vor der Korrektur: 8 Fehlschläge in 2 Tests, grün danach (33 Tests). Nachprüfung: `auftrag-r4.md` (schmal, Diff ab 10d405f).
