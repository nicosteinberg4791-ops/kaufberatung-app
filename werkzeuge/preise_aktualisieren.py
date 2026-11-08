# -*- coding: utf-8 -*-
"""Schreibt preise.json für die App aus der täglichen Preisabfrage (preiswecker.py aus Runde 6), optional mit Push.

Die Rechenlogik (günstigster Gesamtpreis mit belegtem Versand, Tiefstpreis, Verlauf 60 Tage) bleibt in preiswecker.py
und wird hier nur aufgerufen: preise.json ist dieselbe Datenform wie die db-Dokumente "preise/<id>" und "wecker/lauf".
Wunschpreise gibt es hier nicht (die liegen nur auf dem Handy).

Aufrufe:
  python -X utf8 -I werkzeuge/preise_aktualisieren.py                       neu abrufen, .veroeffentlichung/preise.json schreiben
  python -X utf8 -I werkzeuge/preise_aktualisieren.py --abruf abruf.json    vorhandenes Abrufergebnis (stdout von preiswecker.py)
  ... --ziel dist/preise.json                                               anderes Ziel (lokaler Test)
  ... --push                                                                im gh-pages-Arbeitsbaum committen und pushen
  ... --skript <pfad/preiswecker.py>                                        Ort des Skripts (Standard siehe SKRIPTE)
Nur Standardbibliothek.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SEITEN = WURZEL / ".veroeffentlichung"   # git worktree auf dem Zweig gh-pages (werkzeuge/veroeffentlichen.py)
SKRIPTE = [Path.home() / ".claude" / "scheduled-tasks" / "tv-preiswecker" / "preiswecker.py",
           WURZEL / "werkzeuge" / "preiswecker.py"]


def lade_skript(pfad):
    kandidaten = [Path(pfad)] if pfad else SKRIPTE
    for p in kandidaten:
        if p.exists():
            spec = importlib.util.spec_from_file_location("preiswecker", p)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            return m, p
    raise SystemExit("preiswecker.py nicht gefunden: " + ", ".join(str(p) for p in kandidaten))


def zahl_ok(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and 0 < x < 100000


def aktualisiere(pw, erg, ziel):
    alt = {}
    if ziel.exists():
        try:
            alt = json.loads(ziel.read_text(encoding="utf-8"))
        except ValueError:
            alt = {}
    alt_preise = alt.get("preise") if isinstance(alt.get("preise"), dict) else {}
    with tempfile.TemporaryDirectory() as tmp:
        db, aus = Path(tmp, "db"), Path(tmp, "aus")
        (db / "preise").mkdir(parents=True)
        for mid, doc in alt_preise.items():
            if mid in pw.MODELLE and isinstance(doc, dict):
                (db / "preise" / f"{mid}.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        bericht = pw.abgleich(erg, str(db), str(aus))
        preise = {}
        for mid in pw.MODELLE:
            f = aus / f"preise_{mid}.json"
            if f.exists():
                d = json.loads(f.read_text(encoding="utf-8"))
                d.pop("meldung", None)       # Wunschpreis-Abgleich macht die App auf dem Handy
                preise[mid] = d
            elif mid in alt_preise:
                preise[mid] = alt_preise[mid]  # heute kein belegtes Angebot: letzten Stand behalten
        lauf = json.loads((aus / "wecker_lauf.json").read_text(encoding="utf-8"))
    for mid, d in preise.items():
        g = (d.get("aktuell") or {}).get("gesamt")
        assert zahl_ok(g), f"{mid}: Gesamtpreis {g!r} unplausibel"
    neu = {"format": 1, "zeit": erg["zeit"], "quelle": "heise-Preisvergleich, günstigster Gesamtpreis mit belegtem Versand",
           "preise": preise, "lauf": lauf}
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps(neu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return bericht


def git_aus(ordner, *a):
    r = subprocess.run(["git", "-C", str(ordner), *a], capture_output=True, text=True, encoding="utf-8")
    return r.stdout.strip() if r.returncode == 0 else None


def arbeitsbaum_pruefen(ordner, zweig="gh-pages"):
    """Nur ein eigener Git-Arbeitsbaum genau in `ordner` mit ausgechecktem `zweig` ist erlaubt (sonst SystemExit)."""
    wurzel = git_aus(ordner, "rev-parse", "--show-toplevel") if Path(ordner).is_dir() else None
    if not wurzel or Path(wurzel).resolve() != Path(ordner).resolve():
        raise SystemExit(f"--push: {ordner} ist kein eigener Git-Arbeitsbaum (erst werkzeuge/veroeffentlichen.py ausführen)")
    kopf = git_aus(ordner, "symbolic-ref", "--short", "HEAD")
    if kopf != zweig:
        raise SystemExit(f"--push: im Arbeitsbaum ist {kopf!r} ausgecheckt, erwartet {zweig!r}")


def push(ziel):
    arbeitsbaum_pruefen(ziel.parent)
    git = ["git", "-C", str(ziel.parent)]
    fremd = [d for d in (git_aus(ziel.parent, "diff", "--cached", "--name-only") or "").splitlines() if d and d != ziel.name]
    if fremd:
        raise SystemExit("--push: im Index liegen fremde Änderungen, nichts committet: " + ", ".join(fremd))
    subprocess.run(git + ["add", "--", ziel.name], check=True)
    if subprocess.run(git + ["diff", "--cached", "--quiet", "--", ziel.name]).returncode == 0:
        print("preise.json unverändert, kein Commit")
        return
    subprocess.run(git + ["commit", "-q", "-m", "Preise " + json.loads(ziel.read_text(encoding="utf-8"))["zeit"][:10],
                          "--", ziel.name], check=True)
    subprocess.run(git + ["push", "-q", "origin", "gh-pages"], check=True)
    print("gepusht: gh-pages/preise.json")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--abruf", help="JSON-Ausgabe von preiswecker.py (ohne Argumente); sonst wird neu abgerufen")
    a.add_argument("--ziel", default=str(SEITEN / "preise.json"))
    a.add_argument("--skript")
    a.add_argument("--push", action="store_true")
    x = a.parse_args()
    pw, pfad = lade_skript(x.skript)
    erg = json.loads(Path(x.abruf).read_text(encoding="utf-8")) if x.abruf else pw.abruf_alle()
    assert isinstance(erg, dict) and isinstance(erg.get("modelle"), dict) and isinstance(erg.get("zeit"), str), "Abrufergebnis ungültig"
    ziel = Path(x.ziel)
    if x.push:   # vor dem Schreiben: nur der gh-pages-Arbeitsbaum, nur preise.json
        assert ziel.parent.resolve() == SEITEN.resolve() and ziel.name == "preise.json", "--push nur mit dem gh-pages-Arbeitsbaum"
        arbeitsbaum_pruefen(ziel.parent)
    bericht = aktualisiere(pw, erg, ziel)
    print(json.dumps({"skript": str(pfad), "ziel": str(ziel), "status": bericht["status"], "lauf": bericht["lauf"]}, ensure_ascii=False))
    if x.push:
        push(ziel)


if __name__ == "__main__":
    main()
