// Browserprüfung der Kaufberatungs-App mit Chrome headless über das DevTools-Protokoll (nur node + vorhandenes Chrome).
// Aufruf: node pruefe.mjs <dist-Ordner> <Ausgabeordner> [--url https://…]  (ohne --url: eigener Server, Offline = Server stoppen)
import { spawn } from "node:child_process";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";

// dist absolut auflösen: der Server vergleicht mit path.resolve(dist), ein relativer Pfad ergäbe sonst nur 404
const [distArg, aus] = process.argv.slice(2);
const dist = path.resolve(distArg);
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

const ergebnis = { basis };
const messen = `
  const sichtbar = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const klein = [...document.querySelectorAll('.tabs button, .segx button, .seg button, .chip, .navlinks a, .brand, .kbapp-knoepfe button, .kbapp-wecker button, nav a, button')]
    .filter(sichtbar).filter(e => e.getBoundingClientRect().height < 44).map(e => (e.className||e.tagName) + '<' + (e.parentElement.className||'') + '#' + ((e.closest('[id]')||{}).id||'') + ':' + (e.textContent||'').trim().slice(0,20) + ':' + Math.round(e.getBoundingClientRect().height));
  return { scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth, bodyScrollW: document.body.scrollWidth,
    coarse: matchMedia('(pointer: coarse)').matches, dunkel: matchMedia('(prefers-color-scheme: dark)').matches,
    bg: getComputedStyle(document.body).backgroundColor, klein: [...new Set(klein)].slice(0, 60), anzahlKlein: klein.length };`;

// 1. Erstes Öffnen: Service Worker, kein Doppel-Laden
await laden(basis);
await js(`window.__marke = 1; return 1`);
ergebnis.swBereit = await js(`const r = await Promise.race([navigator.serviceWorker.ready.then(r=>r.active&&r.active.state), new Promise(x=>setTimeout(()=>x('zeitüberschreitung'),8000))]); return r`);
await sleep(1500);
ergebnis.ersterBesuch = await js(`return { marke: window.__marke === 1, controller: !!navigator.serviceWorker.controller, caches: await caches.keys(),
  appDateien: (await (await caches.open((await caches.keys()).find(k=>k.startsWith('kb-app-')))).keys()).map(r=>r.url.replace(location.origin,'')) }`);
ergebnis.manifest = await cdp("Page.getAppManifest").then(m => ({ fehler: m.errors, url: m.url })).catch(e => e.message);
ergebnis.installierbar = await cdp("Page.getInstallabilityErrors").then(m => m.installabilityErrors).catch(e => e.message);
// 2. hell
await neu();
ergebnis.hell = await js(messen);
ergebnis.weckerHinweis = await js(`const b = document.getElementById('kbapp-wecker'); return b ? b.textContent.slice(0,120) : null`);
await bild("hell-oben.png");
// 3. dunkel
await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
await sleep(800);
ergebnis.dunkel = await js(messen);
await bild("dunkel-oben.png");
await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });
// 4. Treffer-Hinweis
await js(`localStorage.setItem('kb-app:wunsch', JSON.stringify({tcl_c8l:{preis:2400}})); return 1`);
await neu();
ergebnis.treffer = await js(`const k = document.getElementById('kbapp-treffer'); return k ? { text: k.textContent, rolle: k.getAttribute('role'), hoehe: Math.round(k.getBoundingClientRect().height) } : null`);
await bild("treffer.png");
await js(`localStorage.removeItem('kb-app:wunsch'); return 1`);
// 4b. Runde 6 (nur wenn Preiswecker vorhanden): Status, Preise, Wunschpreis setzen und löschen
if (await js(`return !!document.getElementById('preiswecker')`)) {
  await neu();   // Wunschpreis aus Schritt 4 ist gelöscht: frisch laden, sonst gilt 2400 als unverändert
  await js(`document.getElementById('tab-tv').click(); location.hash='#preiswecker'; return 1`); await sleep(800);
  ergebnis.r6 = { status: await js(`return document.getElementById('pw-status').textContent`),
    liste: await js(`return document.getElementById('pw-liste').textContent.slice(0,400)`),
    hinweis: await js(`const b=document.getElementById('kbapp-wecker'); return b ? {text:b.textContent, sichtbar: b.getBoundingClientRect().height>0} : null`),
    formSichtbar: await js(`const f=document.getElementById('pw-w-tcl_c8l'); return !!f && f.closest('form').hidden===false`) };
  await js(`const i=document.getElementById('pw-w-tcl_c8l'); i.value='2400'; i.closest('form').requestSubmit(); return 1`); await sleep(1200);
  ergebnis.r6.nachSetzen = await js(`return { ls: localStorage.getItem('kb-app:wunsch'), fehler: document.getElementById('pw-f-tcl_c8l').hidden ? null : document.getElementById('pw-f-tcl_c8l').textContent,
    treffer: (document.getElementById('kbapp-treffer')||{}).textContent || null }`);
  await bild("r6-wunsch.png");
  await neu();
  ergebnis.r6.nachNeuladen = await js(`return { feld: document.getElementById('pw-w-tcl_c8l').value, treffer: !!document.getElementById('kbapp-treffer') }`);
  await js(`const i=document.getElementById('pw-w-tcl_c8l'); i.value=''; i.closest('form').requestSubmit(); return 1`); await sleep(1200);
  ergebnis.r6.nachLoeschen = await js(`return { ls: localStorage.getItem('kb-app:wunsch'), fehler: document.getElementById('pw-f-tcl_c8l').hidden ? null : document.getElementById('pw-f-tcl_c8l').textContent,
    treffer: !!document.getElementById('kbapp-treffer') }`);
  await js(`location.hash='#preiswecker'; return 1`); await sleep(500);
  ergebnis.r6.messung = await js(messen);
  await bild("r6-wecker.png");
  ergebnis.r6.punkte = await js(`const bs=[...document.querySelectorAll('.es-dots button')]; if(!bs.length) return null; /* sofort scrollen (die Seite hat scroll-behavior:smooth): erst an den Abschnittsanfang, damit der klebende Ergebnisstand
       an seiner normalen Stelle steht, dann die Punkte in die Bildmitte (dort klebt er nicht unter der Navigationsleiste) */
    const sp = t => window.scrollTo({top: t, behavior:'instant'});
    sp(document.getElementById('entscheiden').getBoundingClientRect().top + scrollY); await new Promise(r=>setTimeout(r,200));
    sp(bs[0].getBoundingClientRect().top + scrollY - innerHeight/2); await new Promise(r=>setTimeout(r,300));
    return bs.map(b=>{const r=b.getBoundingClientRect(), x=r.left+r.width/2, y=r.top+r.height/2; return [-20,0,20].map(d=>document.elementFromPoint(x,y+d)===b).join('/')})`);
  await bild("r6-punkte.png");
}
// 5. Offline: Server stoppen (bzw. Netz abschalten) und neu laden
if (server) { server.closeAllConnections?.(); await new Promise(r => server.close(r)); }
await cdp("Network.emulateNetworkConditions", { offline: true, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
const vorOffline = meldungen.length;
await neu();
ergebnis.offline = await js(`return { titel: document.title, reiter: !!document.getElementById('tab-tv'), controller: !!navigator.serviceWorker.controller,
  preise: Object.keys((await window.__kbApp.ladePreise()).preise).length, scrollW: document.documentElement.scrollWidth }`);
await bild("offline.png");
ergebnis.meldungenOffline = meldungen.slice(vorOffline);
ergebnis.meldungen = meldungen.slice(0, vorOffline);
fs.writeFileSync(path.join(aus, "ergebnis.json"), JSON.stringify(ergebnis, null, 1));
console.log(JSON.stringify(ergebnis, null, 1));
ws.close(); chrome.kill(); process.exit(0);
