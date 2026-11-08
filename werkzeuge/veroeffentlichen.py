# -*- coding: utf-8 -*-
"""Veröffentlicht dist/ auf den Zweig gh-pages (GitHub Pages), preise.json dort bleibt unberührt.

Aufruf:  python -I werkzeuge/veroeffentlichen.py            bauen, nach .veroeffentlichung/ spiegeln, committen, pushen
         python -I werkzeuge/veroeffentlichen.py --trocken  nur bauen und spiegeln, kein Commit, kein Push
Voraussetzung: Remote origin gesetzt. Beim ersten Lauf wird gh-pages als eigener Zweig ohne Vorgeschichte angelegt
und als git worktree unter .veroeffentlichung/ eingebunden (steht in .gitignore).
Push nur mit Nicos Auftrag (AGENTS.md).
"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import app_bauen  # noqa: E402

WURZEL = Path(__file__).resolve().parent.parent
SEITEN = WURZEL / ".veroeffentlichung"
BEHALTEN = {".git", "preise.json"}


def git(*a, cwd=WURZEL, check=True):
    return subprocess.run(["git", "-C", str(cwd), *a], check=check, capture_output=True, text=True, encoding="utf-8")


def arbeitsbaum():
    if (SEITEN / ".git").exists():
        git("pull", "-q", "--ff-only", "origin", "gh-pages", cwd=SEITEN, check=False)
        return
    entfernt = git("ls-remote", "--heads", "origin", "gh-pages", check=False).stdout.strip()
    if entfernt:
        git("fetch", "-q", "origin", "gh-pages")
        git("worktree", "add", "-q", "-B", "gh-pages", str(SEITEN), "origin/gh-pages")
    else:
        git("worktree", "add", "-q", "--orphan", "-b", "gh-pages", str(SEITEN))


def spiegeln():
    for p in SEITEN.iterdir():
        if p.name not in BEHALTEN:
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    for p in (WURZEL / "dist").iterdir():
        if p.name == "preise.json" and (SEITEN / "preise.json").exists():
            continue
        ziel = SEITEN / p.name
        shutil.copytree(p, ziel) if p.is_dir() else shutil.copyfile(p, ziel)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    trocken = "--trocken" in sys.argv[1:]
    v = app_bauen.baue()
    arbeitsbaum()
    spiegeln()
    if trocken:
        print("trocken: .veroeffentlichung/ gespiegelt, nichts committet")
        return
    git("add", "-A", cwd=SEITEN)
    if git("diff", "--cached", "--quiet", cwd=SEITEN, check=False).returncode == 0:
        print("keine Änderung auf gh-pages")
        return
    git("commit", "-q", "-m", f"App {v}", cwd=SEITEN)
    git("push", "-q", "-u", "origin", "gh-pages", cwd=SEITEN)
    print(f"gepusht: gh-pages, App {v}")


if __name__ == "__main__":
    main()
