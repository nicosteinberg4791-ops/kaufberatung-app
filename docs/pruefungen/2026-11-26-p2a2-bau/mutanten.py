# -*- coding: utf-8 -*-
"""Mutantenlauf P2a-2: je Mutante genau eine Ersetzung, Ziel-Tests müssen rot sein; danach git checkout der Datei."""
import re, subprocess, sys
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
    # ---- Korrektur r1 (bewertung-r1.md): je Korrektur die Probe ----
    ("BAU-01 parse_float/parse_int entfernt", "werkzeuge/datenbank.py",
     "parse_float=_endlich_float, parse_int=_endlich_int)", ")",
     [py("test_datenbank.py", "test_nur_endliche_zahlen"), py("test_freigabe.py", "test_datei_an_kandidat_gebunden")]),
    ("BAU-01 allow_nan entfernt", "werkzeuge/datenbank.py",
     'separators=(",", ":"), allow_nan=False)', 'separators=(",", ":"))',
     [py("test_datenbank.py", "test_nur_endliche_zahlen")]),
    ("BAU-02 alte Annahme 'Live ohne Fassung' zurück", "tests/test_bewertung.mjs",
     '    const alt = kurz(JSON.parse(fs.readFileSync(path.join(tmp, "alt.json"), "utf8")));\n    // §9.1: alle Blobs',
     '    const alt = kurz(JSON.parse(fs.readFileSync(path.join(tmp, "alt.json"), "utf8")));\n'
     '    assert.ok(alt.kategorien.every(k => k.gewichte_version === undefined), "Live-Werkzeug kennt keine Fassung");\n'
     '    // §9.1: alle Blobs',
     [node("nach Veröffentlichung von Fassung 1")]),
    ("BAU-03 null wieder als Altschema", "werkzeuge/datenbank.py",   # r3: Stelle im Vordurchlauf
     'if "gewichte_version" not in ka:', 'if ka.get("gewichte_version") is None:',
     [py("test_datenbank.py", "test_referenz_fassung_explizit_ungueltig")]),
    ("BAU-03 Schema-Version nicht geprüft", "werkzeuge/datenbank.py",
     "            if not altschema:", "            if False:",
     [py("test_datenbank.py", "test_referenz_fassung_explizit_ungueltig")]),
    ("BAU-05 entfernte Kategorie übergangen", "werkzeuge/datenbank.py",
     "for kid in alt if kid not in neu_ids]", "for kid in alt if False]",
     [py("test_datenbank.py", "test_entfernte_kategorie")]),
    ("BAU-06 Schutz gegen kleinere Nummer entfernt", "werkzeuge/datenbank.py",
     'elif gv["nummer"] < rv["nummer"]:', "elif False:",
     [py("test_datenbank.py", "test_referenz_schema_1")]),
    ("BAU-04 herkunft der Datei nicht geprüft", "werkzeuge/freigabe.py",
     'if not isinstance(gebaut, dict) or gebaut.get("herkunft") != neu:', "if not isinstance(gebaut, dict):",
     [py("test_freigabe.py", "test_datei_an_kandidat_gebunden")]),
    # ---- Korrektur r2 (bewertung-r2.md) ----
    ("BAU-04 r2 Bytevergleich mit dem Bau entfernt", "werkzeuge/freigabe.py",
     "    if inhalt != soll:", "    if False:",
     [py("test_freigabe.py", "test_datei_an_kandidat_gebunden")]),
    ("BAU-04 r2 Nachbau liest den Arbeitsbaum statt des Commits", "werkzeuge/freigabe.py",
     "            ziel.write_bytes(b.stdout)", "            ziel.write_bytes((Path(ordner) / pfad).read_bytes())",
     [py("test_freigabe.py", "test_datei_an_kandidat_gebunden")]),
    ("BAU-02 r2 feste Menge werfender Fassungen", "tests/test_bewertung.mjs",
     "      if (n.fehler) return;",
     '      if (n.fehler) { assert.equal(blob, ALTFALL_B24C18F, "nur b24c18f wirft"); return; }',
     [node("nach Veröffentlichung von Fassung 1")]),
    ("BAU-03 r2 gerundete Schema-Version wieder Altschema", "werkzeuge/datenbank.py",
     "    if type(version) is not int or version not in (1, 2):",
     "    if isinstance(version, bool) or version not in (1, 2):",
     [py("test_datenbank.py", "test_referenz_gerundet_und_ohne_projektion")]),
    ("BAU-03 r2/r3 Referenz nur je Kategorie geprüft (Stand r2)", "werkzeuge/datenbank.py",
     "    if fehler:\n        return fehler\n    for k in kandidat[\"kategorien\"]:\n        kid, gv = k[\"id\"], k[\"gewichte_version\"]\n",
     "    for k in kandidat[\"kategorien\"]:\n        kid, gv = k[\"id\"], k.get(\"gewichte_version\")\n"
     "        if any(f.startswith(kid + \":\") for f in fehler):\n            continue\n",
     [py("test_datenbank.py", "test_referenz_gerundet_und_ohne_projektion")]),
    ("BAU-03 r2 Kandidat mit schema_version 2.0", "werkzeuge/datenbank.py",
     "    if type(version) is not int or version != 2:", "    if version != 2 or isinstance(version, bool):",
     [py("test_datenbank.py", "test_referenz_gerundet_und_ohne_projektion")]),
    ("BAU-06 r2 abdeckung_mindest aus der Projektion", "werkzeuge/datenbank.py",
     '("anker", "faktor", "abzug", "abdeckung_mindest")', '("anker", "faktor", "abzug")',
     [py("test_datenbank.py", "test_abschlag_isoliert")]),
    ("BAU-06 r2 abzug aus der Projektion", "werkzeuge/datenbank.py",
     '("anker", "faktor", "abzug", "abdeckung_mindest")', '("anker", "faktor", "abdeckung_mindest")',
     [py("test_datenbank.py", "test_abschlag_isoliert")]),
    ("BAU-06 r2 faktor aus der Projektion", "werkzeuge/datenbank.py",
     '("anker", "faktor", "abzug", "abdeckung_mindest")', '("anker", "abzug", "abdeckung_mindest")',
     [py("test_datenbank.py", "test_abschlag_isoliert")]),
    ("BAU-06 r2 mischung aus der Projektion", "werkzeuge/datenbank.py",
     'abschlag["mischung"] = {n: float(db["getestet"]["mischung"][n]) for n in ("test", "datenblatt_roh")}',
     'abschlag["mischung"] = {}',
     [py("test_datenbank.py", "test_abschlag_isoliert")]),
    # ---- Korrektur r3 (bewertung-r3.md) ----
    ("BAU-02 r3 Mindestgröße des Verlaufs zurück", "tests/test_bewertung.mjs",
     '    assert.ok(blobs.has(ALTFALL_B24C18F), "Altfall b24c18f im Verlauf");',
     '    assert.ok(blobs.size >= 3, "gh-pages-Verlauf fehlt? " + blobs.size);\n'
     '    assert.ok(blobs.has(ALTFALL_B24C18F), "Altfall b24c18f im Verlauf");',
     [node("kleiner Verlauf")]),
    ("BAU-02 r3 absolute Notenschwelle zurück", "tests/test_bewertung.mjs",
     '    assert.equal(gerechnet, soll, "jede Eingabe jeder rechnenden Fassung verglichen");',
     '    assert.ok(gerechnet > 20000, gerechnet + " Noten");',
     [node("kleiner Verlauf")]),
    ("BAU-02 r3 Vergleich nur der ersten Kategorie", "tests/test_bewertung.mjs",
     "      n.d.kategorien.forEach((k, ki) => {\n        const ak", "      n.d.kategorien.slice(0, 1).forEach((k, ki) => {\n        const ak",
     [node(r"P2a-2 \(37\)")]),
    ("BAU-03 r3 Schema-Version der Referenz nicht geprüft", "werkzeuge/datenbank.py",
     "    if type(version) is not int or version not in (1, 2):", "    if False:",
     [py("test_datenbank.py", "test_referenz_gerundet_und_ohne_projektion")]),
    ("BAU-06 r3 Frage-ID aus der Projektion", "werkzeuge/datenbank.py",
     'fragen = [{"id": q["id"], "antworten":', 'fragen = [{"antworten":',
     [py("test_datenbank.py", "test_frage_id_isoliert")]),
    ("BAU-04-TEST r3 Schlusszeilenumbruch beim Schreiben des Blobs", "werkzeuge/freigabe.py",
     'r = _git(ordner, "hash-object", "-w", "--stdin", eingabe=inhalt)',
     'r = _git(ordner, "hash-object", "-w", "--stdin", eingabe=inhalt + b"\n")',
     [py("test_freigabe.py", "test_datei_an_kandidat_gebunden")]),
]

def lauf(cmd):
    r = subprocess.run(cmd, cwd=P, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ausgabe = (r.stdout + r.stderr)
    # Sicherstellen, dass wirklich ein Test lief (kein leerer Filter)
    # r1: Test 37 hat zwei Fälle, daher „mindestens ein Test“ statt genau einer Zahl
    lief = bool(re.search(r"Ran [1-9]\d* test", ausgabe)) if cmd[0] == "python" else bool(re.search(r"ℹ tests [1-9]", ausgabe))
    return r.returncode, lief, ausgabe

gesamt_ok = True
print("== Original ==")
for _, _, _, _, cmds in M:
    for c in cmds:
        code, lief, a = lauf(c)
        ok = code == 0 and lief
        gesamt_ok &= ok
        print(("GRÜN " if ok else "FEHLER ") + " ".join(c[-3:]))
        if not ok:   # r3: Ausgabe festhalten (ein nicht reproduzierter Fehlschlag im Lauf auf 288125d)
            print(a[-3000:])
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
st = subprocess.run(["git", "status", "--porcelain", "--", "werkzeuge", "daten", "tests"], cwd=P, capture_output=True, text=True).stdout
print("sauber" if not st.strip() else st); gesamt_ok &= not st.strip()
print("ERGEBNIS", "OK" if gesamt_ok else "FEHLER")
sys.exit(0 if gesamt_ok else 1)
