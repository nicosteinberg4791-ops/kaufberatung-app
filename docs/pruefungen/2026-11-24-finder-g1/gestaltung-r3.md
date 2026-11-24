# Gestaltungsprüfung Finder-Ergebnisschirm (Regler, Rangliste, Vergleich), Stand a70332c

Methode: Impeccable ist im Hauptcheckout nicht installiert (`.claude/skills/impeccable` fehlt; im Worktree `admiring-pasteur-32f79f` nur leere Ordner, wie in `docs/recherche-ux/07-ux-audit.md` vermerkt). Neu installieren hieße ein Netzpaket holen; das blieb dem Besitzer vorbehalten (D21). „Critique“ und „Audit“ sind deshalb sinngemäß angewendet: Gesamturteil und Hierarchie aus Bildschirmansicht, prüfbare Einzelpunkte mit Messung. Schwere P0 (blockiert) bis P3 (Feinschliff).

Ansicht: eingebauter Browser, 375 × 812, dunkel, `dist/` aus `app_bauen.py` (App b1b009f1d93f), Adresse `#k=fernseher&s=ergebnis&b=1000&v=lg-oled-b6-55~lg-oled-c6-48`, Service Worker vorher abgemeldet.

## Critique

Die Reihenfolge Empfehlung → Regler → Rangliste → Vergleich trägt: Die Note bleibt das große Element, die Regler sind ruhig (Name links, Stufe und Anteil rechts, eine Spur), die Rangliste zeigt Punkte als Zahl und Bahn, der Vergleich nennt jedes Modell in jeder Bahn als Text. Farbe trägt nie allein Bedeutung. Keine Dekoration, die mit der Bedienung konkurriert.

## Audit

| Punkt | Messung | Ergebnis |
|---|---|---|
| Tippziele (Knöpfe, Chips, Regler, `summary`) | Höhe < 44 px gezählt | 0 |
| Querrollbahn | `scrollWidth` | 375 = Fensterbreite |
| Konsole | Fehler | keine |
| Fokus nach Neuaufbau (G1-R2-01) | Regler in „Alle Merkmale“ fokussiert, Adresse mit/ohne `a=ton.ja` | Panel neu gebaut, Bereich offen, Fokus und Stufe 4 bleiben |
| Punkteherkunft beim Ziehen | `hz-mehr` offen, Regler bewegt | bleibt offen |
| Fokusring | `.regler-spur:focus-visible` | 3 px Ring vorhanden |

## Befunde

| Nr. | Schwere | Befund | Vorschlag |
|---|---|---|---|
| GS-1 | P2 | „Alle Merkmale (10)“ (Regler und Punkteherkunft) hat keine sichtbare Auf/Zu-Marke: `summary { display: flex }` blendet den Pfeil aus, kein Ersatz in `::before`/`::after` | Pfeil-Symbol, das sich beim Öffnen dreht (bestand schon vor dieser Runde, außerhalb des Auftrags) |
| GS-2 | P3 | Vergleich „Note“: Bei gleicher Punktzahl fehlt die Marke „gleichauf“, die die Merkmalsblöcke haben | mit Frage (c) an Nico („gleichauf“ bei F/F/G) entscheiden |

Kein offener P0/P1.
