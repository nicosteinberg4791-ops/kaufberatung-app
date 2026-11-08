// Browserprüfung der Kaufberatungs-App mit Chrome headless über das DevTools-Protokoll (nur node + vorhandenes Chrome).
// Aufruf: node pruefe.mjs <dist-Ordner> <Ausgabeordner> [--url https://…]  (ohne --url: eigener Server, Offline = Server stoppen)
import { spawn } from "node:child_process";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";

const [dist, aus] = process.argv.slice(2);
const urlArg = process.argv.indexOf("--url") > 0 ? process.argv[process.argv.indexOf("--url") + 1] : null;
fs.mkdirSync(aus, { recursive: true });
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const TYPEN = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
  ".webmanifest": "application/manifest+json", ".png": "image/png", ".svg": "image/svg+xml" };
const sleep = ms => new Promise(r => setTimeout(r, ms));

// --- eigener Server ---
let server = null, basis = urlArg;
if (!urlArg) {
  server = http.createServer((q, s) => {
    let p = decodeURIComponent(new URL(q.url, "http://x").pathname);
    if (p.endsWith("/")) p += "index.html";
    const f = path.join(dist, p);
    if (!f.startsWith(path.resolve(dist)) || !fs.existsSync(f)) { s.writeHead(404); s.end("404"); return; }
    s.writeHead(200, { "Content-Type": TYPEN[path.extname(f)] || "application/octet-stream" });
    s.end(fs.readFileSync(f));
  });
  await new Promise(r => server.listen(8793, "127.0.0.1", r));
  basis = "http://127.0.0.1:8793/";
}

// --- Chrome ---
const profil = fs.mkdtempSync(path.join(os.tmpdir(), "kbcdp-"));
const chrome = spawn(CHROME, ["--headless=new", "--remote-debugging-port=9334", `--user-data-dir=${profil}`, "--no-first-run",
  "--no-default-browser-check", "--disable-extensions", "about:blank"], { stdio: "ignore" });
let ziele = null;
for (let i = 0; i < 50 && !ziele; i++) { await sleep(200); try { ziele = await (await fetch("http://127.0.0.1:9334/json")).json(); } catch {} }
const seite = ziele.find(t => t.type === "page");
const ws = new WebSocket(seite.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r));
let nr = 0; const offen = new Map(); const meldungen = []; const ereignisse = [];
ws.addEventListener("message", ev => {
  const m = JSON.parse(ev.data);
  if (m.id && offen.has(m.id)) { offen.get(m.id)(m); offen.delete(m.id); return; }
  ereignisse.push(m.method);
  if (m.method === "Runtime.consoleAPICalled") meldungen.push(`[${m.params.type}] ` + m.params.args.map(a => a.value ?? a.description ?? "").join(" "));
  if (m.method === "Runtime.exceptionThrown") meldungen.push("[exception] " + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text));
  if (m.method === "Log.entryAdded") meldungen.push(`[log ${m.params.entry.level}] ${m.params.entry.text} ${m.params.entry.url || ""}`);
});
const cdp = (method, params = {}) => new Promise((r, x) => { const id = ++nr; offen.set(id, m => m.error ? x(new Error(method + ": " + m.error.message)) : r(m.result)); ws.send(JSON.stringify({ id, method, params })); });
const js = async expr => { const r = await cdp("Runtime.evaluate", { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; };
const bild = async name => { const r = await cdp("Page.captureScreenshot", { format: "png" }); fs.writeFileSync(path.join(aus, name), Buffer.from(r.data, "base64")); };
const laden = async url => { const t0 = ereignisse.length; await cdp("Page.navigate", { url }); for (let i = 0; i < 100; i++) { await sleep(100); if (ereignisse.slice(t0).includes("Page.loadEventFired")) break; } await sleep(1500); };
const neu = async () => { const t0 = ereignisse.length; await cdp("Page.reload", { ignoreCache: false }); for (let i = 0; i < 100; i++) { await sleep(100); if (ereignisse.slice(t0).includes("Page.loadEventFired")) break; } await sleep(1500); };

await cdp("Page.enable"); await cdp("Runtime.enable"); await cdp("Log.enable"); await cdp("Network.enable");
await cdp("Emulation.setDeviceMetricsOverride", { width: 375, height: 812, deviceScaleFactor: 2, mobile: true });
await cdp("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });


import { execSync } from "node:child_process";
const kopie = path.resolve(dist, "..");
const e = {};
await laden(basis);
await js(`await navigator.serviceWorker.ready; return 1`); await sleep(1000);
e.v1 = await js(`return (await caches.keys()).filter(k=>k.startsWith('kb-app-'))`);
const pj = path.join(dist, "preise.json"), pjAlt = fs.readFileSync(pj);
fs.writeFileSync(pj, process.argv.includes("--null") ? JSON.stringify({preise:{lg_c6elb:null}}) : "<html><body>Fehlerseite</body></html>");
e.b4 = await js(`const r = await fetch('preise.json', {cache:'no-store'}); const t = await r.text();
  const c = await (await caches.open('kb-daten')).match('preise.json'); const ct = c ? await c.text() : null;
  let ok = false; try { ok = !!JSON.parse(ct).preise } catch (x) {} return { antwortGecacht: t.includes('heiseUrl'), cacheGueltig: ok }`);
fs.writeFileSync(pj, pjAlt);
fs.appendFileSync(path.join(kopie, "app", "app.css"), "\n/* Teständerung */\n");
execSync(`python -I "${path.join(kopie, "werkzeuge", "app_bauen.py")}"`);
await js(`const r = await navigator.serviceWorker.getRegistration(); await r.update(); return 1`);
for (let i = 0; i < 40; i++) { await sleep(250); if (await js(`return !!document.getElementById('kbapp-neu')`)) break; }
e.karte = await js(`const k=document.getElementById('kbapp-neu'); return k ? k.textContent : null`);
await bild("update-karte.png");
const t0 = ereignisse.length;
if (process.argv.includes('--fremd')) await js(`(await navigator.serviceWorker.getRegistration()).waiting.postMessage('jetzt'); return 1`);
else await js(`document.querySelector('#kbapp-neu .kbapp-haupt').click(); return 1`);
for (let i = 0; i < 60; i++) { await sleep(200); if (ereignisse.slice(t0).includes("Page.loadEventFired")) break; }
await sleep(1500);
e.nachNeuLaden = await js(`return { caches: (await caches.keys()).filter(k=>k.startsWith('kb-app-')), karte: !!document.getElementById('kbapp-neu'),
  css: [...document.styleSheets].map(s=>s.href||'').filter(h=>h.includes('app.css')) }`);
e.meldungen = meldungen;
console.log(JSON.stringify(e, null, 1));
ws.close(); chrome.kill(); process.exit(0);
