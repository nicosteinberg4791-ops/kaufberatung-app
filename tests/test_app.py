# -*- coding: utf-8 -*-
"""Tests der App-Hülle: Build in einer Kopie, Manifest, Dateiliste des Service Workers, Symbole, Inhalt unverändert,
Rahmen der Live-Seite, preise_aktualisieren mit Testabruf. Nur Standardbibliothek; node nur für die Syntaxprüfung (falls da).
Aufruf: powershell -File tests/alle-tests.ps1  (oder python -I -m unittest discover -s tests)"""
import base64
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

    def lauf(self, abruf, ziel, wunsch=None, code=0):
        a = Path(self.tmp.name) / "abruf.json"
        a.write_text(json.dumps(abruf, ensure_ascii=False), encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k != "WUNSCHPREISE"}
        if wunsch is not None:
            env["WUNSCHPREISE"] = wunsch if isinstance(wunsch, str) else json.dumps(wunsch)
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(WURZEL / "werkzeuge" / "preise_aktualisieren.py"),
                            "--abruf", str(a), "--ziel", str(ziel), "--skript", str(self.SKRIPT), "--meldung", str(self.meldung)],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertEqual(r.returncode, code, r.stderr)
        self.ausgabe = r.stdout + r.stderr
        return json.loads(ziel.read_text(encoding="utf-8")), json.loads(r.stdout.strip().splitlines()[-1])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.meldung = Path(self.tmp.name) / "meldung.txt"

    def test_fortschreiben(self):
        ziel = Path(self.tmp.name) / "seiten" / "preise.json"
        modelle = ["lg_c6elb", "lg_c69lb", "sam_s90h", "tcl_c8l", "sam_qn90f"]
        # Größenvarianten seit 15.11.2026 im Wecker (Preise 900–1899 €)
        modelle += [f"{m}_{g}" for m in ("lg_c6elb", "sam_s90h", "tcl_c8l") for g in ("55", "65", "77")]
        af = {"af_cosori_tt": 249.0, "af_medion_p20": 79.95, "af_cosori_r901": 119.0}   # Air Fryer seit 09.11.2026 im Wecker
        af.update({"af_caso_3186": 137.09, "af_aeg_aafd11b": 169.0, "af_rh_27680": 124.3, "af_ninja_dz400": 135.9,
                   "af_tefal_ey942": 124.59, "af_gastroback_42586": 132.42, "af_ninja_af500": 169.0})   # ab V21 alle Top 10
        tag1 = {"zeit": "2026-11-07T10:00:00+01:00", "modelle": {m: {"sicher": angebot((900.0 if "_" in m[4:] else 2000.0) + i)}
                                                                 for i, m in enumerate(modelle)}}
        tag1["modelle"].update({m: {"sicher": angebot(p)} for m, p in af.items()})
        modelle = modelle + list(af)
        p1, b1 = self.lauf(tag1, ziel)
        self.assertEqual(b1["status"], "ok")
        self.assertEqual(set(p1["preise"]), set(modelle))
        self.assertEqual(p1["lauf"]["letzter"], tag1["zeit"])
        # Tag 2: LG C6ELB teurer (Tiefstpreis bleibt), TCL billiger (neuer Tiefstpreis), Samsung QN90F ohne belegtes Angebot
        tag2 = {"zeit": "2026-11-08T10:00:00+01:00", "modelle": {
            "lg_c6elb": {"sicher": angebot(2100.0)}, "lg_c69lb": {"sicher": angebot(2001.0)},
            "sam_s90h": {"sicher": angebot(2002.0)}, "tcl_c8l": {"sicher": angebot(1900.0, "billig.de")}, "sam_qn90f": {},
            "af_cosori_tt": {"sicher": angebot(239.0, "saturn")}, "af_medion_p20": {"sicher": angebot(79.95)},
            "af_cosori_r901": {"sicher": angebot(119.0)}}}
        p2, b2 = self.lauf(tag2, ziel)
        self.assertEqual(b2["status"], "teilweise")
        lg = p2["preise"]["lg_c6elb"]
        self.assertEqual(lg["aktuell"]["gesamt"], 2100.0)
        self.assertEqual(lg["tief"], {"gesamt": 2000.0, "datum": "2026-11-07", "haendler": "haendler.de"})
        self.assertEqual([v["d"] for v in lg["verlauf"]], ["2026-11-07", "2026-11-08"])
        tcl = p2["preise"]["tcl_c8l"]
        self.assertEqual(tcl["tief"], {"gesamt": 1900.0, "datum": "2026-11-08", "haendler": "billig.de"})
        self.assertEqual(p2["preise"]["sam_qn90f"], p1["preise"]["sam_qn90f"], "ohne Angebot bleibt der alte Stand")
        tt = p2["preise"]["af_cosori_tt"]
        self.assertEqual(tt["tief"], {"gesamt": 239.0, "datum": "2026-11-08", "haendler": "saturn"})
        self.assertEqual(p2["preise"]["af_medion_p20"]["name"], "Medion P20 XXL Twin")
        for d in p2["preise"].values():
            self.assertNotIn("meldung", d, "Wunschpreis-Abgleich gehört aufs Handy")
        # gleicher Tag noch einmal: Verlauf ohne Doppel
        p3, _ = self.lauf(tag2, ziel)
        self.assertEqual(len(p3["preise"]["lg_c6elb"]["verlauf"]), 2)
        self.assertEqual(self.meldung.read_text(encoding="utf-8"), "", "gleicher Tiefstpreis: keine zweite Meldung")

    def test_meldung_tiefstpreis_einmal(self):
        ziel = Path(self.tmp.name) / "preise.json"
        self.lauf({"zeit": "2026-11-07T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(2000.0)}}}, ziel)
        self.assertEqual(self.meldung.read_text(encoding="utf-8"), "", "erster Tag: kein Tiefstpreis-Treffer")
        p, b = self.lauf({"zeit": "2026-11-08T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(1900.0)}}}, ziel)
        self.assertEqual(self.meldung.read_text(encoding="utf-8"), "TCL C8L 1.900 € neuer Tiefstpreis")
        self.assertTrue(b["meldung"])
        self.assertIn("neuer Tiefstpreis", p["lauf"]["meldung"], "Tiefstpreis-Treffer darf öffentlich sein")
        self.lauf({"zeit": "2026-11-09T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(1900.0)}}}, ziel)
        self.assertEqual(self.meldung.read_text(encoding="utf-8"), "")

    def test_wunschpreis_bleibt_privat(self):
        ziel = Path(self.tmp.name) / "preise.json"
        w = {"tcl_c8l": 1950.5}
        self.lauf({"zeit": "2026-11-07T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(2000.0)}}}, ziel, w)
        self.assertEqual(self.meldung.read_text(encoding="utf-8"), "")
        p, b = self.lauf({"zeit": "2026-11-08T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(1900.0)}}}, ziel, w)
        m = self.meldung.read_text(encoding="utf-8")
        self.assertIn("unter Wunschpreis 1.950,50 €", m)
        self.assertEqual(b["wunschpreise"], 1)
        for spur in ("1950", "1.950", "Wunschpreis"):
            self.assertNotIn(spur, ziel.read_text(encoding="utf-8"), "Wunschpreis darf nicht in preise.json")
            self.assertNotIn(spur, self.ausgabe, "Wunschpreis darf nicht ins (öffentliche) Log")
        self.assertNotIn("meldung", p["preise"]["tcl_c8l"])
        # nächster Tag, Preis bleibt unter dem Wunschpreis: keine zweite Meldung
        self.lauf({"zeit": "2026-11-09T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(1920.0)}}}, ziel, w)
        self.assertEqual(self.meldung.read_text(encoding="utf-8"), "")
        # wieder darüber und erneut darunter: neue Meldung
        self.lauf({"zeit": "2026-11-10T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(1990.0)}}}, ziel, w)
        self.lauf({"zeit": "2026-11-11T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(1940.0)}}}, ziel, w)
        self.assertIn("unter Wunschpreis", self.meldung.read_text(encoding="utf-8"))

    def test_meldung_alle_treffer_ungekuerzt(self):
        """Codex R1 B1: fünf Modelle mit neuem Tiefstpreis und Wunschpreis-Treffer -> zehn vollständige Zeilen."""
        ziel = Path(self.tmp.name) / "preise.json"
        modelle = ["lg_c6elb", "lg_c69lb", "sam_s90h", "tcl_c8l", "sam_qn90f"]
        w = {m: 1950.5 for m in modelle}
        self.lauf({"zeit": "2026-11-07T07:00:00+01:00", "modelle": {m: {"sicher": angebot(2000.0)} for m in modelle}}, ziel, w)
        self.lauf({"zeit": "2026-11-08T07:00:00+01:00", "modelle": {m: {"sicher": angebot(1900.0)} for m in modelle}}, ziel, w)
        zeilen = self.meldung.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(zeilen), 10, zeilen)
        for kurz in ("LG C6ELB", "LG C69LB", "Samsung S90H", "TCL C8L", "Samsung QN90F"):
            self.assertIn(f"{kurz} 1.900 € neuer Tiefstpreis", zeilen)
            self.assertIn(f"{kurz} 1.900 € unter Wunschpreis 1.950,50 €", zeilen)

    def test_wunschpreise_ungueltig(self):
        ziel = Path(self.tmp.name) / "preise.json"
        _, b = self.lauf({"zeit": "2026-11-07T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(2000.0)}}},
                         ziel, '{"tcl_c8l": "teuer", "unbekannt": 777}')
        self.assertEqual(b["wunschpreise"], 0)
        self.assertNotIn("777", self.ausgabe, "auch ungültige Werte nie ausgeben")
        self.lauf({"zeit": "2026-11-08T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(1999.0)}}}, ziel, "kein json 4711")
        self.assertIn("kein JSON", self.ausgabe)
        self.assertNotIn("4711", self.ausgabe)

    def test_alles_fehler_exit3_alte_preise_bleiben(self):
        ziel = Path(self.tmp.name) / "preise.json"
        p1, _ = self.lauf({"zeit": "2026-11-07T07:00:00+01:00", "modelle": {"tcl_c8l": {"sicher": angebot(2000.0)}}}, ziel)
        gesperrt = {"zeit": "2026-11-08T07:00:00+01:00",
                    "modelle": {m: {"fehler": "HTTPError: HTTP Error 403: Forbidden"} for m in ("lg_c6elb", "lg_c69lb", "sam_s90h", "tcl_c8l", "sam_qn90f")}}
        p2, b = self.lauf(gesperrt, ziel, code=3)
        self.assertEqual(b["status"], "fehler")
        self.assertIn("403", b["modelle"]["tcl_c8l"])
        self.assertEqual(p2["lauf"]["status"], "fehler")
        self.assertEqual(p2["preise"]["tcl_c8l"], p1["preise"]["tcl_c8l"])

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
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(WURZEL / "werkzeuge" / "preise_aktualisieren.py"),
                            "--ziel", str(ziel), "--nur-push"], capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--push nur mit dem gh-pages-Arbeitsbaum", r.stderr)


class PushSchutz(unittest.TestCase):
    """B2/B3 der Codex-Erstprüfung: Push nur aus eigenem gh-pages-Arbeitsbaum, Commit nur mit preise.json."""

    def setUp(self):
        # Bei "git commit -a" setzt Git GIT_INDEX_FILE & Co. auf den Hook; eigene Git-Aufrufe der Tests
        # (auch die im Prüfling) würden sonst den falschen Index treffen -> GIT_* für diesen Test entfernen.
        umgebung = mock.patch.dict(os.environ)
        umgebung.start()
        self.addCleanup(umgebung.stop)
        for k in [k for k in os.environ if k.startswith("GIT_")]:
            del os.environ[k]
        import preise_aktualisieren
        self.pa = preise_aktualisieren
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "seiten"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "gh-pages")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.repo / "preise.json").write_text('{"zeit": "2026-11-07T10:00:00+01:00"}\n', encoding="utf-8")
        self.git("add", "preise.json")
        self.git("commit", "-q", "-m", "start")

    def git(self, *a):
        return subprocess.run(["git", "-C", str(self.repo), *a], check=True, capture_output=True, text=True).stdout

    def test_kein_arbeitsbaum(self):
        leer = Path(self.tmp.name) / "leer"
        leer.mkdir()
        with self.assertRaises(SystemExit):
            self.pa.arbeitsbaum_pruefen(leer)
        unter = self.repo / "unter"
        unter.mkdir()
        with self.assertRaises(SystemExit):   # Unterordner eines anderen Repos zählt nicht
            self.pa.arbeitsbaum_pruefen(unter)

    def test_falscher_zweig(self):
        self.git("checkout", "-q", "-b", "main")
        with self.assertRaises(SystemExit):
            self.pa.arbeitsbaum_pruefen(self.repo)

    def test_fremder_index_wird_abgelehnt(self):
        (self.repo / "privat.txt").write_text("x", encoding="utf-8")
        self.git("add", "privat.txt")
        (self.repo / "preise.json").write_text('{"zeit": "2026-11-08T10:00:00+01:00"}\n', encoding="utf-8")
        with self.assertRaises(SystemExit):
            self.pa.push(self.repo / "preise.json")
        self.assertEqual(self.git("rev-list", "--count", "HEAD").strip(), "1", "es darf kein Commit entstehen")

    def test_commit_nur_preise(self):
        (self.repo / "preise.json").write_text('{"zeit": "2026-11-08T10:00:00+01:00"}\n', encoding="utf-8")
        (self.repo / "sonst.txt").write_text("nicht gestaged", encoding="utf-8")
        echt = subprocess.run

        def ohne_push(befehl, *a, **k):   # kein Remote: nur den git push überspringen
            if "push" in befehl:
                return subprocess.CompletedProcess(befehl, 0)
            return echt(befehl, *a, **k)
        with mock.patch.object(self.pa.subprocess, "run", side_effect=ohne_push):
            self.pa.push(self.repo / "preise.json")
        self.assertEqual(self.git("show", "--name-only", "--format=", "HEAD").split(), ["preise.json"])


class Workflow(unittest.TestCase):
    """Tägliche Preisabfrage in GitHub Actions: Auslöser, Rechte, Secrets nur als Verweis, kein Topic im Klartext."""

    def setUp(self):
        self.t = (WURZEL / ".github" / "workflows" / "preise.yml").read_text(encoding="utf-8")

    def test_ausloeser_und_rechte(self):
        self.assertRegex(self.t, r'(?m)^  schedule:\n    - cron: "\d+ \d+ \* \* \*"')
        self.assertIn("workflow_dispatch:", self.t)
        self.assertRegex(self.t, r"(?m)^permissions:\n  contents: write")
        self.assertIn("git worktree add -B gh-pages .veroeffentlichung origin/gh-pages", self.t)

    def test_reihenfolge_versand_vor_push(self):
        """Codex R1 B2: Secret prüfen -> schreiben -> senden -> erst dann pushen; kein kombiniertes --push."""
        t = self.t
        stellen = [t.index('if [ -z "$NTFY_TOPIC" ]'), t.index("preise_aktualisieren.py --meldung"),
                   t.index("ntfy.sh/$NTFY_TOPIC"), t.index("preise_aktualisieren.py --nur-push")]
        self.assertEqual(stellen, sorted(stellen))
        self.assertNotIn("--push ", t.replace("--nur-push", ""))
        self.assertEqual(t.count("exit 1"), 4, "fehlendes Secret, falscher VAPID-Schlüssel, Totalausfall und ungültiges Abo machen den Lauf rot")
        self.assertNotIn("continue-on-error", t)

    def test_secrets_nur_als_verweis(self):
        self.assertIn("NTFY_TOPIC: ${{ secrets.NTFY_TOPIC }}", self.t)
        self.assertIn("WUNSCHPREISE: ${{ secrets.WUNSCHPREISE }}", self.t)
        self.assertEqual(re.findall(r"ntfy\.sh/[^\s\"']+", self.t), ["ntfy.sh/$NTFY_TOPIC"])
        # Ausdrücke nur als env-Zuweisung (NAME: ${{ ... }}), nie in run-Zeilen (Einschleusen von Befehlen)
        for zeile in self.t.splitlines():
            if "${{" in zeile:
                self.assertRegex(zeile, r"^\s+[A-Z_]+: \$\{\{ [\w.]+ \}\}$", "Ausdruck außerhalb von env")

    def test_webpush_vor_push_und_abo_fehler_blockiert_nicht(self):
        """Web Push (D6): nach ntfy, vor dem Push; 404/410 (Exit 4) blockiert die Preise nicht, macht den Lauf aber rot."""
        t = self.t
        stellen = [t.index("ntfy.sh/$NTFY_TOPIC"), t.index("webpush.mjs --senden"), t.index("preise_aktualisieren.py --nur-push"),
                   t.index("steps.webpush.outputs.ungueltig == '1'")]
        self.assertEqual(stellen, sorted(stellen))
        self.assertIn("PUSH_ABO: ${{ secrets.PUSH_ABO }}", t)
        self.assertIn("VAPID_PRIVAT: ${{ secrets.VAPID_PRIVAT }}", t)
        self.assertIn('if [ "$rc" = 4 ]; then echo "ungueltig=1" >> "$GITHUB_OUTPUT"; elif [ "$rc" != 0 ]; then exit "$rc"; fi', t)
        self.assertIn("webpush.mjs --oeffentlich", t)
        # Codex B3: Treffer und Test mit eigener Art, damit der Test keinen Treffer verdrängt
        self.assertIn('--art "$3"', t)
        self.assertIn('"TV-Preiswecker" treffer', t)
        self.assertIn('"Kaufberatung: Test" test', t)

    def test_anleitung_ohne_zustellungszusage(self):
        """Codex B1: keine feste Zustellzeit und keine Zuverlässigkeitszusage in der Anleitung."""
        a = (WURZEL / "docs" / "anleitung-handy.md").read_text(encoding="utf-8")
        for verboten in ("ein bis zwei Minuten", "Damit es zuverlässig ankommt"):
            self.assertNotIn(verboten, a)
        self.assertIn("Eine Zustellung ist nicht garantiert", a)


class WebPush(unittest.TestCase):
    """Eigene Benachrichtigung: Sende-Werkzeug (node --test), Schlüssel in der App, Empfang im Service Worker."""

    def test_node_tests(self):
        r = subprocess.run(["node", "--test", "tests/webpush.test.mjs"], cwd=WURZEL, capture_output=True, text=True,
                           encoding="utf-8", timeout=180)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-1500:])
        r = subprocess.run(["node", "werkzeuge/webpush.mjs", "--selbsttest"], cwd=WURZEL, capture_output=True, text=True,
                           encoding="utf-8", timeout=60)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-800:])

    def test_oeffentlicher_schluessel_in_app(self):
        js = (WURZEL / "app" / "app.js").read_text(encoding="utf-8")
        k = re.findall(r'VAPID_OEFFENTLICH = "([A-Za-z0-9_-]+)"', js)
        self.assertEqual(len(k), 1)
        roh = base64.urlsafe_b64decode(k[0] + "=" * (-len(k[0]) % 4))
        self.assertEqual((len(roh), roh[0]), (65, 4), "unkomprimierter P-256-Punkt")
        self.assertIn("userVisibleOnly: true", js)
        # Codex B2: lokales Abo ist keine fertige Einrichtung; Secret und Testlauf bleiben im Status genannt
        self.assertNotIn("Push ist auf diesem Handy eingerichtet", js)
        self.assertIn("Dieses Handy ist für Push angemeldet. Meldungen kommen erst, wenn der Einrichtungscode als Secret PUSH_ABO", js)
        # Passt der private Schlüssel (nur auf Nicos Rechner, außerhalb des Repos) zum öffentlichen in der App?
        privat = WURZEL.parent / "Kaufberatung-App-privat" / "vapid-privat.json"
        if not privat.exists():
            self.skipTest("privater Schlüssel nicht auf diesem Rechner")
        env = dict(os.environ, VAPID_PRIVAT=privat.read_text(encoding="utf-8"))
        r = subprocess.run(["node", "werkzeuge/webpush.mjs", "--oeffentlich"], cwd=WURZEL, capture_output=True, text=True,
                           encoding="utf-8", timeout=60, env=env)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, k[0]))

    def test_service_worker_zeigt_jede_push_nachricht(self):
        sw = (WURZEL / "app" / "sw.js").read_text(encoding="utf-8")
        teil = sw[sw.index('addEventListener("push"'):sw.index('addEventListener("pushsubscriptionchange"')]
        self.assertIn("e.waitUntil(self.registration.showNotification(", teil)
        self.assertIn(r"^\.\/(#[A-Za-z0-9_-]+)?$", teil, "Ziel nur innerhalb der App")


class AirFryerImWecker(unittest.TestCase):
    """Air Fryer im Preiswecker (Nico 09.11.2026): Modelle, Preisgrenzen je Modell, Ids der App-Hülle."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pw_af", WURZEL / "werkzeuge" / "preiswecker.py")
        cls.pw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.pw)

    # Ab V21 alle zehn Modelle der Air Fryer Top 10 (Nico 09.11.2026 „für alle modelle preiswecker“)
    AF = ["af_cosori_tt", "af_medion_p20", "af_cosori_r901", "af_caso_3186", "af_aeg_aafd11b", "af_rh_27680",
          "af_ninja_dz400", "af_tefal_ey942", "af_gastroback_42586", "af_ninja_af500"]
    TV = ["lg_c6elb", "lg_c69lb", "sam_s90h", "tcl_c8l", "sam_qn90f"]
    # Größenwahl (Nico 15.11.2026 „Ja, alle Größen“): C6ELB, S90H, C8L in 55/65/75–77″, kein C69LB
    GR = [f"{m}_{g}" for m in ("lg_c6elb", "sam_s90h", "tcl_c8l") for g in ("55", "65", "77")]

    def test_genau_zehn_air_fryer_und_fernseher_mit_groessen(self):
        """Grenzen werden aus dem Präfix af_ abgeleitet: kein Fernseher darf die Air-Fryer-Grenze bekommen."""
        self.assertEqual(list(self.pw.MODELLE), self.TV + self.GR + self.AF)
        self.assertEqual(sorted(self.pw.GRENZEN), sorted(self.AF))
        self.assertEqual(len(set(self.pw.MODELLE.values())), 24, "jede heise-Seite nur einmal")

    def test_groessen_seiten(self):
        """Größenvarianten: heise-Seite passt zur Modellnummer der Größe, kein C69LB, Fernsehergrenze."""
        nummer = {"lg_c6elb": "oled{g}c6elb", "sam_s90h": None, "tcl_c8l": "{g}c8l"}
        for gid in self.GR:
            m, g = gid.rsplit("_", 1)
            url = self.pw.MODELLE[gid]
            self.assertTrue(url.startswith("https://preisvergleich.heise.de/"), gid)
            if nummer[m]:
                self.assertIn(nummer[m].format(g="75" if (m == "tcl_c8l" and g == "77") else g), url, gid)
            self.assertNotIn(gid, self.pw.GRENZEN)
            self.assertIn(gid, self.pw.NAMEN)
            self.assertIn(gid, self.pw.KURZ)
        self.assertFalse([k for k in self.pw.MODELLE if k.startswith("lg_c69lb_")])

    def test_groessen_ohne_meldung(self):
        """Neuer Tiefstpreis bzw. Wunschpreis: Meldung nur für 83/85″, Größenvarianten speichern nur (Vorprüfung B1)."""
        akt = {"gesamt": 900.0, "artikel": 900.0, "versand": 0.0, "haendler": "H", "sterne": "", "lieferung": ""}
        erg = {"zeit": "2026-11-16T06:30:00+01:00", "modelle": {m: {"sicher": dict(akt)} for m in ("lg_c6elb", "lg_c6elb_65")}}
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp, "db")
            for m in self.pw.MODELLE:
                (db / "preise").mkdir(parents=True, exist_ok=True)
                (db / "preise" / f"{m}.json").write_text(json.dumps(
                    {"version": 1, "tief": {"gesamt": 1000.0, "datum": "2026-11-15"}}), encoding="utf-8")
            for m in ("lg_c6elb", "lg_c6elb_65"):
                (db / "wunsch").mkdir(exist_ok=True)
                (db / "wunsch" / f"{m}.json").write_text(json.dumps({"version": 1, "preis": 950}), encoding="utf-8")
            erg_ = self.pw.abgleich(erg, str(db), str(Path(tmp, "aus")))
        self.assertTrue(any(t.startswith(self.pw.KURZ["lg_c6elb"] + " ") for t in erg_["treffer"]), erg_["treffer"])
        self.assertFalse([t for t in erg_["treffer"] if self.pw.KURZ["lg_c6elb_65"] in t], erg_["treffer"])
        self.assertTrue(self.pw.ist_groesse("tcl_c8l_77") and not self.pw.ist_groesse("tcl_c8l"))

    def test_429_wird_einmal_wiederholt(self):
        """B-429 (15.11.2026): heise drosselt ab ~19 Abrufen; nach HTTP 429 warten und genau einmal wiederholen."""
        import urllib.error
        fehler429 = urllib.error.HTTPError("https://x", 429, "Too Many Requests", {"Retry-After": "7"}, None)
        aufrufe = []

        def abrufen(url, bis=None):
            self.assertIsNotNone(bis, "abruf_alle übergibt den Termin der Lauffrist")
            aufrufe.append(url)
            if len(aufrufe) == 1:
                raise fehler429
            return "seite"
        ergebnis = {"angebote": 1, "sicher": {"gesamt": 1.0}, "roh": None}
        with mock.patch.dict(self.pw.MODELLE, {"tcl_c8l": "https://x"}, clear=True), \
                mock.patch.object(self.pw, "abrufen", side_effect=abrufen), \
                mock.patch.object(self.pw, "auswerten", return_value=ergebnis), \
                mock.patch.object(self.pw.time, "sleep") as schlaf:
            erg = self.pw.abruf_alle()
        self.assertEqual(len(aufrufe), 2)
        self.assertNotIn("fehler", erg["modelle"]["tcl_c8l"])
        self.assertIn(mock.call(7), schlaf.call_args_list, "Retry-After wird beachtet")
        # zweimal 429: Fehler bleibt stehen, keine Endlosschleife
        with mock.patch.dict(self.pw.MODELLE, {"tcl_c8l": "https://x"}, clear=True), \
                mock.patch.object(self.pw, "abrufen", side_effect=fehler429) as ab, \
                mock.patch.object(self.pw.time, "sleep"):
            erg = self.pw.abruf_alle()
        self.assertEqual(ab.call_count, 2)
        self.assertIn("429", erg["modelle"]["tcl_c8l"]["fehler"])

    def test_abruffehler_eigene_meldung(self):
        """Abruffehler (z. B. 429) heißt nicht „kein Angebot“: eigene Zeile in der Laufmeldung (B-429)."""
        erg = {"zeit": "2026-11-16T06:30:00+01:00", "modelle": {
            "lg_c6elb": {"fehler": "HTTPError: HTTP Error 429: Too Many Requests"}, "tcl_c8l": {"angebote": 3, "sicher": None}}}
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp, "db")
            (db / "preise").mkdir(parents=True)
            for m in self.pw.MODELLE:
                (db / "preise" / f"{m}.json").write_text(json.dumps({"version": 1}), encoding="utf-8")
            erg_ = self.pw.abgleich(erg, str(db), str(Path(tmp, "aus")), anlegen=True)
            gespeichert = json.loads(Path(tmp, "aus", "wecker_lauf.json").read_text(encoding="utf-8"))["meldung"]
        self.assertEqual(erg_["status"], "fehler")  # kein Modell mit Preis
        # gespeicherte (auf 300 Zeichen begrenzte) Meldung: Abruffehler sichtbar, Rest gekürzt statt verdrängt (B429-02)
        self.assertLessEqual(len(erg_["lauf"]), 300)
        self.assertEqual(gespeichert, erg_["lauf"])
        self.assertTrue(gespeichert.startswith("Abruf fehlgeschlagen, alter Preis bleibt: " + self.pw.KURZ["lg_c6elb"] + " (HTTP 429)."), gespeichert)
        kein = gespeichert.split("Kein Angebot mit belegtem Versand")[1]
        self.assertIn("(23):", kein)
        self.assertIn("weitere.", kein)
        self.assertNotIn(self.pw.KURZ["lg_c6elb"] + ",", kein)

    def test_meldung_viele_abruffehler_gekuerzt(self):
        """B429-02: auch 20 Abruffehler + kein Angebot + Problem bleiben in 300 Zeichen, jeder Teil sichtbar."""
        erg = {"zeit": "2026-11-16T06:30:00+01:00", "modelle": {
            m: {"fehler": "HTTPError: HTTP Error 429: Too Many Requests"} for m in list(self.pw.MODELLE)[:20]}}
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp, "db")
            (db / "preise").mkdir(parents=True)
            for m in self.pw.MODELLE:
                (db / "preise" / f"{m}.json").write_text(json.dumps({"version": 1}), encoding="utf-8")
            (db / "preise" / f"{list(self.pw.MODELLE)[-1]}.json").write_text("kaputt", encoding="utf-8")
            erg_ = self.pw.abgleich(erg, str(db), str(Path(tmp, "aus")), anlegen=True)
        t = erg_["lauf"]
        self.assertLessEqual(len(t), 300, t)
        self.assertTrue(t.startswith("Abruf fehlgeschlagen, alter Preis bleibt (20): "), t)
        self.assertIn("Fehler", t.split("(20):")[1])
        self.assertIn("Kein Angebot mit belegtem Versand", t)
        self.assertEqual(erg_["status"], "fehler")  # kein Modell gelesen

    def test_429_grenzen_und_andere_fehler(self):
        """B-429: andere Fehler nicht wiederholen; ungültiges Retry-After → 30 s; Budget und Lauffrist begrenzen."""
        import urllib.error

        def h429(wert):
            return urllib.error.HTTPError("https://x", 429, "Too Many Requests", {"Retry-After": wert} if wert is not None else {}, None)
        for wert in (None, "0", "-5", "121", "Wed, 21 Oct 2026 07:28:00 GMT", "abc"):
            self.assertEqual(self.pw._warte_429(h429(wert)), 30, wert)
        self.assertEqual(self.pw._warte_429(urllib.error.HTTPError("https://x", 429, "x", None, None)), 30)
        self.assertEqual(self.pw._warte_429(h429("120")), 120)
        ein = {"tcl_c8l": "https://x"}
        for fehler in (urllib.error.HTTPError("https://x", 503, "Unavailable", {}, None), TimeoutError("timed out")):
            with mock.patch.dict(self.pw.MODELLE, ein, clear=True), \
                    mock.patch.object(self.pw, "abrufen", side_effect=fehler) as ab, \
                    mock.patch.object(self.pw.time, "sleep"):
                erg = self.pw.abruf_alle()
            self.assertEqual(ab.call_count, 1, fehler)
            self.assertIn("fehler", erg["modelle"]["tcl_c8l"])
        # Wartebudget: 240 s / 120 s je Wiederholung → nur die ersten zwei Modelle werden wiederholt
        drei = {"tcl_c8l": "https://a", "lg_c6elb": "https://b", "sam_s90h": "https://c"}
        with mock.patch.dict(self.pw.MODELLE, drei, clear=True), \
                mock.patch.object(self.pw, "abrufen", side_effect=h429("120")) as ab, \
                mock.patch.object(self.pw.time, "sleep") as schlaf:
            erg = self.pw.abruf_alle()
        self.assertEqual(ab.call_count, 5)
        self.assertEqual(schlaf.call_args_list.count(mock.call(120)), 2)
        self.assertEqual(len(erg["modelle"]), 3)
        # Lauffrist: Uhr springt nach dem ersten Modell auf 400 s → zweites und drittes nicht abgerufen
        uhr = iter([0, 0, 400, 400, 400, 400, 400])
        with mock.patch.dict(self.pw.MODELLE, drei, clear=True), \
                mock.patch.object(self.pw, "abrufen", return_value="seite") as ab, \
                mock.patch.object(self.pw, "auswerten", return_value={"angebote": 1, "sicher": None, "roh": None}), \
                mock.patch.object(self.pw.time, "monotonic", side_effect=lambda: next(uhr)), \
                mock.patch.object(self.pw.time, "sleep"):
            erg = self.pw.abruf_alle()
        self.assertEqual(ab.call_count, 1)
        self.assertIn("Lauffrist", erg["modelle"]["lg_c6elb"]["fehler"])
        self.assertIn("Lauffrist", erg["modelle"]["sam_s90h"]["fehler"])
        # Lauffrist verhindert die Wiederholung, wenn Warten + Abruf nicht mehr hineinpassen
        uhr = iter([0, 0, 300, 300])
        with mock.patch.dict(self.pw.MODELLE, ein, clear=True), \
                mock.patch.object(self.pw, "abrufen", side_effect=h429("100")) as ab, \
                mock.patch.object(self.pw.time, "monotonic", side_effect=lambda: next(uhr)), \
                mock.patch.object(self.pw.time, "sleep") as schlaf:
            erg = self.pw.abruf_alle()
        self.assertEqual(ab.call_count, 1)
        self.assertNotIn(mock.call(100), schlaf.call_args_list)

    def test_abruf_endet_am_termin(self):
        """Codex B429-01: eine tröpfelnde Antwort endet am Termin mit TimeoutError; Socket-Timeout ≤ Rest, ≤ 30 s."""
        import itertools

        class Tropf:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read1(self, n=-1):
                return b"x"
        uhr = itertools.count(0, 10)
        with mock.patch.object(self.pw.urllib.request, "urlopen", return_value=Tropf()) as uo, \
                mock.patch.object(self.pw.time, "monotonic", side_effect=lambda: next(uhr)):
            with self.assertRaises(TimeoutError):
                self.pw.abrufen("https://x", bis=25)
        self.assertEqual(uo.call_args.kwargs["timeout"], 25)
        with mock.patch.object(self.pw.urllib.request, "urlopen", return_value=Tropf()) as uo, \
                mock.patch.object(self.pw.time, "monotonic", return_value=0):
            with mock.patch.object(Tropf, "read1", side_effect=[b"<html>", b""]):
                self.assertEqual(self.pw.abrufen("https://x", bis=1000), "<html>")
        self.assertEqual(uo.call_args.kwargs["timeout"], 30)

    def test_blockierender_abruf_endet_mit_lauffrist(self):
        """Codex B429-01 R3: ein Abruf, der in einem einzigen Aufruf hängt (z. B. read() über einen ganzen Block),
        wird von der Lauffrist abgebrochen; der Lauf geht weiter, Fehler aus dem Thread kommen unverändert an."""
        import threading
        import time
        import urllib.error
        frei = threading.Event()
        self.addCleanup(frei.set)

        def haengt(url, bis=None):
            frei.wait(30)
            return "zu spät"
        drei = {"tcl_c8l": "https://a", "lg_c6elb": "https://b"}
        t0 = time.monotonic()
        with mock.patch.dict(self.pw.MODELLE, drei, clear=True), \
                mock.patch.object(self.pw, "LAUF_FRIST", 0.3), mock.patch.object(self.pw, "ABRUF_MAX", 0.1), \
                mock.patch.object(self.pw, "abrufen", side_effect=haengt), \
                mock.patch.object(self.pw.time, "sleep"):
            erg = self.pw.abruf_alle()
        self.assertLess(time.monotonic() - t0, 5)
        self.assertIn("abgebrochen", erg["modelle"]["tcl_c8l"]["fehler"])
        self.assertIn("Lauffrist", erg["modelle"]["lg_c6elb"]["fehler"])
        f = urllib.error.HTTPError("https://x", 429, "x", {}, None)
        with self.assertRaises(urllib.error.HTTPError):
            self.pw._mit_frist(mock.Mock(side_effect=f), 5)
        self.assertEqual(self.pw._mit_frist(lambda: "ok", 5), "ok")

    def test_oeffentliche_meldung_behaelt_abruffehler(self):
        """Codex B429-03: 1 × HTTP 429 und 23 Tiefstpreis-Treffer → veröffentlichte Meldung nennt den Abruffehler."""
        import preise_aktualisieren as pa
        text = "Abruf fehlgeschlagen, alter Preis bleibt: Ninja AF500 (HTTP 429). Treffer: x"
        treffer = [f"{self.pw.KURZ[m]} 100 € neuer Tiefstpreis" for m in list(self.pw.MODELLE)[:23]]
        t = pa.oeffentlicher_lauftext(text, treffer + ["LG C6ELB unter Wunschpreis 999 €"], self.pw._kurzliste)
        self.assertLessEqual(len(t), 300, t)
        self.assertTrue(t.startswith("Abruf fehlgeschlagen, alter Preis bleibt: Ninja AF500 (HTTP 429). Treffer (23): "), t)
        self.assertIn("weitere.", t)
        self.assertNotIn("Wunschpreis", t)
        # viele Abruffehler + Kein Angebot + Treffer: alle drei Teile sichtbar, Abruffehler auf 150 Zeichen begrenzt
        lang = ("Abruf fehlgeschlagen, alter Preis bleibt: " + ", ".join(f"{self.pw.KURZ[m]} (HTTP 429)" for m in list(self.pw.MODELLE)[:9])
                + ". Kein Angebot mit belegtem Versand: TCL C8L.")
        t = pa.oeffentlicher_lauftext(lang, treffer[:3], self.pw._kurzliste)
        self.assertLessEqual(len(t), 300, t)
        self.assertIn(" …", t.split("Treffer")[0])
        self.assertIn("Kein Angebot", t)
        self.assertIn("Treffer: " + treffer[0], t)
        # ohne Abruffehler bleibt das bisherige Verhalten: Text, dann Treffer
        self.assertEqual(pa.oeffentlicher_lauftext("Kein Angebot mit belegtem Versand: TCL C8L.", treffer[:1], self.pw._kurzliste),
                         "Kein Angebot mit belegtem Versand: TCL C8L. Treffer: " + treffer[0] + ".")

    def test_groessenknoepfe_44px(self):
        """Größenleiste (Seite: .gr-leiste .segx button 36 px) bekommt bei grobem Zeiger 44 px Tippfläche."""
        css = (WURZEL / "app" / "app.css").read_text(encoding="utf-8")
        grob = css[css.index("@media (pointer: coarse)"):]
        grob = grob[:grob.index("\n}\n")]
        self.assertRegex(grob, r"\.gr-leiste \.segx button \{ min-height: 44px; \}")

    @staticmethod
    def seite(*preise):
        return " ".join('{"raw_price": %s, "merchant_name": "H%d", "merchant_free_shipping": true}' % (p, i)
                        for i, p in enumerate(preise))

    def test_modelle_und_namen(self):
        for m in self.AF:
            self.assertIn(m, self.pw.MODELLE)
            self.assertTrue(self.pw.MODELLE[m].startswith("https://preisvergleich.heise.de/"))
            self.assertIn(m, self.pw.NAMEN)
            self.assertIn(m, self.pw.KURZ)
        self.assertEqual(set(self.pw.NAMEN), set(self.pw.MODELLE))
        self.assertEqual(set(self.pw.KURZ), set(self.pw.MODELLE))

    def test_preisgrenze_je_modell(self):
        t = self.seite(12.0, 79.95, 5000)   # Zubehör 12 €, Fehlwert 5000 €
        af = self.pw.auswerten(t, self.pw.GRENZEN["af_medion_p20"])
        self.assertEqual(af["angebote"], 1)
        self.assertEqual(af["sicher"]["gesamt"], 79.95)
        # Standard (Fernseher) verwirft dasselbe Angebot weiterhin
        self.assertEqual(self.pw.auswerten(t)["angebote"], 1)
        self.assertEqual(self.pw.auswerten(self.seite(79.95))["angebote"], 0)
        self.assertEqual(self.pw.auswerten(self.seite(2000))["angebote"], 1)

    def test_grenzen_exakt_und_abruf_alle(self):
        """Codex R1 B1: alle Air-Fryer-Grenzen exakt (Rand drin, knapp außerhalb draußen) und Übergabe durch abruf_alle()."""
        for m in self.AF:
            self.assertEqual(self.pw.GRENZEN[m], (30, 1000))
            g = self.pw.GRENZEN[m]
            self.assertEqual(self.pw.auswerten(self.seite(29.99, 30, 1000, 1000.01), g)["angebote"], 2)
        self.assertEqual(self.pw.GRENZE_STANDARD, (500, 20000))
        self.assertEqual(self.pw.auswerten(self.seite(499.99, 500, 20000, 20000.01))["angebote"], 2)
        # abruf_alle: Air Fryer mit 150 € gilt, derselbe Wert beim Fernseher nicht; Zubehör 12 € fällt beim Air Fryer weg
        seite = self.seite(12, 150)
        with mock.patch.object(self.pw, "abrufen", return_value=seite), mock.patch.object(self.pw.time, "sleep"),                 mock.patch.object(self.pw, "ABRUF_JE_LAUF", 99):   # Grenzen aller Modelle, Kontingent hier nicht Gegenstand
            erg = self.pw.abruf_alle()
        for m in self.AF:
            self.assertEqual(erg["modelle"][m]["angebote"], 1, m)
            self.assertEqual(erg["modelle"][m]["sicher"]["gesamt"], 150.0, m)
        for m in set(self.pw.MODELLE) - set(self.AF):
            self.assertEqual(erg["modelle"][m]["angebote"], 0, m)

    def test_app_ids_gleich_modelle(self):
        js = (WURZEL / "app" / "app.js").read_text(encoding="utf-8")
        m = re.search(r"const IDS = \[([^\]]*)\];", js)
        self.assertIsNotNone(m)
        self.assertEqual(re.findall(r'"([a-z0-9_]+)"', m.group(1)), list(self.pw.MODELLE))


class Kontingent(unittest.TestCase):
    """heise-Kontingent (Livelauf 15.11.2026: genau 18 Abrufe je Fenster): höchstens ABRUF_JE_LAUF Abrufe je Lauf,
    älteste Preise zuerst, Nachläufe holen nur, was heute noch fehlt."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pw_k", WURZEL / "werkzeuge" / "preiswecker.py")
        cls.pw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.pw)
        import preise_aktualisieren
        cls.pa = preise_aktualisieren

    ERG = {"angebote": 1, "sicher": {"gesamt": 100.0, "artikel": 100.0, "versand": 0.0, "haendler": "H",
                                      "sterne": "", "lieferung": ""}, "roh": None}

    def test_hoechstens_16_abrufe_rest_verschoben(self):
        self.assertLess(self.pw.ABRUF_JE_LAUF, 18, "Reserve unter dem gemessenen Kontingent")
        ids = list(self.pw.MODELLE)
        with mock.patch.object(self.pw, "abrufen", return_value="seite") as ab,                 mock.patch.object(self.pw, "auswerten", return_value=self.ERG),                 mock.patch.object(self.pw.time, "sleep"):
            erg = self.pw.abruf_alle(list(reversed(ids)))
        self.assertEqual(ab.call_count, self.pw.ABRUF_JE_LAUF)
        reihe = list(reversed(ids))
        self.assertEqual([c.args[0] for c in ab.call_args_list], [self.pw.MODELLE[m] for m in reihe[:16]], "Reihenfolge des Aufrufers")
        self.assertTrue(all(erg["modelle"][m].get("verschoben") for m in reihe[16:]))
        # Teilreihe: übrige Modelle gelten als heute schon gelesen, werden nicht abgerufen
        with mock.patch.object(self.pw, "abrufen", return_value="seite") as ab,                 mock.patch.object(self.pw, "auswerten", return_value=self.ERG),                 mock.patch.object(self.pw.time, "sleep"):
            erg = self.pw.abruf_alle(ids[:2])
        self.assertEqual(ab.call_count, 2)
        self.assertTrue(all(erg["modelle"][m].get("heute_schon") for m in ids[2:]))
        self.assertEqual(len(erg["modelle"]), len(ids))

    def test_429_meldung_mit_messwerten(self):
        import urllib.error
        f = urllib.error.HTTPError("https://x", 429, "Too Many Requests", {"Retry-After": "300"}, None)
        with mock.patch.dict(self.pw.MODELLE, {"tcl_c8l": "https://x"}, clear=True),                 mock.patch.object(self.pw, "abrufen", side_effect=f), mock.patch.object(self.pw.time, "sleep"):
            erg = self.pw.abruf_alle()
        self.assertRegex(erg["modelle"]["tcl_c8l"]["fehler"], r"HTTP Error 429.*\[Retry-After 300, Anfrage 2\]")

    def _abgleich(self, modelle):
        erg = {"zeit": "2026-11-16T07:30:00+01:00", "modelle": modelle}
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp, "db")
            (db / "preise").mkdir(parents=True)
            (db / "wecker").mkdir()
            for m in self.pw.MODELLE:
                (db / "preise" / f"{m}.json").write_text(json.dumps({"version": 1}), encoding="utf-8")
            (db / "wecker" / "lauf.json").write_text(json.dumps({"version": 1}), encoding="utf-8")
            return self.pw.abgleich(erg, str(db), str(Path(tmp, "aus")))

    def test_status_teilweise_bis_alles_da_dann_ok(self):
        ids = list(self.pw.MODELLE)
        erster = {m: dict(self.ERG) for m in ids[:16]} | {m: {"verschoben": True} for m in ids[16:]}
        r = self._abgleich(erster)
        self.assertEqual(r["status"], "teilweise")
        self.assertIn("Folgt im nächsten Lauf", r["lauf"])
        self.assertNotIn("Abruf fehlgeschlagen", r["lauf"])
        self.assertNotIn("Kein Angebot", r["lauf"])
        nachlauf = {m: {"heute_schon": True} for m in ids[:16]} | {m: dict(self.ERG) for m in ids[16:]}
        r = self._abgleich(nachlauf)
        self.assertEqual(r["status"], "ok", r["lauf"])
        self.assertEqual(r["writes"], len(ids) - 16 + 1, "nur nachgeholte Preise und wecker/lauf")

    def test_abrufreihe_aelteste_zuerst_nur_ohne_heutigen_preis(self):
        ids = list(self.pw.MODELLE)
        def doc(z):
            return {"aktuell": {"gesamt": 100.0, "zeit": z}}
        alt = {"preise": {ids[0]: doc("2026-11-16T06:30:00+01:00"), ids[1]: doc("2026-11-15T06:30:00+01:00"),
                          ids[2]: doc("2026-11-14T06:30:00+01:00"), ids[3]: {"aktuell": {"gesamt": None, "zeit": "2026-11-16T06:30:00+01:00"}}}}
        reihe = self.pa.abrufreihe(alt, ids, "2026-11-16")
        self.assertNotIn(ids[0], reihe, "heute schon gelesen")
        self.assertEqual(reihe[:len(ids) - 3], [m for m in ids if m not in ids[:3]], "ohne Preis zuerst, MODELLE-Reihenfolge")
        self.assertEqual(reihe[-2:], [ids[2], ids[1]], "dann älteste zuerst")
        self.assertEqual(self.pa.abrufreihe({"preise": {m: doc("2026-11-16T06:30:00+01:00") for m in ids}}, ids, "2026-11-16"), [])
        self.assertEqual(self.pa.abrufreihe({}, ids, "2026-11-16"), ids)

    def test_heute_schon_ohne_heutigen_preis_ist_fehler(self):
        """Schutz: „heute schon gelesen“ zählt nur, wenn preise.json wirklich einen Preis von heute hat."""
        ids = list(self.pw.MODELLE)
        with tempfile.TemporaryDirectory() as tmp:
            ziel = Path(tmp, "preise.json")
            ziel.write_text(json.dumps({"preise": {ids[0]: {"name": "x", "aktuell": dict(self.ERG["sicher"], zeit="2026-11-15T06:30:00+01:00")}}}), encoding="utf-8")
            erg = {"zeit": "2026-11-16T07:30:00+01:00", "modelle": {m: {"heute_schon": True} for m in ids}}
            bericht, lauf = self.pa.aktualisiere(self.pw, erg, ziel)
        self.assertEqual(bericht["status"], "fehler")
        self.assertIn("Abruf fehlgeschlagen", lauf["meldung"])

    def test_nachlauf_ohne_offene_modelle_ruft_nichts_ab(self):
        ids = list(self.pw.MODELLE)
        heute = __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")
        with tempfile.TemporaryDirectory() as tmp:
            ziel = Path(tmp, "preise.json")
            inhalt = json.dumps({"preise": {m: {"aktuell": {"gesamt": 100.0, "zeit": heute}} for m in ids}})
            ziel.write_text(inhalt, encoding="utf-8")
            meld = Path(tmp, "m.txt")
            r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(WURZEL / "werkzeuge" / "preise_aktualisieren.py"),
                                "--ziel", str(ziel), "--meldung", str(meld)], capture_output=True, text=True, encoding="utf-8", timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('"abgerufen": 0', r.stdout)
            self.assertEqual(ziel.read_text(encoding="utf-8"), inhalt, "preise.json unverändert")
            self.assertEqual(meld.read_text(encoding="utf-8"), "")

    def test_workflow_hat_nachlaeufe(self):
        t = (WURZEL / ".github" / "workflows" / "preise.yml").read_text(encoding="utf-8")
        self.assertGreaterEqual(len(re.findall(r'(?m)^    - cron: "\d+ \d+ \* \* \*"', t)), 3)


if __name__ == "__main__":
    unittest.main()
