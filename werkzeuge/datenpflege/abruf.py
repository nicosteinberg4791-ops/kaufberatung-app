# -*- coding: utf-8 -*-
"""Gemeinsamer Abrufhelfer für die Datenpflege-Subagenten (werkzeuge/datenpflege/abruf.py).

Aufruf:  python -I abruf.py <https-URL> [--text N]
- Je Domain höchstens 1 Abruf pro 60 s, über ALLE parallel laufenden Agenten (Dateisperre + Zeitstempel je Domain).
  Wartet bei Bedarf selbst; nie umgehen.
- robots.txt wird geprüft (einmal je Domain, zählt als Abruf); Saturn-/MediaMarkt-Platzhalterregeln zusätzlich.
- 403/429/503/Captcha: Abbruch mit Exit 3. Nicht wiederholen, nicht umgehen; die Domain für 30 min meiden (Sperrdatei).
- Ausgabe: JSON mit Status, gespeicherter Datei (HTML), Produkten aus JSON-LD (Name, Marke, MPN, GTIN, Preis, Verkäufer)
  und optional den ersten N Zeichen des sichtbaren Textes (--text N).
"""
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.robotparser
from pathlib import Path

WERKZEUGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WERKZEUGE))
import shopabfrage as sa  # noqa: E402

import tempfile  # noqa: E402
HIER = Path(tempfile.gettempdir()) / "kb-datenpflege"   # Takt, Sperren, abgerufene Seiten (nie im Repo)
TAKT = HIER / "takt"
ABLAGE = HIER / "abrufe"
TAKT.mkdir(parents=True, exist_ok=True)
ABLAGE.mkdir(parents=True, exist_ok=True)
ABSTAND = 61
GESPERRT_PFADE = [r"/de/search", r"/de/list/", r"/de/promo-list/", r"storeId=", r"/rest/", r"\.json(\?|$)"]


def sperre_holen(domain):
    """Exklusive Sperre je Domain (Datei per O_EXCL), wartet bis frei; danach Abstand seit dem letzten Abruf einhalten."""
    lock = TAKT / (domain + ".lock")
    start = time.time()
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > 300:   # verwaiste Sperre
                    lock.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.time() - start > 1800:
                raise SystemExit("Zeitüberschreitung beim Warten auf " + domain)
            time.sleep(2)
    stempel = TAKT / (domain + ".zeit")
    if stempel.exists():
        warte = ABSTAND - (time.time() - float(stempel.read_text() or 0))
        if warte > 0:
            time.sleep(warte)
    return lock, stempel


def gesperrt_bis(domain):
    s = TAKT / (domain + ".gesperrt")
    if s.exists() and time.time() - s.stat().st_mtime < 1800:
        return s.read_text(encoding="utf-8")
    return None


def holen(url):
    """Ein Abruf im Takt. Rückgabe (status, text, inhaltstyp) oder SystemExit(3) bei Sperre."""
    domain = urllib.parse.urlsplit(url).hostname
    grund = gesperrt_bis(domain)
    if grund:
        print(json.dumps({"url": url, "fehler": "Domain gesperrt (30 min meiden): " + grund}, ensure_ascii=False))
        raise SystemExit(3)
    lock, stempel = sperre_holen(domain)
    try:
        grund = gesperrt_bis(domain)   # Vorprüfung 1: Sperre kann während des Wartens entstanden sein
        if grund:
            print(json.dumps({"url": url, "fehler": "Domain gesperrt (30 min meiden): " + grund}, ensure_ascii=False))
            raise SystemExit(3)
        try:
            r = sa.abrufen(url)
        finally:
            stempel.write_text(str(time.time()))
    except sa.Weitergeleitet as e:
        print(json.dumps({"url": url, "fehler": "Weiterleitung, nicht verfolgt: " + str(e)}, ensure_ascii=False))
        raise SystemExit(5)
    except sa.NichtAbrufbar as e:
        if re.search(r"HTTP (401|403|429|503)|Challenge|Bot", str(e)):
            (TAKT / (domain + ".gesperrt")).write_text(str(e), encoding="utf-8")
            print(json.dumps({"url": url, "fehler": "gesperrt (nicht umgehen, Domain 30 min meiden): " + str(e)}, ensure_ascii=False))
            raise SystemExit(3)
        print(json.dumps({"url": url, "fehler": "nicht abrufbar: " + str(e)}, ensure_ascii=False))
        raise SystemExit(6)
    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass
    return r


def robots_ok(url):
    teile = urllib.parse.urlsplit(url)
    for m in GESPERRT_PFADE:
        if re.search(m, teile.path + ("?" + teile.query if teile.query else "")):
            return False, "Pfad laut robots-Regel gesperrt: " + m
    domain = teile.hostname
    ablage = TAKT / (domain + ".robots")
    if not ablage.exists():
        try:
            text = holen(f"{teile.scheme}://{domain}/robots.txt")
        except SystemExit as e:
            if e.code == 3:   # Sperre (403/429/Captcha) an den Aufrufer weitergeben, nicht verschlucken
                raise
            return False, "robots.txt nicht abrufbar"
        ablage.write_text(text or "", encoding="utf-8")
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(ablage.read_text(encoding="utf-8").splitlines())
    if not rp.can_fetch("*", url):
        return False, "robots.txt verbietet den Pfad"
    if "proshop" in domain and teile.query and not teile.query.startswith(("pn=", "s=")):
        return False, "Proshop: Abfragen mit ? gesperrt"
    return True, ""


def sichtbarer_text(t):
    t = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or not sys.argv[1].startswith("https://"):
        print(__doc__)
        return 2
    url = sys.argv[1]
    n_text = int(sys.argv[sys.argv.index("--text") + 1]) if "--text" in sys.argv else 0
    ok, grund = robots_ok(url)
    if not ok:
        print(json.dumps({"url": url, "fehler": grund}, ensure_ascii=False))
        return 4
    text = holen(url)
    status = 200
    datei = ABLAGE / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".html")
    datei.write_text(text or "", encoding="utf-8")
    prod = []
    for b in sa.jsonld_bloecke(text or ""):
        for p in sa.produkte(b):
            angebote = sa.angebote_von(p)
            prod.append({"name": p.get("name"), "marke": (p.get("brand") or {}).get("name") if isinstance(p.get("brand"), dict) else p.get("brand"),
                         "mpn": p.get("mpn"), "gtin": sorted(sa.eans(p)), "url": p.get("url"),
                         "angebote": [{"preis": sa.preis_von(o), "verkaeufer": sa.verkaeufer_von(o),
                                       "verfuegbar": o.get("availability")} for o in angebote][:5]})
    aus = {"url": url, "status": status, "datei": str(datei), "bytes": len(text or ""), "produkte_jsonld": prod[:30]}
    # Saturn/MediaMarkt-Produktseite: eigenes Angebot nur mit Nachweis im eingebetteten Preisfeld (sonst Marktplatz/unklar)
    m = re.search(r"/de/product/[^/]*-(\d+)\.html", url)
    if m and ("saturn.de" in url or "mediamarkt.de" in url):
        praefix = "Saturn:de:" if "saturn.de" in url else "Media:de:"
        f = sa.mms_preisfeld(text or "", praefix, m.group(1))
        aus["saturn_eigenes_angebot"] = (None if f is None else
                                         {"marktplatz": f[0], "preis": f[1], "versand": f[2],
                                          "als_preis_nutzbar": (f[0] is False and f[1] is not None)})
    if n_text:
        aus["text"] = sichtbarer_text(text or "")[:n_text]
    print(json.dumps(aus, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
