# Entscheidungsvorlage Finder G1: drei Gestaltungspunkte (28.11.2026)

Methode: Impeccable ist in diesem Checkout nicht installiert (D21, `.claude/skills` fehlt); Empfehlungen sinngemäß nach `frontend-design` begründet (Struktur trägt Information, Zustand sichtbar machen, Bewegung nur als Antwort auf Bedienung, Text ohne Zusatzlabel). Nichts gebaut, keine neuen Fotos.

## (a) Fotos G1 freigeben
**Was:** Zehn Bildschirmfotos (375 px, hell/dunkel) in `docs/pruefungen/2026-11-24-finder-g1/fotos/`: `g1-{hell,dunkel}-1-oben`, `-2-empfehlung`, `-3-regler`, `-4-rangliste`, `-5-vergleich` (.png). Sie sollen belegen, wie G1 aussieht.
**Aktualität:** Nicht aktuell. Fotos vom 24.11. 14:17; danach änderte `app/finder/finder.js` noch die Prüfrunden r1 bis r3 (b7f5b24, a70332c, 0996e86, 65 Zeilen, u. a. Vergleich „gleichauf“ und Fokus). Seit 26.11. änderte sich nur `bewertung.js` (Rechnung P2a-1), keine Oberfläche. Die Fotos zeigen also einen Zwischenstand, nicht die Live-Seite.
**Optionen:** 1. Diese Fotos freigeben. 2. Live-Seite selbst auf dem Handy ansehen und freigeben. 3. Nach (b)/(c) einmal neu fotografieren, dann freigeben.
**Empfehlung:** Option 3 (sonst gibt der Besitzer einen Stand frei, den es nicht mehr gibt). Alte Fotos nur zur Orientierung nutzen. Aufwand: ein Lauf `fotos.mjs` über `lastsperre.ps1 -Klasse browser`, wenige Minuten.

## (b) „Alle Merkmale (10)“ ohne Auf/Zu-Marke (GS-1, P2)
**Was:** Der Aufklapp-Bereich unter Reglern und Punkteherkunft sieht aus wie Fließtext; nichts zeigt, dass man tippen kann oder ob er offen ist (Foto `g1-dunkel-3-regler.png`, unten).
**Optionen:** 1. So lassen. 2. Kleiner Pfeil rechts, der sich beim Öffnen dreht (reines CSS, `::after`). 3. „Mehr“/„Weniger“ im Text wechseln.
**Empfehlung:** Option 2, Pfeil an die Zeile rechts (wie die Stufenanzeige), Drehung kurz, bei „weniger Bewegung“ ohne Animation; dieselbe Marke auch für die zwei gleichartigen Bereiche („So kommt die Note zustande“, Methode), damit ein Zeichen überall dasselbe heißt. Grund: Zustand muss sichtbar sein, ohne ein zusätzliches Textlabel. Aufwand: klein, ca. 10 CSS-Zeilen in `finder.css` (Z. 207, 237, 423), kein JS; Foto-Neulauf deckt die Prüfung ab.

## (c) „gleichauf“ im Vergleich
**Was:** Der Vergleich nennt je Merkmal „gleichauf“ oder „Vorn: X +n“. Die Regel vergleicht nur die zwei besten Modelle. Beispiel Energieklasse (Foto `g1-dunkel-5-vergleich.png`): F, F, G steht „gleichauf“, obwohl das dritte Modell deutlich zurückliegt. Die Note-Zeile (80, 80, 78) hat gar keine Marke, die Rangliste darüber sagt aber „Gleichauf“.
**Optionen:** 1. Lassen (Ratgeber-Regel: nur Spitze zählt). 2. „gleichauf“ nur, wenn alle gewählten innerhalb von 2 Punkten liegen; sonst „Vorn: F-Modelle +n“ bzw. Namen der Spitzengruppe. 3. Wie 2 und Note-Zeile mit derselben Marke.
**Empfehlung:** Option 3. Grund: „gleichauf“ bei F/F/G ist für Laien falsch gelesen (alle drei), und Marke je Zeile muss überall gleich arbeiten; die Note-Zeile ist die wichtigste Zeile. Rangliste bleibt unverändert. Aufwand: klein bis mittel, ca. 15 Zeilen in `finder.js` (`vergleich`, um Z. 930), 2 bis 3 Tests, Codex-Prüfung nur mit Fokus Vergleichsregel (normal); vorher klären, ob die Ratgeber-Regel „Spitze“ bewusst so lautet (Quelle `kaufberatung.html`).

## Reihenfolge
(b) und (c) bauen, dann (a) neu fotografieren und freigeben. Zusammen etwa ein halber Arbeitstag inklusive Prüfung.
