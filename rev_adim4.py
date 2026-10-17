"""Revizyon F — Adım 4: (1) VF.2 ZP8 ile gerçek kişi YP mevduat çift sayımı; (2) gözlenen ihraççı/elinde tutan dağılımı
(EVDS Menkul Kıymet haftalık, DİBS piyasa değeri, ESA sektörleri); (3) 0,08 mevduat→kredi katsayısının kalibrasyonu (para-banka T18/V01).
Kaynaklar: /workspace/aktarim_matrisi/evds/evds_b_para_banka_aylik.csv, evds_c_menkul_kiymet_haftalik.csv, adim4_adres_yonlendirme_sonuc.json.
"""
import json, csv
from pathlib import Path
import numpy as np, pandas as pd
KOK = Path(__file__).resolve().parent; EV = Path("/workspace/aktarim_matrisi/evds")

def pb():
    d = pd.read_csv(EV / "evds_b_para_banka_aylik.csv", usecols=["Donem", "Seri", "Deger"])
    return d.pivot_table(index="Donem", columns="Seri", values="Deger", aggfunc="last") / 1e6  # bin TL → milyar TL

def main():
    a4 = json.loads((KOK / "adim4_adres_yonlendirme_sonuc.json").read_text(encoding="utf-8"))
    A = {x["nesne"]: x["milyar"] for x in a4["adresler"]}
    h_vadeli, f_vadeli, h_yp = A["hane vadeli mevduat (VF.2 ZP8)"], A["firma vadeli mevduat (VF.2 ZP8)"], A["gerçek kişi YP mevduat (HPB tablo 2)"]
    p = pb(); m = p.loc["2026-03"]
    tl_hane = m["TP.KM.E041"] + m["TP.KB.FON033"]  # banka tasarruf (gerçek kişi TL) + katılım hane TL; vadesiz dahil
    ortusme_alt = max(0.0, h_vadeli - tl_hane)  # ZP8 TL vadeliden büyükse fark yalnız YP olabilir → kanıt alt sınır
    ortusme_ust = min(h_yp, h_vadeli)
    toplam = a4["adres_toplam_milyar"]
    cift = {"H_VF2_ZP8": h_vadeli, "hane_TL_tum_mevduat_2026_03": round(tl_hane, 1), "YP_gercek_kisi": h_yp,
            "ortusme_alt": round(ortusme_alt, 1), "ortusme_ust": round(ortusme_ust, 1),
            "adres_toplam_eski": toplam, "adres_toplam_yeni_bandi": [round(h_vadeli + f_vadeli, 1), round(toplam - ortusme_alt, 1)],
            "onerilen": round(h_vadeli + f_vadeli, 1),
            "etiket": "kanıt (alt sınır: ZP8 > tüm hane TL mevduatı → ZP8 YP içerir); üst sınır mantıksal"}
    # (2) DİBS elinde tutanlar
    c = pd.read_csv(EV / "evds_c_menkul_kiymet_haftalik.csv", usecols=["Donem", "Seri", "Deger"])
    c["t"] = pd.to_datetime(c.Donem, format="%d-%m-%Y", errors="coerce")
    def pay(t):
        x = c[(c.t == t) & c.Seri.str.startswith("TP.DIBSPIYDEG.")].set_index("Seri").Deger
        tot = x["TP.DIBSPIYDEG.ST"]
        return {k: round(float(x[f"TP.DIBSPIYDEG.{k}"]) / tot, 4) for k in ("S11", "S121", "S122", "S1234", "S128", "S129", "S13", "S14", "S2")} | {"toplam_milyar": round(float(tot) / 1000, 1)}
    ts = sorted(c[c.Seri == "TP.DIBSPIYDEG.ST"].t.dropna().unique())
    t_q1 = max(t for t in ts if t <= pd.Timestamp("2026-03-31")); t_son = ts[-1]
    dibs = {"2026-Q1_hafta": str(pd.Timestamp(t_q1).date()), "paylar_q1": pay(t_q1), "son_hafta": str(pd.Timestamp(t_son).date()), "paylar_son": pay(t_son),
            "etiket": "kanıt (EVDS Menkul Kıymet, piyasa değeri; ihraççı Hazine=K′)"}
    # (3) 0,08 kalibrasyonu: çeyreklik Δkredi ~ Δmevduat (nominal, milyar TL) ve büyüme oranlarıyla
    q = p[["TP.TOP.T18", "TP.TOP.V01"]].dropna(); q = q[q.index.str[5:7].isin(["03", "06", "09", "12"])]
    sonuc_k = {}
    for ad, bas in (("2011-2026", "2011"), ("2018-2026", "2018"), ("2022-2026", "2022")):
        z = q[q.index >= bas]; dK, dM = z["TP.TOP.T18"].diff().dropna(), z["TP.TOP.V01"].diff().dropna()
        b_lvl = float(np.polyfit(dM, dK, 1)[0])
        gK, gM = np.log(z["TP.TOP.T18"]).diff().dropna(), np.log(z["TP.TOP.V01"]).diff().dropna()
        b_log = float(np.polyfit(gM, gK, 1)[0]); ldr = float((z["TP.TOP.T18"] / z["TP.TOP.V01"]).mean())
        sonuc_k[ad] = {"dK_dM_egimi": round(b_lvl, 3), "log_esneklik": round(b_log, 3), "kredi_mevduat_orani": round(ldr, 3)}
    kal = {"eski": 0.08, "donemler": sonuc_k,
                  "bant": [0.08,
                    max(v["dK_dM_egimi"] for v in sonuc_k.values())],
           "etiket": "aday: tarihsel eş-hareket nedensellik değil (ikisi de kurla/enflasyonla büyür); 0,08 alt uç (tam ikame), üst uç ölçülen eğim (ikame yok)"}
    s = {"faz": "rev F", "cift_sayim": cift, "dibs_elinde_tutan": dibs, "kredi_katsayisi": kal}
    (KOK / "rev_adim4_sonuc.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(s, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
