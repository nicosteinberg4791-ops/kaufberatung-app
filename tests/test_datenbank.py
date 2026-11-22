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

if __name__ == "__main__":
    unittest.main()
