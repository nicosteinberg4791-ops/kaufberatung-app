# Prüfauftrag: Pilot Bestpreis-Mix (D7), Nachprüfung Runde 5

**Ziel:** Prüfen, ob die r4-Befunde D7-02, D7-11 und D7-15 behoben sind, ohne neue Fehler einzuführen. Runde 5 auf Besitzerentscheid (22.11.2026). D7-05 ist Besitzerentscheid und nicht Prüfgegenstand.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“
- `python -I -B -m unittest discover -s tests -t tests -p test_shopabfrage.py` → OK (64 Tests)
- Unvollständige Übertragung (Content-Length, chunked ohne vollständigen Abschluss) = nicht abrufbar; robots.txt dann nicht lesbar = Quelle nicht abfragen.
- Ausdrückliche Captcha-/Roboter-Aufforderungen im sichtbaren Text sperren die Quelle, unabhängig von Inhaltstyp, Position und Auszeichnung; robots.txt-Anweisungen, Skripte und inaktive Vorlagen sperren nicht.
- Saturn: Eigenangebot nur, wenn alle Preisobjekte der Ziel-SKU (jede Feldfolge) lesbar sind und übereinstimmen (kein Marktplatz, gleicher Preis); andere Merkmale derselben SKU stören nicht.

**Dateien (Diff ab Basis):** `werkzeuge/shopabfrage.py` (Z. 55–70, `mms_preisfeld` Z. 249–305, `ist_challenge`/`sichtbarer_text` Z. 415–432, `_StrengeAntwort` bis `abrufen` Z. 441–525) · `tests/test_shopabfrage.py` (`Runde3` D7-02-Test, Klasse `Runde4` ab Z. 644).

**Selbstprüfung:** alle-tests Fehler 0. `Runde4`-Tests und erweiterter D7-02-Test schlagen gegen 6a62c59 fehl. Lokaler Livelauf 22.11.2026: Saturn S90H 1.399 € Eigenangebot (echte Seite mit Liefer-, Abhol- und Medienobjekten derselben SKU), Alternate/Proshop/heise ok.

**Bekannte Grenzen:** `_StrengeAntwort` überschreibt die interne Methode `HTTPResponse._read_and_discard_trailer` (der Test sichert das Verhalten). Ohne Content-Length und ohne chunked ist ein Abbruch nicht erkennbar. Sperrtexte sind eine feste Liste (deutsch/englisch); unbekannte Formulierungen ohne technische Merkmale werden nicht erkannt. Objekte mit eigenem Nicht-Preis-Typ direkt vor der id werden ohne Dekodierung übersprungen. O12/O13 entscheidet der Besitzer.

**Prüffragen**
1. Kann eine unvollständige HTTP-Übertragung noch als vollständige robots.txt oder Produktseite gelten, oder lehnt die strenge Antwortklasse gültige Antworten ab?
2. Kann ein Saturn-Marktplatz- oder widersprüchliches Angebot noch als Eigenangebot gelten, oder wird das echte Eigenangebot fälschlich verworfen?
3. Sperrt `ist_challenge` eine normale Produktseite fälschlich oder übersieht es eine ausdrückliche Aufforderung im sichtbaren Text?
