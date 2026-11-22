# -*- coding: utf-8 -*-
"""Produktdatenbank der Finder-Suche: prüfen und für die App zusammenbauen.

    python -I werkzeuge/datenbank.py pruefen [datei.json …]   # ohne Datei: alle daten/produkte/*.json
    python -I werkzeuge/datenbank.py bauen <ziel.json> [--herkunft <commit>]   # prüft alles, schreibt kompakte App-Daten
    (--herkunft: 40-stelliger Commit, aus dem gebaut wird; werkzeuge/herkunft.py entscheidet damit über das Ersetzen)

Format: daten/produkte/FORMAT.md. Schema (Felder, Kurven, Fragen): daten/schema/kategorien.json.
Exitcode 0 = keine Fehler (Warnungen erlaubt), 1 = Fehler. Nur Standardbibliothek.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SCHEMA = WURZEL / "daten" / "schema" / "kategorien.json"
PRODUKTE = WURZEL / "daten" / "produkte"
ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATUM = re.compile(r"^\d{4}-\d{2}-\d{2}$")
QUELLENFREIGABE = WURZEL / "daten" / "quellen.json"
# Erlaubte Schlüssel laut FORMAT.md; alles andere (z. B. „listenpreis“) ist ein Fehler, damit nichts Unbelegtes durchrutscht.
MODELL_SCHLUESSEL = {"id", "hersteller", "name", "jahr", "werte", "belege", "tests", "varianten"}
VARIANTE_SCHLUESSEL = {"id", "name", "mpn", "ean", "werte", "belege", "preis"}
PREIS_SCHLUESSEL = {"eur", "haendler", "url", "stand"}
TEST_SCHLUESSEL = {"url", "titel"}   # F-01: Testberichte nur als Link, keine übernommenen Noten oder Texte
# F-07: Positivliste der Preisquellen. Shops: Domain muss in daten/quellen.json mit automatisch: true stehen (Händlername
# = Name dort). Herstellershops: nur für Modelle genau dieses Herstellers. Neue Einträge nur hier im Code (Prüfung nötig);
# die Datenpflege-Routine darf nur daten/produkte/*.json ändern und kann die Liste nicht erweitern.
PREIS_SHOPS = ("www.saturn.de", "www.alternate.de", "www.proshop.de")
HERSTELLERSHOPS = {
    "samsung": {"www.samsung.com"}, "lg": {"www.lg.com"}, "ecovacs": {"www.ecovacs.com"}, "sonos": {"www.sonos.com"},
    "bosch": {"www.bosch-home.com"}, "shark": {"www.sharkninja.de"}, "ninja": {"www.sharkninja.de"}, "bose": {"www.bose.de"},
}
PERSOENLICH = [re.compile(p, re.I) for p in (r"[\w.+-]+@[\w-]+\.[\w.]+", r"[a-z]:\\\\users\\\\", r"/users/[a-z]", r"github\.com/[a-z0-9-]+/")]


def lade_schema():
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return s, {k["id"]: k for k in s["kategorien"]}


def ist_datum(t):
    if not isinstance(t, str) or not DATUM.match(t):
        return False
    try:
        return date(2020, 1, 1) <= date.fromisoformat(t) <= date.today()
    except ValueError:
        return False


def feld_ok(feld, wert):
    """Passt der Wert zum Feldtyp und zur Kurve?"""
    typ = feld["typ"]
    if typ == "bool":
        return isinstance(wert, bool)
    if typ == "zahl":
        return isinstance(wert, (int, float)) and not isinstance(wert, bool) and wert == wert and abs(wert) < 1e7
    if typ == "stufe":
        return isinstance(wert, str) and wert in [p[0] for p in feld["kurve"]["punkte"]]
    return False


def teilpunkte(feld, wert):
    """Datenblattwert -> 0..100 nach Kurve (linear interpolieren, Stufen exakt, ja/nein)."""
    k = feld["kurve"]
    pk = k["punkte"]
    if k["art"] in ("stufen", "ja_nein"):
        for w, p in pk:
            if w == wert:
                return float(p)
        return None
    pk = sorted(pk, key=lambda x: x[0])
    if wert <= pk[0][0]:
        return float(pk[0][1])
    if wert >= pk[-1][0]:
        return float(pk[-1][1])
    for (x0, y0), (x1, y1) in zip(pk, pk[1:]):
        if x0 <= wert <= x1:
            return float(y0) if x1 == x0 else y0 + (y1 - y0) * (wert - x0) / (x1 - x0)
    return None


def _freigaben():
    try:
        q = json.loads(QUELLENFREIGABE.read_text(encoding="utf-8"))
        return [e for e in q["quellen"] if isinstance(e, dict) and isinstance(e.get("domain"), str)]
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        # fail-closed (Vorprüfung 4): ohne lesbare Freigabeliste keine grüne Schranke
        raise SystemExit(f"FEHLER  daten/quellen.json nicht lesbar ({e}) – Schranke rot")


def nur_link_domains():
    """Domains, die laut daten/quellen.json nicht automatisch abgefragt werden dürfen (Preis dort nur als Link)."""
    return {e["domain"] for e in _freigaben() if not e.get("automatisch")}


def preis_shops():
    """F-07: {domain: händlername} der freigegebenen Preis-Shops (in PREIS_SHOPS und in quellen.json automatisch: true)."""
    return {e["domain"]: str(e.get("name") or "") for e in _freigaben()
            if e.get("automatisch") is True and e["domain"] in PREIS_SHOPS}


def kanon_host(url):
    """Kleingeschriebener Host ohne Punkt am Ende; None bei Userinfo, Port, Nicht-https oder unlesbarer URL."""
    import urllib.parse
    try:
        t = urllib.parse.urlsplit(str(url))
        host = (t.hostname or "").rstrip(".").lower()
        if t.scheme != "https" or "@" in t.netloc or t.port is not None or not host:
            return None
    except ValueError:
        return None
    return host


def preisquelle_fehler(p, hersteller, shops):
    """F-07: Grund (str), wenn die Preis-URL nicht von einem freigegebenen Shop oder dem eigenen Herstellershop stammt."""
    host = kanon_host(p.get("url", ""))
    if host is None:
        return "Preis-URL unlesbar (nur https, ohne Userinfo und Port)"
    if host in shops:
        if " ".join(str(p.get("haendler", "")).split()).lower() != shops[host].lower():
            return f"Händler {p.get('haendler')!r} passt nicht zur Domain {host} (erwartet {shops[host]!r})"
        return None
    if host in HERSTELLERSHOPS.get(str(hersteller or "").strip().lower(), set()):
        return None
    return f"Preisquelle {host} nicht freigegeben (nur {', '.join(sorted(shops))} oder eigener Herstellershop)"


def testlinks(m):
    """F-01: für den Bau nur url und titel der Testlinks (alles andere fällt weg)."""
    t = m.get("tests")
    return [{"url": x["url"], "titel": x["titel"]} for x in (t if isinstance(t, list) else [])
            if isinstance(x, dict) and isinstance(x.get("url"), str) and isinstance(x.get("titel"), str)]


def host_gesperrt(url, gesperrt):
    """True bei Nur-Link-Domain (auch Subdomain, Punkt am Ende, mit/ohne www) oder URL mit Userinfo."""
    import urllib.parse
    try:
        teile = urllib.parse.urlsplit(str(url))
        host = (teile.hostname or "").rstrip(".").lower()
    except ValueError:
        return True
    if "@" in teile.netloc or not host:
        return True

    def basis(h):
        return h[4:] if h.startswith("www.") else h
    return any(basis(host) == basis(d) or host.endswith("." + basis(d)) for d in gesperrt)


def pruefe_datei(pfad, kats, ids_gesamt, fehler, warnungen, gesperrt=frozenset(), shops=None):
    shops = preis_shops() if shops is None else shops
    ort = Path(pfad).name
    try:
        roh = Path(pfad).read_text(encoding="utf-8")
        d = json.loads(roh)
    except (OSError, ValueError) as e:
        fehler.append(f"{ort}: nicht lesbar ({e})")
        return None
    for m in PERSOENLICH:
        if m.search(roh):
            fehler.append(f"{ort}: mögliche persönliche Angabe/Pfad ({m.pattern})")
    kid = d.get("kategorie")
    if kid not in kats:
        fehler.append(f"{ort}: unbekannte Kategorie {kid!r}")
        return None
    if Path(pfad).stem != kid:
        fehler.append(f"{ort}: Dateiname muss {kid}.json sein")
    if not ist_datum(d.get("stand")):
        fehler.append(f"{ort}: 'stand' fehlt oder ungültig")
    felder = {f["id"]: f for f in kats[kid]["felder"]}
    quellen = d.get("quellen") or {}
    for qid, q in quellen.items():
        if not ID.match(qid):
            fehler.append(f"{ort}: Quellen-ID {qid!r} ungültig")
        if not (isinstance(q, dict) and str(q.get("url", "")).startswith("https://") and q.get("titel") and ist_datum(q.get("gelesen"))):
            fehler.append(f"{ort}: Quelle {qid} braucht url (https), titel, gelesen")
    benutzt = set()
    modelle = d.get("modelle")
    if not isinstance(modelle, list) or not modelle:
        fehler.append(f"{ort}: keine Modelle")
        return d

    def werte_pruefen(wo, werte, belege):
        if not isinstance(werte, dict) or not isinstance(belege, dict):
            fehler.append(f"{wo}: werte/belege müssen Objekte sein")
            return
        for fid, w in werte.items():
            if fid not in felder:
                fehler.append(f"{wo}: unbekanntes Feld {fid}")
                continue
            if not feld_ok(felder[fid], w):
                fehler.append(f"{wo}: Wert {fid}={w!r} passt nicht zu Typ {felder[fid]['typ']}")
            q = belege.get(fid)
            if q not in quellen:
                fehler.append(f"{wo}: Wert {fid} ohne gültigen Beleg")
            benutzt.add(q)
        for fid in belege:
            if fid not in werte:
                warnungen.append(f"{wo}: Beleg für {fid} ohne Wert")

    for m in modelle:
        mid = m.get("id", "?")
        wo = f"{ort}/{mid}"
        if not isinstance(mid, str) or not ID.match(mid):
            fehler.append(f"{wo}: Modell-ID ungültig")
        if mid in ids_gesamt:
            fehler.append(f"{wo}: ID doppelt")
        ids_gesamt.add(mid)
        for s in sorted(set(m) - MODELL_SCHLUESSEL):
            fehler.append(f"{wo}: unbekannter Schlüssel {s!r} (FORMAT.md)")
        for pf in ("hersteller", "name"):
            if not isinstance(m.get(pf), str) or not m[pf].strip():
                fehler.append(f"{wo}: {pf} fehlt")
        if "jahr" in m and not (isinstance(m["jahr"], int) and 2018 <= m["jahr"] <= date.today().year + 1):
            fehler.append(f"{wo}: jahr ungültig")
        werte_pruefen(wo, m.get("werte", {}), m.get("belege", {}))
        tests = m.get("tests", [])
        if not isinstance(tests, list):
            fehler.append(f"{wo}: tests muss eine Liste sein")
            tests = []
        for t in tests:
            if not (isinstance(t, dict) and isinstance(t.get("url"), str) and kanon_host(t["url"])
                    and isinstance(t.get("titel"), str) and t["titel"].strip() and len(t["titel"]) <= 200):
                fehler.append(f"{wo}: Testlink braucht url (https) und titel (Text)")
            if isinstance(t, dict):
                for s in sorted(set(t) - TEST_SCHLUESSEL):
                    fehler.append(f"{wo}: Testlink mit unbekanntem Schlüssel {s!r} (nur Links, keine Noten oder Texte)")
        vs = m.get("varianten")
        if not isinstance(vs, list) or not vs:
            fehler.append(f"{wo}: keine Varianten")
            continue
        eigene = set()
        for v in vs:
            vid = v.get("id", "?")
            if vid in eigene:
                fehler.append(f"{wo}/{vid}: Varianten-ID im Modell doppelt")
            eigene.add(vid)
            wv = f"{wo}/{vid}"
            if not isinstance(vid, str) or not ID.match(vid):
                fehler.append(f"{wv}: Varianten-ID ungültig")
            if vid in ids_gesamt and vid != mid:
                fehler.append(f"{wv}: ID doppelt")
            ids_gesamt.add(vid)
            for s in sorted(set(v) - VARIANTE_SCHLUESSEL):
                fehler.append(f"{wv}: unbekannter Schlüssel {s!r} (FORMAT.md)")
            if not isinstance(v.get("name"), str) or not v["name"].strip():
                fehler.append(f"{wv}: name fehlt")
            for e in v.get("ean", []) or []:
                if not (isinstance(e, str) and re.fullmatch(r"\d{8}|\d{12,14}", e)):
                    fehler.append(f"{wv}: EAN {e!r} ungültig")
            werte_pruefen(wv, v.get("werte", {}), v.get("belege", {}))
            p = v.get("preis")
            if p is not None:
                ok = (isinstance(p, dict) and isinstance(p.get("eur"), (int, float)) and not isinstance(p.get("eur"), bool)
                      and 1 <= p["eur"] <= 100000 and isinstance(p.get("haendler"), str) and p["haendler"].strip()
                      and str(p.get("url", "")).startswith("https://") and ist_datum(p.get("stand")))
                if not ok:
                    fehler.append(f"{wv}: preis braucht eur (1–100000), haendler, url (https), stand")
                if isinstance(p, dict):
                    for s in sorted(set(p) - PREIS_SCHLUESSEL):
                        fehler.append(f"{wv}: preis mit unbekanntem Schlüssel {s!r}")
                    if host_gesperrt(p.get("url", ""), gesperrt):
                        fehler.append(f"{wv}: Preisquelle {p.get('url')} laut daten/quellen.json nur als Link erlaubt"
                                      " (oder URL mit Userinfo)")
                    else:
                        grund = preisquelle_fehler(p, m.get("hersteller"), shops)
                        if grund:
                            fehler.append(f"{wv}: {grund}")
            # Abdeckung der Note (Grundgewichte, ohne Fragen)
            zus = {**m.get("werte", {}), **v.get("werte", {})}
            g_ges = sum(f["gewicht"] for f in felder.values() if f["gewicht"] > 0)
            g_bel = sum(f["gewicht"] for fid, f in felder.items() if f["gewicht"] > 0 and fid in zus)
            if g_ges and g_bel / g_ges < 0.7:
                warnungen.append(f"{wv}: Abdeckung {g_bel / g_ges:.0%} < 70 % (keine Note)")
    for qid in quellen:
        if qid not in benutzt:
            warnungen.append(f"{ort}: Quelle {qid} wird nicht benutzt")
    return d


def alle_pruefen(dateien=None):
    _, kats = lade_schema()
    fehler, warnungen, daten, ids = [], [], [], set()
    pfade = [Path(p) for p in dateien] if dateien else sorted(PRODUKTE.glob("*.json"))
    gesperrt = frozenset(nur_link_domains())
    shops = preis_shops()
    for p in pfade:
        d = pruefe_datei(p, kats, ids, fehler, warnungen, gesperrt, shops)
        if d:
            daten.append(d)
    return daten, fehler, warnungen


def bauen(ziel, herkunft=None):
    """Kompakte App-Daten: Schema + Modelle mit vorberechneten Teilpunkten je Feld (Gewichtung macht die App).
    herkunft: Commit (40 Hex-Zeichen), aus dem gebaut wird (R2-02); steht dann als "herkunft" in der Datei."""
    if herkunft is not None and not re.fullmatch(r"[0-9a-f]{40}", str(herkunft)):
        raise ValueError("herkunft muss ein 40-stelliger Commit sein")
    schema, kats = lade_schema()
    daten, fehler, warnungen = alle_pruefen()
    if fehler:
        return daten, fehler, warnungen
    aus = {"stand": max((d["stand"] for d in daten), default=None), "regeln": {k: schema[k] for k in
           ("klassen", "unterschiedsschwelle_punkte", "datenblatt_abschlag", "aufpreis_regeln")}, "kategorien": []}
    if herkunft is not None:
        aus["herkunft"] = herkunft
    nach_kat = {d["kategorie"]: d for d in daten}
    for k in schema["kategorien"]:
        d = nach_kat.get(k["id"])
        felder = {f["id"]: f for f in k["felder"]}
        eintrag = {"id": k["id"], "name": k["name"], "felder": [{x: f[x] for x in ("id", "name", "einheit", "typ", "gewicht")} for f in k["felder"]],
                   "fragen": k.get("fragen", []), "modelle": []}
        if d:
            for m in d["modelle"]:
                for v in m["varianten"]:
                    w = {**m.get("werte", {}), **v.get("werte", {})}
                    tp = {fid: round(teilpunkte(felder[fid], x), 1) for fid, x in w.items()
                          if fid in felder and felder[fid]["gewicht"] > 0 and teilpunkte(felder[fid], x) is not None}
                    eintrag["modelle"].append({
                        "id": v["id"], "modell": m["id"], "hersteller": m["hersteller"], "name": m["name"], "variante": v["name"],
                        "jahr": m.get("jahr"), "werte": w, "teilpunkte": tp, "preis": v.get("preis"),
                        "tests": testlinks(m), "ean": v.get("ean", [])})
        aus["kategorien"].append(eintrag)
    Path(ziel).write_text(json.dumps(aus, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return daten, fehler, warnungen


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or sys.argv[1] not in ("pruefen", "bauen"):
        print(__doc__)
        return 2
    if sys.argv[1] == "bauen":
        a = sys.argv[2:]
        if len(a) not in (1, 3) or (len(a) == 3 and a[1] != "--herkunft"):
            print("Aufruf: bauen <ziel.json> [--herkunft <commit>]")
            return 2
        daten, fehler, warnungen = bauen(a[0], a[2].strip().lower() if len(a) == 3 else None)
    else:
        daten, fehler, warnungen = alle_pruefen(sys.argv[2:] or None)
    for w in warnungen:
        print("WARNUNG", w)
    for f in fehler:
        print("FEHLER ", f)
    n = sum(len(v["varianten"]) for d in daten for v in d.get("modelle", []) if isinstance(v, dict) and isinstance(v.get("varianten"), list))
    print(f"{len(daten)} Dateien · {sum(len(d.get('modelle', [])) for d in daten)} Modelle · {n} Varianten · Fehler {len(fehler)} · Warnungen {len(warnungen)}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
