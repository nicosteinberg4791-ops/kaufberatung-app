# -*- coding: utf-8 -*-
"""Herkunft der veröffentlichten finder-daten.json (Codex r2 R2-02/R2-07): darf ein neuer Stand die Online-Datei ersetzen?

Jede gebaute finder-daten.json trägt `herkunft` = Commit, aus dem sie gebaut wurde (datenbank.py bauen --herkunft).
Ersetzt wird nur, wenn die Online-Herkunft gleich dem neuen Commit oder sein Vorfahr ist (der neue Stand enthält dann
alles, was online ist). Online-Datei ohne, mit ungültiger oder unbekannter Herkunft → Abbruch (Reihenfolge ungeklärt,
nie automatisch zurücksetzen, D11). Fehlt die Online-Datei oder ist sie kein JSON, darf ersetzt werden.

Aufruf:  python -I werkzeuge/herkunft.py pruefen <online.json> <neuer-commit> [<git-ordner>]
         Exit 0 = ersetzen erlaubt (auch wenn die Datei fehlt), 1 = nicht ersetzen, 2 = Aufruf falsch.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")


def fehler(online_text, neu, ist_vorfahr):
    """Grund gegen das Ersetzen oder None. ist_vorfahr(alt, neu) -> bool (alt ist Vorfahr von neu oder gleich und beide
    sind vorhandene Commits; ist_vorfahr(x, x) heißt also: Commit x ist vorhanden)."""
    # R3-05: der neue Stand wird immer zuerst geprüft (Format und vorhandenes Commit), auch ohne Online-Datei
    if not isinstance(neu, str) or not SHA.match(neu):
        return "neuer Stand ohne gültige Herkunft (40 Hex-Zeichen)"
    if not ist_vorfahr(neu, neu):
        return f"neuer Stand {neu[:12]} ist kein vorhandener Commit"
    if online_text is None:
        return None
    try:
        online = json.loads(online_text)
    except ValueError:
        return None   # unlesbare Online-Datei darf ersetzt werden
    alt = online.get("herkunft") if isinstance(online, dict) else None
    if not isinstance(alt, str) or not SHA.match(alt):
        return "Online-Datei ohne gültige Herkunft: Reihenfolge ungeklärt, nicht ersetzen"
    if ist_vorfahr(alt, neu):   # gleiche SHAs laufen durch dieselbe Git-Prüfung (R3-05)
        return None
    return f"Online-Stand {alt[:12]} ist nicht im neuen Stand {neu[:12]} enthalten (neuer oder abweichend): nicht ersetzen"


def git_vorfahr(ordner):
    def ist_vorfahr(alt, neu):
        r = subprocess.run(["git", "-C", str(ordner), "merge-base", "--is-ancestor", alt, neu],
                           capture_output=True, text=True)
        return r.returncode == 0   # 1 = kein Vorfahr, 128 = unbekanntes Objekt → beides nein
    return ist_vorfahr


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) not in (3, 4) or a[0] != "pruefen":
        print(__doc__)
        return 2
    datei = Path(a[1])
    text = datei.read_text(encoding="utf-8") if datei.exists() else None
    grund = fehler(text, a[2].strip().lower(), git_vorfahr(a[3] if len(a) == 4 else "."))
    if grund:
        print("Abbruch:", grund)
        return 1
    print("Herkunft ok: ersetzen erlaubt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
