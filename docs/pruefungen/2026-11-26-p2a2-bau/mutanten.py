# -*- coding: utf-8 -*-
"""Mutantenlauf P2a-2: je Mutante genau eine Ersetzung, Ziel-Tests müssen rot sein; danach git checkout der Datei."""
import subprocess, sys
from pathlib import Path

P = Path(sys.argv[1])
PY = ["python", "-I", "-B", "-m", "unittest", "discover", "-s", "tests", "-t", "tests", "-p"]

def py(datei, name):
    return PY + [datei, "-k", name]

def node(muster):
    return ["node", "--test", f"--test-name-pattern={muster}", "tests/test_bewertung.mjs"]

M = [
    ("3 Pflicht entfernt", "werkzeuge/datenbank.py",
     'fehler.append(f"Schema {kid}: gewichte_version fehlt (Pflicht ab Schema 2, Entwurf §2.1)")', "pass",
     [py("test_datenbank.py", "test_pflicht_und_fassung_1")]),
    ("38 Zweig gleich/andere Nummer entfernt", "werkzeuge/datenbank.py",
     'elif gleich and gv["nummer"] != rv["nummer"]:', "elif False:",
     [py("test_datenbank.py", "test_gleiche_projektion_gleiche_nummer")]),
    ("40 Felder sortiert", "werkzeuge/datenbank.py",
     '    for f in k["felder"]:\n        if f["gewicht"] > 0:\n            art',
     '    for f in sorted(k["felder"], key=lambda x: x["id"]):\n        if f["gewicht"] > 0:\n            art',
     [py("test_datenbank.py", "test_projektion_normalform_und_reihenfolge")]),
    ("48 _doppelt Felder entfernt", "werkzeuge/datenbank.py",
     'fehler += [f"Schema {kid}: Feld-ID {i!r} doppelt" for i in _doppelt(f.get("id") for f in felder_ok)]', "pass",
     [py("test_datenbank.py", "test_eindeutige_ids")]),
    ("47(h) online_eltern liest origin/gh-pages", "werkzeuge/freigabe.py",
     'r = _git(ordner, "ls-remote", "--exit-code", remote, ZWEIG)',
     'r = _git(ordner, "rev-parse", f"{remote}/gh-pages")',
     [py("test_freigabe.py", "test_alter_ref_bei_fehlendem_zweig_wird_nie_gelesen")]),
    ("47(e) Push ohne Lease", "werkzeuge/freigabe.py",
     'f"--force-with-lease={ZWEIG}:{eltern}", remote,', "remote,",
     [py("test_freigabe.py", "test_zweig_geloescht")]),
    ("47(b) seiten_fehler entfernt", "werkzeuge/veroeffentlichen.py",
     "fehler, _ = freigabe.seiten_fehler(kandidat, eltern, WURZEL)", "fehler = []",
     [py("test_app.py", "test_fassung_geaendert_bricht_vor_dem_bau_ab")]),
    ("47(d)/(f) eltern nur einmal", "werkzeuge/freigabe.py",
     "    for versuch in range(1, versuche + 1):\n        try:\n            eltern = online_eltern(ordner, remote)",
     "    eltern = online_eltern(ordner, remote)\n    for versuch in range(1, versuche + 1):\n        try:\n            pass",
     [py("test_freigabe.py", "test_fremder_push_mit_neuer_herkunft"),
      py("test_freigabe.py", "test_auf_vorfahr_zurueckgesetzt")]),
    ("42/37 Gewicht im Schema geändert", "daten/schema/kategorien.json",
     '["lcd_quantum_dot", 50], ["lcd", 40]]}, "gewicht": 30}', '["lcd_quantum_dot", 50], ["lcd", 40]]}, "gewicht": 31}',
     [node(r"P2a-2 \(42\)"), node(r"P2a-2 \(37\)")]),
]

def lauf(cmd):
    r = subprocess.run(cmd, cwd=P, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ausgabe = (r.stdout + r.stderr)
    # Sicherstellen, dass wirklich ein Test lief (kein leerer Filter)
    lief = ("Ran 1 test" in ausgabe or "Ran 2 test" in ausgabe) if cmd[0] == "python" else ("ℹ tests 1" in ausgabe)
    return r.returncode, lief, ausgabe

gesamt_ok = True
print("== Original ==")
for _, _, _, _, cmds in M:
    for c in cmds:
        code, lief, a = lauf(c)
        ok = code == 0 and lief
        gesamt_ok &= ok
        print(("GRÜN " if ok else "FEHLER ") + " ".join(c[-3:]))
print("== Mutanten ==")
for name, datei, alt, neu, cmds in M:
    f = P / datei
    text = f.read_text(encoding="utf-8")
    if text.count(alt) != 1:
        print(f"FEHLER {name}: Stelle {text.count(alt)}-mal gefunden"); gesamt_ok = False; continue
    f.write_text(text.replace(alt, neu), encoding="utf-8", newline="")
    try:
        for c in cmds:
            code, lief, a = lauf(c)
            rot = code != 0
            gesamt_ok &= rot
            print(("ROT  " if rot else "NICHT ROT ") + f"{name} :: " + " ".join(c[-3:]))
            if not rot:
                print(a[-1500:])
    finally:
        subprocess.run(["git", "checkout", "--", datei], cwd=P, check=True)
print("== Rücksetzen geprüft ==")
st = subprocess.run(["git", "status", "--porcelain", "--", "werkzeuge", "daten"], cwd=P, capture_output=True, text=True).stdout
print("sauber" if not st.strip() else st); gesamt_ok &= not st.strip()
print("ERGEBNIS", "OK" if gesamt_ok else "FEHLER")
sys.exit(0 if gesamt_ok else 1)
