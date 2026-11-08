# -*- coding: utf-8 -*-
"""Tests der App-Hülle: Build in einer Kopie, Manifest, Dateiliste des Service Workers, Symbole, Inhalt unverändert,
Rahmen der Live-Seite, preise_aktualisieren mit Testabruf. Nur Standardbibliothek; node nur für die Syntaxprüfung (falls da).
Aufruf: powershell -File tests/alle-tests.ps1  (oder python -I -m unittest discover -s tests)"""
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "werkzeuge"))
import app_bauen  # noqa: E402


def png_groesse(pfad):
    b = Path(pfad).read_bytes()[:24]
    assert b[:8] == b"\x89PNG\r\n\x1a\n", f"{pfad}: kein PNG"
    return struct.unpack(">II", b[16:24])


class Bau(unittest.TestCase):
    """Baut einmal in einer Kopie (app/, quelle/, werkzeuge/), damit dist/ im Projekt unberührt bleibt."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.kopie = Path(cls.tmp.name) / "kb"
        for d in ("app", "quelle", "werkzeuge"):
            shutil.copytree(WURZEL / d, cls.kopie / d, ignore=shutil.ignore_patterns("__pycache__"))
        cls.lauf = subprocess.run([sys.executable, "-I", str(cls.kopie / "werkzeuge" / "app_bauen.py")],
                                  capture_output=True, text=True, encoding="utf-8")
        cls.dist = cls.kopie / "dist"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_build_laeuft(self):
        self.assertEqual(self.lauf.returncode, 0, self.lauf.stderr)
        self.assertIn("gebaut: dist/", self.lauf.stdout)

    def test_manifest(self):
        m = json.loads((self.dist / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(m["name"], "Kaufberatung")
        self.assertTrue(m["short_name"])
        self.assertEqual(m["display"], "standalone")
        for k in ("start_url", "scope", "id"):
            self.assertTrue(m[k].startswith("./"), f"{k} nicht relativ: {m[k]}")
        paare = {(i["sizes"], i["purpose"]) for i in m["icons"]}
        for g in ("192x192", "512x512"):
            for p in ("any", "maskable"):
                self.assertIn((g, p), paare)
        for i in m["icons"]:
            w, h = png_groesse(self.dist / i["src"])
            self.assertEqual(f"{w}x{h}", i["sizes"], i["src"])

    def test_apple_symbol(self):
        self.assertEqual(png_groesse(self.dist / "icons" / "apple-touch-icon.png"), (180, 180))

    def dateien(self):
        sw = (self.dist / "sw.js").read_text(encoding="utf-8")
        self.assertNotIn("__VERSION__", sw)
        self.assertNotIn("__DATEIEN__", sw)
        m = re.search(r"const DATEIEN = (\[.*?\]);", sw)
        self.assertTrue(m, "DATEIEN fehlt in sw.js")
        return json.loads(m.group(1)), sw

    def test_sw_dateien_vorhanden(self):
        liste, sw = self.dateien()
        version = json.loads((self.dist / "version.json").read_text(encoding="utf-8"))["app"]
        self.assertIn(json.dumps(version), sw)
        self.assertIn("./", liste)
        for d in liste:
            if d == "./":
                continue
            pfad, _, abfrage = d.partition("?")
            self.assertTrue((self.dist / pfad).is_file(), f"{d} fehlt in dist/")
            if abfrage:
                self.assertEqual(abfrage, "v=" + version)
        self.assertNotIn("preise.json", liste, "preise.json gehört nicht in den App-Cache")

    def test_seite_verweist_auf_versionierte_dateien(self):
        liste, _ = self.dateien()
        seite = (self.dist / "index.html").read_text(encoding="utf-8")
        for d in liste:
            if d.startswith(("app.js", "app.css")):
                self.assertIn(d, seite)
        self.assertIn('<link rel="manifest" href="manifest.webmanifest">', seite)
        self.assertEqual(seite.count("<title>"), 1)
        self.assertEqual(seite.lower().count("<meta charset"), 1)

    def test_inhalt_unveraendert(self):
        f = (WURZEL / "quelle" / "kaufberatung.html").read_text(encoding="utf-8")
        f = f.replace('<meta charset="utf-8">\n', "", 1).replace("<title>Kaufberatung</title>\n", "", 1)
        seite = (self.dist / "index.html").read_text(encoding="utf-8")
        self.assertIn(f, seite, "Inhalt der Kaufberatung wurde verändert")
        # Hülle vor dem Inhalt: app.js muss vor den Seitenskripten laufen
        self.assertLess(seite.index("app.js?v="), seite.index(f[:200]))

    def test_js_syntax(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node nicht vorhanden")
        for d in ("app.js", "sw.js"):
            r = subprocess.run([node, "--check", str(self.dist / d)], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, f"{d}: {r.stderr}")

    def test_kein_geheimnis_keine_wunschpreise(self):
        for p in self.dist.rglob("*"):
            if p.suffix in (".js", ".json", ".html", ".css", ".webmanifest"):
                t = p.read_text(encoding="utf-8")
                self.assertNotRegex(t, r"gh[pousr]_[A-Za-z0-9]{20,}", p.name)
                self.assertNotRegex(t, r"sk-[A-Za-z0-9]{20,}", p.name)


class Rahmen(unittest.TestCase):
    def test_fragment_bleibt(self):
        f = (WURZEL / "quelle" / "kaufberatung.html").read_text(encoding="utf-8")
        self.assertEqual(app_bauen.rahmen_entfernen(f), f)

    def test_live_rahmen_wird_entfernt(self):
        # Form der von "Artifact read" gespeicherten Live-Seite: doctype, head, <body>, Fragment, </body></html>
        f = (WURZEL / "quelle" / "kaufberatung.html").read_text(encoding="utf-8")
        live = ("﻿<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\"><style>:root{}</style></head><body>\n"
                + f + "\n</body></html>\n")
        aus = app_bauen.rahmen_entfernen(live)
        self.assertEqual(aus.strip("\n"), f.strip("\n"))
        app_bauen.pruefe_fragment(aus)

    def test_herkunft_passt(self):
        import hashlib
        f = (WURZEL / "quelle" / "kaufberatung.html").read_bytes()
        h = json.loads((WURZEL / "quelle" / "herkunft.json").read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(f).hexdigest(), h["sha256"])

    def test_falsche_datei_abgelehnt(self):
        with self.assertRaises(AssertionError):
            app_bauen.pruefe_fragment("<p>irgendwas</p><script></script>")


def angebot(g, h="haendler.de"):
    return {"gesamt": g, "artikel": g, "versand": 0.0, "haendler": h, "sterne": "4,0 (10)", "lieferung": "sofort"}


class Preise(unittest.TestCase):
    SKRIPT = WURZEL / "werkzeuge" / "preiswecker.py"

    def lauf(self, abruf, ziel):
        a = Path(self.tmp.name) / "abruf.json"
        a.write_text(json.dumps(abruf, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(WURZEL / "werkzeuge" / "preise_aktualisieren.py"),
                            "--abruf", str(a), "--ziel", str(ziel), "--skript", str(self.SKRIPT)],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(ziel.read_text(encoding="utf-8")), json.loads(r.stdout.strip().splitlines()[-1])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_fortschreiben(self):
        ziel = Path(self.tmp.name) / "seiten" / "preise.json"
        modelle = ["lg_c6elb", "lg_c69lb", "sam_s90h", "tcl_c8l", "sam_qn90f"]
        tag1 = {"zeit": "2026-11-07T10:00:00+01:00", "modelle": {m: {"sicher": angebot(2000.0 + i)} for i, m in enumerate(modelle)}}
        p1, b1 = self.lauf(tag1, ziel)
        self.assertEqual(b1["status"], "ok")
        self.assertEqual(set(p1["preise"]), set(modelle))
        self.assertEqual(p1["lauf"]["letzter"], tag1["zeit"])
        # Tag 2: LG C6ELB teurer (Tiefstpreis bleibt), TCL billiger (neuer Tiefstpreis), Samsung QN90F ohne belegtes Angebot
        tag2 = {"zeit": "2026-11-08T10:00:00+01:00", "modelle": {
            "lg_c6elb": {"sicher": angebot(2100.0)}, "lg_c69lb": {"sicher": angebot(2001.0)},
            "sam_s90h": {"sicher": angebot(2002.0)}, "tcl_c8l": {"sicher": angebot(1900.0, "billig.de")}, "sam_qn90f": {}}}
        p2, b2 = self.lauf(tag2, ziel)
        self.assertEqual(b2["status"], "teilweise")
        lg = p2["preise"]["lg_c6elb"]
        self.assertEqual(lg["aktuell"]["gesamt"], 2100.0)
        self.assertEqual(lg["tief"], {"gesamt": 2000.0, "datum": "2026-11-07", "haendler": "haendler.de"})
        self.assertEqual([v["d"] for v in lg["verlauf"]], ["2026-11-07", "2026-11-08"])
        tcl = p2["preise"]["tcl_c8l"]
        self.assertEqual(tcl["tief"], {"gesamt": 1900.0, "datum": "2026-11-08", "haendler": "billig.de"})
        self.assertEqual(p2["preise"]["sam_qn90f"], p1["preise"]["sam_qn90f"], "ohne Angebot bleibt der alte Stand")
        for d in p2["preise"].values():
            self.assertNotIn("meldung", d, "Wunschpreis-Abgleich gehört aufs Handy")
        # gleicher Tag noch einmal: Verlauf ohne Doppel
        p3, _ = self.lauf(tag2, ziel)
        self.assertEqual(len(p3["preise"]["lg_c6elb"]["verlauf"]), 2)

    def test_unplausibler_preis_bricht_ab(self):
        ziel = Path(self.tmp.name) / "preise.json"
        a = Path(self.tmp.name) / "abruf.json"
        a.write_text(json.dumps({"zeit": "2026-11-08T10:00:00+01:00", "modelle": {"lg_c6elb": {"sicher": angebot(0.0)}}}),
                     encoding="utf-8")
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(WURZEL / "werkzeuge" / "preise_aktualisieren.py"),
                            "--abruf", str(a), "--ziel", str(ziel), "--skript", str(self.SKRIPT)],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(ziel.exists(), "bei unplausiblem Preis darf nichts geschrieben werden")

    def test_push_nur_im_arbeitsbaum(self):
        ziel = Path(self.tmp.name) / "preise.json"
        a = Path(self.tmp.name) / "abruf.json"
        a.write_text(json.dumps({"zeit": "2026-11-08T10:00:00+01:00", "modelle": {"lg_c6elb": {"sicher": angebot(2000.0)}}}),
                     encoding="utf-8")
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(WURZEL / "werkzeuge" / "preise_aktualisieren.py"),
                            "--abruf", str(a), "--ziel", str(ziel), "--skript", str(self.SKRIPT), "--push"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--push nur mit dem gh-pages-Arbeitsbaum", r.stderr)


if __name__ == "__main__":
    unittest.main()
