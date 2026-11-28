// Bildschirmfotos G1 (375 px, hell/dunkel) per Chrome headless und DevTools-Protokoll.
// Aufruf: CHROME=<pfad zu chrome> node fotos.mjs <basis-url> <ausgabeordner>   (Pfad nur lokal, VER-01)
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";

const [basis, aus] = process.argv.slice(2);
if (!process.env.CHROME) { console.error("CHROME (Pfad zur Chrome-Programmdatei) fehlt"); process.exit(2); }
fs.mkdirSync(aus, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const profil = fs.mkdtempSync(path.join(os.tmpdir(), "kbfoto-"));
const chrome = spawn(process.env.CHROME, ["--headless=new", "--remote-debugging-port=9335",
  `--user-data-dir=${profil}`, "--no-first-run", "--no-default-browser-check", "--disable-extensions", "about:blank"], { stdio: "ignore" });
let ziele = null;
for (let i = 0; i < 50 && !ziele; i++) { await sleep(200); try { ziele = await (await fetch("http://127.0.0.1:9335/json")).json(); } catch {} }
const seite = ziele.find(z => z.type === "page");
const ws = new WebSocket(seite.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r));
let nr = 0; const offen = new Map();
ws.addEventListener("message", e => { const m = JSON.parse(e.data); if (m.id && offen.has(m.id)) { offen.get(m.id)(m); offen.delete(m.id); } });
const cdp = (method, params = {}) => new Promise(r => { const id = ++nr; offen.set(id, r); ws.send(JSON.stringify({ id, method, params })); }).then(m => { if (m.error) throw new Error(method + ": " + m.error.message); return m.result; });
const js = async ausdruck => (await cdp("Runtime.evaluate", { expression: ausdruck, awaitPromise: true, returnByValue: true })).result.value;

await cdp("Page.enable");
await cdp("Emulation.setDeviceMetricsOverride", { width: 375, height: 812, deviceScaleFactor: 2, mobile: true });
await cdp("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
const adresse = basis + "#k=fernseher&s=ergebnis&b=1000&v=lg-oled-b6-55~lg-oled-c6-48~lg-oled-c6-42";
const bericht = {};
for (const schema of ["hell", "dunkel"]) {
  await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: schema === "hell" ? "light" : "dark" }] });
  await cdp("Page.navigate", { url: adresse });
  for (let i = 0; i < 40; i++) { await sleep(250); if (await js("!!document.getElementById('vgl-titel') && document.fonts.status === 'loaded'")) break; }
  await sleep(400);
  bericht[schema] = await js(`({ geist: document.fonts.check('16px Geist'), breite: document.documentElement.scrollWidth,
    klein: [...document.querySelectorAll('button, .chip, a.knopf, input[type=range]')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.height < 44; }).map(e => (e.className || e.tagName) + ':' + Math.round(e.getBoundingClientRect().height)) })`);
  // Ablage unten ausblenden, damit sie in den Ausschnitten nichts verdeckt
  await js("document.getElementById('ablage').style.visibility='hidden'; true");
  const teile = [["1-oben", ".hauptspalte", 0, 812], ["2-empfehlung", ".empfehlung"], ["3-regler", "#prio"], ["4-rangliste", "#ergebnis-unten > .abschnitt"], ["5-vergleich", "#vergleich"]];
  for (const [name, sel, y0, hoehe] of teile) {
    const r = await js(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); const b = e.getBoundingClientRect(); return { y: b.top + scrollY, h: b.height }; })()`);
    const y = y0 === undefined ? Math.max(0, r.y - 12) : y0;
    const h = hoehe || Math.min(r.h + 24, 2400);
    const bild = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { x: 0, y, width: 375, height: h, scale: 1 } });
    fs.writeFileSync(path.join(aus, `g1-${schema}-${name}.png`), Buffer.from(bild.data, "base64"));
  }
  await js("document.getElementById('ablage').style.visibility=''; true");
}
fs.writeFileSync(path.join(aus, "bericht.json"), JSON.stringify(bericht, null, 2));
console.log(JSON.stringify(bericht));
ws.close(); chrome.kill();
