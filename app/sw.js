/* Service Worker der Kaufberatungs-App. Der Build setzt VERSION und DATEIEN ein (werkzeuge/app_bauen.py).
   Strategie: App-Dateien aus dem versionierten Cache (offline), preise.json zuerst vom Netz (frisch, sonst Cache),
   Google-Schrift aus dem Laufzeit-Cache (veraltet-und-erneuern). Neue Fassung wartet, bis die Seite "jetzt" sagt. */
"use strict";
const VERSION = "__VERSION__";
const APP = "kb-app-" + VERSION;
const LAUFZEIT = "kb-laufzeit";
const DATEN = "kb-daten";            // preise.json, Wunschpreise (Spiegel aus der Seite), gemeldete Treffer
const DATEIEN = __DATEIEN__;
const SCHRIFT = ["https://fonts.googleapis.com", "https://fonts.gstatic.com"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(APP).then(c => c.addAll(DATEIEN.map(d => new Request(d, { cache: "reload" })))));
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith("kb-app-") && k !== APP) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener("message", e => {
  if (e.data === "jetzt") self.skipWaiting();
});

async function netzZuerst(req) {
  const c = await caches.open(DATEN);
  try {
    const ctl = new AbortController();
    const t = setTimeout(() => ctl.abort(), 6000);
    const r = await fetch(req, { cache: "no-store", signal: ctl.signal });
    clearTimeout(t);
    if (r.ok) { await c.put("preise.json", r.clone()); return r; }
    throw new Error("HTTP " + r.status);
  } catch (err) {
    const alt = await c.match("preise.json");
    return alt || new Response("{}", { status: 503, headers: { "Content-Type": "application/json" } });
  }
}

async function schriftCache(req) {
  const c = await caches.open(LAUFZEIT);
  const alt = await c.match(req);
  const neu = fetch(req).then(r => { if (r.ok || r.type === "opaque") c.put(req, r.clone()); return r; }).catch(() => alt);
  return alt || neu;
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    if (url.pathname.endsWith("/preise.json")) { e.respondWith(netzZuerst(req)); return; }
    e.respondWith((async () => {
      const c = await caches.open(APP);
      if (req.mode === "navigate") return (await c.match("./")) || fetch(req);
      return (await c.match(req, { ignoreSearch: true })) || fetch(req);
    })());
    return;
  }
  if (SCHRIFT.includes(url.origin)) e.respondWith(schriftCache(req));
});

/* Preiswecker im Hintergrund (nur installierte App in Chrome, Zeitpunkt bestimmt der Browser, ohne Gewähr) */
async function pruefePreise() {
  const c = await caches.open(DATEN);
  let preise = null, wunsch = {}, gemeldet = {};
  try { const r = await netzZuerst(new Request("preise.json")); preise = await r.json(); } catch (e) { return; }
  try { wunsch = (await (await c.match("wunsch.json")).json()) || {}; } catch (e) { wunsch = {}; }
  try { gemeldet = (await (await c.match("gemeldet.json")).json()) || {}; } catch (e) { gemeldet = {}; }
  const treffer = [];
  for (const [id, w] of Object.entries(wunsch)) {
    const p = preise && preise.preise && preise.preise[id];
    const g = p && p.aktuell && p.aktuell.gesamt;
    const wp = w && w.preis;
    if (typeof g !== "number" || typeof wp !== "number" || !(g <= wp)) continue;
    const sig = g + "|" + wp;
    if (gemeldet[id] === sig) continue;
    gemeldet[id] = sig;
    treffer.push((typeof p.name === "string" ? p.name.slice(0, 40) : id) + ": " + g.toLocaleString("de-DE") + " €");
  }
  if (!treffer.length) return;
  await c.put("gemeldet.json", new Response(JSON.stringify(gemeldet), { headers: { "Content-Type": "application/json" } }));
  if (self.Notification && Notification.permission === "granted") {
    await self.registration.showNotification("Preiswecker: Wunschpreis erreicht", {
      body: treffer.join(" · ").slice(0, 180), icon: "icons/icon-192.png", badge: "icons/icon-maskable-192.png",
      tag: "kb-preiswecker", data: { ziel: "./#preiswecker" }
    });
  }
}

self.addEventListener("periodicsync", e => {
  if (e.tag === "kb-preise") e.waitUntil(pruefePreise());
});

self.addEventListener("notificationclick", e => {
  e.notification.close();
  const ziel = new URL((e.notification.data && e.notification.data.ziel) || "./", self.registration.scope).href;
  e.waitUntil((async () => {
    const alle = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const k of alle) { if ("focus" in k) { await k.navigate(ziel).catch(() => {}); return k.focus(); } }
    return self.clients.openWindow(ziel);
  })());
});
