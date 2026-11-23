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

    def test_leere_query_behaelt_den_trenner(self):
        """R4-04: urllib sendet /x? als Request-Target; Disallow: /x?$ muss greifen (RFC 9309 2.2.2)."""
        regel = "User-agent: *\nDisallow: /x?$\n"
        self.assertFalse(abruf.robots_erlaubt(regel, UA, "https://h.invalid/x?"))
        self.assertTrue(abruf.robots_erlaubt(regel, UA, "https://h.invalid/x"))
        self.assertFalse(abruf.robots_erlaubt(regel, UA, "https://h.invalid/x?#teil"), "Fragment wird nicht gesendet")
        with unittest.mock.patch.object(abruf, "robots_text", return_value=regel):
            ok, _ = abruf.robots_ok("https://h.invalid/x?")
        self.assertFalse(ok, "Abbruch vor holen()")

    def test_leer_oder_html_ist_nicht_auswertbar(self):
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            for antwort in ("", "<html>Wartung</html>"):
                with unittest.mock.patch.object(abruf, "holen", return_value=antwort):
                    ok, grund = abruf.robots_ok("https://h.invalid/de/category/a-1.html")
                self.assertFalse(ok, repr(antwort))
                self.assertIn("nicht auswertbar", grund)
                self.assertFalse((Path(t) / "https-h.invalid-443.robots.json").exists(), "Ungültiges wird nicht abgelegt")

    def test_ablage_laeuft_nach_24_stunden_ab(self):
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            with unittest.mock.patch.object(abruf, "holen", return_value="User-agent: *\nAllow: /\n") as h:
                self.assertTrue(abruf.robots_ok("https://h.invalid/a")[0])
                self.assertTrue(abruf.robots_ok("https://h.invalid/b")[0])
                self.assertEqual(h.call_count, 1, "innerhalb von 24 h aus der Ablage")
            ablage = Path(t) / "https-h.invalid-443.robots.json"
            a = json.loads(ablage.read_text(encoding="utf-8"))
            a["zeit"] = time.time() - 25 * 3600
            ablage.write_text(json.dumps(a), encoding="utf-8")
            with unittest.mock.patch.object(abruf, "holen", return_value="User-agent: *\nDisallow: /\n") as h:
                ok, _ = abruf.robots_ok("https://h.invalid/a")
                self.assertEqual(h.call_count, 1, "abgelaufene Ablage wird erneuert")
                self.assertFalse(ok, "neue Regeln gelten")

    def test_robots_je_schema_host_und_port(self):
        """R5-05: robots.txt gilt je Ursprung (RFC 9309 2.3): Port 8443 holt seine eigene Datei und nutzt nicht die von 443."""
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            with unittest.mock.patch.object(abruf, "holen", return_value="User-agent: *\nAllow: /\n") as h:
                self.assertTrue(abruf.robots_ok("https://h.invalid/a")[0])
            self.assertEqual(h.call_args[0][0], "https://h.invalid/robots.txt")
            with unittest.mock.patch.object(abruf, "holen", return_value="User-agent: *\nDisallow: /\n") as h:
                ok, _ = abruf.robots_ok("https://h.invalid:8443/a")
                self.assertEqual(h.call_count, 1, "eigene robots.txt für Port 8443")
                self.assertEqual(h.call_args[0][0], "https://h.invalid:8443/robots.txt")
                self.assertFalse(ok, "Regeln von 8443 gelten")
                self.assertTrue(abruf.robots_ok("https://h.invalid:443/b")[0], "443 = Standardport von https")
                self.assertEqual(h.call_count, 1, "443 aus der Ablage")
                self.assertFalse(abruf.robots_ok("http://h.invalid/a")[0], "http ist ein anderer Ursprung")
                self.assertEqual(h.call_args[0][0], "http://h.invalid/robots.txt")
            self.assertFalse(abruf.robots_ok("https://h.invalid:99999/a")[0], "ungültiger Port")

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

    @staticmethod
    def _wartezeiten(inhalt, wand, mono):
        """Stempelinhalt (str oder bytes) vorgeben, sperre_holen mit fester Wanduhr und monotoner Uhr ausführen;
        Rückgabe der Wartezeiten (time.sleep-Aufrufe)."""
        schlaf = []

        class Uhr:
            time = staticmethod(lambda: wand)
            monotonic = staticmethod(lambda: mono)
            sleep = staticmethod(lambda s: schlaf.append(s))
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            stempel = Path(t) / "h.invalid.zeit"
            stempel.write_bytes(inhalt) if isinstance(inhalt, bytes) else stempel.write_text(inhalt, encoding="utf-8")
            with unittest.mock.patch.object(abruf, "time", Uhr):
                lock, _ = abruf.sperre_holen("h.invalid")
                abruf.sperre_freigeben(lock)
        return schlaf

    def test_zeitstempel_vor_dem_http_versuch(self):
        """R4-03/A2: während des Versuchs steht die Markierung „laeuft“ mit dem Beginn im Stempel, danach der
        Abschlussstempel „<Wanduhr> <monotone Uhr>“; keine Hilfsdatei bleibt liegen."""
        uhr = {"wand": 1700003600.0, "mono": 4600.0}   # Codex A2-02: feste Uhren, unabhängig von der Laufzeit seit Start

        class Uhr:
            time = staticmethod(lambda: uhr["wand"])
            monotonic = staticmethod(lambda: uhr["mono"])
            sleep = staticmethod(lambda s: (_ for _ in ()).throw(AssertionError("Abstand längst vorbei")))
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            stempel = Path(t) / "h.invalid.zeit"
            stempel.write_text("1700000000.0 1000.0", encoding="utf-8")   # gültig, 3600 s alt

            def abrufen(url):
                art, beginn, _ = stempel.read_text(encoding="utf-8").split()
                self.assertEqual(art, abruf.LAEUFT, "laufender Abruf markiert")
                self.assertEqual(float(beginn), 1700003600.0, "Zeitstempel vor dem Versuch gesetzt")
                uhr.update(wand=1700003602.0, mono=4602.0)
                return "ok"
            with unittest.mock.patch.object(abruf, "einmal_abrufen", side_effect=abrufen), \
                    unittest.mock.patch.object(abruf, "time", Uhr):
                self.assertEqual(abruf.holen("https://h.invalid/a"), "ok")
            self.assertEqual(stempel.read_text(encoding="utf-8"), "1700003602.0 4602.0", "Abschlussstempel nach dem Ende")
            self.assertFalse((Path(t) / "h.invalid.zeit.neu").exists(), "keine Hilfsdatei liegen geblieben")
            # harter Abbruch während eines Versuchs (Markierung bleibt stehen): der nächste wartet den vollen Abstand
            abruf.stempel_setzen(stempel, laeuft=True)
            with unittest.mock.patch("time.sleep") as schlaf:
                lock, _ = abruf.sperre_holen("h.invalid")
                abruf.sperre_freigeben(lock)
            schlaf.assert_called_once_with(abruf.ABSTAND)

    def test_abbruch_beim_schreiben_laesst_den_alten_stempel(self):
        """R5-01: bricht das Schreiben des neuen Stempels ab, bleibt der alte vollständig stehen."""
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            stempel = Path(t) / "h.invalid.zeit"
            stempel.write_bytes(b"1700000000.5 100.0")
            # Codex A2-03: Abbruch nach dem Öffnen und Schreiben (beim fsync), nicht schon beim Lesen der Uhr
            with unittest.mock.patch.object(abruf.os, "fsync", side_effect=RuntimeError("Abbruch")):
                with self.assertRaises(RuntimeError):
                    abruf.stempel_setzen(stempel)
            self.assertEqual(stempel.read_bytes(), b"1700000000.5 100.0", "alter Stempel vollständig erhalten")

    def test_fehler_beim_pruefen_des_stempels_heisst_voller_abstand(self):
        """Codex A2-01 (r2): ein Fehler wie PermissionError beim Abfragen des Eintrags gilt als vorhandener, unlesbarer
        Stempel (voller Abstand); nur FileNotFoundError heißt „kein Stempel“."""
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            stempel, echt = Path(t) / "h.invalid.zeit", os.lstat

            def lstat(p, *a, **k):
                if Path(p) == stempel:
                    raise PermissionError("keine Rechte")
                return echt(p, *a, **k)
            # os.path.lexists nutzt intern os.lstat und meldete den Fehler als „fehlt“
            with unittest.mock.patch.object(abruf.os, "lstat", side_effect=lstat), \
                    unittest.mock.patch("time.sleep") as schlaf:
                lock, _ = abruf.sperre_holen("h.invalid")
                abruf.sperre_freigeben(lock)
            schlaf.assert_called_once_with(abruf.ABSTAND)

    def test_link_ohne_ziel_heisst_voller_abstand(self):
        """Codex A2-01: ein vorhandener Stempel-Eintrag, dessen Ziel fehlt (Link bzw. Junction), ist unlesbar und
        ergibt den vollen Abstand, statt als „kein Stempel“ zu gelten."""
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)):
            stempel, ziel = Path(t) / "h.invalid.zeit", Path(t) / "weg"
            try:
                if os.name == "nt":
                    import _winapi
                    ziel.mkdir()
                    _winapi.CreateJunction(str(ziel), str(stempel))
                    ziel.rmdir()
                else:
                    os.symlink(ziel, stempel)
            except (OSError, ImportError, AttributeError) as e:
                self.skipTest(f"kein Link möglich: {e}")
            self.assertFalse(stempel.exists())
            self.assertTrue(os.path.lexists(stempel))
            with unittest.mock.patch("time.sleep") as schlaf:
                lock, _ = abruf.sperre_holen("h.invalid")
                abruf.sperre_freigeben(lock)
            schlaf.assert_called_once_with(abruf.ABSTAND)

    def test_unbekannter_stempel_heisst_voller_abstand(self):
        """A2: nur der eigene Abschlussstempel „repr(Wanduhr) repr(monotone Uhr)“ zählt. Alles andere ergibt den vollen
        Abstand: leer, unlesbar, alte Einzelwerte (auch `0` und `-1e308`), die Markierung „laeuft“, nan/inf, unmögliche
        Werte (vor 1970, monotone Uhr negativ oder nach jetzt), Wanduhr in der Zukunft, Vorzeichen, fremde Schreibweise
        (gerundet, ohne Nachkomma, andere Trennung). Uhr: Wanduhr 1700000062, monotone Uhr 1001; ein gültiger Stempel
        „1700000000.0 1000.0“ ergäbe 1 s vergangen."""
        for inhalt in ("", "kaputt", "0", "-1e308", "nan", "-inf", "123.0", str(1700000062.0 - 1000),
                       "laeuft", "laeuft 123.0", "laeuft 1700000000.0 1000.0", "1 2 3",
                       "nan 1.0", "1.0 nan", "-inf 1.0", "1.0 inf", "-1e308 -1e308", "1.0 -5.0", "-5.0 1.0",
                       "1.0 1e300", "1700000000.0 1001.5", f"{1700000062.0 + 10 ** 9!r} 1000.0",
                       "1700000000.0 -1e-999", "1700000000.0 -0.0", "-0.0 1000.0", "1700000000.0 1e-999",
                       "1700000000.0 +1000.0", "1700000000.0 1000", "+1700000000.0 1000.0",
                       "1700000000.0\t1000.0", "1700000000.0  1000.0", "1700000000.0 1000.0\n",
                       " 1700000000.0 1000.0", b"\x81\x8d\xff 1.0"):
            with self.subTest(inhalt=inhalt):
                self.assertEqual(self._wartezeiten(inhalt, 1700000062.0, 1001.0), [abruf.ABSTAND])

    def test_gueltiger_stempel_zaehlt_die_kleinere_vergangene_zeit(self):
        """A2: gezählt wird die kleinere vergangene Zeit beider Uhren (Wanduhr-Sprung vorwärts verkürzt nichts)."""
        for wand, mono, erwartet in ((1700000062.0, 1001.0, [abruf.ABSTAND - 1]),   # Wanduhr +62, real 1 s
                                     (1700000001.0, 1100.0, [abruf.ABSTAND - 1]),   # monotone Uhr weiter als Wanduhr
                                     (1700000030.0, 1030.0, [abruf.ABSTAND - 30]),
                                     (1700000100.0, 1100.0, [])):                   # Abstand vorbei: kein Warten
            with self.subTest(wand=wand, mono=mono):
                self.assertEqual(self._wartezeiten("1700000000.0 1000.0", wand, mono), erwartet)

    def test_neustart_haelt_den_abstand(self):
        """A2: Stempel aus einer früheren Startsitzung. Die neue Sitzung begann nach dem Stempel, real sind also
        mindestens `mono` Sekunden vergangen; vergangene Zeit plus Wartezeit ist damit immer mindestens ABSTAND."""
        for stempel, wand, mono in (("1000.0 1.0", 1023.0, 21.0), ("1000.0 0.0", 1005.0, 3.0),
                                    ("1000.0 500.0", 1030.0, 20.0), ("1000.0 1.0", 900.0, 10.0),
                                    ("1000.0 1.0", 5000.0, 59.0)):
            with self.subTest(stempel=stempel, wand=wand, mono=mono):
                self.assertGreaterEqual(mono + sum(self._wartezeiten(stempel, wand, mono)), abruf.ABSTAND)

    def test_sprung_der_systemuhr_haelt_den_abstand(self):
        """A2: Abschlussstempel bei Wanduhr 1000, danach springt die Systemuhr auf 1120, real ist 1 s vergangen
        (monotone Uhr): der nächste Abruf wartet die restlichen 60 s. Ein Rücksprung wartet höchstens ABSTAND."""
        for wand_spaeter, erwartet in ((1120.0, abruf.ABSTAND - 1), (400.0, abruf.ABSTAND)):
            uhr = {"wand": 1000.0, "mono": 50.0}
            schlaf = []

            class Uhr:
                time = staticmethod(lambda: uhr["wand"])
                monotonic = staticmethod(lambda: uhr["mono"])
                sleep = staticmethod(lambda s: schlaf.append(s))
            with self.subTest(wand_spaeter=wand_spaeter), tempfile.TemporaryDirectory() as t, \
                    unittest.mock.patch.object(abruf, "TAKT", Path(t)), unittest.mock.patch.object(abruf, "time", Uhr):
                abruf.stempel_setzen(Path(t) / "h.invalid.zeit")
                uhr.update(wand=wand_spaeter, mono=51.0)
                lock, _ = abruf.sperre_holen("h.invalid")
                abruf.sperre_freigeben(lock)
            self.assertEqual(len(schlaf), 1)
            self.assertAlmostEqual(schlaf[0], erwartet)

    def test_abbruch_nach_verzoegertem_versand_haelt_den_abstand(self):
        """A2/R5-01: Markierung bei Sekunde 0, Versand erst bei Sekunde 62, dann hartes Ende vor dem Abschlussstempel:
        der nächste Abruf derselben Domain geht trotzdem frühestens ABSTAND nach dem ersten ab."""
        uhr = [10000.0]

        class Uhr:   # gemeinsame Uhr für time.time, time.monotonic und time.sleep in abruf
            time = staticmethod(lambda: uhr[0])
            monotonic = staticmethod(lambda: uhr[0] - 5000.0)

            @staticmethod
            def sleep(s):
                uhr[0] += s

        class HartesEnde(BaseException):
            pass
        gesendet, aufrufe = [], []
        echt = abruf.stempel_setzen

        def stempel_bis_abbruch(*a, **k):
            aufrufe.append(a)
            if len(aufrufe) == 2:
                raise HartesEnde()   # Prozess endet vor dem Abschlussstempel
            return echt(*a, **k)

        def verzoegert(url):
            uhr[0] += 62   # z. B. langsamer Verbindungsaufbau vor dem eigentlichen Versand
            gesendet.append(uhr[0])
            return "ok"

        def sofort(url):
            gesendet.append(uhr[0])
            return "ok"
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(abruf, "TAKT", Path(t)), \
                unittest.mock.patch.object(abruf, "time", Uhr):
            with unittest.mock.patch.object(abruf, "einmal_abrufen", side_effect=verzoegert), \
                    unittest.mock.patch.object(abruf, "stempel_setzen", side_effect=stempel_bis_abbruch):
                with self.assertRaises(HartesEnde):
                    abruf.holen("https://h.invalid/a")
            uhr[0] += 1
            with unittest.mock.patch.object(abruf, "einmal_abrufen", side_effect=sofort):
                self.assertEqual(abruf.holen("https://h.invalid/b"), "ok")
        self.assertEqual(len(gesendet), 2)
        self.assertGreaterEqual(gesendet[1] - gesendet[0], abruf.ABSTAND)

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
