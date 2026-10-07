"""Bütçe kanalı entegrasyonu + geriye dönük testler.

Çıktılar: butce_aktarim_ceyreklik.csv, K_kanal_paylari_2026-Q1.csv, geri_test_ozeti.json
Testler:
  T1  Bütçe-finansal uyum: bütçe dengesi ile K' net işlem akışı (NL_K') ilişkisi.
  T2  Matris geriye dönük testi (kimliği ölçümden bağımsız): borçlu sektörlerin yükümlülük değerlemesinden
      Lm ile alacaklı değerlemesi öngörülür, sektör net değerlemesi R ile karşılaştırılır; iki kıyas ölçütüyle.
  T3  λ/κ tanımlanabilirliği: bir sektörün değerleme zararının sonraki çeyrekte ikinci tur etkisi (OLS).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from akis_model import IDX, SEC, load, mat, panel
from kalibre_matris import INSTR
import butce_kanali as bk

DIR = Path(__file__).parent
NAMES = list(INSTR)


def main():
    out = {}
    stab, ftab, tcs, tcf = load()
    P = pd.read_csv(DIR / "temiz_stok_akis_paneli.csv", dtype={"Donem": str})
    qs = sorted(P.Donem.unique())

    # ---- K bütçe kanalı
    q = bk.load()
    shares = {}
    for p in q.index:
        if p not in qs:
            continue
        prev = "2014-Q4" if p == "2015-Q1" else qs[qs.index(p) - 1]
        A, Y = panel(stab, tcs, prev)
        k = NAMES.index("borclanma_senedi")
        shares[p] = bk.tcmb_share_dom_interest(mat(A, Y, ["borclanma_senedi"])[IDX["K"]])
    common = [p for p in q.index if p in shares]
    qq = q.loc[common]
    Phi = bk.build(qq, None) if False else pd.concat(
        [bk.build(qq.loc[[p]], shares[p]) for p in common], ignore_index=True
    )
    Phi.to_csv(DIR / "butce_aktarim_ceyreklik.csv", index=False, encoding="utf-8-sig")

    # K kanal payları (2026-Q1'e en yakın dolu çeyrek, son 4 çeyrek toplamı)
    last4 = Phi.tail(4)
    inflow = {s: last4[f"odeme_{s}_to_K"].sum() for s in ("H", "F")}
    outflow = {s: last4[f"odeme_K_to_{s}"].sum() for s in ("H", "F", "B", "D")}
    tot_in, tot_out = sum(inflow.values()), sum(outflow.values())
    kk = pd.DataFrame({
        "K_gelir_kaynagi_payi(K kazanc -> kim oder)": pd.Series({s: inflow[s] / tot_in for s in inflow}),
        "K_harcama_alicisi_payi(K zarar -> kim kazanir)": pd.Series({s: outflow[s] / tot_out for s in outflow}),
    })
    kk.to_csv(DIR / "K_kanal_paylari_son4ceyrek.csv", encoding="utf-8-sig")
    out["K_kanal_son4ceyrek_donemler"] = list(last4.Donem)
    out["K_gelir_kaynagi_payi"] = {s: round(inflow[s] / tot_in, 3) for s in inflow}
    out["K_harcama_alici_payi"] = {s: round(outflow[s] / tot_out, 3) for s in outflow}
    out["K_son4ceyrek_toplam_trilyonTL"] = {"gelir": round(tot_in / 1e9, 2), "harcama(ozel kesime)": round(tot_out / 1e9, 2),
                                            "faiz": round(last4.ic_faiz.sum() / 1e9 + last4.dis_faiz.sum() / 1e9, 2)}

    # ---- T1: bütçe dengesi vs NL_K'
    f = P[(P.Hazne == "K") & P.Islem.notna()]
    nlK = (f[f.Taraf == "varlik"].groupby("Donem").Islem.sum() - f[f.Taraf == "yukumluluk"].groupby("Donem").Islem.sum())
    bal = Phi.set_index("Donem").butce_dengesi
    j = pd.concat([nlK.rename("NL_Kprime"), bal], axis=1).dropna()
    out["T1_butce_vs_NLK"] = {
        "n": int(len(j)),
        "korelasyon_seviye": round(float(j.corr().iloc[0, 1]), 3),
        "korelasyon_fark": round(float(j.diff().dropna().corr().iloc[0, 1]), 3),
        "ortalama_oran_NL/butce": round(float((j.NL_Kprime / j.butce_dengesi).replace([np.inf, -np.inf], np.nan).median()), 3),
    }

    # ---- T2: matris geriye dönük testi (altın/SDR hariç)
    inst = [n for n in NAMES if n != "altin_sdr"]
    pred, obs = [], []
    rec = []
    for idx, p in enumerate(qs):
        prev = "2014-Q4" if p == "2015-Q1" else qs[idx - 1]
        A, Y = panel(stab, tcs, prev)
        Rp = P[P.Donem == p]
        ry = np.zeros((len(inst), 5))
        ra = np.zeros((len(inst), 5))
        for m_, n in enumerate(inst):
            sub = Rp[(Rp.Enstruman == n) & Rp.Hazne.isin(SEC)]
            for s in SEC:
                ry[m_, IDX[s]] = sub[(sub.Hazne == s) & (sub.Taraf == "yukumluluk")].Degerleme_veya_Degisim.iloc[0]
                ra[m_, IDX[s]] = sub[(sub.Hazne == s) & (sub.Taraf == "varlik")].Degerleme_veya_Degisim.iloc[0]
        r_obs = (ra - ry).sum(axis=0)  # sektör net değerleme
        r_pred = np.zeros(5)
        naive_uniform = np.zeros(5)
        for m_, n in enumerate(inst):
            Lm = mat(A, Y, [n])
            gains = ry[m_] @ Lm  # alacaklı değerleme kazancı (borçlu j zararı -> alacaklılar)
            r_pred += gains - ry[m_]
            # kıyas: alacaklı varlık payı (satır toplamı değil, enstrüman toplam varlık payına göre)
            w = A[list(INSTR).index(n)] / max(A[list(INSTR).index(n)].sum(), 1e-9)
            naive_uniform += ry[m_].sum() * w - ry[m_]
        rec.append((p, r_obs, r_pred, naive_uniform))
        obs.append(r_obs)
        pred.append(r_pred)
    obs, pred = np.array(obs) / 1e9, np.array(pred) / 1e9
    nu = np.array([x[3] for x in rec]) / 1e9
    zero = -np.array([[0] * 5] * len(rec))

    def r2(o, p_):
        ss = ((o - o.mean()) ** 2).sum()
        return float(1 - ((o - p_) ** 2).sum() / ss)

    out["T2_matris_testi"] = {
        "n_ceyrek": len(rec),
        "R2_Lm_modeli(havuz)": round(r2(obs, pred), 3),
        "R2_kiyas_toplam_varlik_payi": round(r2(obs, nu), 3),
        "R2_kiyas_transfer_yok": None,
        "sektor_bazli_korelasyon": {s: round(float(np.corrcoef(obs[:, IDX[s]], pred[:, IDX[s]])[0, 1]), 3) for s in SEC},
        "isaret_dogrulugu_yuzde": {s: round(float((np.sign(obs[:, IDX[s]]) == np.sign(pred[:, IDX[s]])).mean() * 100), 1) for s in SEC},
    }
    out["T2_matris_testi"]["R2_kiyas_transfer_yok"] = None
    eps = {}
    for p in ["2018-Q3", "2021-Q4", "2023-Q2", "2025-Q4"]:
        i = [r[0] for r in rec].index(p)
        eps[p] = {"gozlenen": dict(zip(SEC, obs[i].round(3).tolist())), "tahmin": dict(zip(SEC, pred[i].round(3).tolist()))}
    out["T2_donem_ornekleri_trilyonTL"] = eps

    # ---- T3: ikinci tur (λ/κ tanımlanabilirliği)
    # F'nin negatif net değerlemesi (zarar) -> sonraki çeyrekte B'nin ve K'nın net işlem akışı/değerlemesi
    nl = {}
    for s in SEC:
        g = P[(P.Hazne == s) & P.Islem.notna()]
        nl[s] = (g[g.Taraf == "varlik"].groupby("Donem").Islem.sum() - g[g.Taraf == "yukumluluk"].groupby("Donem").Islem.sum()) / 1e9
    ts = pd.DataFrame({"RF": obs[:, IDX["F"]], "RB": obs[:, IDX["B"]], "RH": obs[:, IDX["H"]], "RK": obs[:, IDX["K"]]}, index=qs)
    ts["lossF"] = (-ts.RF).clip(lower=0)
    ts["NL_B"] = nl["B"]
    ts["NL_K"] = nl["K"]
    ts["NL_H"] = nl["H"]
    res = {}
    for y in ("RB", "RK", "RH", "NL_B", "NL_K", "NL_H"):
        d = pd.DataFrame({"y": ts[y].shift(-1), "x": ts["lossF"], "x0": ts["lossF"].shift(1)}).dropna()
        X = np.column_stack([np.ones(len(d)), d.x.to_numpy()])
        beta, *_ = np.linalg.lstsq(X, d.y.to_numpy(), rcond=None)
        e = d.y.to_numpy() - X @ beta
        s2 = e @ e / (len(d) - 2)
        se = np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1])
        res[y] = {"beta": round(float(beta[1]), 3), "t": round(float(beta[1] / se), 2), "n": int(len(d))}
    out["T3_ikinci_tur_OLS(F zarari t -> y t+1)"] = res
    (DIR / "geri_test_ozeti.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
