# -*- coding: utf-8 -*-
"""Baut die App-Fassung (dist/) aus der fertigen Kaufberatung und der App-Hülle (app/).

Nachziehen einer neuen Fassung (ein Befehl):
    python -I werkzeuge/app_bauen.py --quelle <kaufberatung.html> --version "Artifact-Version 9"
  <kaufberatung.html> darf das Bauergebnis des alten Projekts sein (Fragment ohne <html>) oder die von
  `Artifact read` gespeicherte Live-Seite (mit Veröffentlichungsrahmen, der Rahmen wird entfernt).
  Die Quelle wird nach quelle/kaufberatung.html kopiert (Herkunft in quelle/herkunft.json), danach wird gebaut.
Nur neu bauen (z. B. nach Änderung an app/):
    python -I werkzeuge/app_bauen.py
Inhalte werden nicht verändert: der Inhalt wird unverändert in die Seite gesetzt, die Hülle kommt davor/danach.
Seiten (D8): index.html = Finder „Finden & Vergleichen“ (app/finder/ + finder-daten.json aus werkzeuge/datenbank.py),
ratgeber.html = Inhalt der Kaufberatung (Artifact) mit Hülle app.js/app.css.
Nur Standardbibliothek. Jeder Anker wird per assert geprüft.
"""
import argparse
import hashlib
import json
import re
import os
import shutil
import tempfile
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # python -I nimmt den Skriptordner nicht in den Suchpfad
import datenbank  # noqa: E402

WURZEL = Path(__file__).resolve().parent.parent
APP = WURZEL / "app"
QUELLE = WURZEL / "quelle"
DIST = WURZEL / "dist"
FINDER = ["finder.css", "bewertung.js", "finder-app.js", "finder.js"]   # aus app/finder/, flach nach dist/
BEHALTEN = {"preise.json", "finder-preise.json"}   # gehören den täglichen Abfragen, nie überschreiben
STATISCH = ["app.js", "app.css", "manifest.webmanifest", "icons/icon.svg", "icons/icon-192.png", "icons/icon-512.png",
            "icons/icon-maskable-192.png", "icons/icon-maskable-512.png", "icons/apple-touch-icon.png"]


def rahmen_entfernen(text):
    """Veröffentlichungsrahmen von claude.ai (doctype … <body> … </body></html>) abnehmen, Fragment zurückgeben."""
    t = text.lstrip("﻿")
    if not t.lower().startswith("<!doctype"):
        return t
    i = t.find("<body>")
    j = t.rfind("</body>")
    assert i >= 0 and j > i, "Rahmen erkannt, aber <body> … </body> fehlt"
    return t[i + len("<body>"):j].strip("\n") + "\n"


def pruefe_fragment(f):
    assert f.count("<title>Kaufberatung</title>") == 1, "Titel der Kaufberatung fehlt (falsche Datei?)"
    assert 'id="view-tv"' in f and 'id="tab-sauger"' in f, "Reiter TV/Staubsauger fehlen (falsche Datei?)"
    assert "<html" not in f.lower() and "<body" not in f.lower(), "Fragment enthält noch <html>/<body>"
    assert "</script>" in f, "keine Skripte im Fragment"


def uebernehmen(pfad, version):
    roh = Path(pfad).read_text(encoding="utf-8")
    f = rahmen_entfernen(roh)
    pruefe_fragment(f)
    QUELLE.mkdir(exist_ok=True)
    (QUELLE / "kaufberatung.html").write_text(f, encoding="utf-8", newline="\n")
    herkunft = {"version": version or "unbekannt", "datei": Path(pfad).name,
                "sha256": hashlib.sha256(f.encode("utf-8")).hexdigest(), "bytes": len(f.encode("utf-8")),
                "uebernommen": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")}
    (QUELLE / "herkunft.json").write_text(json.dumps(herkunft, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"übernommen: {herkunft['version']}, {herkunft['bytes']:,} Bytes")


KOPF = """<!doctype html>
<html lang="de"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Kaufberatung</title>
<meta name="description" content="Kaufberatung: Fernseher, Staubsauger und Air Fryer, mit Preiswecker.">
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#eef1f5">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#000000">
<meta name="mobile-web-app-capable" content="yes">
<meta name="robots" content="noindex">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<!-- Grundrahmen wie bei der Veröffentlichung auf claude.ai, damit die Seite gleich aussieht -->
<style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style>
<script>window.KB_APP_STAND="{V}"</script>
<script src="app.js?v={V}"></script>
</head><body>
"""
FUSS = """<link rel="stylesheet" href="app.css?v={V}">
</body></html>
"""


FINDER_ANKER = "<!-- Manifest, Symbole und app.js (Service Worker) setzt der App-Bau ein. -->"
FINDER_KOPF = """<meta name="mobile-web-app-capable" content="yes">
<meta name="robots" content="noindex">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<script>window.KB_APP_STAND="{V}"</script>
<script src="finder-app.js?v={V}"></script>"""


def finder_seite(v):
    """app/finder/index.html mit Hülle (Manifest, Symbole, finder-app.js) und versionierten Verweisen."""
    s = (APP / "finder" / "index.html").read_text(encoding="utf-8")
    assert s.count(FINDER_ANKER) == 1, "Finder: Anker für die Hülle fehlt"
    s = s.replace(FINDER_ANKER, FINDER_KOPF.replace("{V}", v))
    for d in ("finder.css", "bewertung.js", "finder.js"):
        alt = ('href="' if d.endswith(".css") else 'src="') + d + '"'
        assert s.count(alt) == 1, f"Finder: Verweis {alt} {s.count(alt)}-mal"
        s = s.replace(alt, alt[:-1] + f'?v={v}"')
    return s


def versionshash(fragment, daten):
    """Version = Prüfsumme über Inhalt, Daten, Hülle und die HTML-Vorlagen dieses Skripts (F-12): jede Änderung am
    ausgelieferten HTML erzeugt einen neuen Service Worker."""
    h = hashlib.sha256(fragment.encode("utf-8"))
    h.update(daten)
    for vorlage in (KOPF, FUSS, FINDER_ANKER, FINDER_KOPF):
        h.update(b"|" + vorlage.encode("utf-8"))
    for d in STATISCH + ["sw.js", "finder/index.html"] + ["finder/" + x for x in FINDER]:
        h.update((APP / d).read_bytes())
    return h.hexdigest()[:12]


def baue(daten_herkunft=None, ziel=None):
    """daten_herkunft: Commit für finder-daten.json (veroeffentlichen.py, R2-02); lokal ohne.
    ziel: Ausgabeverzeichnis (Standard dist/); veroeffentlichen.py baut in ein eigenes frisches Verzeichnis (R3-01).
    A1: ein eigenes Ziel muss neu oder leer sein und wird nie aufgeräumt oder beschrieben. Gebaut wird in ein exklusiv
    angelegtes Nachbarverzeichnis; erst am Ende ersetzt es das Ziel (os.rmdir scheitert, wenn das Ziel inzwischen
    nicht mehr leer ist; os.rename folgt keinem Link). Ein Rennen oder ein ausgetauschter Zielpfad bricht so ab, statt
    fremde Dateien zu löschen oder zu überschreiben. Aufgeräumt wird nur dist/ (Standard), die Preisdateien bleiben."""
    if ziel is None:
        return _baue(daten_herkunft, globals()["DIST"], "dist/", aufraeumen=True)
    z = Path(ziel)
    if z.exists() and (not z.is_dir() or any(z.iterdir())):
        raise SystemExit(f"Abbruch: Ziel {z} ist nicht leer (nur ein neues oder leeres Verzeichnis)")
    z.absolute().parent.mkdir(parents=True, exist_ok=True)
    bau = None
    try:   # R2-02: mkdtemp im geschützten Block, damit auch ein Abbruch direkt danach aufgeräumt wird
        bau = Path(tempfile.mkdtemp(prefix=".kb-bau-", dir=z.absolute().parent))
        ergebnis = _baue(daten_herkunft, bau, str(z))
        war_leer = z.exists() or z.is_symlink()
        if war_leer:
            try:
                os.rmdir(z)   # nur ein leeres Verzeichnis (oder ein Link darauf) verschwindet
            except OSError:
                raise SystemExit(f"Abbruch: Ziel {z} ist während des Baus nicht mehr leer, nichts geschrieben") from None
        try:
            os.rename(bau, z)
        except BaseException:
            if war_leer:
                z.mkdir(exist_ok=True)   # R2-03: das zuvor leere Ziel wiederherstellen
            raise
    except BaseException:
        if bau is not None:
            shutil.rmtree(bau, ignore_errors=True)
            if bau.exists():   # R2-02: Rest melden statt verschweigen
                print(f"Warnung: Bauverzeichnis {bau} nicht vollständig entfernt", file=sys.stderr)
        raise
    return ergebnis


def _baue(daten_herkunft, DIST, anzeige, aufraeumen=False):
    """Bau nach DIST (dist/ oder das eigene Bauverzeichnis aus baue()); anzeige: Ziel für die Ausgabezeile;
    aufraeumen nur für dist/."""
    f = (QUELLE / "kaufberatung.html").read_text(encoding="utf-8")
    pruefe_fragment(f)
    herkunft = json.loads((QUELLE / "herkunft.json").read_text(encoding="utf-8"))
    # Kopfangaben des Fragments stehen jetzt im <head>: doppelte Zeichensatz-/Titelzeile herausnehmen (genau einmal)
    for alt in ('<meta charset="utf-8">\n', "<title>Kaufberatung</title>\n"):
        assert f.count(alt) == 1, f"Anker {alt.strip()!r} {f.count(alt)}-mal"
        f = f.replace(alt, "", 1)
    if aufraeumen and DIST.exists():   # A1: nur dist/ wird aufgeräumt, nie ein eigenes Ziel
        for p in DIST.iterdir():
            if p.name in BEHALTEN:
                continue
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    (DIST / "icons").mkdir(parents=True, exist_ok=True)
    # Produktdaten zuerst: ein Fehler im Datenbestand bricht den Bau ab, bevor eine Seite entsteht
    _, fehler, _ = datenbank.bauen(DIST / "finder-daten.json", herkunft=daten_herkunft)
    assert not fehler, f"Produktdaten: {len(fehler)} Fehler (python -I werkzeuge/datenbank.py pruefen)"
    v = versionshash(f, (DIST / "finder-daten.json").read_bytes())
    for d in STATISCH:
        shutil.copyfile(APP / d, DIST / d)
    for d in FINDER:
        shutil.copyfile(APP / "finder" / d, DIST / d)
    ratgeber = KOPF.replace("{V}", v) + f + FUSS.replace("{V}", v)
    (DIST / "ratgeber.html").write_text(ratgeber, encoding="utf-8", newline="\n")
    finder = finder_seite(v)
    (DIST / "index.html").write_text(finder, encoding="utf-8", newline="\n")
    dateien = (["./", "index.html", "ratgeber.html", f"app.js?v={v}", f"app.css?v={v}"]
               + [f"{d}?v={v}" for d in FINDER] + [d for d in STATISCH if d not in ("app.js", "app.css")])
    sw = (APP / "sw.js").read_text(encoding="utf-8")
    for anker, neu in (('"__VERSION__"', json.dumps(v)), ("__DATEIEN__", json.dumps(dateien))):
        assert sw.count(anker) == 1, f"sw.js: Anker {anker} {sw.count(anker)}-mal"
        sw = sw.replace(anker, neu)
    (DIST / "sw.js").write_text(sw, encoding="utf-8", newline="\n")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    if not (DIST / "finder-preise.json").exists():
        # Leerer Startstand, bis der Preislauf eigene Preise schreibt (vermeidet 404 im Finder); veroeffentlichen.py
        # überschreibt eine vorhandene Datei auf gh-pages nie
        (DIST / "finder-preise.json").write_text('{"stand": null, "preise": {}}' + chr(10), encoding="utf-8")
    (DIST / "version.json").write_text(json.dumps({"app": v, "inhalt": herkunft["version"], "inhalt_sha256": herkunft["sha256"]},
                                                  ensure_ascii=False) + "\n", encoding="utf-8")
    for seite in (ratgeber, finder):
        assert not re.search(r"(api[_-]?key|token|secret)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}", seite, re.I), "möglicher Schlüssel im Ergebnis"
    groesse = (DIST / "finder-daten.json").stat().st_size
    print(f"gebaut: {anzeige} · App {v} · Inhalt {herkunft['version']} · ratgeber.html {len(ratgeber.encode('utf-8')):,} Bytes"
          f" · finder-daten.json {groesse:,} Bytes")
    return v


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--quelle", help="fertige kaufberatung.html (Fragment oder gespeicherte Live-Seite)")
    a.add_argument("--version", help='Bezeichnung der Inhaltsfassung, z. B. "Artifact-Version 9"')
    a.add_argument("--ziel", help="Ausgabeverzeichnis statt dist/ (veroeffentlichen.py, R3-01/R5-04)")
    a.add_argument("--herkunft", help="Commit für finder-daten.json (veroeffentlichen.py, R2-02)")
    x = a.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if x.quelle:
        uebernehmen(x.quelle, x.version)
    baue(daten_herkunft=x.herkunft, ziel=x.ziel)


if __name__ == "__main__":
    main()
