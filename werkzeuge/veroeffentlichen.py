# -*- coding: utf-8 -*-
"""Veröffentlicht dist/ auf den Zweig gh-pages (GitHub Pages), preise.json und finder-preise.json dort bleiben unberührt.

Aufruf:  python -I werkzeuge/veroeffentlichen.py --stand <commit>   bauen, spiegeln, committen, pushen
         python -I werkzeuge/veroeffentlichen.py --trocken          nur bauen und spiegeln, kein Commit, kein Push
Push nur mit Auftrag des Besitzers bzw. nach bestandener Prüfung (AGENTS.md). Bindung an den geprüften Stand (F-11):
  - `--stand` nennt den geprüften Commit; HEAD muss genau dieser Commit sein, der Arbeitsbaum sauber (auch ohne
    unversionierte Dateien), und origin/main muss in HEAD enthalten sein (kein Bau aus einem älteren Stand);
  - nach dem Bau wird das noch einmal geprüft (nichts hat sich während des Baus geändert);
  - eine neuere finder-daten.json auf gh-pages (Datenworkflow) wird nie durch einen älteren Datenstand ersetzt.
Der Seitenbaum ist ein eigener git worktree ohne Zweig (detached) unter .veroeffentlichung/ dieses Arbeitsbaums,
immer frisch auf origin/gh-pages; gepusht wird `HEAD:gh-pages` ohne Erzwingen (hat sich gh-pages bewegt: neu starten).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import app_bauen  # noqa: E402

WURZEL = Path(__file__).resolve().parent.parent
SEITEN = WURZEL / ".veroeffentlichung"
BEHALTEN = {".git", "preise.json", "finder-preise.json"}


def git(*a, cwd=WURZEL, check=True):
    return subprocess.run(["git", "-C", str(cwd), *a], check=check, capture_output=True, text=True, encoding="utf-8")


def stand_fehler(stand, head, sauber, main_enthalten):
    """Liste der Gründe gegen eine Veröffentlichung (leer = in Ordnung). Reine Funktion, für Tests."""
    f = []
    if not stand:
        f.append("--stand <geprüfter Commit> fehlt")
    elif not head.startswith(stand.lower()) or len(stand) < 7:
        f.append(f"HEAD {head[:12]} ist nicht der geprüfte Stand {stand}")
    if not sauber:
        f.append("Arbeitsbaum nicht sauber (Änderungen oder unversionierte Dateien)")
    if not main_enthalten:
        f.append("origin/main ist nicht in HEAD enthalten (Bau aus älterem Stand?)")
    return f


def daten_aelter(online, neu):
    """True, wenn die gebaute finder-daten.json einen älteren Datenstand hat als die veröffentlichte (nie ersetzen)."""
    try:
        alt_stand = json.loads(online).get("stand")
    except (ValueError, AttributeError):
        return False   # unlesbare Online-Datei darf ersetzt werden
    neu_stand = json.loads(neu).get("stand")
    return isinstance(alt_stand, str) and (not isinstance(neu_stand, str) or neu_stand < alt_stand)


def stand_lesen():
    git("fetch", "-q", "origin", "main", "gh-pages")
    head = git("rev-parse", "HEAD").stdout.strip()
    sauber = git("status", "--porcelain", "--untracked-files=all").stdout.strip() == ""
    enthalten = git("merge-base", "--is-ancestor", "origin/main", "HEAD", check=False).returncode == 0
    return head, sauber, enthalten


def arbeitsbaum():
    """Seitenbaum frisch auf origin/gh-pages (detached), nur wenn er keine eigenen Änderungen hat."""
    if (SEITEN / ".git").exists():
        if git("status", "--porcelain", cwd=SEITEN).stdout.strip():
            raise SystemExit(f"Abbruch: {SEITEN.name}/ hat Änderungen (erst prüfen, nicht verwerfen)")
        git("checkout", "-q", "--detach", "origin/gh-pages", cwd=SEITEN)
    else:
        git("worktree", "add", "-q", "--detach", str(SEITEN), "origin/gh-pages")


def spiegeln():
    for p in SEITEN.iterdir():
        if p.name not in BEHALTEN:
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    for p in (WURZEL / "dist").iterdir():
        if p.name in ("preise.json", "finder-preise.json") and (SEITEN / p.name).exists():
            continue
        ziel = SEITEN / p.name
        shutil.copytree(p, ziel) if p.is_dir() else shutil.copyfile(p, ziel)


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    argv = list(sys.argv[1:] if argv is None else argv)
    trocken = "--trocken" in argv
    stand = argv[argv.index("--stand") + 1] if "--stand" in argv and argv.index("--stand") + 1 < len(argv) else None
    head, sauber, enthalten = stand_lesen()
    if not trocken:
        fehler = stand_fehler(stand, head, sauber, enthalten)
        if fehler:
            print("Abbruch, nichts veröffentlicht:\n  - " + "\n  - ".join(fehler))
            return 1
    arbeitsbaum()
    online = (SEITEN / "finder-daten.json").read_text(encoding="utf-8") if (SEITEN / "finder-daten.json").exists() else None
    v = app_bauen.baue()
    if online is not None and daten_aelter(online, (WURZEL / "dist" / "finder-daten.json").read_text(encoding="utf-8")):
        print("Abbruch: finder-daten.json auf gh-pages ist neuer als der gebaute Stand (nicht überschreiben)")
        return 1
    spiegeln()
    if trocken:
        print("trocken: .veroeffentlichung/ gespiegelt, nichts committet")
        return 0
    if stand_lesen()[:2] != (head, True):
        print("Abbruch: HEAD oder Arbeitsbaum hat sich während des Baus geändert")
        return 1
    git("add", "-A", cwd=SEITEN)
    if git("diff", "--cached", "--quiet", cwd=SEITEN, check=False).returncode == 0:
        print("keine Änderung auf gh-pages")
        return 0
    git("commit", "-q", "-m", f"App {v} (Stand {head[:12]})", cwd=SEITEN)
    r = git("push", "-q", "origin", "HEAD:refs/heads/gh-pages", cwd=SEITEN, check=False)
    if r.returncode != 0:
        print("Push abgelehnt (gh-pages hat sich bewegt?), erneut starten:", r.stderr.strip())
        return 1
    print(f"gepusht: gh-pages, App {v}, Stand {head[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
