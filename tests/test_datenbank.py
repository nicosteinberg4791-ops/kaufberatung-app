# -*- coding: utf-8 -*-
"""Tests für die Schranke werkzeuge/datenbank.py (Format-Schlüssel, Preisquellen nur als Link)."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "werkzeuge"))
import datenbank  # noqa: E402


def beispiel():
    """Kleinste gültige Fernseher-Datei (erfundene Werte, nur für den Test)."""
    return {
        "kategorie": "fernseher", "stand": "2026-11-21",
        "quellen": {"q1": {"url": "https://example.org/a", "titel": "Testquelle", "gelesen": "2026-11-21"}},
        "modelle": [{
            "id": "test-tv", "hersteller": "Test", "name": "TV",
            "werte": {"aufloesung": "4k"}, "belege": {"aufloesung": "q1"},
            "varianten": [{"id": "test-tv-55", "name": "55 Zoll",
                           "preis": {"eur": 500, "haendler": "Alternate", "url": "https://www.alternate.de/x", "stand": "2026-11-21"}}],
        }],
    }


class Schranke(unittest.TestCase):
    def pruefen(self, d):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "fernseher.json"
            p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            _, fehler, _ = datenbank.alle_pruefen([p])
        return fehler

    def test_gueltig(self):
        self.assertEqual(self.pruefen(beispiel()), [])

    def test_doppelte_variante_gleich_modell_id(self):
        d = beispiel()
        m = d["modelle"][0]
        v = copy.deepcopy(m["varianten"][0])
        v["id"] = m["id"]
        m["varianten"] = [v, copy.deepcopy(v)]
        self.assertTrue(any("doppelt" in f for f in self.pruefen(d)))

    def test_unbekannter_schluessel_in_variante(self):
        d = beispiel()
        d["modelle"][0]["varianten"][0]["listenpreis"] = {"eur": 1}
        self.assertTrue(any("listenpreis" in f for f in self.pruefen(d)))

    def test_unbekannter_schluessel_im_modell_und_preis(self):
        d = beispiel()
        d["modelle"][0]["notiz"] = "x"
        d["modelle"][0]["varianten"][0]["preis"]["hinweis"] = "x"
        f = self.pruefen(d)
        self.assertTrue(any("'notiz'" in x for x in f))
        self.assertTrue(any("'hinweis'" in x for x in f))

    def test_preisquelle_nur_link(self):
        gesperrt = datenbank.nur_link_domains()
        self.assertIn("www.mediamarkt.de", gesperrt)
        self.assertNotIn("www.saturn.de", gesperrt)
        d = beispiel()
        d["modelle"][0]["varianten"][0]["preis"]["url"] = "https://www.mediamarkt.de/de/product/_x-1.html"
        self.assertTrue(any("nur als Link" in f for f in self.pruefen(d)))

    def test_testlink_ohne_noten(self):
        """F-01: Testlinks nur mit url und titel; übernommene Punkte oder Texte sind Fehler."""
        d = beispiel()
        d["modelle"][0]["tests"] = [{"url": "https://example.org/test", "titel": "Test", "punkte": 90}]
        self.assertTrue(any("'punkte'" in f for f in self.pruefen(d)))
        d["modelle"][0]["tests"] = [{"url": "https://example.org/test", "titel": 5}]
        self.assertTrue(any("Testlink" in f for f in self.pruefen(d)))
        d["modelle"][0]["tests"] = {"url": "https://example.org/test"}
        self.assertTrue(any("tests" in f for f in self.pruefen(d)))
        d["modelle"][0]["tests"] = [{"url": "https://example.org/test", "titel": "Test"}]
        self.assertEqual(self.pruefen(d), [])

    def test_bau_gibt_nur_url_und_titel_aus(self):
        """F-01: Auch wenn eine Datei vorbei käme, schreibt der Bau nur url und titel."""
        d = beispiel()
        d["modelle"][0]["tests"] = [{"url": "https://example.org/test", "titel": "Test"}]
        aus = datenbank.testlinks(d["modelle"][0])
        self.assertEqual(aus, [{"url": "https://example.org/test", "titel": "Test"}])
        d["modelle"][0]["tests"][0]["punkte"] = 90
        self.assertEqual(datenbank.testlinks(d["modelle"][0]), [{"url": "https://example.org/test", "titel": "Test"}])

    def test_preis_nur_freigegebene_shops(self):
        """F-07: unbekannte Händler-Domain ist ein Fehler (Positivliste statt Sperrliste)."""
        d = beispiel()
        p = d["modelle"][0]["varianten"][0]["preis"]
        p["url"] = "https://www.irgendein-shop.de/tv"
        p["haendler"] = "Irgendein Shop"
        self.assertTrue(any("nicht freigegeben" in f for f in self.pruefen(d)))
        p["url"] = "https://preisvergleich.heise.de/x"   # Preisvergleich ist kein Shop
        self.assertTrue(any("nicht freigegeben" in f for f in self.pruefen(d)))

    def test_preis_haendlername_passt_zur_domain(self):
        d = beispiel()
        d["modelle"][0]["varianten"][0]["preis"]["haendler"] = "Saturn"   # URL ist Alternate
        self.assertTrue(any("Händler" in f for f in self.pruefen(d)))

    def test_herstellershop_nur_fuer_eigenen_hersteller(self):
        d = beispiel()
        p = d["modelle"][0]["varianten"][0]["preis"]
        p["url"], p["haendler"] = "https://www.samsung.com/de/tv/x/", "Samsung Deutschland"
        self.assertTrue(any("nicht freigegeben" in f for f in self.pruefen(d)))   # Hersteller „Test“
        d["modelle"][0]["hersteller"] = "Samsung"
        self.assertEqual(self.pruefen(d), [])
        p["url"] = "https://shop.samsung.com.example.org/x"
        self.assertTrue(any("nicht freigegeben" in f for f in self.pruefen(d)))

    def test_echte_daten_ohne_fehler(self):
        _, fehler, _ = datenbank.alle_pruefen()
        self.assertEqual(fehler, [])



class NurLinkHost(unittest.TestCase):
    def test_schreibweisen(self):
        g = {"www.mediamarkt.de"}
        for url in ["https://www.mediamarkt.de/a", "https://mediamarkt.de/a", "https://m.mediamarkt.de/a",
                    "https://www.mediamarkt.de./a", "https://x@www.saturn.de/a", "https://WWW.MEDIAMARKT.DE/a"]:
            self.assertTrue(datenbank.host_gesperrt(url, g), url)
        for url in ["https://www.saturn.de/a", "https://notmediamarkt.de/a"]:
            self.assertFalse(datenbank.host_gesperrt(url, g), url)


def echtes_schema():
    return json.loads(datenbank.SCHEMA.read_text(encoding="utf-8"))


class SchemaRegeln(unittest.TestCase):
    """P2a-1 (Entwurf §2.2, §2.3, §9.6, §9.7; Tests 2, 7–13, 44 Bau-Hälfte): Schema-Prüfung in datenbank.py."""

    def fehler(self, s):
        return datenbank.schema_fehler(s)

    def kat(self, s, kid="fernseher"):
        return next(k for k in s["kategorien"] if k["id"] == kid)

    def test_echtes_schema_ohne_fehler(self):
        self.assertEqual(self.fehler(echtes_schema()), [])
        self.assertEqual(echtes_schema()["schema_version"], 2)

    def test_schema_version_muss_2_sein(self):       # Test 2
        for v in (1, 3, "2", True, None):
            s = echtes_schema()
            s["schema_version"] = v
            self.assertTrue(any("schema_version" in f for f in self.fehler(s)), v)

    def test_testquelle_form(self):                  # Tests 7, 11, 12
        gut = {"name": "Beispieltester", "url": "https://example.org/test/x",
               "methodik_url": "https://example.org/so-testen-wir", "stand": "2026-11-24"}
        s = echtes_schema()
        self.kat(s)["testquelle"] = gut
        self.assertEqual(self.fehler(s), [])
        faelle = {"liste": [gut], "punkte": {**gut, "punkte": 90}, "ohne_url": {k: v for k, v in gut.items() if k != "url"},
                  "name_leer": {**gut, "name": ""}, "name_leerraum": {**gut, "name": "   "}, "name_81": {**gut, "name": "x" * 81},
                  "name_steuerzeichen": {**gut, "name": "a\tb"}, "stand_text": {**gut, "stand": "24.11.2026"},
                  "stand_zukunft": {**gut, "stand": "2999-01-01"}}
        for art, tq in faelle.items():
            with self.subTest(art=art):
                s = echtes_schema()
                self.kat(s)["testquelle"] = tq
                self.assertTrue(self.fehler(s), art)
        s = echtes_schema()
        self.kat(s)["testquelle"] = {**gut, "name": "😀" * 80}
        self.assertEqual(self.fehler(s), [])         # 80 Codepunkte (Emoji) gelten
        self.kat(s)["testquelle"] = {**gut, "name": "😀" * 81}
        self.assertTrue(self.fehler(s))

    def test_testquelle_urls(self):                  # Test 10
        gut = {"name": "T", "url": "https://example.org/a", "methodik_url": "https://example.org/b", "stand": "2026-11-24"}
        for schluessel in ("url", "methodik_url"):
            for url in ("http://example.org/a", "https://u:p@example.org/a", "https://example.org:8443/a",
                        "https://example.org:443/a", "javascript:alert(1)"):
                with self.subTest(schluessel=schluessel, url=url):
                    s = echtes_schema()
                    self.kat(s)["testquelle"] = {**gut, schluessel: url}
                    self.assertTrue(self.fehler(s), url)

    def test_zweite_testquelle_tippname(self):       # Test 9
        s = echtes_schema()
        self.kat(s)["testquellen"] = {"name": "x"}
        self.assertTrue(any("testquellen" in f for f in self.fehler(s)))

    def test_doppelter_schluessel_testquelle(self):  # Test 8
        text = datenbank.SCHEMA.read_text(encoding="utf-8")
        text = text.replace('"id": "fernseher",', '"id": "fernseher", "testquelle": {"name": "a"}, "testquelle": {"name": "b"},', 1)
        with tempfile.TemporaryDirectory() as t:
            pfad = Path(t) / "kategorien.json"
            pfad.write_text(text, encoding="utf-8")
            alt = datenbank.SCHEMA
            datenbank.SCHEMA = pfad
            try:
                with self.assertRaises(ValueError):
                    datenbank.lade_schema()
                _, fehler, _ = datenbank.alle_pruefen([])
                self.assertTrue(any("doppelter Schlüssel" in f for f in fehler))
            finally:
                datenbank.SCHEMA = alt

    def test_gewichte_version_form_wenn_vorhanden(self):   # Form in P2a-1, Pflicht und Vergleich in P2a-2
        s = echtes_schema()
        self.kat(s)["gewichte_version"] = {"nummer": 1, "stand": "2026-11-24"}
        self.assertEqual(self.fehler(s), [])
        for gv in ({"nummer": 0, "stand": "2026-11-24"}, {"nummer": "1", "stand": "2026-11-24"}, {"nummer": 1.5, "stand": "2026-11-24"},
                   {"nummer": True, "stand": "2026-11-24"}, {"nummer": 10000, "stand": "2026-11-24"},
                   {"nummer": 1, "stand": "24.11.2026"}, {"nummer": 1}, {"nummer": 1, "stand": "2026-11-24", "x": 1}, [1]):
            with self.subTest(gv=gv):
                s = echtes_schema()
                self.kat(s)["gewichte_version"] = gv
                self.assertTrue(self.fehler(s))

    def test_masse_namensregel(self):                # Test 13
        def mit(feld):
            s = echtes_schema()
            self.kat(s, "soundbar")["felder"].append({"id": "x", "name": "x", "einheit": "cm", "typ": "zahl", "gewicht": 0,
                                                       "kurve": {"art": "linear", "punkte": [[0, 0], [250, 0]]}, **feld})
            return self.fehler(s)
        self.assertTrue(mit({"id": "breite_cm", "einheit": "mm"}))                 # doppelt wäre ohnehin rot; Einheit zählt
        for fid in ("breite_mm", "hoehe", "tiefe_innen_cm", "hoehe_innen_cm", "breite"):
            with self.subTest(fid=fid):
                self.assertTrue(mit({"id": fid}), fid)
        self.assertEqual(mit({"id": "schwelle_mm"}), [])
        s = echtes_schema()
        soundbar = self.kat(s, "soundbar")
        feld = next(f for f in soundbar["felder"] if f["id"] == "breite_cm")
        feld["einheit"] = "mm"
        self.assertTrue(self.fehler(s))
        feld["einheit"] = "cm"
        feld["typ"] = "stufe"
        self.assertTrue(self.fehler(s))
        s = echtes_schema()
        self.kat(s, "geschirrspueler")["fragen"].append({"id": "breite", "text": "?", "antworten": []})   # Frage-ID breite bleibt grün
        self.assertFalse(any("breite" in f for f in self.fehler(s)))

    def test_stufenwert_200_codepunkte(self):        # Test 44 (Stufenwert)
        s = echtes_schema()
        feld = next(f for k in s["kategorien"] for f in k["felder"] if f["typ"] == "stufe")
        feld["kurve"]["punkte"].append(["😀" * 200, 50])
        self.assertEqual(self.fehler(s), [])
        feld["kurve"]["punkte"][-1][0] = "😀" * 201
        self.assertTrue(self.fehler(s))


class VertragMetadaten(unittest.TestCase):
    """Gemeinsamer Vertrag §9.6, Bau-Spalte; dieselben Fälle prüft test_bewertung.mjs für den Client (Test 44)."""

    def test_datum(self):
        for t, ok in (("2026-02-30", False), ("2019-12-31", False), ("2020-01-01", True), ("2999-01-01", False),
                      ("2026-01-01\n", False), ("2026-1-1", False)):
            self.assertEqual(datenbank.ist_datum(t), ok, t)

    def test_url(self):
        gut = ["https://example.org/a", "https://ab--c.de/", "https://sub.example.org/a?b=1#c", "https://example.org/" + "a" * 1980,
               # P2A1-01: 2000 Zeichen, die new URL umkodiert; der Client muss sie ebenso behalten (test_bewertung.mjs)
               "https://ab.de/?q=" + "'" * 1983, "https://ab.de/" + '"' * 1986, "https://ab.de/{" + "a" * 1985]
        schlecht = ["http://example.org/a", "https://u@example.org/a", "https://example.org:8443/a", "https://example.org:443/a",
                    "https://999.999.999.999/", "https://192.168.0.1/", "https://localhost/", "https://Example.org/a",
                    "https://example.org/ä", "https://example.org/a b", "https://xn--a.de/", "https://xn--mnchen-3ya.de/",
                    "https://example.org/" + "a" * 1981, "", "https://", "https://example.org/a\n", None, 5]
        for u in gut:
            self.assertTrue(datenbank.quell_url_ok(u), u)
        self.assertEqual(len("https://example.org/" + "a" * 1980), 2000)
        for u in schlecht:
            self.assertFalse(datenbank.quell_url_ok(u), u)

    def test_name(self):
        self.assertTrue(datenbank.name_ok("😀" * 200, 200))
        self.assertFalse(datenbank.name_ok("😀" * 201, 200))
        for x in (" ", " ", "", "a\tb", "a﻿b", "a b", "\ud800"):
            self.assertFalse(datenbank.name_ok(x, 200), repr(x))
        self.assertFalse(datenbank.name_ok(5, 200))

    def test_quellen_id(self):
        for q in ("quelle", "q1", "a-b"):
            self.assertTrue(datenbank.quellen_id_ok(q), q)
        for q in ("prototype", "constructor", "quelle\n", "Q1", "a_b", "", "-a", 5):
            self.assertFalse(datenbank.quellen_id_ok(q), q)


def kopf(d, kid="fernseher"):
    d = copy.deepcopy(d)
    d["kategorie"] = kid
    return d


class MasseUndQuellenInDatei(unittest.TestCase):
    """Test 14 (Produktwert Maße), Test 16 (Quell-URL im Bau), Quellen-ID und -Titel."""

    def pruefen(self, d, kid):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / f"{kid}.json"
            p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            _, fehler, _ = datenbank.alle_pruefen([p])
        return fehler

    def soundbar(self, **w):
        d = kopf(beispiel(), "soundbar")
        d["modelle"][0]["werte"] = w
        d["modelle"][0]["belege"] = {k: "q1" for k in w}
        return d

    def test_mass_wert_grenzen(self):                # Test 14
        for ok, w in ((False, -5), (False, 0), (False, 501), (False, "60"), (False, True), (True, 60), (True, 500), (True, 0.5)):
            with self.subTest(w=w):
                fehler = self.pruefen(self.soundbar(breite_cm=w), "soundbar")
                self.assertEqual(fehler == [], ok, (w, fehler))

    def test_quell_url_userinfo_rot(self):           # Test 16
        for url in ("https://u:p@example.org/a", "http://example.org/a", "https://example.org:8443/a", "https://999.999.999.999/"):
            d = beispiel()
            d["quellen"]["q1"]["url"] = url
            self.assertTrue(any("Quelle q1" in f for f in self.pruefen(d, "fernseher")), url)

    def test_quellen_id_und_titel(self):
        for qid in ("prototype", "constructor", "quelle\n"):
            d = beispiel()
            d["quellen"] = {qid: d["quellen"]["q1"]}
            d["modelle"][0]["belege"] = {"aufloesung": qid}
            self.assertTrue(any("Quellen-ID" in f for f in self.pruefen(d, "fernseher")), repr(qid))
        for titel in (" ", "a\tb", "x" * 201):
            d = beispiel()
            d["quellen"]["q1"]["titel"] = titel
            self.assertTrue(any("Quelle q1" in f for f in self.pruefen(d, "fernseher")), repr(titel))
        d = beispiel()
        d["quellen"]["q1"]["titel"] = "😀" * 200
        self.assertEqual(self.pruefen(d, "fernseher"), [])


class BauMetadaten(unittest.TestCase):
    """Test 15: Bau gibt gewichte_version, testquelle, quellen (nur mit Verweis) und belege (§9.4) aus."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        t = Path(self.tmp.name)
        s = echtes_schema()
        k = next(k for k in s["kategorien"] if k["id"] == "fernseher")
        k["gewichte_version"] = {"nummer": 1, "stand": "2026-11-24"}
        k["testquelle"] = {"name": "Beispieltester", "url": "https://example.org/t", "methodik_url": "https://example.org/m",
                           "stand": "2026-11-24"}
        (t / "kategorien.json").write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
        (t / "produkte").mkdir()
        self.alt = (datenbank.SCHEMA, datenbank.PRODUKTE)
        datenbank.SCHEMA, datenbank.PRODUKTE = t / "kategorien.json", t / "produkte"
        self.addCleanup(lambda: setattr(datenbank, "SCHEMA", self.alt[0]))
        self.addCleanup(lambda: setattr(datenbank, "PRODUKTE", self.alt[1]))
        self.ziel = t / "aus.json"

    def bauen(self, d):
        (datenbank.PRODUKTE / "fernseher.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        _, fehler, _ = datenbank.bauen(self.ziel)
        self.assertEqual(fehler, [])
        return json.loads(self.ziel.read_text(encoding="utf-8"))

    def fernseher(self, aus):
        return next(k for k in aus["kategorien"] if k["id"] == "fernseher")

    def test_fassung_und_testquelle(self):
        aus = self.bauen(beispiel())
        k = self.fernseher(aus)
        self.assertEqual(k["gewichte_version"], {"nummer": 1, "stand": "2026-11-24"})
        # P2A1-02 (Test 44): Freigabe nach dem Produktdatenstand (stand später als d.stand, nicht in der Zukunft) → gültig
        self.assertEqual(aus["stand"], "2026-11-21")
        self.assertGreater(k["gewichte_version"]["stand"], aus["stand"])
        self.assertGreater(k["testquelle"]["stand"], aus["stand"])
        self.assertEqual(sorted(k["testquelle"]), ["methodik_url", "name", "stand", "url"])
        andere = next(x for x in self.bauen(beispiel())["kategorien"] if x["id"] == "akkusauger")
        self.assertNotIn("gewichte_version", andere)     # fehlt im Schema → fehlt in der Ausgabe
        self.assertNotIn("testquelle", andere)

    def test_quellen_nur_mit_verweis_und_drei_schluessel(self):
        d = beispiel()
        d["quellen"]["q2"] = {"url": "https://example.org/b", "titel": "Unbenutzt", "gelesen": "2026-11-21"}
        k = self.fernseher(self.bauen(d))
        self.assertEqual(list(k["quellen"]), ["q1"])
        self.assertEqual(sorted(k["quellen"]["q1"]), ["gelesen", "titel", "url"])

    def test_belege_aus_derselben_ebene_wie_der_wert(self):   # §9.4
        d = beispiel()
        d["quellen"]["qa"] = {"url": "https://example.org/a", "titel": "A", "gelesen": "2026-11-21"}
        d["quellen"]["qb"] = {"url": "https://example.org/b", "titel": "B", "gelesen": "2026-11-21"}
        m = d["modelle"][0]
        m["werte"], m["belege"] = {"aufloesung": "4k"}, {"aufloesung": "qa"}
        v1 = m["varianten"][0]
        v1["belege"] = {"aufloesung": "qb"}                         # Beleg ohne eigenen Wert → nicht übernommen
        v2 = copy.deepcopy(v1)
        v2["id"], v2["name"] = "test-tv-65", "65 Zoll"
        v2["werte"], v2["belege"] = {"aufloesung": "8k"}, {"aufloesung": "qb"}   # eigener Wert und Beleg
        m["varianten"].append(v2)
        k = self.fernseher(self.bauen(d))
        ein = {x["id"]: x for x in k["modelle"]}
        self.assertEqual((ein["test-tv-55"]["werte"]["aufloesung"], ein["test-tv-55"]["belege"]["aufloesung"]), ("4k", "qa"))
        self.assertEqual((ein["test-tv-65"]["werte"]["aufloesung"], ein["test-tv-65"]["belege"]["aufloesung"]), ("8k", "qb"))
        self.assertEqual(sorted(k["quellen"]), ["qa", "qb"])

    def test_belege_nur_fuer_vorhandene_werte(self):
        k = self.fernseher(self.bauen(beispiel()))
        for m in k["modelle"]:
            self.assertTrue(set(m["belege"]) <= set(m["werte"]))


if __name__ == "__main__":
    unittest.main()
