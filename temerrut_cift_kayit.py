"""Temerrüdün ÇİFT KAYDI: alacaklı defteri vs borçlu defteri (hane, tüketici kredisi + kart).

Eski L matrisi temerrüdü "borçludan alacaklıya zarar aktarımı" (sıfır toplamlı) gibi yazıyordu. Gerçekte:
  Borçlu defteri : borç, temerrüt sonrası SİLİNMEZ (bireysel iflas/borçtan kurtulma yok - DOĞRULANMADI) ve gecikme faiziyle büyür.
  Alacaklı defteri: banka karşılık ayırır (net defter = (1-cov)*anapara), faiz tahakkuk ettirmez; VYŞ'ye satılan kısım π*anapara maliyetle VYŞ'de durur.
  Fark = "borçlu yükü fazlası" = borçlunun nominal yükü - alacaklıların taşıdığı değer: kimsenin varlık saymadığı, borçlunun taşıdığı yük (yük stoku).

Girdiler (gözlenen): EVDS takipteki tüketici stoku, hane brüt takip girişi (ΔTGA_tüketici + hane satışı), satış payı (vys_kanali), fiyat, karşılık.
Parametreler (VARSAYIM, ayrıca işaretli): temerrüt faizi = ihtiyaç kredisi faizi, ömür boyu tahsilat = (π + (1-cov))/2, 20 çeyrekte eşit.
"""
import json
from pathlib import Path

import pandas as pd

D = Path(__file__).parent
COV, PI = 0.82, 0.15
SOLD_SHARE = 0.22  # vys_kanali: brüt takip girişinin satılan payı
HANE_SATIS_PAY = 0.80
YONETEM_SATIS_Q2 = 25.7  # mr TL (QNB), Nis-Haz 2026
FREE_CAP = 1236.0  # mr TL, yasal serbest sermaye (kalibre_lambda_rapor)
E_TOT = 4530.2


def ozet(horizon=8, g_inflow=0.0):
    n = pd.read_csv(D / "npl_ham.csv", dtype={"Donem": str})

    def s(code, per):
        v = n[(n.Seri == code) & (n.Donem == per)].Deger
        return float(v.iloc[0]) / 1e6  # mr TL

    f = pd.read_csv(D / "faiz_ham.csv", dtype={"Donem": str})
    r_annual = float(f[f.Seri == "TP.KTF10"].sort_values("Donem").Deger.iloc[-1]) / 100  # varsayım: temerrüt faizi = ihtiyaç faizi
    rq = (1 + r_annual / 12) ** 3 - 1

    # gözlenen başlangıç ve akış
    tuk_jun, tuk_mar, tuk_sep = s("TP.HPBITABLO6.50", "2026-06"), s("TP.HPBITABLO6.50", "2026-03"), s("TP.HPBITABLO6.50", "2026-09")
    vys_hane = HANE_SATIS_PAY * 132.0  # mr TL
    N0 = (tuk_jun - tuk_mar) + HANE_SATIS_PAY * YONETEM_SATIS_Q2  # hane brüt yeni takip girişi / çeyrek (Nis-Haz)
    P_bank = tuk_sep          # bankada tutulan anapara (takipteki tüketici stoku, Eyl 2026)
    P_vys = vys_hane          # VYŞ'nin devraldığı hane alacağı (anapara varsayımı)
    I = 0.0                   # birikmiş gecikme faizi (borçlu defterinde)
    rec_q = ((PI + (1 - COV)) / 2) / 20  # çeyrek tahsilat oranı (başlangıç anaparaya göre)

    rows = []
    cum_prov = 0.0
    for t in range(0, horizon + 1):
        if t > 0:
            N = N0 * (1 + g_inflow) ** t
            sold = SOLD_SHARE * N
            kept = N - sold
            # tahsilat: mevcut anaparadan, banka ve VYŞ payına göre orantılı
            P_tot = P_bank + P_vys
            R = min(P_tot, rec_q * P_tot)
            P_bank = P_bank + kept - R * (P_bank / P_tot)
            P_vys = P_vys + sold - R * (P_vys / P_tot)
            I = I * (1 + rq) + rq * (P_bank + P_vys)  # faiz anapara üzerinden, birikmiş faize de işler
            cum_prov += COV * kept
        P_tot = P_bank + P_vys
        borc_yuk = P_tot + I
        alacakli_deger = (1 - COV) * P_bank + PI * P_vys
        fazla = borc_yuk - alacakli_deger
        rows.append({
            "ceyrek": t,
            "anapara_toplam_mrTL": round(P_tot, 1),
            "bankada": round(P_bank, 1), "VYS": round(P_vys, 1),
            "birikmis_gecikme_faizi": round(I, 1),
            "borclu_yuku(nominal)": round(borc_yuk, 1),
            "alacakli_tasidigi_deger": round(alacakli_deger, 1),
            "borclu_yuku_fazlasi": round(fazla, 1),
            "fazla/borclu_yuku_%": round(100 * fazla / borc_yuk, 1),
            "kumulatif_banka_karsilik_mrTL": round(cum_prov, 1),
            "karsilik/serbest_sermaye_%": round(100 * cum_prov / FREE_CAP, 1),
        })
    out = {
        "nesne": "hane, tüketici kredisi + kart; gözlenen: EVDS takipteki tüketici, VYŞ hane payı, satış payı; varsayım: faiz, tahsilat",
        "baslangic_Eyl2026_mrTL": {"bankada_takipteki_tuketici": round(tuk_sep, 1), "VYS_hane_payi": round(vys_hane, 1)},
        "gozlenen_hane_brut_giris_ceyrek_mrTL": round(N0, 1),
        "satis_payi": SOLD_SHARE,
        "varsayim": {"gecikme_faizi_yillik_%": round(r_annual * 100, 1), "omur_boyu_tahsilat_%anapara": round((PI + (1 - COV)) / 2 * 100, 1), "tahsilat_ceyrek_sayisi": 20,
                     "uyari": "Gecikme faizi (yasal sınırlar) ve tahsilat hızı doğrulanmadı; birikmiş faiz bu iki varsayıma bağlı."},
        "deftersel_fark": ["banka: karşılık ayırır, faiz tahakkuk ettirmez (non-accrual)", "VYŞ: π*anapara maliyet", "hane: borç nominal kalır ve faizle büyür"],
        "tablo": rows,
    }
    return out


if __name__ == "__main__":
    o = ozet()
    print(json.dumps({k: v for k, v in o.items() if k != "tablo"}, ensure_ascii=False, indent=2))
    pd.set_option("display.width", 250, "display.max_columns", 20)
    print(pd.DataFrame(o["tablo"]).to_string(index=False))
    print("\n+%10/çeyrek giriş büyümesi:")
    print(pd.DataFrame(ozet(g_inflow=0.10)["tablo"])[["ceyrek", "borclu_yuku(nominal)", "alacakli_tasidigi_deger", "borclu_yuku_fazlasi", "kumulatif_banka_karsilik_mrTL", "karsilik/serbest_sermaye_%"]].to_string(index=False))
