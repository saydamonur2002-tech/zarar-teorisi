"""L matrisinin çift kayda bağlanması.

ESKİ (akis_model.simulate): borçlunun zararı -x alacaklılara L ile geçer, borçlu (sahip olduğu tamponla) kendi payını emer; toplam = x (sıfır toplamlı
 transfer). Borçlu rahatlar.

YENİ (bu modül): temerrüt = iki ayrı defter olayı
   alacaklı defteri : t=0'da değer düşüklüğü  e0*P*L[j,i]   (e0 = karşılık/satış zararı; bankada tutulan cov, VYŞ'ye satılan 1-π)
                      banka sermayesini aşan kısım L[B,.] ile B'nin alacaklılarına geçer (λ_B(u), kalibre_lambda_rapor)
   borçlu defteri   : borç SİLİNMEZ; sonraki çeyreklerde gecikme faizi birikir  -I_j(t)   (hane/firma net değeri azalır)
   => sistem kaybı = alacaklı değer düşüklüğü + borçlu faiz birikimi (> eski toplam); borçlu rahatlamaz.
L_cift = e0 * L_kullanilan (satır toplamı e0 < 1; geri kalan = beklenen tahsilat) + ayrı vektör: borçlu yükü birikim hızı b_j.

Matris satırları: H -> banka-ağırlıklı (hane kredisi bankalardan; D payı SIFIR); F -> L_bil (gerçek dış borç kısıtlı); B, K, D -> L_v2.
H satırı: kredi enstrümanı %100 B; 'diğer' vb. diğer enstrümanlar Lm[...] satırından (D çıkarılıp yeniden normalize).
Parametreler: kalibre_lambda_rapor + temerrut_cift_kayit ile aynı (cov .82, π .15, satış payı .22, faiz = ihtiyaç faizi).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(__file__).parent
SEC = ["H", "F", "B", "K", "D"]
COV, PI, SOLD = 0.82, 0.15, 0.22
REC_LIFE = (PI + (1 - COV)) / 2  # ömür boyu tahsilat
E0 = COV * (1 - SOLD) + (1 - PI) * SOLD  # t=0'da alacaklı tarafın tanıdığı kayıp oranı
E_FREE = 1.236  # trilyon TL, yasal serbest sermaye (kalibre_lambda_rapor)
E_TOT = 4.530


def _rd(name):
    return pd.read_csv(D / name, index_col=0).reindex(index=SEC, columns=SEC)


def build_L():
    from akis_model import IDX, load, panel
    from kalibre_matris import INSTR, LOSS_INSTR
    stab, ftab, tcs, tcf = load()
    A, Y = panel(stab, tcs, "2026-Q1")
    names = list(INSTR)
    yh = np.array([Y[names.index(n), IDX["H"]] for n in LOSS_INSTR])
    w = yh / yh.sum()
    rowH = np.zeros(5)
    for wi, n in zip(w, LOSS_INSTR):
        if n == "kredi":
            r = np.array([0, 0, 1.0, 0, 0])  # hane kredisi: bankalar (varsayım; hane dış kredisi yok, D=0)
        else:
            r = _rd(f"Lm_{n}_2026-Q1.csv").loc["H"].to_numpy(float).copy()
            r[4] = 0.0
            r[0] = 0.0
            r = r / r.sum() if r.sum() > 0 else np.array([0, 0, 1.0, 0, 0])
        rowH += wi * r
    Lv2, Lbil = _rd("L_v2_2026-Q1.csv"), _rd("L_bil_2026-Q1.csv")
    L = Lv2.copy()
    L.loc["H"] = rowH
    L.loc["F"] = Lbil.loc["F"]
    return L, Lv2, {n: round(float(x), 3) for n, x in zip(LOSS_INSTR, w)}


def sim_eski(j, P, Lv2, lam=0.5):
    from akis_model import IDX, L_G, load, panel, simulate
    stab, ftab, tcs, tcf = load()
    A, Y = panel(stab, tcs, "2026-Q1")
    L, G = L_G(A, Y)
    nfp = np.array([stab.get(("H", "2026-Q1", 1), 0) + stab.get(("NPISH", "2026-Q1", 1), 0), stab[("F", "2026-Q1", 1)],
                    stab[("B", "2026-Q1", 1)] - tcs[("2026-Q1", 1)], stab[("K", "2026-Q1", 1)] + tcs[("2026-Q1", 1)], stab[("D", "2026-Q1", 1)]])
    x = np.zeros(5)
    x[IDX[j]] = -P * 1e9  # trilyon TL -> bin TL
    return dict(zip(SEC, (simulate(L, G, nfp, x, lam=lam) / 1e9).round(3).tolist()))


def sim_yeni(j, P, L, r_annual, horizon=8):
    rq = (1 + r_annual / 12) ** 3 - 1
    rec_q = REC_LIFE / 20
    out = {}
    I = 0.0
    shares = L.loc[j].to_numpy(float)
    loss0 = E0 * P * shares  # alacaklı sektörler, t=0
    # banka sermayesi aşımı
    iB = SEC.index("B")
    excess = max(0.0, loss0[iB] - E_FREE)
    spill = excess * L.loc["B"].to_numpy(float)
    spill[iB] = 0.0
    eff0 = -loss0.copy()
    eff0[iB] += excess  # banka serbest sermayeyi aşan kısmı dışarı taşır
    eff0 -= spill
    for t in range(0, horizon + 1):
        if t > 0:
            Pt = P * max(0.0, 1 - rec_q * t)
            I = I * (1 + rq) + rq * Pt
        eff = eff0.copy()
        eff[SEC.index(j)] -= I  # borçlunun gecikme faizi yükü
        if t in (0, 4, 8):
            out[f"t={t}"] = {s: round(float(v), 3) for s, v in zip(SEC, eff)} | {"toplam": round(float(eff.sum()), 3)}
    return out, {"t0_alacakli_kaybi_toplam": round(float(loss0.sum()), 3), "banka_sermaye_asimi": round(float(excess), 3)}


def ozet():
    f = pd.read_csv(D / "faiz_ham.csv", dtype={"Donem": str})
    r_annual = float(f[f.Seri == "TP.KTF10"].sort_values("Donem").Deger.iloc[-1]) / 100
    L, Lv2, w = build_L()
    Lc = (L * E0)
    for s in SEC:
        Lc.loc[s, s] = 0.0
    Lc.round(4).to_csv(D / "L_cift_2026-Q1.csv", encoding="utf-8-sig")
    L.round(4).to_csv(D / "L_baglanan_2026-Q1.csv", encoding="utf-8-sig")
    from hane_alt import ozet as hane_alt_ozeti
    ha = hane_alt_ozeti()
    row40 = next(r for r in ha["duyarlilik"] if abs(r["borc_payi_Ha"] - 0.40) < 1e-9)
    U_a = row40["odenemez_borc_tr"]  # trilyon TL
    N_q = 0.0623 * 4  # hane gözlenen brüt giriş, 4 çeyrek (trilyon TL)

    scen = {
        "A_hane_Ha_odenemez_borc_taninir": ("H", U_a),
        "B_hane_gozlenen_4_ceyrek_giris": ("H", N_q),
        "C_firma_1_trilyon_temerrut": ("F", 1.0),
    }
    sonuc = {}
    for ad, (j, P) in scen.items():
        yeni, ek = sim_yeni(j, P, L, r_annual)
        sonuc[ad] = {"borclu": j, "anapara_trilyonTL": round(P, 3),
                     "ESKI_transfer_lam0.5": sim_eski(j, P, Lv2),
                     "YENI_cift_kayit": yeni, **ek}
    out = {
        "parametreler": {"e0_alacakli_kayip_orani": round(E0, 4), "beklenen_tahsilat": round(REC_LIFE, 3), "gecikme_faizi_yillik_%": round(r_annual * 100, 1),
                         "serbest_sermaye_trilyonTL": E_FREE, "satis_payi": SOLD},
        "H_satiri_agirliklari_yukumluluk_enstruman": w,
        "H_satiri_eski_v2": {k: round(float(v), 3) for k, v in Lv2.loc["H"].items()},
        "H_satiri_yeni": {k: round(float(v), 3) for k, v in L.loc["H"].items()},
        "F_satiri_eski_v2": {k: round(float(v), 3) for k, v in Lv2.loc["F"].items()},
        "F_satiri_yeni(L_bil)": {k: round(float(v), 3) for k, v in L.loc["F"].items()},
        "senaryolar": sonuc,
        "yorum": [
            "Eski modelde borçlu (özellikle net alacaklı H) zararı kendi tamponuyla emiyor görünür; yeni modelde alacaklı t=0'da kaybı tanır, borçlu rahatlamaz ve faiz yükü birikir.",
            "Eski H satırı borcun ~%28'ini D'ye yazıyordu (hane dış kredisi yok); yeni satır bankaya dayalı, D=0.",
            "Birikmiş faiz yükü varsayıma bağlıdır (gecikme faizi=ihtiyaç faizi, kısmi ödeme yok); alacaklı kaybı ise gözlenen karşılık ve satış fiyatına dayanır.",
        ],
    }
    return out


if __name__ == "__main__":
    print(json.dumps(ozet(), ensure_ascii=False, indent=2))
