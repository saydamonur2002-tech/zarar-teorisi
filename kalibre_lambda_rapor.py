"""λ'nın durum bağımlı kalibrasyonu: bekleyen zarar cebi (II. Grup / yapılandırılmış) vs banka özkaynağı.

Neden bu yöntem: kalibre_lambda.py zaman serisi regresyonunda F'nin değerleme zararı -> provizyon geçişini ayırt edemedi
(θ <= ~%1,4). Eylül 2026 "dondurma" raporu nedenini veriyor: zarar TANINMIYOR, yakın izlemede (II. Grup) bekliyor ve
karşılığı düşük. Bu yüzden geçiş, gerçekleşen zarar yerine "tanınma" olayına bağlanır:

  bekleyen zarar cebi  P = Σ_k stok_k * (karşılık_hedef - karşılık_k)       (II. Grup, yapılandırılmış)
  senaryo s            = P'nin tanınan payı (II. Grup -> TGA geçişi)
  u                    = s*P / E_B   (E_B = banka özkaynağı)
  λ_B(u)               = max(0, 1 - 1/u)   (özkaynağı aşan kısım ileri geçer)

Rapor girdileri (Eylül 2026 raporu, çalışma kitabı: Veri/Banka_Defteri): TBB/BDDK Haziran 2026.
  II. Grup stoku 2.624 mr TL (+%59 yıllık, toplam kredi +%36); yapılandırılmış 1.446 mr TL, bunun 1.361'i II. Grup'ta;
  karşılık: II. Grup %12, yapılandırılmış %16, TGA %82; TGA stoku 818,5 mr TL (BDDK 2026/7);
  takipteki stokun %46'sı bireysel (hane), %54 ticari.
EVDS girdileri: Bankacılık Sektörü Bilançosu (bie_pbtop): özkaynaklar V28, krediler T18, toplam varlık T41, mevduat V01.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(__file__).parent

# ---- rapor girdileri (milyar TL)
YI = 2624.0
YAP_IN_YI = 1361.0
YI_RESTR = YAP_IN_YI
YI_PLAIN = YI - YAP_IN_YI
COV_YI, COV_YAP, COV_TGA = 0.12, 0.16, 0.82
TGA = 818.5
HANE_PAY = 0.456  # takipteki stokta bireysel pay (BDDK 2026/7)


def evds_pbtop(code, month):
    d = pd.read_csv(D / "npl_ham.csv", dtype={"Donem": str})
    v = d[(d.Grup == "bie_pbtop") & (d.Seri == code) & (d.Donem == month)].Deger
    return float(v.iloc[0]) / 1e6 if len(v) else np.nan  # bin TL -> milyar TL


def main():
    month = "2026-06"
    E = evds_pbtop("TP.TOP.V28", month)
    loans = evds_pbtop("TP.TOP.T18", month)
    assets = evds_pbtop("TP.TOP.T41", month)
    dep = evds_pbtop("TP.TOP.V01", month)
    out = {"ay": month, "EVDS_milyarTL": {"ozkaynak": round(E, 1), "krediler": round(loans, 1), "toplam_varlik": round(assets, 1), "mevduat": round(dep, 1)}}

    # tutarlılık kontrolleri
    blended = (YI_PLAIN * COV_YI + YI_RESTR * COV_YAP) / YI
    out["kontroller"] = {
        "YI_harmanlanmis_karsilik_orani": round(blended, 4),
        "rapor_beklenen": "~%14 (2023: %32 -> 2026: %14)",
        "YI/kredi(EVDS)": round(YI / loans, 3),
        "rapor": "toplam kredilerin ~%10'u",
        "TGA/kredi(EVDS)": round(TGA / loans, 4),
        "rapor": "TGA oranı %2,7-2,9",
        "ozkaynak/varlik": round(E / assets, 4),
    }

    # bekleyen zarar cebi
    P_plain = YI_PLAIN * (COV_TGA - COV_YI)
    P_restr = YI_RESTR * (COV_TGA - COV_YAP)
    P = P_plain + P_restr
    out["bekleyen_zarar_cebi_milyarTL"] = {"II_Grup_yapilandirilmamis": round(P_plain, 1), "yapilandirilmis": round(P_restr, 1), "toplam": round(P, 1),
                                           "ozkaynak_orani": round(P / E, 3), "yorum": "II. Grup tamamen TGA'ya geçerse (karşılık %82'ye çıkarsa) ek karşılık ihtiyacı"}
    out["kritik_tanima_orani_s*"] = round(E / P, 3)  # u=1 olduğu pay

    # senaryo tablosu
    rows = []
    L = pd.read_csv(D / "matris_v2_zaman_serisi.csv", dtype={"Donem": str})
    LB = L[(L.Donem == "2026-Q1") & (L.Kaynak == "B")].iloc[0]
    sh = {s: float(LB[f"L_{s}"]) for s in ["H", "F", "B", "K", "D"]}
    out["L_B_satiri_2026Q1"] = {k: round(v, 3) for k, v in sh.items()}
    # Yasal sermaye eşiği: SYR (sermaye yeterlilik) %16,5 [önceki girdi tablosu, BDDK; bu oturumda yeniden doğrulanmadı]
    # RWA ≈ özkaynak / SYR; asgari gereklilik k*RWA (k=%12 varsayım: %8 asgari + %2,5 koruma + ~%1,5 sistemik). Bu eşiği
    # aşan zarar bankayı iflasa değil KREDİ DARALTMAYA iter (spillover F ve H'ye).
    CAR, K_MIN = 0.165, 0.12
    rwa = E / CAR
    E_free = E - K_MIN * rwa
    out["yasal_sermaye"] = {"SYR_varsayim": CAR, "asgari_oran_varsayim": K_MIN, "RWA_milyarTL": round(rwa, 0),
                            "serbest_sermaye_milyarTL": round(E_free, 0), "serbest/ozkaynak": round(E_free / E, 3),
                            "pocket/serbest_sermaye": round(P / E_free, 3), "kritik_tanima_orani_s*_yasal": round(E_free / P, 3),
                            "uyari": "SYR, k ve özkaynak≈yasal sermaye varsayımları. Sektör toplamı; tek tek bankalar (özellikle yüksek YI payı olanlar) daha önce aşabilir."}
    for s in [0.05, 0.10, 0.20, 0.35, 0.50, 0.75, 1.0]:
        loss = s * P
        u = loss / E
        u_reg = loss / E_free
        lam = max(0.0, 1 - 1 / u) if u > 0 else 0.0
        lam_reg = max(0.0, 1 - 1 / u_reg) if u_reg > 0 else 0.0
        excess = max(0.0, loss - E)
        excess_reg = max(0.0, loss - E_free)
        rows.append({
            "tanima_orani_s": s,
            "ek_zarar_milyarTL": round(loss, 1),
            "ozkaynak": {"u": round(u, 3), "lambda_B": round(lam, 3), "asan_milyarTL": round(excess, 1)},
            "yasal_sermaye": {"u": round(u_reg, 3), "lambda_B": round(lam_reg, 3), "asan_milyarTL": round(excess_reg, 1),
                              "asan_L_B_ile(H,F,K,D)_milyarTL": {k: round(excess_reg * v, 1) for k, v in sh.items() if k != "B"}},
        })
    out["senaryolar"] = rows

    # hane / firma ayrımı (TGA payı varsayımı)
    out["kaynak_ayrimi_varsayim"] = {"hane_payi": HANE_PAY, "ticari_payi": round(1 - HANE_PAY, 3),
                                     "kaynak": "BDDK 2026/7 takipteki stok payı; YI için kırılım yayımlanmıyor (rapor sınırı), FİR yakın izleme artışını bireysele bağlıyor",
                                     "uyari": "YI'daki hane payı muhtemelen daha yüksek; u'nun H/F ayrımına duyarlılığı için hane payı 0,46-0,80 alın"}

    # F'nin değerleme zararı ile ilişki (nedensellik değil, büyüklük kıyası): son 4 çeyrek
    P_ = pd.read_csv(D / "temiz_stok_akis_paneli.csv", dtype={"Donem": str})
    g = P_[(P_.Hazne == "F") & (P_.Enstruman != "altin_sdr")]
    rf = (g[g.Taraf == "varlik"].groupby("Donem").Degerleme_veya_Degisim.sum() - g[g.Taraf == "yukumluluk"].groupby("Donem").Degerleme_veya_Degisim.sum()) / 1e9
    last4 = rf.loc["2025-Q2":"2026-Q1"]
    out["F_degerleme_son4ceyrek_trilyonTL"] = {k: round(float(v), 3) for k, v in last4.items()}
    out["F_degerleme_son4_toplam_trilyonTL"] = round(float(last4.sum()), 3)
    dYI = YI - YI / 1.59
    out["YI_artisi_son12ay_milyarTL"] = round(dYI, 1)
    out["YI_artisi/F_son4_zarar(kiyas)"] = round(dYI / 1000 / abs(float(last4.sum())), 3)
    out["kiyas_notu"] = "büyüklük kıyasıdır, nedensellik değil; YI artışı hane kaynaklı ağırlıklı (FİR)"

    (D / "kalibre_lambda_rapor_ozeti.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
