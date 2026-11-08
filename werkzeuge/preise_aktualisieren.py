# -*- coding: utf-8 -*-
"""Schreibt preise.json für die App aus der täglichen Preisabfrage (werkzeuge/preiswecker.py, Stand R4 aus Runde 6),
optional mit Push auf gh-pages und Text für die ntfy-Benachrichtigung. Läuft täglich in GitHub Actions
(.github/workflows/preise.yml), lokal nur zum Testen.

Die Rechenlogik (günstigster Gesamtpreis mit belegtem Versand, Tiefstpreis, Verlauf 60 Tage, Treffer) bleibt in
preiswecker.py und wird hier nur aufgerufen: preise.json ist dieselbe Datenform wie die db-Dokumente "preise/<id>" und
"wecker/lauf". Die alten Einträge gehen mit "version": 1 als Export in einen Temp-Ordner, abgleich() läuft mit
anlegen=True (preise.json ist die einzige Quelle; ein Modell ohne alten Eintrag wird neu angelegt).

Wunschpreise (optional) nur aus der Umgebungsvariable WUNSCHPREISE (JSON {"lg_c6elb": 2500, ...}, in Actions das
Secret gleichen Namens). Sie erscheinen NIE in preise.json und nie auf stdout (Actions-Logs sind öffentlich), nur im
Benachrichtigungstext (--meldung). Ob ein Treffer neu ist, folgt aus dem gestrigen Preis in preise.json (je Ereignis
eine Meldung, ohne gespeicherten Wunschpreis).

Aufrufe:
  python -X utf8 -I werkzeuge/preise_aktualisieren.py                       neu abrufen, .veroeffentlichung/preise.json schreiben
  python -X utf8 -I werkzeuge/preise_aktualisieren.py --abruf abruf.json    vorhandenes Abrufergebnis (stdout von preiswecker.py)
  ... --ziel dist/preise.json                                               anderes Ziel (lokaler Test)
  ... --push                                                                im gh-pages-Arbeitsbaum committen und pushen
  ... --nur-push                                                            vorhandene preise.json im Arbeitsbaum pushen
  ... --meldung datei.txt                                                   Benachrichtigungstext, ein Treffer je Zeile (leer = keine Meldung)
Workflow-Reihenfolge (Codex R1 B2): schreiben -> ntfy senden -> erst dann --nur-push. Scheitert der Versand, bleibt der
alte Stand online und der nächste Lauf erkennt dasselbe Ereignis erneut (mindestens einmal statt höchstens einmal).
  ... --skript <pfad/preiswecker.py>                                        anderes Skript (Tests)
Exitcode 3, wenn kein einziges Modell gelesen wurde (Status "fehler", z. B. heise gesperrt); preise.json ist dann
trotzdem geschrieben (alte Preise, Laufstatus "fehler"), damit die App den Fehler zeigt.
Nur Standardbibliothek.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SEITEN = WURZEL / ".veroeffentlichung"   # git worktree auf dem Zweig gh-pages (veroeffentlichen.py bzw. Workflow)
SKRIPT = WURZEL / "werkzeuge" / "preiswecker.py"


def lade_skript(pfad):
    p = Path(pfad) if pfad else SKRIPT
    if not p.exists():
        raise SystemExit(f"preiswecker.py nicht gefunden: {p}")
    spec = importlib.util.spec_from_file_location("preiswecker", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, p


def zahl_ok(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and 0 < x < 100000


def lies_wunsch(text, modelle):
    """WUNSCHPREISE-Text -> {id: preis}; Ungültiges wird ohne Wert gemeldet und übergangen."""
    if not text or not text.strip():
        return {}
    try:
        roh = json.loads(text)
    except ValueError:
        print("WARNUNG: WUNSCHPREISE ist kein JSON, Wunschpreise ignoriert", file=sys.stderr)
        return {}
    if not isinstance(roh, dict):
        print("WARNUNG: WUNSCHPREISE ist kein Objekt, Wunschpreise ignoriert", file=sys.stderr)
        return {}
    wunsch = {}
    for k, v in roh.items():
        if k in modelle and zahl_ok(v):
            wunsch[k] = float(v)
        else:
            print("WARNUNG: ein Eintrag in WUNSCHPREISE ist unbekannt oder keine gültige Zahl, übergangen", file=sys.stderr)
    return wunsch


def schreibe_doc(ordner, doc_id, felder):
    ordner.mkdir(parents=True, exist_ok=True)
    (ordner / f"{doc_id}.json").write_text(json.dumps(felder | {"version": 1}, ensure_ascii=False), encoding="utf-8")


def oeffentlicher_lauftext(text, treffer):
    """Laufmeldung ohne Wunschpreis-Treffer (die verraten den Wunschpreis); Tiefstpreis-Treffer bleiben."""
    i = text.find("Treffer:")
    text = (text[:i] if i >= 0 else text).strip()
    oeff = [t for t in treffer if "Wunschpreis" not in t]
    if oeff:
        text = (text + " Treffer: " + "; ".join(oeff) + ".").strip()
    return text[:300]


def aktualisiere(pw, erg, ziel, wunsch=None):
    wunsch = wunsch or {}
    alt = {}
    if ziel.exists():
        try:
            alt = json.loads(ziel.read_text(encoding="utf-8"))
        except ValueError:
            alt = {}
    if not isinstance(alt, dict):
        alt = {}
    alt_preise = alt.get("preise") if isinstance(alt.get("preise"), dict) else {}
    with tempfile.TemporaryDirectory() as tmp:
        db, aus = Path(tmp, "db"), Path(tmp, "aus")
        for mid, doc in alt_preise.items():
            if mid in pw.MODELLE and isinstance(doc, dict):
                felder = {k: v for k, v in doc.items() if k not in ("meldung", "version")}
                if mid in wunsch:   # gestriger Stand: war der Preis schon unter dem (heutigen) Wunschpreis?
                    g_alt = (doc.get("aktuell") or {}).get("gesamt") if isinstance(doc.get("aktuell"), dict) else None
                    felder["meldung"] = {"unter_wunsch": bool(zahl_ok(g_alt) and g_alt <= wunsch[mid]), "wunsch": wunsch[mid]}
                schreibe_doc(db / "preise", mid, felder)
        for mid, wp in wunsch.items():
            schreibe_doc(db / "wunsch", mid, {"preis": wp})
        bericht = pw.abgleich(erg, str(db), str(aus), anlegen=True)
        preise = {}
        for mid in pw.MODELLE:
            f = aus / f"preise_{mid}.json"
            if f.exists():
                d = json.loads(f.read_text(encoding="utf-8"))
                d.pop("meldung", None)       # enthält den Wunschpreis: nie veröffentlichen
                preise[mid] = d
            elif mid in alt_preise and isinstance(alt_preise[mid], dict):
                d = dict(alt_preise[mid])      # heute kein belegtes Angebot: letzten Stand behalten
                d.pop("meldung", None)
                preise[mid] = d
        lauf = json.loads((aus / "wecker_lauf.json").read_text(encoding="utf-8"))
    lauf["meldung"] = oeffentlicher_lauftext(lauf.get("meldung", ""), bericht["treffer"])
    for mid, d in preise.items():
        g = (d.get("aktuell") or {}).get("gesamt")
        assert zahl_ok(g), f"{mid}: Gesamtpreis {g!r} unplausibel"
    neu = {"format": 1, "zeit": erg["zeit"], "quelle": "heise-Preisvergleich, günstigster Gesamtpreis mit belegtem Versand",
           "preise": preise, "lauf": lauf}
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps(neu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return bericht, lauf


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


def meldetext(treffer):
    """Alle Treffer vollständig, eine Zeile je Treffer (Codex R1 B1: der R4-Text "push" ist auf 195 Zeichen gekürzt).
    Fünf Modelle mit je zwei Treffern ergeben unter 600 Zeichen; ntfy nimmt bis 4096 Byte als Text."""
    return "\n".join(treffer)


def uebersicht(erg):
    """Je Modell nur Angebotszahl oder Fehler (für das öffentliche Log; zeigt z. B. eine heise-Sperre)."""
    return {mid: (r.get("fehler") if r.get("fehler") else f"{r.get('angebote', '?')} Angebote")
            for mid, r in erg["modelle"].items() if isinstance(r, dict)}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--abruf", help="JSON-Ausgabe von preiswecker.py (ohne Argumente); sonst wird neu abgerufen")
    a.add_argument("--ziel", default=str(SEITEN / "preise.json"))
    a.add_argument("--skript")
    a.add_argument("--push", action="store_true")
    a.add_argument("--nur-push", action="store_true",
                   help="nichts abrufen: die vorhandene preise.json im gh-pages-Arbeitsbaum committen und pushen")
    a.add_argument("--meldung", help="Datei für den Benachrichtigungstext (wird immer geschrieben, leer = keine Meldung)")
    x = a.parse_args()
    if x.nur_push or x.push:   # vor allem anderen: nur der gh-pages-Arbeitsbaum, nur preise.json
        ziel = Path(x.ziel)
        assert ziel.parent.resolve() == SEITEN.resolve() and ziel.name == "preise.json", "--push nur mit dem gh-pages-Arbeitsbaum"
        arbeitsbaum_pruefen(ziel.parent)
    if x.nur_push:
        push(Path(x.ziel))
        return
    pw, pfad = lade_skript(x.skript)
    wunsch = lies_wunsch(os.environ.get("WUNSCHPREISE", ""), pw.MODELLE)
    erg = json.loads(Path(x.abruf).read_text(encoding="utf-8")) if x.abruf else pw.abruf_alle()
    assert isinstance(erg, dict) and isinstance(erg.get("modelle"), dict) and isinstance(erg.get("zeit"), str), "Abrufergebnis ungültig"
    ziel = Path(x.ziel)
    bericht, lauf = aktualisiere(pw, erg, ziel, wunsch)
    text = meldetext(bericht["treffer"])
    if x.meldung:
        Path(x.meldung).write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"skript": str(pfad), "ziel": str(ziel), "status": bericht["status"], "wunschpreise": len(wunsch),
                      "meldung": len(bericht["treffer"]), "modelle": uebersicht(erg), "lauf": lauf["meldung"]},
                     ensure_ascii=False))
    if x.push:
        push(ziel)
    if bericht["status"] == "fehler":
        sys.exit(3)


if __name__ == "__main__":
    main()
