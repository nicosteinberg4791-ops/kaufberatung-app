# -*- coding: utf-8 -*-
"""Tests für die Schranke werkzeuge/datenbank.py (Format-Schlüssel, Preisquellen nur als Link)."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
        s = echtes_schema()   # Frage-ID breite bleibt grün (P2a-2: gültige, eindeutige Frage, sonst greifen die Vorbedingungen)
        self.kat(s, "fernseher")["fragen"].append({"id": "breite", "text": "?", "antworten": [{"id": "a", "text": "a"}]})
        self.assertEqual(self.fehler(s), [])

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

    def test_bau_schreibt_lf(self):
        """VER-03: finder-daten.json endet mit LF und enthält kein CR, auf jeder Plattform (Abnahme vergleicht SHA-256)."""
        self.bauen(beispiel())
        roh = self.ziel.read_bytes()
        self.assertTrue(roh.endswith(b"}\n"))
        self.assertNotIn(b"\r", roh)

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
        self.assertEqual(andere["gewichte_version"], {"nummer": 1, "stand": FASSUNG1_STAND})   # P2a-2: Pflicht, Fassung 1
        self.assertNotIn("testquelle", andere)           # fehlt im Schema → fehlt in der Ausgabe

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


FASSUNG1_STAND = "2026-11-26"   # F-1: Fassung 1 = heutige Werte, vom Besitzer am 26.11.2026 freigegeben


def kat_von(s, kid="fernseher"):
    return next(k for k in s["kategorien"] if k["id"] == kid)


def feld_von(s, fid, kid="fernseher"):
    return next(f for f in kat_von(s, kid)["felder"] if f["id"] == fid)


def referenz():
    """Echtes Schema als Referenz mit Schema 2 und älterem Stand, damit ein Kandidat einen neuen Stand setzen kann."""
    s = echtes_schema()
    for k in s["kategorien"]:
        k["gewichte_version"] = {"nummer": 1, "stand": "2026-11-01"}
    return s


def hochzaehlen(s, *kids, stand="2026-11-25"):
    for k in s["kategorien"]:
        if not kids or k["id"] in kids:
            k["gewichte_version"] = {"nummer": k["gewichte_version"]["nummer"] + 1, "stand": stand}
    return s


def _mit_nummer(s, nummer, kid="fernseher", stand="2026-11-25"):
    kat_von(s, kid)["gewichte_version"] = {"nummer": nummer, "stand": stand}
    return s


class Gewichtsfassung(unittest.TestCase):
    """P2a-2 (Entwurf §2.1, §9.1, §9.3, §9.9): Pflicht der Fassung, Projektion, Referenzvergleich, Vorbedingungen."""

    def vergleich(self, kandidat, ref):
        return datenbank.fassung_gegen_fehler(kandidat, ref)

    def rot(self, kandidat, ref, art):
        self.assertTrue(self.vergleich(kandidat, ref), art)

    def gruen(self, kandidat, ref, art):
        self.assertEqual(self.vergleich(kandidat, ref), [], art)

    def test_pflicht_und_fassung_1(self):            # Test 3, F-1
        s = echtes_schema()
        for k in s["kategorien"]:
            self.assertEqual(k.get("gewichte_version"), {"nummer": 1, "stand": FASSUNG1_STAND}, k["id"])
        self.assertEqual(datenbank.schema_fehler(s), [])
        del kat_von(s)["gewichte_version"]
        self.assertTrue(any("fernseher" in f and "gewichte_version" in f for f in datenbank.schema_fehler(s)))

    def test_referenzvergleich(self):                # Test 6
        ref = referenz()
        self.gruen(copy.deepcopy(ref), ref, "unverändert")
        faelle = {
            "gewicht": lambda s: feld_von(s, "bildtechnik").update(gewicht=31),
            "faktor": lambda s: kat_von(s)["fragen"][0]["antworten"][0]["gewichte"].update(bildtechnik=1.4),
            "kurvenpunkt": lambda s: feld_von(s, "bildtechnik")["kurve"]["punkte"][0].__setitem__(1, 99),
        }
        for art, aendern in faelle.items():
            with self.subTest(art=art):
                k = copy.deepcopy(ref); aendern(k)
                self.rot(k, ref, art + " bei gleicher Nummer")
                self.gruen(hochzaehlen(copy.deepcopy(k), "fernseher"), ref, art + " mit Nummer + 1 und neuem Stand")
                self.rot(hochzaehlen(copy.deepcopy(k), "fernseher", stand="2026-11-01"), ref,
                         art + " mit Nummer + 1, aber altem Stand")
        k = copy.deepcopy(ref)
        k["datenblatt_abschlag"]["anker"] = 51          # betrifft alle Kategorien
        fehler = self.vergleich(k, ref)
        self.assertEqual(len([f for f in fehler if "Nummer" in f]), len(ref["kategorien"]), fehler)
        self.gruen(hochzaehlen(copy.deepcopy(k)), ref, "anker mit neuer Nummer überall")
        self.rot(hochzaehlen(copy.deepcopy(k), "fernseher"), ref, "anker, aber nur eine Kategorie hochgezählt")
        k = copy.deepcopy(ref)                          # Gegenprobe: mindest ändert keine Note
        spiele = next(a for a in kat_von(k)["fragen"][0]["antworten"] if a["id"] == "spiele")
        spiele["mindest"]["hdmi_4k120_anzahl"] = 2
        self.gruen(k, ref, "nur mindest geändert")

    def test_gleiche_projektion_gleiche_nummer(self):   # Test 38
        ref = referenz()
        self.gruen(copy.deepcopy(ref), ref, "gleich")
        self.rot(hochzaehlen(copy.deepcopy(ref), "fernseher"), ref, "gleiche Projektion, Nummer erhöht")
        k = copy.deepcopy(ref)
        kat_von(k)["gewichte_version"]["nummer"] = 0
        self.rot(k, ref, "Nummer 0")
        del kat_von(k)["gewichte_version"]
        self.rot(k, ref, "Kandidat ohne Fassung")

    def test_egal_umbenannt(self):                   # Test 39
        ref = referenz()
        k = copy.deepcopy(ref)
        kat, frage = next((kat, q) for kat in k["kategorien"] for q in kat.get("fragen", [])
                          if any(a["id"] == "egal" for a in q["antworten"]))
        next(a for a in frage["antworten"] if a["id"] == "egal")["id"] = "beliebig"
        self.rot(k, ref, "egal umbenannt, Faktoren gleich")
        self.gruen(hochzaehlen(k, kat["id"]), ref, "mit neuer Nummer")

    def test_projektion_normalform_und_reihenfolge(self):   # Test 40
        ref = referenz()
        k = copy.deepcopy(ref); feld_von(k, "bildtechnik")["gewicht"] = 30.0
        self.gruen(k, ref, "1 gegen 1.0")
        k = copy.deepcopy(ref); f = kat_von(k)["felder"]; f[0], f[1] = f[1], f[0]
        self.rot(k, ref, "Reihenfolge der Felder mit Gewicht > 0")
        k = copy.deepcopy(ref); f = kat_von(k)["felder"]; f.insert(0, f.pop(f.index(feld_von(k, "diagonale_zoll"))))
        self.gruen(k, ref, "Feld mit Gewicht 0 verschoben")
        k = copy.deepcopy(ref); q = kat_von(k)["fragen"]; q[0], q[1] = q[1], q[0]
        self.rot(k, ref, "Reihenfolge der Fragen")
        k = copy.deepcopy(ref); a = kat_von(k)["fragen"][0]["antworten"]; a[0], a[1] = a[1], a[0]
        self.rot(k, ref, "Reihenfolge der Antworten")
        k = copy.deepcopy(ref); feld_von(k, "bildwiederholrate_hz")["kurve"]["punkte"].reverse()
        self.rot(k, ref, "Reihenfolge der Kurvenpunkte")
        k = copy.deepcopy(ref); g = kat_von(k)["fragen"][0]["antworten"][0]["gewichte"]
        kat_von(k)["fragen"][0]["antworten"][0]["gewichte"] = dict(reversed(list(g.items())))
        self.gruen(k, ref, "Schlüsselreihenfolge in gewichte einer Antwort wirkt nicht")
        # R2-01: f0…f4 mit 8/3/7/11/5, ohne Fragen; die Umordnung kippt die Anzeige 39 → 38 (Rechnung: test_bewertung.mjs)
        r2 = copy.deepcopy(ref)
        kat_von(r2)["felder"] = [{"id": f"f{i}", "name": f"F{i}", "einheit": "", "typ": "zahl", "gewicht": g,
                                  "kurve": {"art": "linear", "punkte": [[0, 0], [100, 100]]}} for i, g in enumerate((8, 3, 7, 11, 5))]
        kat_von(r2)["fragen"] = []
        k = copy.deepcopy(r2); kat_von(k)["felder"].reverse()
        self.rot(k, r2, "R2-01: umgekehrte Feldliste ohne neue Nummer")
        # Normalform: |x| >= 1e7 rot (int 34,8 gegen float 34,7), 1200 gegen 1200.0 gleich
        k = copy.deepcopy(ref); feld_von(k, "bildwiederholrate_hz")["kurve"]["punkte"][0][0] = -10000000000000000
        self.assertTrue(datenbank.schema_fehler(k)); self.rot(k, ref, "Stützpunkt -1e16")
        k = copy.deepcopy(ref); feld_von(k, "bildwiederholrate_hz")["kurve"]["punkte"][0][0] = 1e7
        self.assertTrue(datenbank.schema_fehler(k), "x = 1e7")
        k = copy.deepcopy(ref); feld_von(k, "bildwiederholrate_hz")["kurve"]["punkte"][0][1] = 101
        self.assertTrue(datenbank.schema_fehler(k), "y = 101")
        a = copy.deepcopy(ref); feld_von(a, "bildwiederholrate_hz")["kurve"]["punkte"] = [[1200, 20], [1204, 79]]
        b = copy.deepcopy(ref); feld_von(b, "bildwiederholrate_hz")["kurve"]["punkte"] = [[1200.0, 20], [1204.0, 79]]
        self.gruen(b, a, "1200 gegen 1200.0")
        ta = round(datenbank.teilpunkte(feld_von(a, "bildwiederholrate_hz"), 1201), 1)
        tb = round(datenbank.teilpunkte(feld_von(b, "bildwiederholrate_hz"), 1201), 1)
        self.assertEqual((ta, tb), (34.8, 34.8))
        k = copy.deepcopy(ref); feld_von(k, "vrr")["gewicht"] = True
        r = copy.deepcopy(ref); feld_von(r, "vrr")["gewicht"] = 1
        self.rot(k, r, "Gewicht true statt 1")
        # P2A2-04: Feld außerhalb der Projektion (Gewicht 0) kaputt → Vorbedingung rot, Kandidat und Referenz gleich
        k = copy.deepcopy(ref); feld_von(k, "diagonale_zoll")["gewicht"] = False
        self.assertTrue(datenbank.schema_fehler(k))
        self.assertTrue(any(f.startswith("Kandidat") for f in self.vergleich(k, ref)))
        self.assertTrue(any(f.startswith("Referenz") for f in self.vergleich(ref, k)))
        k = copy.deepcopy(ref); feld_von(k, "diagonale_zoll")["id"] = "constructor"
        fehler = self.vergleich(k, ref)
        self.assertTrue(fehler and all("Kennung" in f for f in fehler), fehler)
        # jede Zahl der normierten Projektion ist float
        p = datenbank.projektion(echtes_schema(), "fernseher")
        zahlen = [f["gewicht"] for f in p["felder"]] + [y for f in p["felder"] for _, y in f["kurve"]["punkte"]]
        zahlen += [x for f in p["felder"] if f["kurve"]["art"] == "linear" for x, _ in f["kurve"]["punkte"]]
        zahlen += [v for q in p["fragen"] for a in q["antworten"] for v in a["gewichte"].values()]
        zahlen += [v for v in p["abschlag"].values() if not isinstance(v, dict)] + list(p["abschlag"].get("mischung", {}).values())
        self.assertTrue(zahlen and all(type(z) is float for z in zahlen))
        self.assertEqual(sorted(p), ["abschlag", "felder", "fragen"])
        self.assertNotIn("diagonale_zoll", [f["id"] for f in p["felder"]])

    def test_referenz_schema_1(self):                # Test 41
        r1 = echtes_schema()
        r1["schema_version"] = 1
        for k in r1["kategorien"]:
            k.pop("gewichte_version", None)
        k = echtes_schema()
        self.gruen(k, r1, "gleiche Projektion, Nummer 1")
        self.rot(hochzaehlen(copy.deepcopy(k), "fernseher"), r1, "gleiche Projektion, Nummer 2")
        g = copy.deepcopy(k); feld_von(g, "bildtechnik")["gewicht"] = 31
        self.rot(g, r1, "geänderte Projektion, Nummer 1")
        self.rot(hochzaehlen(g, "fernseher"), r1, "geänderte Projektion, Nummer 2")
        r3 = referenz(); kat_von(r3)["gewichte_version"]["nummer"] = 3
        k2 = referenz(); kat_von(k2)["gewichte_version"] = {"nummer": 2, "stand": "2026-11-25"}
        self.rot(k2, r3, "Nummer kleiner als in der Referenz mit Schema 2")
        # P2A2-BAU-06: Rückschritt auch bei geänderter Projektion und gültigem neuem Datum (dann greift nur der
        # Schutz gegen kleinere Nummern, nicht die Regeln für gleiche Projektion oder gleichen Stand)
        k3 = copy.deepcopy(k2); feld_von(k3, "bildtechnik")["gewicht"] = 31
        self.rot(k3, r3, "Nummer 3 → 2, Gewicht geändert, neuer Stand")
        k4 = copy.deepcopy(k3); kat_von(k4)["fragen"][0]["antworten"][0]["gewichte"]["bildtechnik"] = 1.4
        kat_von(k4)["gewichte_version"] = {"nummer": 1, "stand": "2026-11-25"}
        self.rot(k4, r3, "Nummer 3 → 1, Faktor und Gewicht geändert, neuer Stand")
        self.gruen(_mit_nummer(copy.deepcopy(k3), 4), r3, "Gegenprobe: dieselbe Änderung mit Nummer 4")

    def test_referenz_fassung_explizit_ungueltig(self):   # P2A2-BAU-03
        k = echtes_schema()
        for wert, version in ((None, 2), (None, 1), ("fehlt", 2), ("fehlt", True), ("fehlt", 3)):
            with self.subTest(wert=wert, version=version):
                r = echtes_schema(); r["schema_version"] = version
                for kat in r["kategorien"]:
                    if wert == "fehlt":
                        kat.pop("gewichte_version", None)
                    else:
                        kat["gewichte_version"] = wert
                fehler = self.vergleich(k, r)
                # Schema true/3: Meldung zur Schema-Version vor jeder Fassungsprüfung (P2A2-BAU-03 r3)
                wort = "gewichte_version" if version in (1, 2) and type(version) is int else "schema_version"
                self.assertTrue(fehler and all(wort in f for f in fehler), fehler)
        r1 = echtes_schema(); r1["schema_version"] = 1   # Gegenprobe: Altschema mit fehlendem Schlüssel
        for kat in r1["kategorien"]:
            kat.pop("gewichte_version")
        self.gruen(k, r1, "Schema 1 ohne Schlüssel bleibt die Erstfassung")

    def test_referenz_gerundet_und_ohne_projektion(self):   # P2A2-BAU-03 r2
        """Altschema nur bei der ganzen Zahl 1 (auch nach strengem Lesen: 0.99999999999999999 wird 1.0), und bei
        ungültigen Fassungsangaben der Referenz läuft keine Projektion."""
        k = echtes_schema()
        roh = json.dumps({**echtes_schema(), "kategorien": [{x: v for x, v in kat.items() if x != "gewichte_version"}
                                                              for kat in echtes_schema()["kategorien"]]})
        for text in ("0.99999999999999999", "1.0", "1e0", "1.00000000000000001"):
            with self.subTest(schema_version=text):
                r = datenbank.json_streng(roh.replace('"schema_version": 2', '"schema_version": ' + text, 1))
                self.assertEqual(r["schema_version"], 1.0)
                with mock.patch.object(datenbank, "projektion", wraps=datenbank.projektion) as p:
                    fehler = self.vergleich(k, r)
                self.assertTrue(fehler and all("schema_version" in f for f in fehler), fehler)
                self.assertEqual(p.call_count, 0, text)
        r = datenbank.json_streng(roh.replace('"schema_version": 2', '"schema_version": 1', 1))
        self.gruen(k, r, "Gegenprobe: ganze Zahl 1 bleibt Altschema")
        for art, version, wert in (("fehlt, Schema 2", 2, "fehlt"), ("null", 2, None),
                                   ("Nummer 0", 2, {"nummer": 0, "stand": "2026-11-01"})):
            with self.subTest(art=art):
                r = echtes_schema(); r["schema_version"] = version
                for kat in r["kategorien"]:
                    if wert == "fehlt":
                        kat.pop("gewichte_version", None)
                    else:
                        kat["gewichte_version"] = wert
                with mock.patch.object(datenbank, "projektion", wraps=datenbank.projektion) as p:
                    fehler = self.vergleich(k, r)
                self.assertEqual(len(fehler), len(k["kategorien"]), fehler)
                self.assertEqual(p.call_count, 0, art)
        # P2A2-BAU-03 r3 (Speicherproben aus dem Bericht r2): ungültige Schema-Version bei sonst gültigen Fassungen,
        # und eine einzige ungültige Fassung in einer späten Kategorie – beide rot, ohne einen Projektionsaufruf
        letzte = k["kategorien"][-1]["id"]
        for art, version, kaputt in (("Schema 2.0, Fassungen gültig", 2.0, None), ("Schema 3, Fassungen gültig", 3, None),
                                     ("Schema true", True, None), (f"nur {letzte} null", 2, letzte),
                                     ("nur akkusauger null", 2, "akkusauger")):
            with self.subTest(art=art):
                r = referenz(); r["schema_version"] = version
                if kaputt:
                    next(x for x in r["kategorien"] if x["id"] == kaputt)["gewichte_version"] = None
                with mock.patch.object(datenbank, "projektion", wraps=datenbank.projektion) as p:
                    fehler = self.vergleich(k, r)
                self.assertTrue(fehler, art)
                self.assertEqual(p.call_count, 0, art)
                if kaputt:
                    self.assertTrue(all(f.startswith(kaputt + ":") for f in fehler), fehler)
        with mock.patch.object(datenbank, "projektion", wraps=datenbank.projektion) as p:   # Gegenprobe gültig
            self.gruen(k, referenz(), "gültige Referenz")
        self.assertEqual(p.call_count, 2 * len(k["kategorien"]))
        s = echtes_schema(); s["schema_version"] = 2.0
        self.assertTrue(any("schema_version" in f for f in datenbank.schema_fehler(s)), "Kandidat mit 2.0")

    def test_abschlag_isoliert(self):               # P2A2-BAU-06 r2
        """Jeder Wert des Datenblatt-Abschlags in der Projektion (§9.3) einzeln geändert: gleiche Nummer rot, neue
        Nummer mit neuem Stand in allen Kategorien grün."""
        ref = referenz()
        faelle = {n: (lambda n: lambda db: db.__setitem__(n, db[n] + (0.05 if n in ("faktor", "abdeckung_mindest") else 1)))(n)
                  for n in ("anker", "faktor", "abzug", "abdeckung_mindest")}   # §9.3 ausdrücklich, nicht aus dem Code
        faelle["mischung.test"] = lambda db: db["getestet"]["mischung"].__setitem__("test", 0.65)
        faelle["mischung.datenblatt_roh"] = lambda db: db["getestet"]["mischung"].__setitem__("datenblatt_roh", 0.35)
        for art, aendern in faelle.items():
            with self.subTest(art=art):
                k = copy.deepcopy(ref); aendern(k["datenblatt_abschlag"])
                self.assertEqual(datenbank.schema_fehler(k), [], art)
                fehler = self.vergleich(k, ref)
                self.assertEqual(len([f for f in fehler if "Nummer muss steigen" in f]), len(ref["kategorien"]), fehler)
                self.gruen(hochzaehlen(copy.deepcopy(k)), ref, art + " mit neuer Nummer überall")
        k = copy.deepcopy(ref); k["datenblatt_abschlag"]["spanne_plus_minus"] = 9   # Gegenprobe: nur Anzeige
        self.gruen(k, ref, "spanne ändert keine Note")

    def test_frage_id_isoliert(self):               # P2A2-BAU-06 r3
        """§9.3: die Frage-ID gehört zur Projektion. Jede Frage jeder Kategorie einzeln umbenannt (sonst nichts):
        Schema gültig, gleiche Nummer rot, neue Nummer grün."""
        ref = referenz()
        faelle = [(kat["id"], i) for kat in ref["kategorien"] for i in range(len(kat.get("fragen", [])))]
        self.assertTrue(faelle)
        for kid, i in faelle:
            with self.subTest(kategorie=kid, frage=i):
                k = copy.deepcopy(ref); q = next(x for x in k["kategorien"] if x["id"] == kid)["fragen"][i]
                q["id"] = q["id"] + "-neu"
                self.assertEqual(datenbank.schema_fehler(k), [])
                self.assertEqual(self.vergleich(k, ref), [f"{kid}: Gewichte, Kurven oder Abschlag geändert, Nummer muss steigen "
                                                        f"(Referenz {kat_von(ref, kid)['gewichte_version']['nummer']})"])
                self.gruen(hochzaehlen(k, kid), ref, "mit neuer Nummer")

    def test_feld_id_isoliert(self):                # P2A2-BAU-06 r3-Hinweis
        """§9.3: die ID eines Feldes mit Gewicht > 0 gehört zur Projektion. Je Kategorie jedes gewichtete Feld einzeln
        umbenannt (Verweise in den Antworten mit, sonst wäre das Schema ungültig): gleiche Nummer rot, neue grün."""
        ref = referenz()
        faelle = [(kat["id"], f["id"]) for kat in ref["kategorien"] for f in kat["felder"] if f["gewicht"] > 0]
        self.assertTrue(faelle)
        for kid, fid in faelle:
            with self.subTest(kategorie=kid, feld=fid):
                k = copy.deepcopy(ref); kat = kat_von(k, kid); neu = "neu_" + fid
                feld_von(k, fid, kid)["id"] = neu
                for q in kat.get("fragen", []):
                    for a in q["antworten"]:
                        for n in ("gewichte", "mindest", "hoechst"):
                            if fid in a.get(n, {}):
                                a[n] = {(neu if x == fid else x): v for x, v in a[n].items()}
                self.assertEqual(datenbank.schema_fehler(k), [])
                self.assertEqual(self.vergleich(k, ref), [f"{kid}: Gewichte, Kurven oder Abschlag geändert, Nummer muss steigen "
                                                        f"(Referenz {kat_von(ref, kid)['gewichte_version']['nummer']})"])
                self.gruen(hochzaehlen(k, kid), ref, "mit neuer Nummer")

    def test_entfernte_kategorie(self):              # P2A2-BAU-05
        r8 = referenz(); kat_von(r8)["gewichte_version"] = {"nummer": 8, "stand": "2026-11-01"}
        ohne = copy.deepcopy(r8); ohne["kategorien"].remove(kat_von(ohne))
        fehler = self.vergleich(ohne, r8)
        self.assertTrue(any(f.startswith("fernseher:") and "fehlt" in f for f in fehler), fehler)
        umbenannt = copy.deepcopy(r8); kat_von(umbenannt)["id"] = "fernseher-neu"
        fehler = self.vergleich(umbenannt, r8)
        self.assertTrue(any(f.startswith("fernseher:") and "fehlt" in f for f in fehler), fehler)
        # zweiter Übergang aus dem Befund: Wiederkehr mit Nummer 1 gegen den (nun nicht freigebbaren) Zwischenstand
        zurueck = copy.deepcopy(r8); kat_von(zurueck)["gewichte_version"] = {"nummer": 1, "stand": "2026-11-25"}
        feld_von(zurueck, "bildtechnik")["gewicht"] = 31
        self.rot(zurueck, r8, "Wiederkehr mit Nummer 1 gegen die Referenz mit Fassung 8")
        neu = copy.deepcopy(r8); extra = copy.deepcopy(kat_von(neu)); extra["id"] = "fernseher-zwei"
        neu["kategorien"].append(extra)
        self.gruen(neu, r8, "Gegenprobe: neue Kategorie dazu")

    def test_nur_endliche_zahlen(self):             # P2A2-BAU-01
        roh = datenbank.SCHEMA.read_text(encoding="utf-8")
        for zahl in ("1e999", "-1e999", "1" + "0" * 400):
            with self.subTest(zahl=zahl):
                with self.assertRaises(ValueError):
                    datenbank.schema_laden('{"a": {"mindest": {"x": ' + zahl + '}}}')
        self.assertEqual(datenbank.schema_laden('{"a": 1e308, "b": 12}'), {"a": 1e308, "b": 12})
        s = echtes_schema()
        a = next(a for a in kat_von(s)["fragen"][0]["antworten"] if a["id"] == "spiele")
        a["mindest"]["hdmi_4k120_anzahl"] = 7
        text = json.dumps(s, ensure_ascii=False).replace('"hdmi_4k120_anzahl": 7', '"hdmi_4k120_anzahl": 1e999')
        self.assertIn("1e999", text)
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "k.json").write_text(text, encoding="utf-8")
            alt = datenbank.SCHEMA
            datenbank.SCHEMA = Path(t) / "k.json"
            try:
                _, fehler, _ = datenbank.bauen(Path(t) / "aus.json")
            finally:
                datenbank.SCHEMA = alt
            self.assertTrue(any("nicht endlich" in f for f in fehler), fehler)
            self.assertFalse((Path(t) / "aus.json").exists())
            # Produktdaten: eine Datei mit 1e999 ist ein Fehler
            p = Path(t) / "p.json"
            p.write_text('{"kategorie": "fernseher", "x": 1e999}', encoding="utf-8")
            fehler = []
            self.assertIsNone(datenbank.pruefe_datei(p, {}, set(), fehler, []))
            self.assertTrue(any("nicht lesbar" in f for f in fehler), fehler)
            # Bau: ein nicht endlicher Wert, der am Lader vorbeikommt, wird nicht geschrieben (allow_nan=False)
            alt_lade = datenbank.lade_schema
            def lade_inf():
                s2, k2 = alt_lade()
                next(a for a in kat_von(s2)["fragen"][0]["antworten"] if a["id"] == "spiele")["mindest"]["hdmi_4k120_anzahl"] = float("inf")
                return s2, {k["id"]: k for k in s2["kategorien"]}
            datenbank.lade_schema = lade_inf
            try:
                _, fehler, _ = datenbank.bauen(Path(t) / "aus2.json")
            finally:
                datenbank.lade_schema = alt_lade
            self.assertTrue(any("kein strenges JSON" in f for f in fehler), fehler)
            self.assertFalse((Path(t) / "aus2.json").exists())
        self.assertEqual(roh, datenbank.SCHEMA.read_text(encoding="utf-8"))

    def test_eindeutige_ids(self):                   # Test 48
        def dopplung(aendern):
            s = echtes_schema(); aendern(s); return datenbank.schema_fehler(s)
        vrr2 = {"id": "vrr", "name": "VRR", "einheit": "", "typ": "bool", "gewicht": 0,
                "kurve": {"art": "ja_nein", "punkte": [[True, 100], [False, 0]]}}
        faelle = {
            "feld": lambda s: kat_von(s)["felder"].append(vrr2),
            "frage": lambda s: kat_von(s)["fragen"].append(copy.deepcopy(kat_von(s)["fragen"][0])),
            "antwort": lambda s: kat_von(s)["fragen"][0]["antworten"].append(copy.deepcopy(kat_von(s)["fragen"][0]["antworten"][0])),
            "kategorie": lambda s: s["kategorien"].append(copy.deepcopy(kat_von(s))),
            "stufenwert": lambda s: feld_von(s, "bildtechnik")["kurve"]["punkte"].append(["oled", 10]),
        }
        for art, aendern in faelle.items():
            with self.subTest(art=art):
                fehler = dopplung(aendern)
                self.assertTrue(any("doppelt" in f for f in fehler), (art, fehler))
        # Gegenprobe: gleiche Antwort-ID in zwei Fragen ist erlaubt (das echte Schema hat das schon)
        self.assertEqual(dopplung(lambda s: None), [])
        s = echtes_schema(); q = kat_von(s)["fragen"]
        q[1]["antworten"][0]["id"] = q[0]["antworten"][0]["id"]
        self.assertEqual(datenbank.schema_fehler(s), [])
        # weder Projektion noch Bau: doppeltes Feld mit Gewicht 0 am Ende → Bau rot, keine Datei
        with tempfile.TemporaryDirectory() as t:
            s = echtes_schema(); kat_von(s)["felder"].append(vrr2)
            (Path(t) / "k.json").write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
            alt = datenbank.SCHEMA
            datenbank.SCHEMA = Path(t) / "k.json"
            try:
                _, fehler, _ = datenbank.bauen(Path(t) / "aus.json")
            finally:
                datenbank.SCHEMA = alt
            self.assertTrue(fehler)
            self.assertFalse((Path(t) / "aus.json").exists())
            self.assertTrue(any("Referenz" in f or "Kandidat" in f for f in self.vergleich(s, referenz())))


if __name__ == "__main__":
    unittest.main()
