"""Varlık yönetim şirketlerine (VYŞ) takipteki alacak satışı: "zarar bankadan çıkar, hane borcu kalır" kanalı.

Mekanizma (çift kayıt):
  1) Banka takipteki alacağı (anapara P) fiyat π*P ile VYŞ'ye satar: bankanın takipteki stoku P kadar azalır, nakit π*P girer,
     karşılık serbest kalır (kaynaklı kayıt: karşılık %82 ise net defter değeri (1-0,82)=%18 P).
  2) VYŞ alacağı π*P maliyetle alır (S.125 içinde; bankadan çıkar) ama HANENİN borcu P (+faiz, masraf) olarak kalır; tahsilat baskısı VYŞ'ye geçer.
  3) Ölçülen takip oranı düşer, ama hane yükü azalmaz. "Satış-düzeltilmiş" yük = bankadaki takipteki + VYŞ'nin devraldığı.

Girdiler (haber/FİR derlemesi; resmî seriyle doğrulanmadı):
  satış: 2024 yılı toplam 40,7 mr TL; 2026 ilk 5 ay 42,7 mr TL; 2026 Nis-Haz 25,7 mr TL (QNB Invest; BDDK verisinden)
  VYŞ devraldığı portföy: 132 mr TL, yıllık +%67,7 (TCMB Finansal İstikrar Raporu aktarımı, haber)
  fiyat: Akbank Haz 2026 514/3.259 = %15,8; Garanti Ağu 2026 449/~3.070 = %14,6; bazı portföyler %25-32; Sözcü örneği ~%12,5
  bireysel pay: 2025 ana para satışlarında %80
EVDS: bankacılık sektörü takipteki alacaklar (TP.HPBITABLO2.38), takipteki tüketici kredileri (TP.HPBITABLO6.50).
"""
import json
from pathlib import Path

import pandas as pd

D = Path(__file__).parent
SATIS_5A26, SATIS_Q2_26, SATIS_2024 = 42.7, 25.7, 40.7  # mr TL
VYS_PORTFOY = 132.0  # mr TL
FIYAT = {"Akbank_Haz26": 514 / 3259, "Garanti_Ağu26": 449 / 3070, "dusuk(Sozcu)": 400 / 3200, "yuksek_portfoy": 0.285}
BIREYSEL_PAY = 0.80
COV_TGA = 0.82


def ozet():
    n = pd.read_csv(D / "npl_ham.csv", dtype={"Donem": str})

    def s(code, per):
        v = n[(n.Seri == code) & (n.Donem == per)].Deger
        return float(v.iloc[0]) / 1e6 if len(v) else float("nan")  # bin TL -> mr TL

    tga = {p: s("TP.HPBITABLO2.38", p) for p in ["2025-12", "2026-03", "2026-05", "2026-06", "2026-09"]}
    tuk = {p: s("TP.HPBITABLO6.50", p) for p in ["2025-12", "2026-03", "2026-05", "2026-06", "2026-09"]}
    out = {"EVDS_takipteki_toplam_mrTL": {k: round(v, 1) for k, v in tga.items()},
           "EVDS_takipteki_tuketici_mrTL": {k: round(v, 1) for k, v in tuk.items()}}

    # satış / brüt takip girişi: brüt giriş = Δstok + satış (satılanlar stoktan çıktığı için)
    g5 = tga["2026-05"] - tga["2025-12"] + SATIS_5A26
    gq2 = tga["2026-06"] - tga["2026-03"] + SATIS_Q2_26
    out["brut_takip_girisi_ve_satis_payi"] = {
        "Oca-May_2026": {"dStok": round(tga["2026-05"] - tga["2025-12"], 1), "satis": SATIS_5A26, "brut_giris": round(g5, 1), "satis_payi": round(SATIS_5A26 / g5, 3)},
        "Nis-Haz_2026": {"dStok": round(tga["2026-06"] - tga["2026-03"], 1), "satis": SATIS_Q2_26, "brut_giris": round(gq2, 1), "satis_payi": round(SATIS_Q2_26 / gq2, 3)},
        "not": "satış tutarı anapara varsayıldı; stok ile tanım farkı olabilir (faiz dahil/hariç)",
    }
    out["satis/takipteki_stok(yillik_hiz)"] = round(SATIS_5A26 * 12 / 5 / tga["2026-05"], 3)

    # satış-düzeltilmiş yük
    adj_total = tga["2026-06"] + VYS_PORTFOY
    kredi = 26182.7  # EVDS bankacılık sektörü bilançosu, Haz 2026, mr TL (bie_pbtop T18)
    out["satis_duzeltilmis_takip_orani"] = {
        "raporlanan(EVDS takipteki/krediler)": round(tga["2026-06"] / kredi, 4),
        "VYS_portfoyu_eklenince": round(adj_total / (kredi + VYS_PORTFOY), 4),
        "fark_puan": round((adj_total / (kredi + VYS_PORTFOY) - tga["2026-06"] / kredi) * 100, 2),
    }
    hane_vys = BIREYSEL_PAY * VYS_PORTFOY
    out["hane_yuku_mrTL"] = {"bankada_takipteki_tuketici_2026-06": round(tuk["2026-06"], 1), "VYS_devraldigi_hane_payi(%80 varsayim)": round(hane_vys, 1),
                             "toplam_gorunen_yuk": round(tuk["2026-06"] + hane_vys, 1),
                             "banka_raporlamasi_eksik_%": round(hane_vys / (tuk["2026-06"] + hane_vys) * 100, 1)}

    # fiyat ve defter etkisi
    net_defter = 1 - COV_TGA
    fiyat_rows = []
    for ad, p in FIYAT.items():
        fiyat_rows.append({"portfoy": ad, "fiyat_%anapara": round(p * 100, 1), "net_defter_%": round(net_defter * 100, 1),
                           "banka_ek_kar(+)/zarar(-)_puan": round((p - net_defter) * 100, 1),
                           "hane_borcu_kalan_%": 100.0, "VYS_iskonto_%": round((1 - p) * 100, 1)})
    out["fiyat"] = fiyat_rows
    out["yorum"] = [
        "Satış fiyatı anaparanın %12-16'sı. Ortalama TGA karşılığı (%82) alınırsa net defter %18 ve satış küçük bir zarar (-2..-5 puan) yazar; "
        "ama satılan havuzlar büyük olasılıkla eski ve neredeyse tamamen karşılanmış (DOĞRULANMADI), bu durumda satış bankaya KÂR yazar (karşılık iadesi). "
        "Her iki durumda hane borcu %100 olarak kalır ve VYŞ %85 iskontoyla aldığı alacağı tahsil etmeye çalışır.",
        "Bu kanal raporlanan takip oranını düşürür ve zararı bankanın dışına, VYŞ + hane arasına taşır; ölçülen 'sistemik yük' eksik sayılır.",
        "VYŞ portföyü (132 mr TL) takipteki stokun (EVDS, Haz 2026) yaklaşık %16'sı: kanal küçük ama hızlı büyüyor (yıllık +%67,7).",
    ]
    return out


if __name__ == "__main__":
    print(json.dumps(ozet(), ensure_ascii=False, indent=2))
