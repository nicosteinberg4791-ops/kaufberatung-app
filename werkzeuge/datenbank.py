# -*- coding: utf-8 -*-
"""Produktdatenbank der Finder-Suche: prüfen und für die App zusammenbauen.

    python -I werkzeuge/datenbank.py pruefen [--gegen [<commit>]] [datei.json …]   # ohne Datei: alle daten/produkte/*.json
    python -I werkzeuge/datenbank.py bauen <ziel.json> [--herkunft <commit>]   # prüft alles, schreibt kompakte App-Daten
    (--herkunft: 40-stelliger Commit, aus dem gebaut wird; werkzeuge/herkunft.py entscheidet damit über das Ersetzen)
    (--gegen: Freigabeschranke der Gewichtsfassung, Entwurf §9.3. Mit Commit: Referenz ist dessen Schema. Ohne Wert:
     Referenz ist die herkunft der Online-finder-daten.json auf gh-pages (git ls-remote, nie ein vorhandener Ref).)

Format: daten/produkte/FORMAT.md. Schema (Felder, Kurven, Fragen): daten/schema/kategorien.json.
Exitcode 0 = keine Fehler (Warnungen erlaubt), 1 = Fehler. Nur Standardbibliothek.
"""
import json
import math
import re
import sys
import unicodedata
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


KATEGORIE_SCHLUESSEL = {"id", "name", "felder", "fragen", "gewichte_version", "testquelle"}   # §2.2: Positivliste
TESTQUELLE_SCHLUESSEL = {"name", "url", "methodik_url", "stand"}
MASS_FELDER = {"breite_cm", "hoehe_cm", "tiefe_cm"}   # §2.3/§9.7: feste Namen, typ zahl, einheit cm, Werte 0 < x <= 500
MASS_GRENZE = 500
# §9.6: Namen aus Object.prototype (plus prototype) sind als Quellen-ID gesperrt, der Client lehnt sie ab (kennungOk).
GESPERRTE_IDS = {"constructor", "prototype", "hasOwnProperty", "isPrototypeOf", "propertyIsEnumerable", "toString",
                 "toLocaleString", "valueOf", "__proto__", "__defineGetter__", "__defineSetter__", "__lookupGetter__",
                 "__lookupSetter__"}
DNS_HOST = re.compile(r"([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z]([a-z0-9-]*[a-z0-9])?")


def _ohne_doppelte_schluessel(paare):
    """object_pairs_hook (§2.2): json.loads nähme bei doppelten Schlüsseln still den letzten Wert."""
    d = {}
    for k, v in paare:
        if k in d:
            raise ValueError(f"doppelter Schlüssel {k!r}")
        d[k] = v
    return d


def _keine_konstante(name):
    """parse_constant (P2a-2): NaN und Infinity sind keine JSON-Zahlen (Python nähme sie sonst an, der Client nie)."""
    raise ValueError(f"keine JSON-Zahl: {name}")


def schema_laden(text):
    """Schema aus Text, mit denselben Regeln wie lade_schema (auch für die Referenz aus Git, §9.3)."""
    return json.loads(text, object_pairs_hook=_ohne_doppelte_schluessel, parse_constant=_keine_konstante)


def lade_schema():
    s = schema_laden(SCHEMA.read_text(encoding="utf-8"))
    return s, {k["id"]: k for k in s["kategorien"]}


def name_ok(x, n):
    """§9.6 Namensregel: 1..n Codepunkte, kein Zeichen der Klassen Cc, Cf, Cs, Zl, Zp und nicht nur Zs (Leerraum)."""
    if not isinstance(x, str) or not 1 <= len(x) <= n:
        return False
    klassen = [unicodedata.category(c) for c in x]
    return not any(k in ("Cc", "Cf", "Cs", "Zl", "Zp") for k in klassen) and not all(k == "Zs" for k in klassen)


def quellen_id_ok(q):
    """§9.6: ganze Übereinstimmung mit ID (fullmatch, nicht match) und nicht in der Sperrliste."""
    return isinstance(q, str) and ID.fullmatch(q) is not None and q not in GESPERRTE_IDS


def quell_url_ok(u):
    """§9.6: ursprüngliche Zeichenfolge, druckbares ASCII, 1..2000 Zeichen, https, Host ein DNS-Name (kein Userinfo, kein
    Port, keine IP, kein xn--), danach kanon_host."""
    if not isinstance(u, str) or not 1 <= len(u) <= 2000 or not all(0x21 <= ord(c) <= 0x7E for c in u):
        return False
    if not u.startswith("https://"):
        return False
    host = re.split(r"[/?#]", u[len("https://"):], maxsplit=1)[0]
    if not DNS_HOST.fullmatch(host) or any(teil.startswith("xn--") for teil in host.split(".")):
        return False
    return kanon_host(u) is not None


def fassung_fehler(g):
    """Grund, wenn gewichte_version nicht {nummer 1..9999, stand} ist (§2.1/§9.6; Pflicht ab P2a-2, siehe schema_fehler)."""
    if not isinstance(g, dict) or set(g) != {"nummer", "stand"}:
        return "gewichte_version muss genau nummer und stand enthalten"
    if not isinstance(g["nummer"], int) or isinstance(g["nummer"], bool) or not 1 <= g["nummer"] <= 9999:
        return "gewichte_version.nummer muss eine ganze Zahl 1..9999 sein"
    if not ist_datum(g["stand"]):
        return "gewichte_version.stand muss ein Datum JJJJ-MM-TT sein (ab 2020-01-01, nicht in der Zukunft)"
    return None


def testquelle_fehler(t):
    """Grund, wenn testquelle nicht genau {name, url, methodik_url, stand} ist (§2.2, nur Link, D13)."""
    if not isinstance(t, dict):
        return "testquelle muss ein Objekt sein (höchstens eine Primärquelle)"
    if set(t) != TESTQUELLE_SCHLUESSEL:
        return f"testquelle braucht genau {sorted(TESTQUELLE_SCHLUESSEL)} (gefunden {sorted(t)}); keine Noten oder Punkte"
    if not name_ok(t["name"], 80):
        return "testquelle.name: 1..80 Zeichen, keine Steuerzeichen, nicht nur Leerraum"
    if not quell_url_ok(t["url"]) or not quell_url_ok(t["methodik_url"]):
        return "testquelle.url/methodik_url: nur https, DNS-Name, ohne Userinfo und Port, höchstens 2000 ASCII-Zeichen"
    if not ist_datum(t["stand"]):
        return "testquelle.stand muss ein Datum JJJJ-MM-TT sein (ab 2020-01-01, nicht in der Zukunft)"
    return None


# ---- P2a-2, Entwurf §9.3: Vorbedingungen, Projektion und Referenzvergleich der Gewichtsfassung ----
# Kennung wie kennungOk im Client (bewertung.js): [a-z0-9_]+(-[a-z0-9_]+)* als ganze Zeichenfolge, Prototyp-Namen gesperrt
KENNUNG = re.compile(r"[a-z0-9_]+(?:-[a-z0-9_]+)*")
KURVENART = {"zahl": "linear", "bool": "ja_nein", "stufe": "stufen"}
ABSCHLAG_PROJEKTION = ("anker", "faktor", "abzug", "abdeckung_mindest")   # was die Zahl bestimmt (spanne nur Anzeige)


def _js_leer(c):
    """Zeichen, die JS String.prototype.trim entfernt (WhiteSpace und LineTerminator)."""
    return c in "\t\n\v\f\r﻿  " or unicodedata.category(c) == "Zs"


def js_text(x, n=500):
    """istText im Client: Text mit höchstens n UTF-16-Einheiten (String.length)."""
    return isinstance(x, str) and len(x.encode("utf-16-le")) // 2 <= n


def js_name(x, n):
    """istName im Client: istText und nicht leer nach trim."""
    return js_text(x, n) and not all(_js_leer(c) for c in x)


def js_zahl(x, lo, hi):
    """zahlIn im Client: echte, endliche Zahl (kein Wahrheitswert) im Bereich lo..hi."""
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and lo <= x <= hi


def kennung_ok(x):
    return isinstance(x, str) and KENNUNG.fullmatch(x) is not None and x not in GESPERRTE_IDS


def _regeln_fehler(s):
    """regelnPruefen (bewertung.js): datenblatt_abschlag und aufpreis_regeln, sonst verwirft der Client die ganze Datei."""
    f = []
    db = s.get("datenblatt_abschlag")
    if not (isinstance(db, dict) and all(js_zahl(db.get(n), 0, 100) for n in ("anker", "abzug", "spanne_plus_minus"))
            and js_zahl(db.get("faktor"), 0, 2) and js_zahl(db.get("abdeckung_mindest"), 0, 1)):
        return ["datenblatt_abschlag wie im Client ungültig (anker/abzug/spanne 0..100, faktor 0..2, abdeckung_mindest 0..1)"]
    if "getestet" in db:
        m = db["getestet"].get("mischung") if isinstance(db["getestet"], dict) else None
        if not (isinstance(m, dict) and js_zahl(m.get("test"), 0, 1) and js_zahl(m.get("datenblatt_roh"), 0, 1)):
            f.append("datenblatt_abschlag.getestet.mischung wie im Client ungültig (test, datenblatt_roh 0..1)")
    a = s.get("aufpreis_regeln")
    if not (isinstance(a, dict) and isinstance(a.get("aufpreis"), dict) and isinstance(a.get("spar"), dict)):
        return f + ["aufpreis_regeln wie im Client ungültig"]
    ap, sp = a["aufpreis"], a["spar"]
    if not (all(js_zahl(ap.get(n), 0, 100000) for n in ("budget_faktor_max", "aufpreis_min_eur", "punkte_min",
                                                       "punkte_min_datenblatt", "effizienz_min_je_100eur"))
            and js_text(ap.get("text"))):
        f.append("aufpreis_regeln.aufpreis wie im Client ungültig")
    if not (all(js_zahl(sp.get(n), 0, 100000) for n in ("ersparnis_min_eur", "ersparnis_min_anteil", "verlust_max_gleich",
                                                       "verlust_max_schwaecher", "ersparnis_anteil_schwaecher"))
            and js_text(sp.get("text_gleich")) and js_text(sp.get("text_schwaecher"))
            and ("text_gleichauf" not in sp or js_text(sp["text_gleichauf"]))):
        f.append("aufpreis_regeln.spar wie im Client ungültig")
    return f


def _kurve_fehler(f):
    """Nur im Bau (§9.3, P2A2-R3-01): Kurvenart passt zum Typ, Teilpunkte 0..100, lineares x mit |x| < 1e7, Stufen- und
    ja/nein-Werte vom passenden Typ und eindeutig (P2A2-01)."""
    k = f.get("kurve")
    art = k.get("art") if isinstance(k, dict) else None
    if art != KURVENART.get(f.get("typ")) or not isinstance(k.get("punkte"), list) or not k["punkte"]:
        return f"Kurve braucht art {KURVENART.get(f.get('typ'))!r} und Stützpunkte"
    werte = []
    for p in k["punkte"]:
        if not (isinstance(p, list) and len(p) == 2):
            return "Stützpunkt muss [wert, teilpunkte] sein"
        x, y = p
        if not js_zahl(y, 0, 100):
            return f"Teilpunkte {y!r} sind keine Zahl 0..100"
        if art == "linear" and not (js_zahl(x, float("-inf"), float("inf")) and abs(x) < 1e7):
            return f"Stützpunkt {x!r} ist keine Zahl mit |x| < 1e7"
        if (art == "stufen" and not isinstance(x, str)) or (art == "ja_nein" and not isinstance(x, bool)):
            return f"Kurvenwert {x!r} passt nicht zur Kurvenart {art}"
        werte.append(x)
    if art != "linear" and len(set(werte)) != len(werte):
        return "Kurvenwert doppelt"
    return None


def _doppelt(ids):
    gesehen, doppelt = set(), []
    for i in ids:
        if i in gesehen and i not in doppelt:
            doppelt.append(i)
        gesehen.add(i)
    return doppelt


def vorbedingung_fehler(s):
    """§9.3 Vorbedingungen für Kandidat und Referenz (P2A2-01, P2A2-04): eindeutige IDs, das ganze Schema besteht die
    Prüfungen, mit denen datenPruefen die Datei verwirft (alle Kategorien, Felder auch mit Gewicht 0, Fragen, Antworten,
    Regeln), dazu Kurven nur im Bau. Liste der Fehler, leer = Projektion und Bau dürfen laufen."""
    if not isinstance(s, dict) or not isinstance(s.get("kategorien"), list):
        return ["Schema: kategorien fehlt"]
    fehler = [f"Schema: {x}" for x in _regeln_fehler(s)]
    kats = [k for k in s["kategorien"] if isinstance(k, dict)]
    if len(kats) != len(s["kategorien"]):
        fehler.append("Schema: Kategorie ist kein Objekt")
    fehler += [f"Schema: Kategorie-ID {i!r} doppelt" for i in _doppelt(k.get("id") for k in kats)]
    for k in kats:
        kid = k.get("id", "?")
        if not kennung_ok(k.get("id")) or not js_name(k.get("name"), 80):
            fehler.append(f"Schema {kid}: Kennung oder Name der Kategorie wie im Client ungültig")
        felder, fragen = k.get("felder"), k.get("fragen", [])
        if not isinstance(felder, list) or not isinstance(fragen, list):
            fehler.append(f"Schema {kid}: felder muss eine Liste sein, fragen fehlen oder eine Liste sein")
            continue
        felder_ok = [f for f in felder if isinstance(f, dict)]
        fehler += [f"Schema {kid}: Feld-ID {i!r} doppelt" for i in _doppelt(f.get("id") for f in felder_ok)]
        fehler += [f"Schema {kid}: Frage-ID {i!r} doppelt" for i in _doppelt(q.get("id") for q in fragen if isinstance(q, dict))]
        for f in felder:
            fid = f.get("id", "?") if isinstance(f, dict) else "?"
            if not (isinstance(f, dict) and kennung_ok(f.get("id")) and js_name(f.get("name"), 80)
                    and f.get("typ") in KURVENART and js_zahl(f.get("gewicht"), 0, 1000)
                    and "einheit" in f and (f["einheit"] is None or js_text(f["einheit"], 20))):
                fehler.append(f"Schema {kid}/{fid}: Feld wie im Client ungültig (Kennung, Name, typ, gewicht 0..1000, einheit)")
                continue
            if grund := _kurve_fehler(f):
                fehler.append(f"Schema {kid}/{fid}: {grund}")
        for q in fragen:
            qid = q.get("id", "?") if isinstance(q, dict) else "?"
            if not (isinstance(q, dict) and kennung_ok(q.get("id")) and js_text(q.get("text"))
                    and isinstance(q.get("antworten"), list) and q["antworten"]):
                fehler.append(f"Schema {kid}/{qid}: Frage wie im Client ungültig (Kennung, text, antworten)")
                continue
            fehler += [f"Schema {kid}/{qid}: Antwort-ID {i!r} doppelt"
                       for i in _doppelt(a.get("id") for a in q["antworten"] if isinstance(a, dict))]
            for a in q["antworten"]:
                aid = a.get("id", "?") if isinstance(a, dict) else "?"
                ok = isinstance(a, dict) and kennung_ok(a.get("id")) and js_text(a.get("text"))
                for n in ("gewichte", "mindest", "hoechst"):
                    ok = ok and (n not in a or (isinstance(a[n], dict) and all(x not in GESPERRTE_IDS for x in a[n])))
                if ok and isinstance(a.get("gewichte"), dict):
                    ok = all(js_zahl(v, 0, 100) for v in a["gewichte"].values())
                if not ok:
                    fehler.append(f"Schema {kid}/{qid}/{aid}: Antwort wie im Client ungültig (Kennung, text, Faktoren 0..100)")
    return fehler


def projektion(s, kid):
    """§9.3: alles, was die Zahl der Kategorie bestimmt, in Normalform (jede Zahl float). Felder mit Gewicht > 0 in
    Schemareihenfolge [{id, typ, gewicht, kurve}], Fragen und Antworten in ihrer Reihenfolge mit id und gewichte, dazu
    datenblatt_abschlag (anker, faktor, abzug, abdeckung_mindest, ggf. getestet.mischung). Ohne mindest/hoechst und
    Felder mit Gewicht 0. Nur nach bestandenen Vorbedingungen aufrufen."""
    k = next(x for x in s["kategorien"] if x["id"] == kid)
    db = s["datenblatt_abschlag"]
    abschlag = {n: float(db[n]) for n in ABSCHLAG_PROJEKTION}
    if "getestet" in db:
        abschlag["mischung"] = {n: float(db["getestet"]["mischung"][n]) for n in ("test", "datenblatt_roh")}
    felder = []
    for f in k["felder"]:
        if f["gewicht"] > 0:
            art = f["kurve"]["art"]
            punkte = [[float(x) if art == "linear" else x, float(y)] for x, y in f["kurve"]["punkte"]]
            felder.append({"id": f["id"], "typ": f["typ"], "gewicht": float(f["gewicht"]),
                           "kurve": {"art": art, "punkte": punkte}})
    fragen = [{"id": q["id"], "antworten": [{"id": a["id"], "gewichte": {fid: float(v) for fid, v in a.get("gewichte", {}).items()}}
                                            for a in q["antworten"]]} for q in k.get("fragen", [])]
    return {"felder": felder, "fragen": fragen, "abschlag": abschlag}


def fassung_gegen_fehler(kandidat, referenz):
    """§9.3 Referenzvergleich je Kategorie. Vorbedingungen für beide Seiten zuerst (sonst keine Projektion). Gleiche
    Projektion → gleiche Nummer; abweichend → größere Nummer und neuer stand; kleinere Nummer immer Fehler; Referenz
    ohne gewichte_version (Schema 1) → Projektion gleich und Nummer 1. Eine neue Kategorie ohne Referenz wird nur auf
    ihre Form geprüft. Liste der Fehler, leer = Fassung freigegeben."""
    fehler = [f"Kandidat: {x}" for x in vorbedingung_fehler(kandidat)]
    fehler += [f"Referenz: {x}" for x in vorbedingung_fehler(referenz)]
    if fehler:
        return fehler
    alt = {k["id"]: k for k in referenz["kategorien"]}
    for k in kandidat["kategorien"]:
        kid, gv = k["id"], k.get("gewichte_version")
        if grund := fassung_fehler(gv):
            fehler.append(f"{kid}: {grund}")
            continue
        if kid not in alt:
            continue
        gleich = projektion(kandidat, kid) == projektion(referenz, kid)
        rv = alt[kid].get("gewichte_version")
        if rv is None:
            if not gleich:
                fehler.append(f"{kid}: Projektion weicht von der Referenz ohne Fassung ab (Fassung 1 darf keine Note ändern)")
            if gv["nummer"] != 1:
                fehler.append(f"{kid}: erste Fassung muss Nummer 1 haben (gefunden {gv['nummer']})")
        elif grund := fassung_fehler(rv):
            fehler.append(f"{kid}: Referenz: {grund}")
        elif gv["nummer"] < rv["nummer"]:
            fehler.append(f"{kid}: Nummer {gv['nummer']} ist kleiner als in der Referenz ({rv['nummer']})")
        elif gleich and gv["nummer"] != rv["nummer"]:
            fehler.append(f"{kid}: Projektion unverändert, Nummer muss {rv['nummer']} bleiben (gefunden {gv['nummer']})")
        elif not gleich and gv["nummer"] == rv["nummer"]:
            fehler.append(f"{kid}: Gewichte, Kurven oder Abschlag geändert, Nummer muss steigen (Referenz {rv['nummer']})")
        elif not gleich and gv["stand"] == rv["stand"]:
            fehler.append(f"{kid}: neue Nummer {gv['nummer']} braucht einen neuen stand (Referenz {rv['stand']})")
    return fehler


def schema_fehler(s):
    """Prüfung des Schemas selbst: schema_version 2, Kategorieschlüssel, gewichte_version Pflicht (P2a-2), testquelle
    (wenn da), Vorbedingungen §9.3, Maßfeldregel, Stufenwerte. Liste der Fehler, leer = gültig."""
    fehler = []
    version = s.get("schema_version") if isinstance(s, dict) else None
    if version != 2 or isinstance(version, bool):
        fehler.append(f"Schema: schema_version muss 2 sein (gefunden {version!r})")
    if not isinstance(s, dict) or not isinstance(s.get("kategorien"), list):
        return fehler + ["Schema: kategorien fehlt"]
    fehler += vorbedingung_fehler(s)
    for k in s["kategorien"]:
        if not isinstance(k, dict):
            continue
        kid = k.get("id", "?")
        for sch in sorted(set(k) - KATEGORIE_SCHLUESSEL):
            fehler.append(f"Schema {kid}: unbekannter Kategorieschlüssel {sch!r} (erlaubt: {', '.join(sorted(KATEGORIE_SCHLUESSEL))})")
        if "gewichte_version" not in k:
            fehler.append(f"Schema {kid}: gewichte_version fehlt (Pflicht ab Schema 2, Entwurf §2.1)")
        elif grund := fassung_fehler(k["gewichte_version"]):
            fehler.append(f"Schema {kid}: {grund}")
        if "testquelle" in k and (grund := testquelle_fehler(k["testquelle"])):
            fehler.append(f"Schema {kid}: {grund}")
        for f in k.get("felder", []) if isinstance(k.get("felder"), list) else []:
            fid = f.get("id") if isinstance(f, dict) else None
            if not isinstance(fid, str):
                continue
            if fid.startswith(("breite", "hoehe", "tiefe")):
                if fid not in MASS_FELDER:
                    fehler.append(f"Schema {kid}/{fid}: Maßfelder heißen genau breite_cm, hoehe_cm oder tiefe_cm")
                elif f.get("typ") != "zahl" or f.get("einheit") != "cm":
                    fehler.append(f"Schema {kid}/{fid}: Maßfeld braucht typ \"zahl\" und einheit \"cm\"")
            if f.get("typ") == "stufe":
                kurve = f.get("kurve") if isinstance(f.get("kurve"), dict) else {}
                for p in kurve.get("punkte", []) if isinstance(kurve.get("punkte"), list) else []:
                    wert = p[0] if isinstance(p, list) and p else p
                    if not name_ok(wert, 200):
                        fehler.append(f"Schema {kid}/{fid}: Stufenwert {wert!r} ungültig (1..200 Zeichen, keine Steuerzeichen)")
    return fehler


def ist_datum(t):
    if not isinstance(t, str) or not DATUM.fullmatch(t):
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
        if not (isinstance(wert, (int, float)) and not isinstance(wert, bool) and wert == wert and abs(wert) < 1e7):
            return False
        return 0 < wert <= MASS_GRENZE if feld.get("id") in MASS_FELDER else True   # §2.3: Maße 0 < x <= 500
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
        if not quellen_id_ok(qid):
            fehler.append(f"{ort}: Quellen-ID {qid!r} ungültig")
        if not (isinstance(q, dict) and quell_url_ok(q.get("url")) and name_ok(q.get("titel"), 200) and ist_datum(q.get("gelesen"))):
            fehler.append(f"{ort}: Quelle {qid} braucht url (https, DNS-Name, ohne Userinfo und Port), titel (1–200 Zeichen), gelesen")
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
        if not isinstance(mid, str) or not ID.fullmatch(mid):
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
            if not isinstance(vid, str) or not ID.fullmatch(vid):
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
    try:
        schema, kats = lade_schema()
    except (OSError, ValueError, KeyError, TypeError) as e:
        return [], [f"Schema nicht lesbar: {e}"], []
    fehler, warnungen, daten, ids = schema_fehler(schema), [], [], set()
    if fehler:   # ein ungültiges Schema (P2a-1): keine Produktprüfung auf unsicherer Grundlage
        return [], fehler, []
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
    daten, fehler, warnungen = alle_pruefen()
    if fehler:
        return daten, fehler, warnungen
    schema, kats = lade_schema()
    aus = {"stand": max((d["stand"] for d in daten), default=None), "regeln": {k: schema[k] for k in
           ("unterschiedsschwelle_punkte", "datenblatt_abschlag", "aufpreis_regeln")}, "kategorien": []}   # D12: ohne klassen
    if herkunft is not None:
        aus["herkunft"] = herkunft
    nach_kat = {d["kategorie"]: d for d in daten}
    for k in schema["kategorien"]:
        d = nach_kat.get(k["id"])
        felder = {f["id"]: f for f in k["felder"]}
        eintrag = {"id": k["id"], "name": k["name"], "felder": [{x: f[x] for x in ("id", "name", "einheit", "typ", "gewicht")} for f in k["felder"]],
                   "fragen": k.get("fragen", []), "modelle": []}
        if "gewichte_version" in k:   # genau {nummer, stand}, im Schema geprüft (schema_fehler)
            eintrag["gewichte_version"] = {x: k["gewichte_version"][x] for x in ("nummer", "stand")}
        if "testquelle" in k:         # genau vier Schlüssel, nur Link (D13)
            eintrag["testquelle"] = {x: k["testquelle"][x] for x in ("name", "url", "methodik_url", "stand")}
        verwendet = {}
        if d:
            for m in d["modelle"]:
                for v in m["varianten"]:
                    w = {**m.get("werte", {}), **v.get("werte", {})}
                    # §9.4: Wert und Beleg je Feld aus derselben Ebene (Variante, sonst Modell); ein Variantenbeleg
                    # ohne Variantenwert gilt nicht (pruefe_datei warnt dazu).
                    b = {fid: (v.get("belege", {}) if fid in v.get("werte", {}) else m.get("belege", {}))[fid] for fid in w}
                    tp = {fid: round(teilpunkte(felder[fid], x), 1) for fid, x in w.items()
                          if fid in felder and felder[fid]["gewicht"] > 0 and teilpunkte(felder[fid], x) is not None}
                    for q in b.values():
                        verwendet[q] = {x: d["quellen"][q][x] for x in ("titel", "url", "gelesen")}
                    eintrag["modelle"].append({
                        "id": v["id"], "modell": m["id"], "hersteller": m["hersteller"], "name": m["name"], "variante": v["name"],
                        "jahr": m.get("jahr"), "werte": w, "belege": b, "teilpunkte": tp, "preis": v.get("preis"),
                        "tests": testlinks(m), "ean": v.get("ean", [])})
        eintrag["quellen"] = dict(sorted(verwendet.items()))   # nur Quellen, auf die ein Beleg verweist (§2.4)
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
        a, gegen = list(sys.argv[2:]), None
        if "--gegen" in a:
            i = a.index("--gegen")
            a.pop(i)
            gegen = a.pop(i).lower() if i < len(a) and re.fullmatch(r"[0-9a-fA-F]{40}", a[i]) else ""
        daten, fehler, warnungen = alle_pruefen(a or None)
        if gegen is not None and not fehler:
            sys.path.insert(0, str(Path(__file__).resolve().parent))   # -I nimmt den Skriptordner nicht in sys.path
            import freigabe
            kandidat = lade_schema()[0]
            fehler = freigabe.gegen_commit_fehler(kandidat, gegen, WURZEL) if gegen else freigabe.lokal_fehler(WURZEL, kandidat)
    for w in warnungen:
        print("WARNUNG", w)
    for f in fehler:
        print("FEHLER ", f)
    n = sum(len(v["varianten"]) for d in daten for v in d.get("modelle", []) if isinstance(v, dict) and isinstance(v.get("varianten"), list))
    print(f"{len(daten)} Dateien · {sum(len(d.get('modelle', [])) for d in daten)} Modelle · {n} Varianten · Fehler {len(fehler)} · Warnungen {len(warnungen)}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
