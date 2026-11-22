# -*- coding: utf-8 -*-
"""Produktdatenbank der Finder-Suche: prüfen und für die App zusammenbauen.

    python -I werkzeuge/datenbank.py pruefen [datei.json …]   # ohne Datei: alle daten/produkte/*.json
    python -I werkzeuge/datenbank.py bauen <ziel.json>        # prüft alles, schreibt kompakte App-Daten

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


def nur_link_domains():
    """Domains, die laut daten/quellen.json nicht automatisch abgefragt werden dürfen (Preis dort nur als Link)."""
    try:
        q = json.loads(QUELLENFREIGABE.read_text(encoding="utf-8"))
        return {e["domain"] for e in q.get("quellen", []) if not e.get("automatisch") and e.get("domain")}
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        # fail-closed (Vorprüfung 4): ohne lesbare Freigabeliste keine grüne Schranke
        raise SystemExit(f"FEHLER  daten/quellen.json nicht lesbar ({e}) – Schranke rot")


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


def pruefe_datei(pfad, kats, ids_gesamt, fehler, warnungen, gesperrt=frozenset()):
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
        for t in m.get("tests", []) or []:
            if not (isinstance(t, dict) and str(t.get("url", "")).startswith("https://") and t.get("titel")):
                fehler.append(f"{wo}: Testlink braucht url (https) und titel")
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
    for p in pfade:
        d = pruefe_datei(p, kats, ids, fehler, warnungen, gesperrt)
        if d:
            daten.append(d)
    return daten, fehler, warnungen


def bauen(ziel):
    """Kompakte App-Daten: Schema + Modelle mit vorberechneten Teilpunkten je Feld (Gewichtung macht die App)."""
    schema, kats = lade_schema()
    daten, fehler, warnungen = alle_pruefen()
    if fehler:
        return daten, fehler, warnungen
    aus = {"stand": max((d["stand"] for d in daten), default=None), "regeln": {k: schema[k] for k in
           ("klassen", "unterschiedsschwelle_punkte", "datenblatt_abschlag", "aufpreis_regeln")}, "kategorien": []}
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
                        "tests": m.get("tests", []), "ean": v.get("ean", [])})
        aus["kategorien"].append(eintrag)
    Path(ziel).write_text(json.dumps(aus, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return daten, fehler, warnungen


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or sys.argv[1] not in ("pruefen", "bauen"):
        print(__doc__)
        return 2
    if sys.argv[1] == "bauen":
        if len(sys.argv) != 3:
            print("Ziel fehlt")
            return 2
        daten, fehler, warnungen = bauen(sys.argv[2])
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
