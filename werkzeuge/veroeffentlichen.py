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
    genau des geprüften Commits (direkt aus den Git-Objekten, ohne Attribute und Filter, danach mit dem Commit
    abgeglichen, R5-04) mit dem Bauskript dieser Kopie als eigenem Prozess; der Arbeitsbaum wird nicht gelesen;
  - Commit aus einem unveränderlichen Git-Baum (R4-01): nach `git add -A` wird der Index mit `git write-tree` zu einem
    Baumobjekt; geprüft wird genau dieser Baum (jede Datei gleich dem eigenen Bau mit Modus, Typ und Objekt-ID, R5-02,
    finder-daten.json mit der geprüften Herkunft, Preisdateien mit vollem Eintrag aus dem Elterncommit, sonst nichts;
    zusätzlich muss die Baum-ID gleich dem aus dem Soll gebildeten Baum sein, R6-01),
    committet wird genau dieser Baum mit `git commit-tree` auf den geprüften gh-pages-Elterncommit, gepusht wird genau
    diese Commit-ID, und nur wenn gh-pages auf GitHub noch genau dieser Elterncommit ist (Lease, R5-03);
  - alle Git-Aufrufe und der Bau laufen ohne Ersetzungsreferenzen und Grafts (R7-01); die Bauquelle hat
    nur normale Dateien (100644, R7-02); Pfade werden als Bytes gelesen, Steuer- und Formatzeichen brechen ab
    (R7-03, R8-02); unter Windows unzulässige oder kollidierende Namen brechen vor dem ersten Schreiben ab (R8-03);
  - `commit-tree` startet keine Commit-Hooks (R4-02): der Projekt-Hook prüft Quellcommits (tests/ fehlt im Seitenbaum);
    die für den Seitencommit vorgesehene Prüfung ist die Baumprüfung oben, die dieser Lauf selbst macht;
  - preise.json und finder-preise.json kommen nie aus dem Bau (dort ignoriert, ungeprüft, R2-01): vorhandene auf gh-pages
    bleiben, eine fehlende finder-preise.json bekommt den festen Startstand.
Der Seitenbaum ist ein eigener git worktree ohne Zweig (detached) unter .veroeffentlichung/ dieses Arbeitsbaums,
immer frisch auf origin/gh-pages; gepusht wird `<commit>:gh-pages` mit Lease auf den Elterncommit (hat sich gh-pages
bewegt oder fehlt es: Abbruch, neu starten).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import herkunft  # noqa: E402

WURZEL = Path(__file__).resolve().parent.parent
SEITEN = WURZEL / ".veroeffentlichung"
BEHALTEN = {".git", "preise.json", "finder-preise.json"}
PREIS_START = '{"stand": null, "preise": {}}\n'   # finder-preise.json, bis der Preislauf eigene Preise schreibt


def umgebung(**extra):
    """Umgebung jedes Git-Aufrufs und des Baus: ohne Ersetzungsreferenzen (git replace) und Grafts, damit jede
    Objekt-ID genau ihr eigenes Objekt mit seinen echten Elterncommits liefert (R7-01)."""
    return {**os.environ, **herkunft.OHNE_ERSATZ, **extra}


def git(*a, cwd=None, check=True):
    cwd = WURZEL if cwd is None else cwd   # zur Laufzeit (Tests ersetzen WURZEL)
    return subprocess.run(["git", "-C", str(cwd), *a], check=check, capture_output=True, text=True, encoding="utf-8",
                          env=umgebung())


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
    """{Pfad: (Modus, Typ, Objekt-ID)} eines Git-Baums, alle Eintragsarten (R5-02: Modus und Typ gehören zum Vergleich).
    Gelesen als Bytes, Pfade unverändert als UTF-8 (R7-03: der Textmodus machte aus \\r ein \\n); ein Pfad mit
    Zeichen der Unicode-Klasse C (Steuer-, Format-, Ersatz-, private, nicht zugeordnete; C0, DEL, C1, Richtungswechsel)
    oder einem Zeilen-/Absatztrenner bricht ab (R8-02)."""
    r = subprocess.run(["git", "-C", str(cwd), "ls-tree", "-r", "-z", baum], check=True, capture_output=True,
                       env=umgebung())
    aus = {}
    for z in r.stdout.split(b"\0"):
        if z:
            kopf, roh = z.split(b"\t", 1)
            modus, art, sha = kopf.decode("ascii").split(" ")
            try:
                pfad = roh.decode("utf-8")
            except UnicodeDecodeError:
                raise SystemExit(f"Abbruch, nichts veröffentlicht: Pfad {roh!r} in {baum[:12]} ist kein UTF-8")
            if any(unicodedata.category(c)[0] == "C" or unicodedata.category(c) in ("Zl", "Zp") for c in pfad):
                raise SystemExit(f"Abbruch, nichts veröffentlicht: Pfad {pfad!r} in {baum[:12]} enthält Steuerzeichen")
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


def soll_baum(soll, cwd):
    """Objekt-ID des Wurzelbaums, der genau aus soll entsteht (eigener, leerer Index; R6-01). Gleiche ID = gleicher
    Baum samt aller Verzeichniseinträge, auch solcher, die `ls-tree -r` nicht zeigt (leere Unterbäume)."""
    with tempfile.TemporaryDirectory(prefix="kb-index-") as t:
        env = umgebung(GIT_INDEX_FILE=str(Path(t) / "index"))   # nie der Index des Seitenbaums
        zeilen = "".join(f"{m} {sha}\t{p}\0" for p, (m, _, sha) in sorted(soll.items()))
        r = subprocess.run(["git", "-C", str(cwd), "update-index", "-z", "--add", "--index-info"],
                           input=zeilen.encode("utf-8"), capture_output=True, env=env)
        if r.returncode != 0:
            raise SystemExit("Abbruch, nichts veröffentlicht: Soll-Baum nicht bildbar\n"
                             + r.stderr.decode("utf-8", "replace"))
        r = subprocess.run(["git", "-C", str(cwd), "write-tree", "--missing-ok"], check=True, capture_output=True,
                           env=env)
        return r.stdout.decode("ascii").strip()


def objekte_lesen(shas):
    """{Objekt-ID: Bytes} der Blobs aus der Objektdatenbank der Quelle (git cat-file --batch, ohne Filter)."""
    r = subprocess.run(["git", "-C", str(WURZEL), "cat-file", "--batch"],
                       input="".join(f"{s}\n" for s in shas).encode("ascii"), check=True, capture_output=True,
                       env=umgebung())
    aus, b, pos = {}, r.stdout, 0
    for sha in shas:
        ende = b.index(b"\n", pos)
        kopf = b[pos:ende].decode("ascii").split(" ")
        if kopf[0] != sha or len(kopf) != 3 or kopf[1] != "blob":
            raise SystemExit(f"Abbruch, nichts veröffentlicht: Objekt {sha[:12]} ist kein Blob ({' '.join(kopf[1:])})")
        n = int(kopf[2])
        aus[sha] = b[ende + 1:ende + 1 + n]
        pos = ende + 2 + n   # Inhalt, dann ein Zeilenende
    return aus


GERAETE = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {f"{g}{n}" for g in ("COM", "LPT")
                                                             for n in "0123456789¹²³"}
KURZNAME = re.compile(r"~[0-9]")   # konservativ: jede Tilde mit Ziffer, wie in PROGRA~1 oder VEROEF~1.PY


def windows_pfad_fehler(pfade):
    """Gründe gegen das Auspacken dieser Pfade unter Windows (leer = in Ordnung, R8-03), geprüft vor dem ersten
    Schreiben: kein \\, keine Zeichen <>:"|?*, kein Punkt oder Leerzeichen am Namensende (auch nicht . und ..), keine
    Gerätenamen (auch mit Endung, z. B. nul.txt), keine Komponente über 255 UTF-16-Zeichen (R9-01), kein möglicher
    8.3-Kurzname (Tilde mit Ziffer, R9-02), keine zwei Pfade, die sich nur in Groß-/Kleinschreibung unterscheiden
    (auch bei Ordnern). Reine Funktion, für Tests."""
    f, gesehen = [], {}
    for p in sorted(pfade):
        teile = p.split("/")
        for i, n in enumerate(teile):
            if not n or any(c in '\\<>:"|?*' for c in n) or n[-1] in ". ":
                f.append(f"{p}: Name {n!r} ist unter Windows unzulässig")
            elif n.split(".")[0].rstrip(" ").upper() in GERAETE:
                f.append(f"{p}: Name {n!r} ist ein Windows-Gerätename")
            elif len(n.encode("utf-16-le")) // 2 > 255:   # R9-01: NTFS-Grenze je Komponente, auch ohne MAX_PATH
                f.append(f"{p}: Name {n[:20]!r}… ist länger als 255 UTF-16-Zeichen")
            elif KURZNAME.search(n):   # R9-02: 8.3-Kurzname (veroef~1.py) kann dieselbe Datei treffen wie der lange Name
                f.append(f"{p}: Name {n!r} kann ein Windows-Kurzname sein")
            vorne = "/".join(teile[:i + 1])
            frueher = gesehen.setdefault(vorne.casefold(), vorne)
            if frueher != vorne:
                f.append(f"{p}: {vorne!r} kollidiert unter Windows mit {frueher!r} (Groß-/Kleinschreibung)")
    return f


def kopie_fehler(ziel, eintraege):
    """Gründe, warum die Kopie in ziel nicht genau die Einträge des Commits ist (Pfade, Objekt-IDs, nichts zusätzlich).
    Reine Prüfung, für Tests (R5-04)."""
    ziel = Path(ziel)
    da = {p.relative_to(ziel).as_posix(): p for p in ziel.rglob("*") if p.is_file() or p.is_symlink()}
    f = [f"{p}: nicht im Stand" for p in sorted(set(da) - set(eintraege))]
    f += [f"{p}: fehlt in der Kopie" for p in sorted(set(eintraege) - set(da))]
    f += [f"{p}: Inhalt weicht vom Stand ab" for p in sorted(set(da) & set(eintraege))
          if da[p].is_symlink() or blob_sha(da[p].read_bytes()) != eintraege[p][2]]
    return f


def kopie_holen(head, ziel):
    """Genau den Inhalt von Commit head nach ziel schreiben, direkt aus den Git-Objekten (R5-04): keine Attribute
    (auch nicht .git/info/attributes mit export-ignore/export-subst), keine Filter, nie der Arbeitsbaum; danach
    Abgleich jeder Datei mit dem Commit."""
    eintraege = baum_eintraege(head, WURZEL)
    ziel = Path(ziel).resolve()
    for p, (m, art, _) in sorted(eintraege.items()):
        if art != "blob" or m != DATEI:   # R7-02: auch nicht 100755 (das Ausführungsbit ginge in der Kopie verloren)
            raise SystemExit(f"Abbruch, nichts veröffentlicht: {p} im Stand ist keine normale Datei ({m} {art})")
    fehler = windows_pfad_fehler(eintraege)
    if fehler:   # R8-03: vor dem ersten Schreiben, nicht erst im Abgleich danach
        raise SystemExit("Abbruch, nichts veröffentlicht: Pfade im Stand sind unter Windows nicht auspackbar\n  - "
                         + "\n  - ".join(fehler[:10]))
    inhalt = objekte_lesen(sorted({e[2] for e in eintraege.values()}))
    for p, (_, _, sha) in sorted(eintraege.items()):
        datei = (ziel / p).resolve()
        if ziel not in datei.parents:
            raise SystemExit(f"Abbruch, nichts veröffentlicht: {p} liegt außerhalb der Kopie")
        datei.parent.mkdir(parents=True, exist_ok=True)
        datei.write_bytes(inhalt[sha])
    fehler = kopie_fehler(ziel, eintraege)
    if fehler:
        raise SystemExit("Abbruch, nichts veröffentlicht: Kopie weicht vom Stand ab\n  - " + "\n  - ".join(fehler[:10]))


def app_bau_starten(kopie, ziel, head):
    """Bauskript der Kopie als eigener Prozess: liest nur die Kopie, schreibt nur nach ziel. Rückgabe App-Version."""
    r = subprocess.run([sys.executable, "-I", str(Path(kopie) / "werkzeuge" / "app_bauen.py"), "--ziel", str(ziel),
                        "--herkunft", head], capture_output=True, text=True, encoding="utf-8", env=umgebung())
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
    if not fehler and baum != soll_baum(soll, SEITEN):   # R6-01: auch Verzeichniseinträge (leere Unterbäume)
        fehler.append(f"Baum {baum[:12]} weicht vom eigenen Bau ab (Verzeichniseinträge)")
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
