"""D (dış dünya) satırı için gerçek bilateral kısıt: brüt dış borç, borçlu sektöre göre (milyon USD).

C[D,j]: yabancıların yerleşik borçlu sektör j'ye alacağı. Eşleme: K' = Genel Hükümet + Merkez Bankası;
B' = Bankalar; F = Diğer Sektörler + Doğrudan yatırım (borç ilişkisi); H = 0.
USD/TRY çeyrek sonu ile bin TL'ye çevrilir. D'nin borç-benzeri varlık toplamına (finansal hesaplar) ölçeklenir.
Kalan yurt içi yükümlülük, yurt içi alacaklılar arasında varlık payına göre dağıtılır.
Çıktı: L_bil_ceyreklik.csv, L_bil_2026-Q1.csv, bilateral_test_ozeti.json
"""
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from akis_model import IDX, SEC, load, mat, panel
from kalibre_matris import INSTR, LOSS_INSTR
from kur_kanali import usd_quarter_end, BASE

DIR = Path(__file__).parent
NAMES = list(INSTR)
CODES = {"K": ["TP.BRUTDBSDDS.G2", "TP.BRUTDBSDDS.G16"], "B": ["TP.BRUTDBSDDS.G30"], "F": ["TP.BRUTDBSDDS.G43", "TP.BRUTDBSDDS.G56"]}


def fetch_ext():
    allc = sorted({c for v in CODES.values() for c in v})
    body = {"type": "json", "series": "-".join(allc), "aggregationTypes": "-".join("last" for _ in allc), "formulas": "-".join("0" for _ in allc),
            "startDate": "01-10-2014", "endDate": "07-10-2026", "frequency": "5", "decimalSeperator": ".", "decimal": "4",
            "dateFormat": "0", "lang": "TR", "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": True, "isRaporSayfasi": False}
    req = urllib.request.Request(f"{BASE}/fe", data=json.dumps(body).encode(), headers={"Accept": "application/json", "Content-Type": "application/json"}, method="POST")
    d = json.loads(urllib.request.urlopen(req, timeout=120).read().decode("utf-8-sig"))
    rows = {}
    for it in d["items"]:
        rows[str(it["Tarih"])] = {c: float(str(it.get(c.replace(".", "_"), "nan")).replace(",", "")) for c in allc}
    return pd.DataFrame(rows).T.sort_index()


def build_Lbil(A, Y, C_D):
    """A,Y: [8 enstrüman, 5 hazne]; C_D[j]: D'nin j'ye alacağı (bin TL, ham). -> L_bil[j, i] (satır j borçlu)."""
    li = [NAMES.index(n) for n in LOSS_INSTR]
    Yd = Y[li].sum(axis=0)  # borçlu j borç benzeri yükümlülük
    Ad = A[li].sum(axis=0)  # alacaklı i borç benzeri varlık
    C = np.array([C_D.get(s, 0.0) for s in SEC])
    if C.sum() > 0:
        C = C * (Ad[IDX["D"]] / C.sum())  # D'nin toplam alacağına ölçekle
    C = np.minimum(C, Yd)
    L = np.zeros((5, 5))
    dom_assets = Ad.copy()
    dom_assets[IDX["D"]] = 0
    for j in range(5):
        if j == IDX["D"] or Yd[j] <= 0:
            continue
        rem = max(Yd[j] - C[j], 0.0)
        w = dom_assets.copy()
        w[j] = 0
        if w.sum() > 0:
            L[j] = rem * w / w.sum() / Yd[j]
        L[j, IDX["D"]] = C[j] / Yd[j]
    # D borçlu: yurt içi sahipler (D'nin yükümlülüğü yurt içi varlık)
    jd = IDX["D"]
    if Yd[jd] > 0:
        w = dom_assets.copy()
        L[jd] = w / w.sum()
    return L, C


def main():
    ext = fetch_ext()
    fx = usd_quarter_end()
    stab, ftab, tcs, tcf = load()
    P = pd.read_csv(DIR / "temiz_stok_akis_paneli.csv", dtype={"Donem": str})
    qs = sorted(P.Donem.unique())
    ts, tl_ratio = [], {}
    Cq, Lq = {}, {}
    for idx, p in enumerate(qs):
        if p not in ext.index:
            continue
        r = ext.loc[p]
        usd_to_bintl = fx.get(p, np.nan) * 1000.0
        C_D = {s: sum(r[c] for c in cs) * usd_to_bintl for s, cs in CODES.items()}
        prev = "2014-Q4" if p == "2015-Q1" else qs[idx - 1]
        A, Y = panel(stab, tcs, prev)
        # ölçek kontrolü: ham dış borç / D'nin borç-benzeri varlığı
        li = [NAMES.index(n) for n in LOSS_INSTR]
        tl_ratio[p] = sum(C_D.values()) / A[li][:, IDX["D"]].sum()
        L, C = build_Lbil(A, Y, C_D)
        Lq[p] = L
        for j, s in enumerate(SEC):
            ts.append({"Donem": p, "Kaynak": s, **{f"L_{t}": L[j, i] for i, t in enumerate(SEC)}})
    pd.DataFrame(ts).to_csv(DIR / "L_bil_ceyreklik.csv", index=False, encoding="utf-8-sig")
    last = max(Lq)
    pd.DataFrame(Lq[last], index=SEC, columns=SEC).round(4).to_csv(DIR / f"L_bil_{last}.csv", encoding="utf-8-sig")
    print("L_bil", last, "\n", pd.DataFrame(Lq[last], index=SEC, columns=SEC).round(3).to_string())

    # --- T2'yi bilateral L ile tekrarla (borç-benzeri enstrümanlar bilateral, diğerleri orantılı)
    inst = [n for n in NAMES if n != "altin_sdr"]
    obs, pb, pp = [], [], []
    used = []
    for idx, p in enumerate(qs):
        if p not in Lq:
            continue
        prev = "2014-Q4" if p == "2015-Q1" else qs[idx - 1]
        A, Y = panel(stab, tcs, prev)
        Rp = P[P.Donem == p]
        r_obs = np.zeros(5); r_b = np.zeros(5); r_p = np.zeros(5)
        for n in inst:
            k = NAMES.index(n)
            sub = Rp[(Rp.Enstruman == n) & Rp.Hazne.isin(SEC)]
            ry = np.array([sub[(sub.Hazne == s) & (sub.Taraf == "yukumluluk")].Degerleme_veya_Degisim.iloc[0] for s in SEC])
            ra = np.array([sub[(sub.Hazne == s) & (sub.Taraf == "varlik")].Degerleme_veya_Degisim.iloc[0] for s in SEC])
            r_obs += ra - ry
            Lprop = mat(A, Y, [n])
            r_p += ry @ Lprop - ry
            Luse = Lq[p] if n in LOSS_INSTR else Lprop
            r_b += ry @ Luse - ry
        obs.append(r_obs); pb.append(r_b); pp.append(r_p); used.append(p)
    o, b, pr = np.array(obs) / 1e9, np.array(pb) / 1e9, np.array(pp) / 1e9

    def r2(a, c):
        return round(float(1 - ((a - c) ** 2).sum() / ((a - a.mean()) ** 2).sum()), 3)

    sc = np.abs(o).sum(axis=1, keepdims=True)
    iD = IDX["D"]
    out = {
        "n_ceyrek": len(used),
        "dis_borc/D_borc_benzeri_varlik_ortanca_oran": round(float(np.median(list(tl_ratio.values()))), 3),
        "R2_havuz": {"orantili": r2(o, pr), "bilateral": r2(o, b)},
        "R2_olcek_bagimsiz": {"orantili": r2(o / sc, pr / sc), "bilateral": r2(o / sc, b / sc)},
        "MAE_trilyonTL": {s: {"orantili": round(float(np.abs(o[:, IDX[s]] - pr[:, IDX[s]]).mean()), 3), "bilateral": round(float(np.abs(o[:, IDX[s]] - b[:, IDX[s]]).mean()), 3)} for s in SEC},
        "korelasyon_bilateral": {s: round(float(np.corrcoef(o[:, IDX[s]], b[:, IDX[s]])[0, 1]), 3) for s in SEC},
        "isaret_dogrulugu_bilateral_yuzde": {s: round(float((np.sign(o[:, IDX[s]]) == np.sign(b[:, IDX[s]])).mean() * 100), 1) for s in SEC},
        "D_ornekler": {p: {"gozlenen": round(float(o[used.index(p), iD]), 3), "orantili": round(float(pr[used.index(p), iD]), 3), "bilateral": round(float(b[used.index(p), iD]), 3)} for p in ["2018-Q3", "2021-Q4", "2023-Q2", "2025-Q4"] if p in used},
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    (DIR / "bilateral_test_ozeti.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
