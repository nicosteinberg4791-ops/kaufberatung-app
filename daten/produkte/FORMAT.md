# Format der Produktdatenbank (`daten/produkte/<kategorie>.json`)

Eine Datei je Kategorie aus `daten/schema/kategorien.json` (Feld `id`). UTF-8, gültiges JSON, 1 Leerzeichen Einzug.
Prüfen: `python -I werkzeuge/datenbank.py pruefen` (alle Dateien) oder `… pruefen daten/produkte/fernseher.json`.

```json
{
 "kategorie": "fernseher",
 "stand": "2026-11-21",
 "quellen": {
  "lg-c6-datenblatt": {"url": "https://www.lg.com/de/…", "titel": "LG OLED evo C6 Datenblatt", "gelesen": "2026-11-21"}
 },
 "modelle": [
  {
   "id": "lg-oled-c6",
   "hersteller": "LG",
   "name": "OLED evo C6",
   "jahr": 2026,
   "werte":  {"bildtechnik": "oled", "bildwiederholrate_hz": 144, "vrr": true},
   "belege": {"bildtechnik": "lg-c6-datenblatt", "bildwiederholrate_hz": "lg-c6-datenblatt", "vrr": "lg-c6-datenblatt"},
   "tests": [{"url": "https://…", "titel": "Testbericht (nur Link)"}],
   "varianten": [
    {
     "id": "lg-oled65c6elb",
     "name": "65 Zoll",
     "mpn": "OLED65C6ELB",
     "ean": ["8806096000000"],
     "werte":  {"diagonale_zoll": 65, "energieklasse_sdr": "F"},
     "belege": {"diagonale_zoll": "lg-c6-datenblatt", "energieklasse_sdr": "lg-c6-datenblatt"},
     "preis": {"eur": 1668.99, "haendler": "Alternate", "url": "https://www.alternate.de/…", "stand": "2026-11-21"}
    }
   ]
  }
 ]
}
```

## Regeln (prüft `werkzeuge/datenbank.py`)

- `werte` nur mit Feld-IDs der Kategorie. Typ `zahl` = Zahl, `bool` = true/false, `stufe` = einer der Stufenwerte aus der Kurve (genau so geschrieben).
- **Jeder Wert braucht einen Beleg:** `belege[feld]` nennt eine ID aus `quellen`; jede Quelle hat `url` (https), `titel`, `gelesen` (JJJJ-MM-TT). Unbekannte Werte weglassen, nie schätzen.
- Werte, die je Variante abweichen (Größe, Speicher, Energieklasse je Diagonale), stehen in der Variante; Variantenwerte überschreiben Modellwerte.
- `id` von Modellen und Varianten: Kleinbuchstaben, Ziffern, Bindestrich; über alle Kategorien eindeutig.
- `preis` optional (null = „Preis unbekannt“). Wenn gesetzt: `eur` 1–100000, `haendler`, `url` (https, Produktseite), `stand`. Nur Neuware, Verkäufer = Shop selbst (kein Marktplatz), lieferbar. Preisquellen: Saturn, Alternate, Proshop (freigegeben in `daten/quellen.json`) oder der Herstellershop selbst; Domains mit `automatisch: false` dort (MediaMarkt, idealo) sind Fehler. Andere Händler nicht ohne Freigabe.
- Nur die Schlüssel aus dem Beispiel oben (Modell: `id`, `hersteller`, `name`, `jahr`, `werte`, `belege`, `tests`, `varianten`; Variante: `id`, `name`, `mpn`, `ean`, `werte`, `belege`, `preis`); andere Schlüssel (z. B. `listenpreis`) sind Fehler.
- `tests`: nur Links auf Testberichte, keine übernommenen Noten oder Texte.
- Keine persönlichen Daten, keine Konto-URLs, keine kopierten Shop- oder Herstellertexte (nur Fakten).
- Abdeckung (Anteil der Gewichte mit belegtem Wert) unter 70 % = Warnung; solche Modelle bekommen keine Note.
