# -*- coding: utf-8 -*-
"""Shopabfrage (Pilot Bestpreis-Mix, D7, Bauplan docs/recherche-eigene-preissuche.md Abschnitt 8).

Liest für die Pilotmodelle (daten/pilot_modelle.json) die festen Produktseiten der freigegebenen Quellen
(daten/quellen.json) und schreibt das Ergebnis getrennt nach pilot-preise.json. Kein Einfluss auf preise.json,
den Preiswecker oder Push.

Aufruf:  python -X utf8 -I werkzeuge/shopabfrage.py                    (Abruf, schreibt pilot-preise.json)
         python -X utf8 -I werkzeuge/shopabfrage.py --aus <datei>       (anderer Ausgabeort)
         python -X utf8 -I werkzeuge/shopabfrage.py --zeige <quelle> <url-oder-datei>
                                                                    (eine Seite auswerten und alle Angebote mit Grund zeigen)

Regeln (Abschnitt 6, Punkt 5): Ein Angebot zählt nur, wenn
  - die EAN des Produkts im JSON-LD zu einer EAN des Modells passt (führende Nullen egal, GTIN-8/12/13/14),
  - itemCondition NewCondition ist (fehlt die Angabe, gilt Neuware),
  - availability InStock ist,
  - die Währung EUR ist und der Preis im Korridor des Modells liegt,
  - der Verkäufer der Shop selbst ist (Name aus quellen.json „verkaeufer“), kein Marktplatzhändler. Saturn nennt im
    JSON-LD keinen Verkäufer; dort gilt ein Angebot nur, wenn das eingebettete Preisfeld des Artikels
    (CofrPriceFeature, id Saturn:de:<sku>) isProductOfTypeMarketplace=false und denselben Preis zeigt
    („verkaeufer_nachweis“: „mms_preisfeld“). Fehlt der Nachweis, zählt das Angebot nicht.
Versand: aus dem JSON-LD (shippingDetails, Ziel DE oder ohne Ziel), sonst Versandregel der Quelle (mit Beleg),
sonst unbekannt („zzgl. Versand“). Die Herkunft steht in versand_herkunft.

Abruf: nur Quellen mit "automatisch": true; je Quelle robots.txt live gelesen (nicht lesbar = nicht abfragen),
URL ohne Query und auf der Domain der Quelle, je Abruf 3 s Pause je Quelle, Timeout 25 s, höchstens eine
Wiederholung nur bei Zeitüberschreitung/5xx-außer-503. 403, 429, 503, Captcha oder Challenge-Seite: Quelle für
diesen Lauf „nicht abrufbar“, nie umgangen. Nicht freigegebene Quellen erscheinen nur als Link.
heise: bei Freigabe wird die heise-Produktseite mit werkzeuge/preiswecker.auswerten gelesen (nur importiert,
nicht geändert); der Link führt auf die heise-Seite, nie auf /redir/.
Nur Standardbibliothek.
"""
import argparse
import html
import html.parser
import http.client
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLEN = os.path.join(WURZEL, "daten", "quellen.json")
MODELLE = os.path.join(WURZEL, "daten", "pilot_modelle.json")
AUSGABE = os.path.join(WURZEL, "pilot-preise.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Kaufberatung-Preispilot (privat, nicht kommerziell)"
UA_TOKEN = "Kaufberatung-Preispilot"  # Name für robots.txt-Regeln (sonst gilt User-agent *)
PAUSE = 3.0
TIMEOUT = 25
MAX_BYTES = 6_000_000
# Sperrseitenerkennung (D7-03, D7-11, D7-17): HTML wird mit html.parser zerlegt in sichtbaren Text, Attributwerte
# aktiver Elemente und Inhalt aktiver Inline-Skripte. Inhalte in <template>, <noscript>, Kommentaren und Skriptstrings
# zählen nicht als sichtbarer Text; eine echte robots.txt ist nie eine Sperrseite.
# Sichtbare Aufforderungen (Text, auch <title>)
SPERRE_TEXT = re.compile(r"Access Denied|Pardon Our Interruption|Attention Required|"
                         r"complete the captcha|solve the captcha|captcha (eingeben|lösen|ausfüllen)|"
                         r"Ich bin kein Roboter|I'?m not a robot|"
                         r"verify (that )?you are (a )?human|(bestätigen|beweisen) Sie, dass Sie kein Roboter sind", re.I)
# Nur im Titeltext, dort am Anfang (D7-R6-02: Titel getrennt erfasst, Position im übrigen Text egal)
SPERRE_TITEL = re.compile(r"^\s*Just a moment", re.I)
# Technische Merkmale in Attributwerten aktiver Elemente (Skript-src, id, class, iframe-src, Formular-action)
SPERRE_ATTRIBUT = re.compile(r"challenge-platform/h/[a-z]/orchestrate|chl_page|cf-chl|px-captcha|_Incapsula_", re.I)
# Technische Merkmale in aktiven Inline-Skripten: nur die Zuweisung der Challenge-Konfiguration (Funktion, kein Text);
# gesucht wird im Skript ohne Zeichenketten und Kommentare (js_maskiert, D7-17)
SPERRE_SKRIPT = re.compile(r"\b_cf_chl_opt\s*=\s*\{")
# Ausführbare Inline-Skripte: ohne type oder mit JavaScript-Typ, ohne src (sonst ignoriert der Browser den Inhalt)
JS_TYPEN = {"", "text/javascript", "application/javascript", "text/ecmascript", "application/ecmascript", "module"}
# Content-Length nur aus ASCII-Ziffern (D7-R6-04: isdigit() ließe z. B. „²“ durch)
LAENGE = re.compile(r"[0-9]{1,15}")
# Schwache Merkmale: auch normale Produktseiten verweisen passiv darauf (Cloudflare-Skript, Captcha im Formular);
# nur ohne JSON-LD eine Sperrseite
CHALLENGE_SCHWACH = re.compile(r"challenge-platform|captcha", re.I)
ROBOTS_ZEILE = re.compile(r"\s*(#.*)?|\s*[A-Za-z][A-Za-z-]*\s*:.*")


# ---------------------------------------------------------------- JSON-LD lesen

def jsonld_bloecke(text):
    """Alle JSON-LD-Blöcke der Seite als Python-Objekte (unlesbare Blöcke werden übersprungen)."""
    out = []
    for m in re.finditer(r'<script\b[^>]*type\s*=\s*["\']?application/ld\+json["\']?[^>]*>(.*?)</script\s*>',
                         text, re.I | re.S):
        roh = m.group(1).strip()
        if roh.startswith("<!--"):
            roh = roh[4:]
        if roh.endswith("-->"):
            roh = roh[:-3]
        roh = roh.strip()
        if not roh:
            continue
        try:
            out.append(json.loads(roh))
        except ValueError:
            try:  # manche Shops escapen HTML-Entities im Block
                out.append(json.loads(html.unescape(roh)))
            except ValueError:
                continue
    return out


def _typen(o):
    t = o.get("@type") if isinstance(o, dict) else None
    if isinstance(t, str):
        return {t.rsplit("/", 1)[-1]}
    if isinstance(t, list):
        return {str(x).rsplit("/", 1)[-1] for x in t}
    return set()


def produkte(o, tiefe=0):
    """Rekursiv alle Objekte mit @type Product (auch in @graph, BuyAction, ProductGroup.hasVariant usw.)."""
    if tiefe > 40:
        return []
    out = []
    if isinstance(o, list):
        for x in o:
            out += produkte(x, tiefe + 1)
    elif isinstance(o, dict):
        if "Product" in _typen(o) or "IndividualProduct" in _typen(o):
            out.append(o)
        for k, v in o.items():
            if isinstance(v, (dict, list)) and k != "offers":
                out += produkte(v, tiefe + 1)
    return out


def norm_ean(x):
    s = re.sub(r"\D", "", str(x or ""))
    return s.lstrip("0") if len(s) in (8, 12, 13, 14) else ""


def eans(p):
    out = set()
    for k in ("gtin13", "gtin", "gtin14", "gtin12", "gtin8", "ean"):
        v = p.get(k)
        for x in (v if isinstance(v, list) else [v]):
            e = norm_ean(x)
            if e:
                out.add(e)
    return out


def angebote_von(p):
    """offers normalisieren: Offer, Liste, AggregateOffer mit offers."""
    roh = p.get("offers")
    liste = roh if isinstance(roh, list) else [roh]
    out = []
    for o in liste:
        if not isinstance(o, dict):
            continue
        if "AggregateOffer" in _typen(o) and o.get("offers"):
            innen = o["offers"]
            out += [x for x in (innen if isinstance(innen, list) else [innen]) if isinstance(x, dict)]
        else:
            out.append(o)
    return out


def zahl(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip().replace("€", "").replace(" ", "").strip()
        if re.fullmatch(r"\d+(\.\d+)?|\.\d+", s):  # auch ".00" (Proshop-Versand, D7-08)
            return float(s)
        if re.fullmatch(r"\d{1,3}(\.\d{3})*(,\d{1,2})?", s):
            return float(s.replace(".", "").replace(",", "."))
        if re.fullmatch(r"\d+,\d{1,2}", s):
            return float(s.replace(",", "."))
    return None


def betrag_ok(x):
    """Endlicher, nicht negativer Betrag (D7-10: NaN, Unendlich, negative Werte verwerfen)."""
    return x is not None and math.isfinite(x) and x >= 0


def _endung(x):
    return str(x or "").rsplit("/", 1)[-1].strip()


def preis_von(o):
    p = zahl(o.get("price"))
    if p is None and isinstance(o.get("priceSpecification"), (dict, list)):
        ps = o["priceSpecification"]
        for s in (ps if isinstance(ps, list) else [ps]):
            if not isinstance(s, dict) or _endung(s.get("priceType")) in ("ListPrice", "StrikethroughPrice", "MSRP", "SRP"):
                continue  # Streich-/Listenpreis ist kein Angebotspreis
            if zahl(s.get("price")) is not None:
                return zahl(s.get("price")), str(s.get("priceCurrency") or o.get("priceCurrency") or "")
    return p, str(o.get("priceCurrency") or "")


def verkaeufer_von(o):
    s = o.get("seller")
    if isinstance(s, list):
        s = s[0] if s else None
    if isinstance(s, dict):
        return str(s.get("name") or "").strip()
    if isinstance(s, str):
        return s.strip()
    return ""


def versand_von(o):
    """Versandbetrag aus shippingDetails (Ziel DE oder ohne Ziel); None = nicht angegeben."""
    sd = o.get("shippingDetails")
    werte = []
    for d in (sd if isinstance(sd, list) else [sd]):
        if not isinstance(d, dict):
            continue
        ziel = d.get("shippingDestination")
        laender = set()
        for z in (ziel if isinstance(ziel, list) else [ziel]):
            if isinstance(z, dict) and z.get("addressCountry"):
                laender.add(str(z["addressCountry"]).upper())
        if laender and "DE" not in laender:
            continue
        r = d.get("shippingRate")
        for rr in (r if isinstance(r, list) else [r]):
            if isinstance(rr, dict):
                w = zahl(rr.get("value"))
                cur = str(rr.get("currency") or "EUR")
                if betrag_ok(w) and cur == "EUR":
                    werte.append(w)
    # Mehrere verschiedene Sätze (z. B. Abholung 0 € neben Spedition): nicht raten, Versand bleibt unbekannt
    return werte[0] if werte and len(set(werte)) == 1 else None


def _name_norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


class DoppelterSchluessel(ValueError):
    pass


def _ohne_doppelte(paare):
    """object_pairs_hook: doppelte Schlüssel im selben Objekt sind mehrdeutig (D7-14)."""
    obj = {}
    for k, v in paare:
        if k in obj:
            raise DoppelterSchluessel(k)
        obj[k] = v
    return obj


# D7-R7-02: enge Positivliste nach der echten Seite: das Skript beginnt mit genau dieser Zuweisung
_ZUSTAND_START = re.compile(r"\s*window\.__PRELOADED_STATE__\s*=\s*(?=\{)")
_JS_TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|\bundefined\b|[{}\[\]]', re.S)
# Passive Teile eines Skripts: Zeichenketten ("…", '…', `…` ohne Verschachtelung) und Kommentare (// …, /* … */,
# HTML-artige Zeilenkommentare <!-- … und --> … am Zeilenanfang klassischer Skripte, D7-R7-03)
_JS_PASSIV = re.compile(r'"(?:[^"\\\n]|\\.)*"|' r"'(?:[^'\\\n]|\\.)*'|`(?:[^`\\]|\\.)*`|//[^\n]*|/\*.*?(?:\*/|\Z)|"
                        r"<!--[^\n]*|^[ \t]*-->[^\n]*", re.S | re.M)


def js_maskiert(skript):
    """Skript mit Zeichenketten und Kommentaren durch gleich viele Leerzeichen ersetzt (Positionen bleiben gleich).
    Nur darin wird das Challenge-Merkmal gesucht (D7-17). Leitplanke (D7-R7-03): Regex-Literale und verschachtelte
    Template-Literale werden nicht erkannt; dort kann passiver Text eine Fehlsperre auslösen oder Code verdecken.
    Fehlsperre = sichere Richtung (Quelle in diesem Lauf nicht abgefragt, kein falscher Preis)."""
    return _JS_PASSIV.sub(lambda m: " " * len(m.group(0)), skript)


def mms_zustand(text):
    """D7-15/D7-18/D7-R6-01/D7-R7-02: eingebetteten Seitenzustand der MMS-Plattform vollständig lesen. Enge
    Positivliste nach der echten Seite: genau ein ausführbares Inline-Skript (nicht in HTML-Kommentaren, <template>,
    <noscript>, Daten-Skripten, Skripten mit src) beginnt mit `window.__PRELOADED_STATE__ = {`; danach nur das
    Objektliteral, optional „;“ und Leerraum bis zum Skriptende. Kein anderes ausführbares Skript nennt den Zustand im
    Code. Das Objektliteral muss außer `undefined` (-> null) gültiges JSON sein, Klammern ausgeglichen, keine doppelten
    Schlüssel. Sonst None (kein Nachweis)."""
    funde, andere = [], 0
    for skript in seitenzerlegung(text).skripte:
        m = _ZUSTAND_START.match(skript)
        if m:
            funde.append((skript, m.end()))
        elif "__PRELOADED_STATE__" in js_maskiert(skript):
            andere += 1
    if len(funde) != 1 or andere:
        return None
    skript, anfang = funde[0]
    teile, pos, tiefe = [], anfang, 0
    for m in _JS_TOKEN.finditer(skript, anfang):
        tok = m.group(0)
        if tok == "undefined":
            teile.append(skript[pos:m.start()] + "null")
            pos = m.end()
            continue
        if tok in "{[":
            tiefe += 1
        elif tok in "}]":
            tiefe -= 1
            if tiefe == 0:
                teile.append(skript[pos:m.end()])
                break
    else:
        return None  # Objekt nicht abgeschlossen
    if not re.fullmatch(r"\s*;?\s*", skript[m.end():]):
        return None  # angehängter Ausdruck („.artikel“, „|| x“, Template-Literal) oder weiterer Code
    try:
        zustand = json.loads("".join(teile), object_pairs_hook=_ohne_doppelte)
    except ValueError:  # auch DoppelterSchluessel
        return None
    return zustand if isinstance(zustand, dict) else None


def _alle_objekte(wurzel):
    stapel = [wurzel]
    while stapel:
        x = stapel.pop()
        if isinstance(x, dict):
            yield x
            stapel.extend(x.values())
        elif isinstance(x, list):
            stapel.extend(x)


def _ist_preisobjekt(o):
    preis = o.get("price")
    return (o.get("__typename") == "CofrPriceFeature"
            or (isinstance(preis, dict) and preis.get("__typename") == "CofrPriceFeaturePrice")
            or (o.get("__typename") is None and ("currency" in o or "isProductOfTypeMarketplace" in o)))


def mms_preisfeld(text, praefix, sku):
    """Saturn/MediaMarkt (Plattform MMS): JSON-LD nennt keinen Verkäufer. Der eingebettete Seitenzustand enthält je
    Artikel ein Preisfeld „CofrPriceFeature“ mit id "<praefix><sku>" und isProductOfTypeMarketplace. Rückgabe
    (marktplatz: bool, betrag, versand) des Hauptangebots oder None, falls nicht eindeutig belegt.
    Strukturell (D7-15/D7-18): alle Preisobjekte der Ziel-SKU im gesamten Zustand, jede Feldfolge, müssen gültig sein
    und übereinstimmen. Andere Merkmale derselben SKU (Abholung, Lieferung, Medien, Verweise) zählen nicht."""
    if not sku:
        return None
    zustand = mms_zustand(text)
    if zustand is None:
        return None
    ziel = f"{praefix}{sku}"
    funde = set()
    for o in _alle_objekte(zustand):
        if o.get("id") != ziel or not _ist_preisobjekt(o):
            continue
        preis = o.get("price")
        if (o.get("__typename") not in (None, "CofrPriceFeature") or o.get("currency") != "EUR"
                or not isinstance(o.get("isProductOfTypeMarketplace"), bool)):
            return None  # widersprüchlich oder unvollständig: kein Nachweis
        betrag = versand = None
        if isinstance(preis, dict) and preis.get("__typename") == "CofrPriceFeaturePrice":
            betrag, versand = zahl(preis.get("amount")), zahl(preis.get("shippingCost"))
        funde.add((o["isProductOfTypeMarketplace"], betrag if betrag_ok(betrag) else None,
                   versand if betrag_ok(versand) else None))
    return funde.pop() if len(funde) == 1 else None


def pruefe_angebot(o, modell, quelle, text="", sku=None):
    """(gueltig, grund, daten) für ein einzelnes Offer."""
    preis, cur = preis_von(o)
    zustand = _endung(o.get("itemCondition"))
    lieferbar = _endung(o.get("availability"))
    verk = verkaeufer_von(o)
    daten = {"preis": preis, "waehrung": cur, "zustand": zustand or None, "lieferbar": lieferbar or None,
             "verkaeufer": verk or None}
    if not verk and quelle.get("verkaeufer_nachweis") == "mms_preisfeld" and preis is not None:
        f = mms_preisfeld(text, quelle["mms_praefix"], sku)
        if f is None:
            daten["verkaeufer"] = None
        elif f[0]:
            return False, "Marktplatzangebot (Seitenzustand)", daten
        elif f[1] is None or not betrag_ok(preis) or abs(f[1] - preis) > 0.005:
            return False, f"Preis im Seitenzustand ({f[1]}) passt nicht zum JSON-LD", daten
        else:
            verk = quelle["name"]
            daten["verkaeufer"] = verk + " (Seitenzustand: kein Marktplatz)"
            daten["versand_seite"] = f[2]
    if not betrag_ok(preis):
        return False, "kein Preis", daten
    if cur != "EUR":
        return False, f"Währung {cur or 'fehlt'}", daten
    if zustand and zustand != "NewCondition":
        return False, f"Zustand {zustand}", daten
    if lieferbar != "InStock":
        return False, f"nicht lieferbar ({lieferbar or 'keine Angabe'})", daten
    erlaubt = {_name_norm(n) for n in quelle.get("verkaeufer", [])}
    if not verk:
        return False, "Verkäufer fehlt oder nicht belegt", daten
    if "versand_seite" not in daten and _name_norm(verk) not in erlaubt:  # Seitenzustand-Nachweis ersetzt den Namen
        return False, f"Verkäufer {verk} (Marktplatz?)", daten
    lo, hi = modell["korridor"]
    if not lo <= preis <= hi:
        return False, f"Preis {preis} außerhalb Korridor {lo}–{hi}", daten
    return True, "ok", daten


def auswerten_seite(text, modell, quelle, link, zeit):
    """Alle Angebote der Seite prüfen. Rückgabe: (gültige Angebote, Protokoll aller geprüften Angebote)."""
    ziel = {norm_ean(e) for e in modell["eans"]} - {""}
    gueltig, protokoll = [], []
    prods = [p for b in jsonld_bloecke(text) for p in produkte(b)]
    if not prods:
        protokoll.append({"grund": "kein Product im JSON-LD"})
    for p in prods:
        pe = eans(p)
        passt = bool(pe & ziel)
        for o in angebote_von(p):
            if not passt:
                protokoll.append({"grund": f"EAN passt nicht ({', '.join(sorted(pe)) or 'keine'})"})
                continue
            ok, grund, d = pruefe_angebot(o, modell, quelle, text, p.get("sku"))
            protokoll.append(dict(d, grund=grund))
            if not ok:
                continue
            v = versand_von(o)
            herkunft = "json-ld"
            if v is None and d.get("versand_seite") is not None:
                v, herkunft = d["versand_seite"], "seitenzustand"
            if v is None:
                v, herkunft = versand_regel(quelle, d["preis"])
            gueltig.append({"quelle": "eigen", "shop": quelle["id"], "haendler": quelle["name"],
                            "preis": round(d["preis"], 2), "versand": None if v is None else round(v, 2),
                            "versand_herkunft": herkunft,
                            "gesamt": None if v is None else round(d["preis"] + v, 2), "link": link, "zeit": zeit})
    return gueltig, protokoll


def versand_regel(quelle, preis):
    """Rückfall-Versandregel aus quellen.json: {"frei_ab": X, "sonst": Y} mit Beleg; sonst unbekannt."""
    r = quelle.get("versandregel")
    if not isinstance(r, dict) or not r.get("beleg"):
        return None, "unbekannt"
    if r.get("frei_ab") is not None and preis >= r["frei_ab"]:
        return 0.0, "shopregel"
    if r.get("sonst") is not None:
        return float(r["sonst"]), "shopregel"
    return None, "unbekannt"


# ---------------------------------------------------------------- heise (nur bei Freigabe)

def heise_auswerten(text, modell, link, zeit):
    sys.path.insert(0, os.path.join(WURZEL, "werkzeuge"))
    import preiswecker  # nur lesend genutzt (angebote, versand wie in preiswecker.auswerten)
    lo, hi = modell["korridor"]
    out = []
    # Alle Angebote im Korridor, keine Vorauswahl: ausgewählt wird erst nach der Dublettenbereinigung (D7-06)
    for o in preiswecker.angebote(text):
        preis = o.get("raw_price")
        if isinstance(preis, bool) or not isinstance(preis, (int, float)) or not lo <= preis <= hi:
            continue
        v, _ = preiswecker.versand(o)
        out.append({"quelle": "heise", "shop": "heise", "haendler": str(o.get("merchant_name") or "?")[:60],
                    "preis": round(float(preis), 2), "versand": v,
                    "versand_herkunft": "heise" if v is not None else "unbekannt",
                    "gesamt": None if v is None else round(preis + v, 2), "link": link, "zeit": zeit})
    return out, [{"grund": f"heise: {len(out)} Angebote im Korridor"}]


# ---------------------------------------------------------------- Abruf

class NichtAbrufbar(Exception):
    pass


class Weitergeleitet(NichtAbrufbar):
    """Antwort kam von einer anderen URL (Weiterleitung): nicht auswerten, Quelle aber nicht für den Lauf sperren."""


class _Seitenteile(html.parser.HTMLParser):
    """Zerlegt HTML in sichtbaren Text, Titeltexte, Attributwerte aktiver Elemente und die Inhalte ausführbarer
    Inline-Skripte (je Skript ein Eintrag)."""
    UNSICHTBAR = {"template", "noscript"}
    INLINE = {"a", "abbr", "b", "bdi", "bdo", "cite", "code", "data", "dfn", "em", "font", "i", "kbd", "mark", "q", "s",
              "samp", "small", "span", "strong", "sub", "sup", "time", "u", "var", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.attribute, self.skripte, self.titel = [], [], [], []
        self.jsonld = False  # echter JSON-LD-Skriptblock (nicht in Kommentar/<template>/<noscript>, D7-R7-05)
        self._unsichtbar = 0
        self._in = None  # "skript" (ausführbares Inline-Skript) oder "stumm" (Stil, Daten-Skript, Skript mit src)
        self._skript = self._titel = None

    def handle_starttag(self, tag, attrs):
        if tag in self.UNSICHTBAR:
            self._unsichtbar += 1
        if self._unsichtbar:
            return
        self.attribute.extend(v for _, v in attrs if v)
        if tag in ("script", "style"):
            a = dict(attrs)
            if tag == "script" and "ld+json" in (a.get("type") or "").lower():
                self.jsonld = True
            aktiv = tag == "script" and (a.get("type") or "").strip().lower() in JS_TYPEN and "src" not in a
            self._in = "skript" if aktiv else "stumm"
            self._skript = [] if aktiv else None
        elif tag == "title":
            self._titel = []
        elif tag not in self.INLINE:
            self.text.append(" ")

    def handle_startendtag(self, tag, attrs):
        if not self._unsichtbar:
            self.attribute.extend(v for _, v in attrs if v)
            if tag not in self.INLINE:
                self.text.append(" ")

    def handle_endtag(self, tag):
        if tag in self.UNSICHTBAR:
            self._unsichtbar = max(0, self._unsichtbar - 1)
        elif tag in ("script", "style"):
            self._skript_ende()
            self._in = None
        elif tag == "title" and self._titel is not None:
            self.titel.append(re.sub(r"\s+", " ", "".join(self._titel)))  # D7-R7-04: Umbrüche wie Leerzeichen
            self._titel = None
            self.text.append(" ")
        elif tag not in self.INLINE and not self._unsichtbar:
            self.text.append(" ")

    def _skript_ende(self):
        if self._skript is not None:
            self.skripte.append("".join(self._skript))
            self._skript = None

    def handle_data(self, data):
        if self._unsichtbar:
            return
        if self._in == "skript":
            self._skript.append(data)
        elif self._in is None:
            self.text.append(data)
            if self._titel is not None:
                self._titel.append(data)


def seitenzerlegung(text):
    """Seitenteile einer Antwort (Parser-Objekt mit text, titel, attribute, skripte)."""
    p = _Seitenteile()
    try:
        p.feed(text)
        p.close()
    except Exception:  # html.parser ist tolerant; im Zweifel mit dem bis dahin Gelesenen weiter
        pass
    p._skript_ende()  # nicht geschlossenes letztes Skript (Antwort endet im Skript)
    return p


def seitenteile(text):
    """(sichtbarer Text, Attributwerte, Inline-Skripte) einer Antwort; Leerraum im Text zusammengefasst."""
    p = seitenzerlegung(text)
    return re.sub(r"\s+", " ", "".join(p.text)), "\n".join(p.attribute), "\n".join(p.skripte)


def ist_challenge(text, inhaltstyp):
    """Sperr-/Challenge-Seite? Eine echte robots.txt nie (gleiche Prüfung wie robots_gueltig, D7-R6-03; Kommentare und
    passive Pfade zählen nicht, D7-11/D7-17). Sonst sperren sichtbare Aufforderungen (auch Titel) und technische
    Merkmale aktiver Elemente immer, unabhängig von Inhaltstyp, Position und Auszeichnung; schwache Merkmale nur bei
    HTML ohne JSON-LD, und auch dann nur in denselben gefilterten Seitenteilen (D7-17)."""
    if robots_gueltig(text):
        return False
    p = seitenzerlegung(text)
    sichtbar = re.sub(r"\s+", " ", "".join(p.text))
    attribute = "\n".join(p.attribute)
    code = "\n".join(js_maskiert(x) for x in p.skripte)
    if (SPERRE_TEXT.search(sichtbar) or any(SPERRE_TITEL.search(x) for x in p.titel)
            or SPERRE_ATTRIBUT.search(attribute) or SPERRE_SKRIPT.search(code)):
        return True
    if "html" not in (inhaltstyp or "").lower():
        return False
    schwach = "\n".join((sichtbar, attribute, code))
    return bool(CHALLENGE_SCHWACH.search(schwach)) and not p.jsonld


class _KeineWeiterleitung(urllib.request.HTTPRedirectHandler):
    """3xx nicht verfolgen (D7-01): urllib löst dann HTTPError mit dem 3xx-Code aus, das Ziel wird nie abgerufen."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class UnklarerRahmen(http.client.HTTPException):
    """Antwortende nicht eindeutig belegt (D7-02/D7-16)."""


class _StrengeAntwort(http.client.HTTPResponse):
    """D7-02/D7-16: Antwortende muss eindeutig belegt sein. Erlaubt sind genau zwei Rahmen:
    - Content-Length (ohne Transfer-Encoding): gelesene Länge wird in abrufen() verglichen;
    - Transfer-Encoding chunked (Wert nach Leerraum-/Großschreibangleichung genau „chunked“): jede Größenzeile,
      jedes Chunk-Ende und der Abschluss (Trailer, Leerzeile) streng mit CRLF.
    Alles andere (anderes Transfer-Encoding, beides zugleich, Ende nur durch Verbindungsabbau) = UnklarerRahmen.
    Überschreibt die internen Methoden `_get_chunk_left` und `_read_and_discard_trailer` (Python 3.11–3.13);
    `test_d7_02_gekuerzte_200_antwort` sichert das Verhalten ab, falls sich die Interna ändern."""

    def begin(self):
        super().begin()
        werte = self.headers.get_all("Transfer-Encoding") or []
        laenge = self.headers.get_all("Content-Length") or []
        if werte:
            if len(werte) != 1 or werte[0].strip().lower() != "chunked" or laenge:
                raise UnklarerRahmen(f"Transfer-Encoding {werte!r}, Content-Length {laenge!r}")
            self.chunked, self.chunk_left, self.length = True, None, None
        elif self.status == 200 and (len(laenge) != 1 or not LAENGE.fullmatch(laenge[0].strip(" \t"))):
            raise UnklarerRahmen(f"weder chunked noch eindeutige Content-Length ({laenge!r})")

    def _zeile(self):
        z = self.fp.readline(http.client._MAXLINE + 1)
        if len(z) > http.client._MAXLINE:
            raise http.client.LineTooLong("chunk")
        if not z.endswith(b"\r\n"):
            raise http.client.IncompleteRead(b"")
        return z[:-2]

    def _get_chunk_left(self):
        chunk_left = self.chunk_left
        if not chunk_left:
            if chunk_left is not None and self._safe_read(2) != b"\r\n":
                raise http.client.IncompleteRead(b"")
            groesse = self._zeile().split(b";", 1)[0].strip(b" \t")
            if not re.fullmatch(rb"[0-9A-Fa-f]{1,16}", groesse):
                raise http.client.IncompleteRead(b"")
            chunk_left = int(groesse, 16)
            if chunk_left == 0:
                self._read_and_discard_trailer()
                self._close_conn()
                chunk_left = None
            self.chunk_left = chunk_left
        return chunk_left

    def _read_and_discard_trailer(self):
        while self._zeile() != b"":
            pass


class _StrengHTTP(http.client.HTTPConnection):
    response_class = _StrengeAntwort


class _StrengHTTPS(http.client.HTTPSConnection):
    response_class = _StrengeAntwort


class _HTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(_StrengHTTP, req)


class _HTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        kw = {"context": self._context}
        if getattr(self, "_check_hostname", None) is not None:
            kw["check_hostname"] = self._check_hostname
        return self.do_open(_StrengHTTPS, req, **kw)


_OPENER = urllib.request.build_opener(_KeineWeiterleitung, _HTTPHandler, _HTTPSHandler)


def abrufen(url):
    """GET mit ehrlichem User-Agent, ohne Weiterleitungen. 403/429/503/Challenge -> NichtAbrufbar (nie umgehen)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "de-DE,de;q=0.9",
                                               "Accept": "text/html,application/xhtml+xml"})
    for versuch in (1, 2):
        try:
            with _OPENER.open(req, timeout=TIMEOUT) as r:
                roh = r.read(MAX_BYTES + 1)
                if getattr(r, "status", 200) != 200:  # D7-02: Teilantworten (206) u. ä. nicht auswerten
                    raise NichtAbrufbar(f"HTTP {r.status} (keine vollständige Antwort)")
                if len(roh) > MAX_BYTES:
                    raise NichtAbrufbar("Antwort über der Lesegrenze (abgeschnitten)")
                laenge = r.headers.get("Content-Length")
                if laenge is not None:
                    laenge = laenge.strip(" \t")
                if laenge is not None and (not LAENGE.fullmatch(laenge) or int(laenge) != len(roh)):
                    raise NichtAbrufbar("Antwort unvollständig (Länge passt nicht zu Content-Length)")  # D7-02
                text = roh.decode(r.headers.get_content_charset() or "utf-8", "replace")
                typ = r.headers.get("Content-Type", "")
                if r.geturl() != url:  # zweite Sicherung, falls doch eine Weiterleitung verfolgt wurde
                    raise Weitergeleitet(f"Weiterleitung auf {r.geturl()[:120]}")
        except http.client.HTTPException as e:  # D7-02/D7-16: vorzeitiges Ende oder unklarer Rahmen
            raise NichtAbrufbar(f"Antwort unvollständig oder Rahmen unklar ({type(e).__name__})")
        except urllib.error.HTTPError as e:
            if 300 <= e.code < 400:
                raise Weitergeleitet(f"Weiterleitung (HTTP {e.code}) auf {str(e.headers.get('Location') or '?')[:120]}")
            if e.code in (401, 403, 429, 503):
                raise NichtAbrufbar(f"HTTP {e.code}")
            if e.code >= 500 and versuch == 1:
                time.sleep(PAUSE)
                continue
            raise NichtAbrufbar(f"HTTP {e.code}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if versuch == 1:
                time.sleep(PAUSE)
                continue
            raise NichtAbrufbar(f"Netzfehler: {getattr(e, 'reason', e)}")
        if ist_challenge(text, typ):
            raise NichtAbrufbar("Bot-Prüfung/Challenge-Seite")
        return text
    raise NichtAbrufbar("kein Ergebnis")


def robots_fuer(quelle, holen=abrufen):
    """robots.txt live lesen; Rückgabe RobotFileParser oder Grund (str), falls nicht lesbar."""
    url = f"https://{quelle['domain']}/robots.txt"
    try:
        text = holen(url)
    except NichtAbrufbar as e:
        return f"robots.txt nicht lesbar ({e})"
    if not robots_gueltig(text):
        return "robots.txt nicht lesbar (keine gültigen Regeln, z. B. HTML-Seite)"
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(text.splitlines())
    return rp


def robots_gueltig(text):
    """D7-02: nur echte robots.txt auswerten. Jede Zeile leer, Kommentar oder „Feld: Wert“, mindestens eine
    User-agent-Zeile. HTML-Wartungsseiten, Fließtext oder leere Antworten gelten als nicht lesbar."""
    zeilen = (text or "").splitlines()
    return (all(ROBOTS_ZEILE.fullmatch(z) for z in zeilen)
            and any(re.match(r"\s*user-agent\s*:", z, re.I) for z in zeilen))


def url_erlaubt(url, quelle, rp):
    t = urllib.parse.urlsplit(url)
    if t.scheme != "https" or t.hostname != quelle["domain"]:
        return False, "URL nicht auf der Domain der Quelle"
    if t.query:
        return False, "URL mit Query (nicht erlaubt)"
    for pfad in quelle.get("gesperrte_pfade", []):
        if t.path.startswith(pfad):
            return False, f"Pfad {pfad} laut robots.txt gesperrt"
    # robotparser kennt keine Wildcards (*, $) mitten im Pfad: dafür gesperrte_pfade und der Query-Ausschluss oben
    if not rp.can_fetch(UA_TOKEN, url):
        return False, "robots.txt verbietet die URL"
    return True, ""


# ---------------------------------------------------------------- Zusammenführung

def _haendler_norm(s):
    """D7-07: nur Groß-/Kleinschreibung und Leerraum angleichen; andere Schreibweisen nur über Aliase."""
    return " ".join(str(s or "").lower().split())


def haendler_aliase(quellen):
    """Normalisierter Händlername -> Quellen-id, nur aus quellen.json (name, verkaeufer) der Shops (D7-07)."""
    out = {}
    for q in quellen:
        if q.get("typ") == "shop":
            for n in [q.get("name"), q.get("id")] + list(q.get("verkaeufer") or []):
                if _haendler_norm(n):
                    out[_haendler_norm(n)] = q["id"]
    return out


def bestpreis(angebote, aliase=None):
    """Günstigstes Angebot nach Gesamtpreis; ohne bekannten Versand nur, wenn kein Angebot mit Versand billiger ist.
    Dubletten (gleicher Händler laut vollem Namen oder Alias, gleicher Artikelpreis) fallen weg; das eigene Angebot
    hat Vorrang vor heise, bei gleichem Vorrang gewinnt der niedrigere belegte Gesamtpreis."""
    aliase = aliase or {}
    gesehen, eindeutig = set(), []
    for a in sorted(angebote, key=lambda a: (a["quelle"] != "eigen", a["preis"], a["gesamt"] is None,
                                             a["gesamt"] or 0)):
        n = _haendler_norm(a["haendler"])
        k = (aliase.get(n, n), a["preis"])
        if k in gesehen:
            continue
        gesehen.add(k)
        eindeutig.append(a)
    sicher = sorted((a for a in eindeutig if a["gesamt"] is not None), key=lambda a: a["gesamt"])
    offen = sorted((a for a in eindeutig if a["gesamt"] is None), key=lambda a: a["preis"])
    best = sicher[0] if sicher else (offen[0] if offen else None)
    hinweis = offen[0] if offen and sicher and offen[0]["preis"] < sicher[0]["gesamt"] else None
    return best, hinweis, eindeutig


def lauf(quellen, modelle, holen=abrufen, pause=PAUSE, jetzt=None):
    zeit = jetzt or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    qmap = {q["id"]: q for q in quellen}
    aliase = haendler_aliase(quellen)
    status_quelle, robots = {}, {}
    letzter = {}
    for q in quellen:
        if q.get("automatisch") is not True:
            status_quelle[q["id"]] = "nur Link (nicht freigegeben)"
    erg = {}
    for m in modelle:
        alle, je = [], {}
        for qid, url in m.get("urls", {}).items():
            q = qmap.get(qid)
            if q is None:
                je[qid] = {"status": "unbekannte Quelle", "link": url}
                continue
            if q.get("automatisch") is not True:
                je[qid] = {"status": "nur Link", "link": url}
                continue
            if qid in status_quelle:
                je[qid] = {"status": status_quelle[qid], "link": url}
                continue
            if qid not in robots:
                robots[qid] = robots_fuer(q, holen)
                letzter[qid] = time.monotonic()
                if isinstance(robots[qid], str):
                    status_quelle[qid] = "nicht abrufbar: " + robots[qid]
                    je[qid] = {"status": status_quelle[qid], "link": url}
                    continue
            ok, grund = url_erlaubt(url, q, robots[qid])
            if not ok:
                je[qid] = {"status": "nicht abgefragt: " + grund, "link": url}
                continue
            warte = pause - (time.monotonic() - letzter.get(qid, -1e9))
            if warte > 0:
                time.sleep(warte)
            try:
                text = holen(url)
            except Weitergeleitet as e:
                je[qid] = {"status": f"nicht ausgewertet: {e}", "link": url}
                continue
            except NichtAbrufbar as e:
                status_quelle[qid] = f"nicht abrufbar: {e}"
                je[qid] = {"status": status_quelle[qid], "link": url}
                continue
            finally:
                letzter[qid] = time.monotonic()
            if qid == "heise":
                gueltig, prot = heise_auswerten(text, m, url, zeit)
            else:
                gueltig, prot = auswerten_seite(text, m, q, url, zeit)
            alle += gueltig
            je[qid] = {"status": "ok" if gueltig else "kein gültiges Angebot", "link": url,
                       "angebote": gueltig, "geprueft": prot[:10]}
        best, hinweis, eindeutig = bestpreis(alle, aliase)
        erg[m["id"]] = {"name": m["name"], "kategorie": m["kategorie"], "bestpreis": best, "hinweis_ohne_versand": hinweis,
                        "angebote": eindeutig, "quellen": je}
    return {"stand": zeit, "hinweis": "Pilot: günstigster Preis bei den geprüften Quellen, kein Marktbestpreis.",
            "quellen_status": status_quelle, "modelle": erg}


def lade(pfad):
    with open(pfad, encoding="utf-8") as f:
        return json.load(f)


def pruefe_daten(quellen, modelle):
    """Pflichtfelder prüfen; Fehlerliste (leer = ok)."""
    fehler = []
    ids = set()
    for q in quellen:
        for k in ("id", "name", "domain", "automatisch", "pruefung"):
            if k not in q:
                fehler.append(f"Quelle {q.get('id', '?')}: {k} fehlt")
        if not isinstance(q.get("automatisch"), bool):
            fehler.append(f"Quelle {q.get('id')}: automatisch muss true oder false sein")
        if q.get("automatisch") is True and not (q.get("pruefung") or {}).get("datum"):
            fehler.append(f"Quelle {q.get('id')}: automatisch ohne Prüfdatum")
        ids.add(q.get("id"))
    for m in modelle:
        for k in ("id", "name", "kategorie", "eans", "korridor", "urls"):
            if k not in m:
                fehler.append(f"Modell {m.get('id', '?')}: {k} fehlt")
        if not all(norm_ean(e) for e in m.get("eans", [])) or not m.get("eans"):
            fehler.append(f"Modell {m.get('id')}: EAN ungültig")
        for qid in m.get("urls", {}):
            if qid not in ids:
                fehler.append(f"Modell {m.get('id')}: unbekannte Quelle {qid}")
    return fehler


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--aus", default=AUSGABE)
    ap.add_argument("--quellen", default=QUELLEN)
    ap.add_argument("--modelle", default=MODELLE)
    ap.add_argument("--zeige", nargs=2, metavar=("QUELLE", "URL_ODER_DATEI"))
    ap.add_argument("--modell", help="mit --zeige: Modell-id für EAN und Korridor")
    a = ap.parse_args(argv)
    quellen = lade(a.quellen)["quellen"]
    modelle = lade(a.modelle)["modelle"]
    fehler = pruefe_daten(quellen, modelle)
    if fehler:
        print("Datenfehler:\n  " + "\n  ".join(fehler), file=sys.stderr)
        return 2
    if a.zeige:
        qid, ziel = a.zeige
        q = {x["id"]: x for x in quellen}[qid]
        if os.path.exists(ziel):
            text = open(ziel, encoding="utf-8").read()
        else:  # Abruf nur wie im Lauf: freigegebene Quelle, robots.txt und URL-Regeln
            rp = robots_fuer(q) if q.get("automatisch") is True else "Quelle nicht freigegeben"
            ok, grund = (False, rp) if isinstance(rp, str) else url_erlaubt(ziel, q, rp)
            if not ok:
                print("nicht abgerufen:", grund, file=sys.stderr)
                return 3
            time.sleep(PAUSE)
            text = abrufen(ziel)
        for b in jsonld_bloecke(text):
            for p in produkte(b):
                print("Product:", str(p.get("name"))[:80], "| EAN", sorted(eans(p)), "| MPN", p.get("mpn"))
                for o in angebote_von(p):
                    pr, cur = preis_von(o)
                    print("   ", pr, cur, _endung(o.get("availability")), _endung(o.get("itemCondition")),
                          "| Verkäufer:", verkaeufer_von(o) or "-", "| Versand:", versand_von(o))
        if a.modell:
            m = {x["id"]: x for x in modelle}[a.modell]
            g, prot = auswerten_seite(text, m, q, ziel, "jetzt")
            print(json.dumps({"gueltig": g, "geprueft": prot}, ensure_ascii=False, indent=1))
        return 0
    erg = lauf(quellen, modelle)
    tmp = a.aus + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(erg, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, a.aus)
    for mid, e in erg["modelle"].items():
        b = e["bestpreis"]
        print(f"{mid:14} " + (f"{b['gesamt'] if b['gesamt'] is not None else b['preis']} € bei {b['haendler']} ({b['quelle']})"
                              if b else "kein gültiges Angebot"),
              "|", ", ".join(f"{k}: {v['status']}" for k, v in e["quellen"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
