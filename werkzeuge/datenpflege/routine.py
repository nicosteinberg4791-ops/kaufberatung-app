# -*- coding: utf-8 -*-
"""Rahmen der wöchentlichen Datenpflege-Routine (D11): eigener Arbeitsbaum, Schutz gegen Löschen, Schranke, Push.

Aufruf (aus einem beliebigen Klon des Repos):
  python -I -X utf8 werkzeuge/datenpflege/routine.py vorbereiten      → Arbeitsbaum .claude/worktrees/datenpflege-routine
                                                                        frisch auf origin/main (bricht ab, wenn er Reste hat)
  python -I -X utf8 werkzeuge/datenpflege/routine.py pruefen [--pushen] (im Arbeitsbaum, nach dem Commit der Routine)

`pruefen` verlangt, in dieser Reihenfolge:
  1. sauberer Arbeitsbaum, HEAD baut auf origin/main auf (frisch geholt);
  2. geändert sind nur daten/produkte/<kategorie>.json (kein Code, kein Schema, kein FORMAT.md);
  3. keine Modell- oder Varianten-ID und keine Datei aus origin/main fehlt (nie automatisch löschen, D11);
  4. python -I werkzeuge/datenbank.py pruefen → 0 Fehler;
  5. tests/alle-tests.ps1 → 0 Fehler.
Nur wenn alles grün ist und --pushen gesetzt ist: git push origin HEAD:main (kein Erzwingen). finder-daten.yml bringt
finder-daten.json danach live. Exit 0 = grün (und ggf. gepusht), 1 = Schranke rot, 2 = Aufruf/Umgebung.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ERLAUBT = re.compile(r"^daten/produkte/[a-z0-9_]+\.json$")
ZWEIG = "datenpflege-routine"


def git(*args, cwd=None, pruefen=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if pruefen and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r


def ids_aus(text):
    """Modell- und Varianten-IDs einer Produktdatei (unlesbare Datei → leere Menge, die Schranke meldet sie ohnehin)."""
    try:
        d = json.loads(text)
    except ValueError:
        return set()
    out = set()
    for m in d.get("modelle", []) if isinstance(d, dict) else []:
        if isinstance(m, dict) and m.get("id"):
            out.add("modell:" + str(m["id"]))
            for v in m.get("varianten", []) or []:
                if isinstance(v, dict) and v.get("id"):
                    out.add("variante:" + str(v["id"]))
    return out


def geloescht(alt, neu):
    """alt/neu: {pfad: text}. Liste der Verluste (fehlende Dateien und IDs) – leer heißt: nichts gelöscht."""
    verluste = []
    for pfad, text in sorted(alt.items()):
        if pfad not in neu:
            verluste.append(f"Datei fehlt: {pfad}")
            continue
        for i in sorted(ids_aus(text) - ids_aus(neu[pfad])):
            verluste.append(f"{pfad}: {i} fehlt")
    return verluste


def fremde_pfade(pfade):
    return [p for p in pfade if not ERLAUBT.match(p)]


def produktdateien(ref, cwd):
    namen = git("ls-tree", "--name-only", ref, "daten/produkte/", cwd=cwd).stdout.split()
    return {n: git("show", f"{ref}:{n}", cwd=cwd).stdout for n in namen if n.endswith(".json")}


def vorbereiten():
    gemeinsam = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    haupt = gemeinsam.parent
    baum = haupt / ".claude" / "worktrees" / ZWEIG
    git("fetch", "-q", "origin", "main", cwd=haupt)
    if baum.exists():
        rest = git("status", "--porcelain", cwd=baum).stdout.strip()
        if rest:
            print(f"Abbruch: {baum} hat ungesicherte Änderungen aus einem früheren Lauf (nicht verwerfen, Besitzer fragen):")
            print(rest)
            return 1
        git("checkout", "-q", "-B", ZWEIG, "origin/main", cwd=baum)
    else:
        git("worktree", "add", "-q", "-B", ZWEIG, str(baum), "origin/main", cwd=haupt)
    print(f"Arbeitsbaum bereit: {baum} (Zweig {ZWEIG} = origin/main {git('rev-parse', '--short', 'HEAD', cwd=baum).stdout.strip()})")
    return 0


def pruefen(pushen):
    wurzel = Path(git("rev-parse", "--show-toplevel").stdout.strip())
    rot = []
    git("fetch", "-q", "origin", "main", cwd=wurzel)
    if git("status", "--porcelain", cwd=wurzel).stdout.strip():
        rot.append("Arbeitsbaum nicht sauber (erst committen)")
    if git("merge-base", "--is-ancestor", "origin/main", "HEAD", cwd=wurzel, pruefen=False).returncode != 0:
        rot.append("HEAD baut nicht auf origin/main auf (vorbereiten neu ausführen)")
    geaendert = git("diff", "--name-only", "origin/main", "HEAD", cwd=wurzel).stdout.split()
    if not geaendert:
        print("Keine Änderung gegenüber origin/main – nichts zu prüfen oder zu pushen.")
        return 0
    rot += [f"nicht erlaubte Änderung: {p}" for p in fremde_pfade(geaendert)]
    rot += geloescht(produktdateien("origin/main", wurzel), produktdateien("HEAD", wurzel))
    if rot:
        return melden(rot)
    db = subprocess.run([sys.executable, "-I", "-X", "utf8", "werkzeuge/datenbank.py", "pruefen"], cwd=wurzel,
                        capture_output=True, text=True, encoding="utf-8")
    print((db.stdout.strip().splitlines() or ["(keine Ausgabe)"])[-1])
    if db.returncode != 0:
        return melden([z for z in db.stdout.splitlines() if z.startswith("FEHLER")] or ["datenbank.py pruefen rot"])
    t = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "tests/alle-tests.ps1"],
                       cwd=wurzel, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print((t.stdout.strip().splitlines() or ["(keine Ausgabe)"])[-1])
    if t.returncode != 0:
        return melden([z for z in t.stdout.splitlines() if z.startswith("FEHLER")] or ["Tests rot"])
    print(f"Schranke grün: {len(geaendert)} Datei(en) geändert, nichts gelöscht, Datenbank und Tests grün.")
    if pushen:
        r = git("push", "origin", "HEAD:main", cwd=wurzel, pruefen=False)
        if r.returncode != 0:
            return melden(["Push abgelehnt (main hat sich bewegt?): " + r.stderr.strip()])
        print("Gepusht auf main; finder-daten.yml veröffentlicht finder-daten.json.")
    return 0


def melden(rot):
    print("SCHRANKE ROT – nicht pushen:")
    for z in rot:
        print("  -", z)
    return 1


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if argv[:1] == ["vorbereiten"]:
            return vorbereiten()
        if argv[:1] == ["pruefen"]:
            return pruefen("--pushen" in argv)
    except RuntimeError as e:
        print("Fehler:", e)
        return 2
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
