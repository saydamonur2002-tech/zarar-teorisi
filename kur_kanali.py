"""Döviz maruziyet payı (f) tahmini: değerleme getirisi = f * kur değişimi + e (hazne x enstrüman x taraf).
Kur: USD/TRY döviz alış, çeyrek sonu (aylık son gözlem). Sonuç fx_maruziyet.csv; Lm'yi f ile ağırlıklar (Lfx)."""
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from akis_model import IDX, SEC, load, mat, panel
from kalibre_matris import INSTR

DIR = Path(__file__).parent
BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis"
NAMES = list(INSTR)


def usd_quarter_end():
    body = {"type": "json", "series": "TP.DK.USD.A", "aggregationTypes": "last", "formulas": "0",
            "startDate": "01-10-2014", "endDate": "07-10-2026", "frequency": "5", "decimalSeperator": ".",
            "decimal": "4", "dateFormat": "0", "lang": "TR", "yon": "0", "sira": "0", "ozelFormuller": [],
            "groupSeperator": True, "isRaporSayfasi": False}
    req = urllib.request.Request(f"{BASE}/fe", data=json.dumps(body).encode(), headers={"Accept": "application/json", "Content-Type": "application/json"}, method="POST")
    d = json.loads(urllib.request.urlopen(req, timeout=120).read().decode("utf-8-sig"))
    s = {}
    for it in d["items"]:
        y, m = str(it["Tarih"]).split("-")[:2]
        if int(m) % 3 == 0:
            s[f"{y}-Q{int(m)//3}"] = float(str(it["TP_DK_USD_A"]).replace(",", ""))
    return pd.Series(s).sort_index()


def main():
    fx = usd_quarter_end()
    dep = np.log(fx / fx.shift(1)).dropna()
    P = pd.read_csv(DIR / "temiz_stok_akis_paneli.csv", dtype={"Donem": str})
    qs = [p for p in sorted(P.Donem.unique())]
    stab, ftab, tcs, tcf = load()
    rows = []
    for n in NAMES:
        for s in SEC:
            for taraf in ("varlik", "yukumluluk"):
                g = P[(P.Enstruman == n) & (P.Hazne == s) & (P.Taraf == taraf)].set_index("Donem")
                prev_stock = g.Stok.shift(1)
                prev_stock.loc["2015-Q1"] = np.nan
                rate = (g.Degerleme_veya_Degisim / prev_stock)
                d = pd.DataFrame({"r": rate, "x": dep}).replace([np.inf, -np.inf], np.nan).dropna()
                d = d[(prev_stock.reindex(d.index) > 0)]
                if len(d) < 20 or d.x.var() == 0:
                    continue
                X = np.column_stack([np.ones(len(d)), d.x.to_numpy()])
                b, *_ = np.linalg.lstsq(X, d.r.to_numpy(), rcond=None)
                e = d.r.to_numpy() - X @ b
                se = np.sqrt((e @ e / (len(d) - 2)) * np.linalg.inv(X.T @ X)[1, 1])
                ss = ((d.r - d.r.mean()) ** 2).sum()
                rows.append({"Enstruman": n, "Hazne": s, "Taraf": taraf, "f": float(np.clip(b[1], 0, 1)), "f_ham": float(b[1]), "t": float(b[1] / se),
                             "R2": float(1 - (e @ e) / ss) if ss > 0 else np.nan, "n": len(d)})
    F = pd.DataFrame(rows)
    F.to_csv(DIR / "fx_maruziyet.csv", index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 200)
    for n in ("kredi", "mevduat" if False else "para_mevduat", "borclanma_senedi", "hisse_ozkaynak"):
        t = F[F.Enstruman == n].pivot(index="Hazne", columns="Taraf", values="f").round(2)
        print("\nf =", n, "\n", t.to_string())

    # --- T2'yi f-ağırlıklı alacaklı dağılımıyla tekrarla
    fa = F.set_index(["Enstruman", "Hazne", "Taraf"]).f
    inst = [n for n in NAMES if n != "altin_sdr"]
    res = {"gozlenen": [], "tahmin_fx": [], "tahmin_orantili": []}
    for idx, p in enumerate(qs):
        prev = "2014-Q4" if p == "2015-Q1" else qs[idx - 1]
        A, Y = panel(stab, tcs, prev)
        Rp = P[P.Donem == p]
        r_obs = np.zeros(5); r_fx = np.zeros(5); r_pr = np.zeros(5)
        for n in inst:
            k = NAMES.index(n)
            sub = Rp[(Rp.Enstruman == n) & Rp.Hazne.isin(SEC)]
            ry = np.array([sub[(sub.Hazne == s) & (sub.Taraf == "yukumluluk")].Degerleme_veya_Degisim.iloc[0] for s in SEC])
            ra = np.array([sub[(sub.Hazne == s) & (sub.Taraf == "varlik")].Degerleme_veya_Degisim.iloc[0] for s in SEC])
            r_obs += ra - ry
            fw = np.array([fa.get((n, s, "varlik"), 0.0) for s in SEC])
            # orantılı
            E = A[k]
            for j in range(5):
                others = E.copy(); others[j] = 0
                if others.sum() > 0:
                    r_pr += ry[j] * others / others.sum()
                w = E * fw; w[j] = 0
                if w.sum() > 1e-9:
                    r_fx += ry[j] * w / w.sum()
                elif others.sum() > 0:
                    r_fx += ry[j] * others / others.sum()
            r_pr -= ry
            r_fx -= ry
        res["gozlenen"].append(r_obs); res["tahmin_fx"].append(r_fx); res["tahmin_orantili"].append(r_pr)
    o = np.array(res["gozlenen"]) / 1e9
    pf = np.array(res["tahmin_fx"]) / 1e9
    pp = np.array(res["tahmin_orantili"]) / 1e9

    def r2(a, b):
        return round(float(1 - ((a - b) ** 2).sum() / ((a - a.mean()) ** 2).sum()), 3)

    # ölçek-bağımsız: her çeyreği toplam mutlak gözleme böl
    sc = np.abs(o).sum(axis=1, keepdims=True)
    out = {
        "R2_havuz": {"orantili": r2(o, pp), "fx_agirlikli": r2(o, pf)},
        "R2_olcek_bagimsiz": {"orantili": r2(o / sc, pp / sc), "fx_agirlikli": r2(o / sc, pf / sc)},
        "MAE_trilyonTL_D": {"orantili": round(float(np.abs(o[:, IDX['D']] - pp[:, IDX['D']]).mean()), 3), "fx_agirlikli": round(float(np.abs(o[:, IDX['D']] - pf[:, IDX['D']]).mean()), 3)},
        "sektor_korelasyon_fx": {s: round(float(np.corrcoef(o[:, IDX[s]], pf[:, IDX[s]])[0, 1]), 3) for s in SEC},
        "D_2025Q4": {"gozlenen": round(float(o[qs.index('2025-Q4'), IDX['D']]), 3), "orantili": round(float(pp[qs.index('2025-Q4'), IDX['D']]), 3), "fx": round(float(pf[qs.index('2025-Q4'), IDX['D']]), 3)},
        "D_2023Q2": {"gozlenen": round(float(o[qs.index('2023-Q2'), IDX['D']]), 3), "orantili": round(float(pp[qs.index('2023-Q2'), IDX['D']]), 3), "fx": round(float(pf[qs.index('2023-Q2'), IDX['D']]), 3)},
    }
    print("\n", json.dumps(out, ensure_ascii=False, indent=2))
    (DIR / "fx_test_ozeti.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
