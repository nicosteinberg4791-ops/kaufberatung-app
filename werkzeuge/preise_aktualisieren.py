# -*- coding: utf-8 -*-
"""Schreibt preise.json für die App aus der täglichen Preisabfrage (werkzeuge/preiswecker.py, Stand R4 aus Runde 6),
optional mit Push auf gh-pages und Text für die ntfy-Benachrichtigung. Läuft täglich in GitHub Actions
(.github/workflows/preise.yml), lokal nur zum Testen.

Die Rechenlogik (günstigster Gesamtpreis mit belegtem Versand, Tiefstpreis, Verlauf 60 Tage, Treffer) bleibt in
preiswecker.py und wird hier nur aufgerufen: preise.json ist dieselbe Datenform wie die db-Dokumente "preise/<id>" und
"wecker/lauf". Die alten Einträge gehen mit "version": 1 als Export in einen Temp-Ordner, abgleich() läuft mit
anlegen=True (preise.json ist die einzige Quelle; ein Modell ohne alten Eintrag wird neu angelegt).

Wunschpreise (optional) nur aus der Umgebungsvariable WUNSCHPREISE (JSON {"lg_c6elb": 2500, ...}, in Actions das
Secret gleichen Namens). Sie erscheinen NIE in preise.json und nie auf stdout (Actions-Logs sind öffentlich), nur im
Benachrichtigungstext (--meldung). Ob ein Treffer neu ist, folgt aus dem gestrigen Preis in preise.json (je Ereignis
eine Meldung, ohne gespeicherten Wunschpreis).

Aufrufe:
  python -X utf8 -I werkzeuge/preise_aktualisieren.py                       neu abrufen, .veroeffentlichung/preise.json schreiben
  python -X utf8 -I werkzeuge/preise_aktualisieren.py --abruf abruf.json    vorhandenes Abrufergebnis (stdout von preiswecker.py)
  ... --ziel dist/preise.json                                               anderes Ziel (lokaler Test)
  ... --push                                                                auf gh-pages pushen (Commit nur aus dem Remote-Stand, siehe push())
  ... --nur-push                                                            vorhandene preise.json im Arbeitsbaum pushen
  ... --meldung datei.txt                                                   Benachrichtigungstext, ein Treffer je Zeile (leer = keine Meldung)
Workflow-Reihenfolge (Codex R1 B2): schreiben -> ntfy senden -> erst dann --nur-push. Scheitert der Versand, bleibt der
alte Stand online und der nächste Lauf erkennt dasselbe Ereignis erneut (mindestens einmal statt höchstens einmal).
  ... --skript <pfad/preiswecker.py>                                        anderes Skript (Tests)
Exitcode 3, wenn kein einziges Modell gelesen wurde (Status "fehler", z. B. heise gesperrt); preise.json ist dann
trotzdem geschrieben (alte Preise, Laufstatus "fehler"), damit die App den Fehler zeigt.
Nur Standardbibliothek.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SEITEN = WURZEL / ".veroeffentlichung"   # git worktree auf dem Zweig gh-pages (veroeffentlichen.py bzw. Workflow)
SKRIPT = WURZEL / "werkzeuge" / "preiswecker.py"


def lade_skript(pfad):
    p = Path(pfad) if pfad else SKRIPT
    if not p.exists():
        raise SystemExit(f"preiswecker.py nicht gefunden: {p}")
    spec = importlib.util.spec_from_file_location("preiswecker", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, p


def zahl_ok(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and 0 < x < 100000


def lies_wunsch(text, modelle):
    """WUNSCHPREISE-Text -> {id: preis}; Ungültiges wird ohne Wert gemeldet und übergangen."""
    if not text or not text.strip():
        return {}
    try:
        roh = json.loads(text)
    except ValueError:
        print("WARNUNG: WUNSCHPREISE ist kein JSON, Wunschpreise ignoriert", file=sys.stderr)
        return {}
    if not isinstance(roh, dict):
        print("WARNUNG: WUNSCHPREISE ist kein Objekt, Wunschpreise ignoriert", file=sys.stderr)
        return {}
    wunsch = {}
    for k, v in roh.items():
        if k in modelle and zahl_ok(v):
            wunsch[k] = float(v)
        else:
            print("WARNUNG: ein Eintrag in WUNSCHPREISE ist unbekannt oder keine gültige Zahl, übergangen", file=sys.stderr)
    return wunsch


def lies_alt(ziel):
    """Bisherige preise.json als dict (fehlt oder unlesbar: {})."""
    try:
        alt = json.loads(Path(ziel).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return alt if isinstance(alt, dict) else {}


def preis_datum(doc):
    """Datum (JJJJ-MM-TT) des aktuellen Preises eines Eintrags, sonst ""."""
    akt = doc.get("aktuell") if isinstance(doc, dict) else None
    z = akt.get("zeit") if isinstance(akt, dict) else None
    return z[:10] if isinstance(z, str) and zahl_ok(akt.get("gesamt")) else ""


def abrufreihe(alt, modelle, heute):
    """Kontingent-Lösung (15.11.2026): nur Modelle ohne Preis von heute, älteste zuerst (fehlende ganz vorn,
    bei Gleichstand MODELLE-Reihenfolge). Mehrere Läufe am Tag holen so nacheinander alle Preise, ohne doppelt zu
    fragen; fällt ein Lauf aus, rückt der älteste Preis am nächsten Tag nach vorn."""
    preise = alt.get("preise") if isinstance(alt.get("preise"), dict) else {}
    lauf = alt.get("lauf") if isinstance(alt.get("lauf"), dict) else {}
    versuche = lauf.get("versuche") if isinstance(lauf.get("versuche"), dict) else {}

    def zeit(mid):
        # Codex KONT-02: Schlüssel = späterer Zeitpunkt aus letztem Preis und letztem Abrufversuch. Ein Modell, das
        # gerade erfolglos versucht wurde, rückt hinter die übrigen; dauerhaft scheiternde Modelle blockieren nicht.
        akt = (preise.get(mid) or {}).get("aktuell") if isinstance(preise.get(mid), dict) else None
        p = akt.get("zeit") if preis_datum(preise.get(mid)) and isinstance(akt.get("zeit"), str) else ""
        v = versuche.get(mid) if isinstance(versuche.get(mid), str) else ""
        return max(p, v)
    offen = [m for m in modelle if preis_datum(preise.get(m)) != heute]
    return sorted(offen, key=lambda m: zeit(m))   # sorted ist stabil: gleiche Zeit -> MODELLE-Reihenfolge


def schreibe_doc(ordner, doc_id, felder):
    ordner.mkdir(parents=True, exist_ok=True)
    (ordner / f"{doc_id}.json").write_text(json.dumps(felder | {"version": 1}, ensure_ascii=False), encoding="utf-8")


def oeffentlicher_lauftext(text, treffer, kurzliste):
    """Laufmeldung ohne Wunschpreis-Treffer (die verraten den Wunschpreis); Tiefstpreis-Treffer bleiben.
    kurzliste = preiswecker._kurzliste (Liste mit „+k weitere“ auf eine Länge bringen)."""
    i = text.find("Treffer:")
    text = (text[:i] if i >= 0 else text).strip()
    oeff = [t for t in treffer if "Wunschpreis" not in t]
    if not oeff:
        return text[:300]
    # Codex B429-03: Abruffehler (Satz am Anfang, aus abgleich) bleiben sichtbar, höchstens 150 Zeichen;
    # die Treffer bekommen den Platz danach (zu viele mit „+k weitere“), der übrige Text (kein Angebot,
    # Fehler) wird zuletzt gekürzt. Die Treffer kommen aus der Liste, nicht aus dem gekürzten Lauftext.
    kopf, rest = "", text
    if text.startswith("Abruf fehlgeschlagen"):
        j = text.find(". ")
        j = len(text) if j < 0 else j + 1
        kopf, rest = text[:j], text[j:].strip()
        if len(kopf) > 150:
            kopf = kopf[:148].rsplit(", ", 1)[0] + " …"
    zusatz = kurzliste("Treffer", oeff, "; ", 300 - len(kopf) - 1).strip()
    platz = 300 - len(kopf) - len(zusatz) - 2
    if len(rest) > platz:
        rest = rest[:max(0, platz - 1)].rstrip() + "…" if platz > 1 else ""
    return " ".join(x for x in (kopf, rest, zusatz) if x)[:300]


def aktualisiere(pw, erg, ziel, wunsch=None):
    wunsch = wunsch or {}
    alt = lies_alt(ziel)
    alt_preise = alt.get("preise") if isinstance(alt.get("preise"), dict) else {}
    # „heute schon gelesen“ nur gelten lassen, wenn preise.json wirklich einen Preis von heute hat; sonst Abruffehler
    # (kein Modell darf ohne heutigen Preis als gelesen zählen)
    for mid, r in erg["modelle"].items():
        if isinstance(r, dict) and r.get("heute_schon") and preis_datum(alt_preise.get(mid)) != erg["zeit"][:10]:
            erg["modelle"][mid] = {"url": r.get("url"), "fehler": "nicht abgerufen, kein Preis von heute vorhanden",
                                  "nicht_versucht": True}
    with tempfile.TemporaryDirectory() as tmp:
        db, aus = Path(tmp, "db"), Path(tmp, "aus")
        for mid, doc in alt_preise.items():
            if mid in pw.MODELLE and isinstance(doc, dict):
                felder = {k: v for k, v in doc.items() if k not in ("meldung", "version")}
                if mid in wunsch:   # gestriger Stand: war der Preis schon unter dem (heutigen) Wunschpreis?
                    g_alt = (doc.get("aktuell") or {}).get("gesamt") if isinstance(doc.get("aktuell"), dict) else None
                    felder["meldung"] = {"unter_wunsch": bool(zahl_ok(g_alt) and g_alt <= wunsch[mid]), "wunsch": wunsch[mid]}
                schreibe_doc(db / "preise", mid, felder)
        for mid, wp in wunsch.items():
            schreibe_doc(db / "wunsch", mid, {"preis": wp})
        bericht = pw.abgleich(erg, str(db), str(aus), anlegen=True)
        preise = {}
        for mid in pw.MODELLE:
            f = aus / f"preise_{mid}.json"
            if f.exists():
                d = json.loads(f.read_text(encoding="utf-8"))
                d.pop("meldung", None)       # enthält den Wunschpreis: nie veröffentlichen
                preise[mid] = d
            elif mid in alt_preise and isinstance(alt_preise[mid], dict):
                d = dict(alt_preise[mid])      # heute kein belegtes Angebot: letzten Stand behalten
                d.pop("meldung", None)
                preise[mid] = d
        lauf = json.loads((aus / "wecker_lauf.json").read_text(encoding="utf-8"))
    # letzter Abrufversuch je Modell (für die Reihenfolge der nächsten Läufe, Codex KONT-02); nur Zeitpunkte
    alt_lauf = alt.get("lauf") if isinstance(alt.get("lauf"), dict) else {}
    versuche = {m: z for m, z in (alt_lauf.get("versuche") or {}).items()
                if m in pw.MODELLE and isinstance(z, str)} if isinstance(alt_lauf.get("versuche"), dict) else {}
    for mid, r in erg["modelle"].items():
        if mid in pw.MODELLE and isinstance(r, dict) and not (r.get("heute_schon") or r.get("verschoben") or r.get("nicht_versucht")):
            versuche[mid] = erg["zeit"]
    lauf["versuche"] = versuche
    lauf["meldung"] = oeffentlicher_lauftext(lauf.get("meldung", ""), bericht["treffer"], pw._kurzliste)
    for mid, d in preise.items():
        g = (d.get("aktuell") or {}).get("gesamt")
        assert zahl_ok(g), f"{mid}: Gesamtpreis {g!r} unplausibel"
    neu = {"format": 1, "zeit": erg["zeit"], "quelle": "heise-Preisvergleich, günstigster Gesamtpreis mit belegtem Versand",
           "preise": preise, "lauf": lauf}
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps(neu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return bericht, lauf


# Umgebung jedes Git-Aufrufs (Codex P2A2-05-01/-05): ohne Ersetzungsreferenzen und Grafts (wie herkunft.OHNE_ERSATZ),
# ohne geerbte Umleitung von Repository, Arbeitsbaum, Index oder Objektspeicher. Transport und Zugang bleiben.
UMLEITUNGEN = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
               "GIT_COMMON_DIR", "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM")
OHNE_ERSATZ = {"GIT_NO_REPLACE_OBJECTS": "1", "GIT_GRAFT_FILE": os.devnull}
REGULAER = ("100644", "100755")


def umgebungs_konfig(k):
    """Konfiguration aus der Umgebung (Codex R2-04): GIT_CONFIG_COUNT/KEY_n/VALUE_n und GIT_CONFIG_PARAMETERS (`git -c`)
    lenken sonst über url.<x>.insteadOf/pushInsteadOf oder pushurl um. GIT_CONFIG_GLOBAL/SYSTEM/NOSYSTEM bleiben
    (Dateiorte; ein insteadOf dort gilt für Lesen und Schreiben gleich, ein pushInsteadOf bricht in ziel_url() ab)."""
    # GIT_CONFIG (R3-02) gilt nur für `git config` und ließe die Prüfung in ziel_url() eine andere Datei lesen als die
    # Transportbefehle.
    return (k in ("GIT_CONFIG", "GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS")
            or k.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")))


def git_umgebung(**extra):
    return {k: v for k, v in os.environ.items() if k not in UMLEITUNGEN and not umgebungs_konfig(k)} | OHNE_ERSATZ | extra


def ziel_pruefen(ziel):
    """preise.json darf kein Symlink und, wenn vorhanden, nur eine reguläre Datei sein (sonst SystemExit). Läuft in main()
    vor jedem Lesen oder Schreiben des Ziels (Codex R2-02) und noch einmal in preis_commit()."""
    if ziel.is_symlink() or (ziel.exists() and not ziel.is_file()):
        raise SystemExit(f"--push: {ziel.name} ist keine reguläre Datei, nichts gelesen, geschrieben oder gepusht")


def git_aus(ordner, *a):
    r = subprocess.run(["git", "-C", str(ordner), *a], capture_output=True, text=True, encoding="utf-8",
                       env=git_umgebung())
    return r.stdout.strip() if r.returncode == 0 else None


def arbeitsbaum_pruefen(ordner, zweig="gh-pages"):
    """Nur ein eigener Git-Arbeitsbaum genau in `ordner` mit ausgechecktem `zweig` ist erlaubt (sonst SystemExit)."""
    wurzel = git_aus(ordner, "rev-parse", "--show-toplevel") if Path(ordner).is_dir() else None
    if not wurzel or Path(wurzel).resolve() != Path(ordner).resolve():
        raise SystemExit(f"--push: {ordner} ist kein eigener Git-Arbeitsbaum (erst werkzeuge/veroeffentlichen.py ausführen)")
    kopf = git_aus(ordner, "symbolic-ref", "--short", "HEAD")
    if kopf != zweig:
        raise SystemExit(f"--push: im Arbeitsbaum ist {kopf!r} ausgecheckt, erwartet {zweig!r}")


def git_lauf(ordner, *a, env=None, pruefen=True):
    """git im Ordner; bei Fehler (pruefen=True) SystemExit mit der Meldung von git, sonst CompletedProcess."""
    r = subprocess.run(["git", "-C", str(ordner), *a], capture_output=True, text=True, encoding="utf-8",
                       env=env or git_umgebung())
    if pruefen and r.returncode != 0:
        raise SystemExit(f"--push: git {a[0]} fehlgeschlagen, nichts gepusht: {r.stderr.strip()}")
    return r


def git_bytes(ordner, *a):
    """git im Ordner, Ausgabe als Bytes (Pfade bytegenau, Codex R2-03); bei Fehler SystemExit."""
    r = subprocess.run(["git", "-C", str(ordner), *a], capture_output=True, env=git_umgebung())
    if r.returncode != 0:
        raise SystemExit(f"--push: git {a[0]} fehlgeschlagen, nichts gepusht: " + r.stderr.decode("utf-8", "replace").strip())
    return r.stdout


def ziel_url(ordner):
    """Die eine URL von origin für ls-remote, fetch und push (Codex R2-04): Lesen und Schreiben treffen dasselbe Ziel,
    remote.origin.pushurl wirkt so nicht. url.<x>.pushInsteadOf würde nur den Push umschreiben: dann Abbruch.
    (url.<x>.insteadOf gilt für alle drei Aufrufe gleich.)"""
    url = git_lauf(ordner, "remote", "get-url", "origin").stdout.strip()
    if not url or "\n" in url:
        raise SystemExit("--push: origin hat keine eindeutige URL, nichts gepusht")
    # R3-01: Git löst das Zielargument zuerst als Namen einer konfigurierten Remote auf (deren url/pushurl/Refspec
    # griffen dann). Eine URL mit „/“ liest Git nie aus .git/remotes oder .git/branches; die Konfiguration genügt.
    if url in git_lauf(ordner, "remote").stdout.splitlines():
        raise SystemExit("--push: eine Remote heißt wie die URL von origin (Ziel nicht eindeutig), nichts gepusht")
    umschreiben = git_lauf(ordner, "config", "--get-regexp", r"^url\..*\.pushinsteadof$", pruefen=False)
    if umschreiben.returncode not in (0, 1) or (umschreiben.returncode == 0 and umschreiben.stdout.strip()):
        # rc 1 = kein Eintrag; 0 mit Treffer oder jeder andere Code (Prüffehler, R3-02) = Abbruch
        raise SystemExit("--push: url.*.pushInsteadOf ist gesetzt oder nicht prüfbar (Push ginge an ein anderes Ziel), "
                         "nichts gepusht")
    return url


def eltern_holen(ordner, url):
    """SHA von gh-pages auf origin (ls-remote, nicht der lokale Zweig; P2A2-03/-05). Fehlt der Commit lokal (z. B.
    flacher Abruf in Actions und inzwischen ein fremder Push), wird der Zweig nachgeholt; er muss dann noch derselbe sein."""
    zeilen = git_lauf(ordner, "ls-remote", "--exit-code", url, "refs/heads/gh-pages", pruefen=False)
    treffer = [z.split("\t")[0] for z in zeilen.stdout.splitlines() if z.endswith("\trefs/heads/gh-pages")]
    sha = treffer[0] if zeilen.returncode == 0 and len(treffer) == 1 else ""   # genau der Zweig, nicht x/refs/heads/…
    if len(sha) not in (40, 64):
        raise SystemExit("--push: gh-pages fehlt auf origin oder ist nicht lesbar, nichts gepusht")
    if git_lauf(ordner, "cat-file", "-e", f"{sha}^{{commit}}", pruefen=False).returncode != 0:
        git_lauf(ordner, "fetch", "-q", "--no-tags", url, "+refs/heads/gh-pages:refs/remotes/origin/gh-pages")
        if git_lauf(ordner, "rev-parse", "refs/remotes/origin/gh-pages^{commit}").stdout.strip() != sha:
            raise SystemExit("--push: gh-pages hat sich während des Abrufs geändert, nichts gepusht (erneut starten)")
    return sha


def preis_commit(ordner, eltern, ziel):
    """Commit aus genau `eltern`, darin allein preise.json durch die Datei `ziel` ersetzt (eigener Index; HEAD, Index
    und lokaler Zweig gehen nicht ein). None, wenn preise.json in `eltern` schon genau so steht."""
    ziel_pruefen(ziel)
    if not ziel.is_file():
        raise SystemExit(f"--push: {ziel.name} fehlt, nichts gepusht")
    # Einmal gelesen: dieselben Bytes für JSON und Blob, ohne Git-Filter (P2A2-05-04). Zeilenenden fest auf LF wie
    # `.gitattributes` (`eol=lf`), damit ein lokal mit autocrlf ausgecheckter Stand keinen Scheincommit erzeugt.
    daten = ziel.read_bytes().replace(b"\r\n", b"\n")
    datum = json.loads(daten.decode("utf-8"))["zeit"][:10]
    r = subprocess.run(["git", "-C", str(ordner), "hash-object", "-w", "--no-filters", "--stdin"], input=daten,
                       capture_output=True, env=git_umgebung())
    if r.returncode != 0:
        raise SystemExit("--push: git hash-object fehlgeschlagen, nichts gepusht: " + r.stderr.decode("utf-8", "replace"))
    blob = r.stdout.decode("ascii").strip()
    alt = git_lauf(ordner, "ls-tree", eltern, "--", ziel.name).stdout.split()
    if alt and (alt[1] != "blob" or alt[0] not in REGULAER):
        raise SystemExit(f"--push: {ziel.name} ist auf gh-pages keine reguläre Datei ({alt[0]}), nichts gepusht")
    modus = alt[0] if alt else "100644"
    with tempfile.TemporaryDirectory(prefix="kb-preis-index-") as tmp:
        env = git_umgebung(GIT_INDEX_FILE=str(Path(tmp) / "index"))
        git_lauf(ordner, "read-tree", eltern, env=env)
        git_lauf(ordner, "update-index", "--add", "--cacheinfo", f"{modus},{blob},{ziel.name}", env=env)
        baum = git_lauf(ordner, "write-tree", env=env).stdout.strip()
    if baum == git_lauf(ordner, "rev-parse", f"{eltern}^{{tree}}").stdout.strip():
        return None
    return git_lauf(ordner, "commit-tree", baum, "-p", eltern, "-m", "Preise " + datum).stdout.strip()


def commit_fehler(ordner, eltern, neu, name="preise.json"):
    """Grund gegen den Push oder None: `neu` hat genau `eltern` als Elternteil und ändert genau `name`."""
    kopf = git_lauf(ordner, "rev-list", "--parents", "-n", "1", neu).stdout.split()
    if kopf[1:] != [eltern]:
        return f"Commit {neu[:12]} hat nicht genau gh-pages {eltern[:12]} als Elternteil"
    # Wurzeleinträge ohne Rekursion (P2A2-05-02): jede weitere Änderung an Pfad, Modus, Typ oder Objekt-ID zählt, auch
    # an Verzeichnissen und leeren Unterbäumen, die `diff-tree -r` nicht meldet. Pfade als Bytes (R2-03): kein
    # Umwandeln von CR/CRLF, kein Dekodierfehler bei ungültigem UTF-8.
    def wurzel(c):
        eintraege = {}
        for z in git_bytes(ordner, "ls-tree", "-z", c).split(b"\0"):
            if z:
                kopf, pfad = z.split(b"\t", 1)
                eintraege[pfad] = tuple(kopf.decode("ascii").split())
        return eintraege
    a, b, n = wurzel(eltern), wurzel(neu), name.encode("utf-8")
    geaendert = sorted(p for p in a.keys() | b.keys() if a.get(p) != b.get(p))
    if geaendert != [n]:
        return (f"Commit {neu[:12]} ändert gegenüber gh-pages nicht genau {name}: "
                + ", ".join(repr(p.decode("utf-8", "backslashreplace")) for p in geaendert[:10]))
    eintrag = b.get(n)
    if eintrag is None:   # R2-05: im Kandidaten gelöscht
        return f"{name} fehlt im Commit {neu[:12]}"
    if eintrag[0] not in REGULAER or eintrag[1] != "blob":
        return f"{name} im Commit {neu[:12]} ist keine reguläre Datei ({eintrag[0]})"
    return None


def push(ziel):
    """Preis-Push (P2a-2, P2A2-05; Muster veroeffentlichen.py): Commit nur aus dem Remote-Stand `eltern`, Baumprüfung,
    Push genau dieses Commits mit Lease auf `eltern`, an die eine URL von origin (ziel_url). Ein unveröffentlichter
    lokaler Commit (etwa mit finder-daten.json) kommt so nicht mit; ist gh-pages auf origin inzwischen versetzt oder
    gelöscht, scheitert die Lease. Lokaler Zweig, HEAD und Index bleiben immer unverändert (Codex R2-01)."""
    ordner = ziel.parent
    arbeitsbaum_pruefen(ordner)
    url = ziel_url(ordner)
    eltern = eltern_holen(ordner, url)
    neu = preis_commit(ordner, eltern, ziel)
    if neu is None:
        print("preise.json unverändert, kein Commit")
        return
    grund = commit_fehler(ordner, eltern, neu, ziel.name)
    if grund:
        raise SystemExit("--push: Abbruch, nichts gepusht: " + grund)
    r = git_lauf(ordner, "push", "-q", "--no-follow-tags", f"--force-with-lease=refs/heads/gh-pages:{eltern}", url,
                 f"{neu}:refs/heads/gh-pages", pruefen=False)
    if r.returncode != 0:
        raise SystemExit("--push: Push abgelehnt (gh-pages ist nicht mehr der abgerufene Stand), erneut starten: "
                         + r.stderr.strip())
    print("gepusht: gh-pages/preise.json")
    # Kein Nachziehen des lokalen Stands (R2-01): jede Schreibaktion auf Index oder Zweig kann eine lokale Fassung
    # verwerfen. In Actions endet der Arbeitsbaum ohnehin; lokal bleibt preise.json als Änderung stehen.
    print("Hinweis: lokaler gh-pages und Index bleiben unverändert; preise.json steht im Arbeitsbaum als Änderung "
          "(veroeffentlichen.py bricht ab, bis sie geklärt ist)", file=sys.stderr)


def meldetext(treffer):
    """Alle Treffer vollständig, eine Zeile je Treffer (Codex R1 B1: der R4-Text "push" ist auf 195 Zeichen gekürzt).
    Fünf Modelle mit je zwei Treffern ergeben unter 600 Zeichen; ntfy nimmt bis 4096 Byte als Text."""
    return "\n".join(treffer)


def uebersicht(erg):
    """Je Modell nur Angebotszahl oder Fehler (für das öffentliche Log; zeigt z. B. eine heise-Sperre)."""
    def zeile(r):
        if r.get("fehler"):
            return r["fehler"]
        if r.get("heute_schon"):
            return "heute schon gelesen"
        if r.get("verschoben"):
            return "folgt im nächsten Lauf"
        return f"{r.get('angebote', '?')} Angebote"
    return {mid: zeile(r) for mid, r in erg["modelle"].items() if isinstance(r, dict)}


def dieselbe_datei(a, b):
    """True, wenn beide Pfade dieselbe Datei meinen: gleicher aufgelöster Pfad oder, bei zwei vorhandenen Dateien,
    dieselbe Dateiidentität (Hardlink, VER-04). Lässt sich die Identität nicht feststellen, gilt sie als gleich."""
    a, b = Path(a), Path(b)
    if a.resolve() == b.resolve():
        return True
    try:
        return a.exists() and b.exists() and a.samefile(b)
    except OSError:
        return True


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--abruf", help="JSON-Ausgabe von preiswecker.py (ohne Argumente); sonst wird neu abgerufen")
    a.add_argument("--ziel", default=str(SEITEN / "preise.json"))
    a.add_argument("--skript")
    a.add_argument("--push", action="store_true")
    a.add_argument("--nur-push", action="store_true",
                   help="nichts abrufen: die vorhandene preise.json im gh-pages-Arbeitsbaum committen und pushen")
    a.add_argument("--meldung", help="Datei für den Benachrichtigungstext (wird immer geschrieben, leer = keine Meldung)")
    x = a.parse_args()
    if x.meldung and dieselbe_datei(x.meldung, x.ziel):   # R3-03, VER-04: Meldung überschriebe preise.json
        raise SystemExit("--meldung und --ziel sind dieselbe Datei, nichts abgerufen oder geschrieben")
    if x.nur_push or x.push:   # vor allem anderen: nur der gh-pages-Arbeitsbaum, nur preise.json
        ziel = Path(x.ziel)
        assert ziel.parent.resolve() == SEITEN.resolve() and ziel.name == "preise.json", "--push nur mit dem gh-pages-Arbeitsbaum"
        arbeitsbaum_pruefen(ziel.parent)
        ziel_pruefen(ziel)   # R2-02: vor lies_alt() und aktualisiere(), die sonst durch einen Symlink lesen/schreiben
    if x.nur_push:
        push(Path(x.ziel))
        return
    pw, pfad = lade_skript(x.skript)
    wunsch = lies_wunsch(os.environ.get("WUNSCHPREISE", ""), pw.MODELLE)
    if x.abruf:
        erg = json.loads(Path(x.abruf).read_text(encoding="utf-8"))
    else:
        heute = datetime.now(timezone.utc).astimezone().date().isoformat()   # Ortszeit wie erg["zeit"] (TZ im Workflow)
        alt = lies_alt(x.ziel)
        reihe = abrufreihe(alt, list(pw.MODELLE), heute)
        alt_status = alt.get("lauf", {}).get("status") if isinstance(alt.get("lauf"), dict) else None
        # Nachlauf, alles schon von heute und Status ok: nichts abrufen, preise.json unverändert. Steht noch ein
        # älterer Status (z. B. „teilweise“ eines früheren Laufs), wird er ohne Abruf neu berechnet (abruf_alle([])).
        if not reihe and alt_status == "ok":
            if x.meldung:
                Path(x.meldung).write_text("", encoding="utf-8")
            print(json.dumps({"ziel": x.ziel, "status": "ok", "abgerufen": 0,
                              "lauf": f"Alle {len(pw.MODELLE)} Preise von heute schon vorhanden, nichts abgerufen."},
                             ensure_ascii=False))
            return
        erg = pw.abruf_alle(reihe)
    assert isinstance(erg, dict) and isinstance(erg.get("modelle"), dict) and isinstance(erg.get("zeit"), str), "Abrufergebnis ungültig"
    ziel = Path(x.ziel)
    bericht, lauf = aktualisiere(pw, erg, ziel, wunsch)
    text = meldetext(bericht["treffer"])
    if x.meldung:
        Path(x.meldung).write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"skript": str(pfad), "ziel": str(ziel), "status": bericht["status"], "wunschpreise": len(wunsch),
                      "meldung": len(bericht["treffer"]), "modelle": uebersicht(erg), "lauf": lauf["meldung"]},
                     ensure_ascii=False))
    if x.push:
        push(ziel)
    if bericht["status"] == "fehler":
        sys.exit(3)


if __name__ == "__main__":
    main()
