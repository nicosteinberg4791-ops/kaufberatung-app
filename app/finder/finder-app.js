/* App-Hülle der Startseite „Finden & Vergleichen“ (läuft vor finder.js).
   1. Alte Sprungmarken des Ratgebers (#preiswecker, #besitzer, #tv …) führen weiter auf ratgeber.html:
      Der Finder schreibt seinen Zustand immer als „#k=…&…“, also mit „=“. Alles ohne „=“ gehört dem Ratgeber.
   2. Service Worker anmelden, neue Fassung melden („Neu laden“), wie app.js im Ratgeber. */
(function () {
  "use strict";
  function zumRatgeber() {
    try {
      const h = String(location.hash || "");
      // #inhalt ist die eigene Sprungmarke der Seite („Zum Inhalt springen“)
      if (/^#[A-Za-z0-9_-]+$/.test(h) && h !== "#inhalt") { location.replace("ratgeber.html" + h); return true; }
    } catch (e) { /* ohne Adresse: Finder bleibt */ }
    return false;
  }
  if (zumRatgeber()) return;
  // Auch wenn nur der Hash in der offenen Seite wechselt (Link, Benachrichtigung auf dieselbe Seite)
  window.addEventListener("hashchange", zumRatgeber);

  function hinweis(w, setzeGewuenscht) {
    if (document.getElementById("app-neu")) return;
    const k = document.createElement("div");
    k.id = "app-neu"; k.className = "app-hinweis karte"; k.setAttribute("role", "status");
    const t = document.createElement("p"); t.className = "gross"; t.textContent = "Neue Fassung bereit";
    const reihe = document.createElement("div"); reihe.className = "app-hinweis-reihe";
    const ja = document.createElement("button"); ja.type = "button"; ja.className = "knopf haupt"; ja.textContent = "Neu laden";
    ja.addEventListener("click", () => { setzeGewuenscht(); w.postMessage("jetzt"); });
    const nein = document.createElement("button"); nein.type = "button"; nein.className = "knopf neben"; nein.textContent = "Später";
    nein.addEventListener("click", () => k.remove());
    reihe.append(ja, nein); k.append(t, reihe);
    document.body.appendChild(k);
  }

  function swAnmelden() {
    if (!("serviceWorker" in navigator)) return;
    let neuGeladen = false, gewuenscht = false;
    let gesteuert = !!navigator.serviceWorker.controller;
    navigator.serviceWorker.addEventListener("controllerchange", () => {
      if (!gesteuert && !gewuenscht) { gesteuert = true; return; }
      if (!neuGeladen) { neuGeladen = true; location.reload(); }
    });
    navigator.serviceWorker.register("sw.js").then(reg => {
      const melde = w => hinweis(w, () => { gewuenscht = true; });
      if (reg.waiting && navigator.serviceWorker.controller) melde(reg.waiting);
      reg.addEventListener("updatefound", () => {
        const w = reg.installing;
        if (w) w.addEventListener("statechange", () => { if (w.state === "installed" && navigator.serviceWorker.controller) melde(w); });
      });
      document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") reg.update().catch(() => {}); });
    }).catch(e => console.warn("Service Worker nicht angemeldet:", e && e.message));
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", swAnmelden); else swAnmelden();
})();
