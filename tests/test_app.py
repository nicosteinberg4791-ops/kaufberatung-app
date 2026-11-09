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


if __name__ == "__main__":
    unittest.main()
