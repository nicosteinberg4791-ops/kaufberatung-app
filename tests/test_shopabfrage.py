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

    def test_proshop_ohne_versandangabe(self):
        g, _ = s.auswerten_seite(vorlage("proshop_s26.html"), MODELLE["phone_s26_ultra_256"], QUELLEN["proshop"], "L", "Z")
        self.assertEqual(len(g), 1)
        self.assertIsNone(g[0]["versand"])
        self.assertIsNone(g[0]["gesamt"])
        self.assertEqual(g[0]["versand_herkunft"], "unbekannt")

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
        text = vorlage("saturn_ninja.html").split("<script>window.__ZUSTAND__")[0]
        g, prot = s.auswerten_seite(text, MODELLE["af_ninja_af500"], QUELLEN["saturn"], "L", "Z")
        self.assertEqual(g, [])
        self.assertIn("Verkäufer fehlt oder nicht belegt", [p["grund"] for p in prot])

    def test_saturn_preisfeld_mit_anderem_preis(self):
        text = vorlage("saturn_ninja.html").replace('"amount": 219.99', '"amount": 199.99').replace(
            '\\"amount\\":219.99', '\\"amount\\":199.99')
        g, prot = s.auswerten_seite(text, MODELLE["af_ninja_af500"], QUELLEN["saturn"], "L", "Z")
        self.assertEqual(g, [])
        self.assertTrue(any("passt nicht zum JSON-LD" in p["grund"] for p in prot), prot)


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
        self.assertEqual([s.zahl(x) for x in (1599, "1599.00", "1.599,00", "219,99", "€ 9", True, "abc")],
                         [1599.0, 1599.0, 1599.0, 219.99, 9.0, None, None])

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
        sperre = "<html><script src='/cdn-cgi/challenge-platform/h/b/orchestrate'></script></html>"
        self.assertTrue(s.ist_challenge(sperre, "text/html; charset=UTF-8"))
        self.assertFalse(s.ist_challenge(sperre + seite(produkt()), "text/html"))

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


if __name__ == "__main__":
    unittest.main()
