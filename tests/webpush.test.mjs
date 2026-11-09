// Tests für werkzeuge/webpush.mjs (node:test). Aufruf: node --test tests/webpush.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { verschluesseln, ableiten, vapidKopf, senden } from "../werkzeuge/webpush.mjs";

const HIER = path.dirname(fileURLToPath(import.meta.url));
const PROJEKT = path.resolve(HIER, "..");
const SKRIPT = path.join(PROJEKT, "werkzeuge", "webpush.mjs");

const b64u = (s) => Buffer.from(s.replace(/\s+/g, ""), "base64url");
const hmac = (k, d) => crypto.createHmac("sha256", k).update(d).digest();

// ---- Hilfen: Empfängerseite (User Agent) ------------------------------------
function neuesAbo(endpoint) {
  const ua = crypto.createECDH("prime256v1");
  ua.generateKeys();
  const auth = crypto.randomBytes(16);
  return {
    ua, auth,
    abo: { endpoint, keys: { p256dh: ua.getPublicKey().toString("base64url"), auth: auth.toString("base64url") } },
  };
}

function entschluesseln(koerper, ua, auth) {
  const salt = koerper.subarray(0, 16);
  const rs = koerper.readUInt32BE(16);
  const idlen = koerper[20];
  const asPublic = koerper.subarray(21, 21 + idlen);
  const ct = koerper.subarray(21 + idlen);
  assert.equal(rs, 4096);
  const ecdh = ua.computeSecret(asPublic);
  const prkKey = hmac(auth, ecdh);
  const keyInfo = Buffer.concat([Buffer.from("WebPush: info\0"), ua.getPublicKey(), asPublic]);
  const ikm = hmac(prkKey, Buffer.concat([keyInfo, Buffer.from([1])]));
  const prk = hmac(salt, ikm);
  const cek = hmac(prk, Buffer.from("Content-Encoding: aes128gcm\0\x01", "latin1")).subarray(0, 16);
  const nonce = hmac(prk, Buffer.from("Content-Encoding: nonce\0\x01", "latin1")).subarray(0, 12);
  const d = crypto.createDecipheriv("aes-128-gcm", cek, nonce);
  d.setAuthTag(ct.subarray(ct.length - 16));
  const voll = Buffer.concat([d.update(ct.subarray(0, ct.length - 16)), d.final()]);
  let ende = voll.length;
  while (ende > 0 && voll[ende - 1] === 0) ende--;
  assert.equal(voll[ende - 1], 2, "Delimiter 0x02 am Ende");
  return voll.subarray(0, ende - 1);
}

function jwtPruefen(authKopf, erwartetAud) {
  const m = /^vapid t=([^,]+), k=(.+)$/.exec(authKopf);
  assert.ok(m, "Authorization hat Form 'vapid t=..., k=...'");
  const pubRoh = b64u(m[2]);
  assert.equal(pubRoh.length, 65);
  assert.equal(pubRoh[0], 4);
  const [h, c, s] = m[1].split(".");
  const pub = crypto.createPublicKey({
    key: { kty: "EC", crv: "P-256", x: pubRoh.subarray(1, 33).toString("base64url"), y: pubRoh.subarray(33, 65).toString("base64url") },
    format: "jwk",
  });
  const sig = b64u(s);
  assert.equal(sig.length, 64);
  assert.ok(crypto.verify("sha256", Buffer.from(h + "." + c), { key: pub, dsaEncoding: "ieee-p1363" }, sig), "JWT-Signatur gültig");
  assert.deepEqual(JSON.parse(b64u(h).toString()), { typ: "JWT", alg: "ES256" });
  const claims = JSON.parse(b64u(c).toString());
  assert.equal(claims.aud, erwartetAud);
  const jetzt = Math.floor(Date.now() / 1000);
  assert.ok(claims.exp > jetzt && claims.exp <= jetzt + 24 * 3600, "exp höchstens 24 h");
  assert.equal(claims.sub, "https://nicosteinberg4791-ops.github.io/kaufberatung-app/");
  return { pubB64: m[2], claims };
}

// ---- Hilfen: lokaler Server -----------------------------------------------------
// antworten: Liste von Statuscodes, der letzte gilt für alle weiteren Aufrufe
async function starteServer(antworten) {
  const aufrufe = [];
  const server = http.createServer((req, res) => {
    const teile = [];
    req.on("data", (d) => teile.push(d));
    req.on("end", () => {
      aufrufe.push({ headers: req.headers, url: req.url, method: req.method, body: Buffer.concat(teile) });
      const status = antworten[Math.min(aufrufe.length - 1, antworten.length - 1)];
      res.writeHead(status);
      res.end();
    });
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const port = server.address().port;
  return { aufrufe, port, schliessen: () => new Promise((r) => server.close(r)) };
}

function neuerVapid() {
  const { privateKey } = crypto.generateKeyPairSync("ec", { namedCurve: "prime256v1" });
  return privateKey.export({ format: "jwk" });
}

const schnell = { warte: async () => {} };

// ---- 1. RFC-8291-Anhang-A -------------------------------------------------------
test("RFC 8291 Anhang A: Zwischenwerte, Kopf und Chiffrat", () => {
  const asEcdh = crypto.createECDH("prime256v1");
  asEcdh.setPrivateKey(b64u("yfWPiYE-n46HLnH0KqZOF1fJJU3MYrct3AELtAQ-oRw"));
  const abo = {
    endpoint: "https://push.example.invalid/x",
    keys: {
      p256dh: "BCVxsr7N_eNgVRqvHtD0zTZsEc6-VV-JvLexhqUzORcxaOzi6-AYWXvTBHm4bjyPjs7Vd8pZGH6SRpkNtoIAiw4",
      auth: "BTBZMqHH6r4Tts7J_aSIgg",
    },
  };
  const salt = b64u("DGv6ra1nlYgDCS1FRnbzlw");
  const klartext = b64u("V2hlbiBJIGdyb3cgdXAsIEkgd2FudCB0byBiZSBhIHdhdGVybWVsb24");
  assert.equal(klartext.toString(), "When I grow up, I want to be a watermelon");

  const z = ableiten(abo, { asEcdh, salt });
  assert.deepEqual(z.asPublic, b64u("BP4z9KsN6nGRTbVYI_c7VJSPQTBtkgcy27mlmlMoZIIgDll6e3vCYLocInmYWAmS6TlzAC8wEqKK6PBru3jl7A8"));
  assert.deepEqual(z.ecdh, b64u("kyrL1jIIOHEzg3sM2ZWRHDRB62YACZhhSlknJ672kSs"));
  assert.deepEqual(z.prkKey, b64u("Snr3JMxaHVDXHWJn5wdC52WjpCtd2EIEGBykDcZW32k"));
  assert.deepEqual(z.ikm, b64u("S4lYMb_L0FxCeq0WhDx813KgSYqU26kOyzWUdsXYyrg"));
  assert.deepEqual(z.prk, b64u("09_eUZGrsvxChDCGRCdkLiDXrReGOEVeSCdCcPBSJSc"));
  assert.deepEqual(z.cek, b64u("oIhVW04MRdy2XN9CiKLxTg"));
  assert.deepEqual(z.nonce, b64u("4h_95klXJ5E_qnoN"));

  const koerper = verschluesseln(klartext, abo, { asEcdh, salt });
  const kopf = b64u("DGv6ra1nlYgDCS1FRnbzlwAAEABBBP4z9KsN6nGRTbVYI_c7VJSPQTBtkgcy27mlmlMoZIIgDll6e3vCYLocInmYWAmS6TlzAC8wEqKK6PBru3jl7A8");
  const chiffrat = b64u("8pfeW0KbunFT06SuDKoJH9Ql87S1QUrdirN6GcG7sFz1y1sqLgVi1VhjVkHsUoEsbI_0LpXMuGvnzQ");
  assert.equal(kopf.length, 86);
  assert.deepEqual(koerper.subarray(0, 86), kopf);
  assert.deepEqual(koerper.subarray(86), chiffrat);
});

// ---- 2. Rundreise ---------------------------------------------------------------
test("Rundreise: verschlüsseln und mit UA-Schlüssel entschlüsseln", () => {
  const { ua, auth, abo } = neuesAbo("https://push.example.invalid/x");
  const klartext = Buffer.from("Größe 65 Zoll – günstig ✓", "utf8");
  const k = verschluesseln(klartext, abo);
  assert.equal(k.length, 86 + klartext.length + 1 + 16);
  assert.deepEqual(entschluesseln(k, ua, auth), klartext);
  // zwei Läufe liefern unterschiedliche Körper (frisches Salz und Schlüsselpaar)
  assert.notDeepEqual(verschluesseln(klartext, abo), k);
});

test("Prüfung des Abos: http außerhalb localhost, p256dh- und auth-Länge", async () => {
  const { abo } = neuesAbo("https://push.example.invalid/x");
  assert.throws(() => verschluesseln(Buffer.from("x"), { ...abo, endpoint: "http://example.invalid/x" }), /https/);
  assert.throws(() => verschluesseln(Buffer.from("x"), { ...abo, keys: { ...abo.keys, auth: "AAAA" } }), /auth/);
  assert.throws(() => verschluesseln(Buffer.from("x"), { ...abo, keys: { ...abo.keys, p256dh: "AAAA" } }), /p256dh/);
  await assert.rejects(senden({ ...abo, endpoint: "http://example.invalid/x" }, neuerVapid(), { titel: "a", text: "b", ziel: "c" }), /https/);
});

// ---- 3. senden gegen lokalen Server ----------------------------------------------
test("senden: Kopfzeilen, JWT, Körper entschlüsselbar (201 = ok)", async () => {
  const srv = await starteServer([201]);
  try {
    const { ua, auth, abo } = neuesAbo(`http://127.0.0.1:${srv.port}/geheimer/pfad`);
    const n = { titel: "TV-Preiswecker", text: "Preis gefallen: 499 €", ziel: "./#preiswecker" };
    const r = await senden(abo, neuerVapid(), n, schnell);
    assert.deepEqual(r, { status: 201, ok: true, ungueltig: false });
    assert.equal(srv.aufrufe.length, 1);
    const a = srv.aufrufe[0];
    assert.equal(a.method, "POST");
    assert.equal(a.url, "/geheimer/pfad");
    assert.equal(a.headers.ttl, "86400");
    assert.equal(a.headers.urgency, "high");
    assert.equal(a.headers["content-encoding"], "aes128gcm");
    assert.equal(a.headers["content-type"], "application/octet-stream");
    jwtPruefen(a.headers.authorization, `http://127.0.0.1:${srv.port}`);
    assert.deepEqual(JSON.parse(entschluesseln(a.body, ua, auth).toString("utf8")), n);
  } finally { await srv.schliessen(); }
});

test("senden: 200 und 202 sind ok", async () => {
  for (const code of [200, 202]) {
    const srv = await starteServer([code]);
    try {
      const { abo } = neuesAbo(`http://127.0.0.1:${srv.port}/p`);
      const r = await senden(abo, neuerVapid(), { titel: "a", text: "b", ziel: "c" }, schnell);
      assert.equal(r.ok, true);
      assert.equal(r.status, code);
    } finally { await srv.schliessen(); }
  }
});

for (const code of [410, 404]) {
  test(`senden: ${code} = ungültig, keine Wiederholung`, async () => {
    const srv = await starteServer([code]);
    try {
      const { abo } = neuesAbo(`http://127.0.0.1:${srv.port}/p`);
      const r = await senden(abo, neuerVapid(), { titel: "a", text: "b", ziel: "c" }, schnell);
      assert.deepEqual(r, { status: code, ok: false, ungueltig: true });
      assert.equal(srv.aufrufe.length, 1);
    } finally { await srv.schliessen(); }
  });
}

test("senden: 500, 500, 500 = Fehler nach genau 3 Versuchen (Wartezeiten 2 s, 5 s)", async () => {
  const srv = await starteServer([500]);
  const waits = [];
  try {
    const { abo } = neuesAbo(`http://127.0.0.1:${srv.port}/p`);
    const r = await senden(abo, neuerVapid(), { titel: "a", text: "b", ziel: "c" }, { warte: async (ms) => { waits.push(ms); } });
    assert.deepEqual(r, { status: 500, ok: false, ungueltig: false });
    assert.equal(srv.aufrufe.length, 3);
    assert.deepEqual(waits, [2000, 5000]);
  } finally { await srv.schliessen(); }
});

test("senden: 429 dann 201 = ok nach 2 Aufrufen", async () => {
  const srv = await starteServer([429, 201]);
  try {
    const { abo } = neuesAbo(`http://127.0.0.1:${srv.port}/p`);
    const r = await senden(abo, neuerVapid(), { titel: "a", text: "b", ziel: "c" }, schnell);
    assert.deepEqual(r, { status: 201, ok: true, ungueltig: false });
    assert.equal(srv.aufrufe.length, 2);
  } finally { await srv.schliessen(); }
});

for (const code of [400, 401, 403, 413]) {
  test(`senden: ${code} = sofort Fehler`, async () => {
    const srv = await starteServer([code]);
    try {
      const { abo } = neuesAbo(`http://127.0.0.1:${srv.port}/p`);
      const r = await senden(abo, neuerVapid(), { titel: "a", text: "b", ziel: "c" }, schnell);
      assert.deepEqual(r, { status: code, ok: false, ungueltig: false });
      assert.equal(srv.aufrufe.length, 1);
    } finally { await srv.schliessen(); }
  });
}

test("senden: Netzfehler wird wiederholt und liefert keine Ausnahme mit Endpoint", async () => {
  let n = 0;
  const f = async () => { n++; throw new Error("connect ECONNREFUSED https://geheim.example/pfad"); };
  const { abo } = neuesAbo("https://geheim.example/pfad");
  const r = await senden(abo, neuerVapid(), { titel: "a", text: "b", ziel: "c" }, { fetch: f, ...schnell });
  assert.deepEqual(r, { status: 0, ok: false, ungueltig: false });
  assert.equal(n, 3);
});

test("senden: JSON über 3000 Byte wird am Text gekürzt (Zeichengrenze, Suffix)", async () => {
  const srv = await starteServer([201]);
  try {
    const { ua, auth, abo } = neuesAbo(`http://127.0.0.1:${srv.port}/p`);
    const lang = "Größe äöü 😀 ".repeat(600); // Mehrbyte-Zeichen, weit über 3000 Byte
    await senden(abo, neuerVapid(), { titel: "T", text: lang, ziel: "./#x" }, schnell);
    const klar = entschluesseln(srv.aufrufe[0].body, ua, auth);
    assert.ok(klar.length <= 3000, `Länge ${klar.length}`);
    assert.ok(klar.length > 2900, "nicht übermäßig gekürzt");
    const o = JSON.parse(klar.toString("utf8")); // gültiges UTF-8 und JSON
    assert.ok(o.text.endsWith(" … (weitere in der App)"));
    assert.ok(!o.text.includes("�"));
    assert.equal(o.titel, "T");
    assert.equal(o.ziel, "./#x");
  } finally { await srv.schliessen(); }
});

test("vapidKopf: aud = Origin des Endpoints, ungültiger Schlüssel gibt keinen Inhalt preis", () => {
  const jwk = neuerVapid();
  const kopf = vapidKopf("https://fcm.googleapis.com/fcm/send/GEHEIM", jwk, Math.floor(Date.now() / 1000));
  jwtPruefen(kopf, "https://fcm.googleapis.com");
  assert.ok(!kopf.includes("GEHEIM"));
  assert.ok(!kopf.includes(jwk.d));
  assert.throws(() => vapidKopf("https://a.example/x", { kty: "EC", crv: "P-256", x: "a", y: "b", d: "GEHEIMD" }, 1), (e) => !/GEHEIMD/.test(e.message));
});

// ---- 4. CLI ---------------------------------------------------------------------
function cli(args, env = {}, entferne = []) {
  const e = { ...process.env, ...env };
  for (const k of entferne) delete e[k];
  const r = spawnSync(process.execPath, [SKRIPT, ...args], { env: e, encoding: "utf8", timeout: 60000 });
  return { code: r.status, out: (r.stdout || "") + (r.stderr || ""), stdout: r.stdout || "", stderr: r.stderr || "" };
}

function tempOrdner() { return fs.mkdtempSync(path.join(os.tmpdir(), "webpush-test-")); }

function geheimnisseFrei(ausgabe, abo, jwk) {
  const pfad = new URL(abo.endpoint).pathname;
  for (const g of [pfad, abo.keys.auth, abo.keys.p256dh, jwk.d]) {
    assert.ok(g.length > 8 && !ausgabe.includes(g), `Geheimnis in Ausgabe: ${g.slice(0, 4)}…`);
  }
}

test("CLI: fehlende Umgebung = Exit 5, ohne Geheimnisse", () => {
  const dir = tempOrdner();
  try {
    const datei = path.join(dir, "text.txt");
    fs.writeFileSync(datei, "Hallo");
    const r = cli(["--senden", "--datei", datei], {}, ["PUSH_ABO", "VAPID_PRIVAT"]);
    assert.equal(r.code, 5);
    assert.match(r.out, /PUSH_ABO/);
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});

test("CLI: gültiger Lauf = Exit 0; 410 = Exit 4; leere Datei = Exit 5; keine Geheimnisse in der Ausgabe", async () => {
  const dir = tempOrdner();
  const jwk = neuerVapid();
  try {
    const datei = path.join(dir, "text.txt");
    fs.writeFileSync(datei, "Preis gefallen");
    const leer = path.join(dir, "leer.txt");
    fs.writeFileSync(leer, "  \n");

    const srv = await starteServer([201]);
    try {
      const { abo } = neuesAbo(`http://127.0.0.1:${srv.port}/sehr/geheimer/pfad-123`);
      const env = { PUSH_ABO: JSON.stringify(abo), VAPID_PRIVAT: JSON.stringify(jwk) };
      const r = await new Promise((res) => {
        // asynchron starten, damit der Server im selben Prozess weiter antworten kann
        import("node:child_process").then(({ execFile }) =>
          execFile(process.execPath, [SKRIPT, "--senden", "--datei", datei], { env: { ...process.env, ...env } },
            (err, so, se) => res({ code: err ? err.code : 0, out: so + se })));
      });
      assert.equal(r.code, 0, r.out);
      assert.match(r.out, /127\.0\.0\.1/);
      geheimnisseFrei(r.out, abo, jwk);
      assert.equal(srv.aufrufe.length, 1);

      const r5 = await new Promise((res) => {
        import("node:child_process").then(({ execFile }) =>
          execFile(process.execPath, [SKRIPT, "--senden", "--datei", leer], { env: { ...process.env, ...env } },
            (err, so, se) => res({ code: err ? err.code : 0, out: so + se })));
      });
      assert.equal(r5.code, 5);
      geheimnisseFrei(r5.out, abo, jwk);
    } finally { await srv.schliessen(); }

    const srv410 = await starteServer([410]);
    try {
      const { abo } = neuesAbo(`http://127.0.0.1:${srv410.port}/sehr/geheimer/pfad-410`);
      const env = { PUSH_ABO: JSON.stringify(abo), VAPID_PRIVAT: JSON.stringify(jwk) };
      const r = await new Promise((res) => {
        import("node:child_process").then(({ execFile }) =>
          execFile(process.execPath, [SKRIPT, "--senden", "--datei", datei], { env: { ...process.env, ...env } },
            (err, so, se) => res({ code: err ? err.code : 0, out: so + se })));
      });
      assert.equal(r.code, 4, r.out);
      assert.match(r.out, /Push einrichten/);
      assert.match(r.out, /PUSH_ABO/);
      geheimnisseFrei(r.out, abo, jwk);
    } finally { await srv410.schliessen(); }
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});

test("CLI: ungültiges PUSH_ABO/VAPID_PRIVAT = Exit 5 ohne Inhalt in der Ausgabe", () => {
  const dir = tempOrdner();
  try {
    const datei = path.join(dir, "t.txt");
    fs.writeFileSync(datei, "x");
    const r = cli(["--senden", "--datei", datei], { PUSH_ABO: "{geheim-kaputt", VAPID_PRIVAT: "{}" });
    assert.equal(r.code, 5);
    assert.ok(!r.out.includes("geheim-kaputt"));
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});

// ---- 5. --neuer-schluessel / --oeffentlich / --selbsttest ------------------------
test("--neuer-schluessel verweigert Pfad im Projektordner", () => {
  const ziel = path.join(PROJEKT, "werkzeuge", "webpush-test-schluessel-darf-nicht-entstehen.json");
  try {
    const r = cli(["--neuer-schluessel", ziel]);
    assert.notEqual(r.code, 0);
    assert.ok(!fs.existsSync(ziel), "Datei im Projektordner darf nicht entstehen");
  } finally { fs.rmSync(ziel, { force: true }); }
});

test("--neuer-schluessel verweigert vorhandene Datei (unverändert)", () => {
  const dir = tempOrdner();
  try {
    const datei = path.join(dir, "vorhanden.json");
    fs.writeFileSync(datei, "ORIGINAL");
    const r = cli(["--neuer-schluessel", datei]);
    assert.notEqual(r.code, 0);
    assert.equal(fs.readFileSync(datei, "utf8"), "ORIGINAL");
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});

test("--neuer-schluessel und --oeffentlich liefern denselben öffentlichen Schlüssel, ohne d", () => {
  const dir = tempOrdner();
  try {
    const datei = path.join(dir, "vapid.json");
    const r = cli(["--neuer-schluessel", datei]);
    assert.equal(r.code, 0, r.out);
    const jwk = JSON.parse(fs.readFileSync(datei, "utf8"));
    assert.ok(jwk.d && jwk.x && jwk.y);
    const pub = r.stdout.trim();
    assert.equal(b64u(pub).length, 65);
    assert.ok(!r.out.includes(jwk.d), "d nicht in der Ausgabe");
    const r2 = cli(["--oeffentlich"], { VAPID_PRIVAT: JSON.stringify(jwk) });
    assert.equal(r2.code, 0, r2.out);
    assert.equal(r2.stdout.trim(), pub);
    assert.ok(!r2.out.includes(jwk.d));
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});

test("--selbsttest: Exit 0", () => {
  const r = cli(["--selbsttest"]);
  assert.equal(r.code, 0, r.out);
  assert.ok(!/FEHLER/.test(r.out));
});
