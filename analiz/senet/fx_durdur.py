"""Döviz stok artışını durdurma taslağı.

Mevcut sözleşme silinmez (RAPOR.md:44). Değerleme artışı s0·yp·δ, bugünkü stoktan.
Yeni YP mevduat birikimi gelmez; o akış kâğıda veya TL mevduata yazılır.
Brüt dış borç ayrı nesnedir (DOVIZ_EGILIM.md).
"""
from __future__ import annotations

import csv

import rev_sok
from mahsuplasma.mahsup import optimal_mahsup
from mahsuplasma.model import Parametreler, calistir

import rant
from ortak import BETA, KOK, KUR, LAM, adres, med, oku_json, r2, r4, usd_ay, yaz_csv, yaz_json, yp_stok


def miktar(s0: float, s1: float, e0: float, e1: float) -> dict:
    q0, q1 = s0 / e0, s1 / e1
    kur = s0 * (e1 / e0 - 1.0)
    akis = s1 - s0 - kur
    return {
        "stok0": r4(s0), "stok1": r4(s1), "kur0": r4(e0), "kur1": r4(e1),
        "dTL": r4(s1 - s0), "dUSD": r4(q1 - q0), "kur_TL": r4(kur), "miktar_TL": r4(akis),
    }


def sok(girdi, kenar=None) -> dict:
    g, artis = rev_sok.ag_kur(KUR, LAM, girdi, kenar)
    p = Parametreler(holding_odeme_orani=0.5, sart_kaldiraci=True, ucret_gecis_beta=BETA)
    r = calistir(g, p)
    a = r["asamalar"]["4_sart_kaldiraci"]
    t = r["teshis"]
    return {
        "artis": r4(artis),
        "temerrut": int(a["temerrut_sayisi"]),
        "kopru": r2(a["kredi_ihtiyaci"]),
        "kilitli": len(t["kilitli"]),
        "batik": len(t["batik"]),
        "kilitli_ad": list(t["kilitli"]),
        "batik_ad": list(t["batik"]),
        "ag": g,
    }


def mevduat_yp() -> list[dict]:
    out = []
    for r in csv.DictReader((KOK / "diger_mevduat.csv").open(encoding="utf-8-sig")):
        if r.get("seri", "").startswith("TP.HPBITABLO2.") and r["seri"][-1] in "678":
            out.append({
                "donem": r["donem"], "ad": r["kalem"], "seri": r["seri"],
                "milyar": float(r["stok_milyar"]),
            })
    return out


def main():
    girdi = rev_sok.yukle()
    A = adres()
    usd = usd_ay()
    artis = rev_sok.artis_stok(KUR, girdi)
    tam = sok(girdi)
    net = optimal_mahsup(tam.pop("ag"))
    bol = rant.halka(net, 1.0e9, False)
    sey = []
    for s in range(rev_sok.TOHUM):
        ken = rev_sok.seyrek_kenar(girdi, 0.25, s)
        if ken is None:
            continue
        sey.append(sok(girdi, ken))
        sey[-1].pop("ag", None)
    stok = {r["donem"]: r["milyar_tl"] for r in yp_stok()}
    gercek = [
        miktar(stok["2024-Q4"], stok["2025-Q4"], usd["2024-12"], usd["2025-12"]),
        miktar(stok["2025-Q4"], stok["2026-Q1"], usd["2025-12"], usd["2026-03"]),
    ]
    gercek[0]["pencere"] = "2024-Q4_2025-Q4"
    gercek[1]["pencere"] = "2025-Q4_2026-Q1"
    gercek[0]["etiket"] = "aday: aylik ortalama kur ile stok miktari; faiz tahakkuku ayrilmadi"
    gercek[1]["etiket"] = "tek ceyrek, yil degil"
    yurtici = {}
    for r in mevduat_yp():
        yurtici.setdefault(r["seri"], {})[r["donem"]] = r["milyar"]
    ceyrek = {}
    for seri, ad in (
        ("TP.HPBITABLO2.6", "yurtici"),
        ("TP.HPBITABLO2.7", "gercek"),
        ("TP.HPBITABLO2.8", "tuzel"),
    ):
        s0, s1 = yurtici[seri]["2025-Q4"], yurtici[seri]["2026-Q1"]
        ceyrek[ad] = miktar(s0, s1, usd["2025-12"], usd["2026-03"])
    borc = oku_json("akis_model_ozeti.json")["dis_borc_artisi"]
    st = borc["stok_milyar_USD"]
    yil_borc = []
    for ad in ("Toplam", "Özel"):
        u0, u1 = st["2024-Q4"][ad], st["2025-Q4"][ad]
        k0 = st["2024-Q4"]["USDTRY"]
        yil_borc.append({
            "nesne": ad,
            "usd0": u0, "usd1": u1, "dUSD": r2(u1 - u0),
            "yeni_TL": r2((u1 - u0) * k0),
            "not": "yuvarlak stok farki; acilis kuru dis_borc_artisi kimligi",
        })
    fx_akis = gercek[0]["miktar_TL"]
    butceler = {
        "fx": fx_akis,
        "Aon30": 0.30 * A["A_on"],
        "Aon30_fx": 0.30 * A["A_on"] + fx_akis,
        "Auc30": 0.30 * A["A_uc"],
        "Auc30_fx": 0.30 * A["A_uc"] + fx_akis,
    }
    tam_akis = {}
    sey_akis = {}
    for ad, B in butceler.items():
        h = rant.halka(net, B, False)
        hs = [rant.halka(n, B, False) for n in _nets(girdi)]
        tam_akis[ad] = {"butce": r2(B), "cekilen": h["cekilen"], "araci": h["araci"], "banka": h["banka"], "atil": h["atil"]}
        sey_akis[ad] = {
            "butce": r2(B),
            "kapanan": sum(x["araci"] < 0.05 for x in hs),
            "n": len(hs),
            "araci_med": r2(med([x["araci"] for x in hs])),
            "cekilen_med": r2(med([x["cekilen"] for x in hs])),
            "banka_med": r2(med([x["banka"] for x in hs])),
            "holding_med": r2(med([x["holding"] for x in hs])),
            "atil_med": r2(med([x["atil"] for x in hs])),
        }
    banka_sonra = bol["banka"]
    kosul = {
        "yp_maruziyeti_korunmus": False,
        "kur_yukumluluk_karsilanmis": banka_sonra < 0.05,
        "ag_yogun_veya_merkezi_takas": False,
        "kopru_boyutlandi": tam["kopru"] <= 52.4,
        "uc_kosul": False,
        "not": "Dondurma yeni akisi keser. Mevcut yp degerlenir. Halka BANKA ayagini kapatmaz. Yogunluk 0,25 ayri kosuludur.",
    }
    gsyh = A["gsyh_2026"]
    finans = {}
    for ad, h in tam_akis.items():
        atil = h["atil"]
        finans[ad] = {
            "atil": atil,
            "gsyh_yuzde": r4(100.0 * atil / gsyh),
            "kredi_bant": [r2(A["c_bant"][0] * atil), r2(A["c_bant"][1] * atil)],
        }
    out = {
        "etiket": "aday: kur/miktar ayrimi ve 2025 hizinin surmesi; degerleme vurusu kanit formulu",
        "lam": LAM,
        "kur_yuzde": KUR,
        "s0": r4(girdi["s0"]),
        "yp": r4(girdi["yp"]),
        "artis": r4(artis),
        "artis_baz": 2660.8843,
        "artis_ayni": abs(artis - 2660.8843) < 1e-3,
        "tam": {k: tam[k] for k in ("artis", "temerrut", "kopru", "kilitli", "batik", "kilitli_ad", "batik_ad")},
        "halka_cekilen": bol["cekilen"],
        "halka_banka": bol["banka"],
        "halka_araci0": rant.halka(net, 0.0, False)["araci"],
        "seyrek": {
            "n": len(sey),
            "temerrut_min": min(x["temerrut"] for x in sey),
            "temerrut_med": med([x["temerrut"] for x in sey]),
            "temerrut_max": max(x["temerrut"] for x in sey),
            "kopru_min": r2(min(x["kopru"] for x in sey)),
            "kopru_med": r2(med([x["kopru"] for x in sey])),
            "kopru_max": r2(max(x["kopru"] for x in sey)),
            "kilit_med": med([x["kilitli"] for x in sey]),
            "batik_med": med([x["batik"] for x in sey]),
            "artis_tek": sorted({x["artis"] for x in sey}),
        },
        "gercek_kisi_yp": gercek,
        "diger_mevduat_ceyrek": ceyrek,
        "brut_dis_borc_2025": yil_borc,
        "egim_ceyrek_mr_usd": 10.64,
        "korunmasiz_senaryo_yillik_mr_usd": r4(121.8 * 0.06),
        "fx_akis_tl": fx_akis,
        "tam_akis": tam_akis,
        "seyrek_akis": sey_akis,
        "finans_tam": finans,
        "emme": {
            "fx_H": fx_akis <= A["H"],
            "fx_genis": fx_akis <= A["genis"],
            "fx_piyasa": fx_akis <= A["piyasa"],
            "H": A["H"], "genis": A["genis"], "piyasa": A["piyasa"],
        },
        "adim2_kosul_bu_taslakta": kosul,
        "sfc": "Yeni akis FX mevduat yerine esit TL kagit/mevduattir; ek NFP 0. Mevcut degerleme bazdaki artis. Prim 0.",
    }
    yaz_json("fx_durdur_sonuc.json", out)
    yaz_csv(
        "fx_durdur.csv",
        ["pencere", "dUSD", "miktar_TL", "kur_TL", "dTL"],
        gercek,
    )
    print("fx artis", out["artis"], "akis", fx_akis, "kosul", kosul["uc_kosul"])


def _nets(girdi):
    if not hasattr(_nets, "bellek"):
        bellek = []
        for s in range(rev_sok.TOHUM):
            ken = rev_sok.seyrek_kenar(girdi, 0.25, s)
            if ken is None:
                continue
            gs, _ = rev_sok.ag_kur(KUR, LAM, girdi, ken)
            bellek.append(optimal_mahsup(gs))
        _nets.bellek = bellek
    return _nets.bellek


if __name__ == "__main__":
    main()
