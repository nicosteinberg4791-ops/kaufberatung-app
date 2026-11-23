# Bewertung Codex r2 (Nachprüfung, high, Basis 8cb198d, Stand 2d14798)

Bericht: `codex-nach-20261123-142906.json` · Urteil nicht bestanden · geschlossen: A2-02, A2-03 (A3 seit r1).

| Nr. | Schwere | Einordnung | Klasse | Vorschlag |
|---|---|---|---|---|
| A1-01 | kritisch | ungeklärt → Besitzer: technisch richtig, setzt aber einen fremden lokalen Prozess voraus, der den Eintrag des eigenen `mkdtemp`-Verzeichnisses im Elternordner gegen Link/Junction tauscht | Rennen mit feindlichem lokalem Prozess (TOCTOU auf Verzeichniseinträge) | Bedrohungsmodell festlegen: lokales Werkzeug eines Nutzers, kein feindlicher Prozess mit Schreibrecht im Elternordner → Restrisiko annehmen |
| R2-01 | schwer | ungeklärt → Besitzer: Windows-`rmdir` entfernt eine untergeschobene Junction auf einen belegten Ordner | wie A1-01 | wie A1-01 |
| A2-01 | schwer | bestätigt: `os.path.lexists` liefert auch bei `PermissionError` `False`, Wartezeit entfällt | Vorhandensein über eine Prüfung, die Fehler als „fehlt“ meldet | `os.lstat` mit `FileNotFoundError` = fehlt, jeder andere `OSError` = voller Abstand; Test mit `PermissionError` |
| R2-02 | mittel | bestätigt: Bauverzeichnis kann bei Löschfehler oder Abbruch zwischen `mkdtemp` und `try` liegen bleiben (nur eigener Rest, keine fremden Daten) | Aufräumen ohne Meldung | `try` um `mkdtemp` ziehen, Löschfehler melden statt verschlucken |
| R2-03 | mittel | bestätigt: scheitert `os.rename` nach `os.rmdir`, fehlt danach das zuvor leere Ziel | nicht wiederhergestellter Zwischenzustand | leeres Ziel nach Fehlschlag neu anlegen oder Ziel nur „neu“ (nicht vorhanden) zulassen |
| R2-04 | mittel | bewusste Entscheidung (außerhalb des Umfangs): `gesperrt_bis` wertet einen Link ohne Ziel als „nicht gesperrt“, schon in `bewertung-r1.md` an den Besitzer gemeldet | wie A2-01 | eigenes kleines Paket zusammen mit A2-01 |

Nicht behoben, Entscheidung offen (KERN §3, Muster „jede Korrektur zeigt eine neue Stelle“).
