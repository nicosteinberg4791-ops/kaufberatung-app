# VER-02: Historie von persönlichen Angaben bereinigen (Analyse, 28.11.2026)

Nur gelesen, nichts umgeschrieben. Muster: `<vorname>`, `<konto>`, Pfad `Users\<vorname>`. Gezählt auf origin/main (241 Commits) und origin/gh-pages (69).

## Befund
- Aktueller Stand sauber: `git grep -iE '<vorname>|<konto>' origin/main` und `origin/gh-pages` = 0 Treffer (Befehl je Ref).
- Dateistände mit Treffer (Schleife `git rev-list <ref>` + `git grep -q` je Commit): main 232 von 241; gh-pages 32 von 69.
  - Vorname: main 223, gh-pages 32 (u. a. Gewichtssatz und Handy-Bezug in `index.html`, `app.js`, `sw.js`).
  - Kontoname: main 71, gh-pages 27. Pfad `Users\<vorname>`: main 122, gh-pages 0.
- Commits, die die Angabe ändern (`git log -G`): main 107 (Vorname), 13 (Konto), 9 (Pfad); gh-pages 11 / 2 / 0.
- Dateiarten (`git log -G ... --name-only`, main): `.md` 169 (STATUS.md 77, Prüfberichte, Aufträge, offene Punkte), `.py` 11, `.html` 10, `.mjs`/`.js` 8, `.yml` 3, `.txt` 4, Hook 2.
- Commit-Nachrichten: main 2 (`00bfb96`, `e7a30fa`), gh-pages 0. Autor/Committer: nur `Kaufberatung`, Bot und `Test` mit `.invalid`-Adressen, keine Person.
- Offen noch: lokaler Commit `0634588` (nicht gepusht, enthält den Pfad), Zweig `origin/claude/paket-abruf-dead7c`.
- Repo öffentlich, 0 Forks, 0 Sterne, 0 Pull Requests, 0 Tags (`gh api`).

## Was eine Bereinigung braucht
- `git filter-repo` fehlt (`git filter-repo --version` = kein Git-Befehl); Installation wäre Entscheidung des Besitzers. Ohne: `git filter-branch` (veraltet, langsam, hier aber bei ~310 Commits machbar).
- Ersetzen per Textliste (Pfad, Konto, Vorname) in allen Dateien, plus `--message-callback` für 2 Nachrichten, auf allen Zweigen.
- Force-Push main und gh-pages; Schutzregeln prüfen. Alle 310 Commit-Hashes ändern sich.
- Folgen: Hash-Bezüge in STATUS.md, Prüfberichten und Aufträgen (137 Dateien mit 40-stelligen SHAs) zeigen ins Leere; `version.json` (App-Hash `cd6f226225dc`) und `finder-daten.json` (`herkunft` 8a41085) müssen neu gebaut werden.
- `herkunft.py` und `freigabe.py` prüfen, dass der alte Herkunfts-SHA Vorfahre ist (`merge-base --is-ancestor`); nach Umschreiben schlägt das fehl, die Workflows `finder-daten.yml` und `preise.yml` stoppen, bis die Herkunft einmal manuell neu gesetzt ist. `veroeffentlichen.py` verlangt HEAD in origin/main: erst nach Neu-Push wieder erfüllt.
- Ersetzung von Texten wie "Gewichtssatz <vorname>" ändert Inhalt und App-Hash; gh-pages-Inhalt neu bauen und prüfen (Codex, Prüfpunkt kritisch).
- GitHub behält alte Objekte: per SHA weiter abrufbar, Pull-Request-Refs und Caches bleiben; echte Löschung nur über GitHub Support. Wirkung daher teilweise.

## Optionen
| Option | Aufwand | Risiko | Wirkung |
|---|---|---|---|
| A Nichts tun (Stand VER-02) | 0 | keins | Angaben bleiben abrufbar, Art schon vorhanden |
| B Umschreiben + Force-Push | 3-5 h, Prüfrunde | hoch (Herkunftsketten, Workflows, Hash-Bezüge) | Zweige sauber, alte SHAs weiter abrufbar bis Support-Löschung |
| C Neues Repo, gequetschte Historie (ein Commit je Zweig) | 1-2 h + Prüfung | mittel: Pages-URL ändert sich | Alte Historie weg, wenn altes Repo gelöscht wird; sauberste Lösung |
| D Nur lokal `0634588` vorher bereinigen | – | – | entfällt: 0634588 ist seit dem Push vom 28.11.2026 (8a41085) öffentlich (Lead-Prüfung `git merge-base --is-ancestor`) |

Option C: neue Pages-URL, installierte PWAs (Scope an Ursprung gebunden) bleiben auf der alten Adresse, bis Nutzer neu installieren; Push-Abos, `kb-app:besitzer` und Wunschpreise (localStorage) gehen verloren. Alte Seite kann nicht weiterleiten, wenn das Repo gelöscht ist. Der Kontoname bleibt in jeder GitHub-URL, auch in C, außer bei Konto- oder Org-Wechsel: das ist nur über Umbenennen/Neuanlegen unter anderem Konto lösbar (Pages-URL ändert sich ebenfalls, kein Redirect).

## Empfehlung
A (nichts tun), solange der Besitzer die Angaben nicht als Schaden sieht: Vorname und Konto sind schon öffentlich (auch in der URL), 0 Forks. Wird dennoch bereinigt, C statt B. (D entfällt, siehe Tabelle; Korrektur des Leads.)
