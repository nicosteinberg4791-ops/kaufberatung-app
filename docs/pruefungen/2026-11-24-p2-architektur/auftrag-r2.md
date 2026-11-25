# Nachprüfung r2 – Architektur P2 Notenmodell (high, nach)

**Ziel:** Prüfen, ob die Korrekturen zu P2-01 … P2-11 (Bewertung `bewertung-r1.md`) im Entwurf `docs/recherche-ux/p2-entwurf.md` die Befunde schließen, ohne neue Widersprüche zu erzeugen.

**Prüfgegenstand:** nur der Diff von `docs/recherche-ux/p2-entwurf.md` ab `bf48f2d`: neuer §9 (Z. 195–Ende) und die Verweise darauf in §1, §2.1, §2.3, §2.4, §3, §4, §5, §6 und §8 (A-2, A-3, A-6, A-9). Abgleich mit dem Code nur dort, wo §9 sich darauf stützt: `app/finder/bewertung.js` (`gewichte`, `bewerteModell`, `auswerten`, `datenPruefen`, `sichereUrl`), `app/finder/finder.js:185–240`, `:450–460`, `app/sw.js`, `werkzeuge/datenbank.py:40–120`, `:186–206`, `:310–330`, `.github/workflows/finder-daten.yml`, `werkzeuge/herkunft.py`, `daten/schema/kategorien.json`.

**Fertigkriterien**
- Jeder der 11 Befunde ist durch die genannte Korrektur geschlossen (oder der Rest ist benannt).
- §9.3 (Referenzvergleich): Kein Weg, die Gewichte zu ändern, ohne dass die Nummer steigen muss. Das gilt in CI und lokal sowie für Antwort-ID und Reihenfolge. Fehlt die Referenz, bricht der Lauf ab.
- §9.2: Das Orakel liefert für jede angezeigte Antwort dieselbe Note, die `auswerten` mit dieser Antwort für das Modell rechnen würde, auch wenn das Modell `passt "nein"` hat.
- §9.1: Die Fassungsliste lässt sich aus `origin/gh-pages` mit dem genannten Befehl reproduzieren.
- §9 widerspricht §2–§8 nirgends still; wo er vorgeht, steht das dort als Verweis.

**Selbstprüfung (Lead):** Alle Befunde sind am Code nachgelesen (Spalte „Gegenprobe“ in `bewertung-r1.md`). Der Node-Abgleich `datenPruefen` je gh-pages-Fassung gegen drei Datenstände ist in §9.1 notiert. Der Hook lief beim Commit `d429afc` ohne Fehler (unittest, node --test, Geheimnis-Scan). Gebaut ist nichts.

**Bekannte Grenzen:** F-1 … F-5 sind beim Besitzer offen, bitte nicht entscheiden. Die Beobachtung zum Worker von `b24c18f` (lehnt die Live-Daten seit `a7434dd` ab) liegt außerhalb von P2. Der Wortlaut der Ansicht gehört zu P2b.

**Prüffragen (Klassenfrage je Korrektur):**
1. §9.3: Ist die Projektion vollständig, also wirkt jedes notenwirksame Schema-Element darin mit? Oder fehlt etwas, etwa `nicht_anwendbar`-Regeln, `mindest`/`hoechst` oder Faktoren aus Antworten?
2. §9.3: Ist der CI-Schritt „Referenz vor dem Bau“ mit `herkunft.py` und `fetch-depth: 0` umsetzbar, ohne dass der Workflow beim ersten Lauf (Referenz ohne `gewichte_version`) dauerhaft rot bleibt?
3. §9.5/§9.7: Stimmen die Nenner und die Maßregel mit dem Datenbestand überein? Falsch-positive Fälle bei bestehenden Feld-IDs wären ein Befund.
4. Gibt es weitere Stellen der Klassen aus `bewertung-r1.md` (Spalte „Klasse“), die §9 nicht erfasst?
