# -*- coding: utf-8 -*-
"""Tests für werkzeuge/shopabfrage.py (Pilot Bestpreis-Mix, D7).

Vorlagen in tests/vorlagen/: gekürzte echte Seiten vom 21.11.2026 (nur JSON-LD ohne Texte/Bilder, bei Saturn dazu das
eingebettete Preisfeld). Kein Netzzugriff: lauf() bekommt eine Ersatzfunktion für den Abruf.
"""
import copy
import json
import os
import sys
import unittest

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(HIER)
sys.path.insert(0, os.path.join(WURZEL, "werkzeuge"))
import shopabfrage as s  # noqa: E402

VORLAGEN = os.path.join(HIER, "vorlagen")


def vorlage(name):
    with open(os.path.join(VORLAGEN, name), encoding="utf-8") as f:
        return f.read()


QUELLEN = {q["id"]: q for q in s.lade(s.QUELLEN)["quellen"]}
MODELLE = {m["id"]: m for m in s.lade(s.MODELLE)["modelle"]}


def seite(*objekte):
    return "".join('<script type="application/ld+json">%s</script>' % json.dumps(o) for o in objekte)


def produkt(ean="8806096835395", **offer):
    o = {"@type": "Offer", "price": "1599.00", "priceCurrency": "EUR", "availability": "https://schema.org/InStock",
         "itemCondition": "https://schema.org/NewCondition", "seller": {"@type": "Organization", "name": "ALTERNATE GmbH"}}
    o.update(offer)
    return {"@context": "https://schema.org", "@type": "Product", "gtin13": ean, "offers": o}


class Daten(unittest.TestCase):
    def test_daten_vollstaendig(self):
        self.assertEqual(s.pruefe_daten(list(QUELLEN.values()), list(MODELLE.values())), [])

    def test_fuenf_modelle_jedes_mit_freigegebener_quelle(self):
        self.assertEqual(len(MODELLE), 5)
        for m in MODELLE.values():
            self.assertTrue(any(QUELLEN[q]["automatisch"] for q in m["urls"]), m["id"])

    def test_freigabe_nur_mit_pruefung(self):
        for q in QUELLEN.values():
            p = q["pruefung"]
            for k in ("datum", "robots", "agb", "technik", "ergebnis"):
                self.assertTrue(p.get(k), f"{q['id']}: {k}")
            self.assertEqual(q["automatisch"], p["ergebnis"] == "freigegeben", q["id"])

    def test_gesperrte_quellen_nur_link(self):
        for qid in ("mediamarkt", "idealo"):
            self.assertFalse(QUELLEN[qid]["automatisch"], qid)

    def test_heise_freigabe_mit_besitzerentscheid(self):
        self.assertTrue(QUELLEN["heise"]["automatisch"])
        self.assertIn("Besitzer 21.11.2026", QUELLEN["heise"]["pruefung"]["entscheidung"])

    def test_feste_urls_ohne_query_bei_freigegebenen_quellen(self):
        for m in MODELLE.values():
            for qid, url in m["urls"].items():
                if QUELLEN[qid]["automatisch"]:
                    self.assertNotIn("?", url, f"{m['id']} {qid}")
                    self.assertIn(QUELLEN[qid]["domain"], url)


class Vorlagen(unittest.TestCase):
    def test_alternate_lg_mit_versand(self):
        g, _ = s.auswerten_seite(vorlage("alternate_lg65.html"), MODELLE["lg_c6elb_65"], QUELLEN["alternate"], "L", "Z")
        self.assertEqual(len(g), 1)
        a = g[0]
        self.assertEqual((a["preis"], a["versand"], a["gesamt"], a["versand_herkunft"]), (1599.0, 69.99, 1668.99, "json-ld"))
        self.assertEqual((a["haendler"], a["quelle"], a["link"], a["zeit"]), ("Alternate", "eigen", "L", "Z"))

    def test_proshop_ninja_ean_mit_fuehrender_null(self):
        g, _ = s.auswerten_seite(vorlage("proshop_ninja.html"), MODELLE["af_ninja_af500"], QUELLEN["proshop"], "L", "Z")
        self.assertEqual([(a["preis"], a["versand"]) for a in g], [(174.05, 4.99)])

    def test_proshop_versand_punkt_null(self):
        # D7-08: Vorlage nennt Versand nach DE als ".00" EUR
        g, _ = s.auswerten_seite(vorlage("proshop_s26.html"), MODELLE["phone_s26_ultra_256"], QUELLEN["proshop"], "L", "Z")
        self.assertEqual(len(g), 1)
        self.assertEqual((g[0]["versand"], g[0]["versand_herkunft"], g[0]["gesamt"]), (0.0, "json-ld", 969.0))

    def test_vorlagen_ohne_konto_pfade_und_zusatzangebote(self):
        # D7-09: nur Felder, die die Tests brauchen; keine Konto-URLs, keine Service-/Garantietexte
        for name in os.listdir(VORLAGEN):
            t = vorlage(name)
            for verboten in ("myaccount", "loyalty", '"addOn"', "Garantie", "MerchantReturnPolicy", "BreadcrumbList", "Media Markt"):
                self.assertNotIn(verboten, t, f"{name}: {verboten}")

    def test_saturn_produktgruppe_nur_passende_ean_und_eigenes_angebot(self):
        g, prot = s.auswerten_seite(vorlage("saturn_s90h.html"), MODELLE["sam_s90h_65"], QUELLEN["saturn"], "L", "Z")
        self.assertEqual([(a["preis"], a["versand"], a["versand_herkunft"]) for a in g], [(1399.0, 0.0, "seitenzustand")])
        self.assertTrue(any(p["grund"].startswith("EAN passt nicht") for p in prot))

    def test_saturn_marktplatz_wird_verworfen(self):
        g, prot = s.auswerten_seite(vorlage("saturn_s26.html"), MODELLE["phone_s26_ultra_256"], QUELLEN["saturn"], "L", "Z")
        self.assertEqual(g, [])
        self.assertIn("Marktplatzangebot (Seitenzustand)", [p["grund"] for p in prot])

    def test_saturn_ninja(self):
        g, _ = s.auswerten_seite(vorlage("saturn_ninja.html"), MODELLE["af_ninja_af500"], QUELLEN["saturn"], "L", "Z")
        self.assertEqual([a["gesamt"] for a in g], [219.99])

    def test_saturn_ohne_preisfeld_kein_verkaeufernachweis(self):
        text = vorlage("saturn_ninja.html").split("<script>window.__PRELOADED_STATE__")[0]
        g, prot = s.auswerten_seite(text, MODELLE["af_ninja_af500"], QUELLEN["saturn"], "L", "Z")
        self.assertEqual(g, [])
        self.assertIn("Verkäufer fehlt oder nicht belegt", [p["grund"] for p in prot])

    def test_saturn_preisfeld_mit_anderem_preis(self):
        text = vorlage("saturn_ninja.html").replace('"amount": 219.99', '"amount": 199.99').replace(
            '\\"amount\\":219.99', '\\"amount\\":199.99')
        g, prot = s.auswerten_seite(text, MODELLE["af_ninja_af500"], QUELLEN["saturn"], "L", "Z")
        self.assertEqual(g, [])
        self.assertTrue(any("passt nicht zum JSON-LD" in p["grund"] for p in prot), prot)

    def test_saturn_preisfeld_nicht_aus_folgeobjekt(self):
        # D7-04: SKU-Objekt ohne Preis darf den Preis des folgenden Objekts (andere SKU, Marktplatz) nicht übernehmen
        p = produkt(ean="0622356270373", price="219.99")
        del p["offers"]["seller"]
        p["sku"] = "111"
        zustand = ('{"id":"Saturn:de:111","currency":"EUR","isProductOfTypeMarketplace":false,"price":null,'
                   '"productGroupId":1}, {"id":"Saturn:de:222","currency":"EUR","isProductOfTypeMarketplace":true,'
                   '"price":{"__typename":"CofrPriceFeaturePrice","amount":219.99,"shippingCost":0}}')
        text = seite(p) + zustand_skript('{"artikel":[%s]}' % zustand)
        g, prot = s.auswerten_seite(text, MODELLE["af_ninja_af500"], QUELLEN["saturn"], "L", "Z")
        self.assertEqual(g, [], prot)


class Regeln(unittest.TestCase):
    m = MODELLE["lg_c6elb_65"]
    q = QUELLEN["alternate"]

    def gruende(self, *objekte):
        g, prot = s.auswerten_seite(seite(*objekte), self.m, self.q, "L", "Z")
        return g, [p["grund"] for p in prot]

    def test_gueltig(self):
        g, _ = self.gruende(produkt())
        self.assertEqual(len(g), 1)
        self.assertIsNone(g[0]["versand"])

    def test_gebraucht_verworfen(self):
        g, gr = self.gruende(produkt(itemCondition="https://schema.org/RefurbishedCondition"))
        self.assertEqual((g, gr), ([], ["Zustand RefurbishedCondition"]))

    def test_zustand_fehlt_gilt_neu(self):
        p = produkt()
        del p["offers"]["itemCondition"]
        self.assertEqual(len(self.gruende(p)[0]), 1)

    def test_nicht_lieferbar(self):
        g, gr = self.gruende(produkt(availability="https://schema.org/OutOfStock"))
        self.assertEqual(g, [])
        self.assertTrue(gr[0].startswith("nicht lieferbar"))

    def test_marktplatzhaendler(self):
        g, gr = self.gruende(produkt(seller={"name": "JB-Vertrieb-GmbH"}))
        self.assertEqual(g, [])
        self.assertIn("Marktplatz", gr[0])

    def test_verkaeufer_fehlt(self):
        p = produkt()
        del p["offers"]["seller"]
        self.assertEqual(self.gruende(p)[1], ["Verkäufer fehlt oder nicht belegt"])

    def test_falsche_ean(self):
        g, gr = self.gruende(produkt(ean="4006381333931"))
        self.assertEqual(g, [])
        self.assertTrue(gr[0].startswith("EAN passt nicht"))

    def test_waehrung_und_korridor(self):
        self.assertEqual(self.gruende(produkt(priceCurrency="CHF"))[1], ["Währung CHF"])
        self.assertIn("Korridor", self.gruende(produkt(price="29.99"))[1][0])

    def test_kein_product(self):
        self.assertEqual(self.gruende({"@type": "BreadcrumbList"})[1], ["kein Product im JSON-LD"])

    def test_graph_aggregateoffer_und_typliste(self):
        p = produkt()
        inner = p.pop("offers")
        p["@type"] = ["Product", "Thing"]
        p["offers"] = {"@type": "AggregateOffer", "offers": [inner, dict(inner, price="1499,00")]}
        g, _ = self.gruende({"@graph": [{"@type": "WebPage"}, p]})
        self.assertEqual(sorted(a["preis"] for a in g), [1499.0, 1599.0])

    def test_versand_nur_fuer_deutschland(self):
        sd = [{"@type": "OfferShippingDetails", "shippingRate": {"value": 9.9, "currency": "EUR"},
               "shippingDestination": {"addressCountry": "AT"}},
              {"@type": "OfferShippingDetails", "shippingRate": {"value": "19.90", "currency": "EUR"},
               "shippingDestination": [{"addressCountry": "DE"}]}]
        g, _ = self.gruende(produkt(shippingDetails=sd))
        self.assertEqual(g[0]["versand"], 19.9)

    def test_versand_mehrdeutig_bleibt_unbekannt(self):
        sd = [{"shippingRate": {"value": 0, "currency": "EUR"}}, {"shippingRate": {"value": 69.99, "currency": "EUR"}}]
        g, _ = self.gruende(produkt(shippingDetails=sd))
        self.assertIsNone(g[0]["versand"])

    def test_streichpreis_in_pricespecification(self):
        p = produkt()
        del p["offers"]["price"]
        p["offers"]["priceSpecification"] = [{"priceType": "https://schema.org/ListPrice", "price": 3199},
                                             {"price": 1599, "priceCurrency": "EUR"}]
        self.assertEqual(self.gruende(p)[0][0]["preis"], 1599.0)

    def test_versandregel_mit_beleg(self):
        q = dict(self.q, versandregel={"frei_ab": 1000, "sonst": 5.99, "beleg": "Beispiel"})
        g, _ = s.auswerten_seite(seite(produkt()), self.m, q, "L", "Z")
        self.assertEqual((g[0]["versand"], g[0]["versand_herkunft"]), (0.0, "shopregel"))
        q["versandregel"] = {"frei_ab": 1000, "sonst": 5.99}  # ohne Beleg: nicht verwenden
        g, _ = s.auswerten_seite(seite(produkt()), self.m, q, "L", "Z")
        self.assertEqual(g[0]["versand_herkunft"], "unbekannt")

    def test_unlesbarer_block_und_kommentar(self):
        text = '<script type="application/ld+json">{kaputt</script>' \
               '<script type="application/ld+json"><!-- %s --></script>' % json.dumps(produkt())
        self.assertEqual(len(s.jsonld_bloecke(text)), 1)

    def test_zahlen(self):
        self.assertEqual([s.zahl(x) for x in (1599, "1599.00", "1.599,00", "219,99", "€ 9", True, "abc", ".00", ".5")],
                         [1599.0, 1599.0, 1599.0, 219.99, 9.0, None, None, 0.0, 0.5])

    def test_ean_normalisierung(self):
        self.assertEqual(s.norm_ean("0622356270373"), s.norm_ean("622356270373"))
        self.assertEqual(s.norm_ean("12345"), "")


class Bestpreis(unittest.TestCase):
    def a(self, quelle, haendler, preis, versand):
        return {"quelle": quelle, "haendler": haendler, "preis": preis, "versand": versand,
                "gesamt": None if versand is None else round(preis + versand, 2)}

    def test_gesamtpreis_entscheidet(self):
        best, hinweis, _ = s.bestpreis([self.a("eigen", "Alternate", 1599, 69.99), self.a("eigen", "Saturn", 1649, 0)])
        self.assertEqual(best["haendler"], "Saturn")
        self.assertIsNone(hinweis)

    def test_ohne_versand_nur_hinweis(self):
        best, hinweis, _ = s.bestpreis([self.a("eigen", "Saturn", 1000, 0), self.a("eigen", "Proshop", 969, None)])
        self.assertEqual((best["haendler"], hinweis["haendler"]), ("Saturn", "Proshop"))

    def test_nur_ohne_versand(self):
        best, _, _ = s.bestpreis([self.a("eigen", "Proshop", 969, None)])
        self.assertEqual(best["preis"], 969)

    def test_dublette_eigen_vor_heise(self):
        best, _, alle = s.bestpreis([self.a("heise", "ALTERNATE", 1599, 69.99), self.a("eigen", "Alternate", 1599, 69.99)])
        self.assertEqual(len(alle), 1)
        self.assertEqual(best["quelle"], "eigen")

    def test_leer(self):
        self.assertEqual(s.bestpreis([])[:2], (None, None))

    def test_dublette_nur_bei_gleichem_haendler(self):
        # D7-07: gleicher Wortanfang ist kein gleicher Händler
        _, _, alle = s.bestpreis([self.a("heise", "Elektronik Nord", 500, 0), self.a("heise", "Elektronik Sued", 500, 0)])
        self.assertEqual(len(alle), 2)

    def test_dublette_behaelt_belegten_guenstigeren_gesamtpreis(self):
        # D7-07: zwei direkte Alternate-Treffer zu 1.599 €: der mit kostenlosem Versand bleibt, nicht der zuerst gelieferte
        best, _, alle = s.bestpreis([self.a("eigen", "Alternate", 1599, 69.99), self.a("eigen", "Alternate", 1599, 0)])
        self.assertEqual((len(alle), best["gesamt"]), (1, 1599))

    def test_alias_aus_quellen(self):
        aliase = s.haendler_aliase(list(QUELLEN.values()))
        _, _, alle = s.bestpreis([self.a("heise", "proshop.de", 969, 0), self.a("eigen", "Proshop", 969, 0)], aliase)
        self.assertEqual([a["quelle"] for a in alle], ["eigen"])


class Lauf(unittest.TestCase):
    ROBOTS = {"preisvergleich.heise.de": "User-agent: *\nDisallow: /redir/\n",
              "www.saturn.de": "User-Agent: *\nDisallow: /de/search\n",
              "www.alternate.de": "User-agent: *\nDisallow: /rest/\n",
              "www.proshop.de": "User-agent: *\nDisallow: /Basket/\n"}
    SEITEN = {"alternate": "alternate_lg65.html", "saturn": "saturn_s90h.html", "proshop": "proshop_ninja.html"}

    def holen_fabrik(self, gesperrt=()):
        aufrufe = []

        def holen(url):
            aufrufe.append(url)
            host = url.split("/")[2]
            if host in gesperrt:
                raise s.NichtAbrufbar("HTTP 403")
            if url.endswith("/robots.txt"):
                return self.ROBOTS[host]
            if host == "preisvergleich.heise.de":
                return '<script>var x = {"offers": [{"raw_price": 9999.0, "merchant_name": "Teuer"}]};</script>'
            qid = {"www.saturn.de": "saturn", "www.alternate.de": "alternate", "www.proshop.de": "proshop"}[host]
            return vorlage(self.SEITEN[qid])
        return holen, aufrufe

    def modelle(self):
        return [MODELLE["lg_c6elb_65"], MODELLE["sam_s90h_65"], MODELLE["af_ninja_af500"]]

    def test_lauf_ohne_netz(self):
        holen, aufrufe = self.holen_fabrik()
        erg = s.lauf(list(QUELLEN.values()), self.modelle(), holen=holen, pause=0, jetzt="2026-11-21T06:00:00+00:00")
        m = erg["modelle"]
        self.assertEqual(m["lg_c6elb_65"]["bestpreis"]["gesamt"], 1668.99)
        self.assertEqual(m["sam_s90h_65"]["bestpreis"]["gesamt"], 1399.0)
        self.assertEqual(m["af_ninja_af500"]["bestpreis"]["haendler"], "Proshop")
        self.assertEqual(m["lg_c6elb_65"]["quellen"]["idealo"]["status"], "nur Link")
        self.assertEqual(m["lg_c6elb_65"]["quellen"]["heise"]["status"], "kein gültiges Angebot")  # 9999 € > Korridor
        # keine nicht freigegebene Quelle abgerufen, robots.txt je Quelle einmal
        self.assertFalse([u for u in aufrufe if "idealo" in u or "mediamarkt" in u])
        self.assertEqual(sum(u.endswith("robots.txt") for u in aufrufe), 4)
        self.assertEqual(erg["stand"], "2026-11-21T06:00:00+00:00")

    def test_sperre_gilt_fuer_ganzen_lauf(self):
        holen, aufrufe = self.holen_fabrik(gesperrt=("www.saturn.de",))
        erg = s.lauf(list(QUELLEN.values()), self.modelle(), holen=holen, pause=0)
        st = erg["modelle"]["af_ninja_af500"]["quellen"]["saturn"]["status"]
        self.assertTrue(st.startswith("nicht abrufbar"), st)
        self.assertEqual(sum("saturn" in u for u in aufrufe), 1)  # nur der robots-Versuch, kein weiterer Abruf

    def test_robots_verbietet(self):
        holen, aufrufe = self.holen_fabrik()
        self.ROBOTS = dict(self.ROBOTS, **{"www.alternate.de": "User-agent: *\nDisallow: /LG/\n"})
        erg = s.lauf(list(QUELLEN.values()), [MODELLE["lg_c6elb_65"]], holen=holen, pause=0)
        self.assertEqual(erg["modelle"]["lg_c6elb_65"]["quellen"]["alternate"]["status"],
                         "nicht abgefragt: robots.txt verbietet die URL")
        self.assertFalse([u for u in aufrufe if "/html/product/" in u])

    def test_weiterleitung_nicht_auswerten_quelle_bleibt_offen(self):
        holen, aufrufe = self.holen_fabrik()

        def mit_umleitung(url):
            if "/html/product/100198061" in url:
                raise s.Weitergeleitet("Weiterleitung auf https://andere.example/")
            return holen(url)
        erg = s.lauf(list(QUELLEN.values()), [MODELLE["lg_c6elb_65"], MODELLE["phone_s26_ultra_256"]],
                     holen=mit_umleitung, pause=0)
        self.assertTrue(erg["modelle"]["lg_c6elb_65"]["quellen"]["alternate"]["status"].startswith("nicht ausgewertet"))
        self.assertNotIn("alternate", erg["quellen_status"])  # nächste Alternate-URL wird weiter abgefragt
        self.assertIn("100191446", " ".join(aufrufe))

    def test_robots_regel_fuer_eigenen_namen(self):
        rp = s.urllib.robotparser.RobotFileParser()
        rp.parse(["User-agent: Kaufberatung-Preispilot", "Disallow: /", "", "User-agent: *", "Disallow:"])
        self.assertFalse(s.url_erlaubt("https://www.proshop.de/a/1", QUELLEN["proshop"], rp)[0])

    def test_challenge_erkennung(self):
        robots_saturn = "User-Agent: *\nDisallow: /cdn-cgi/bm/cv/\nDisallow: /cdn-cgi/challenge-platform/\n"
        self.assertFalse(s.ist_challenge(robots_saturn, "text/plain"))  # Livelauf 21.11.2026: Fehlalarm
        sperre = "<html><script src='/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1'></script></html>"
        self.assertTrue(s.ist_challenge(sperre, "text/html; charset=UTF-8"))
        # D7-03: aktive Challenge und eindeutige Sperrtexte sperren auch mit JSON-LD
        self.assertTrue(s.ist_challenge(sperre + seite(produkt()), "text/html"))
        self.assertTrue(s.ist_challenge("<h1>Access Denied</h1>" + seite(produkt()), "text/html"))
        # passiver Cloudflare-Skriptverweis auf normaler Produktseite mit JSON-LD: keine Sperre
        passiv = "<script src='/cdn-cgi/challenge-platform/scripts/jsd/main.js'></script>"
        self.assertFalse(s.ist_challenge(passiv + seite(produkt()), "text/html"))
        self.assertTrue(s.ist_challenge(passiv, "text/html"))

    def test_robots_html_oder_fliesstext_nicht_lesbar(self):
        # D7-02: HTML-Wartungsseite mit HTTP 200 ist keine robots.txt
        for text in ("<!doctype html><html><body>Wartung, bitte spaeter</body></html>",
                     "Wir sind gleich wieder da.\nDanke fuer Ihre Geduld.", "", "Disallow: /x\n"):
            rp = s.robots_fuer(QUELLEN["proshop"], holen=lambda url, t=text: t)
            self.assertIsInstance(rp, str, repr(text))
            self.assertIn("nicht lesbar", rp)
        rp = s.robots_fuer(QUELLEN["proshop"], holen=lambda url: "# Kommentar\nUser-agent: *\nDisallow: /Basket/\n"
                                                                  "Sitemap: https://www.proshop.de/sitemap.xml\n")
        self.assertNotIsInstance(rp, str)

    def test_keine_weiterleitung_kein_zweiter_abruf(self):
        # D7-01: 3xx wird nicht verfolgt; das Ziel wird nie angefragt
        import http.server
        import threading
        pfade = []

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                pfade.append(self.path)
                if self.path == "/start":
                    self.send_response(302)
                    self.send_header("Location", "/ziel")
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html>Ziel</html>")

            def log_message(self, *a):
                pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            alt = os.environ.pop("NO_PROXY", None), os.environ.get("no_proxy")
            os.environ["no_proxy"] = "127.0.0.1"
            with self.assertRaises(s.Weitergeleitet):
                s.abrufen("http://127.0.0.1:%d/start" % srv.server_address[1])
        finally:
            srv.shutdown()
            srv.server_close()
            if alt[0] is not None:
                os.environ["NO_PROXY"] = alt[0]
            if alt[1] is None:
                os.environ.pop("no_proxy", None)
            else:
                os.environ["no_proxy"] = alt[1]
        self.assertEqual(pfade, ["/start"])

    def test_heise_alle_kandidaten_auswahl_nach_dubletten(self):
        # D7-06: heise Alternate 1.500 € frei, Shop B 1.550 € frei; direkt Alternate 1.500 € + 50 € Versand.
        # Nach Dublettenbereinigung (eigen vor heise) muss Shop B mit 1.550 € gewinnen, nicht Alternate mit 1.550 €+.
        heise_seite = '<script>var x = {"offers": [' \
                      '{"raw_price": 1500.0, "merchant_name": "ALTERNATE", "merchant_free_shipping": true}, ' \
                      '{"raw_price": 1540.0, "merchant_name": "Shop B", "merchant_free_shipping": true}]};</script>'
        sd = {"shippingRate": {"value": 50, "currency": "EUR"}, "shippingDestination": {"addressCountry": "DE"}}
        alternate_seite = seite(produkt(price="1500.00", shippingDetails=sd))

        def holen(url):
            if url.endswith("robots.txt"):
                return "User-agent: *\nDisallow: /redir/\n"
            return heise_seite if "heise" in url else alternate_seite
        quellen = [q for q in QUELLEN.values() if q["id"] in ("alternate", "heise", "idealo", "mediamarkt")]
        erg = s.lauf(quellen, [MODELLE["lg_c6elb_65"]], holen=holen, pause=0)
        m = erg["modelle"]["lg_c6elb_65"]
        self.assertEqual(len(m["quellen"]["heise"]["angebote"]), 2)
        self.assertEqual((m["bestpreis"]["haendler"], m["bestpreis"]["gesamt"]), ("Shop B", 1540.0))

    def test_url_pruefung(self):
        q = QUELLEN["proshop"]
        rp = s.urllib.robotparser.RobotFileParser()
        rp.parse(["User-agent: *", "Disallow:"])
        self.assertFalse(s.url_erlaubt("https://www.proshop.de/x?s=1", q, rp)[0])
        self.assertFalse(s.url_erlaubt("https://www.proshop.de/Basket/x", q, rp)[0])
        self.assertFalse(s.url_erlaubt("https://evil.example/x", q, rp)[0])
        self.assertFalse(s.url_erlaubt("http://www.proshop.de/x", q, rp)[0])
        self.assertTrue(s.url_erlaubt("https://www.proshop.de/Heissluftfritteusen/x/1", q, rp)[0])

    def test_heise_bei_freigabe_ueber_preiswecker(self):
        heise_seite = '<script>var x = {"offers": [{"raw_price": 179.0, "merchant_name": "Shop A", ' \
                      '"merchant_free_shipping": true}, {"raw_price": 20.0, "merchant_name": "Zubehoer"}]};</script>'
        quellen = copy.deepcopy(list(QUELLEN.values()))
        for q in quellen:
            q["automatisch"] = q["id"] == "heise"
            q["pruefung"]["ergebnis"] = "freigegeben" if q["automatisch"] else q["pruefung"]["ergebnis"]

        def holen(url):
            return "User-agent: *\nDisallow: /redir/\n" if url.endswith("robots.txt") else heise_seite
        erg = s.lauf(quellen, [MODELLE["af_ninja_af500"]], holen=holen, pause=0)
        b = erg["modelle"]["af_ninja_af500"]["bestpreis"]
        self.assertEqual((b["quelle"], b["haendler"], b["gesamt"]), ("heise", "Shop A", 179.0))
        self.assertTrue(b["link"].startswith("https://preisvergleich.heise.de/"))
        self.assertNotIn("/redir/", b["link"])


def saturn_text(zustand_objekte, preis="219.99", sku="111"):
    p = produkt(ean="0622356270373", price=preis)
    del p["offers"]["seller"]
    p["sku"] = sku
    z = json.dumps({"artikel": zustand_objekte}, separators=(",", ":"))
    return seite(p) + zustand_skript(z)


def zustand_skript(roh):
    """Seitenzustand wie auf der echten Saturn-Seite: JavaScript-Objektliteral in window.__PRELOADED_STATE__."""
    return "<script>window.__PRELOADED_STATE__ = %s;</script>" % roh


class Runde2(unittest.TestCase):
    """Regressionstests zur Codex-Nachprüfung r2 (21.11.2026)."""
    m = MODELLE["af_ninja_af500"]

    def saturn(self, objekte, **kw):
        return s.auswerten_seite(saturn_text(objekte, **kw), self.m, QUELLEN["saturn"], "L", "Z")

    def obj(self, sku="111", mp=False, amount=219.99, versand=0, erst_typename=False):
        o = {"id": "Saturn:de:" + sku, "currency": "EUR", "isProductOfTypeMarketplace": mp,
             "price": {"__typename": "CofrPriceFeaturePrice", "amount": amount, "shippingCost": versand}}
        return dict({"__typename": "CofrPriceFeature"}, **o) if erst_typename else o

    def test_saturn_gueltig_mit_vollstaendigem_objekt(self):
        g, prot = self.saturn([self.obj()])
        self.assertEqual([(a["preis"], a["versand"], a["versand_herkunft"]) for a in g], [(219.99, 0.0, "seitenzustand")], prot)
        # echte Saturn-Seite 21.11.2026: das Preisobjekt beginnt mit __typename, id folgt danach
        g, prot = self.saturn([{"id": "Saturn:de:111", "price": {"installment": None}}, self.obj(erst_typename=True)])
        self.assertEqual([a["gesamt"] for a in g], [219.99], prot)

    def test_d7_10_negativer_versand_und_nan(self):
        g, _ = self.saturn([self.obj(versand=-500)])
        self.assertTrue(all(a["gesamt"] is None or a["gesamt"] >= a["preis"] for a in g), g)
        z = saturn_text([self.obj()]).replace("219.99,", "NaN,", 1)  # amount im Seitenzustand
        self.assertIn("NaN", z)
        g, _ = s.auswerten_seite(z, self.m, QUELLEN["saturn"], "L", "Z")
        self.assertEqual(g, [])
        self.assertFalse(s.betrag_ok(float("nan")))
        self.assertFalse(s.betrag_ok(-1.0))

    def test_d7_04_folgeobjekt_mit_anderer_feldreihenfolge(self):
        ohne_preis = {"id": "Saturn:de:111", "currency": "EUR", "isProductOfTypeMarketplace": False, "price": None}
        g, _ = self.saturn([ohne_preis, self.obj(sku="222", mp=True, erst_typename=True)])
        self.assertEqual(g, [])

    def test_d7_11_sperrtext_spaet_oder_als_text_plain(self):
        self.assertTrue(s.ist_challenge("<h1>Access Denied</h1>", "text/plain"))
        self.assertTrue(s.ist_challenge("x" * 30000 + "<h1>Access Denied</h1>" + seite(produkt()), "text/html"))
        robots_saturn = "User-Agent: *\nDisallow: /cdn-cgi/challenge-platform/\n"
        self.assertFalse(s.ist_challenge(robots_saturn, "text/plain"))

    def test_d7_12_automatisch_nur_echtes_true(self):
        quellen = copy.deepcopy(list(QUELLEN.values()))
        for q in quellen:
            if q["id"] == "mediamarkt":
                q["automatisch"] = "false"
        self.assertTrue(any("true oder false" in f for f in s.pruefe_daten(quellen, list(MODELLE.values()))))
        aufrufe = []
        erg = s.lauf(quellen, [MODELLE["lg_c6elb_65"]], holen=lambda u: aufrufe.append(u) or "User-agent: *\n", pause=0)
        self.assertFalse([u for u in aufrufe if "mediamarkt" in u])
        self.assertEqual(erg["modelle"]["lg_c6elb_65"]["quellen"]["mediamarkt"]["status"], "nur Link")

    def test_d7_07_aehnliche_namen_ohne_alias_getrennt(self):
        a = lambda h, v: {"quelle": "heise", "haendler": h, "preis": 969, "versand": v, "gesamt": 969 + v}
        best, _, alle = s.bestpreis([a("Proshop", 50), a("Pro-Shop", 0)])
        self.assertEqual((len(alle), best["gesamt"]), (2, 969))

    def test_d7_02_teilantwort_und_lesegrenze(self):
        import http.server
        import threading

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = b"User-agent: *\nDisallow: " if self.path == "/teil" else b"User-agent: *\n" + b"#" * 200
                self.send_response(206 if self.path == "/teil" else 200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        basis = "http://127.0.0.1:%d" % srv.server_address[1]
        alt_grenze, alt_proxy = s.MAX_BYTES, os.environ.get("no_proxy")
        os.environ["no_proxy"] = "127.0.0.1"
        try:
            with self.assertRaises(s.NichtAbrufbar):
                s.abrufen(basis + "/teil")
            s.MAX_BYTES = 100
            with self.assertRaises(s.NichtAbrufbar):
                s.abrufen(basis + "/gross")
            s.MAX_BYTES = alt_grenze
            self.assertTrue(s.abrufen(basis + "/gross").startswith("User-agent"))
        finally:
            s.MAX_BYTES = alt_grenze
            srv.shutdown()
            srv.server_close()
            if alt_proxy is None:
                os.environ.pop("no_proxy", None)
            else:
                os.environ["no_proxy"] = alt_proxy


class Runde3(unittest.TestCase):
    """Regressionstests zur Codex-Nachprüfung r3 (21.11.2026)."""
    m = MODELLE["af_ninja_af500"]

    def test_d7_14_doppelter_marktplatzschluessel_kein_nachweis(self):
        roh = ('{"id":"Saturn:de:111","currency":"EUR","isProductOfTypeMarketplace":true,'
               '"isProductOfTypeMarketplace":false,'
               '"price":{"__typename":"CofrPriceFeaturePrice","amount":219.99,"shippingCost":0}}')
        p = produkt(ean="0622356270373", price="219.99")
        del p["offers"]["seller"]
        p["sku"] = "111"
        text = seite(p) + zustand_skript('{"artikel":[%s]}' % roh)
        self.assertIsNone(s.mms_preisfeld(text, "Saturn:de:", "111"))
        g, prot = s.auswerten_seite(text, self.m, QUELLEN["saturn"], "L", "Z")
        self.assertEqual(g, [], prot)
        # Gegenprobe: ohne Dublette bleibt das Eigenangebot gültig
        ok = roh.replace('"isProductOfTypeMarketplace":true,', "", 1)
        text = seite(p) + zustand_skript('{"artikel":[%s]}' % ok)
        self.assertEqual(s.mms_preisfeld(text, "Saturn:de:", "111"), (False, 219.99, 0.0))

    def test_d7_11_captcha_aufforderung_und_robots_pfad(self):
        for sperr in ("Please complete the CAPTCHA to continue.", "Bitte bestätigen Sie, dass Sie kein Roboter sind.",
                      "I'm not a robot", "Verify you are human"):
            self.assertTrue(s.ist_challenge(sperr, "text/plain"), sperr)
            self.assertTrue(s.ist_challenge("x" * 30000 + "<h1>%s</h1>" % sperr + seite(produkt()), "text/html"), sperr)
        robots = ("User-agent: *\nDisallow: /cdn-cgi/challenge-platform/h/b/orchestrate/\n"
                  "Disallow: /cdn-cgi/chl_page\nAllow: /\n")
        self.assertFalse(s.ist_challenge(robots, "text/plain"))
        self.assertFalse(s.ist_challenge(seite(produkt()) + '<form><div class="g-recaptcha"></div></form>', "text/html"))

    def test_d7_02_gekuerzte_200_antwort(self):
        import http.server
        import socket
        import threading

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                voll = b"User-agent: *\nDisallow: /de/product/\n"
                body = voll[:24] if self.path == "/kurz" else voll
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                if self.path.startswith("/chunk"):
                    self.send_header("Transfer-Encoding", "chunked")
                    self.end_headers()
                    kopf = b"%x\r\n" % len(voll)
                    self.wfile.write({"/chunk": kopf + voll[:10],  # Chunk endet vorzeitig
                                      "/chunk0": kopf + voll + b"\r\n0",  # D7-02 r4: Ende nach "0"
                                      "/chunk0crlf": kopf + voll + b"\r\n0\r\n",  # ohne Leerzeile
                                      "/chunkok": kopf + voll + b"\r\n0\r\n\r\n"}[self.path])
                else:
                    self.send_header("Content-Length", str(len(voll)))
                    self.end_headers()
                    self.wfile.write(body)
                self.wfile.flush()
                self.connection.shutdown(socket.SHUT_WR)
                self.close_connection = True

            def log_message(self, *a):
                pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        basis = "http://127.0.0.1:%d" % srv.server_address[1]
        alt_proxy = os.environ.get("no_proxy")
        os.environ["no_proxy"] = "127.0.0.1"
        try:
            for pfad in ("/kurz", "/chunk", "/chunk0", "/chunk0crlf"):
                with self.assertRaises(s.NichtAbrufbar, msg=pfad):
                    s.abrufen(basis + pfad)
            self.assertIn("Disallow: /de/product/", s.abrufen(basis + "/voll"))
            self.assertIn("Disallow: /de/product/", s.abrufen(basis + "/chunkok"))
            r = s.robots_fuer({"domain": "x"}, holen=lambda u: s.abrufen(basis + "/kurz"))
            self.assertIsInstance(r, str)  # nicht lesbar -> Quelle nicht abfragen
        finally:
            srv.shutdown()
            srv.server_close()
            if alt_proxy is None:
                os.environ.pop("no_proxy", None)
            else:
                os.environ["no_proxy"] = alt_proxy


class Runde4(unittest.TestCase):
    """Regressionstests zur Codex-Nachprüfung r4 (22.11.2026)."""
    m = MODELLE["af_ninja_af500"]

    def test_d7_15_zweites_preisobjekt_andere_feldfolge(self):
        eigen = {"id": "Saturn:de:111", "currency": "EUR", "isProductOfTypeMarketplace": False,
                 "price": {"__typename": "CofrPriceFeaturePrice", "amount": 219.99, "shippingCost": 0}}
        markt = {"__typename": "CofrPriceFeature", "isProductOfTypeMarketplace": True, "currency": "EUR",
                 "id": "Saturn:de:111",
                 "price": {"__typename": "CofrPriceFeaturePrice", "amount": 219.99, "shippingCost": 0}}
        text = saturn_text([eigen, markt])
        self.assertIsNone(s.mms_preisfeld(text, "Saturn:de:", "111"))
        g, prot = s.auswerten_seite(text, self.m, QUELLEN["saturn"], "L", "Z")
        self.assertEqual(g, [], prot)
        # Gegenprobe: zwei gleichlautende Preisobjekte in beliebiger Feldfolge bleiben gültig
        gleich = dict(markt, isProductOfTypeMarketplace=False)
        self.assertEqual(s.mms_preisfeld(saturn_text([eigen, gleich]), "Saturn:de:", "111"), (False, 219.99, 0.0))
        self.assertEqual(s.mms_preisfeld(saturn_text([gleich]), "Saturn:de:", "111"), (False, 219.99, 0.0))
        # echte Saturn-Seite 22.11.2026: Abhol-/Liefermerkmale tragen dieselbe id und ein eigenes Marktplatzfeld
        abholung = {"__typename": "CofrPickupFeature", "id": "Saturn:de:111", "isProductOfTypeMarketplace": False}
        lieferung = {"__typename": "CofrDeliveryFeature", "id": "Saturn:de:111", "shippingCost": 0,
                     "isProductOfTypeMarketplace": False}
        verweis = {"id": "Saturn:de:111", "price": {"installment": None}}
        self.assertEqual(s.mms_preisfeld(saturn_text([verweis, abholung, gleich, lieferung]), "Saturn:de:", "111"),
                         (False, 219.99, 0.0))
        # unlesbarer Zustand (unausgeglichene Klammern) ist nie ein Nachweis
        z = json.dumps({"artikel": [gleich]}, separators=(",", ":"))
        p = produkt(ean="0622356270373", price="219.99")
        del p["offers"]["seller"]
        p["sku"] = "111"
        self.assertIsNone(s.mms_preisfeld(seite(p) + zustand_skript(z[:-1] + ',"x":[{{{{]}'), "Saturn:de:", "111"))

    def test_d7_11_r4_sichtbarer_text_und_passive_inhalte(self):
        sperr = "Please complete the <strong>CAPTCHA</strong> to continue."
        self.assertTrue(s.ist_challenge(sperr, "text/plain"))
        self.assertTrue(s.ist_challenge(seite(produkt()) + "<p>%s</p>" % sperr, "text/html"))
        self.assertTrue(s.ist_challenge("<p>Ich&nbsp;bin kein Roboter</p>", "text/html"))
        robots = "User-agent: *\nDisallow: /cdn-cgi/challenge-platform/h/b/orchestrate/\n"
        self.assertFalse(s.ist_challenge(robots, "text/plain"))
        self.assertFalse(s.ist_challenge(robots, "text/html"))
        vorlage_inaktiv = seite(produkt()) + "<template><label>Ich bin kein Roboter</label></template>"
        self.assertFalse(s.ist_challenge(vorlage_inaktiv, "text/html"))
        self.assertFalse(s.ist_challenge(seite(produkt()) + "<script>var t='Access Denied';</script>", "text/html"))


class Runde5(unittest.TestCase):
    """Regressionstests zur Codex-Nachprüfung r5 (22.11.2026), Umbau der drei Prüfstellen."""
    m = MODELLE["af_ninja_af500"]

    @staticmethod
    def preis(sku="111", mp=False, amount=219.99, **extra):
        o = {"__typename": "CofrPriceFeature", "id": "Saturn:de:" + sku, "currency": "EUR",
             "isProductOfTypeMarketplace": mp,
             "price": {"__typename": "CofrPriceFeaturePrice", "amount": amount, "shippingCost": 0}}
        o.update(extra)
        return o

    def test_d7_15_unvollstaendiges_oder_doppelt_typisiertes_preisobjekt(self):
        ohne_waehrung = {"__typename": "CofrMediaAssetsFeature", "id": "Saturn:de:111",
                         "price": {"__typename": "CofrPriceFeaturePrice", "amount": 229.99}}
        self.assertIsNone(s.mms_preisfeld(saturn_text([self.preis(), ohne_waehrung]), "Saturn:de:", "111"))
        z = json.dumps({"artikel": [self.preis()]}, separators=(",", ":"))
        doppelt = z[:-2] + ',{"__typename":"CofrPriceFeature","__typename":"CofrMediaAssetsFeature",' \
                           '"id":"Saturn:de:111","isProductOfTypeMarketplace":true}]}'
        p = produkt(ean="0622356270373", price="219.99")
        del p["offers"]["seller"]
        p["sku"] = "111"
        text = seite(p) + zustand_skript(doppelt)
        self.assertIsNone(s.mms_preisfeld(text, "Saturn:de:", "111"))
        g, prot = s.auswerten_seite(text, self.m, QUELLEN["saturn"], "L", "Z")
        self.assertEqual(g, [], prot)

    def test_d7_18_grosses_medienobjekt_stoert_nicht(self):
        medien = {"__typename": "CofrMediaAssetsFeature", "media": [{"a": {"b": i}} for i in range(200)],
                  "id": "Saturn:de:111"}
        self.assertEqual(s.mms_preisfeld(saturn_text([medien, self.preis()]), "Saturn:de:", "111"), (False, 219.99, 0.0))

    def test_zustand_wie_echte_seite(self):
        # echte Saturn-Seite 22.11.2026: Objektliteral mit undefined, Verweisschlüssel mit eingebetteten Anführungen
        roh = ('{"a":{"error":undefined,"CofrPriceFeature:{\\"id\\":\\"Saturn:de:111\\"}":%s},"b":[undefined]}'
               % json.dumps(self.preis()))
        p = produkt(ean="0622356270373", price="219.99")
        del p["offers"]["seller"]
        p["sku"] = "111"
        self.assertEqual(s.mms_preisfeld(seite(p) + zustand_skript(roh), "Saturn:de:", "111"), (False, 219.99, 0.0))
        zwei = seite(p) + zustand_skript(roh) + zustand_skript(roh)  # zwei Zuweisungen: mehrdeutig
        self.assertIsNone(s.mms_preisfeld(zwei, "Saturn:de:", "111"))

    def test_d7_11_auszeichnung_im_wort(self):
        self.assertTrue(s.ist_challenge(seite(produkt()) + "<p>Please complete the CAP<strong>T</strong>CHA "
                                        "to continue.</p>", "text/html"))
        self.assertTrue(s.ist_challenge("<p>Ich bin kein Ro<span>bo</span>ter</p>", "text/html"))

    def test_d7_17_passive_merkmale_sperren_nicht_aktive_schon(self):
        p = seite(produkt())
        self.assertFalse(s.ist_challenge(p + "<template><div id='px-captcha'></div></template>", "text/html"))
        self.assertFalse(s.ist_challenge(p + "<script>const label='px-captcha';</script>", "text/html"))
        self.assertFalse(s.ist_challenge(p + "<!-- Access Denied -->", "text/html"))
        robots = "User-agent: *\n# /cdn-cgi/challenge-platform/h/b/orchestrate/\nDisallow: /cdn-cgi/\n"
        self.assertFalse(s.ist_challenge(robots, "text/plain"))
        self.assertFalse(s.ist_challenge(robots, "text/html"))
        self.assertTrue(s.ist_challenge(p + "<div id='px-captcha'></div>", "text/html"))
        self.assertTrue(s.ist_challenge("<script>window._cf_chl_opt={cvId:'3'};</script>", "text/html"))
        self.assertTrue(s.ist_challenge('<script src="/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1">'
                                        "</script>", "text/html"))
        self.assertTrue(s.ist_challenge("<title>Just a moment...</title>", "text/html"))

    def test_d7_02_d7_16_rahmen_streng(self):
        import http.server
        import socket
        import threading
        voll = b"User-agent: *\r\nDisallow: /de/product/\r\n"
        kopf = b"%x\r\n" % len(voll) + voll + b"\r\n"
        antworten = {
            "/lf": ("chunked", kopf + b"0\r\n\n"),  # D7-02 r5: Abschluss nur LF
            "/trailer": ("chunked", kopf + b"0\r\nX-Pruef: 1\r\n\r\n"),  # gültig mit Trailer
            "/leer_te": ("chunked ", kopf),  # D7-16: Leerzeichen, Endchunk fehlt
            "/leer_te_ok": ("chunked ", kopf + b"0\r\n\r\n"),  # D7-16: Leerzeichen, vollständig
            "/gzip": ("gzip, chunked", kopf + b"0\r\n\r\n"),  # anderer Rahmen
            "/offen": (None, voll),  # weder Länge noch chunked: Ende nur durch Verbindungsabbau
            "/beides": ("chunked", kopf + b"0\r\n\r\n"),  # chunked und Content-Length zugleich
            "/ende_ohne_crlf": ("chunked", b"%x\r\n" % len(voll) + voll + b"XX0\r\n\r\n"),
        }

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                te, body = antworten[self.path]
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                if te:
                    self.send_header("Transfer-Encoding", te)
                if self.path == "/beides":
                    self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                self.wfile.flush()
                self.connection.shutdown(socket.SHUT_WR)
                self.close_connection = True

            def log_message(self, *a):
                pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        basis = "http://127.0.0.1:%d" % srv.server_address[1]
        alt_proxy = os.environ.get("no_proxy")
        os.environ["no_proxy"] = "127.0.0.1"
        try:
            for pfad in ("/lf", "/leer_te", "/gzip", "/offen", "/beides", "/ende_ohne_crlf"):
                with self.assertRaises(s.NichtAbrufbar, msg=pfad):
                    s.abrufen(basis + pfad)
            for pfad in ("/trailer", "/leer_te_ok"):
                self.assertIn("Disallow: /de/product/", s.abrufen(basis + pfad), pfad)
            r = s.robots_fuer({"domain": "x"}, holen=lambda u: s.abrufen(basis + "/lf"))
            self.assertIsInstance(r, str)
        finally:
            srv.shutdown()
            srv.server_close()
            if alt_proxy is None:
                os.environ.pop("no_proxy", None)
            else:
                os.environ["no_proxy"] = alt_proxy


if __name__ == "__main__":
    unittest.main()
