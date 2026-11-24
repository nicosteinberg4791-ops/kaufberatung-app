# Bewertung Codex r1 (medium, Basis 33fa490, Stand 54052c3)

Bericht: `codex-erst-20261124-145514.json` · Urteil: nicht bestanden (schwer 2, mittel 3).

| Befund | Schwere | Einordnung | Klasse | Suche | Korrektur | Probe |
|---|---|---|---|---|---|---|
| G1-01 Regler fehlt nach Adresswechsel (`a=ton.ja` → ohne) | schwer | bestätigt (DOM-Test reproduziert) | Teil-Neuaufbau ohne Abgleich der Feldauswahl | `rg "reglerAnzeigen\|reglerPanel" app/finder` → nur der schnelle Pfad in `zeichne()` | `reglerFelder()`/`reglerStand`; schneller Pfad nur bei gleicher Feldauswahl, sonst Neuaufbau | `G1-01` (auch Rückweg und „ohne Feldwechsel dasselbe Element“) |
| G1-02 fehlender Wert als „0 Punkte“ vorgelesen | schwer | bestätigt (bewertung.js nimmt `fehlend` aus dem Mittel) | zugänglicher Name widerspricht der Rechnung | `rg "0 Punkte" app/finder` → 1 Treffer | `aria-label` „nicht angegeben“ | `G1-02` |
| G1-03 Vergleich „gleichauf“ bei 83 vs 80 angezeigt | mittel | bestätigt | Abstand aus ungerundeten Werten | `rg "d >= 3" app/finder` → Rangliste rechnet schon gerundet | `tpVon` liefert gerundete Teilpunkte | `G1-03` (Vorn +3 und gleichauf 80/82) |
| G1-04 Beobachter behält entfernte Karten | mittel | bestätigt | `disconnect()` nur bei neuen Karten | `rg "glasBeobachter" app/finder` | `disconnect()` immer zuerst und beim Schirmwechsel | `G1-04` (Neurechnen ohne Karten, Budgetschirm) |
| G1-05 Bewegungsreduktion erst nach Neuladen | mittel | bestätigt | Einstellung einmal beim Laden gelesen | `rg "reduziert" app/finder` → 2 Stellen | `reduziert()` fragt jedes Mal (FLIP, Scrollen) | `G1-05` (Kontrolle mit Animation, dann reduziert ohne) |

Proben: `node --test tests/test_finder_dom.mjs tests/test_bewertung.mjs` → 68/68 grün; gegen `finder.js` aus 54052c3: genau G1-01…G1-05 rot (27 grün, 5 rot).
