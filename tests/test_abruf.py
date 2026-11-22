# -*- coding: utf-8 -*-
"""Tests für werkzeuge/datenpflege/abruf.py ohne Netz: ein HTTP-Versuch je Takt (F-04), robots.txt nach RFC 9309 (F-06)."""
import io
import json
import os
import subprocess
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

    def test_gleiche_normalisierung_fuer_laenge(self):
        """R2-04: %70 = p (nicht reserviert) wird für Vergleich und Länge gleich normalisiert; %2A bleibt Literal."""
        text = "User-agent: *\nDisallow: /de/category/px\nAllow: /de/category/%70\n"
        self.assertFalse(abruf.robots_erlaubt(text, UA, "https://h.invalid/de/category/px"))
        self.assertTrue(abruf.robots_erlaubt(text, UA, "https://h.invalid/de/category/pa"))
        self.assertFalse(abruf.robots_erlaubt("User-agent: *\nDisallow: /a%62c\n", UA, "https://h.invalid/abc"))
        self.assertFalse(abruf.robots_erlaubt("User-agent: *\nDisallow: /abc\n", UA, "https://h.invalid/a%62c"))
        stern = "User-agent: *\nDisallow: /x%2Ay\n"
        self.assertTrue(abruf.robots_erlaubt(stern, UA, "https://h.invalid/xzzy"), "%2A ist kein Platzhalter")
        self.assertFalse(abruf.robots_erlaubt(stern, UA, "https://h.invalid/x%2ay"))
        self.assertFalse(abruf.robots_erlaubt("User-agent: *\nDisallow: /kühl\n", UA, "https://h.invalid/k%C3%BChl-1.html"))

    def test_rfc9309_sonderzeichen(self):
        """R3-03: RFC 9309 § 2.2.3 – %2A/%24 in der Regel treffen wörtliches * und $ im URL-Pfad (beide Schreibweisen)."""
        regel = lambda r: "User-agent: *\nDisallow: " + r + "\n"
        stern = regel("/path/file-with-a-%2A.html")
        self.assertFalse(abruf.robots_erlaubt(stern, UA, "https://h.invalid/path/file-with-a-*.html"))
        self.assertFalse(abruf.robots_erlaubt(stern, UA, "https://h.invalid/path/file-with-a-%2a.html"))
        self.assertTrue(abruf.robots_erlaubt(stern, UA, "https://h.invalid/path/file-with-a-x.html"))
        dollar = regel("/path/foo-%24")
        self.assertFalse(abruf.robots_erlaubt(dollar, UA, "https://h.invalid/path/foo-$"))
        self.assertFalse(abruf.robots_erlaubt(dollar, UA, "https://h.invalid/path/foo-%24"))
        self.assertFalse(abruf.robots_erlaubt(regel("/x%2Ay"), UA, "https://h.invalid/x*y"))
        self.assertFalse(abruf.robots_erlaubt(regel("/x%24"), UA, "https://h.invalid/x$"))
        # Platzhalter in Regeln bleiben: * beliebig, nur abschließendes $ = Pfadende, $ mitten in der Regel ist wörtlich
        self.assertFalse(abruf.robots_erlaubt(regel("/a*c$"), UA, "https://h.invalid/abbc"))
        self.assertTrue(abruf.robots_erlaubt(regel("/a*c$"), UA, "https://h.invalid/abbcd"))
        self.assertFalse(abruf.robots_erlaubt(regel("/a$b"), UA, "https://h.invalid/a$b"))
        self.assertTrue(abruf.robots_erlaubt(regel("/a$b"), UA, "https://h.invalid/a"))
        self.assertFalse(abruf.robots_erlaubt(regel("/a$$"), UA, "https://h.invalid/a$"), "nur das letzte $ ist Pfadende")
        self.assertTrue(abruf.robots_erlaubt(regel("/a$$"), UA, "https://h.invalid/a$b"))
        self.assertTrue(abruf.robots_erlaubt(regel("/a$$"), UA, "https://h.invalid/a"))

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


class Domainsperre(unittest.TestCase):
    """R3-04: Domainsperre als Betriebssystem-Dateisperre: genau ein Inhaber, die Datei wird nie gelöscht."""

    def test_domainsperre_ein_inhaber(self):
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            erste = abruf.sperre_versuchen("h.invalid")
            self.assertIsNotNone(erste)
            try:
                self.assertIsNone(abruf.sperre_versuchen("h.invalid"), "zweiter Inhaber trotz gehaltener Sperre")
                # Ein zweiter Prozess bekommt die Sperre ebenfalls nicht
                kind = subprocess.run([sys.executable, "-I", "-c",
                    "import sys; sys.path[:0]=[sys.argv[1], sys.argv[2]]; import abruf; from pathlib import Path; "
                    "abruf.TAKT=Path(sys.argv[3]); sys.exit(0 if abruf.sperre_versuchen('h.invalid') is None else 1)",
                    str(WURZEL / "werkzeuge" / "datenpflege"), str(WURZEL / "werkzeuge"), t], capture_output=True, text=True)
                self.assertEqual(kind.returncode, 0, kind.stderr)
            finally:
                abruf.sperre_freigeben(erste)
            zweite = abruf.sperre_versuchen("h.invalid")
            self.assertIsNotNone(zweite, "nach Freigabe wieder frei")
            abruf.sperre_freigeben(zweite)

    def test_alte_sperrdatei_wird_nicht_geloescht(self):
        """Eine alte Sperrdatei ohne Inhaber sperrt nicht; eine gehaltene bleibt gehalten, egal wie alt."""
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            lock = Path(t) / "h.invalid.lock"
            lock.write_bytes(b"")
            os.utime(lock, (time.time() - 3600, time.time() - 3600))
            erste = abruf.sperre_versuchen("h.invalid")
            self.assertIsNotNone(erste, "liegengebliebene Datei ohne Inhaber sperrt nicht")
            try:
                os.utime(lock, (time.time() - 3600, time.time() - 3600))
                with unittest.mock.patch("time.sleep", side_effect=RuntimeError("wartet")):
                    with self.assertRaises(RuntimeError):
                        abruf.sperre_holen("h.invalid")   # wartet statt die alte Datei zu löschen
                self.assertTrue(lock.exists())
            finally:
                abruf.sperre_freigeben(erste)

    def test_holen_gibt_die_sperre_frei_und_laesst_die_datei(self):
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)),              unittest.mock.patch.object(abruf, "einmal_abrufen", side_effect=sa.NichtAbrufbar("Netzfehler: x")):
            with self.assertRaises(SystemExit):
                abruf.holen("https://h.invalid/a")
            self.assertTrue((Path(t) / "h.invalid.lock").exists(), "Sperrdatei bleibt liegen")
            self.assertTrue((Path(t) / "h.invalid.zeit").exists(), "Zeitstempel auch nach Fehler")
            f = abruf.sperre_versuchen("h.invalid")
            self.assertIsNotNone(f, "nach dem Abruf wieder frei")
            abruf.sperre_freigeben(f)


if __name__ == "__main__":
    unittest.main()
