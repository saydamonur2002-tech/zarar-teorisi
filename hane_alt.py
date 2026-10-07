"""Hane haznesinin alt bölünmesi: asgari ücretli (Ha), memur (Hm), diğer (Ho). Borç asgariye yakın varsayılır.

KULLANICI VARSAYIMI: H'nin borcunun payı Ha'da yoğunlaşır (taban %70). Bu ÖLÇÜM değil varsayımdır; modül bunun
taşınabilirliğini ayrıca sınar (kapasite + gözlenen stresle çapraz kontrol) ve duyarlılık verir.

Varsayımlar
  borç payları (Ha, Hm, Ho): taban (0.70, 0.10, 0.20); varlık/mevduat payları (0.05, 0.15, 0.80) (mevduat yoğunluğu: ~2,7 milyon kişi
  ve ≥1 milyon TL hesaplar toplam mevduatın çoğunu tutuyor, BDDK/haber, Eyl 2025; kesin pay yok)
  gelir: asgari net 28.075,50; memur bekâr kök ~66.188 (benim hesabım); kişi sayısı: asgari ~6,85 milyon, memur 3,67 milyon
  taşıma kapasitesi: taksit/gelir <= %30, 36 ay eşit taksit, faiz EVDS ihtiyaç kredisi (akım) son gözlem (KKDF/BSMV hariç)
  bireysel gelir ve bireysel borç (hane = 1 gelirli kişi) varsayımı; çok gelirli haneler kapasiteyi artırır.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(__file__).parent
ASGARI, MEMUR = 28075.50, 66188.0
N_A, N_M = 6.85e6, 3.67e6
DTI, VADE = 0.30, 36
COV_TGA, COV_YI = 0.82, 0.1407
YI, HANE_PAY_LOW, HANE_PAY_HIGH = 2624.0, 0.456, 0.80  # mr TL; YI'da hane payı: BDDK TGA payı .. üst varsayım
D_A_BASE = 0.40  # Ha'nın hane borcundaki taban payı (ilk varsayım %70'ti; gözlenen stresle uyumlu aralığın üstündeydi, bkz. ima_edilen_Ha_borc_payi_ust_siniri)


def taksit_faktor(rate_pct, n=VADE):
    i = rate_pct / 100 / 12
    return i / (1 - (1 + i) ** -n)


def _shares(d_a):
    rest = 1 - d_a
    return np.array([d_a, rest / 3, 2 * rest / 3])  # kalan borç: Hm:Ho = 1:2


def ozet():
    from akis_model import IDX, load, panel
    stab, ftab, tcs, tcf = load()
    A, Y = panel(stab, tcs, "2026-Q1")
    iH = IDX["H"]
    assets = A[:, iH].sum() / 1e9
    liab = Y[:, iH].sum() / 1e9  # trilyon TL

    f = pd.read_csv(D / "faiz_ham.csv", dtype={"Donem": str})
    rate = float(f[f.Seri == "TP.KTF10"].sort_values("Donem").Deger.iloc[-1])
    fac = taksit_faktor(rate)
    cap_a = DTI * ASGARI / fac * N_A / 1e12  # trilyon TL
    cap_m = DTI * MEMUR / fac * N_M / 1e12

    npl = pd.read_csv(D / "npl_ham.csv", dtype={"Donem": str})
    tga = float(npl[(npl.Seri == "TP.HPBITABLO6.50") & (npl.Donem == "2026-09")].Deger.iloc[0]) / 1e9
    S_low = tga
    S_high = tga + HANE_PAY_HIGH * YI / 1000
    S_mid = tga + 0.5 * (HANE_PAY_LOW + HANE_PAY_HIGH) / 2 * YI / 1000  # ~ orta

    # taban senaryo: NFP bölünmesi
    a_sh = np.array([0.05, 0.15, 0.80])
    base = _shares(D_A_BASE)
    nfp = a_sh * assets - base * liab
    tab = pd.DataFrame({"grup": ["Ha asgari", "Hm memur", "Ho diğer"], "varlik_tr": a_sh * assets, "borc_tr": base * liab, "NFP_tr": nfp})
    tab.round(3).to_csv(D / "hane_alt_nfp.csv", index=False, encoding="utf-8-sig")

    # kapasite ve ödenemez borç (taban ve duyarlılık)
    fl = pd.read_csv(D / "kalibre_lambda_rapor_ozeti.json".replace(".json", ".json")) if False else None
    lam = json.loads((D / "kalibre_lambda_rapor_ozeti.json").read_text(encoding="utf-8"))
    E_free = lam["yasal_sermaye"]["serbest_sermaye_milyarTL"] / 1000
    E_tot = lam["EVDS_milyarTL"]["ozkaynak"] / 1000
    sens = []
    for d_a in (0.18, 0.30, D_A_BASE, 0.47, 0.70, 0.90):
        debt_a = d_a * liab
        unserv = max(0.0, debt_a - cap_a)
        loss = unserv * (COV_TGA - COV_YI)  # tamamı tanınırsa ek karşılık (trilyon TL)
        u = loss / E_free
        sens.append({
            "borc_payi_Ha": d_a,
            "Ha_borcu_tr": round(debt_a, 2),
            "kisi_basi_borc_bin_TL": round(debt_a * 1e12 / N_A / 1e3),
            "borc/yillik_gelir": round(debt_a * 1e12 / N_A / (ASGARI * 12), 2),
            "yillik_faiz/yillik_gelir": round(debt_a * 1e12 / N_A * rate / 100 / (ASGARI * 12), 2),
            "Ha_kapasitesi_tr": round(cap_a, 2),
            "odenemez_borc_tr": round(unserv, 2),
            "tanınırsa_ek_karsilik_tr": round(loss, 2),
            "ek_karsilik/ozkaynak": round(loss / E_tot, 2),
            "u_yasal_sermaye": round(u, 2),
            "lambda_B": round(max(0.0, 1 - 1 / u), 2) if u > 0 else 0.0,
        })

    # gözlenen stresten ima edilen üst sınır: ödenemez borç ≈ gözlenen stres (tüm stres Ha'da varsayımıyla)
    imp = {k: round((cap_a + S) / liab, 2) for k, S in (("stres_alt(sadece takipteki)", S_low), ("stres_orta", S_mid), ("stres_ust(takipteki+hane payı yakın izleme)", S_high))}

    out = {
        "varsayim": f"Kullanıcı: hane borcu asgariye yakın. Taban Ha borç payı %{D_A_BASE*100:.0f}; varlık payı %5 (mevduat yoğunluğu). Ölçüm değil.",
        "H_toplam_2026Q1_trilyonTL": {"varlik": round(assets, 2), "borc": round(liab, 2), "NFP": round(assets - liab, 2)},
        "taban_NFP_trilyonTL": {r.grup: {"varlik": round(r.varlik_tr, 2), "borc": round(r.borc_tr, 2), "NFP": round(r.NFP_tr, 2)} for r in tab.itertuples()},
        "faiz_ihtiyac_%": round(rate, 2),
        "tasima_kapasitesi_trilyonTL": {"Ha_asgari": round(cap_a, 2), "Hm_memur": round(cap_m, 2), "dayanak": f"taksit/gelir<=%{DTI*100:.0f}, {VADE} ay"},
        "kapasite_kisi_basi_bin_TL": {"Ha": round(DTI * ASGARI / fac / 1e3), "Hm": round(DTI * MEMUR / fac / 1e3)},
        "gozlenen_hane_stresi_trilyonTL": {"takipteki_tuketici_2026-09": round(S_low, 3), "ust(takipteki+yakin_izleme_hane_payi)": round(S_high, 2)},
        "ima_edilen_Ha_borc_payi_ust_siniri": imp,
        "duyarlilik": sens,
        "yorum": [
            "Yüksek Ha payı (%70 gibi), kişi başı borcu yıllık gelirin birkaç katına çıkarır; yalnız 1 gelirli kişi varsayımıyla taşınamaz. "
            "Böyle bir pay ancak (a) çok gelirli haneler, (b) borcu borçla çevirme (kart rotatifi, yapılandırma) ya da (c) gizli temerrüt ile tutarlı olabilir.",
            "Gözlenen stresle çapraz kontrol: tüm stres Ha'da olsa bile ima edilen Ha borç payı en çok ~%17-44 (ima_edilen_Ha_borc_payi_ust_siniri). "
            "Bunun üstündeki pay, ödenemeyen borcun henüz stres olarak görünmediği (borçla çevirme/yapılandırma) anlamına gelir = gizli kırılganlık (yük stoku).",
            "Temerrüt sıfır toplamlı transfer değildir: banka karşılık ayırır, hane borcu silinmez (bireysel iflas/borçtan kurtulma yok, DOĞRULANMADI). Sistem net kayıp.",
        ],
    }
    return out


if __name__ == "__main__":
    print(json.dumps(ozet(), ensure_ascii=False, indent=2))
