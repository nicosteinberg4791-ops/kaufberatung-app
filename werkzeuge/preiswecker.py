# -*- coding: utf-8 -*-
"""Preiswecker (Runde 6; ab 09.11.2026 mit Air Fryern, ab V21 alle zehn der Top 10; ab 15.11.2026 auch die Fernseher in
55/65/75–77″): liest die heise-Preisvergleich-Seiten der fünf Fernseher (83/85″), neun Größenvarianten und zehn Air Fryer (nur GET, kein Konto,
kein Formular) und gibt je Modell das günstigste Angebot als JSON aus.

Herkunft: Stand R4 aus Runde 6 (Codex bestanden), übernommen am 08.11.2026; geändert nur die Pfade in diesem Kopf.

Aufruf:  python -X utf8 -I werkzeuge/preiswecker.py            (alle Modelle, JSON auf stdout)
         python -X utf8 -I werkzeuge/preiswecker.py --datei X   (statt Abruf eine gespeicherte Seite auswerten)

Versand: heise nennt die Versandkosten nur als Freitext je Händler. Freitext ergibt NIE 0 € (R6-02, Livelauf: 0 von 33
Angeboten nutzten den Freitextpfad). Sicher 0 € ist der Versand nur bei „merchant_free_shipping“ wahr. Ein
ausdrücklicher Betrag („Versand € 69,99“, „Spedition € 79,90“) wird addiert; alles andere ist „unklar“ (der Text bleibt
als versandtext erhalten). Das Ergebnis trennt deshalb:
  sicher  = günstigster Gesamtpreis mit belegtem Versand
  roh     = günstigster Artikelpreis, falls billiger und Versand unklar (nur Hinweis, kein Alarm)

Abgleich:  python -X utf8 -I werkzeuge/preiswecker.py --abgleich <db-Ordner> --aus <Ausgabe> [--anlegen]
Schreibregel (Versionspin, R6-01): Ohne --anlegen enthält writes.json NIE ein Element ohne if_version. Je Dokument
(preise/<id>, wecker/lauf) gilt:
  ok      = lesbar mit ganzzahliger Version -> set mit if_version.
  fehlt   = in keinem Export enthalten (weder <sammlung>/<id>.json noch Eintrag in <sammlung>.json), Sammlungsexport
            lesbar oder ganz ohne Export -> OHNE --anlegen: Fehler vermerkt, KEIN Schreibauftrag;
            MIT --anlegen (ausdrücklicher Erstlauf, db leer): Anlegen ohne if_version.
  defekt  = Datei vorhanden, aber unlesbar, kein JSON, kein Objekt oder ohne Version (auch unlesbare Sammlungsdatei)
            -> immer Fehler vermerkt, KEIN Schreibauftrag (auch mit --anlegen).
Ungepinntes set nur beim Erstlauf (--anlegen). Das Zielsystem (ArtifactData) verweigert jedes Schreiben ohne
if_version auf ein bereits vorhandenes Dokument; im batch schreibt dann der ganze batch nichts. Ungepinntes set =
atomares „nur anlegen, falls nicht vorhanden“; bestehende Daten können so nicht überschrieben werden.
Die tägliche Aufgabe ruft nie --anlegen auf.
Ein fehlender/defekter Laufexport (wecker/lauf) zählt wie ein Modellfehler: Status „teilweise“ und Text nennt ihn.
Altdokumente mit falschen Typen (verlauf nicht Liste, meldung nicht Objekt) werden als leer behandelt (Warnung);
ein Fehler in einem Modell stoppt die anderen nicht.
Nur Standardbibliothek.
"""
import html
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

MODELLE = {
    "lg_c6elb": "https://preisvergleich.heise.de/lg-oled-evo-ai-c6-oled83c6elb-a3774767.html",
    "lg_c69lb": "https://preisvergleich.heise.de/lg-oled-evo-ai-c6-oled83c69lb-a3773534.html",
    "sam_s90h": "https://preisvergleich.heise.de/samsung-gq8390h-a3805643.html",
    "tcl_c8l": "https://preisvergleich.heise.de/tcl-85c8l-a3810591.html",
    "sam_qn90f": "https://preisvergleich.heise.de/samsung-qe85qn90f-a3479298.html",
    # Größenwahl (V23): dieselben Fernseher in 55/65/75–77″ (Nico, 15.11.2026 „Ja, alle Größen“). heise-Seiten aus
    # kaufberatung/daten/groessen.json (Recherche 14.11.2026). Id = <Modell>_<Größenstufe>; Stufe 77 ist bei TCL der 75C8L.
    # LG C69LB hat in 55/65/77″ kein belegtes Angebot und fehlt deshalb hier.
    "lg_c6elb_55": "https://preisvergleich.heise.de/lg-oled-evo-ai-c6-oled55c6elb-a3774754.html",
    "lg_c6elb_65": "https://preisvergleich.heise.de/lg-oled-evo-ai-c6-oled65c6elb-a3774758.html",
    "lg_c6elb_77": "https://preisvergleich.heise.de/lg-oled-evo-ai-c6-oled77c6elb-a3774764.html",
    "sam_s90h_55": "https://preisvergleich.heise.de/samsung-gq5s90h-a3805570.html",
    "sam_s90h_65": "https://preisvergleich.heise.de/samsung-gq6s90h-a3805608.html",
    "sam_s90h_77": "https://preisvergleich.heise.de/samsung-gq7790h-a3805616.html",
    "tcl_c8l_55": "https://preisvergleich.heise.de/tcl-55c8l-a3810824.html",
    "tcl_c8l_65": "https://preisvergleich.heise.de/tcl-65c8l-a3810509.html",
    "tcl_c8l_77": "https://preisvergleich.heise.de/tcl-75c8l-a3810580.html",
    # Air Fryer (Nico, 09.11.2026 „Ja, aufnehmen“): heise-Produktseiten per heise-Suche nach der Modellnummer gefunden.
    # Medion: heise führt vier Einträge zur MD11760 (Nummern 50072937/50072938/50078168/50079506); gewählt ist der
    # Eintrag „XXL Twin“, der zur Modellbezeichnung P20 XXL Twin passt (Variantenwahl offen für Nicos Bestätigung).
    "af_cosori_tt": "https://preisvergleich.heise.de/cosori-turbo-tower-pro-smart-schwarz-gold-caf-dc123s-dder-a3472492.html",
    "af_medion_p20": "https://preisvergleich.heise.de/medion-md-11760-xxl-twin-50079506-a3787540.html",
    "af_cosori_r901": "https://preisvergleich.heise.de/cosori-doppel-heissluftfritteuse-schwarz-caf-r901-aeu-a3146998.html",
    # Restliche Modelle der Air Fryer Top 10 (Nico, 09.11.2026 „für alle modelle preiswecker“), heise-Suche nach Modellnummer.
    # Bei mehreren Farbvarianten ist der Grundeintrag gewählt (Ninja DZ400EU, AF500EU), bei Tefal die im Bericht genannte EY942BE0.
    "af_caso_3186": "https://preisvergleich.heise.de/caso-airfry-duochef-3186-a3417119.html",
    "af_aeg_aafd11b": "https://preisvergleich.heise.de/aeg-8000-aafd11b-910-004-063-a3916554.html",
    "af_rh_27680": "https://preisvergleich.heise.de/russell-hobbs-satisfry-dual-basket-9l-27680-56-a3487630.html",
    "af_ninja_dz400": "https://preisvergleich.heise.de/ninja-dz400eu-max-6-in-1-dual-zone-a3525190.html",
    "af_tefal_ey942": "https://preisvergleich.heise.de/tefal-ey942b-dual-easy-fry-ey942be0-a3535540.html",
    "af_gastroback_42586": "https://preisvergleich.heise.de/gastroback-42586-multi-duo-family-9l-a3785334.html",
    "af_ninja_af500": "https://preisvergleich.heise.de/ninja-af500eu-foodi-flexdrawer-a3337334.html",
}
# Plausibler Artikelpreisbereich je Modell (€); Fernseher 500–20000, Air Fryer 30–1000 (verwirft Zubehör/Fehlwerte)
GRENZEN = {mid: (30, 1000) for mid in MODELLE if mid.startswith("af_")}
GRENZE_STANDARD = (500, 20000)


def ist_groesse(mid):
    """Größenvariante eines Fernsehers (<modell>_55/65/77): wird abgefragt und gespeichert, meldet aber nichts."""
    return mid.startswith(("lg_c6elb_", "sam_s90h_", "tcl_c8l_"))
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
    if o.get("merchant_free_shipping") is True or o.get("merchant_free_shipping") == 1:
        return 0.0, t
    # Freitext (auch „versandkostenfrei“) belegt keinen Versand: unklar
    return None, t


def sterne(o):
    r = (o.get("merchant_stars") or {}).get("rating") or {}
    s, n = r.get("stars"), r.get("amount")
    if isinstance(s, (int, float)) and isinstance(n, int) and n > 0:
        return f"{s:.1f}".replace(".", ",") + f" ({n:,})".replace(",", ".")
    return "keine Bewertung"


def auswerten(text, grenzen=GRENZE_STANDARD):
    liste = []
    for o in angebote(text):
        preis = o.get("raw_price")
        if not isinstance(preis, (int, float)) or not grenzen[0] <= preis <= grenzen[1]:
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


def abrufen(url, bis=None):
    """Seite holen. bis = Termin auf der time.monotonic()-Uhr (Codex B429-01): Socket-Timeout höchstens bis dahin
    (max. 30 s), gelesen wird blockweise; ist der Termin während des Lesens überschritten, folgt TimeoutError.
    Eine tröpfelnde Antwort überzieht den Termin so höchstens um ein Socket-Timeout."""
    t = 30 if bis is None else max(1, min(30, bis - time.monotonic()))
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "de-DE,de;q=0.9"})
    teile = []
    with urllib.request.urlopen(req, timeout=t) as r:
        while True:
            if bis is not None and time.monotonic() > bis:
                raise TimeoutError("Lauffrist während des Abrufs erreicht")
            b = r.read1(65536)  # read1: höchstens ein Socket-Empfang je Aufruf (read() füllt den Block ganz)
            if not b:
                break
            teile.append(b)
    return b"".join(teile).decode("utf-8", "replace")


NAMEN = {"lg_c6elb": "LG OLED83C6ELB", "lg_c69lb": "LG OLED83C69LB", "sam_s90h": "Samsung GQ83S90H",
         "tcl_c8l": "TCL 85C8L", "sam_qn90f": "Samsung QE85QN90F",
         "lg_c6elb_55": "LG OLED55C6ELB", "lg_c6elb_65": "LG OLED65C6ELB", "lg_c6elb_77": "LG OLED77C6ELB",
         "sam_s90h_55": "Samsung GQ55S90H", "sam_s90h_65": "Samsung GQ65S90H", "sam_s90h_77": "Samsung GQ77S90H",
         "tcl_c8l_55": "TCL 55C8L", "tcl_c8l_65": "TCL 65C8L", "tcl_c8l_77": "TCL 75C8L",
         "af_cosori_tt": "Cosori Turbo Tower Pro Smart", "af_medion_p20": "Medion P20 XXL Twin", "af_cosori_r901": "Cosori Dual Basket R901",
         "af_caso_3186": "Caso AirFry DuoChef 3186", "af_aeg_aafd11b": "AEG AAFD11B", "af_rh_27680": "Russell Hobbs SatisFry Dual 27680-56",
         "af_ninja_dz400": "Ninja Dual Zone DZ400EU", "af_tefal_ey942": "Tefal Easy Fry Dual XXL EY942", "af_gastroback_42586": "Gastroback Duo Family 42586",
         "af_ninja_af500": "Ninja FlexDrawer AF500EU"}
KURZ = {"lg_c6elb": "LG C6ELB", "lg_c69lb": "LG C69LB", "sam_s90h": "Samsung S90H", "tcl_c8l": "TCL C8L", "sam_qn90f": "Samsung QN90F",
        "lg_c6elb_55": "LG C6 55″", "lg_c6elb_65": "LG C6 65″", "lg_c6elb_77": "LG C6 77″",
        "sam_s90h_55": "Samsung S90H 55″", "sam_s90h_65": "Samsung S90H 65″", "sam_s90h_77": "Samsung S90H 77″",
        "tcl_c8l_55": "TCL C8L 55″", "tcl_c8l_65": "TCL C8L 65″", "tcl_c8l_77": "TCL C8L 75″",
        "af_cosori_tt": "Cosori Turbo Tower", "af_medion_p20": "Medion P20 XXL", "af_cosori_r901": "Cosori R901",
        "af_caso_3186": "Caso DuoChef", "af_aeg_aafd11b": "AEG AAFD11B", "af_rh_27680": "Russell Hobbs 27680", "af_ninja_dz400": "Ninja DZ400",
        "af_tefal_ey942": "Tefal EY942", "af_gastroback_42586": "Gastroback 42586", "af_ninja_af500": "Ninja AF500"}
ENDE = "2026-12-01"


WARTE_429 = 30          # Sekunden nach HTTP 429 ohne brauchbares Retry-After
WARTE_429_MAX = 120     # höchstens so lange je Wiederholung
WARTE_429_SUMME = 240   # Wartebudget je Lauf (Workflow-Timeout 10 min), danach keine Wiederholung mehr
# Gesamtfrist für alle Abrufe (Codex B429-01): Workflow-Timeout 10 min, davor Checkout, danach Meldung und Push.
# Ein Abruf beginnt nur, wenn noch ABRUF_MAX (urlopen-Timeout in abrufen) Rest bleibt; sonst Abruffehler „Lauffrist“.
LAUF_FRIST = 420
ABRUF_MAX = 30


def _warte_429(e):
    """Wartezeit nach HTTP 429: Retry-After in Sekunden (1…WARTE_429_MAX), sonst WARTE_429."""
    try:
        s = int(str((e.headers or {}).get("Retry-After", "")).strip())
        return s if 1 <= s <= WARTE_429_MAX else WARTE_429
    except (ValueError, AttributeError):
        return WARTE_429


def _mit_frist(fn, sekunden):
    """fn() in einem Daemon-Thread; läuft er nach `sekunden` noch, TimeoutError (Codex B429-01 R3).
    Erzwingt die Frist unabhängig vom Netzwerkaufruf (DNS, Verbindungsaufbau, tröpfelndes Lesen);
    ein hängender Thread bleibt zurück und endet mit dem Prozess."""
    erg = {}

    def lauf():
        try:
            erg["wert"] = fn()
        except BaseException as e:  # im Hauptthread erneut auslösen (u. a. HTTPError für die 429-Wiederholung)
            erg["fehler"] = e
    t = threading.Thread(target=lauf, daemon=True)
    t.start()
    t.join(sekunden)
    if t.is_alive():
        raise TimeoutError(f"Abruf nach {sekunden:.0f} s abgebrochen (Lauffrist)")
    if "fehler" in erg:
        raise erg["fehler"]
    return erg["wert"]


def _kurzliste(titel, namen, sep, platz):
    """„Titel: a, b. “ – passt die Liste nicht in platz Zeichen: „Titel (n): a, +k weitere. “ (B429-02)."""
    voll = f"{titel}: {sep.join(namen)}. "
    if len(voll) <= platz:
        return voll
    for k in range(len(namen) - 1, -1, -1):
        s = f"{titel} ({len(namen)}): " + "".join(x + sep for x in namen[:k]) + f"+{len(namen) - k} weitere. "
        if len(s) <= platz or k == 0:
            return s


def abruf_alle():
    jetzt = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    erg = {"zeit": jetzt, "modelle": {}}
    budget = WARTE_429_SUMME
    start = time.monotonic()

    def rest():
        return LAUF_FRIST - (time.monotonic() - start)
    for mid, url in MODELLE.items():
        if rest() < ABRUF_MAX:  # Frist reicht nicht für einen weiteren Abruf: nicht abrufen, als Abruffehler melden
            erg["modelle"][mid] = {"url": url, "fehler": f"Lauffrist {LAUF_FRIST} s erreicht, nicht abgerufen"}
            continue
        for versuch in (1, 2):
            try:
                seite = _mit_frist(lambda: abrufen(url, bis=start + LAUF_FRIST), max(1, rest()))
                erg["modelle"][mid] = {"url": url, **auswerten(seite, GRENZEN.get(mid, GRENZE_STANDARD))}
                break
            except urllib.error.HTTPError as e:
                # B-429 (15.11.2026): heise drosselt ab ~19 Abrufen kurz hintereinander; einmal warten und wiederholen
                w = _warte_429(e) if e.code == 429 else 0
                if versuch == 1 and w and w <= budget and w + ABRUF_MAX <= rest():
                    budget -= w
                    time.sleep(w)
                    continue
                erg["modelle"][mid] = {"url": url, "fehler": f"{type(e).__name__}: {str(e)[:120]}"}
                break
            except Exception as e:  # Abruf- oder Formatfehler: Modell als Fehler melden, weiter mit den anderen
                erg["modelle"][mid] = {"url": url, "fehler": f"{type(e).__name__}: {str(e)[:120]}"}
                break
        time.sleep(2)
    return erg


def eur(x):
    t = f"{x:,.0f}" if abs(x - round(x)) < 1e-9 else f"{x:,.2f}"
    return t.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def _felder_version(o):
    """Aus einem Dokumentobjekt (mit oder ohne Hülle) (Felder, Version oder None) ziehen."""
    ver = next((o[k] for k in ("version", "_version", "__version__") if isinstance(o.get(k), int) and not isinstance(o.get(k), bool)), None)
    felder = o.get("data") if isinstance(o.get("data"), dict) else o
    felder = {k: v for k, v in felder.items() if k not in ("version", "_version", "__version__", "id", "doc_id", "path")}
    return felder, ver


def lies_doc(db_dir, sammlung, doc_id):
    """Von ArtifactData (out_dir) gespeichertes Dokument lesen: (Felder, Version, Status).
    Status: "ok" (lesbar mit Version), "fehlt" (in keinem Export, Sammlung lesbar oder ganz ohne Export),
            "defekt" (Datei da, aber unlesbar/kein JSON/kein Objekt/keine Version, auch defekter Sammlungsexport)."""
    import os
    einzel = os.path.join(db_dir, sammlung, doc_id + ".json")
    if os.path.exists(einzel):
        try:
            o = json.load(open(einzel, encoding="utf-8"))
        except (OSError, ValueError):
            return {}, None, "defekt"
        if not isinstance(o, dict):
            return {}, None, "defekt"
        felder, ver = _felder_version(o)
        return (felder, ver, "ok") if ver is not None else ({}, None, "defekt")
    sammel = os.path.join(db_dir, sammlung + ".json")
    if os.path.exists(sammel):  # ein Export je Sammlung statt je Dokument (tolerante Lesart)
        try:
            c = json.load(open(sammel, encoding="utf-8"))
        except (OSError, ValueError):
            return {}, None, "defekt"
        eintrag = None
        if isinstance(c, dict):
            for k in ("docs", "documents", "items", "data"):
                if isinstance(c.get(k), (dict, list)):
                    c = c[k]
                    break
        if isinstance(c, dict):
            eintrag = c.get(doc_id)
        elif isinstance(c, list):
            eintrag = next((x for x in c if isinstance(x, dict) and doc_id in (x.get("id"), x.get("doc_id"))), None)
        elif c is not None:
            return {}, None, "defekt"
        if eintrag is None:
            return {}, None, "fehlt"
        if not isinstance(eintrag, dict):
            return {}, None, "defekt"
        felder, ver = _felder_version(eintrag)
        return (felder, ver, "ok") if ver is not None else ({}, None, "defekt")
    return {}, None, "fehlt"


def zahl_ok(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and 0 < x < 100000


def abgleich(erg, db_dir, aus_dir, anlegen=False):
    """Neue Dokumente für preise/<id> und wecker/lauf berechnen, Schreibliste + Meldung ablegen."""
    import os
    os.makedirs(aus_dir, exist_ok=True)
    heute = erg["zeit"][:10]
    writes, treffer, fehler, probleme, warnungen = [], [], [], [], []
    abruf = []  # Modelle, deren Abruf scheiterte (z. B. HTTP 429); zählen wie fehler, eigener Text
    for mid in MODELLE:
        try:
            alt, ver, st = lies_doc(db_dir, "preise", mid)
            if st == "defekt":
                # Exportdatei vorhanden, aber unbrauchbar: nicht blind überschreiben, kein Schreibauftrag
                probleme.append(f"{KURZ[mid]}: db-Export preise/{mid} unlesbar oder ohne Version, nicht geschrieben")
                continue
            if st == "fehlt" and not anlegen:
                probleme.append(f"{KURZ[mid]}: preise/{mid} nicht im db-Export, nicht geschrieben (Erstlauf nur mit --anlegen)")
                continue
            wunsch, _, wst = lies_doc(db_dir, "wunsch", mid)
            if ist_groesse(mid):
                wunsch, wst = {}, "fehlt"  # Wunschpreise gibt es nur für die 83/85″-Modelle
            if wst == "defekt":
                warnungen.append(f"{KURZ[mid]}: Wunschpreis-Export unlesbar, Wunschpreis ignoriert")
            r = erg["modelle"].get(mid, {})
            akt = r.get("sicher")
            if not akt:
                if r.get("fehler"):  # Abruf gescheitert (B-429): nicht als „kein Angebot“ melden
                    code = re.search(r"HTTP Error (\d+)", str(r["fehler"]))
                    abruf.append(KURZ[mid] + (f" (HTTP {code.group(1)})" if code else ""))
                else:
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
                # Größenvarianten (<modell>_55/65/77) nur speichern und anzeigen, keine Meldung/Push (Nico 15.11.2026:
                # Benachrichtigungen bleiben bei den 83/85″-Modellen)
                if tief_alt and not ist_groesse(mid):
                    treffer.append(f"{KURZ[mid]} {eur(g)} neuer Tiefstpreis")
            vl = alt.get("verlauf", [])
            if not isinstance(vl, list):  # z. B. null oder Text im Altdokument
                warnungen.append(f"{KURZ[mid]}: verlauf im Altdokument kein Feld vom Typ Liste, als leer behandelt")
                vl = []
            verlauf = [v for v in vl if isinstance(v, dict) and v.get("d") != heute and zahl_ok(v.get("g"))]
            neu["verlauf"] = (verlauf + [{"d": heute, "g": g, "h": akt["haendler"]}])[-60:]
            wp = wunsch.get("preis")
            unter = zahl_ok(wp) and g <= wp
            ma = alt.get("meldung")
            if ma is not None and not isinstance(ma, dict):
                warnungen.append(f"{KURZ[mid]}: meldung im Altdokument kein Objekt, als leer behandelt")
                ma = {}
            ma = ma or {}
            war_unter = bool(ma.get("unter_wunsch")) and ma.get("wunsch") == wp
            if unter and not war_unter:
                treffer.append(f"{KURZ[mid]} {eur(g)} unter Wunschpreis {eur(wp)}")
            neu["meldung"] = {"unter_wunsch": bool(unter), "wunsch": wp if zahl_ok(wp) else None}
            datei = os.path.join(aus_dir, f"preise_{mid}.json")
            json.dump(neu, open(datei, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            w = {"op": "set", "collection": "preise", "doc_id": mid, "file_path": os.path.abspath(datei)}
            # Ungepinntes set nur beim Erstlauf (--anlegen). Das Zielsystem (ArtifactData) verweigert jedes Schreiben ohne
            # if_version auf ein bereits vorhandenes Dokument; im batch schreibt dann der ganze batch nichts. Ungepinntes set =
            # atomares „nur anlegen, falls nicht vorhanden“; bestehende Daten können so nicht überschrieben werden.
            # Die tägliche Aufgabe ruft nie --anlegen auf.
            if st == "ok":
                w["if_version"] = ver
            writes.append(w)
        except Exception as e:  # ein kaputtes Modell darf die anderen und die Ausgabedateien nicht stoppen
            probleme.append(f"{KURZ[mid]}: {type(e).__name__}: {str(e)[:100]}")
    n_ok = len(MODELLE) - len(fehler) - len(abruf) - len([x for x in probleme if not x.startswith("wecker/lauf")])
    fehler_alle = fehler + abruf
    lauf_alt, lauf_ver, lst = lies_doc(db_dir, "wecker", "lauf")
    if lst == "defekt":
        probleme.append("wecker/lauf: db-Export unlesbar oder ohne Version, nicht geschrieben")
    elif lst == "fehlt" and not anlegen:
        probleme.append("wecker/lauf: nicht im db-Export, nicht geschrieben (Erstlauf nur mit --anlegen)")
    status = "ok" if not (fehler_alle or probleme) else ("fehler" if n_ok == 0 else "teilweise")
    text = f"Alle {len(MODELLE)} Preise gelesen." if not (fehler_alle or probleme) else ""
    # Codex B429-02: Die Meldung wird auf 300 Zeichen gekürzt. Abruffehler zuerst, dann Fehler, dann „kein Angebot“;
    # jede Liste bekommt den Restplatz abzüglich einer Reserve für die folgenden Teile (Titel + „(n): +k weitere. “);
    # zu lange Listen werden mit „+n weitere“ gekürzt, damit kein Teil ganz verschwindet.
    teile = [(t, n, s) for t, n, s in (("Abruf fehlgeschlagen, alter Preis bleibt", abruf, ", "),
                                       ("Fehler", probleme, "; "),
                                       ("Kein Angebot mit belegtem Versand", fehler, ", ")) if n]
    for i, (titel, namen, sep) in enumerate(teile):
        reserve = sum(len(t) + 22 for t, _, _ in teile[i + 1:])
        text += _kurzliste(titel, namen, sep, max(40, 300 - len(text) - reserve))
    if treffer:
        text += "Treffer: " + "; ".join(treffer) + "."
    text = text.strip()
    lauf = {"letzter": erg["zeit"], "status": status, "meldung": text[:300], "bis": ENDE}
    datei = os.path.join(aus_dir, "wecker_lauf.json")
    json.dump(lauf, open(datei, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if lst == "defekt" or (lst == "fehlt" and not anlegen):
        pass  # Fehler steht oben schon in probleme (Status/Text), kein Schreibauftrag
    else:
        w = {"op": "set", "collection": "wecker", "doc_id": "lauf", "file_path": os.path.abspath(datei)}
        # Ungepinntes set nur beim Erstlauf (--anlegen). Das Zielsystem (ArtifactData) verweigert jedes Schreiben ohne
        # if_version auf ein bereits vorhandenes Dokument; im batch schreibt dann der ganze batch nichts. Ungepinntes set =
        # atomares „nur anlegen, falls nicht vorhanden“; bestehende Daten können so nicht überschrieben werden.
        # Die tägliche Aufgabe ruft nie --anlegen auf.
        if lst == "ok":
            w["if_version"] = lauf_ver
        writes.append(w)
    json.dump(writes, open(os.path.join(aus_dir, "writes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    push = ("TV-Preiswecker: " + "; ".join(treffer))[:195] if treffer else ""
    open(os.path.join(aus_dir, "meldung.txt"), "w", encoding="utf-8").write(push)
    for x in probleme + warnungen:
        print("WARNUNG/FEHLER: " + x, file=sys.stderr)
    return {"status": status, "treffer": treffer, "push": push, "writes": len(writes), "lauf": text,
            "fehler": probleme, "warnungen": warnungen}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "--datei":
        print(json.dumps(auswerten(open(a[1], encoding="utf-8").read()), ensure_ascii=False, indent=1))
        return
    anlegen = "--anlegen" in a
    rest = [x for x in a if x != "--anlegen"]
    if len(rest) == 4 and rest[0] == "--abgleich" and rest[2] == "--aus":
        # rest[1] = Ordner mit den per ArtifactData (out_dir) gespeicherten Dokumenten, rest[3] = Ausgabeordner
        erg = abruf_alle()
        print(json.dumps(abgleich(erg, rest[1], rest[3], anlegen), ensure_ascii=False, indent=1))
        return
    print(json.dumps(abruf_alle(), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
