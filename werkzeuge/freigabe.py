# -*- coding: utf-8 -*-
"""Freigabeschranke der Gewichtsfassung (P2a-2, Entwurf docs/recherche-ux/p2-entwurf.md §9.3).

Referenz ist immer die `herkunft` der finder-daten.json, die ersetzt werden soll, gelesen aus genau einem gh-pages-Commit
(`eltern`). Gegen das Schema an diesem Herkunftscommit vergleicht datenbank.fassung_gegen_fehler die Projektion des
Kandidaten. Streng: fehlt die Online-Datei, ist sie unlesbar, fehlt ihre herkunft, ist der Commit nicht auflösbar oder
fehlt bzw. ist dort daten/schema/kategorien.json unlesbar, bricht der Lauf mit SHA ab (anders als herkunft.py, das
weiter zusätzlich läuft).

Wege:
  - lokal:          python -I werkzeuge/datenbank.py pruefen --gegen      (lokal_fehler: git ls-remote, dann genau diesen
                    SHA holen; ein vorhandener Ref origin/gh-pages wird nie gelesen)
  - App-Publish:    werkzeuge/veroeffentlichen.py ruft seiten_fehler vor dem Bau
  - Datenworkflow:  python -I werkzeuge/freigabe.py daten-push <finder-daten.json> <commit>
                    (.github/workflows/finder-daten.yml): je Versuch Eltern-SHA holen, prüfen, Commit nur aus `eltern`
                    mit ersetzter finder-daten.json, Push mit Lease auf `eltern`; höchstens drei Versuche.
Exit 0 = veröffentlicht oder unverändert, 1 = Abbruch, 2 = Aufruf falsch. Nur Standardbibliothek und git.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import datenbank  # noqa: E402
import herkunft  # noqa: E402

SHA = re.compile(r"[0-9a-f]{40}")
SCHEMA_PFAD = "daten/schema/kategorien.json"
ZWEIG = "refs/heads/gh-pages"


class ReferenzFehler(Exception):
    """Referenz nicht eindeutig lesbar: Abbruch, nichts kopiert, kein Commit, kein Push."""


def _git(ordner, *a, eingabe=None, env=None):
    """Git ohne Ersetzungsreferenzen und Grafts (wie veroeffentlichen.py, R7-01); Ausgabe als Bytes."""
    return subprocess.run(["git", "-C", str(ordner), *a], input=eingabe, capture_output=True,
                          env={**os.environ, **herkunft.OHNE_ERSATZ, **(env or {})})


def _text(r):
    return r.stdout.decode("utf-8", "replace").strip()


def ist_commit(ordner, sha):
    r = _git(ordner, "cat-file", "-t", sha)
    return r.returncode == 0 and _text(r) == "commit"


def online_eltern(ordner, remote="origin"):
    """SHA von gh-pages auf remote (ls-remote), danach genau dieser Commit geholt. Nie ein vorhandener Ref (P2A2-03)."""
    r = _git(ordner, "ls-remote", "--exit-code", remote, ZWEIG)
    zeilen = _text(r).split()
    if r.returncode != 0 or not zeilen or not SHA.fullmatch(zeilen[0]):
        raise ReferenzFehler(f"gh-pages auf {remote} nicht abrufbar (Zweig fehlt oder Abruf gescheitert)")
    sha = zeilen[0]
    if _git(ordner, "fetch", "-q", "--no-tags", remote, sha).returncode != 0 or not ist_commit(ordner, sha):
        raise ReferenzFehler(f"gh-pages {sha} nicht holbar")
    return sha


def schema_am_commit(sha, ordner, remote=None):
    """Schema (dict) aus <sha>:daten/schema/kategorien.json, mit denselben Leseregeln wie der Bau. remote: einmal
    nachholen, wenn der Commit lokal fehlt (nur lokaler Weg)."""
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise ReferenzFehler(f"Herkunft {sha!r} ist kein Commit (40 Hex-Zeichen)")
    if not ist_commit(ordner, sha) and remote:
        _git(ordner, "fetch", "-q", "--no-tags", remote, sha)
    if not ist_commit(ordner, sha):
        raise ReferenzFehler(f"Herkunft {sha} ist kein vorhandener Commit")
    r = _git(ordner, "show", f"{sha}:{SCHEMA_PFAD}")
    if r.returncode != 0:
        raise ReferenzFehler(f"{SCHEMA_PFAD} fehlt am Herkunftscommit {sha}")
    try:
        s = datenbank.schema_laden(r.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise ReferenzFehler(f"{SCHEMA_PFAD} am Herkunftscommit {sha} unlesbar ({e})")
    if not isinstance(s, dict):
        raise ReferenzFehler(f"{SCHEMA_PFAD} am Herkunftscommit {sha} ist kein Objekt")
    return s


def referenz(eltern, ordner, remote=None):
    """(herkunft, schema, online_text) aus <eltern>:finder-daten.json, streng (§9.3 „Strikt“)."""
    r = _git(ordner, "show", f"{eltern}:finder-daten.json")
    if r.returncode != 0:
        raise ReferenzFehler(f"finder-daten.json fehlt auf gh-pages {eltern}")
    try:
        text = r.stdout.decode("utf-8")
        d = datenbank.json_streng(text)
    except (UnicodeDecodeError, ValueError):
        raise ReferenzFehler(f"finder-daten.json auf gh-pages {eltern} unlesbar")
    h = d.get("herkunft") if isinstance(d, dict) else None
    if not isinstance(h, str) or not SHA.fullmatch(h):
        raise ReferenzFehler(f"finder-daten.json auf gh-pages {eltern} ohne gültige herkunft")
    return h, schema_am_commit(h, ordner, remote), text


def _vergleich(kandidat, h, ref):
    print(f"Freigabeschranke: Referenz ist das Schema am Herkunftscommit {h[:12]}")
    return [f"Freigabeschranke (Referenz {h[:12]}): {x}" for x in datenbank.fassung_gegen_fehler(kandidat, ref)]


def gegen_commit_fehler(kandidat, sha, ordner):
    """`pruefen --gegen <commit>`: Referenz ist das Schema an diesem Commit."""
    try:
        return _vergleich(kandidat, sha, schema_am_commit(sha, ordner))
    except ReferenzFehler as e:
        return [f"Freigabeschranke: {e}"]


def seiten_fehler(kandidat, eltern, ordner, remote=None):
    """(Fehlerliste, Online-Text) für den gh-pages-Commit eltern; ReferenzFehler wird zur Fehlerzeile."""
    try:
        h, ref, text = referenz(eltern, ordner, remote)
    except ReferenzFehler as e:
        return [f"Freigabeschranke: {e}"], None
    return _vergleich(kandidat, h, ref), text


def lokal_fehler(ordner, kandidat, remote="origin"):
    """`pruefen --gegen` ohne Wert: Referenz ist die Herkunft der Online-Datei auf gh-pages, nicht origin/main."""
    try:
        eltern = online_eltern(ordner, remote)
    except ReferenzFehler as e:
        return [f"Freigabeschranke: {e}"]
    return seiten_fehler(kandidat, eltern, ordner, remote)[0]


def _seitencommit(ordner, eltern, inhalt, nachricht):
    """Commit aus dem Baum von eltern, darin allein finder-daten.json ersetzt (eigener Index); None = unverändert."""
    with tempfile.TemporaryDirectory(prefix="kb-daten-index-") as t:
        env = {"GIT_INDEX_FILE": str(Path(t) / "index")}
        if _git(ordner, "read-tree", eltern, env=env).returncode != 0:
            raise ReferenzFehler(f"Baum von gh-pages {eltern} nicht lesbar")
        r = _git(ordner, "hash-object", "-w", "--stdin", eingabe=inhalt)
        blob = _text(r)
        if r.returncode != 0 or not SHA.fullmatch(blob):
            raise ReferenzFehler("finder-daten.json nicht als Objekt speicherbar")
        if _git(ordner, "update-index", "--add", "--cacheinfo", f"100644,{blob},finder-daten.json", env=env).returncode:
            raise ReferenzFehler("Index nicht aktualisierbar")
        r = _git(ordner, "write-tree", env=env)
        baum = _text(r)
    if r.returncode != 0 or baum == _text(_git(ordner, "rev-parse", f"{eltern}^{{tree}}")):
        return None
    r = _git(ordner, "commit-tree", baum, "-p", eltern, "-m", nachricht)
    neu = _text(r)
    if r.returncode != 0 or not SHA.fullmatch(neu):
        raise ReferenzFehler("Seitencommit nicht erzeugbar: " + r.stderr.decode("utf-8", "replace").strip())
    geaendert = _text(_git(ordner, "diff-tree", "--no-renames", "--name-only", "-r", eltern, neu)).split()
    if geaendert != ["finder-daten.json"]:
        raise ReferenzFehler(f"Seitencommit ändert {geaendert}, erlaubt ist nur finder-daten.json")
    return neu


def daten_push(ordner, datei, neu, kandidat=None, remote="origin", versuche=3, haken=None):
    """Veröffentlichungsschritt des Datenworkflows. haken(versuch, eltern) läuft direkt vor dem Push (nur Tests)."""
    def abbruch(grund):
        print("Abbruch, nichts veröffentlicht:", grund)
        return 1
    inhalt = Path(datei).read_bytes()
    # P2A2-BAU-04: genau diese Bytes werden veröffentlicht, also an den geprüften Kandidaten binden (strenges JSON,
    # herkunft = neu), bevor ein Schema geprüft oder ein Commit erzeugt wird.
    try:
        gebaut = datenbank.json_streng(inhalt.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        return abbruch(f"{Path(datei).name} ist kein strenges JSON ({e})")
    if not isinstance(gebaut, dict) or gebaut.get("herkunft") != neu:
        h = gebaut.get("herkunft") if isinstance(gebaut, dict) else None
        return abbruch(f"{Path(datei).name} trägt herkunft {h!r}, geprüft wird {neu}")
    try:
        kandidat = schema_am_commit(neu, ordner) if kandidat is None else kandidat
    except ReferenzFehler as e:
        return abbruch(f"Kandidat: {e}")
    for versuch in range(1, versuche + 1):
        try:
            eltern = online_eltern(ordner, remote)   # je Versuch neu: nach einem fremden Push gilt dessen Herkunft
        except ReferenzFehler as e:
            return abbruch(e)
        fehler, online = seiten_fehler(kandidat, eltern, ordner)
        if fehler:
            return abbruch(f"gh-pages {eltern[:12]}\n  - " + "\n  - ".join(fehler[:20]))
        grund = herkunft.fehler(online, neu, herkunft.git_vorfahr(ordner))   # wie bisher zusätzlich (R2-07)
        if grund:
            return abbruch(f"finder-daten.json auf gh-pages {eltern[:12]} – {grund}")
        try:
            commit = _seitencommit(ordner, eltern, inhalt, f"Finder-Daten {neu[:7]}")
        except ReferenzFehler as e:
            return abbruch(e)
        if commit is None:
            print(f"finder-daten.json unverändert (gh-pages {eltern[:12]})")
            return 0
        if haken:
            haken(versuch, eltern)
        r = _git(ordner, "push", "-q", "--no-follow-tags", f"--force-with-lease={ZWEIG}:{eltern}", remote,
                 f"{commit}:{ZWEIG}")
        if r.returncode == 0:
            print(f"gepusht: gh-pages/finder-daten.json ({commit[:12]} auf {eltern[:12]})")
            return 0
        print(f"Versuch {versuch}: Push abgelehnt (gh-pages ist nicht mehr {eltern[:12]}), neu prüfen")
    return abbruch(f"Push auf gh-pages {versuche}-mal gescheitert")


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) != 3 or a[0] != "daten-push" or not SHA.fullmatch(a[2].strip().lower()):
        print(__doc__)
        return 2
    return daten_push(Path.cwd(), a[1], a[2].strip().lower())


if __name__ == "__main__":
    sys.exit(main())
