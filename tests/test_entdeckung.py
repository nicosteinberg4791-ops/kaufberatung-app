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


class AbgleichSchreibweisen(unittest.TestCase):
    """Zusatzprüfung 22.11.: Shoptitel mit Ordinalzahl, deutschem Gattungswort, TM und MPN ohne Länderendung
    (Namen erfunden, Aufbau wie die verpassten Treffer der Entdeckung vom 22.11.2026)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = {"kategorie": "kopfhoerer_overear", "stand": "2026-11-21", "quellen": {}, "modelle": [
            {"id": "acme-pods-pro-3", "hersteller": "Acme", "name": "Pods Pro 3", "varianten": [{"id": "a1", "name": "x"}]},
            {"id": "acme-qc-hp", "hersteller": "Acme", "name": "QuietSound Headphones", "varianten": [{"id": "a2", "name": "x"}]},
            {"id": "acme-qc-ultra-hp-2", "hersteller": "Acme", "name": "QuietSound Ultra Headphones (2. Gen.)",
             "varianten": [{"id": "a3", "name": "x"}]},
            {"id": "acme-v9", "hersteller": "Acme", "name": "V9 Detect Slim", "varianten": [{"id": "a4", "name": "x"}]},
            {"id": "acme-bar", "hersteller": "Acme", "name": "Q-Serie HW-Q900XY", "varianten": [{"id": "a5", "name": "x", "mpn": "HW-Q900XY/ZG"}]},
            {"id": "acme-fry", "hersteller": "Acme", "name": "Tower CAF-DC100S-DEUR", "varianten": [{"id": "a6", "name": "x", "mpn": "CAF-DC100S-DEUR"}]},
            {"id": "acme-na35", "hersteller": "Acme", "name": "Fryer 3000 Serie NA351", "varianten": [{"id": "a7", "name": "x", "mpn": "NA351/00"}]},
        ]}
        (Path(self.tmp.name) / "kopfhoerer_overear.json").write_text(json.dumps(d), encoding="utf-8")
        self.idx = en.bestand_index(self.tmp.name)["kopfhoerer_overear"]

    def tearDown(self):
        self.tmp.cleanup()

    def z(self, name):
        return en.zuordnen({"name": name}, self.idx)

    def test_ordinalzahl(self):
        self.assertEqual(self.z("ACME Pods Pro (3rd generation), In-ear Weiß"), "acme-pods-pro-3")
        self.assertIsNone(self.z("ACME Pods Pro (2nd generation)"))

    def test_kopfhoerer_heisst_headphones_und_spezifisch_gewinnt(self):
        self.assertEqual(self.z("ACME QuietSound Ultra Kopfhörer (2. Gen.) – kabellos"), "acme-qc-ultra-hp-2")
        self.assertEqual(self.z("ACME QuietSound Kopfhörer Schwarz"), "acme-qc-hp")

    def test_tm_am_wort(self):
        self.assertEqual(self.z("ACME V9 DetectTM Slim kabellos"), "acme-v9")

    def test_mpn_ohne_laenderendung_und_ohne_fuellwort(self):
        self.assertEqual(self.z("ACME HW-Q900XY 11.1.4-Kanal Soundbar"), "acme-bar")
        self.assertEqual(self.z("ACME CAF-DC100S-DDER Tower"), "acme-fry")
        self.assertEqual(self.z("ACME NA351/00 Fryer 3000 Series"), "acme-na35")
        self.assertIsNone(self.z("ACME NA3510 Fryer"), "kein Treffer mitten in einer Zahl")
        self.assertIsNone(self.z("ACME HW-Q910XY Soundbar"))


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

    def test_sperre_auch_ohne_itemlist(self):
        """F-05: Seite ohne verwertbare ItemList reserviert die Woche trotzdem."""
        def leer(url):
            self.abrufe.append(url)
            return "<html>keine Liste</html>"
        erg, _ = self.laufen(holen=leer)
        self.assertEqual(len(self.abrufe), 1)
        self.assertIn("versucht", erg["kategorien"]["fernseher"])
        self.laufen(holen=leer, jetzt=JETZT + dt.timedelta(hours=1))
        self.assertEqual(len(self.abrufe), 1, "kein zweiter Abruf innerhalb von 6 Tagen")
        self.laufen(jetzt=JETZT + dt.timedelta(days=7))
        self.assertEqual(len(self.abrufe), 4)

    def test_sperre_auch_bei_abbruch_im_abruf(self):
        def bricht(url):
            self.abrufe.append(url)
            raise SystemExit(6)
        self.laufen(holen=bricht)
        self.laufen(holen=bricht, jetzt=JETZT + dt.timedelta(days=1))
        self.assertEqual(len(self.abrufe), 1)

    def test_paralleler_lauf_ruft_nichts_ab(self):
        """F-05/R2-06: hält ein anderer Lauf die Betriebssystem-Sperre, endet ein zweiter sofort mit Exit 4;
        eine liegengebliebene Sperrdatei ohne Inhaber (Absturz) hält nichts auf."""
        halter = en.sperre_holen(self.ziel)
        self.assertIsNotNone(halter)
        try:
            self.assertIsNone(en.sperre_holen(self.ziel), "zweiter Inhaber unmöglich")
            _, code = self.laufen()
            self.assertEqual((code, self.abrufe), (4, []))
        finally:
            en.sperre_freigeben(halter)
        self.assertTrue(Path(str(self.ziel) + ".lock").exists(), "Datei bleibt liegen (wie nach Absturz)")
        _, code = self.laufen()
        self.assertEqual(code, 0, "Datei ohne Inhaber wird übernommen")
        self.assertEqual(len(self.abrufe), 3)

    def test_vorhandener_ungueltiger_zeitstempel_sperrt(self):
        """R2-05: vorhandenes Feld mit "", 0, false, null oder Objekt sperrt; ebenso ein Eintrag, der kein Objekt ist."""
        for w in ("", 0, False, None, {}, [], 5):
            self.assertTrue(en.zu_frueh({"kategorien": {"fernseher": {"versucht": w}}}, "fernseher", JETZT), repr(w))
        for k in ("x", 0, [], True):
            self.assertTrue(en.zu_frueh({"kategorien": {"fernseher": k}}, "fernseher", JETZT), repr(k))
        self.assertTrue(en.zu_frueh({"kategorien": []}, "fernseher", JETZT))
        self.assertFalse(en.zu_frueh({"kategorien": {"fernseher": {"quelle": "x"}}}, "fernseher", JETZT))

    def test_unlesbare_ergebnisdatei_ruft_nichts_ab(self):
        """R2-05 (gleiche Fehlerklasse): kaputte Ergebnisdatei gilt nicht als leer, sondern sperrt den Lauf."""
        self.ziel.parent.mkdir(parents=True, exist_ok=True)
        self.ziel.write_text('{"kategorien": {"fernseher": {"versucht": "2026-11-2', encoding="utf-8")
        _, code = self.laufen()
        self.assertEqual((code, self.abrufe), (4, []))
        self.assertTrue(self.ziel.read_text(encoding="utf-8").endswith("2026-11-2"), "Datei bleibt unverändert")

    def test_unlesbarer_zeitstempel_sperrt(self):
        self.assertTrue(en.zu_frueh({"kategorien": {"fernseher": {"versucht": "gestern"}}}, "fernseher", JETZT))
        self.assertFalse(en.zu_frueh({"kategorien": {}}, "fernseher", JETZT))

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


class RoutineGit(unittest.TestCase):
    """F-03: echte Git-Repos (temporär): jeder neue Commit zählt, gepusht wird genau der geprüfte Commit."""

    def setUp(self):
        import os
        import subprocess
        self.sp = subprocess
        # Im Pre-Commit-Hook setzt Git GIT_INDEX_FILE u. a.: ohne Bereinigung schrieben die Wegwerf-Repos in den
        # Index des echten Arbeitsbaums. Für die Testdauer alle GIT_*-Variablen entfernen (auch für routine.git).
        sauber = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
        self.umgebung = unittest.mock.patch.dict(os.environ, sauber, clear=True)
        self.umgebung.start()
        self.addCleanup(self.umgebung.stop)
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.origin, self.klon = t / "origin.git", t / "klon"
        self.g("init", "-q", "--bare", "-b", "main", str(self.origin), cwd=t)
        self.g("clone", "-q", str(self.origin), str(self.klon), cwd=t)
        for k, v in (("user.name", "Test"), ("user.email", "test@example.invalid"), ("core.autocrlf", "false")):
            self.g("config", k, v)
        self.schreibe("daten/produkte/fernseher.json", json.dumps({"modelle": [{"id": "m1", "varianten": [{"id": "v1"}]}]}))
        self.schreibe("werkzeuge/x.py", "x = 1")
        self.commit("Start")
        self.g("push", "-q", "origin", "HEAD:main")

    def tearDown(self):
        self.tmp.cleanup()

    def g(self, *a, cwd=None):
        r = self.sp.run(["git", *a], cwd=cwd or self.klon, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def schreibe(self, pfad, text):
        p = self.klon / pfad
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))

    def commit(self, msg):
        self.g("add", "-A")
        self.g("commit", "-q", "-m", msg)
        return self.g("rev-parse", "HEAD")

    def pruefen(self, schranken=lambda w: []):
        with unittest.mock.patch("builtins.print"):
            return routine.pruefen(True, wurzel=self.klon, schranken=schranken)

    def main_auf_origin(self):
        return self.g("rev-parse", "main", cwd=self.origin)

    def test_zwischencommit_mit_fremder_datei_ist_rot(self):
        self.schreibe("geheim.txt", "nicht veroeffentlichen")
        self.commit("fremd")
        (self.klon / "geheim.txt").unlink()
        self.schreibe("daten/produkte/fernseher.json", json.dumps({"modelle": [{"id": "m1", "varianten": [{"id": "v1"}]}, {"id": "m2"}]}))
        self.commit("zurück und Daten")
        vorher = self.main_auf_origin()
        self.assertEqual(self.pruefen(), 1)
        self.assertEqual(self.main_auf_origin(), vorher, "nichts gepusht")

    def test_gepusht_wird_der_gepruefte_commit(self):
        self.schreibe("daten/produkte/fernseher.json", json.dumps({"modelle": [{"id": "m1", "varianten": [{"id": "v1"}]}, {"id": "m2"}]}))
        sha = self.commit("Daten")

        def schranken_mit_parallelem_commit(w):
            self.schreibe("werkzeuge/x.py", "x = 2")
            self.commit("parallel")
            return []
        self.assertEqual(self.pruefen(schranken_mit_parallelem_commit), 1, "HEAD hat sich bewegt")
        self.assertNotEqual(self.main_auf_origin(), sha)
        self.g("reset", "-q", "--hard", sha)
        self.assertEqual(self.pruefen(), 0)
        self.assertEqual(self.main_auf_origin(), sha)

    def test_unversionierte_datei_ist_rot(self):
        self.schreibe("daten/produkte/fernseher.json", json.dumps({"modelle": [{"id": "m1", "varianten": [{"id": "v1"}]}, {"id": "m2"}]}))
        self.commit("Daten")
        self.schreibe("notiz.txt", "x")
        self.assertEqual(self.pruefen(), 1)


if __name__ == "__main__":
    unittest.main()
