# -*- coding: utf-8 -*-
"""Gemeinsamer Abrufhelfer für die Datenpflege-Subagenten (werkzeuge/datenpflege/abruf.py).

Aufruf:  python -I abruf.py <https-URL> [--text N]
- Je Domain höchstens 1 Abruf pro 60 s, über ALLE parallel laufenden Agenten (Dateisperre + Zeitstempel je Domain).
  Wartet bei Bedarf selbst; nie umgehen.
- Jeder einzelne HTTP-Versuch steht unter dem Takt (F-04): keine Wiederholung innerhalb eines Abrufs.
- robots.txt (F-06): Ablage je Domain höchstens 24 h alt (Abruf im Takt), ausgewertet nach RFC 9309 für den gesendeten
  User-Agent (sonst Gruppe *), mit Platzhaltern * und $, längste Regel gewinnt; unlesbar, leer oder keine echte
  robots.txt → Abbruch (fail-closed). Saturn-/MediaMarkt-Pfadsperren (GESPERRT_PFADE) gelten zusätzlich.
- 403/429/503/Captcha: Abbruch mit Exit 3. Nicht wiederholen, nicht umgehen; die Domain für 30 min meiden (Sperrdatei).
- Ausgabe: JSON mit Status, gespeicherter Datei (HTML), Produkten aus JSON-LD (Name, Marke, MPN, GTIN, Preis, Verkäufer)
  und optional den ersten N Zeichen des sichtbaren Textes (--text N).
"""
import hashlib
import html
import json
import math
import os
import re
import stat
import sys
import time
import urllib.error
import urllib.request
import urllib.parse
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
ROBOTS_MAX_ALTER = 24 * 3600
GESPERRT_PFADE = [r"/de/search", r"/de/list/", r"/de/promo-list/", r"storeId=", r"/rest/", r"\.json(\?|$)"]
SPERRDAUER = 1800   # Sperrvermerk nach 401/403/429/503/Challenge: Domain 30 min meiden

# Gewöhnlicher Hostname (RFC 1123): Bezeichner aus a-z, 0-9 und -, je 1–63 Zeichen, ohne - am Rand, durch Punkte getrennt
_HOSTNAME = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*")
_GERAETE = frozenset(["con", "prn", "aux", "nul", "conin$", "conout$"] + [f"{a}{z}" for a in ("com", "lpt")
                                                                          for z in "0123456789¹²³"])


def host_schluessel(host):
    """Gemeinsamer Dateischlüssel je Host für Sperr-, Zeit- und Sperrvermerkdatei (R6-02): unter Windows zulässig und
    eindeutig. Ein gewöhnlicher Hostname bis 100 Zeichen (Pfad bleibt unter MAX_PATH), dessen erster Bezeichner kein Windows-Gerätename ist, bleibt
    wie er ist (vorhandene Stempel gelten weiter). Alles andere (IPv6, Zonen-ID, Nicht-ASCII, Gerätenamen, Punkt am
    Ende, zu lang) wird zu „h--<SHA-256>“: dessen erster Bezeichner ist 67 Zeichen lang und damit nie ein gewöhnlicher
    Hostname. Groß-/Kleinschreibung wie bei urlsplit().hostname. ValueError bei leerem Host."""
    if not host:
        raise ValueError("URL ohne Host")
    host = host.lower()
    if len(host) <= 100 and _HOSTNAME.fullmatch(host) and host.split(".")[0] not in _GERAETE:
        return host
    return "h--" + hashlib.sha256(host.encode("utf-8", "surrogatepass")).hexdigest()


def takt_datei(host, endung):
    """Datei des Domaintakts für host (.lock, .zeit, .gesperrt) unter dem gemeinsamen Schlüssel (R6-02)."""
    return TAKT / (host_schluessel(host) + endung)


def sperre_versuchen(domain):
    """Domainsperre als Betriebssystem-Dateisperre (R3-04) auf der dauerhaft liegenden Datei <domain>.lock: genau ein
    Inhaber, frei beim Prozessende (auch nach Absturz), kein Altern und kein Löschen. Rückgabe Dateiobjekt oder None."""
    f = open(takt_datei(domain, ".lock"), "a+b")
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
    """Sperre lösen und Datei schließen; die Datei bleibt liegen (sie sperrt ohne Inhaber nichts)."""
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


def sperre_holen(domain):
    """Wartet auf die Domainsperre (höchstens 30 min), danach auf den Abstand seit dem letzten Abruf. Warten, Abruf und
    Zeitstempel laufen unter derselben Sperre (holen()). Rückgabe (Sperre, Zeitstempeldatei)."""
    start = time.time()
    while True:
        lock = sperre_versuchen(domain)
        if lock is not None:
            break
        if time.time() - start > 1800:
            raise SystemExit("Zeitüberschreitung beim Warten auf " + domain)
        time.sleep(2)
    stempel = takt_datei(domain, ".zeit")
    try:
        try:   # Codex A2-01: nur ein sicher fehlender Eintrag heißt „kein Stempel“
            os.lstat(stempel)
        except FileNotFoundError:
            warte = 0
        except OSError:   # A2-01 (r3): nicht prüfbar (Rechte o. Ä.) = genau voller Abstand, Stempel nicht lesen
            warte = ABSTAND
        else:
            # A2: nur ein abgeschlossener Abruf zählt ab seinem Ende. Leer, unlesbar (auch Link ohne Ziel), fremde
            # Schreibweise oder die Markierung „laeuft“ (Vorgänger endete während des Versuchs, Versand unbekannt)
            # zählt als „gerade eben“: voller Abstand ab der Übernahme der Sperre (der Vorgänger sendet danach nichts).
            try:
                vergangen = verstrichen(stempel.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):   # nicht lesbar oder nicht dekodierbar = unbekannt
                vergangen = None
            warte = ABSTAND if vergangen is None else ABSTAND - vergangen
        if warte > 0:
            time.sleep(warte)
    except BaseException:
        sperre_freigeben(lock)
        raise
    return lock, stempel


LAEUFT = "laeuft"   # Markierung im Zeitstempel: Abrufversuch begonnen, noch nicht abgeschlossen (A2)


def verstrichen(text):
    """Sekunden seit einem Abschlussstempel „<Wanduhr> <monotone Uhr>“, vorsichtig geschätzt, oder None (unbekannt:
    voller Abstand). A2: gezählt wird das Minimum beider Uhren, nie unter 0. Ein Sprung der Systemuhr verlängert so
    nur die Wartezeit; die monotone Uhr (systemweit seit dem Start) zählt nach einem Neustart weniger als real
    vergangen ist. Gültig ist nur der ganze Text genau in der Schreibweise von stempel_setzen (repr beider Werte,
    genau ein Leerzeichen, kein Vorzeichen); sonst runden float() oder fremde Trennungen still (z. B. „-1e-999“ zu
    -0.0). Nur mögliche Werte: endlich, Wanduhr nicht vor 1970, monotone Uhr zwischen 0 und jetzt (ein größerer Wert
    stammt aus einer früheren Startsitzung oder ist beschädigt). „laeuft …“, alte Einzelwerte, nan und inf: None."""
    teile = text.split()
    if len(teile) != 2:
        return None
    try:
        wand, mono = float(teile[0]), float(teile[1])
    except ValueError:
        return None
    if any(t.startswith("-") for t in teile) or text != f"{wand!r} {mono!r}":
        return None
    jetzt_mono = time.monotonic()
    if not (math.isfinite(wand) and math.isfinite(mono) and wand >= 0 and 0 <= mono <= jetzt_mono):
        return None
    return max(0.0, min(time.time() - wand, jetzt_mono - mono))


def stempel_setzen(stempel, laeuft=False):
    """Zeitstempel des Domaintakts atomar schreiben (R5-01): Hilfsdatei schreiben, auf den Datenträger bringen (fsync),
    dann per os.replace an die Stelle des alten Stempels; ein Abbruch dazwischen lässt den alten Stempel stehen.
    laeuft=True: „laeuft <Wanduhr> <monotone Uhr>“ vor dem Versuch; sonst „<Wanduhr> <monotone Uhr>“ nach dem Versuch
    (A2). Nur der Inhaber der Domainsperre schreibt, daher genügt ein fester Name der Hilfsdatei. Fehler brechen den
    Abruf ab."""
    jetzt = f"{time.time()!r} {time.monotonic()!r}"
    neu = stempel.with_name(stempel.name + ".neu")
    with open(neu, "w", encoding="utf-8", newline="") as f:
        f.write(f"{LAEUFT} {jetzt}" if laeuft else jetzt)
        f.flush()
        os.fsync(f.fileno())
    os.replace(neu, stempel)


def gesperrt_bis(domain):
    """Grund der Domainsperre (nicht leerer Text) oder None. R2-04 (fail-closed): None nur, wenn der Sperrvermerk sicher
    fehlt (FileNotFoundError) oder eine normale Datei ist, die älter als SPERRDAUER ist. Jeder andere Zustand sperrt:
    Prüffehler (Rechte o. Ä.), Link ohne Ziel bzw. Junction, Ordner oder anderer Eintrag (auch alt; von Hand entfernen),
    Lesefehler, nicht dekodierbarer oder leerer Inhalt."""
    s = takt_datei(domain, ".gesperrt")
    try:
        st = os.lstat(s)
    except FileNotFoundError:
        return None
    except OSError as e:
        return f"Sperrvermerk nicht prüfbar ({type(e).__name__})"
    if not stat.S_ISREG(st.st_mode) or getattr(st, "st_reparse_tag", 0):
        return "Sperrvermerk ist keine normale Datei (von Hand prüfen und entfernen)"
    if time.time() - st.st_mtime >= SPERRDAUER:
        return None
    try:
        grund = s.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return f"Sperrvermerk nicht lesbar ({type(e).__name__})"
    return grund or "Sperrvermerk ohne Grund"


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
        stempel_setzen(stempel, laeuft=True)   # R4-03/A2: laufenden Versuch markieren, bevor die Anfrage abgeht
        try:
            r = einmal_abrufen(url)
        except BaseException:
            # Ende des Versuchs. Scheitert der Abschlussstempel, bleibt „laeuft“ (voller Abstand) und die ursprüngliche
            # Ausnahme geht weiter, damit z. B. eine 403 trotzdem den Sperrvermerk schreibt (Vorprüfung, R5-01-Rand)
            try:
                stempel_setzen(stempel)
            except Exception:
                pass
            raise
        stempel_setzen(stempel)   # Ende des Versuchs: der Abstand zählt wie bisher ab dem Ende
    except sa.Weitergeleitet as e:
        print(json.dumps({"url": url, "fehler": "Weiterleitung, nicht verfolgt: " + str(e)}, ensure_ascii=False))
        raise SystemExit(5)
    except sa.NichtAbrufbar as e:
        if re.search(r"HTTP (401|403|429|503)|Challenge|Bot", str(e)):
            takt_datei(domain, ".gesperrt").write_text(str(e), encoding="utf-8")
            print(json.dumps({"url": url, "fehler": "gesperrt (nicht umgehen, Domain 30 min meiden): " + str(e)}, ensure_ascii=False))
            raise SystemExit(3)
        print(json.dumps({"url": url, "fehler": "nicht abrufbar: " + str(e)}, ensure_ascii=False))
        raise SystemExit(6)
    finally:
        sperre_freigeben(lock)   # Datei bleibt liegen (R3-04)
    return r


def einmal_abrufen(url):
    """Genau ein HTTP-Versuch (F-04), sonst wie shopabfrage.abrufen: ehrlicher User-Agent, keine Weiterleitung,
    nur vollständige 200-Antworten, 401/403/429/503/Challenge → NichtAbrufbar. Keine Wiederholung bei 5xx/Netzfehler."""
    req = urllib.request.Request(url, headers={"User-Agent": sa.UA, "Accept-Language": "de-DE,de;q=0.9",
                                               "Accept": "text/html,application/xhtml+xml"})
    try:
        with sa._OPENER.open(req, timeout=sa.TIMEOUT) as r:
            roh = r.read(sa.MAX_BYTES + 1)
            if getattr(r, "status", 200) != 200:
                raise sa.NichtAbrufbar(f"HTTP {r.status} (keine vollständige Antwort)")
            if len(roh) > sa.MAX_BYTES:
                raise sa.NichtAbrufbar("Antwort über der Lesegrenze (abgeschnitten)")
            text = roh.decode(r.headers.get_content_charset() or "utf-8", "replace")
            typ = r.headers.get("Content-Type", "")
            if r.geturl() != url:
                raise sa.Weitergeleitet(f"Weiterleitung auf {r.geturl()[:120]}")
    except urllib.error.HTTPError as e:
        if 300 <= e.code < 400:
            raise sa.Weitergeleitet(f"Weiterleitung (HTTP {e.code}) auf {str(e.headers.get('Location') or '?')[:120]}")
        raise sa.NichtAbrufbar(f"HTTP {e.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise sa.NichtAbrufbar(f"Netzfehler: {getattr(e, 'reason', e)}")
    if sa.ist_challenge(text, typ):
        raise sa.NichtAbrufbar("Bot-Prüfung/Challenge-Seite")
    return text


_UNRESERVIERT = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")


def _norm(s, regel=False):
    """Pfad oder Regel gleich normalisieren (RFC 9309 2.2.2, R2-04): %XX nur für nicht reservierte Zeichen dekodieren,
    sonst groß kodiert lassen; Nicht-ASCII und Leerzeichen UTF-8-kodieren. %2A/%24 bleiben kodiert und damit Literale.
    R3-03 (RFC 9309 2.2.3): im URL-Pfad werden wörtliches * und $ zu %2A/%24, damit kodierte Literalregeln sie treffen;
    in Regeln bleibt * Platzhalter und nur ein abschließendes $ Pfadende, ein $ mitten in der Regel wird %24."""
    ende = regel and s.endswith("$")   # nur das letzte Zeichen einer Regel kann Pfadende sein
    if ende:
        s = s[:-1]
    aus, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "%" and re.fullmatch(r"[0-9A-Fa-f]{2}", s[i + 1:i + 3]):
            z = chr(int(s[i + 1:i + 3], 16))
            aus.append(z if z in _UNRESERVIERT else "%" + s[i + 1:i + 3].upper())
            i += 3
            continue
        if c == "$" or (c == "*" and not regel):
            aus.append("%24" if c == "$" else "%2A")
        else:
            aus.append(urllib.parse.quote(c, safe="") if ord(c) > 126 or ord(c) <= 32 else c)
        i += 1
    return "".join(aus) + ("$" if ende else "")


def _muster(m):
    """robots-Pfadmuster (normalisiert) → regulärer Ausdruck (RFC 9309: * beliebig, $ am Ende = Pfadende)."""
    ende = m.endswith("$")
    kern = m[:-1] if ende else m
    return re.compile(re.escape(kern).replace(r"\*", ".*") + ("$" if ende else ""))


def robots_regeln(text, ua_token):
    """Regeln [(erlaubt, muster)] der Gruppe(n) für ua_token (Groß-/Kleinschreibung egal), sonst der Gruppe(n) *."""
    gruppen, aktuell, agent_zuletzt = [], None, False
    for zeile in (text or "").splitlines():
        z = zeile.split("#", 1)[0].strip()
        if ":" not in z:
            continue
        feld, wert = (x.strip() for x in z.split(":", 1))
        feld = feld.lower()
        if feld == "user-agent":
            if aktuell is None or not agent_zuletzt:
                aktuell = {"agenten": set(), "regeln": []}
                gruppen.append(aktuell)
            aktuell["agenten"].add(wert.lower())
            agent_zuletzt = True
        elif feld in ("allow", "disallow"):
            agent_zuletzt = False
            if aktuell is not None and wert:
                aktuell["regeln"].append((feld == "allow", wert))
    eigen = [g for g in gruppen if ua_token.lower() in g["agenten"]]
    wahl = eigen or [g for g in gruppen if "*" in g["agenten"]]
    return [r for g in wahl for r in g["regeln"]]


def robots_erlaubt(text, ua_token, url):
    """RFC 9309: längstes passendes Muster entscheidet, bei Gleichstand Allow; ohne passende Regel erlaubt."""
    # R4-04: geprüft wird genau das Request-Target, das urllib sendet (Pfad samt "?" auch bei leerer Query, ohne Fragment)
    pfad = _norm(urllib.request.Request(url).selector or "/")
    if pfad == "/robots.txt":
        return True
    best = None
    for erlaubt, roh in robots_regeln(text, ua_token):
        m = _norm(roh, regel=True)   # Vergleich und Länge mit derselben Form (R2-04, R3-03)
        if _muster(m).match(pfad):
            schluessel = (len(m), erlaubt)
            if best is None or schluessel > best:
                best = schluessel
    return True if best is None else best[1]


STANDARDPORT = {"http": 80, "https": 443}


def robots_ursprung(teile):
    """(Schema, Host, effektiver Port) einer URL: robots.txt gilt je Ursprung (RFC 9309 2.3, R5-05). ValueError bei
    fehlendem Host, unbekanntem Schema oder ungültigem Port. Standardport nur ohne Port (auch leer, RFC 3986 3.2.3);
    Port 0 ist kein Standardport, sondern ungültig (R5-05)."""
    scheme, host = teile.scheme.lower(), teile.hostname
    if not host or scheme not in STANDARDPORT:
        raise ValueError("URL ohne Host oder mit unbekanntem Schema")
    port = teile.port   # wirft ValueError bei ungültigem Port
    if port is None:
        return scheme, host, STANDARDPORT[scheme]
    if port == 0:
        raise ValueError("Port 0")
    return scheme, host, port


def robots_ablage(scheme, host, port):
    """Ablagedatei der robots.txt eines Ursprungs (R5-05): Name aus dem SHA-256 des vollständigen Ursprungs, also
    eindeutig je (Schema, Host, Port) und unter Windows zulässig."""
    ursprung = json.dumps([scheme, host, port], ensure_ascii=True)
    return TAKT / ("robots-" + hashlib.sha256(ursprung.encode("ascii")).hexdigest() + ".json")


def robots_text(scheme, host, port):
    """robots.txt des Ursprungs (Schema, Host, Port) aus der Ablage (höchstens ROBOTS_MAX_ALTER alt) oder frisch im Takt.
    None = nicht auswertbar. Die Domainsperre in holen() bleibt je Host."""
    ablage = robots_ablage(scheme, host, port)
    netz = (f"[{host}]" if ":" in host else host) + ("" if STANDARDPORT[scheme] == port else f":{port}")
    try:
        a = json.loads(ablage.read_text(encoding="utf-8"))
        if time.time() - float(a["zeit"]) < ROBOTS_MAX_ALTER and sa.robots_gueltig(a["text"]):
            return a["text"]
    except (OSError, ValueError, KeyError, TypeError):
        pass
    text = holen(f"{scheme}://{netz}/robots.txt")   # SystemExit 3 (Sperre) geht an den Aufrufer
    if not sa.robots_gueltig(text):
        return None
    ablage.write_text(json.dumps({"zeit": time.time(), "text": text}), encoding="utf-8")
    return text


def robots_ok(url):
    teile = urllib.parse.urlsplit(url)
    for m in GESPERRT_PFADE:
        if re.search(m, teile.path + ("?" + teile.query if teile.query else "")):
            return False, "Pfad laut robots-Regel gesperrt: " + m
    try:
        ursprung = robots_ursprung(teile)
    except ValueError:
        return False, "URL ohne gültigen Ursprung (Schema, Host, Port)"
    domain = ursprung[1]
    try:
        text = robots_text(*ursprung)
    except SystemExit as e:
        if e.code == 3:   # Sperre (403/429/Captcha) an den Aufrufer weitergeben, nicht verschlucken
            raise
        return False, "robots.txt nicht abrufbar"
    if text is None:
        return False, "robots.txt nicht auswertbar (leer oder keine robots.txt) – Abbruch"
    if not robots_erlaubt(text, sa.UA_TOKEN, url):
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
