# Bewertung Codex r5 – Finder-Veröffentlichung (22.11.2026)

Bericht: `codex-nach-20261122-103338.json` (Codex gpt-6.2-sol high, Stand ae72e55, 307 s) · Urteil: nicht bestanden · geschlossen R3-01, R3-05, R4-02, R4-04, R4-05, R4-06, R4-07 · offen R4-01, R4-03 (Folgebefunde R5-01…R5-04) · neu R5-05.
Einordnung nach Skill `pruefschleife` Schritt 5, nur am Code belegt; **noch nichts behoben** (Runde 5 über Rundenlimit, Runde 6 nur mit Entscheid des Besitzers).

| ID | Schwere | Einordnung | Beleg und Korrekturvorschlag |
|---|---|---|---|
| R5-01 | schwer | bestätigt (Code: `stempel_schreiben` öffnet mit `"w"` und leert damit den Startstempel; `sperre_holen` liest eine leere Datei über `or 0` als 0 → kein Warten) | Stempel atomar schreiben (Hilfsdatei + `os.replace`), leere oder unlesbare Stempel als „gerade eben“ behandeln (voller Abstand). Test: Abbruch zwischen Leeren und Schreiben. |
| R5-02 | schwer | bestätigt (Code: `baum_eintraege` verwirft den Git-Modus; gleiche Blob-ID als Datei und als symbolischer Link besteht) | Modus, Typ und ID gemeinsam vergleichen; Bauartefakte nur `100644`, Preisdateien mit vollem Eintrag des Elterncommits. Test: Moduswechsel bei gleicher Blob-ID. Praktisch nur durch einen fremden Vorgang im Seitenbaum erreichbar. |
| R5-03 | schwer | bestätigt (Code: Push ohne Lease; wird gh-pages auf einen Vorgänger von `eltern` zurückgesetzt, ist der neue Commit trotzdem ein Fast-Forward) | `git push --force-with-lease=refs/heads/gh-pages:<eltern>` (nur wenn das Ziel genau `eltern` ist; der Commit bleibt Kind von `eltern`). Test: Ziel zurückgesetzt und gelöscht. Praktisch nur durch einen fremden Eingriff auf GitHub erreichbar. |
| R5-04 | schwer | bestätigt (Code: `app_bauen.baue` kopiert `app/`, `quelle/`, `daten/` aus dem Arbeitsbaum; die Sauberkeitsprüfungen davor und danach sehen eine vorübergehende Änderung nicht) | Veröffentlichungsbau aus einer eigenen Kopie genau des geprüften Commits (`git worktree add --detach <head>` in ein Temp-Verzeichnis oder `git archive`). Test: Datei während des Baus ändern und zurücksetzen. Praktisch nur durch gleichzeitiges Bearbeiten im Arbeitsbaum erreichbar. |
| R5-05 | mittel | bestätigt (Code: `robots_ok` gibt nur `teile.hostname` weiter; Ablage und Abruf der robots.txt ohne Port) | robots.txt und Ablage an Schema, Host und effektiven Port binden; Domainsperre bleibt je Host. Test mit Port 8443. Die gepflegten Shop-URLs haben keinen Port. |

Fehlalarme: 0 von 5. Keine bewusste Entscheidung, nichts ungeklärt.
Muster: R5-02…R5-04 setzen einen gleichzeitig und gezielt eingreifenden fremden Vorgang voraus (lokal oder auf GitHub); R5-01 ist ein echtes Abbruchfenster von wenigen Mikrosekunden. Alle Korrekturen sind klein und gut testbar.

**Behebung (Runde 6, vom Besitzer beauftragt, O16):** R5-01 Stempel atomar (Hilfsdatei, `fsync`, `os.replace`), leer/unlesbar/zukünftig = voller Abstand (`letzter_abruf`); R5-02 Vergleich von Modus, Typ und ID, Bauartefakte nur `100644`, Link im Bau bricht ab; R5-03 Push mit `--force-with-lease=refs/heads/gh-pages:<eltern>`; R5-04 Bau aus `git archive` des geprüften Commits mit dessen eigenem Bauskript als Prozess (`app_bauen.py --ziel --herkunft`); R5-05 robots.txt und Ablage je Schema, Host und effektivem Port. Je ein Test rot vor, grün nach der Korrektur. Nachprüfung: `auftrag-r6.md`.
