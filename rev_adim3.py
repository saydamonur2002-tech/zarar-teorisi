"""Revizyon E — Adım 3: duran faiz, nominal büyüyen stok, TL/YP ayrımı, r senaryo bantları, ψ yeniden.
Kaynaklar (dondurulmuş): tavan_akis_ham.csv ZP34 (F.4 stok), faiz_ham.csv TP.BKR.TRY.1 / TP.BKR.USD.1 (stok faizleri, ticari),
faiz_kur_ham.csv usd (aylık), /workspace/aktarim_matrisi/tcmb/FKDFDVY2026-07.xlsx 'Nakdi Krediler' (milyon USD; yurtiçi+yurtdışı),
rev_veri Sektör Bilançoları 2023–2024 (finansman gideri, banka kredileri).
Etiketler: YP payı olcum_turevi (FKDFDVY×kur / ZP34; kapsam farkı olabilir), g olcum_turevi bandı, r_TL patikaları VARSAYIM, κ VARSAYIM.
"""
import csv, json, math
from pathlib import Path
import pandas as pd
import tek_sistem_kademe as tk
import adim3_faiz_durma as a3
import rev_veri as rv
KOK = Path(__file__).resolve().parent
FKD = Path("/workspace/aktarim_matrisi/tcmb/FKDFDVY2026-07.xlsx")

def fkd():
    x = pd.read_excel(FKD, header=None); i = next(k for k in range(len(x)) if str(x.iloc[k, 1]).strip() == "Nakdi Krediler")
    return {str(x.iloc[7, j]): float(x.iloc[i, j]) for j in range(2, x.shape[1]) if pd.notna(x.iloc[i, j])}

def aylik(seri):
    return {r["Donem"]: float(r["Deger"]) for r in csv.DictReader(open(KOK / "faiz_ham.csv", encoding="utf-8-sig")) if r["Seri"] == seri and r["Deger"] not in ("", "nan")}

def main():
    usd = {r["donem"]: float(r["usd"]) for r in csv.DictReader(open(KOK / "faiz_kur_ham.csv", encoding="utf-8-sig")) if r["usd"]}
    stok = a3.f4_stok(); nk = fkd()
    yp = {}
    for ay, q in (("2023-12", "2023-Q4"), ("2024-12", "2024-Q4"), ("2025-12", "2025-Q4"), ("2026-03", "2026-Q1")):
        yp[q] = nk[ay] * usd[ay] / 1000 / stok[q]
    rT, rU = aylik("TP.BKR.TRY.1"), aylik("TP.BKR.USD.1")
    q24 = [f"2024-Q{i}" for i in range(1, 5)]
    rq = lambda d, q: sum(d[f"{q[:4]}-{m:02d}"] for m in range(3 * int(q[-1]) - 2, 3 * int(q[-1]) + 1)) / 300
    sy = {q: yp["2023-Q4"] + (yp["2024-Q4"] - yp["2023-Q4"]) * (i + 1) / 4 for i, q in enumerate(q24)}
    karma = {q: (1 - sy[q]) * rq(rT, q) + sy[q] * rq(rU, q) for q in q24}
    FG = 3143.4  # adim3 psi.finansman_gideri_2024 (tek_sistem_kopru, olcum)
    nom_evds = sum(karma[q] * stok[q] / 4 for q in q24)
    p = rv.nace_panel(); bk = {y: float(p[p.yil == y].banka.sum()) for y in (2023, 2024)}
    s_sb = (bk[2023] + bk[2024]) / 2; r24 = sum(karma.values()) / 4
    psi = {"eski_repo": 0.3584,
           "evds_tl_yp": round(FG / nom_evds, 4),
           "sb_ayni_kapsam": round(FG / (r24 * s_sb), 4),
           "not": "Finansman gideri kur farkı zararını ve banka dışı borç faizini içerir → ψ>1 mümkün; oran eşitlik değil (olcum_turevi)."}
    # g bandı: ZP34 son 8 çeyrek çeyreklik büyüme
    qs = sorted(k for k in stok if k >= "2024-Q1"); gr = [stok[b] / stok[a] - 1 for a, b in zip(qs, qs[1:])][-8:]
    gr_s = sorted(gr); G = {"sifir": 0.0, "medyan": gr_s[len(gr_s) // 2], "min": gr_s[0], "max": gr_s[-1]}
    k2 = next(x for x in tk.PENCERELER if x.kod == "K2_stok"); don = tk._iter_donem(tk.DONEM_BAS, tk.DONEM_SON)
    rT_son = rT[max(rT)] ; rU_son = rU[max(rU)]
    def rpat(ad, d):
        y, q = int(d[:4]), int(d[-1]); t = (y - 2026) * 4 + q - 3  # 2026-Q3=0
        if ad == "sabit": return rT_son
        if ad == "dusus": return max(30.0, rT_son - (rT_son - 30.0) * t / 9)  # 2028-Q4'te 30 (VARSAYIM)
        if ad == "yuksek": return 55.0
    s0 = stok["2026-Q1"]; s_yp = yp["2026-Q1"]
    satir, yil = [], {}
    for gad, g in G.items():
        for rad in ("dusus", "sabit", "yuksek"):
            for kap in (0.25, 0.5, 1.0):
                for i, d in enumerate(don):
                    S = s0 * (1 + g) ** (i + 2)  # 2026-Q1'den itibaren
                    u2 = tk.uygulama_orani(d, k2); D = kap * u2 * S
                    I = D * ((1 - s_yp) * rpat(rad, d) + s_yp * rU_son) / 400
                    satir.append({"g": gad, "r": rad, "kappa": kap, "donem": d, "S_milyar": round(S, 1), "D_milyar": round(D, 1), "I_sozlesme_milyar": round(I, 1)})
                    yil.setdefault((gad, rad, kap), {}).setdefault(d[:4], 0.0); yil[(gad, rad, kap)][d[:4]] += I
    pd.DataFrame(satir).to_csv(KOK / "rev_adim3.csv", index=False)
    ozet = []
    for (gad, rad, kap), yl in yil.items():
        ozet.append({"g": gad, "r": rad, "kappa": kap, "I_2029_milyar": round(yl["2029"], 1), "I_2031_milyar": round(yl["2031"], 1),
                     "oran_FG2024_2029": round(yl["2029"] / FG, 2)})
    oz = pd.DataFrame(ozet); oz.to_csv(KOK / "rev_adim3_ozet.csv", index=False)
    k1 = oz[oz.kappa == 1.0]
    sonuc = {"faz": "rev E", "yp_payi": {k: round(v, 4) for k, v in yp.items()}, "r_son": {"TL_stok": rT_son, "USD_stok": rU_son, "ay": max(rT)},
             "psi": psi, "g_ceyreklik": {k: round(v, 4) for k, v in G.items()},
             "kappa1_I_2029_bandi_milyar": [float(k1.I_2029_milyar.min()), float(k1.I_2029_milyar.max())],
             "kappa1_oran_FG2024_2029_bandi": [float(k1.oran_FG2024_2029.min()), float(k1.oran_FG2024_2029.max())],
             "eski_kappa1_2029": 4830.8, "eski_oran": 1.54,
             "etiketler": {"yp_payi": "olcum_turevi", "g": "olcum_turevi bandı (2024-Q1..2026-Q1)", "r_TL": "varsayim patika (düşüş→%30, sabit, %55)", "kappa": "varsayim",
                           "I": "sözleşme faizi (ψ uygulanmadı; ψ>1 çıktığı için ψ ile ölçek küçültmek savunulamaz)"}}
    (KOK / "rev_adim3_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(sonuc, ensure_ascii=False, indent=1)); print(oz[oz.kappa == 1.0].to_string(index=False))

if __name__ == "__main__":
    main()
