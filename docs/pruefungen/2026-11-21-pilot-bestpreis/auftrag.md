# Prüfauftrag: Pilot Bestpreis-Mix (D7), Erstprüfung

**Ziel:** Prüfen, ob die lokale Shopabfrage nur legal freigegebene Quellen abfragt, gültige Angebote streng nach den Regeln wählt und der Workflow-Entwurf gefahrlos auf `main` gepusht werden kann.

**Fertigkriterien**
- `powershell -File tests/alle-tests.ps1` → „Fehler: 0“
- `python -I -B -m unittest discover -s tests -t tests -p test_shopabfrage.py` → OK (44 Tests)
- Nur Quellen mit `"automatisch": true` werden abgerufen; robots.txt live gelesen, nicht lesbar = Quelle nicht abfragen; 403/429/503/Challenge = Quelle für den Lauf gesperrt, nie umgangen.
- Angebot gültig nur bei passender EAN, NewCondition (oder fehlend), InStock, EUR, Preis im Korridor, Verkäufer = Shop (Saturn: Nachweis über eingebettetes Preisfeld, Marktplatz verworfen).
- Je Angebot `quelle`, `haendler`, `preis`, `versand`, `versand_herkunft`, `link`, `zeit`; Bestpreis ohne Dubletten.
- `pilot-preise.yml`: nur `workflow_dispatch`, `contents: read`, kein Push, berührt `preise.json`/Preiswecker/Push nicht.
- Keine persönlichen Daten, Pfade, Konto-URLs oder fremden Shoptexte in versionierten Dateien (Repo öffentlich).

**Dateien:** `werkzeuge/shopabfrage.py` (ganz) · `daten/quellen.json` · `daten/pilot_modelle.json` · `tests/test_shopabfrage.py` · `tests/vorlagen/*.html` · `.github/workflows/pilot-preise.yml` · `.gitignore` (letzte 3 Zeilen). Referenz nur lesend: `werkzeuge/preiswecker.py` Funktion `auswerten`.

**Selbstprüfung:** alle-tests.ps1 Fehler 0, Warnungen 0; Livelauf 21.11.2026 lieferte für alle 5 Modelle Preis, Quelle, Link, Zeit; ein Fehlalarm (Challenge-Erkennung auf Saturns robots.txt) gefunden und mit Test behoben.

**Bekannte Grenzen:** Rechtliche Einstufung ist Recherchestand, keine Rechtsberatung. heise automatisch nach Besitzerentscheid 21.11.2026 (über `preiswecker.auswerten`). robotparser kennt keine Wildcards: abgefangen über `gesperrte_pfade` und Query-Verbot. Vorprüfung (Sonnet) erledigt: Weiterleitung, robots-Name, `--zeige`-Abruf, mehrdeutiger Versand, Streichpreis, Händlernamen in Vorlage behoben; Actions nur per Tag gebunden wie `preise.yml` (bewusst). Saturn-Nachweis hängt am Seitenformat (Regex auf eingebettetem Zustand). Versand ohne JSON-LD-Angabe bleibt „unbekannt“.

**Prüffragen**
1. Gibt es einen Pfad, auf dem eine nicht freigegebene Quelle oder eine von robots.txt gesperrte URL doch abgerufen wird (auch Wiederholung, Weiterleitung auf andere Domain)?
2. Kann ein Marktplatz-, Gebraucht- oder nicht lieferbares Angebot als gültig durchrutschen (v. a. Saturn-Preisfeld, Varianten-SKU, ProductGroup)?
3. Ist `bestpreis()` korrekt (Dubletten, Angebote ohne Versand, Vorrang eigen vor heise)?
4. Ist der Workflow sicher und minimal (Rechte, Timeout, Artefakt, keine Secrets)?
5. Enthalten die Vorlagen oder Daten etwas, das im öffentlichen Repo nicht stehen darf?
