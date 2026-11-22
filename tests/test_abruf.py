# -*- coding: utf-8 -*-
"""Tests für werkzeuge/datenpflege/abruf.py ohne Netz: ein HTTP-Versuch je Takt (F-04), robots.txt nach RFC 9309 (F-06)."""
import io
import json
import sys
import tempfile
import time
import unittest
import unittest.mock
import urllib.error
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "werkzeuge" / "datenpflege"))
sys.path.insert(0, str(WURZEL / "werkzeuge"))
import abruf  # noqa: E402
import shopabfrage as sa  # noqa: E402

UA = sa.UA_TOKEN


class EinVersuch(unittest.TestCase):
    """F-04: HTTP 500 und Netzfehler werden nicht innerhalb des Taktes wiederholt."""

    def test_500_und_netzfehler_genau_ein_versuch(self):
        for fehler in (urllib.error.HTTPError("https://x.invalid/", 500, "x", {}, io.BytesIO(b"")),
                       urllib.error.URLError("weg")):
            aufrufe = []

            def oeffnen(req, timeout=None, fehler=fehler):
                aufrufe.append(req.full_url)
                raise fehler
            with unittest.mock.patch.object(sa._OPENER, "open", side_effect=oeffnen), \
                 unittest.mock.patch("time.sleep") as schlaf:
                with self.assertRaises(sa.NichtAbrufbar):
                    abruf.einmal_abrufen("https://x.invalid/a")
            self.assertEqual(len(aufrufe), 1, fehler)
            schlaf.assert_not_called()

    def test_holen_nutzt_den_einzelversuch(self):
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)), \
             unittest.mock.patch.object(abruf, "einmal_abrufen", return_value="ok") as ein, \
             unittest.mock.patch.object(sa, "abrufen", side_effect=AssertionError("Mehrfachabruf")):
            self.assertEqual(abruf.holen("https://x.invalid/a"), "ok")
            ein.assert_called_once()
            self.assertTrue((Path(t) / "x.invalid.zeit").exists(), "Zeitstempel für den Takt")


class Robots(unittest.TestCase):
    def test_benannter_user_agent_vor_stern(self):
        text = "User-agent: *\nAllow: /\n\nUser-agent: Kaufberatung-Preispilot\nDisallow: /de/category/\n"
        self.assertFalse(abruf.robots_erlaubt(text, UA, "https://www.saturn.de/de/category/tv-1.html"))
        self.assertTrue(abruf.robots_erlaubt(text, "AndererBot", "https://www.saturn.de/de/category/tv-1.html"))

    def test_platzhalter_und_ende(self):
        text = "User-agent: *\nDisallow: /*?*sort=\nDisallow: /*.pdf$\nDisallow: /de/*/filter/\n"
        self.assertFalse(abruf.robots_erlaubt(text, UA, "https://h.invalid/de/category/a.html?page=2&sort=preis"))
        self.assertTrue(abruf.robots_erlaubt(text, UA, "https://h.invalid/de/category/a.html?page=2"))
        self.assertFalse(abruf.robots_erlaubt(text, UA, "https://h.invalid/x/datenblatt.pdf"))
        self.assertTrue(abruf.robots_erlaubt(text, UA, "https://h.invalid/x/datenblatt.pdf.html"))
        self.assertFalse(abruf.robots_erlaubt(text, UA, "https://h.invalid/de/tv/filter/a"))

    def test_laengste_regel_gewinnt_gleichstand_allow(self):
        text = "User-agent: *\nDisallow: /de/\nAllow: /de/category/\nDisallow: /de/category/geheim\n"
        self.assertTrue(abruf.robots_erlaubt(text, UA, "https://h.invalid/de/category/tv-1.html"))
        self.assertFalse(abruf.robots_erlaubt(text, UA, "https://h.invalid/de/product/x.html"))
        self.assertFalse(abruf.robots_erlaubt(text, UA, "https://h.invalid/de/category/geheim-1.html"))
        self.assertTrue(abruf.robots_erlaubt("User-agent: *\nDisallow: /a\nAllow: /a\n", UA, "https://h.invalid/a"))

    def test_kodierte_pfade(self):
        text = "User-agent: *\nDisallow: /de/category/k%C3%BChl\n"
        self.assertFalse(abruf.robots_erlaubt(text, UA, "https://h.invalid/de/category/k%C3%BChlschr%C3%A4nke-1235.html"))

    def test_leer_oder_html_ist_nicht_auswertbar(self):
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            for antwort in ("", "<html>Wartung</html>"):
                with unittest.mock.patch.object(abruf, "holen", return_value=antwort):
                    ok, grund = abruf.robots_ok("https://h.invalid/de/category/a-1.html")
                self.assertFalse(ok, repr(antwort))
                self.assertIn("nicht auswertbar", grund)
                self.assertFalse((Path(t) / "h.invalid.robots.json").exists(), "Ungültiges wird nicht abgelegt")

    def test_ablage_laeuft_nach_24_stunden_ab(self):
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            with unittest.mock.patch.object(abruf, "holen", return_value="User-agent: *\nAllow: /\n") as h:
                self.assertTrue(abruf.robots_ok("https://h.invalid/a")[0])
                self.assertTrue(abruf.robots_ok("https://h.invalid/b")[0])
                self.assertEqual(h.call_count, 1, "innerhalb von 24 h aus der Ablage")
            ablage = Path(t) / "h.invalid.robots.json"
            a = json.loads(ablage.read_text(encoding="utf-8"))
            a["zeit"] = time.time() - 25 * 3600
            ablage.write_text(json.dumps(a), encoding="utf-8")
            with unittest.mock.patch.object(abruf, "holen", return_value="User-agent: *\nDisallow: /\n") as h:
                ok, _ = abruf.robots_ok("https://h.invalid/a")
                self.assertEqual(h.call_count, 1, "abgelaufene Ablage wird erneuert")
                self.assertFalse(ok, "neue Regeln gelten")

    def test_sperre_wird_weitergegeben(self):
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)), \
             unittest.mock.patch.object(abruf, "holen", side_effect=SystemExit(3)):
            with self.assertRaises(SystemExit):
                abruf.robots_ok("https://h.invalid/a")


if __name__ == "__main__":
    unittest.main()
