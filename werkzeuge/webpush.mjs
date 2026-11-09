// webpush.mjs - Sende-Werkzeug für Standard-Web-Push (ohne Firebase-Projekt, ohne npm-Pakete).
// Zweck: Der tägliche GitHub-Actions-Lauf schickt damit eine Benachrichtigung an die installierte App.
// Normen: RFC 8030 (Web Push), RFC 8291 (Nachrichtenverschlüsselung, aes128gcm), RFC 8292 (VAPID, ES256-JWT).
// Nur node:crypto, node:fs, node:path, node:url und das globale fetch (Node >= 18).
//
// Aufruf (CLI):
//   node werkzeuge/webpush.mjs --senden --datei <textdatei> [--titel "TV-Preiswecker"] [--ziel "./#preiswecker"]
//   node werkzeuge/webpush.mjs --neuer-schluessel <datei>   (privater JWK in Datei, öffentlicher Schlüssel auf stdout)
//   node werkzeuge/webpush.mjs --oeffentlich                (öffentlicher Schlüssel aus VAPID_PRIVAT)
//   node werkzeuge/webpush.mjs --selbsttest                 (RFC-8291-Vektoren + JWT-Signatur)
//
// Exitcodes: 0 = gesendet/erfolgreich, 1 = sonstiger Fehler, 4 = Abo ungültig (HTTP 404/410),
//            5 = Konfiguration fehlt oder ist ungültig.
// Secrets (nur über Umgebungsvariablen, nie in Repo/Chat/Ausgabe):
//   PUSH_ABO      = PushSubscription.toJSON() als JSON ({endpoint, keys:{p256dh, auth}})
//   VAPID_PRIVAT  = privater VAPID-Schlüssel als JWK-JSON (P-256, mit x, y, d)
// Geheimnisschutz: Es werden nie Endpoint-Pfad, p256dh, auth, JWT oder privater Schlüssel ausgegeben;
// erlaubt sind nur der Host des Endpoints und der HTTP-Status.

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const SKRIPT = fileURLToPath(import.meta.url);
const PROJEKTORDNER = path.resolve(path.dirname(SKRIPT), "..");
const SUBJEKT = "https://nicosteinberg4791-ops.github.io/kaufberatung-app/";
const MAX_JSON_BYTES = 3000;
const KUERZUNG = " … (weitere in der App)";

// Fehler mit bereinigter Meldung; code: "konfig" (Exit 5) oder "fehler" (Exit 1)
export class WebPushFehler extends Error {
  constructor(meldung, code = "fehler") {
    super(meldung);
    this.name = "WebPushFehler";
    this.code = code;
  }
}
const konfigFehler = (m) => new WebPushFehler(m, "konfig");

const hmac = (k, d) => crypto.createHmac("sha256", k).update(d).digest();
const b64u = (buf) => Buffer.from(buf).toString("base64url");
const vonB64u = (s) => Buffer.from(String(s ?? "").replace(/\s+/g, ""), "base64url");

// ---------------------------------------------------------------- Abo prüfen
function pruefeAbo(abo) {
  if (!abo || typeof abo !== "object" || !abo.keys || typeof abo.endpoint !== "string") {
    throw konfigFehler("Abo ungültig: endpoint oder keys fehlen");
  }
  let url;
  try { url = new URL(abo.endpoint); } catch { throw konfigFehler("Abo ungültig: endpoint ist keine URL"); }
  const lokal = url.hostname === "127.0.0.1" || url.hostname === "localhost";
  if (url.protocol !== "https:" && !(url.protocol === "http:" && lokal)) {
    throw konfigFehler("Abo ungültig: endpoint muss https sein");
  }
  const p256dh = vonB64u(abo.keys.p256dh);
  const auth = vonB64u(abo.keys.auth);
  if (p256dh.length !== 65 || p256dh[0] !== 4) throw konfigFehler("Abo ungültig: p256dh muss 65 Byte (unkomprimiert) ergeben");
  if (auth.length !== 16) throw konfigFehler("Abo ungültig: auth muss 16 Byte ergeben");
  return { url, p256dh, auth };
}

// ---------------------------------------------------------------- RFC 8291
// Leitet alle Zwischenwerte ab (auch für Tests/Selbsttest sichtbar)
export function ableiten(abo, { asEcdh, salt } = {}) {
  const { p256dh, auth } = pruefeAbo(abo);
  const ecdhObj = asEcdh ?? (() => { const e = crypto.createECDH("prime256v1"); e.generateKeys(); return e; })();
  const saltBytes = salt ?? crypto.randomBytes(16);
  if (saltBytes.length !== 16) throw konfigFehler("Salz muss 16 Byte lang sein");
  const asPublic = ecdhObj.getPublicKey();
  let ecdh;
  try { ecdh = ecdhObj.computeSecret(p256dh); } catch { throw konfigFehler("Abo ungültig: p256dh ist kein gültiger P-256-Punkt"); }
  const prkKey = hmac(auth, ecdh);
  const keyInfo = Buffer.concat([Buffer.from("WebPush: info\0"), p256dh, asPublic]);
  const ikm = hmac(prkKey, Buffer.concat([keyInfo, Buffer.from([1])]));
  const prk = hmac(saltBytes, ikm);
  const cek = hmac(prk, Buffer.from("Content-Encoding: aes128gcm\0\x01", "latin1")).subarray(0, 16);
  const nonce = hmac(prk, Buffer.from("Content-Encoding: nonce\0\x01", "latin1")).subarray(0, 12);
  return { ecdh, prkKey, ikm, prk, cek, nonce, asPublic, salt: saltBytes };
}

// Verschlüsselt den Klartext als aes128gcm-Körper: 86-Byte-Kopf + Chiffrat (rs 4096, Einzelrecord, Delimiter 0x02)
export function verschluesseln(klartext, abo, { asEcdh, salt } = {}) {
  const rs = 4096;
  if (klartext.length > rs - 17) throw new WebPushFehler("Klartext zu lang für einen Record");
  const z = ableiten(abo, { asEcdh, salt });
  const c = crypto.createCipheriv("aes-128-gcm", z.cek, z.nonce);
  const ct = Buffer.concat([c.update(Buffer.concat([klartext, Buffer.from([2])])), c.final(), c.getAuthTag()]);
  const kopf = Buffer.alloc(21);
  z.salt.copy(kopf, 0);
  kopf.writeUInt32BE(rs, 16);
  kopf[20] = z.asPublic.length;
  return Buffer.concat([kopf, z.asPublic, ct]);
}

// ---------------------------------------------------------------- RFC 8292 (VAPID)
function privateKeyAusJwk(privJwk) {
  if (!privJwk || privJwk.kty !== "EC" || privJwk.crv !== "P-256" || !privJwk.x || !privJwk.y || !privJwk.d) {
    throw konfigFehler("VAPID_PRIVAT ungültig: P-256-JWK mit x, y, d erwartet");
  }
  try {
    return crypto.createPrivateKey({ key: { kty: "EC", crv: "P-256", x: privJwk.x, y: privJwk.y, d: privJwk.d }, format: "jwk" });
  } catch {
    throw konfigFehler("VAPID_PRIVAT ungültig: Schlüssel nicht lesbar");
  }
}

// Öffentlicher Schlüssel (65 Byte unkomprimiert) als base64url
export function oeffentlicherSchluessel(privJwk) {
  privateKeyAusJwk(privJwk);
  return b64u(Buffer.concat([Buffer.from([4]), vonB64u(privJwk.x), vonB64u(privJwk.y)]));
}

// Wert für den Authorization-Header: "vapid t=<jwt>, k=<öffentlicher Schlüssel>"
export function vapidKopf(endpoint, privJwk, jetztSek) {
  const key = privateKeyAusJwk(privJwk);
  const teil = (o) => Buffer.from(JSON.stringify(o)).toString("base64url");
  const daten = teil({ typ: "JWT", alg: "ES256" }) + "." +
    teil({ aud: new URL(endpoint).origin, exp: jetztSek + 12 * 3600, sub: SUBJEKT });
  const sig = crypto.sign("sha256", Buffer.from(daten), { key, dsaEncoding: "ieee-p1363" });
  return `vapid t=${daten}.${b64u(sig)}, k=${oeffentlicherSchluessel(privJwk)}`;
}

// ---------------------------------------------------------------- Senden
// JSON auf höchstens 3000 Byte bringen: text an Zeichengrenze kürzen
function nachrichtAlsJson(n) {
  const bauen = (text) => JSON.stringify({ titel: n.titel, text, ziel: n.ziel });
  let json = bauen(n.text);
  if (Buffer.byteLength(json) <= MAX_JSON_BYTES) return json;
  const zeichen = Array.from(String(n.text));
  let lo = 0, hi = zeichen.length;
  while (lo < hi) {
    const mitte = Math.ceil((lo + hi) / 2);
    if (Buffer.byteLength(bauen(zeichen.slice(0, mitte).join("") + KUERZUNG)) <= MAX_JSON_BYTES) lo = mitte; else hi = mitte - 1;
  }
  json = bauen(zeichen.slice(0, lo).join("") + KUERZUNG);
  return json;
}

const standardWarte = (ms) => new Promise((r) => setTimeout(r, ms));
const WARTEZEITEN = [2000, 5000];

export async function senden(abo, privJwk, nachricht, opt = {}) {
  const f = opt.fetch ?? globalThis.fetch;
  const warte = opt.warte ?? standardWarte;
  const versuche = opt.versuche ?? 3;
  const { url } = pruefeAbo(abo);
  const koerper = verschluesseln(Buffer.from(nachrichtAlsJson(nachricht), "utf8"), abo);
  let status = 0;
  for (let i = 0; i < versuche; i++) {
    if (i > 0) await warte(WARTEZEITEN[Math.min(i - 1, WARTEZEITEN.length - 1)]);
    try {
      const antwort = await f(abo.endpoint, {
        method: "POST",
        headers: {
          TTL: "86400",
          Urgency: "high",
          "Content-Encoding": "aes128gcm",
          "Content-Type": "application/octet-stream",
          Authorization: vapidKopf(abo.endpoint, privJwk, Math.floor(Date.now() / 1000)),
        },
        body: koerper,
        signal: AbortSignal.timeout(20000),
      });
      status = antwort.status;
      try { await antwort.arrayBuffer(); } catch { /* Antwortkörper unwichtig */ }
    } catch (e) {
      if (e instanceof WebPushFehler) throw e;
      status = 0; // Netzfehler: Meldung enthält ggf. die URL, daher nicht weitergeben
      continue;
    }
    if (status === 200 || status === 201 || status === 202) return { status, ok: true, ungueltig: false };
    if (status === 404 || status === 410) return { status, ok: false, ungueltig: true };
    if (status === 429 || status >= 500) continue;
    return { status, ok: false, ungueltig: false }; // 400/401/403/413 u. a.: sofort Fehler
  }
  return { status, ok: false, ungueltig: false };
}

// ---------------------------------------------------------------- Selbsttest
export function selbsttest() {
  const meldungen = [];
  let fehler = 0;
  const gleich = (name, ist, soll) => {
    const ok = ist.equals(vonB64u(soll));
    if (!ok) fehler++;
    meldungen.push((ok ? "OK     " : "FEHLER ") + name);
  };
  const asEcdh = crypto.createECDH("prime256v1");
  asEcdh.setPrivateKey(vonB64u("yfWPiYE-n46HLnH0KqZOF1fJJU3MYrct3AELtAQ-oRw"));
  const abo = {
    endpoint: "https://push.example.invalid/x",
    keys: {
      p256dh: "BCVxsr7N_eNgVRqvHtD0zTZsEc6-VV-JvLexhqUzORcxaOzi6-AYWXvTBHm4bjyPjs7Vd8pZGH6SRpkNtoIAiw4",
      auth: "BTBZMqHH6r4Tts7J_aSIgg",
    },
  };
  const salt = vonB64u("DGv6ra1nlYgDCS1FRnbzlw");
  const klartext = vonB64u("V2hlbiBJIGdyb3cgdXAsIEkgd2FudCB0byBiZSBhIHdhdGVybWVsb24");
  const z = ableiten(abo, { asEcdh, salt });
  gleich("as_public", z.asPublic, "BP4z9KsN6nGRTbVYI_c7VJSPQTBtkgcy27mlmlMoZIIgDll6e3vCYLocInmYWAmS6TlzAC8wEqKK6PBru3jl7A8");
  gleich("ECDH-Geheimnis", z.ecdh, "kyrL1jIIOHEzg3sM2ZWRHDRB62YACZhhSlknJ672kSs");
  gleich("PRK_key", z.prkKey, "Snr3JMxaHVDXHWJn5wdC52WjpCtd2EIEGBykDcZW32k");
  gleich("IKM", z.ikm, "S4lYMb_L0FxCeq0WhDx813KgSYqU26kOyzWUdsXYyrg");
  gleich("PRK", z.prk, "09_eUZGrsvxChDCGRCdkLiDXrReGOEVeSCdCcPBSJSc");
  gleich("CEK", z.cek, "oIhVW04MRdy2XN9CiKLxTg");
  gleich("NONCE", z.nonce, "4h_95klXJ5E_qnoN");
  const k = verschluesseln(klartext, abo, { asEcdh, salt });
  // Kopf (86 Byte) und Chiffrat getrennt vergleichen: base64url-Texte dürfen nicht aneinandergehängt werden
  gleich("Kopf (86 Byte)", k.subarray(0, 86),
    "DGv6ra1nlYgDCS1FRnbzlwAAEABBBP4z9KsN6nGRTbVYI_c7VJSPQTBtkgcy27mlmlMoZIIgDll6e3vCYLocInmYWAmS6TlzAC8wEqKK6PBru3jl7A8");
  gleich("Chiffrat (RFC 8291 Anhang A)", k.subarray(86),
    "8pfeW0KbunFT06SuDKoJH9Ql87S1QUrdirN6GcG7sFz1y1sqLgVi1VhjVkHsUoEsbI_0LpXMuGvnzQ");
  // JWT-Signatur erzeugen und mit dem öffentlichen Schlüssel prüfen
  const { privateKey } = crypto.generateKeyPairSync("ec", { namedCurve: "prime256v1" });
  const jwk = privateKey.export({ format: "jwk" });
  const kopf = vapidKopf("https://fcm.googleapis.com/fcm/send/abc", jwk, Math.floor(Date.now() / 1000));
  const m = /^vapid t=([^,]+), k=(.+)$/.exec(kopf);
  let sigOk = false;
  if (m) {
    const [h, c, s] = m[1].split(".");
    const pubRoh = vonB64u(m[2]);
    const pub = crypto.createPublicKey({ key: { kty: "EC", crv: "P-256", x: b64u(pubRoh.subarray(1, 33)), y: b64u(pubRoh.subarray(33, 65)) }, format: "jwk" });
    const sig = vonB64u(s);
    sigOk = pubRoh.length === 65 && sig.length === 64 &&
      crypto.verify("sha256", Buffer.from(h + "." + c), { key: pub, dsaEncoding: "ieee-p1363" }, sig) &&
      JSON.parse(vonB64u(c).toString()).aud === "https://fcm.googleapis.com";
  }
  if (!sigOk) fehler++;
  meldungen.push((sigOk ? "OK     " : "FEHLER ") + "VAPID-JWT ES256 (64 Byte r||s, prüfbar, aud = Origin)");
  return { fehler, meldungen };
}

// ---------------------------------------------------------------- CLI
function leseJsonEnv(name) {
  const roh = process.env[name];
  if (!roh || !roh.trim()) throw konfigFehler(`Umgebungsvariable ${name} fehlt`);
  try { return JSON.parse(roh); } catch { throw konfigFehler(`${name} ist kein gültiges JSON`); }
}

function innerhalbProjekt(ziel) {
  const aufloesen = (p) => {
    const abs = path.resolve(p);
    try { return path.join(fs.realpathSync(path.dirname(abs)), path.basename(abs)); } catch { return abs; }
  };
  const rel = path.relative(aufloesen(PROJEKTORDNER), aufloesen(ziel));
  return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
}

function argWert(args, name) {
  const i = args.indexOf(name);
  return i >= 0 && i + 1 < args.length ? args[i + 1] : undefined;
}

export async function cli(args) {
  if (args.includes("--selbsttest")) {
    const { fehler, meldungen } = selbsttest();
    console.log(meldungen.join("\n"));
    console.log(fehler ? `Selbsttest: ${fehler} Fehler` : "Selbsttest: alles in Ordnung");
    return fehler ? 1 : 0;
  }
  if (args.includes("--oeffentlich")) {
    console.log(oeffentlicherSchluessel(leseJsonEnv("VAPID_PRIVAT")));
    return 0;
  }
  if (args.includes("--neuer-schluessel")) {
    const datei = argWert(args, "--neuer-schluessel");
    if (!datei) throw konfigFehler("--neuer-schluessel braucht einen Dateipfad");
    if (innerhalbProjekt(datei)) throw konfigFehler("Verweigert: Der private Schlüssel darf nicht im Projektordner liegen");
    const { privateKey } = crypto.generateKeyPairSync("ec", { namedCurve: "prime256v1" });
    const jwk = privateKey.export({ format: "jwk" });
    try {
      fs.writeFileSync(datei, JSON.stringify(jwk), { flag: "wx", mode: 0o600 });
    } catch (e) {
      throw konfigFehler(e && e.code === "EEXIST" ? "Verweigert: Datei existiert bereits" : "Schlüsseldatei konnte nicht geschrieben werden");
    }
    console.log(oeffentlicherSchluessel(jwk));
    return 0;
  }
  if (args.includes("--senden")) {
    const datei = argWert(args, "--datei");
    if (!datei) throw konfigFehler("--senden braucht --datei <textdatei>");
    const abo = leseJsonEnv("PUSH_ABO");
    const priv = leseJsonEnv("VAPID_PRIVAT");
    let text;
    try { text = fs.readFileSync(datei, "utf8").trim(); } catch { throw konfigFehler("Textdatei nicht lesbar"); }
    if (!text) throw konfigFehler("Textdatei ist leer, nichts zu senden");
    const host = new URL(pruefeAbo(abo).url).host;
    const erg = await senden(abo, priv, {
      titel: argWert(args, "--titel") ?? "TV-Preiswecker",
      text,
      ziel: argWert(args, "--ziel") ?? "./#preiswecker",
    });
    if (erg.ok) { console.log(`Push gesendet (HTTP ${erg.status}) an ${host}`); return 0; }
    if (erg.ungueltig) {
      console.error(`Abo ungültig (HTTP ${erg.status} von ${host}): in der App „Push einrichten“ erneut tippen und Secret PUSH_ABO erneuern.`);
      return 4;
    }
    console.error(`Push fehlgeschlagen (HTTP ${erg.status || "Netzfehler"}) bei ${host}`);
    return 1;
  }
  console.error("Aufruf: --senden --datei <datei> [--titel T] [--ziel Z] | --neuer-schluessel <datei> | --oeffentlich | --selbsttest");
  return 5;
}

if (process.argv[1] && pathToFileURL(path.resolve(process.argv[1])).href === import.meta.url) {
  cli(process.argv.slice(2)).then(
    (code) => { process.exitCode = code; },
    (e) => {
      // Nur bereinigte Meldungen: nie e.message fremder Ausnahmen oder Stacktraces ausgeben
      if (e instanceof WebPushFehler) {
        console.error(e.message);
        process.exitCode = e.code === "konfig" ? 5 : 1;
      } else {
        console.error(`Unerwarteter Fehler (${e && e.name ? e.name : "unbekannt"})`);
        process.exitCode = 1;
      }
    },
  );
}
