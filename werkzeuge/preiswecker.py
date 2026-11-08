# -*- coding: utf-8 -*-
"""Preiswecker TV (Runde 6): liest die heise-Preisvergleich-Seiten der fünf Fernseher (nur GET, kein Konto,
kein Formular) und gibt je Modell das günstigste Angebot als JSON aus.

Aufruf:  python -X utf8 -I kaufberatung/build/preiswecker.py            (alle Modelle, JSON auf stdout)
         python -X utf8 -I kaufberatung/build/preiswecker.py --datei X   (statt Abruf eine gespeicherte Seite auswerten)

Versand: heise nennt die Versandkosten nur als Freitext je Händler. Sicher 0 € ist er nur bei
„merchant_free_shipping“ oder „GRATISVERSAND“/„versandkostenfrei“ ohne Ausnahme. „Gratisversand ab … Warenwert,
ausgenommen Speditionsware“ (Fernseher sind Speditionsware) gilt als „unklar“. Ein ausdrücklicher Betrag
(„Versand € 69,99“, „Spedition € 79,90“) wird addiert. Das Ergebnis trennt deshalb:
  sicher  = günstigster Gesamtpreis mit belegtem Versand
  roh     = günstigster Artikelpreis, falls billiger und Versand unklar (nur Hinweis, kein Alarm)
Nur Standardbibliothek.
"""
import html
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

MODELLE = {
    "lg_c6elb": "https://preisvergleich.heise.de/lg-oled-evo-ai-c6-oled83c6elb-a3774767.html",
    "lg_c69lb": "https://preisvergleich.heise.de/lg-oled-evo-ai-c6-oled83c69lb-a3773534.html",
    "sam_s90h": "https://preisvergleich.heise.de/samsung-gq8390h-a3805643.html",
    "tcl_c8l": "https://preisvergleich.heise.de/tcl-85c8l-a3810591.html",
    "sam_qn90f": "https://preisvergleich.heise.de/samsung-qe85qn90f-a3479298.html",
}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Preiswecker-privat"
BETRAG = r"(?:€|&euro;)\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{1,2})?|[0-9]+(?:,[0-9]{1,2})?)(?:,-)?"


def zahl(s):
    return float(s.replace(".", "").replace(",", "."))


def angebote(text):
    """Alle Angebotsobjekte (mit raw_price) aus dem eingebetteten JSON der Seite."""
    dec = json.JSONDecoder()
    gesehen, out = set(), []
    for m in re.finditer(r'"raw_price"\s*:', text):
        p = m.start()
        for _ in range(120):
            p = text.rfind("{", 0, p)
            if p < 0:
                break
            try:
                o, ende = dec.raw_decode(text, p)
            except ValueError:
                continue
            if isinstance(o, dict) and "raw_price" in o and ende > m.start():
                if p not in gesehen:
                    gesehen.add(p)
                    out.append(o)
                break
    return out


def versand(o):
    """(Betrag oder None, Text) – None = unklar."""
    roh = html.unescape(o.get("availability_text_el") or "")
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", roh)).strip()
    tl = t.lower()
    m = re.search(r"(versand|spedition|lieferung)[^.€]{0,30}" + BETRAG, t, re.I)
    if m and "ab" not in tl[max(0, m.start(2) - 8):m.start(2)]:
        return zahl(m.group(2)), t
    if o.get("merchant_free_shipping") == 1 or (("gratisversand" in tl or "versandkostenfrei" in tl)
                                                 and "ausgenommen" not in tl and "gratisversand ab" not in tl):
        return 0.0, t
    return None, t


def sterne(o):
    r = (o.get("merchant_stars") or {}).get("rating") or {}
    s, n = r.get("stars"), r.get("amount")
    if isinstance(s, (int, float)) and isinstance(n, int) and n > 0:
        return f"{s:.1f}".replace(".", ",") + f" ({n:,})".replace(",", ".")
    return "keine Bewertung"


def auswerten(text):
    liste = []
    for o in angebote(text):
        preis = o.get("raw_price")
        if not isinstance(preis, (int, float)) or not 500 <= preis <= 20000:
            continue
        v, vt = versand(o)
        liste.append({"artikel": round(float(preis), 2), "versand": v, "gesamt": None if v is None else round(preis + v, 2),
                      "haendler": str(o.get("merchant_name") or "?")[:60], "sterne": sterne(o),
                      "lieferung": re.sub(r"<[^>]+>", "", str(o.get("delivery_time") or ""))[:60], "versandtext": vt[:200]})
    sicher = sorted((a for a in liste if a["gesamt"] is not None), key=lambda a: a["gesamt"])
    roh = sorted(liste, key=lambda a: a["artikel"])
    best = sicher[0] if sicher else None
    hinweis = roh[0] if roh and (best is None or roh[0]["artikel"] < best["gesamt"]) and roh[0]["gesamt"] is None else None
    return {"angebote": len(liste), "sicher": best, "roh": hinweis}


def abrufen(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "de-DE,de;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


NAMEN = {"lg_c6elb": "LG OLED83C6ELB", "lg_c69lb": "LG OLED83C69LB", "sam_s90h": "Samsung GQ83S90H",
         "tcl_c8l": "TCL 85C8L", "sam_qn90f": "Samsung QE85QN90F"}
KURZ = {"lg_c6elb": "LG C6ELB", "lg_c69lb": "LG C69LB", "sam_s90h": "Samsung S90H", "tcl_c8l": "TCL C8L", "sam_qn90f": "Samsung QN90F"}
ENDE = "2026-12-01"


def abruf_alle():
    jetzt = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    erg = {"zeit": jetzt, "modelle": {}}
    for mid, url in MODELLE.items():
        try:
            erg["modelle"][mid] = {"url": url, **auswerten(abrufen(url))}
        except Exception as e:  # Abruf- oder Formatfehler: Modell als Fehler melden, weiter mit den anderen
            erg["modelle"][mid] = {"url": url, "fehler": f"{type(e).__name__}: {str(e)[:120]}"}
        time.sleep(2)
    return erg


def eur(x):
    t = f"{x:,.0f}" if abs(x - round(x)) < 1e-9 else f"{x:,.2f}"
    return t.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def lies_doc(pfad):
    """Von ArtifactData (out_dir) gespeichertes Dokument lesen: (Felder, Version) – tolerant gegenüber der Hülle."""
    try:
        o = json.load(open(pfad, encoding="utf-8"))
    except (OSError, ValueError):
        return {}, None
    if not isinstance(o, dict):
        return {}, None
    ver = next((o[k] for k in ("version", "_version", "__version__") if isinstance(o.get(k), int)), None)
    felder = o.get("data") if isinstance(o.get("data"), dict) else o
    felder = {k: v for k, v in felder.items() if k not in ("version", "_version", "__version__", "id", "doc_id", "path")}
    return felder, ver


def zahl_ok(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and 0 < x < 100000


def abgleich(erg, db_dir, aus_dir):
    """Neue Dokumente für preise/<id> und wecker/lauf berechnen, Schreibliste + Meldung ablegen."""
    import os
    os.makedirs(aus_dir, exist_ok=True)
    heute = erg["zeit"][:10]
    writes, treffer, fehler = [], [], []
    for mid in MODELLE:
        alt, ver = lies_doc(os.path.join(db_dir, "preise", mid + ".json"))
        wunsch, _ = lies_doc(os.path.join(db_dir, "wunsch", mid + ".json"))
        r = erg["modelle"].get(mid, {})
        akt = r.get("sicher")
        if not akt:
            fehler.append(KURZ[mid])
            continue
        neu = {"name": NAMEN[mid], "heiseUrl": MODELLE[mid],
               "aktuell": {k: akt[k] for k in ("gesamt", "artikel", "versand", "haendler", "sterne", "lieferung")} | {"zeit": erg["zeit"]}}
        if r.get("roh"):
            neu["roh"] = {k: r["roh"][k] for k in ("artikel", "haendler", "sterne")} | {"zeit": erg["zeit"]}
        g = akt["gesamt"]
        tief_alt = alt.get("tief") if isinstance(alt.get("tief"), dict) and zahl_ok(alt["tief"].get("gesamt")) else None
        if tief_alt and tief_alt["gesamt"] <= g:
            neu["tief"] = tief_alt
        else:
            neu["tief"] = {"gesamt": g, "datum": heute, "haendler": akt["haendler"]}
            if tief_alt:
                treffer.append(f"{KURZ[mid]} {eur(g)} neuer Tiefstpreis")
        verlauf = [v for v in alt.get("verlauf", []) if isinstance(v, dict) and v.get("d") != heute and zahl_ok(v.get("g"))]
        neu["verlauf"] = (verlauf + [{"d": heute, "g": g, "h": akt["haendler"]}])[-60:]
        wp = wunsch.get("preis")
        unter = zahl_ok(wp) and g <= wp
        war_unter = bool((alt.get("meldung") or {}).get("unter_wunsch")) and (alt.get("meldung") or {}).get("wunsch") == wp
        if unter and not war_unter:
            treffer.append(f"{KURZ[mid]} {eur(g)} unter Wunschpreis {eur(wp)}")
        neu["meldung"] = {"unter_wunsch": bool(unter), "wunsch": wp if zahl_ok(wp) else None}
        datei = os.path.join(aus_dir, f"preise_{mid}.json")
        json.dump(neu, open(datei, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        w = {"op": "set", "collection": "preise", "doc_id": mid, "file_path": os.path.abspath(datei)}
        if ver is not None:
            w["if_version"] = ver
        writes.append(w)
    status = "ok" if not fehler else ("fehler" if len(fehler) == len(MODELLE) else "teilweise")
    text = "Alle fünf Preise gelesen." if not fehler else "Kein Angebot mit belegtem Versand: " + ", ".join(fehler) + "."
    if treffer:
        text += " Treffer: " + "; ".join(treffer) + "."
    lauf_alt, lauf_ver = lies_doc(os.path.join(db_dir, "wecker", "lauf.json"))
    lauf = {"letzter": erg["zeit"], "status": status, "meldung": text[:300], "bis": ENDE}
    datei = os.path.join(aus_dir, "wecker_lauf.json")
    json.dump(lauf, open(datei, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    w = {"op": "set", "collection": "wecker", "doc_id": "lauf", "file_path": os.path.abspath(datei)}
    if lauf_ver is not None:
        w["if_version"] = lauf_ver
    writes.append(w)
    json.dump(writes, open(os.path.join(aus_dir, "writes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    push = ("TV-Preiswecker: " + "; ".join(treffer))[:195] if treffer else ""
    open(os.path.join(aus_dir, "meldung.txt"), "w", encoding="utf-8").write(push)
    return {"status": status, "treffer": treffer, "push": push, "writes": len(writes), "lauf": text}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "--datei":
        print(json.dumps(auswerten(open(a[1], encoding="utf-8").read()), ensure_ascii=False, indent=1))
        return
    if len(a) == 4 and a[0] == "--abgleich" and a[2] == "--aus":
        # a[1] = Ordner mit den per ArtifactData (out_dir) gespeicherten Dokumenten, a[3] = Ausgabeordner
        erg = abruf_alle()
        print(json.dumps(abgleich(erg, a[1], a[3]), ensure_ascii=False, indent=1))
        return
    print(json.dumps(abruf_alle(), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
