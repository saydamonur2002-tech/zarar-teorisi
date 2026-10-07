"""Ana gösterge: ÖDEMEYEN PAYI, hane ve firma ayrı (takip, VYŞ'ye satılan, yakın izleme).

Kademeler (her biri bir öncekini içerir):
  G1  takip oranı        = takipteki / (performans kredisi + takipteki)                    (EVDS, aylık, 2024-06 ..)
  G2  + VYŞ'ye satılan   = (takipteki + VYŞ portföyünün payı) / (kredi + takipteki + VYŞ payı)   (VYŞ 132 mr TL; hane %80 / firma %20: varsayım)
  G3  + yakın izleme     = G2 + II. Grup (2.624 mr TL, Haz 2026, TBB); hane payı aralığı [%45,6 .. %80], firma = kalan  (kırılım YAYIMLANMIYOR)
Aylık tam seri yalnızca G1. G2 ve G3 için tek kesit (2026-06).
Kişi göstergesi: TBB Risk Merkezi yasal takibe GİRİŞ (kişi/ay, akım; çıkanlar netlenmiyor).
"""
import json
from pathlib import Path

import pandas as pd

D = Path(__file__).parent
VYS, VYS_HANE = 132.0, 0.80
YI = 2624.0
YI_HANE_LOW, YI_HANE_HIGH = 0.456, 0.80
KISI = {"2026-01": 262000, "2026-02": 221000, "2026-03": 220000, "2026-04": 213775, "2026-05": 210255, "2026-06": 297309, "2026-07": 264580}


def ozet():
    n = pd.read_csv(D / "npl_ham.csv", dtype={"Donem": str})
    h = n[n.Grup == "bie_hpbitablo6"].pivot_table(index="Donem", columns="Seri", values="Deger", aggfunc="last") / 1e6  # mr TL
    ser = pd.DataFrame({
        "tuketici_kredi": h["TP.HPBITABLO6.2"], "ticari_ve_diger_kredi": h["TP.HPBITABLO6.19"],
        "takip_tuketici": h["TP.HPBITABLO6.50"], "takip_ticari_diger": h["TP.HPBITABLO6.55"],
    })
    ser["hane_G1_%"] = 100 * ser.takip_tuketici / (ser.tuketici_kredi + ser.takip_tuketici)
    ser["firma_G1_%"] = 100 * ser.takip_ticari_diger / (ser.ticari_ve_diger_kredi + ser.takip_ticari_diger)
    ser["hane/firma"] = ser["hane_G1_%"] / ser["firma_G1_%"]
    ser.round(3).to_csv(D / "odemeyen_payi_aylik.csv", encoding="utf-8-sig")

    r = ser.loc["2026-06"]
    vh, vf = VYS * VYS_HANE, VYS * (1 - VYS_HANE)
    g2_h = 100 * (r.takip_tuketici + vh) / (r.tuketici_kredi + r.takip_tuketici + vh)
    g2_f = 100 * (r.takip_ticari_diger + vf) / (r.ticari_ve_diger_kredi + r.takip_ticari_diger + vf)
    g3 = {}
    for ad, ph in (("alt(hane payi %45,6)", YI_HANE_LOW), ("ust(hane payi %80)", YI_HANE_HIGH)):
        yh, yf = ph * YI, (1 - ph) * YI
        g3[ad] = {"hane_%": round(100 * (r.takip_tuketici + vh + yh) / (r.tuketici_kredi + r.takip_tuketici + vh + yh), 2),
                  "firma_%": round(100 * (r.takip_ticari_diger + vf + yf) / (r.ticari_ve_diger_kredi + r.takip_ticari_diger + vf + yf), 2)}

    a, b, c = ser.loc["2024-06"], ser.loc["2025-06"], ser.loc["2026-09"]
    out = {
        "tanim": "ödemeyen payı = hane ve firma için ayrı; G1 resmi takip oranı, G2 VYŞ eklenir, G3 yakın izleme eklenir",
        "G1_takip_orani_%": {
            "hane": {"2024-06": round(a["hane_G1_%"], 2), "2025-06": round(b["hane_G1_%"], 2), "2026-09": round(c["hane_G1_%"], 2)},
            "firma": {"2024-06": round(a["firma_G1_%"], 2), "2025-06": round(b["firma_G1_%"], 2), "2026-09": round(c["firma_G1_%"], 2)},
            "hane/firma_2026-09": round(c["hane/firma"], 2),
        },
        "kesit_2026-06": {
            "G1": {"hane_%": round(r["hane_G1_%"], 2), "firma_%": round(r["firma_G1_%"], 2)},
            "G2_VYS_eklenince": {"hane_%": round(g2_h, 2), "firma_%": round(g2_f, 2)},
            "G3_yakin_izleme_eklenince": g3,
        },
        "kisi_gostergesi_yasal_takibe_giris_aylik": KISI,
        "kisi_gostergesi_not": "akım, çıkanlar netlenmiyor, aynı kişi kart+kredi tek sayılır; Oca-Tem 2026 toplamı = %d (benzersiz kişi sayısı değildir)" % sum(KISI.values()),
        "uyari": [
            "G3 'ÖDEMEYEN' değil 'ödeme riski altında': yakın izlemenin büyük kısmı gecikmesiz (FİR 2026-I, TFRS 9 'riskte kayda değer artış'); "
            "'gecikmesi olan yakın izleme' TGA ile birlikte ~%5 (FİR). G1/G2 ödeme yapmayanları, G3 olası ödemeyenleri de içerir.",
            "G2/G3 tek kesit; zaman serisi yok (VYŞ ve yakın izleme serisi yok).",
            "Yakın izleme hane/firma kırılımı yayımlanmıyor: aralık [%45,6 .. %80] varsayım; FİR artışı ağırlıkla haneye bağlıyor.",
            "Paydalar: EVDS yurt içi şube kredileri; yakın izleme TBB (farklı kapsam), karşılaştırma yaklaşık.",
            "Firma tarafı KOBİ ve büyük firma ayrımını içermiyor (KOBİ TGA yaklaşık %3,4, büyük firma %1,4 - FİR 2026-I).",
        ],
    }
    return out


if __name__ == "__main__":
    print(json.dumps(ozet(), ensure_ascii=False, indent=2))
