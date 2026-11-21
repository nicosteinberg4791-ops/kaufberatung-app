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

    def test_echte_daten_ohne_fehler(self):
        _, fehler, _ = datenbank.alle_pruefen()
        self.assertEqual(fehler, [])


if __name__ == "__main__":
    unittest.main()
