"""Siteyi üretir: repodaki CSV/JSON verisini template.html'e gömer.

Çalıştır: python3 site/build_site.py
Çıktı: site/model.fragment.html (yayın parçası), site/index.html (bağımsız sayfa).
"""
import csv
import json
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
SITE = Path(__file__).resolve().parent


def oku(ad):
    return list(csv.DictReader(open(KOK / ad, encoding="utf-8-sig")))


def f(x):
    return None if x in ("", None) else float(x)


def veri():
    pairs = [{"cift": x["cift"], "ab": f(x["bacak_ab"]) or 0, "ba": f(x["bacak_ba"]) or 0,
              "ortak": f(x["ortak_stok"]), "brut": f(x["brut"]),
              "iki": x["kaynak_ab"] == "metin" and x["kaynak_ba"] == "metin"} for x in oku("adim1_stok.csv")]
    nace = [{"nace": x["nace"], "alacak": f(x["ticari_alacak"]), "borc": f(x["ticari_borc"]), "net": f(x["net"]) or 0,
             "nakit": f(x["hazir_degerler"]), "kv": f(x["banka_kredisi_kv"]), "fin": f(x["finansman_gideri"])}
            for x in oku("adim1_nace.csv")]
    y20 = [{"taban": x["taban"], "brut": f(x["brut_milyar"]), "ust": f(x["ust_sinir_milyar"])} for x in oku("adim1_yuzde20.csv")]
    dugum = [{"d": x["dugum"], "nakit": f(x["nakit_milyar"]), "borc": f(x["ticari_borc"])} for x in oku("adim2_nace_dugum.csv")]
    a2 = [{"l": f(x["lambda"]), "h": f(x["holding_odeme_orani"]), "b": f(x["ucret_gecis_beta"]),
           "tb": f(x["temerrut_brut"]), "tm": f(x["temerrut_mahsup"]), "ts": f(x["temerrut_sart"]),
           "ub": f(x["ucret_temerrut_brut"]), "us": f(x["ucret_temerrut_sart"]),
           "kb": f(x["kredi_ihtiyaci_brut"]), "ks": f(x["kredi_ihtiyaci_sart"]),
           "ib": f(x["istihdam_korunan_brut"]), "is": f(x["istihdam_korunan_sart"]),
           "sil": f(x["silinen_milyar"]), "silo": f(x["silinen_oran"]), "lik": f(x["serbest_likidite"]),
           "uc": f(x["ucret_piyasa_kanali"]), "batik": x["batik"]} for x in oku("adim2_nace_ag.csv")]
    q4 = sorted({x["donem"] for x in oku("adim4_adres_yonlendirme.csv")})
    a4 = {}
    for x in oku("adim4_adres_yonlendirme.csv"):
        k = f"{float(x['theta'])}|{float(x['chi'])}|{float(x['pi'])}"
        a4.setdefault(k, {"stok": {}, "prim": {}})
        a4[k]["stok"][x["donem"]] = round(float(x["stok"]), 2)
        a4[k]["prim"][x["donem"]] = round(float(x["prim_ceyrek"]), 4)
    a4 = {k: {m: [v[m][q] for q in q4] for m in v} for k, v in a4.items()}
    a45 = json.load(open(KOK / "adim45_birim.json", encoding="utf-8"))
    a5 = [{"n": x["nesne"], "lo": x["alt"], "hi": x["ust"], "e": x["durum"]} for x in oku("adim5_kira_aralik.csv")]
    return {"pairs": pairs, "nace": nace, "y20": y20, "dugum": dugum, "a2": a2, "q4": q4, "a4": a4, "a45": a45, "a5": a5}


def main():
    html = (SITE / "template.html").read_text(encoding="utf-8").replace("__DATA__", json.dumps(veri(), ensure_ascii=False, separators=(",", ":")))
    (SITE / "model.fragment.html").write_text(html, encoding="utf-8")
    (SITE / "index.html").write_text('<!doctype html>\n<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>\n' + html + "\n</body></html>\n", encoding="utf-8")
    print("yazıldı:", len(html), "bayt")


if __name__ == "__main__":
    main()
