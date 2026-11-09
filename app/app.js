/* App-Hülle der Kaufberatung (läuft vor den Seitenskripten).
   1. Ersatz für window.claude.use("db" | "user"), damit die Seitenskripte (Preiswecker, Entscheiden ab Runde 6)
      unverändert laufen: "preise" und "wecker/lauf" kommen read-only aus preise.json, "wunsch" liegt per localStorage
      auf diesem Gerät. user.id() liefert null: Entscheiden bleibt bei seinem eigenen localStorage.
   2. Service Worker anmelden, neue Fassung melden ("Neu laden").
   3. Wunschpreis-Treffer beim Öffnen deutlich anzeigen; Benachrichtigung im Hintergrund nur als Versuch (ohne Gewähr).
   Alle Daten aus preise.json und localStorage sind fremde Daten: geprüft, nur textContent. */
(function () {
  "use strict";
  const IDS = ["lg_c6elb", "lg_c69lb", "sam_s90h", "tcl_c8l", "sam_qn90f", "af_cosori_tt", "af_medion_p20", "af_cosori_r901"];
  const LS_WUNSCH = "kb-app:wunsch";
  const LS_AUS = "kb-app:treffer-ausgeblendet";
  const zahlOk = x => typeof x === "number" && isFinite(x) && x > 0 && x < 100000;
  const eur = v => v.toLocaleString("de-DE", { minimumFractionDigits: Number.isInteger(v) ? 0 : 2, maximumFractionDigits: 2 }) + " €";

  function lsLies(k) { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch (e) { return null; } }
  function lsSchreib(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }

  function wunschAlle() {
    const roh = lsLies(LS_WUNSCH), out = {};
    if (roh && typeof roh === "object") for (const id of IDS) {
      const w = roh[id];
      if (w && zahlOk(w.preis)) out[id] = { preis: w.preis, gesetzt: typeof w.gesetzt === "string" ? w.gesetzt.slice(0, 40) : "" };
    }
    return out;
  }
  /* Spiegel für den Service Worker (der kein localStorage lesen kann) */
  function wunschSpiegeln(w) {
    try {
      if (window.caches) caches.open("kb-daten").then(c => c.put("wunsch.json",
        new Response(JSON.stringify(w), { headers: { "Content-Type": "application/json" } }))).catch(() => {});
    } catch (e) { /* ohne Cache-API kein Hintergrundabgleich */ }
  }

  /* ---------- preise.json ---------- */
  let preiseVersprechen = null;
  function ladePreise() {
    if (!preiseVersprechen) preiseVersprechen = fetch("preise.json", { cache: "no-store" })
      .then(r => (r.ok ? r.json() : null)).catch(() => null)
      .then(j => (j && typeof j === "object" && j.preise && typeof j.preise === "object" ? j : { preise: {}, lauf: null }));
    return preiseVersprechen;
  }

  /* ---------- Ersatz für window.claude.use ---------- */
  const beobachter = { wunsch: new Set() };
  const schnapp = obj => ({
    metadata: { fromCache: false },
    docs: Object.keys(obj).filter(id => IDS.indexOf(id) >= 0).map(id => ({ id, data: () => obj[id] }))
  });
  const fehlerDoc = code => Object.assign(new Error(code), { code });

  function sammlung(name) {
    return {
      onSnapshot(cb, fehl) {
        if (name === "wunsch") {
          beobachter.wunsch.add(cb);
          setTimeout(() => cb(schnapp(wunschAlle())), 0);
          return () => beobachter.wunsch.delete(cb);
        }
        if (name === "preise") {
          ladePreise().then(j => cb(schnapp(j.preise))).catch(e => fehl && fehl(e));
          return () => {};
        }
        setTimeout(() => cb(schnapp({})), 0);
        return () => {};
      }
    };
  }
  function dokument(pfad) {
    const teile = String(pfad).split("/");
    return {
      onSnapshot(cb, fehl) {
        if (pfad === "wecker/lauf") {
          ladePreise().then(j => {
            const l = j.lauf && typeof j.lauf === "object" ? j.lauf : null;
            cb({ exists: !!l, metadata: { fromCache: false }, data: () => l });
          }).catch(e => fehl && fehl(e));
        } else setTimeout(() => cb({ exists: false, metadata: { fromCache: false }, data: () => null }), 0);
        return () => {};
      },
      async get() { return { exists: false, data: () => null }; },
      async set(daten) {
        // preis: Zahl = setzen, null = löschen (leeres Feld im Preiswecker)
        if (teile.length === 2 && teile[0] === "wunsch" && IDS.indexOf(teile[1]) >= 0 && daten && (daten.preis === null || zahlOk(daten.preis))) {
          const roh0 = lsLies(LS_WUNSCH), roh = roh0 && typeof roh0 === "object" && !Array.isArray(roh0) ? roh0 : {};
          if (daten.preis === null) delete roh[teile[1]];
          else roh[teile[1]] = { preis: daten.preis, gesetzt: new Date().toISOString() };
          if (!lsSchreib(LS_WUNSCH, roh)) throw fehlerDoc("speicher-voll-oder-gesperrt");
          const alle = wunschAlle();
          wunschSpiegeln(alle);
          beobachter.wunsch.forEach(cb => { try { cb(schnapp(alle)); } catch (e) { console.error(e); } });
          setTimeout(zeigeTreffer, 0);
          return;
        }
        throw fehlerDoc("nur-auf-claude-ai");
      }
    };
  }
  const db = { collection: sammlung, doc: dokument };
  const user = { isOwner: async () => true, id: async () => null };
  if (!window.claude) {
    window.claude = { use: async name => (name === "db" ? db : name === "user" ? user : null), app: true };
  }

  /* ---------- Hinweiskarten (Treffer, neue Fassung) ---------- */
  let stapel = null;
  function stapelHolen() {
    if (!stapel) { stapel = document.createElement("div"); stapel.className = "kbapp-stapel"; document.body.appendChild(stapel); }
    return stapel;
  }
  function karte(id, art, titel, text, knoepfe) {
    let k = document.getElementById(id);
    if (k) k.remove();
    k = document.createElement("div");
    k.id = id; k.className = "kbapp-karte kbapp-" + art; k.setAttribute("role", art === "treffer" ? "alert" : "status");
    const t = document.createElement("p"); t.className = "kbapp-titel"; t.textContent = titel;
    const p = document.createElement("p"); p.className = "kbapp-text"; p.textContent = text;
    const reihe = document.createElement("div"); reihe.className = "kbapp-knoepfe";
    for (const kn of knoepfe) {
      const b = document.createElement("button"); b.type = "button"; b.textContent = kn.text;
      b.className = kn.haupt ? "kbapp-haupt" : "kbapp-neben";
      b.addEventListener("click", () => kn.tun(k));
      reihe.appendChild(b);
    }
    k.append(t, p, reihe);
    stapelHolen().appendChild(k);
    return k;
  }

  async function zeigeTreffer() {
    const j = await ladePreise();
    const w = wunschAlle(), liste = [], sig = [];
    for (const id of IDS) {
      const p = j.preise[id], g = p && p.aktuell && p.aktuell.gesamt;
      if (!w[id] || !zahlOk(g) || g > w[id].preis) continue;
      const name = p && typeof p.name === "string" ? p.name.slice(0, 40) : id;
      const h = p.aktuell && typeof p.aktuell.haendler === "string" ? " bei " + p.aktuell.haendler.slice(0, 40) : "";
      liste.push(name + " für " + eur(g) + h + " (Wunsch " + eur(w[id].preis) + ")");
      sig.push(id + ":" + g + ":" + w[id].preis);
    }
    const alt = document.getElementById("kbapp-treffer");
    if (!liste.length) { if (alt) alt.remove(); return; }
    const s = sig.join(",");
    if (lsLies(LS_AUS) === s) return;
    const z = j.lauf && typeof j.lauf.letzter === "string" ? /^(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2})/.exec(j.lauf.letzter) : null;
    const stand = z ? " Stand der Preise: " + z[3] + "." + z[2] + "." + z[1] + ", " + z[4] + " Uhr." : "";
    karte("kbapp-treffer", "treffer", liste.length === 1 ? "Wunschpreis erreicht" : liste.length + " Wunschpreise erreicht",
      liste.join("; ") + "." + stand, [
        { text: "Zum Preiswecker", haupt: true, tun: k => { k.remove(); zeigeWecker(); } },
        { text: "Ausblenden", tun: k => { lsSchreib(LS_AUS, s); k.remove(); } }
      ]);
  }
  function zeigeWecker() {
    const tabTv = document.getElementById("tab-tv");
    if (tabTv && tabTv.getAttribute("aria-selected") !== "true") tabTv.click();
    location.hash = "#preiswecker";
  }

  /* Hinweis im Preiswecker: wo die Wunschpreise liegen, Benachrichtigung als Versuch */
  function weckerErgaenzen() {
    const pw = document.getElementById("preiswecker");
    if (!pw || document.getElementById("kbapp-wecker")) return;
    const box = document.createElement("div"); box.id = "kbapp-wecker"; box.className = "kbapp-wecker small";
    const p = document.createElement("p");
    p.textContent = "In der App liegen Wunschpreise nur auf diesem Handy. Die Preise kommen aus der täglichen Abfrage (preise.json). " +
      "Ein Treffer erscheint beim Öffnen der App als Hinweis oben.";
    box.appendChild(p);
    const kannPush = "serviceWorker" in navigator && "Notification" in window && "PushManager" in window;
    if (kannPush) {
      const b = document.createElement("button"); b.type = "button"; b.className = "kbapp-neben";
      const zst = document.createElement("p"); zst.className = "kbapp-zst";
      const code = document.createElement("div"); code.className = "kbapp-code"; code.hidden = true;
      const zeichne = async () => {
        const abo = await pushAbo(false);
        b.hidden = Notification.permission === "denied";
        b.textContent = abo ? "Einrichtungscode zeigen" : "Push einrichten";
        zst.textContent = Notification.permission === "denied"
          ? "Benachrichtigungen sind für diese App gesperrt (Android-Einstellungen → Apps → Chrome bzw. Kaufberatung → Benachrichtigungen)."
          : abo ? "Dieses Handy ist für Push angemeldet. Meldungen kommen erst, wenn der Einrichtungscode als Secret PUSH_ABO auf GitHub " +
            "gespeichert ist (nach jeder Neuanmeldung erneuern); prüfen mit einem Testlauf (siehe Anleitung)."
          : "Push: Die tägliche Abfrage meldet neue Tiefstpreise direkt als Benachrichtigung der Kaufberatung (einmal einrichten).";
      };
      b.addEventListener("click", async () => {
        try { await Notification.requestPermission(); } catch (e) { /* abgelehnt */ }
        if (Notification.permission !== "granted") { await zeichne(); return; }
        const abo = await pushAbo(true);
        await hintergrundAnmelden();
        if (!abo) { zst.textContent = "Push-Anmeldung hat nicht geklappt (ohne Netz? Chrome aktuell?). Später erneut versuchen."; return; }
        codeZeigen(code, abo);
        await zeichne();
      });
      zeichne();
      box.append(b, zst, code);
    }
    const status = document.getElementById("pw-status");
    (status && status.parentNode === pw ? status : pw.lastElementChild).insertAdjacentElement("afterend", box);
  }

  /* ---------- Web Push (eigene Benachrichtigung, Sender: tägliche Abfrage auf GitHub) ----------
     Öffentlicher VAPID-Schlüssel des Absenders (darf öffentlich sein; der private liegt nur als GitHub-Secret VAPID_PRIVAT).
     Das Abo (Endpoint + Schlüssel) ist geheim: Nico legt es einmal als Secret PUSH_ABO an. */
  const VAPID_OEFFENTLICH = "BD8emN7S7iqJ8w_1uSQOa9CgYSjHtWg5_qa7O15NlD2HMnHoi8dRoKV3eNx8SVspWcJy5sOUh3uweolU3M9wZAc";
  const SECRET_SEITE = "https://github.com/nicosteinberg4791-ops/kaufberatung-app/settings/secrets/actions/new";
  function b64uBytes(s) {
    const b = atob(s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4));
    return Uint8Array.from(b, z => z.charCodeAt(0));
  }
  function gleicheBytes(a, b) {
    if (!a || !b || a.byteLength !== b.byteLength) return false;
    const x = new Uint8Array(a), y = new Uint8Array(b);
    for (let i = 0; i < x.length; i++) if (x[i] !== y[i]) return false;
    return true;
  }
  async function pushAbo(anlegen) {
    try {
      const reg = await navigator.serviceWorker.ready;
      const schluessel = b64uBytes(VAPID_OEFFENTLICH);
      let abo = await reg.pushManager.getSubscription();
      // Abo mit anderem Absenderschlüssel (Schlüssel gewechselt) ist nutzlos: abmelden und neu anlegen
      if (abo && abo.options && abo.options.applicationServerKey && !gleicheBytes(abo.options.applicationServerKey, schluessel.buffer)) {
        if (!anlegen) return null;
        await abo.unsubscribe(); abo = null;
      }
      if (!abo && anlegen) abo = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: schluessel });
      return abo;
    } catch (e) { return null; }
  }
  function codeZeigen(ziel, abo) {
    ziel.textContent = "";
    const text = JSON.stringify(abo.toJSON());
    const h = document.createElement("p");
    h.textContent = "Letzter Schritt (einmal): Code kopieren, auf GitHub als Secret mit dem Namen PUSH_ABO speichern. " +
      "Der Code ist geheim: nur dort einfügen, nicht teilen. Danach unter Actions → Preisabfrage → Run workflow mit Häkchen testen.";
    const feld = document.createElement("textarea"); feld.readOnly = true; feld.rows = 3; feld.value = text;
    feld.setAttribute("aria-label", "Einrichtungscode für das Secret PUSH_ABO");
    const reihe = document.createElement("div"); reihe.className = "kbapp-knoepfe";
    const kopie = document.createElement("button"); kopie.type = "button"; kopie.className = "kbapp-haupt"; kopie.textContent = "Code kopieren";
    kopie.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(text); kopie.textContent = "Kopiert"; }
      catch (e) { feld.focus(); feld.select(); kopie.textContent = "Bitte markierten Code kopieren"; }
    });
    const link = document.createElement("a"); link.href = SECRET_SEITE; link.target = "_blank"; link.rel = "noopener";
    link.className = "kbapp-neben"; link.textContent = "Secret auf GitHub anlegen";
    reihe.append(kopie, link);
    ziel.append(h, feld, reihe);
    ziel.hidden = false;
  }

  async function hintergrundAnmelden() {
    try {
      if (Notification.permission !== "granted") return;
      const reg = await navigator.serviceWorker.ready;
      if (!reg.periodicSync) return;
      const st = await navigator.permissions.query({ name: "periodic-background-sync" });
      if (st.state !== "granted") return;
      await reg.periodicSync.register("kb-preise", { minInterval: 12 * 60 * 60 * 1000 });
    } catch (e) { /* nicht verfügbar: es bleibt der Hinweis beim Öffnen */ }
  }

  /* ---------- Service Worker ---------- */
  function swAnmelden() {
    if (!("serviceWorker" in navigator)) return;
    let neuGeladen = false, gewuenscht = false;
    // Erste Übernahme (erster Besuch, clients.claim) ohne Neuladen; jeder spätere Wechsel der Fassung genau einmal neu laden,
    // auch wenn eine andere Registerkarte „Neu laden“ gewählt hat
    let gesteuert = !!navigator.serviceWorker.controller;
    navigator.serviceWorker.addEventListener("controllerchange", () => {
      if (!gesteuert && !gewuenscht) { gesteuert = true; return; }
      if (!neuGeladen) { neuGeladen = true; location.reload(); }
    });
    navigator.serviceWorker.register("sw.js").then(reg => {
      const melde = w => karte("kbapp-neu", "neu", "Neue Fassung bereit", "Die Kaufberatung wurde aktualisiert.", [
        { text: "Neu laden", haupt: true, tun: () => { gewuenscht = true; w.postMessage("jetzt"); } },
        { text: "Später", tun: k => k.remove() }
      ]);
      if (reg.waiting && navigator.serviceWorker.controller) melde(reg.waiting);
      reg.addEventListener("updatefound", () => {
        const w = reg.installing;
        if (w) w.addEventListener("statechange", () => { if (w.state === "installed" && navigator.serviceWorker.controller) melde(w); });
      });
      document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") reg.update().catch(() => {}); });
    }).catch(e => console.warn("Service Worker nicht angemeldet:", e && e.message));
  }

  function start() {
    wunschSpiegeln(wunschAlle());
    swAnmelden();
    weckerErgaenzen();
    zeigeTreffer();
    hintergrundAnmelden();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
  window.__kbApp = { wunschAlle, ladePreise, zeigeTreffer, weckerErgaenzen };
})();
