# Prüfauftrag: Pilot Bestpreis-Mix (D7), Nachprüfung Runde 4

**Ziel:** Prüfen, ob die r3-Befunde D7-02, D7-09, D7-11 und D7-14 behoben sind, ohne neue Fehler einzuführen. D7-05 ist ein Besitzerentscheid (`docs/entscheidungen.md`, D7-Nachtrag) und wird nicht erneut geprüft.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“
- `python -I -B -m unittest discover -s tests -t tests -p test_shopabfrage.py` → OK (62 Tests)
- robots.txt live gelesen, nicht lesbar oder unvollständig übertragen = Quelle nicht abfragen; 403/429/503/Challenge/ausdrückliche Captcha-Aufforderung = Quelle für den Lauf gesperrt; passive robots.txt-Pfade sperren nicht.
- Saturn: Eigenangebot nur bei eindeutigem Preisfeld (kein Marktplatz, gleicher Preis); widersprüchliche oder doppelte Felder = kein Nachweis.
- heise-Treffer dürfen den Bestpreis stellen (Besitzerentscheid 21.11.2026); eigene Shopangebote haben bei Preisgleichheit Vorrang.
- Keine persönlichen Daten, Pfade, Konto-URLs oder fremden Shoptexte in versionierten Dateien (Repo öffentlich).

**Dateien (Diff ab Basis):** `werkzeuge/shopabfrage.py` (Kopf Z. 55–70, `_ohne_doppelte`/`mms_preisfeld` Z. 230–290, `ist_challenge`/`abrufen`/`robots_fuer` Z. 400–475) · `tests/test_shopabfrage.py` (Klasse `Runde3`, Vorlagentest Z. 91–96) · `tests/vorlagen/*.html` · `docs/pruefungen/2026-11-21-pilot-bestpreis/*` (nur auf Shoptexte/Kontopfade prüfen).

**Selbstprüfung:** alle-tests Fehler 0, Warnungen 0. Die 3 neuen `Runde3`-Tests schlagen gegen fed7378 fehl. Lokaler Livelauf 21.11.2026: Saturn S90H weiter 1.399 € Eigenangebot, Alternate/Proshop/heise ok. Geheimnis-Scan 0 Funde.

**Bekannte Grenzen:** Ohne Content-Length und ohne chunked ist ein Abbruch nicht erkennbar (Verbindungsende = Körperende). Eine Dublette in einem vor dem Zielobjekt stehenden Nachbarobjekt verwirft den Saturn-Nachweis ebenfalls (bewusst vorsichtig). Alte Vorlagen in der öffentlichen Historie (79daf34) entscheidet der Besitzer (O13). Saturn/Proshop sperren GitHub-Runner (403), nicht umgangen (O12).

**Prüffragen**
1. Kann eine gekürzte oder abgebrochene Antwort (200, chunked) noch als vollständige robots.txt oder Produktseite gelten?
2. Erkennt `ist_challenge` ausdrückliche Captcha-Seiten unabhängig von Inhaltstyp und Position, ohne normale Produktseiten oder robots.txt fälschlich zu sperren?
3. Kann ein Saturn-Objekt mit doppelten oder widersprüchlichen Feldern noch als Eigenangebot gelten?
4. Stehen in versionierten Dateien des Diffs noch Shoptexte, Kontopfade oder persönliche Daten?
