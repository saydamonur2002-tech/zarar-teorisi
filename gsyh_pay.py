"""Yürütme maliyetinin yıl bazında GSYH'ye oranı (düşük / orta / yüksek).

Çıktı: gsyh_pay.csv, GSYH_PAY.md. Çalıştır: python3 gsyh_pay.py

Payda: repoda GSYH yalnız 2023-2025 (tavan_akis.csv, ölçüm). Sonrası için YOL VARSAYIMDIR:
  GSYH_t = GSYH_t-1 × (1 + TÜFE_t) × (1 + REEL); TÜFE = bes_yil_senaryo.csv senaryo alt/üst ortası.
  2029-2030 TÜFE senaryosu yok: 2028 ile 2031 arası doğrusal (varsayım). REEL = %3 (varsayım, repoda yok).
Pay: adım 3 ve 4 kendi çeyreklik CSV'lerinden yıla toplanır; adım 4.5 2030; adım 1-2 tek sefer, takvim yılı repoda yok,
2029'a konur (varsayım); adım 5 yıl belirsiz ve 2026 fiyatıyla: payda GSYH 2026, ayrı satır, toplama girmez.
"""
import csv
import collections
from pathlib import Path

import adim45_maliyet as P45
import yurutme_maliyet as Y

KOK = Path(__file__).resolve().parent
REEL = 0.03
YILLAR = range(2026, 2032)


def oku(ad):
    return list(csv.DictReader(open(KOK / ad, encoding="utf-8-sig")))


def gsyh_yolu():
    g = {2025: P45.gsyh_2025()}
    t = {}
    for x in oku("bes_yil_senaryo.csv"):
        if x["degisken"] == "enflasyon_tufe_yillik" and x["senaryo_alt"]:
            t[int(x["yil"])] = (float(x["senaryo_alt"]) + float(x["senaryo_ust"])) / 200
    for y in (2029, 2030):
        t[y] = t[2028] + (t[2031] - t[2028]) * (y - 2028) / 3
    for y in YILLAR:
        g[y] = g[y - 1] * (1 + t[y]) * (1 + REEL)
    return g, t


def akislar():
    R = Y.RHO
    a4 = collections.defaultdict(lambda: collections.defaultdict(float))
    for x in oku("adim4_adres_yonlendirme.csv"):
        a4[(float(x["theta"]), float(x["chi"]), float(x["pi"]))][int(x["donem"][:4])] += float(x["prim_ceyrek"])
    top = {k: sum(v.values()) for k, v in a4.items()}
    k_lo, k_hi, k_mid = min(top, key=top.get), max(top, key=top.get), (0.25, 0.5, 0.05)
    a3 = collections.defaultdict(lambda: collections.defaultdict(float))
    for x in oku("adim3_faiz_durma.csv"):
        a3[float(x["kappa"])][int(x["donem"][:4])] += float(x["duran_faiz_etkin_milyar"])
    a1, a2 = Y.akis_adim1(), Y.akis_adim2()
    m = P45.maliyet()
    A, B = m["A"], m["B"]
    sc = {"düşük": ("alt", 0.25, k_lo, A[0]), "orta": ("orta", 0.5, k_mid, sum(A) / 2), "yüksek": ("ust", 1.0, k_hi, B[1])}
    out = {}
    for ad, (rho, kap, k4, c45) in sc.items():
        s = {y: collections.OrderedDict() for y in YILLAR}
        for y in YILLAR:
            s[y]["adım 3"] = a3[kap].get(y, 0) * R[rho]
            s[y]["adım 4"] = a4[k4].get(y, 0) * R[rho]
        s[2029]["adım 1-2 (tek sefer, 2029 varsayım)"] = (a1 + a2) * R["alt"]
        s[2030]["adım 4.5"] = c45
        out[ad] = s
    a5 = Y.akis_adim5()[50]
    ad5 = {"düşük": a5[0] * R["alt"], "orta": sum(a5) / 2 * R["orta"], "yüksek": a5[1] * R["ust"]}
    return out, ad5


def main():
    g, t = gsyh_yolu()
    out, ad5 = akislar()
    rows = []
    for ad, s in out.items():
        for y in YILLAR:
            tp = sum(s[y].values())
            rows.append((ad, y, round(tp, 1), round(g[y], 1), round(100 * tp / g[y], 3), "; ".join(f"{k} {v:.1f}" for k, v in s[y].items() if v)))
    with open(KOK / "gsyh_pay.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["senaryo", "yil", "maliyet_milyar_TL", "gsyh_milyar_TL", "pay_yuzde_gsyh", "kalemler"])
        w.writerows(rows)
    L = ["# Yürütme maliyeti, yıl bazında GSYH payı", "",
         "Çalıştır: `python3 gsyh_pay.py`. Çıktı: `gsyh_pay.csv`. Her yılın maliyeti o yılın GSYH'sine bölünür (yüzde).", "",
         "**Payda varsayımdır.** Repoda GSYH yalnız 2023-2025 (ölçüm). 2026 sonrası: önceki yıl × (1+TÜFE) × (1+reel %3). "
         "TÜFE, `bes_yil_senaryo.csv` senaryo alt/üst ortası; 2029-2030 için senaryo yok, 2028-2031 arası doğrusal. Reel büyüme repoda yok, benim varsayımım.", "",
         "| Yıl | GSYH (mlr TL, varsayım yolu) | Düşük | Orta | Yüksek |", "|---|---|---|---|---|"]
    for y in YILLAR:
        c = [next(r for r in rows if r[0] == ad and r[1] == y) for ad in out]
        L.append(f"| {y} | {g[y]:,.0f} | " + " | ".join(f"{r[2]:,.1f} mlr TL = %{r[4]:.3f}" for r in c) + " |")
    L += ["", "Senaryolar: düşük = ρ %0,4, κ 0,25, en küçük prim senaryosu, adım 4.5 A alt; orta = ρ %9, κ 0,5, orta prim senaryosu, adım 4.5 A ortası; yüksek = ρ %29, κ 1,0, en büyük prim senaryosu, adım 4.5 B üst. Adım 1-2 her üçünde ρ %0,4 (stok mahsubunda yüksek ρ uygulanmaz).", "",
          "Kalemler (yıl, senaryo bazında): " + "", ""]
    for r in rows:
        if r[2]:
            L.append(f"- {r[0]} {r[1]}: {r[5]}")
    L += ["", f"**Adım 5 (toplama girmedi).** Kira transferi (kapsama %50) 2026 fiyatıyla ve yılı belirsiz; yürütme maliyeti düşük/orta/yüksek = {ad5['düşük']:.1f} / {ad5['orta']:.1f} / {ad5['yüksek']:.1f} mlr TL/yıl = GSYH 2026'nın %{100*ad5['düşük']/g[2026]:.3f} / %{100*ad5['orta']/g[2026]:.3f} / %{100*ad5['yüksek']/g[2026]:.3f}'i.", "",
          "**Sınırlar.** Adım 3 ve 4 maliyeti, ρ ile çarpılmış akıştır; ρ dayanağı zayıf (BES_ADIM_MALIYET.md). Üç senaryo tutarlı bir tahmin değil, bant uçlarıdır. Payda yolu tahmin değil; reel büyüme ve 2029-2030 TÜFE'si benim varsayımım."]
    (KOK / "GSYH_PAY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:14]))


if __name__ == "__main__":
    main()
