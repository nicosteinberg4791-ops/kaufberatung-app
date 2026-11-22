# -*- coding: utf-8 -*-
"""Entdeckung neuer Modelle (D10): Saturn-Kategorieseiten gegen den Bestand abgleichen.

Aufruf:  python -I -X utf8 werkzeuge/entdeckung.py [--kategorie fernseher,laptop] [--seiten 3]

- Je Kategorie höchstens 3 Listenseiten (`/de/category/…`, `?page=N`), alle Abrufe über werkzeuge/datenpflege/abruf.py
  (≥ 61 s je Domain über alle Prozesse, robots.txt, Sperre bei 403/429 → Lauf endet sofort, nicht umgehen).
- Höchstens einmal je Kategorie in 6 Tagen (wöchentlich, D10); die Sperre steht im Ergebnis selbst und ist nicht abschaltbar.
  Sie wird vor dem ersten Abruf der Kategorieseite reserviert („versucht“), gilt also auch bei leerem oder fehlerhaftem
  Ergebnis (F-05). Ein zweiter Lauf zur selben Zeit endet sofort (Betriebssystem-Dateisperre neben der Ergebnisdatei,
  frei beim Prozessende, Exit 4, R2-06). Unlesbare Ergebnisdatei oder unlesbarer Zeitstempel sperrt (R2-05).
- Abgleich gegen daten/produkte/*.json über EAN, MPN (im Namen) und Hersteller + Modellname.
- Gespeichert werden nur Name, URL und Saturn-Nummer der Kandidaten (§ 87b UrhG: kein Spiegeln, keine Preise, keine
  Datenblätter) in `%TEMP%/kb-datenpflege/entdeckung/kandidaten.json` (für alle Arbeitsbäume gleich, nie im Repo). Die Datenpflege-Routine (D11) liest die Datei,
  belegt die Werte auf Produktseiten nach werkzeuge/datenpflege/ANLEITUNG.md und trägt kuratiert ein.
Exit: 0 ok · 3 Domain gesperrt (Lauf abgebrochen, Teilergebnis gespeichert) · 4 anderer Lauf aktiv · 2 Aufruffehler.
"""
import datetime as dt
import json
import re
import sys
import urllib.parse
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "werkzeuge" / "datenpflege"))
sys.path.insert(0, str(WURZEL / "werkzeuge"))

PRODUKTE = WURZEL / "daten" / "produkte"
# Fester Ort für alle Arbeitsbäume (Vorprüfung 6), neben Takt und Sperren von abruf.py; nie im Repo
import tempfile  # noqa: E402
ZIEL = Path(tempfile.gettempdir()) / "kb-datenpflege" / "entdeckung" / "kandidaten.json"
MAX_SEITEN = 3
MIN_TAGE = 6
SATURN = "https://www.saturn.de/de/category/"

# Kategorie der App → Saturn-Kategorieseite (ermittelt am 22.11.2026 aus sitemap-productlistpages.xml und Navigation)
KATEGORIEN = {
    "fernseher": "4k-fernseher-2301.html",
    "akkusauger": "akkuhandstaubsauger-1582.html",
    "saugroboter": "saugroboter-1297.html",
    "airfryer": "hei%C3%9Fluftfriteuse-1727.html",
    "smartphone": "handys-ohne-vertrag-494.html",
    "tablet": "tablets-122.html",
    "laptop": "notebooks-2013.html",
    "kopfhoerer_inear": "in-ear-kopfh%C3%B6rer-1139.html",
    "kopfhoerer_overear": "over-ear-kopfh%C3%B6rer-1140.html",
    "soundbar": "soundbars-soundbases-1112.html",
    "waschmaschine": "waschmaschinen-1202.html",
    "trockner": "trockner-1515.html",
    "kuehlschrank": "k%C3%BChlschr%C3%A4nke-1235.html",
    "geschirrspueler": "geschirrsp%C3%BCler-1214.html",
}


# Abgleich nach Namen (geprüft an der Entdeckung vom 22.11.2026): Shoptitel schreiben Ordinalzahlen („3rd generation“),
# deutsche statt englische Gattungswörter, „™“/„TM“ am Namen und MPNs ohne Länderendung („/ZG“, „-DEUR“).
SYNONYME = {"kopfhoerer": "headphones", "headphones": "kopfhoerer", "serie": "series", "series": "serie"}
FUELLWOERTER = {"serie", "series", "gen", "generation"}   # zählen im Bestandsnamen nur, wenn sonst keine Modellnummer bleibt
ORDINAL = re.compile(r"^(\d+)(st|nd|rd|th)$")


def _klein(t):
    t = str(t or "").lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        t = t.replace(a, b)
    return t


def norm(t):
    """Kleinbuchstaben, nur a-z0-9 (für MPN-Vergleich)."""
    return re.sub(r"[^a-z0-9]", "", _klein(t))


def woerter(t):
    """Wortmenge mit Zusatzformen: ohne führende Ziffern (55e7s → e7s), Ordinalzahl als Zahl (3rd → 3),
    ohne angehängtes TM (detecttm → detect) und Synonyme (kopfhoerer ↔ headphones)."""
    out = set()
    for w in re.findall(r"[a-z0-9]+", _klein(t)):
        out.add(w)
        ohne = w.lstrip("0123456789")
        if ohne and ohne != w and re.search(r"\d", ohne):
            out.add(ohne)
        m = ORDINAL.match(w)
        if m:
            out.add(m.group(1))
        if len(w) > 4 and w.endswith("tm"):
            out.add(w[:-2])
        if w in SYNONYME:
            out.add(SYNONYME[w])
    return out


def namens_woerter(t):
    """Wörter eines Bestandsnamens ohne Füllwörter, solange eine Modellnummer (Wort mit Ziffer) übrig bleibt."""
    w = woerter(t)
    rest = w - FUELLWOERTER
    return rest if any(re.search(r"\d", x) for x in rest) else w


def mpn_schluessel(mpn):
    """Normierte MPN (≥ 5 Zeichen) und, falls vorhanden, ihr Stamm ohne Länderendung (/ZG, /00, -DEUR; ≥ 6 Zeichen)."""
    roh = str(mpn or "")
    out = {norm(roh)} if len(norm(roh)) >= 5 else set()
    stamm = re.sub(r"-[A-Za-z]{2,4}$", "", roh.split("/")[0])
    if len(norm(stamm)) >= 6:
        out.add(norm(stamm))
    return out


def bestand_index(produkte=PRODUKTE):
    """Je Kategorie: EANs, MPNs (normiert, mit Stamm) und Modelle (Hersteller-Wörter, Namens-Wörter, ID)."""
    idx = {}
    for p in sorted(Path(produkte).glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        k = idx.setdefault(d["kategorie"], {"ean": {}, "mpn": {}, "modelle": []})
        for m in d.get("modelle", []):
            k["modelle"].append((woerter(m.get("hersteller")), namens_woerter(m.get("name")), m["id"]))
            for v in m.get("varianten", []):
                for e in v.get("ean", []) or []:
                    k["ean"][str(e)] = m["id"]
                for schluessel in mpn_schluessel(v.get("mpn")):
                    k["mpn"][schluessel] = m["id"]
    return idx


def mpn_im_namen(mpn, n):
    """MPN kommt im normierten Namen vor und endet dort nicht mitten in einer Zahl (na351 ≠ na3510)."""
    i = n.find(mpn)
    while i >= 0:
        nach = n[i + len(mpn):i + len(mpn) + 1]
        if not (nach.isdigit() and mpn[-1].isdigit()):
            return True
        i = n.find(mpn, i + 1)
    return False


def zuordnen(eintrag, k):
    """Modell-ID aus dem Bestand oder None (= Kandidat). eintrag: {name, gtin[]}."""
    for e in eintrag.get("gtin", []):
        if e in k["ean"]:
            return k["ean"][e]
    n = norm(eintrag.get("name"))
    for mpn, mid in k["mpn"].items():
        if mpn_im_namen(mpn, n):
            return mid
    w = woerter(eintrag.get("name"))
    # das spezifischste Bestandsmodell gewinnt (QuietComfort Ultra Headphones vor QuietComfort Headphones)
    passend = [(len(name), mid) for hersteller, name, mid in k["modelle"] if name and hersteller and (hersteller & w) and name <= w]
    return max(passend, key=lambda x: x[0])[1] if passend else None


def itemlist(text):
    """Produkte aus JSON-LD-ItemList: [{name, url, gtin[]}] (Preise und Bewertungen werden bewusst nicht übernommen)."""
    import shopabfrage as sa
    out = []
    for b in sa.jsonld_bloecke(text or ""):
        for blk in (b if isinstance(b, list) else [b]):
            if not isinstance(blk, dict) or "ItemList" not in str(blk.get("@type")):
                continue
            for li in blk.get("itemListElement") or []:
                it = li.get("item", li) if isinstance(li, dict) else {}
                if not isinstance(it, dict) or not it.get("name"):
                    continue
                url = str(it.get("url") or "")
                if not url.startswith("https://www.saturn.de/de/product/"):
                    continue
                out.append({"name": str(it["name"])[:200], "url": url, "gtin": sorted(sa.eans(it))})
    return out


def saturn_nr(url):
    m = re.search(r"-(\d+)\.html$", urllib.parse.urlsplit(url).path)
    return m.group(1) if m else None


def laden(ziel=ZIEL):
    """Ergebnisdatei lesen. Fehlt sie: leer. Ist sie unlesbar: Merker _unlesbar (sperrt den Lauf, R2-05)."""
    try:
        erg = json.loads(Path(ziel).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"kategorien": {}}
    except (OSError, ValueError):
        return {"kategorien": {}, "_unlesbar": True}
    return erg if isinstance(erg, dict) else {"kategorien": {}, "_unlesbar": True}


def speichern(erg, ziel):
    """Atomar schreiben (Temp-Datei + os.replace), damit ein Abbruch die Wochensperre nicht zurücksetzt."""
    import os
    Path(ziel).parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(ziel) + ".tmp")
    tmp.write_text(json.dumps(erg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, ziel)


def zu_frueh(alt, kat, jetzt):
    """Letzter Abruf oder Abrufversuch (F-05) vor weniger als MIN_TAGE. Jedes vorhandene Feld, das kein lesbarer
    Zeitstempel ist (auch "", 0, false, null), und ein Eintrag, der kein Objekt ist, zählen als gesperrt (R2-05)."""
    kats = alt.get("kategorien", {})
    if not isinstance(kats, dict):
        return True
    if kat not in kats:
        return False
    k = kats[kat]
    if not isinstance(k, dict):
        return True
    for feld in ("abgerufen", "versucht"):
        if feld not in k:
            continue
        t = k[feld]
        try:
            if not isinstance(t, str):
                raise TypeError(feld)
            if jetzt - dt.datetime.fromisoformat(t) < dt.timedelta(days=MIN_TAGE):
                return True
        except (ValueError, TypeError):
            print(f"{kat}: Zeitstempel {feld}={t!r} unlesbar – gesperrt (D10)")
            return True
    return False


def sperre_holen(ziel):
    """Exklusive Laufsperre als Betriebssystem-Dateisperre auf der offen gehaltenen Datei <ziel>.lock (R2-06): genau ein
    Inhaber, frei beim Prozessende (auch nach Absturz), kein Altern und kein Löschen. Rückgabe Dateiobjekt oder None."""
    import os
    sperre = Path(str(ziel) + ".lock")
    sperre.parent.mkdir(parents=True, exist_ok=True)
    f = open(sperre, "a+b")
    try:
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return None
    return f


def sperre_freigeben(f):
    """Sperre lösen und Datei schließen (die Datei bleibt liegen; sie sperrt ohne Inhaber nichts)."""
    import os
    try:
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass
    finally:
        f.close()


def lauf(kats, seiten, holen, robots_ok, ziel=ZIEL, produkte=PRODUKTE, jetzt=None):
    """Kern ohne Netz (holen/robots_ok werden übergeben, für Tests ersetzbar). Rückgabe (ergebnis, exitcode)."""
    jetzt = jetzt or dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    sperre = sperre_holen(ziel)
    if sperre is None:
        print("Ein anderer Entdeckungslauf ist aktiv: nichts abgerufen (D10)")
        return laden(ziel), 4
    try:
        return _lauf(kats, seiten, holen, robots_ok, ziel, produkte, jetzt)
    finally:
        sperre_freigeben(sperre)


def _lauf(kats, seiten, holen, robots_ok, ziel, produkte, jetzt):
    idx = bestand_index(produkte)
    erg = laden(ziel)   # erst unter der Laufsperre lesen
    if erg.get("_unlesbar"):
        print(f"Ergebnisdatei {Path(ziel).name} unlesbar: nichts abgerufen, Datei bleibt (erst prüfen, D10)")
        return erg, 4
    erg.setdefault("kategorien", {})
    code = 0
    for kat in kats:
        if zu_frueh(erg, kat, jetzt):
            print(f"{kat}: übersprungen (letzter Abruf vor weniger als {MIN_TAGE} Tagen, D10)")
            continue
        basis = SATURN + KATEGORIEN[kat]
        kand, bekannt, fehler, gesehen = {}, {}, [], set()
        for s in range(1, seiten + 1):
            url = basis if s == 1 else f"{basis}?page={s}"
            try:
                ok, grund = robots_ok(url)
            except SystemExit as e:
                ok, grund = False, f"robots.txt: Abruf abgebrochen (Exit {e.code})"
                code = 3 if e.code == 3 else code
            if not ok:
                fehler.append(f"Seite {s}: {grund}")
                break
            if s == 1:
                # F-05: Versuch vor dem ersten Abruf der Kategorie festhalten (Sperre gilt auch ohne Ergebnis)
                erg["kategorien"].setdefault(kat, {})["versucht"] = jetzt.isoformat()
                speichern(erg, ziel)
            try:
                text = holen(url)
            except SystemExit as e:
                fehler.append(f"Seite {s}: Abruf abgebrochen (Exit {e.code})")
                if e.code == 3:
                    code = 3
                break
            treffer = itemlist(text)
            if not treffer:
                fehler.append(f"Seite {s}: keine ItemList")
                break
            for t in treffer:
                nr = saturn_nr(t["url"]) or t["url"]
                if nr in gesehen:
                    continue
                gesehen.add(nr)
                mid = zuordnen(t, idx.get(kat, {"ean": {}, "mpn": {}, "modelle": []}))
                if mid:
                    bekannt[nr] = mid
                else:
                    kand[nr] = {"name": t["name"], "url": t["url"], "saturn_nr": nr}
        if not gesehen:
            # nichts gelesen: alten Stand und Wochensperre nicht überschreiben (Vorprüfung 7), nur Fehler vermerken
            erg["kategorien"].setdefault(kat, {})["letzter_fehler"] = {"zeit": jetzt.isoformat(), "fehler": fehler}
            print(f"{kat}: nichts gelesen · " + "; ".join(fehler))
            speichern(erg, ziel)
            if code == 3:
                print("Domain gesperrt: Lauf beendet (nicht umgehen, frühestens in 30 min erneut)")
                break
            continue
        erg["kategorien"][kat] = {"abgerufen": jetzt.isoformat(), "versucht": jetzt.isoformat(), "quelle": basis, "seiten": seiten,
                                  "gelesen": len(gesehen), "bekannt": len(bekannt),
                                  "kandidaten": list(kand.values()), "fehler": fehler}
        print(f"{kat}: {len(gesehen)} gelesen · {len(bekannt)} bekannt · {len(kand)} Kandidaten"
              + (" · " + "; ".join(fehler) if fehler else ""))
        speichern(erg, ziel)
        if code == 3:
            print("Domain gesperrt: Lauf beendet (nicht umgehen, frühestens in 30 min erneut)")
            break
    return erg, code


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    argv = list(sys.argv[1:] if argv is None else argv)
    kats = list(KATEGORIEN)
    seiten = MAX_SEITEN
    try:
        if "--kategorie" in argv:
            kats = argv[argv.index("--kategorie") + 1].split(",")
        if "--seiten" in argv:
            seiten = int(argv[argv.index("--seiten") + 1])
    except (IndexError, ValueError):
        print(__doc__)
        return 2
    unbekannt = [k for k in kats if k not in KATEGORIEN]
    if unbekannt or not 1 <= seiten <= MAX_SEITEN:
        print("Unbekannte Kategorie oder Seitenzahl außerhalb 1–3:", unbekannt or seiten)
        return 2
    import abruf
    _, code = lauf(kats, seiten, abruf.holen, abruf.robots_ok)
    print("Ergebnis:", ZIEL)
    return code


if __name__ == "__main__":
    sys.exit(main())
