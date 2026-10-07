"""Dış borç stoku artışı: borçlu sektöre göre, yeni borçlanma / kur etkisi ayrımı ve modeldeki karşılığı.

Kaynak: EVDS bie_brutdbborclu (Brüt Dış Borç, borçlu dağılımı, milyon USD, çeyreklik, TCMB). USD/TRY çeyrek sonu (EVDS TP.DK.USD.A).
Ayrıştırma (t0 -> t1, TL):  ΔTL = (USD1 - USD0)*kur0   [yeni borçlanma/geri ödeme, açılış kuruyla]
                                  + USD1*(kur1 - kur0)    [kur etkisi, kapanış stokuna]
Modeldeki karşılık: D'nin net finansal değeri (finansal hesaplar, D çevrilmiş) değişimi = net işlem (NL_D) + değerleme (R_D).
"""
import json
from pathlib import Path

import pandas as pd

D = Path(__file__).parent
GRUP = {"Kamu": "TP.BRUTDBORCLU.G2", "TCMB": "TP.BRUTDBORCLU.G13", "Özel": "TP.BRUTDBORCLU.G14",
        "Özel_banka": "TP.BRUTDBORCLU.G16", "Özel_banka_dışı_fin": "TP.BRUTDBORCLU.G17", "Özel_finans_dışı": "TP.BRUTDBORCLU.G18",
        "Toplam": "TP.BRUTDBORCLU.G1"}


def _veri():
    f = D / "dis_borc_ham.csv"
    if not f.exists():
        from evds_cek import fetch_group
        rows, _ = fetch_group("bie_brutdbborclu")
        pd.DataFrame(rows, columns=["Grup", "Donem", "Seri", "Ad", "Agg", "Deger"]).to_csv(f, index=False, encoding="utf-8-sig")
    d = pd.read_csv(f, dtype={"Donem": str})
    return d.pivot_table(index="Donem", columns="Seri", values="Deger", aggfunc="last")


def ozet():
    from kur_kanali import usd_quarter_end
    p = _veri()
    fx = usd_quarter_end()
    usd = pd.DataFrame({k: p[v] for k, v in GRUP.items()}) / 1e3  # milyar USD
    usd = usd.loc[[i for i in usd.index if i in fx.index]]
    tl = usd.mul(fx.reindex(usd.index), axis=0)  # milyar TL

    def ayristir(t0, t1):
        r = {}
        for g in ["Kamu", "TCMB", "Özel", "Toplam"]:
            flow = (usd.loc[t1, g] - usd.loc[t0, g]) * fx[t0]
            kur = usd.loc[t1, g] * (fx[t1] - fx[t0])
            r[g] = {"USD_t0_mr": round(usd.loc[t0, g], 1), "USD_t1_mr": round(usd.loc[t1, g], 1), "dUSD_mr": round(usd.loc[t1, g] - usd.loc[t0, g], 1),
                    "dTL_trilyon": round((tl.loc[t1, g] - tl.loc[t0, g]) / 1e3, 2),
                    "yeni_borclanma_TL_trilyon": round(flow / 1e3, 2), "kur_etkisi_TL_trilyon": round(kur / 1e3, 2)}
        return r

    t_son = usd.index[-1]
    secili = [t for t in ["2023-Q4", "2024-Q4", "2025-Q4", "2026-Q1", t_son] if t in usd.index]
    tablo = {t: {"Kamu": round(usd.loc[t, "Kamu"], 1), "TCMB": round(usd.loc[t, "TCMB"], 1), "Özel": round(usd.loc[t, "Özel"], 1),
                 "Toplam": round(usd.loc[t, "Toplam"], 1), "Özel_pay_%": round(100 * usd.loc[t, "Özel"] / usd.loc[t, "Toplam"], 1),
                 "USDTRY": round(fx[t], 2)} for t in secili}

    # modeldeki karşılık: D'nin NFP değişimi = NL + R
    P = pd.read_csv(D / "temiz_stok_akis_paneli.csv", dtype={"Donem": str})
    d = P[P.Hazne == "D"]
    a, y = d[d.Taraf == "varlik"], d[d.Taraf == "yukumluluk"]
    stok = (a.groupby("Donem").Stok.sum() - y.groupby("Donem").Stok.sum()) / 1e9  # D varlığı - yükümlülüğü, çevrilmiş D (trilyon TL)
    nl = ((a.groupby("Donem").Islem.sum() - y.groupby("Donem").Islem.sum())) / 1e9
    rr = ((a.groupby("Donem").Degerleme_veya_Degisim.sum() - y.groupby("Donem").Degerleme_veya_Degisim.sum())) / 1e9
    son8 = [q for q in sorted(nl.dropna().index) if q >= "2024-Q2"]
    seri = {q: {"NFP_D": round(float(stok[q]), 2), "net_islem": round(float(nl[q]), 2), "degerleme": round(float(rr[q]), 2)} for q in son8}
    w = [q for q in son8 if q >= "2025-Q2"]
    top = {"net_islem": round(float(sum(nl[q] for q in w)), 2), "degerleme": round(float(sum(rr[q] for q in w)), 2), "dNFP": round(float(sum(nl[q] + rr[q] for q in w)), 2)}

    # L_bil'de D payı zaman içinde (F ve B ve K için)
    lb = pd.read_csv(D / "L_bil_ceyreklik.csv", dtype={"Donem": str})
    dz = {s: {q: round(float(lb[(lb.Donem == q) & (lb.Kaynak == s)].L_D.iloc[0]), 3) for q in ["2018-Q3", "2021-Q4", "2023-Q4", "2026-Q1"]} for s in ["F", "B", "K"]}

    # Eylül 2026 "Bilanço Rotasyonu" raporundaki rakamlarla karşılaştırma (Kamu+TCMB / Özel / Toplam, milyar USD)
    rapor = {"2023": (247, 245, 492), "2024": (254, 264, 517), "2025-Q3": (264, 301, 565), "2026-Q2": (221, 318, 539)}
    esle = {"2023": "2023-Q4", "2024": "2024-Q4", "2025-Q3": "2025-Q3", "2026-Q2": "2026-Q2"}
    karsi = {}
    for k, (kt, oz, top_) in rapor.items():
        q = esle[k]
        e_kt = float(usd.loc[q, "Kamu"] + usd.loc[q, "TCMB"])
        karsi[k] = {"rapor": {"Kamu+TCMB": kt, "Özel": oz, "Toplam": top_},
                    "EVDS": {"Kamu+TCMB": round(e_kt, 1), "Özel": round(float(usd.loc[q, "Özel"]), 1), "Toplam": round(float(usd.loc[q, "Toplam"]), 1)},
                    "fark_Kamu+TCMB": round(kt - e_kt, 1), "fark_Özel": round(oz - float(usd.loc[q, "Özel"]), 1)}

    out = {
        "kaynak": "EVDS bie_brutdbborclu (milyon USD -> milyar USD), USD/TRY çeyrek sonu; TL = USD*kur",
        "rapor_ile_uyumsuzluk": {
            "karsilastirma": karsi,
            "sonuc": "2026-Q2'de birebir uyuşuyor; önceki yıllarda Kamu+TCMB raporda ~30-55 mr USD YÜKSEK (EVDS'de çıkmıyor), Özel yakın. "
                     "EVDS serisiyle Kamu+TCMB 2023-Q4'ten 2026-Q2'ye ARTIYOR (194 -> 221), raporda AZALIYOR (247 -> 221): 'rotasyon' (kamu azaldı, özel arttı) EVDS'de görünmüyor. "
                     "Raporun kaynak dosyası/tanımı (örn. farklı kamu kapsamı) doğrulanmalı.",
        },
        "stok_milyar_USD": tablo,
        "ayristirma_2023Q4_to_son": ayristir("2023-Q4", t_son),
        "ayristirma_2025Q4_to_son": ayristir("2025-Q4", t_son) if "2025-Q4" in usd.index else None,
        "modelde_D_NFP(trilyonTL)_son_ceyrekler": seri,
        "modelde_D_NFP_son4ceyrek_toplami": top,
        "L_bil_D_payi_zaman": dz,
        "yorum": [
            "TL cinsinden dış borç artışı iki bileşenden oluşur: yeni borçlanma (USD artışı) ve TL değer kaybının kapanış stokuna etkisi. Kur etkisi gerçek borçlanma olmadan TL yükünü büyütür.",
            "Modelde bu, D'nin net finansal değerindeki artışın işlem (NL) + değerleme (R) ayrımıdır; değerleme zararın aktarımının asıl taşıyıcısıdır.",
        ],
    }
    return out


if __name__ == "__main__":
    print(json.dumps(ozet(), ensure_ascii=False, indent=2))
