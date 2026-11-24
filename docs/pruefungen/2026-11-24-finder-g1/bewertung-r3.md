# Bewertung Codex r3 (medium, nach, Basis b7f5b24, Stand a70332c)

Bericht: `codex-nach-20261124-155951.json` · Urteil: bestanden mit Hinweisen (kritisch 0, schwer 0, mittel 2) · gpt-6.2-sol medium, 266 s, Eingabe 1,45 Mio. (ungecacht 149 Tsd.), Ausgabe 3,6 Tsd. G1-R2-01…04 geschlossen (Mutanten und Fälle von Codex nachvollzogen).

| Befund | Schwere | Einordnung | Klasse | Suche | Vorschlag Lead |
|---|---|---|---|---|---|
| G1-R3-01 Neuaufbau erhält den offenen Bereich, aber nicht den Fokus auf seiner Überschrift (`summary` ohne `data-fokus`, `finder.js:681`) | mittel | ungeklärt → Nico: am Code bestätigt (`grep -n '"summary"' app/finder/finder.js` → Z. 480, 681, 753, alle ohne `data-fokus`); tritt nur auf, wenn eine Bereichsüberschrift fokussiert ist und die Adresse wechselt (Zurück, Link) | Fokusziel ohne stabilen Schlüssel | 3 Treffer (s. links) | beheben: Schlüssel je `summary`, `fokusFreilegen` öffnet den eigenen Bereich eines fokussierten `summary` nicht; Probe wie G1-R2-01 |
| G1-R3-02 Beim Verlassen des Ergebnisses fehlt der FLIP-Abbruch (`finder.js:1005`) | mittel | ungeklärt → Nico: am Code bestätigt (voller Neuaufbau in `zeichne()` ruft `gleitenStoppen()` nicht); die Bewegung läuft dann nur noch auf entfernten, nicht gezeichneten Einträgen höchstens 240 ms weiter, sichtbar ist nichts | Bewegung ohne Abbruch bei Schirmwechsel | `grep -n "gleitenStoppen" app/finder/finder.js` → Aufrufe nur in `rangGleiten` und im `change`-Hörer | beheben (eine Zeile neben `glasBeobachter.disconnect()` in `zeichne()`), Probe: Schirmwechsel mit laufender Bewegung |
