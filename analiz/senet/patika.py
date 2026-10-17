"""Yıllık kademe: θ ∈ {0,10; 0,30}. M_t = θ · A, kalan stok son yılda.

θ kalanın yüzdesi değildir. 0,10 on yıl sürer. 0,30 üç tam yıl ve dördüncü yılda 0,10 · A.

Emme tavanları rev_adim4 DİBS paylarıdır (kanıt stok). Onları akış tavanı saymak adaydır.
Üretim açığı bir kez ölçülür; model açığı her çeyrek yeniden doğurmaz (aday).
"""
from __future__ import annotations

import rev_sok
from mahsuplasma.mahsup import optimal_mahsup

import rant
from ortak import KUR, LAM, adres, med, r2, r4, yaz_csv, yaz_json


def dilimler(A: float, theta: float) -> list[float]:
    kalan = A
    out = []
    while kalan > 1e-6:
        parca = min(theta * A, kalan)
        out.append(parca)
        kalan -= parca
    return out


def emme(akis: float, tavan: float) -> dict:
    return {
        "akis": r2(akis),
        "tavan": r4(tavan),
        "alir": akis <= tavan + 1e-9,
        "oran": r4(akis / tavan) if tavan else None,
        "sure_yil": r4(tavan / akis) if akis else None,
    }


def main():
    A = adres()
    girdi = rev_sok.yukle()
    g, artis = rev_sok.ag_kur(KUR, LAM, girdi)
    net = optimal_mahsup(g)
    bol = rant.halka(net, 1.0e9, False)
    cek = bol["cekilen"]
    nets = []
    for s in range(rev_sok.TOHUM):
        ken = rev_sok.seyrek_kenar(girdi, 0.25, s)
        if ken is None:
            continue
        gs, _ = rev_sok.ag_kur(KUR, LAM, girdi, ken)
        nets.append(optimal_mahsup(gs))
    yillar = []
    ceyrekler = []
    for theta in (0.10, 0.30):
        for ad, AA in (("on", A["A_on"]), ("uc", A["A_uc"])):
            parca = dilimler(AA, theta)
            stok = 0.0
            for i, m in enumerate(parca, start=1):
                stok += m
                q = m / 4.0
                h = rant.halka(net, q, False)
                hs = [rant.halka(n, q, False) for n in nets]
                yil = 2025 + i
                gsyh = A["gsyh"].get(str(yil))
                atil = max(0.0, m - cek) if i == 1 else m
                satir = {
                    "theta": theta,
                    "adres": ad,
                    "A": AA,
                    "yil_sira": i,
                    "takvim_aday": yil,
                    "akis": r2(m),
                    "ceyrek": r2(q),
                    "kumulatif": r2(stok),
                    "kalan_stok": r2(AA - stok),
                    "emme_H": emme(m, A["H"]),
                    "emme_genis": emme(m, A["genis"]),
                    "emme_piyasa": emme(m, A["piyasa"]),
                    "tam_ceyrek_cekilen": h["cekilen"],
                    "tam_ceyrek_araci": h["araci"],
                    "tam_ceyrek_banka": h["banka"],
                    "tam_ceyrek_atil": h["atil"],
                    "seyrek_ceyrek_araci_med": r2(med([x["araci"] for x in hs])),
                    "seyrek_ceyrek_cekilen_med": r2(med([x["cekilen"] for x in hs])),
                    "seyrek_ceyrek_kapanan": sum(x["araci"] < 0.05 for x in hs),
                    "seyrek_n": len(hs),
                    "TCMB_akis": r2(m),
                    "TCMB_atil_tek_sefer": r2(atil),
                    "TCMB_atil_gsyh": None if not gsyh else r4(100.0 * atil / gsyh),
                    "kredi_bant_atil": [r2(A["c_bant"][0] * atil), r2(A["c_bant"][1] * atil)],
                    "gsyh": gsyh,
                }
                yillar.append(satir)
                ceyrekler.append({
                    "theta": theta, "adres": ad, "yil_sira": i, "ceyrek_akis": r2(q),
                    "tam_araci": h["araci"], "tam_cekilen": h["cekilen"], "tam_banka": h["banka"],
                    "seyrek_kapanan": satir["seyrek_ceyrek_kapanan"], "seyrek_n": len(hs),
                    "seyrek_araci_med": satir["seyrek_ceyrek_araci_med"],
                })
    # stok kuponu: yıl sonu birikmiş anapara × π. Ödenen prim 0 (R yok).
    kupon = []
    for theta in (0.10, 0.30):
        for ad, AA in (("on", A["A_on"]), ("uc", A["A_uc"])):
            stok = 0.0
            for i, m in enumerate(dilimler(AA, theta), start=1):
                stok += m
                for pi in (0.02, 0.05):
                    kupon.append({
                        "theta": theta, "adres": ad, "yil_sira": i, "pi": pi,
                        "stok": r2(stok), "tasarim_kupon": r2(pi * stok),
                        "akis_kupon": r2(pi * m), "odenen": 0.0,
                    })
    out = {
        "etiket": "aday: yillik theta stokun yuzdesi; takvim 2026'dan; acik tek sefer",
        "artis_banka": r4(artis),
        "tam_cekilen": cek,
        "tam_banka_halka": bol["banka"],
        "A": {"on": A["A_on"], "uc": A["A_uc"], "H": A["H"], "genis": A["genis"], "piyasa": A["piyasa"]},
        "c_bant": A["c_bant"],
        "gsyh_2026": A["gsyh_2026"],
        "yillar": yillar,
        "kupon_tasarim": kupon,
        "not": "Katman sonuclari tasinmaz (TEK_SISTEM_KADEME.md). Bu patika Adim 2 hukumune yazilmaz.",
    }
    yaz_json("patika_sonuc.json", out)
    alan = [
        "theta", "adres", "yil_sira", "takvim_aday", "akis", "ceyrek", "kumulatif",
        "emme_H_alir", "emme_genis_alir", "emme_piyasa_alir",
        "tam_ceyrek_cekilen", "tam_ceyrek_araci", "seyrek_ceyrek_kapanan", "seyrek_n",
        "TCMB_atil_tek_sefer", "TCMB_atil_gsyh", "kredi_alt", "kredi_ust",
    ]
    duz = []
    for s in yillar:
        duz.append({
            "theta": s["theta"], "adres": s["adres"], "yil_sira": s["yil_sira"],
            "takvim_aday": s["takvim_aday"], "akis": s["akis"], "ceyrek": s["ceyrek"],
            "kumulatif": s["kumulatif"],
            "emme_H_alir": s["emme_H"]["alir"], "emme_genis_alir": s["emme_genis"]["alir"],
            "emme_piyasa_alir": s["emme_piyasa"]["alir"],
            "tam_ceyrek_cekilen": s["tam_ceyrek_cekilen"], "tam_ceyrek_araci": s["tam_ceyrek_araci"],
            "seyrek_ceyrek_kapanan": s["seyrek_ceyrek_kapanan"], "seyrek_n": s["seyrek_n"],
            "TCMB_atil_tek_sefer": s["TCMB_atil_tek_sefer"], "TCMB_atil_gsyh": s["TCMB_atil_gsyh"],
            "kredi_alt": s["kredi_bant_atil"][0], "kredi_ust": s["kredi_bant_atil"][1],
        })
    yaz_csv("patika.csv", alan, duz)
    print("patika", len(yillar), "cekilen", cek)


if __name__ == "__main__":
    main()
