# -*- coding: utf-8 -*-
"""Tests für werkzeuge/entdeckung.py (D10) und werkzeuge/datenpflege/routine.py (D11), ohne Netz und ohne Git-Aufrufe.
Alle Produktnamen und Nummern sind erfunden."""
import datetime as dt
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "werkzeuge"))
sys.path.insert(0, str(WURZEL / "werkzeuge" / "datenpflege"))
import entdeckung as en  # noqa: E402
import routine  # noqa: E402

JETZT = dt.datetime(2026, 11, 22, 6, 0, tzinfo=dt.timezone.utc)


def bestand(ordner):
    d = {"kategorie": "fernseher", "stand": "2026-11-21", "quellen": {}, "modelle": [
        {"id": "acme-x9", "hersteller": "Acme", "name": "Vision X9", "varianten": [
            {"id": "acme-x9-55", "name": "55 Zoll", "mpn": "55X9AB", "ean": ["4000000000017"]}]},
        {"id": "acme-q2", "hersteller": "Acme", "name": "Q2", "varianten": [
            {"id": "acme-q2-65", "name": "65 Zoll", "mpn": "QN65Q2XZ", "ean": []}]}]}
    (Path(ordner) / "fernseher.json").write_text(json.dumps(d), encoding="utf-8")


def seite(namen, start=0):
    items = [{"@type": "ListItem", "position": i + 1, "item": {
        "@type": "Product", "name": n, "offers": {"@type": "Offer", "price": 999, "priceCurrency": "EUR"},
        "url": f"https://www.saturn.de/de/product/_x-{1000 + start + i}.html"}} for i, n in enumerate(namen)]
    return ('<html><script type="application/ld+json">'
            + json.dumps({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": items})
            + "</script></html>")


class Abgleich(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        bestand(self.tmp.name)
        self.idx = en.bestand_index(self.tmp.name)["fernseher"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_mpn_im_namen(self):
        self.assertEqual(en.zuordnen({"name": "ACME QN65Q2XZ Fernseher (65 Zoll)"}, self.idx), "acme-q2")

    def test_hersteller_und_modellname_mit_groessenpraefix(self):
        # andere Länder-MPN, aber Hersteller + alle Namenswörter vorhanden
        self.assertEqual(en.zuordnen({"name": "ACME 65X9ZZ Vision X9 (65 Zoll)"}, self.idx), "acme-x9")

    def test_ean(self):
        self.assertEqual(en.zuordnen({"name": "irgendwas", "gtin": ["4000000000017"]}, self.idx), "acme-x9")

    def test_neues_modell_ist_kandidat(self):
        self.assertIsNone(en.zuordnen({"name": "ACME Vision X10 (65 Zoll)"}, self.idx))
        self.assertIsNone(en.zuordnen({"name": "Fremd Q2 (65 Zoll)"}, self.idx), "Hersteller muss passen")

    def test_itemlist_nur_saturn_produkte_ohne_preis(self):
        t = seite(["A 1"]).replace("https://www.saturn.de/de/product/", "https://example.org/")
        self.assertEqual(en.itemlist(t), [])
        it = en.itemlist(seite(["A 1"]))
        self.assertEqual(set(it[0]), {"name", "url", "gtin"})


class Lauf(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        bestand(self.tmp.name)
        self.ziel = Path(self.tmp.name) / "out" / "kandidaten.json"
        self.abrufe = []

    def tearDown(self):
        self.tmp.cleanup()

    def holen(self, url):
        self.abrufe.append(url)
        n = len(self.abrufe)
        return seite([f"ACME Neu{n} TV", "ACME QN65Q2XZ Q2 TV"], start=n * 10)

    def laufen(self, holen=None, robots=lambda u: (True, ""), jetzt=JETZT, seiten=3):
        with unittest.mock.patch("builtins.print"):
            return en.lauf(["fernseher"], seiten, holen or self.holen, robots, ziel=self.ziel,
                           produkte=self.tmp.name, jetzt=jetzt)

    def test_hoechstens_drei_seiten_und_ergebnis_ohne_preise(self):
        erg, code = self.laufen()
        self.assertEqual(code, 0)
        self.assertEqual(len(self.abrufe), 3)
        self.assertTrue(self.abrufe[0].endswith("4k-fernseher-2301.html"))
        self.assertTrue(self.abrufe[2].endswith("?page=3"))
        k = erg["kategorien"]["fernseher"]
        self.assertEqual((k["gelesen"], k["bekannt"], len(k["kandidaten"])), (6, 3, 3))
        self.assertNotIn("999", self.ziel.read_text(encoding="utf-8"), "keine Preise speichern (§ 87b)")
        self.assertEqual(set(k["kandidaten"][0]), {"name", "url", "saturn_nr"})

    def test_woechentlich_sperre(self):
        self.laufen()
        self.abrufe.clear()
        self.laufen(jetzt=JETZT + dt.timedelta(days=5))
        self.assertEqual(self.abrufe, [], "innerhalb von 6 Tagen kein neuer Abruf")
        self.laufen(jetzt=JETZT + dt.timedelta(days=7))
        self.assertEqual(len(self.abrufe), 3)

    def test_sperre_der_domain_beendet_lauf(self):
        def gesperrt(url):
            raise SystemExit(3)
        erg, code = self.laufen(holen=gesperrt)
        self.assertEqual(code, 3)
        self.assertIn("Exit 3", erg["kategorien"]["fernseher"]["letzter_fehler"]["fehler"][0])

    def test_robots_verbot(self):
        erg, _ = self.laufen(robots=lambda u: (False, "robots.txt verbietet den Pfad"))
        self.assertEqual(self.abrufe, [])
        self.assertIn("robots", erg["kategorien"]["fernseher"]["letzter_fehler"]["fehler"][0])

    def test_sperre_bei_robots_txt_beendet_ohne_stempel(self):
        def robots(url):
            raise SystemExit(3)
        erg, code = self.laufen(robots=robots)
        self.assertEqual(code, 3)
        self.assertNotIn("abgerufen", erg["kategorien"]["fernseher"], "ohne Abruf keine Wochensperre")
        self.laufen(jetzt=JETZT + dt.timedelta(minutes=40))
        self.assertEqual(len(self.abrufe), 3, "nach Sperre ist ein späterer Lauf erlaubt")

    def test_cli_grenzen(self):
        with unittest.mock.patch("builtins.print"):
            self.assertEqual(en.main(["--seiten", "4"]), 2)
            self.assertEqual(en.main(["--kategorie", "gibtsnicht"]), 2)

    def test_alle_app_kategorien_haben_eine_saturn_seite(self):
        schema = json.loads((WURZEL / "daten" / "schema" / "kategorien.json").read_text(encoding="utf-8"))
        kats = schema if isinstance(schema, list) else schema["kategorien"]
        self.assertEqual({k["id"] for k in kats}, set(en.KATEGORIEN))
        for pfad in en.KATEGORIEN.values():
            self.assertRegex(pfad, r"^[a-zA-Z0-9%-]+-\d+\.html$")


class Schranke(unittest.TestCase):
    ALT = json.dumps({"modelle": [{"id": "m1", "varianten": [{"id": "v1"}, {"id": "v2"}]}]})

    def test_nichts_geloescht(self):
        neu = json.dumps({"modelle": [{"id": "m1", "varianten": [{"id": "v1"}, {"id": "v2"}]}, {"id": "m2"}]})
        self.assertEqual(routine.geloescht({"daten/produkte/a.json": self.ALT}, {"daten/produkte/a.json": neu}), [])

    def test_variante_modell_und_datei_geloescht(self):
        neu = json.dumps({"modelle": [{"id": "m1", "varianten": [{"id": "v1"}]}]})
        v = routine.geloescht({"daten/produkte/a.json": self.ALT, "daten/produkte/b.json": self.ALT},
                              {"daten/produkte/a.json": neu})
        self.assertIn("daten/produkte/a.json: variante:v2 fehlt", v)
        self.assertIn("Datei fehlt: daten/produkte/b.json", v)
        v2 = routine.geloescht({"daten/produkte/a.json": self.ALT}, {"daten/produkte/a.json": '{"modelle": []}'})
        self.assertIn("daten/produkte/a.json: modell:m1 fehlt", v2)

    def test_kaputtes_json_zaehlt_als_verlust(self):
        v = routine.geloescht({"daten/produkte/a.json": self.ALT}, {"daten/produkte/a.json": "{kaputt"})
        self.assertEqual(len(v), 3)

    def test_nur_produktdateien_erlaubt(self):
        self.assertEqual(routine.fremde_pfade(["daten/produkte/fernseher.json"]), [])
        for p in ["daten/produkte/FORMAT.md", "daten/schema/kategorien.json", "werkzeuge/datenbank.py",
                  ".github/workflows/finder-daten.yml", "daten/produkte/../quellen.json"]:
            self.assertEqual(routine.fremde_pfade([p]), [p], p)


if __name__ == "__main__":
    unittest.main()
