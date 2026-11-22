# -*- coding: utf-8 -*-
"""Veröffentlicht dist/ auf den Zweig gh-pages (GitHub Pages), preise.json und finder-preise.json dort bleiben unberührt.

Aufruf:  python -I werkzeuge/veroeffentlichen.py --stand <commit>   bauen, spiegeln, committen, pushen
         python -I werkzeuge/veroeffentlichen.py --trocken          nur bauen und spiegeln, kein Commit, kein Push
Push nur mit Auftrag des Besitzers bzw. nach bestandener Prüfung (AGENTS.md). Bindung an den geprüften Stand (F-11):
  - `--stand` nennt den geprüften Commit; HEAD muss genau dieser Commit sein, der Arbeitsbaum sauber (auch ohne
    unversionierte Dateien), und origin/main muss in HEAD enthalten sein (kein Bau aus einem älteren Stand);
  - nach dem Bau wird das noch einmal geprüft (nichts hat sich während des Baus geändert);
  - finder-daten.json trägt die Herkunft (Commit); die Online-Datei wird nur ersetzt, wenn ihre Herkunft im geprüften
    Stand enthalten ist (werkzeuge/herkunft.py, R2-02), sonst Abbruch;
  - gebaut wird in ein eigenes frisches Verzeichnis (nie das gemeinsame dist/, R3-01), und zwar aus einer eigenen Kopie
    genau des geprüften Commits (`git archive`, R5-04) mit dem Bauskript dieser Kopie als eigenem Prozess; der
    Arbeitsbaum wird nicht gelesen;
  - Commit aus einem unveränderlichen Git-Baum (R4-01): nach `git add -A` wird der Index mit `git write-tree` zu einem
    Baumobjekt; geprüft wird genau dieser Baum (jede Datei gleich dem eigenen Bau mit Modus, Typ und Objekt-ID, R5-02,
    finder-daten.json mit der geprüften Herkunft, Preisdateien mit vollem Eintrag aus dem Elterncommit, sonst nichts),
    committet wird genau dieser Baum mit `git commit-tree` auf den geprüften gh-pages-Elterncommit, gepusht wird genau
    diese Commit-ID, und nur wenn gh-pages auf GitHub noch genau dieser Elterncommit ist (Lease, R5-03);
  - `commit-tree` startet keine Commit-Hooks (R4-02): der Projekt-Hook prüft Quellcommits (tests/ fehlt im Seitenbaum);
    die für den Seitencommit vorgesehene Prüfung ist die Baumprüfung oben, die dieser Lauf selbst macht;
  - preise.json und finder-preise.json kommen nie aus dem Bau (dort ignoriert, ungeprüft, R2-01): vorhandene auf gh-pages
    bleiben, eine fehlende finder-preise.json bekommt den festen Startstand.
Der Seitenbaum ist ein eigener git worktree ohne Zweig (detached) unter .veroeffentlichung/ dieses Arbeitsbaums,
immer frisch auf origin/gh-pages; gepusht wird `<commit>:gh-pages` mit Lease auf den Elterncommit (hat sich gh-pages
bewegt oder fehlt es: Abbruch, neu starten).
"""
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import herkunft  # noqa: E402

WURZEL = Path(__file__).resolve().parent.parent
SEITEN = WURZEL / ".veroeffentlichung"
BEHALTEN = {".git", "preise.json", "finder-preise.json"}
PREIS_START = '{"stand": null, "preise": {}}\n'   # finder-preise.json, bis der Preislauf eigene Preise schreibt


def git(*a, cwd=None, check=True):
    cwd = WURZEL if cwd is None else cwd   # zur Laufzeit (Tests ersetzen WURZEL)
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


def bereitgestellt_fehler(text, gebaut, head):
    """Grund gegen den Commit oder None (R3-01): bereitgestellte finder-daten.json muss gültiges JSON mit herkunft = head
    sein und genau dem eigenen Bau gleichen. Reine Funktion, für Tests."""
    if text is None:
        return "finder-daten.json fehlt im Seitenbaum"
    try:
        d = json.loads(text)
    except ValueError:
        return "finder-daten.json im Seitenbaum ist kein JSON"
    if not isinstance(d, dict) or d.get("herkunft") != head:
        return f"finder-daten.json im Seitenbaum trägt nicht die geprüfte Herkunft {head[:12]}"
    if text != gebaut:
        return "finder-daten.json im Seitenbaum weicht vom eigenen Bau ab"
    return None


def blob_sha(daten):
    """Git-Objekt-ID einer Datei (blob) aus ihren Bytes."""
    return hashlib.sha1(b"blob %d\0" % len(daten) + daten).hexdigest()


DATEI = "100644"   # einziger zulässiger Modus der Bauartefakte (keine Links, nicht ausführbar, R5-02)


def bau_erwartet(bau, eltern_preise):
    """Soll-Inhalt des Seitencommits {Pfad: (Modus, Typ, Objekt-ID)}: alle Dateien des eigenen Baus als normale Datei
    (100644) außer den Preisdateien der obersten Ebene, dazu die Preisdateien mit vollem Eintrag des Elterncommits
    (eltern_preise); fehlt finder-preise.json, der Startstand. Ein Link im Bau bricht ab."""
    soll = {}
    for p in sorted(Path(bau).rglob("*")):
        rel = p.relative_to(bau).as_posix()
        if p.is_symlink():
            raise SystemExit(f"Abbruch, nichts veröffentlicht: {rel} im Bau ist ein Link")
        if p.is_file() and rel not in ("preise.json", "finder-preise.json"):
            soll[rel] = (DATEI, "blob", blob_sha(p.read_bytes()))
    soll.update(eltern_preise)
    soll.setdefault("finder-preise.json", (DATEI, "blob", blob_sha(PREIS_START.encode("utf-8"))))
    return soll


def baum_eintraege(baum, cwd):
    """{Pfad: (Modus, Typ, Objekt-ID)} eines Git-Baums, alle Eintragsarten (R5-02: Modus und Typ gehören zum Vergleich)."""
    aus = {}
    for z in git("ls-tree", "-r", "-z", baum, cwd=cwd).stdout.split("\0"):
        if z:
            kopf, pfad = z.split("\t", 1)
            modus, art, sha = kopf.split(" ")
            aus[pfad] = (modus, art, sha)
    return aus


def baum_fehler(ist, soll):
    """Gründe gegen den Commit dieses Baums (leer = genau der geprüfte Bau, R4-01): Modus, Typ und Objekt-ID müssen
    gemeinsam gleichen (R5-02). Reine Funktion, für Tests."""
    f = [f"{p}: nicht im eigenen Bau" for p in sorted(set(ist) - set(soll))]
    f += [f"{p}: fehlt im Seitenbaum" for p in sorted(set(soll) - set(ist))]
    for p in sorted(set(ist) & set(soll)):
        if ist[p] != soll[p]:
            art = "Modus/Typ" if ist[p][2] == soll[p][2] else "Inhalt"
            f.append(f"{p}: {art} weicht vom eigenen Bau ab ({' '.join(ist[p][:2])} statt {' '.join(soll[p][:2])})")
    return f


def kopie_holen(head, ziel):
    """Genau den Inhalt von Commit head nach ziel auspacken (git archive), nie den Arbeitsbaum (R5-04)."""
    r = subprocess.run(["git", "-C", str(WURZEL), "archive", "--format=tar", head], check=True, capture_output=True)
    with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tar:
        tar.extractall(ziel, filter="data")   # keine Pfade außerhalb von ziel, keine Gerätedateien


def app_bau_starten(kopie, ziel, head):
    """Bauskript der Kopie als eigener Prozess: liest nur die Kopie, schreibt nur nach ziel. Rückgabe App-Version."""
    r = subprocess.run([sys.executable, "-I", str(Path(kopie) / "werkzeuge" / "app_bauen.py"), "--ziel", str(ziel),
                        "--herkunft", head], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit("Abbruch, nichts veröffentlicht: Bau fehlgeschlagen\n" + (r.stderr or r.stdout)[-2000:])
    print(r.stdout.strip())
    return json.loads((Path(ziel) / "version.json").read_text(encoding="utf-8"))["app"]


def baue_aus_stand(head, ziel):
    """Bau genau des geprüften Commits head nach ziel (R5-04). Rückgabe App-Version."""
    with tempfile.TemporaryDirectory(prefix="kb-quelle-") as kopie:
        kopie_holen(head, kopie)
        return app_bau_starten(kopie, ziel, head)


def spiegeln(quelle=None):
    """Seitenbaum = Bau aus <quelle> (Standard dist/) plus die Preisdateien von gh-pages."""
    quelle = WURZEL / "dist" if quelle is None else Path(quelle)
    for p in SEITEN.iterdir():
        if p.name not in BEHALTEN:
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    for p in quelle.iterdir():
        if p.name in ("preise.json", "finder-preise.json"):
            continue   # gehören den Preisläufen; lokale Kopien sind ungeprüft (R2-01)
        ziel = SEITEN / p.name
        shutil.copytree(p, ziel) if p.is_dir() else shutil.copyfile(p, ziel)
    if not (SEITEN / "finder-preise.json").exists():
        (SEITEN / "finder-preise.json").write_text(PREIS_START, encoding="utf-8", newline="\n")


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
    eltern = git("rev-parse", "HEAD^{commit}", cwd=SEITEN).stdout.strip()   # geprüfter Seiten-Elterncommit (R4-01)
    r = git("show", f"{eltern}:finder-daten.json", cwd=SEITEN, check=False)
    grund = herkunft.fehler(r.stdout if r.returncode == 0 else None, head, herkunft.git_vorfahr(WURZEL))
    if grund:
        print("Abbruch, nichts veröffentlicht: finder-daten.json auf gh-pages –", grund)
        return 1
    alt = baum_eintraege(eltern, SEITEN)
    eltern_preise = {p: alt[p] for p in ("preise.json", "finder-preise.json") if p in alt}
    with tempfile.TemporaryDirectory(prefix="kb-veroeffentlichung-") as tmp:
        bau = Path(tmp) / "dist"   # eigenes frisches Verzeichnis, kein anderer Lauf schreibt hinein (R3-01)
        v = baue_aus_stand(head, bau)   # aus der Kopie genau dieses Commits, nicht aus dem Arbeitsbaum (R5-04)
        gebaut = (bau / "finder-daten.json").read_text(encoding="utf-8") if (bau / "finder-daten.json").exists() else ""
        soll = bau_erwartet(bau, eltern_preise)
        spiegeln(bau)
    git("add", "-A", cwd=SEITEN)
    baum = git("write-tree", cwd=SEITEN).stdout.strip()   # unveränderlich: genau dieser Baum wird geprüft und committet
    r = git("show", f"{baum}:finder-daten.json", cwd=SEITEN, check=False)
    fehler = baum_fehler(baum_eintraege(baum, SEITEN), soll)
    grund = bereitgestellt_fehler(r.stdout if r.returncode == 0 else None, gebaut, head)
    if grund:
        fehler.insert(0, grund)
    if trocken or fehler:
        git("reset", "-q", cwd=SEITEN)   # nur aus dem Index nehmen; die gespiegelten Dateien bleiben zur Ansicht
    if fehler:
        print("Abbruch, nichts veröffentlicht:\n  - " + "\n  - ".join(fehler[:10]))
        return 1
    if trocken:
        print(f"trocken: .veroeffentlichung/ gespiegelt, Baum {baum[:12]} geprüft, nichts committet")
        return 0
    if baum == git("rev-parse", f"{eltern}^{{tree}}", cwd=SEITEN).stdout.strip():
        print("keine Änderung auf gh-pages")
        return 0
    if stand_lesen()[:2] != (head, True):
        git("reset", "-q", cwd=SEITEN)
        print("Abbruch: HEAD oder Arbeitsbaum hat sich während des Baus geändert")
        return 1
    neu = git("commit-tree", baum, "-p", eltern, "-m", f"App {v} (Stand {head[:12]})", cwd=SEITEN).stdout.strip()
    git("update-ref", "--no-deref", "HEAD", neu, eltern, cwd=SEITEN)   # Seitenbaum steht danach sauber auf dem Commit
    # R5-03: nur wenn gh-pages auf GitHub noch genau der geprüfte Elterncommit ist (nicht zurückgesetzt, nicht gelöscht)
    r = git("push", "-q", f"--force-with-lease=refs/heads/gh-pages:{eltern}", "origin", f"{neu}:refs/heads/gh-pages",
            cwd=SEITEN, check=False)
    if r.returncode != 0:
        print("Push abgelehnt (gh-pages ist nicht mehr der geprüfte Elterncommit), erneut starten:", r.stderr.strip())
        return 1
    print(f"gepusht: gh-pages, App {v}, Stand {head[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
