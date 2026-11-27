# -*- coding: utf-8 -*-
"""Freigabeschranke der Gewichtsfassung (P2a-2, Entwurf §9.3, Test 47): lokale Prüfung und Schritt des Datenworkflows,
jeweils gegen ein lokales Bare-Repository als origin. Der App-Publish (veroeffentlichen.py) steht in test_app.py."""
import contextlib
import copy
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "werkzeuge"))
import datenbank  # noqa: E402
import freigabe  # noqa: E402

SCHEMA_PFAD = "daten/schema/kategorien.json"


def schema(nummer=1, gewicht=None, stand="2026-11-01", mit_fassung=True):
    """Echtes Schema; gewicht ändert bildtechnik (Fernseher), ohne Fassung = Schema 1."""
    s = json.loads(datenbank.SCHEMA.read_text(encoding="utf-8"))
    for k in s["kategorien"]:
        if mit_fassung:
            k["gewichte_version"] = {"nummer": nummer if k["id"] == "fernseher" else 1, "stand": stand}
        else:
            k.pop("gewichte_version", None)
    if not mit_fassung:
        s["schema_version"] = 1
    if gewicht is not None:
        next(f for f in s["kategorien"][0]["felder"] if f["id"] == "bildtechnik")["gewicht"] = gewicht
    return s


class Repos:
    """quelle (Arbeitsklon mit main), seite (baut gh-pages-Commits), ursprung (bare, origin)."""

    def __init__(self, testfall):
        sauber = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
        umgebung = mock.patch.dict(os.environ, sauber, clear=True)
        umgebung.start(); testfall.addCleanup(umgebung.stop)
        self.t = Path(tempfile.mkdtemp(prefix="kb-freigabe-")); testfall.addCleanup(shutil.rmtree, self.t, True)
        self.ursprung, self.quelle, self.seite = self.t / "ursprung.git", self.t / "quelle", self.t / "seite"
        self.g(self.t, "init", "-q", "--bare", str(self.ursprung))
        for r in (self.quelle, self.seite):
            self.g(self.t, "init", "-q", "-b", "main", str(r))
            self.g(r, "config", "user.name", "Test"); self.g(r, "config", "user.email", "test@example.invalid")
            self.g(r, "config", "core.autocrlf", "false")
            self.g(r, "remote", "add", "origin", str(self.ursprung))

    @staticmethod
    def g(cwd, *a, check=True):
        r = subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, encoding="utf-8")
        if check and r.returncode != 0:
            raise AssertionError(f"git {' '.join(a)}: {r.stderr}")
        return r.stdout.strip()

    def quelle_commit(self, inhalt, nachricht="stand"):
        """Commit auf main mit diesem Schema (dict, Text oder None = Datei fehlt), nach origin gepusht."""
        p = self.quelle / SCHEMA_PFAD
        p.parent.mkdir(parents=True, exist_ok=True)
        if inhalt is None:
            if p.exists():
                p.unlink()
            (self.quelle / "leer.txt").write_text(nachricht, encoding="utf-8")
        else:
            p.write_text(inhalt if isinstance(inhalt, str) else json.dumps(inhalt, ensure_ascii=False), encoding="utf-8")
        self.g(self.quelle, "add", "-A"); self.g(self.quelle, "commit", "-q", "--allow-empty", "-m", nachricht)
        self.g(self.quelle, "push", "-q", "origin", "HEAD:refs/heads/main")
        return self.g(self.quelle, "rev-parse", "HEAD")

    def seite_commit(self, daten, preise='{"p": 1}', erzwingen=False):
        """gh-pages-Commit mit finder-daten.json (Text oder None = fehlt), nach origin gepusht."""
        for name, inhalt in (("finder-daten.json", daten), ("preise.json", preise), ("index.html", "<p>seite</p>")):
            p = self.seite / name
            if inhalt is None:
                if p.exists():
                    p.unlink()
            else:
                p.write_text(inhalt, encoding="utf-8")
        self.g(self.seite, "add", "-A"); self.g(self.seite, "commit", "-q", "--allow-empty", "-m", "seite")
        sha = self.g(self.seite, "rev-parse", "HEAD")
        self.g(self.seite, "push", "-q", *(["--force"] if erzwingen else []), "origin", f"{sha}:refs/heads/gh-pages")
        return sha

    def setze_gh_pages(self, sha):
        self.g(self.seite, "push", "-q", "--force", "origin", f"{sha}:refs/heads/gh-pages")

    def loesche_gh_pages(self):
        self.g(self.seite, "push", "-q", "origin", ":refs/heads/gh-pages")

    def oben(self):
        r = subprocess.run(["git", "-C", str(self.ursprung), "rev-parse", "--verify", "-q", "refs/heads/gh-pages"],
                           capture_output=True, text=True)
        return r.stdout.strip() or None

    def zeige(self, rev, pfad):
        return self.g(self.ursprung, "show", f"{rev}:{pfad}")

    def bau(self, herkunft):
        datei = self.t / "finder-daten.json"
        datei.write_text(json.dumps({"herkunft": herkunft, "kategorien": []}) + "\n", encoding="utf-8")
        return datei


def herkunft(h):
    return json.dumps({"herkunft": h, "kategorien": []})


def ausgabe(f, *a, **kw):
    puffer = io.StringIO()
    with contextlib.redirect_stdout(puffer):
        ergebnis = f(*a, **kw)
    return ergebnis, puffer.getvalue()


def negative_faelle(r):
    """Test 47(c): {Art: (gh-pages-Commit, erwartete SHA in der Meldung)}; jeder Fall ein eigener Seitenstand."""
    h_ohne = r.quelle_commit(None, "ohne schema")
    h_kaputt = r.quelle_commit("kaputt{", "schema kaputt")
    faelle = {}
    faelle["Online-Datei fehlt"] = r.seite_commit(None, erzwingen=True)
    faelle["Datei unlesbar"] = r.seite_commit("kein json", erzwingen=True)
    faelle["herkunft fehlt"] = r.seite_commit(json.dumps({"kategorien": []}), erzwingen=True)
    faelle["herkunft nicht auflösbar"] = r.seite_commit(herkunft("c" * 40), erzwingen=True)
    faelle["Schema am Herkunftscommit fehlt"] = r.seite_commit(herkunft(h_ohne), erzwingen=True)
    faelle["Schema am Herkunftscommit unlesbar"] = r.seite_commit(herkunft(h_kaputt), erzwingen=True)
    erwartet = {"herkunft nicht auflösbar": "c" * 12, "Schema am Herkunftscommit fehlt": h_ohne[:12],
                "Schema am Herkunftscommit unlesbar": h_kaputt[:12]}
    return {art: (sha, erwartet.get(art, sha[:12])) for art, sha in faelle.items()}


class Lokal(unittest.TestCase):
    """47(a), (c) lokal, (h): `datenbank.py pruefen --gegen` ohne Wert liest die Herkunft der Online-Datei."""

    def test_kandidat_auf_origin_main_gegen_aeltere_herkunft(self):   # 47(a)
        r = Repos(self)
        h0 = r.quelle_commit(schema(), "referenz")
        r.seite_commit(herkunft(h0))
        h1 = r.quelle_commit(schema(gewicht=31), "kandidat auf origin/main, gleiche Nummer")
        self.assertEqual(r.g(r.ursprung, "rev-parse", "main"), h1, "Vorbedingung: Kandidat liegt auf origin/main")
        fehler = freigabe.lokal_fehler(r.quelle, schema(gewicht=31))
        self.assertTrue(fehler)
        self.assertTrue(any(h0[:12] in f for f in fehler), fehler)
        self.assertEqual(freigabe.lokal_fehler(r.quelle, schema()), [], "unveränderter Kandidat")
        self.assertEqual(freigabe.lokal_fehler(r.quelle, schema(nummer=2, gewicht=31, stand="2026-11-25")), [])

    def test_negative_referenzen(self):                               # 47(c) lokal
        r = Repos(self)
        for art, (sha, erwartet) in negative_faelle(r).items():
            with self.subTest(art=art):
                r.setze_gh_pages(sha)
                fehler = freigabe.lokal_fehler(r.quelle, schema())
                self.assertTrue(fehler, art)
                self.assertTrue(any(erwartet in f for f in fehler), (art, fehler))

    def test_alter_ref_bei_fehlendem_zweig_wird_nie_gelesen(self):    # 47(h)
        r = Repos(self)
        h0 = r.quelle_commit(schema(), "referenz")
        r.seite_commit(herkunft(h0))
        r.g(r.quelle, "fetch", "-q", "origin", "+refs/heads/gh-pages:refs/remotes/origin/gh-pages")
        self.assertEqual(freigabe.lokal_fehler(r.quelle, schema()), [])
        r.loesche_gh_pages()
        self.assertTrue(r.g(r.quelle, "rev-parse", "--verify", "-q", "refs/remotes/origin/gh-pages"), "alter Ref steht noch")
        fehler = freigabe.lokal_fehler(r.quelle, schema())
        self.assertTrue(fehler and any("gh-pages" in f for f in fehler), fehler)

    def test_cli_gegen_commit(self):
        """`pruefen --gegen <commit>` im echten Repository: HEAD gegen sich selbst ist grün, ein fremder SHA rot."""
        kopf = subprocess.run(["git", "-C", str(WURZEL), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        lauf = lambda *a: subprocess.run([sys.executable, "-I", str(WURZEL / "werkzeuge" / "datenbank.py"), "pruefen", *a],
                                         capture_output=True, text=True, encoding="utf-8")
        gut = lauf("--gegen", kopf)
        self.assertEqual(gut.returncode, 0, gut.stdout[-800:])
        self.assertIn(kopf[:12], gut.stdout)
        schlecht = lauf("--gegen", "c" * 40)
        self.assertEqual(schlecht.returncode, 1)
        self.assertIn("c" * 12, schlecht.stdout)


class DatenPush(unittest.TestCase):
    """Schrittfunktion des Datenworkflows (finder-daten.yml): 47(c) Workflow, (d)–(g)."""

    def setUp(self):
        self.r = Repos(self)

    def push(self, neu, haken=None):
        return ausgabe(freigabe.daten_push, self.r.quelle, self.r.bau(neu), neu, haken=haken)

    def test_normaler_lauf_ersetzt_nur_finder_daten(self):
        r = self.r
        h0 = r.quelle_commit(schema(), "referenz")
        e0 = r.seite_commit(herkunft(h0))
        h1 = r.quelle_commit(schema(), "neuer stand")
        code, text = self.push(h1)
        self.assertEqual(code, 0, text)
        oben = r.oben()
        self.assertNotEqual(oben, e0)
        self.assertEqual(r.g(r.ursprung, "rev-parse", f"{oben}^@"), e0, "einziger Elternteil ist der geprüfte Stand")
        self.assertEqual(r.g(r.ursprung, "diff-tree", "--no-renames", "--name-only", "-r", e0, oben), "finder-daten.json")
        self.assertEqual(json.loads(r.zeige(oben, "finder-daten.json"))["herkunft"], h1)
        code, text = self.push(h1)
        self.assertEqual((code, r.oben()), (0, oben), "zweiter Lauf: unverändert, kein Commit")

    def test_geaenderte_gewichte_ohne_neue_nummer(self):
        r = self.r
        h0 = r.quelle_commit(schema(), "referenz")
        e0 = r.seite_commit(herkunft(h0))
        h1 = r.quelle_commit(schema(gewicht=31), "kandidat")
        code, text = self.push(h1)
        self.assertEqual((code, r.oben()), (1, e0), text)
        self.assertIn(h0[:12], text)

    def test_datei_an_kandidat_gebunden(self):                        # P2A2-BAU-04
        """Die veröffentlichten Bytes müssen strenges JSON mit herkunft = geprüfter Kandidat sein, sonst kein Commit."""
        r = self.r
        h0 = r.quelle_commit(schema(), "referenz")
        e0 = r.seite_commit(herkunft(h0))
        h1 = r.quelle_commit(schema(), "kandidat")
        datei = r.t / "finder-daten.json"
        for art, inhalt in {"andere herkunft": herkunft(h0), "fremde herkunft": herkunft("d" * 40),
                            "ohne herkunft": json.dumps({"kategorien": []}),
                            "Infinity": '{"herkunft": "%s", "kategorien": [], "x": Infinity}' % h1,
                            "1e999": '{"herkunft": "%s", "kategorien": [], "x": 1e999}' % h1,
                            "keine Objektform": "[]"}.items():
            with self.subTest(art=art):
                datei.write_text(inhalt + "\n", encoding="utf-8")
                code, text = ausgabe(freigabe.daten_push, r.quelle, datei, h1)
                self.assertEqual((code, r.oben()), (1, e0), text)
                self.assertIn("nichts veröffentlicht", text)
        code, text = self.push(h1)                                     # Gegenprobe: passende Datei
        self.assertEqual(code, 0, text)
        self.assertNotEqual(r.oben(), e0)

    def test_herkunft_nicht_enthalten(self):
        """herkunft.py läuft wie bisher zusätzlich: eine Online-Herkunft, die nicht im neuen Stand liegt, bricht ab."""
        r = self.r
        h0 = r.quelle_commit(schema(), "referenz")
        # gleicher Baum, aber eigener Wurzelcommit: kein Vorfahr von h0, Fassungsvergleich gleich
        fremd = r.g(r.quelle, "commit-tree", r.g(r.quelle, "rev-parse", f"{h0}^{{tree}}"), "-m", "fremd")
        e0 = r.seite_commit(herkunft(fremd))
        code, text = self.push(h0)
        self.assertEqual((code, r.oben()), (1, e0), text)

    def test_negative_referenzen(self):                               # 47(c) Workflow
        r = self.r
        faelle = negative_faelle(r)
        neu = r.quelle_commit(schema(), "kandidat")
        for art, (sha, erwartet) in faelle.items():
            with self.subTest(art=art):
                r.setze_gh_pages(sha)
                code, text = self.push(neu)
                self.assertEqual(code, 1, (art, text))
                self.assertEqual(r.oben(), sha, "kein Commit, kein Push")
                self.assertIn(erwartet, text, art)

    def test_fremder_push_mit_neuer_herkunft(self):                   # 47(d)
        r = self.r
        h1 = r.quelle_commit(schema(), "referenz")
        r.seite_commit(herkunft(h1))
        h2 = r.quelle_commit(schema(nummer=2, gewicht=31, stand="2026-11-25"), "fassung 2")
        neu = r.quelle_commit(schema(), "kandidat mit Fassung 1")
        zustand = {}

        def haken(versuch, eltern):
            if versuch == 1:
                zustand["e2"] = r.seite_commit(herkunft(h2))
        code, text = self.push(neu, haken)
        self.assertEqual(code, 1, text)
        self.assertEqual(r.oben(), zustand["e2"], "nichts gepusht")
        self.assertIn(h2[:12], text, "zweiter Versuch prüft gegen die neue Herkunft")

    def test_zweig_geloescht(self):                                   # 47(e)
        r = self.r
        h0 = r.quelle_commit(schema(), "referenz")
        r.seite_commit(herkunft(h0))
        neu = r.quelle_commit(schema(), "kandidat")
        code, text = self.push(neu, lambda versuch, eltern: r.loesche_gh_pages() if versuch == 1 else None)
        self.assertEqual(code, 1, text)
        self.assertIsNone(r.oben(), "kein Zweig angelegt")

    def test_auf_vorfahr_zurueckgesetzt(self):                        # 47(f)
        r = self.r
        h0 = r.quelle_commit(schema(mit_fassung=False), "referenz schema 1")
        e0 = r.seite_commit(herkunft(h0))
        h1 = r.quelle_commit(schema(), "fassung 1")
        r.seite_commit(herkunft(h1))
        neu = r.quelle_commit(schema(), "kandidat")
        code, text = self.push(neu, lambda versuch, eltern: r.setze_gh_pages(e0) if versuch == 1 else None)
        self.assertEqual(code, 0, text)
        self.assertEqual(r.g(r.ursprung, "rev-parse", f"{r.oben()}^@"), e0, "auf den Vorfahren gesetzt")
        self.assertIn(h0[:12], text, "zweiter Versuch prüft gegen die Herkunft des Vorfahren")

    def test_preis_push_dazwischen(self):                             # 47(g)
        r = self.r
        h0 = r.quelle_commit(schema(), "referenz")
        r.seite_commit(herkunft(h0))
        neu = r.quelle_commit(schema(), "kandidat")
        zustand = {}

        def haken(versuch, eltern):
            if versuch == 1:
                zustand["preis"] = r.seite_commit(herkunft(h0), preise='{"p": 2}')
        code, text = self.push(neu, haken)
        self.assertEqual(code, 0, text)
        self.assertEqual(r.g(r.ursprung, "rev-parse", f"{r.oben()}^@"), zustand["preis"])
        self.assertEqual(json.loads(r.zeige(r.oben(), "preise.json")), {"p": 2}, "Preise bleiben")

    def test_cli(self):
        r = self.r
        h0 = r.quelle_commit(schema(), "referenz")
        r.seite_commit(herkunft(h0))
        neu = r.quelle_commit(schema(), "kandidat")
        lauf = subprocess.run([sys.executable, "-I", str(WURZEL / "werkzeuge" / "freigabe.py"), "daten-push",
                               str(r.bau(neu)), neu], cwd=r.quelle, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(lauf.returncode, 0, lauf.stdout + lauf.stderr)
        self.assertEqual(json.loads(r.zeige(r.oben(), "finder-daten.json"))["herkunft"], neu)


class WorkflowText(unittest.TestCase):
    """finder-daten.yml ruft für den Veröffentlichungsschritt nur die getestete Schrittfunktion auf."""

    def test_schritt(self):
        wf = (WURZEL / ".github" / "workflows" / "finder-daten.yml").read_text(encoding="utf-8")
        self.assertIn("fetch-depth: 0", wf)
        self.assertIn('--herkunft "$GITHUB_SHA"', wf)
        schritt = wf.split("Auf gh-pages veröffentlichen", 1)[1].split("- name:", 1)[0]
        self.assertIn('werkzeuge/freigabe.py daten-push "$RUNNER_TEMP/finder-daten.json" "$GITHUB_SHA"', schritt)
        for verboten in ("cp ", "git push", "git commit", "git worktree"):
            self.assertNotIn(verboten, schritt, verboten)


if __name__ == "__main__":
    unittest.main()
