"""λ / geçiş-oranı kalibrasyonu: F'nin değerleme zararı -> bankanın GERÇEKLEŞEN kredi zararı (provizyon gideri).

Neden provizyon? λ zararın bozulma (temerrüt) yoluyla alacaklıya geçişini yönetir. Değerleme verisi zıt işaretli
bir transfer ölçer (borçlunun kur zararı = alacaklının kazancı), bu yüzden λ'yı onunla kalibre etmek yanlış olur.
Bankanın gerçekleşen zararı: Mevduat Bankaları Kâr-Zarar Hesabı, Takipteki Alacaklar Özel Provizyonu (TP.PFVPBI10.K21).

Tanımlar
  x_t   = F'nin net değerleme zararı (pozitif = zarar), enstrüman toplamı, altın/SDR hariç, trilyon TL
  y_t,h = provizyon gideri, t..t+h çeyrekleri toplamı
  Ölçek: ikisi de nominal büyür -> GSYH'ye bölünür (aksi halde enflasyon sahte korelasyon üretir)
  β_h   = d(y/GSYH)/d(x/GSYH) (OLS, sabitli; Newey-West t, gecikme 2)
  θ_h   = β_h / L[F->B]: F'nin zararından B'de gerçekleşen kısım, matris payına oranla
          (θ = F zararının alacaklılara geçen (gerçekleşen) kesri varsayımı altında)
"""
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from akis_model import IDX, SEC

D = Path(__file__).parent
BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis"


def gdp_q():
    body = {"type": "json", "series": "TP.GSYIH30.AY.B1GQ", "aggregationTypes": "last", "formulas": "0", "startDate": "01-01-2010",
            "endDate": "07-10-2026", "frequency": "5", "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR", "yon": "0",
            "sira": "0", "ozelFormuller": [], "groupSeperator": True, "isRaporSayfasi": False}
    r = urllib.request.Request(f"{BASE}/fe", data=json.dumps(body).encode(), headers={"Accept": "application/json", "Content-Type": "application/json"}, method="POST")
    d = json.loads(urllib.request.urlopen(r, timeout=120).read().decode("utf-8-sig"))
    return pd.Series({str(i["Tarih"]): float(str(i["TP_GSYIH30_AY_B1GQ"]).replace(",", "")) / 1e9 for i in d["items"]})


def prov_quarterly():
    d = pd.read_csv(D / "prov_ham.csv", dtype={"Donem": str})
    k = d[d.Seri == "TP.PFVPBI10.K21"].sort_values("Donem").set_index("Donem").Deger
    yil = k.index.str[:4]
    flow = k.groupby(yil).diff().fillna(k)  # yıl içi birikimli -> aylık
    flow[k.index.str[5:7] == "01"] = k[k.index.str[5:7] == "01"]
    q = flow.groupby([f"{p[:4]}-Q{(int(p[5:7]) - 1) // 3 + 1}" for p in flow.index]).agg(["sum", "count"])
    q = q[q["count"] == 3]["sum"] / 1e9  # trilyon TL
    return q


def nw_ols(y, x, lag=2):
    X = np.column_stack([np.ones(len(x)), x])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    e = y - X @ b
    n = len(y)
    S = (X * e[:, None]).T @ (X * e[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1)
        G = (X[l:] * e[l:, None]).T @ (X[:-l] * e[:-l, None])
        S += w * (G + G.T)
    XtXi = np.linalg.inv(X.T @ X)
    V = XtXi @ S @ XtXi
    return b, np.sqrt(np.diag(V)), n


def main():
    P = pd.read_csv(D / "temiz_stok_akis_paneli.csv", dtype={"Donem": str})
    g = P[(P.Hazne == "F") & (P.Enstruman != "altin_sdr")]
    rf = (g[g.Taraf == "varlik"].groupby("Donem").Degerleme_veya_Degisim.sum() - g[g.Taraf == "yukumluluk"].groupby("Donem").Degerleme_veya_Degisim.sum()) / 1e9
    lossF = -rf  # zarar pozitif
    gdp = gdp_q()
    prov = prov_quarterly()
    L = pd.read_csv(D / "matris_v2_zaman_serisi.csv", dtype={"Donem": str})
    LFB = L[L.Kaynak == "F"].set_index("Donem").L_B

    qs = [p for p in sorted(lossF.index) if p in prov.index and p in gdp.index]
    out = {"orneklem": f"{qs[0]}..{qs[-1]}", "n_ceyrek": len(qs)}
    res = {}
    for h in range(0, 5):
        rows = []
        for i, p in enumerate(sorted(prov.index)):
            pass
        allq = sorted(prov.index)
        for p in lossF.index:
            if p not in gdp.index or p not in allq:
                continue
            j = allq.index(p)
            if j + h >= len(allq):
                continue
            win = allq[j: j + h + 1]
            if any(w not in gdp.index for w in win):
                continue
            y = sum(prov[w] for w in win) / gdp[p]
            x = lossF[p] / gdp[p]
            rows.append((p, x, y))
        if len(rows) < 12:
            continue
        d = pd.DataFrame(rows, columns=["p", "x", "y"])
        b, se, n = nw_ols(d.y.to_numpy(), d.x.to_numpy())
        lfb = float(LFB.loc[d.p].mean())
        res[f"h{h}"] = {"n": n, "beta": round(float(b[1]), 4), "t_NW": round(float(b[1] / se[1]), 2),
                        "theta=beta/L_FB": round(float(b[1]) / lfb, 4), "L_FB_ort": round(lfb, 3),
                        "y_ort/GSYH": round(float(d.y.mean()), 5), "x_ort/GSYH": round(float(d.x.mean()), 5)}
    out["provizyon_regresyonu(F zarari/GSYH -> kumulatif provizyon/GSYH)"] = res

    # kıyas: aynı yöntemle K'nin net işlemi (önceki T3'ün GSYH-normalize hali)
    nl = P[(P.Hazne == "K") & P.Islem.notna()]
    nlK = (nl[nl.Taraf == "varlik"].groupby("Donem").Islem.sum() - nl[nl.Taraf == "yukumluluk"].groupby("Donem").Islem.sum()) / 1e9
    resK = {}
    for h in range(0, 4):
        rows = []
        allq = sorted(nlK.index)
        for p in lossF.index:
            if p not in gdp.index or p not in allq:
                continue
            j = allq.index(p)
            if j + h >= len(allq):
                continue
            win = allq[j: j + h + 1]
            rows.append((p, lossF[p] / gdp[p], sum(nlK[w] for w in win) / gdp[p]))
        d = pd.DataFrame(rows, columns=["p", "x", "y"])
        b, se, n = nw_ols(d.y.to_numpy(), d.x.to_numpy())
        resK[f"h{h}"] = {"n": n, "beta": round(float(b[1]), 3), "t_NW": round(float(b[1] / se[1]), 2)}
    out["K_net_islem_regresyonu(GSYH-normalize)"] = resK

    # özet parametre önerisi
    h4 = res.get("h4") or res.get("h3")
    out["oneri"] = {
        "theta_F_to_B": h4["theta=beta/L_FB"] if h4 else None,
        "yorum": "θ, F zararının B'de gerçekleşen (provizyon) kesri / matris payı. Küçükse F zararının büyük kısmı gerçekleşmiyor "
                 "(F'de kalıyor ya da çözülüyor); simülatörde F->B kenarı θ ile ölçeklenmeli.",
        "uyari": "Örneklem küçük (n~30), provizyon gideri nominal şoklara ve düzenleyici kurallara (BDDK) duyarlı; seri 2022-08'de bitiyor.",
    }
    (D / "kalibre_lambda_ozeti.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
