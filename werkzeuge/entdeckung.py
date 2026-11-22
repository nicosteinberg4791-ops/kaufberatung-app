# -*- coding: utf-8 -*-
"""Entdeckung neuer Modelle (D10): Saturn-Kategorieseiten gegen den Bestand abgleichen.

Aufruf:  python -I -X utf8 werkzeuge/entdeckung.py [--kategorie fernseher,laptop] [--seiten 3]

- Je Kategorie höchstens 3 Listenseiten (`/de/category/…`, `?page=N`), alle Abrufe über werkzeuge/datenpflege/abruf.py
  (≥ 61 s je Domain über alle Prozesse, robots.txt, Sperre bei 403/429 → Lauf endet sofort, nicht umgehen).
- Höchstens einmal je Kategorie in 6 Tagen (wöchentlich, D10); die Sperre steht im Ergebnis selbst und ist nicht abschaltbar.
- Abgleich gegen daten/produkte/*.json über EAN, MPN (im Namen) und Hersteller + Modellname.
- Gespeichert werden nur Name, URL und Saturn-Nummer der Kandidaten (§ 87b UrhG: kein Spiegeln, keine Preise, keine
  Datenblätter) in `%TEMP%/kb-datenpflege/entdeckung/kandidaten.json` (für alle Arbeitsbäume gleich, nie im Repo). Die Datenpflege-Routine (D11) liest die Datei,
  belegt die Werte auf Produktseiten nach werkzeuge/datenpflege/ANLEITUNG.md und trägt kuratiert ein.
Exit: 0 ok · 3 Domain gesperrt (Lauf abgebrochen, Teilergebnis gespeichert) · 2 Aufruffehler.
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


def norm(t):
    """Kleinbuchstaben, nur a-z0-9 (für MPN-Vergleich)."""
    return re.sub(r"[^a-z0-9]", "", str(t or "").lower().replace("ß", "ss"))


def woerter(t):
    """Wortmenge; zusätzlich jedes Wort ohne führende Ziffern (55e7s → e7s), damit Größenpräfixe nicht stören."""
    out = set()
    for w in re.findall(r"[a-z0-9]+", str(t or "").lower().replace("ß", "ss")):
        out.add(w)
        ohne = w.lstrip("0123456789")
        if ohne and ohne != w and re.search(r"\d", ohne):
            out.add(ohne)
    return out


def bestand_index(produkte=PRODUKTE):
    """Je Kategorie: EANs, MPNs (normiert, ≥ 5 Zeichen) und Modelle (Hersteller-Wörter, Namens-Wörter, ID)."""
    idx = {}
    for p in sorted(Path(produkte).glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        k = idx.setdefault(d["kategorie"], {"ean": {}, "mpn": {}, "modelle": []})
        for m in d.get("modelle", []):
            k["modelle"].append((woerter(m.get("hersteller")), woerter(m.get("name")), m["id"]))
            for v in m.get("varianten", []):
                for e in v.get("ean", []) or []:
                    k["ean"][str(e)] = m["id"]
                if len(norm(v.get("mpn"))) >= 5:
                    k["mpn"][norm(v.get("mpn"))] = m["id"]
    return idx


def zuordnen(eintrag, k):
    """Modell-ID aus dem Bestand oder None (= Kandidat). eintrag: {name, gtin[]}."""
    for e in eintrag.get("gtin", []):
        if e in k["ean"]:
            return k["ean"][e]
    n = norm(eintrag.get("name"))
    for mpn, mid in k["mpn"].items():
        if mpn in n:
            return mid
    w = woerter(eintrag.get("name"))
    for hersteller, name, mid in k["modelle"]:
        if name and hersteller and (hersteller & w) and name <= w:
            return mid
    return None


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
    try:
        return json.loads(Path(ziel).read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {"kategorien": {}}


def speichern(erg, ziel):
    """Atomar schreiben (Temp-Datei + os.replace), damit ein Abbruch die Wochensperre nicht zurücksetzt."""
    import os
    Path(ziel).parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(ziel) + ".tmp")
    tmp.write_text(json.dumps(erg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, ziel)


def zu_frueh(alt, kat, jetzt):
    t = (alt.get("kategorien", {}).get(kat) or {}).get("abgerufen")
    if not t:
        return False
    try:
        return jetzt - dt.datetime.fromisoformat(t) < dt.timedelta(days=MIN_TAGE)
    except ValueError:
        return False


def lauf(kats, seiten, holen, robots_ok, ziel=ZIEL, produkte=PRODUKTE, jetzt=None):
    """Kern ohne Netz (holen/robots_ok werden übergeben, für Tests ersetzbar). Rückgabe (ergebnis, exitcode)."""
    jetzt = jetzt or dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    idx = bestand_index(produkte)
    erg = laden(ziel)
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
        erg["kategorien"][kat] = {"abgerufen": jetzt.isoformat(), "quelle": basis, "seiten": seiten,
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
