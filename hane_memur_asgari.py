"""Hane haznesinin memur / asgari ücretli ayrımı: borç taşıma kapasitesi (gelir tarafı).

Girdiler (haber/kaynak derlemesi, resmî tabloyla doğrulanmadı; birim TL/ay):
  asgari ücret net 2026: 28.075,50 (2026 boyunca ara zam bulunamadı)
  en düşük memur maaşı Temmuz 2026: 70.251 (Ocak-Haziran 61.890; evli+çocuklu, aile yardımı dahil); bekâr kök maaş Ocak-Haz 58.305
  Türk-İş Eylül 2026: açlık sınırı 37.801 (4 kişilik, yalnız gıda); yoksulluk sınırı 123.130 (4 kişilik); bekâr yaşama maliyeti 48.884,82
  grup büyüklüğü: asgari ücretli ~6,8-6,9 milyon (SGK 4/a'nın ~%40'ı, 2023-25); memur (4/c) 3,67 milyon (SGK Ocak 2026), kadrolu 3,58 milyon (Haz 2026)
Faiz: EVDS TP.KTF10 (ihtiyaç kredisi, TL, akım, % yıllık).
Kapasite = net gelir - zorunlu harcama; kredi taksidi: aylık bileşik, eşit taksit (KKDF/BSMV ve sigorta hariç -> taksit alt sınır).
"""
import json

import numpy as np
import pandas as pd

d = pd.read_csv("faiz_ham.csv", dtype={"Donem": str})
f = d[d.Seri == "TP.KTF10"].sort_values("Donem")
r_son = float(f.Deger.iloc[-1])
r_don = f.Donem.iloc[-1]
r_ort12 = float(f.Deger.tail(12).mean())
print(f"İhtiyaç kredisi faizi (akım): son {r_don} = %{r_son:.2f} ; son 12 ay ort. %{r_ort12:.2f}")

ASGARI = 28075.50
MEMUR_ALT = 70251.0                    # en düşük memur, Temmuz (aile yardımı dahil)
MEMUR_BEKAR = round(58305 * 1.1352)    # bekâr kök maaşa Temmuz zammı (BENİM HESABIM)
ACLIK_4 = 37801.0
YOKSUL_4 = 123130.0
BEKAR_YASAM = 48884.82


def taksit(P, annual_pct, n):
    i = annual_pct / 100 / 12
    return P * i / (1 - (1 + i) ** -n)


rows = []
for ad, gelir in [("Asgari ücretli (net)", ASGARI), ("Memur, bekâr kök (hesap)", MEMUR_BEKAR), ("En düşük memur (aile yardımlı)", MEMUR_ALT)]:
    r = {"grup": ad, "net_gelir": round(gelir),
         "gelir/bekar_yasam_maliyeti": round(gelir / BEKAR_YASAM, 2),
         "gelir/acliksiniri_4kisi": round(gelir / ACLIK_4, 2),
         "gelir/yoksulluksiniri_4kisi": round(gelir / YOKSUL_4, 2),
         "kapasite_bekar_TL(gelir-yasam)": round(gelir - BEKAR_YASAM),
         "kapasite_4kisi_TL(gelir-aclik)": round(gelir - ACLIK_4)}
    for P in (50000, 100000, 250000):
        t = taksit(P, r_son, 36)
        r[f"taksit_{P//1000}bin_36ay"] = round(t)
        r[f"taksit/gelir_{P//1000}bin"] = round(t / gelir, 3)
    rows.append(r)
T = pd.DataFrame(rows)
pd.set_option("display.width", 250, "display.max_columns", 30)
print(T.T.to_string())

# gelir oranı ve toplam büyüklük
out = {
    "faiz": {"donem": r_don, "ihtiyac_%": round(r_son, 2), "son12ay_ort_%": round(r_ort12, 2)},
    "memur/asgari": {"Ocak-Haz (61.890/28.075)": round(61890 / ASGARI, 2), "Temmuz (70.251/28.075)": round(MEMUR_ALT / ASGARI, 2)},
    "grup_buyuklugu_milyon": {"asgari_4a_yaklasik": 6.85, "memur_4c_SGK_Ocak26": 3.67, "kadrolu_Haz26": 3.58},
    "tablo": rows,
    "uyari": "Gelir ve maliyet rakamları haber/sendika derlemesi; memur bekâr rakamı benim hesabım; ücretle çalışanın tek gelirli olduğu varsayımı; hane geliri yerine bireysel gelir.",
}
open("hane_memur_asgari_ozeti.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
