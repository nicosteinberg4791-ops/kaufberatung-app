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
Nur Standardbibliothek. Jeder Anker wird per assert geprüft.
"""
import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
APP = WURZEL / "app"
QUELLE = WURZEL / "quelle"
DIST = WURZEL / "dist"
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
<meta name="description" content="Private Kaufberatung: Fernseher und Staubsauger, mit Preiswecker.">
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


def baue():
    f = (QUELLE / "kaufberatung.html").read_text(encoding="utf-8")
    pruefe_fragment(f)
    herkunft = json.loads((QUELLE / "herkunft.json").read_text(encoding="utf-8"))
    # Kopfangaben des Fragments stehen jetzt im <head>: doppelte Zeichensatz-/Titelzeile herausnehmen (genau einmal)
    for alt in ('<meta charset="utf-8">\n', "<title>Kaufberatung</title>\n"):
        assert f.count(alt) == 1, f"Anker {alt.strip()!r} {f.count(alt)}-mal"
        f = f.replace(alt, "", 1)
    # Version = Prüfsumme über Inhalt und Hülle: jede Änderung erzeugt einen neuen Service Worker
    h = hashlib.sha256(f.encode("utf-8"))
    for d in STATISCH + ["sw.js"]:
        h.update((APP / d).read_bytes())
    v = h.hexdigest()[:12]
    if DIST.exists():
        for p in DIST.iterdir():
            if p.name == "preise.json":
                continue  # Preise gehören der täglichen Abfrage, nie überschreiben
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    (DIST / "icons").mkdir(parents=True, exist_ok=True)
    for d in STATISCH:
        shutil.copyfile(APP / d, DIST / d)
    seite = KOPF.replace("{V}", v) + f + FUSS.replace("{V}", v)
    (DIST / "index.html").write_text(seite, encoding="utf-8", newline="\n")
    dateien = ["./", "index.html", f"app.js?v={v}", f"app.css?v={v}"] + [d for d in STATISCH if d not in ("app.js", "app.css")]
    sw = (APP / "sw.js").read_text(encoding="utf-8")
    for anker, neu in (('"__VERSION__"', json.dumps(v)), ("__DATEIEN__", json.dumps(dateien))):
        assert sw.count(anker) == 1, f"sw.js: Anker {anker} {sw.count(anker)}-mal"
        sw = sw.replace(anker, neu)
    (DIST / "sw.js").write_text(sw, encoding="utf-8", newline="\n")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "version.json").write_text(json.dumps({"app": v, "inhalt": herkunft["version"], "inhalt_sha256": herkunft["sha256"]},
                                                  ensure_ascii=False) + "\n", encoding="utf-8")
    assert not re.search(r"(api[_-]?key|token|secret)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}", seite, re.I), "möglicher Schlüssel im Ergebnis"
    print(f"gebaut: dist/ · App {v} · Inhalt {herkunft['version']} · index.html {len(seite.encode('utf-8')):,} Bytes")
    return v


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--quelle", help="fertige kaufberatung.html (Fragment oder gespeicherte Live-Seite)")
    a.add_argument("--version", help='Bezeichnung der Inhaltsfassung, z. B. "Artifact-Version 9"')
    x = a.parse_args()
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    if x.quelle:
        uebernehmen(x.quelle, x.version)
    baue()


if __name__ == "__main__":
    main()
