"""Dagilim stresi — olculmus 2026-Q1 stoklarina bagli (temiz).

Toplam firma mevduati 8.59 tr TL, aylik borc servisi 1.67 tr TL (PR #3).
Alt dugumlere lognormal. Baslangic tampon = mevduat / aylik servis.
Sikintili: tampon < 3 ay.
Bloke periyot sayaci: ufuk icinde sikintili pay >= %25 olan periyot.
Kisa ufuk (6 ay) + sabit dis akim (toplam servisi karsilar, dagilim bozulmaz).
FX cevirilemezse sikintili dugumlerin FX servisi reel kayip.

Soru: agregat 5.1x varken yuksek konsantrasyon yerel sikinti payini veya reel kaybi buyutuyor mu?
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent
TOHUM = 20261010
N = 200
T = 6                       # kisa ufuk
MEVDUAT_TOP = 8.59
SERVIS_AYLIK = 1.67
FX_KREDI_PAY = 0.596
PI_AYLIK = 0.0225
TAMPON_ESIK = 3.0           # ay

def dagit(toplam: float, n: int, sigma: float, rng: np.random.Generator) -> np.ndarray:
    x = rng.lognormal(0.0, sigma, size=n)
    return x / x.sum() * toplam

def gini(x: np.ndarray) -> float:
    x = np.sort(np.maximum(x, 0.0))
    s = x.sum()
    if s <= 0:
        return 0.0
    n = len(x)
    i = np.arange(1, n + 1)
    return float((2 * np.sum(i * x) / (n * s)) - (n + 1) / n)

def calistir(sigma: float, fx: bool = False, valf: bool = False) -> dict:
    rng = np.random.default_rng(TOHUM + int(sigma * 1000) + int(fx) * 17 + int(valf) * 31)
    mevduat = dagit(MEVDUAT_TOP, N, sigma, rng)
    servis = dagit(SERVIS_AYLIK, N, max(0.1, sigma * 0.6), rng)
    # dis akim: toplamda servisi karsilar, her dugume kendi servisi kadar gelir
    # (agregat tampon korunur, sadece dagilim farki kalir)
    dis_akis = servis.copy()

    tampon_bas = mevduat / np.maximum(servis, 1e-9)
    m = mevduat.copy()
    sik_paylari = []
    bloke = 0
    reel = 0.0

    for t in range(T):
        oran = m / np.maximum(servis, 1e-9)
        sik = oran < TAMPON_ESIK
        pay = float(sik.mean())
        sik_paylari.append(pay)
        if pay >= 0.25:
            bloke += 1
        if fx:
            kayip = float((servis * FX_KREDI_PAY * sik).sum())
            if valf:
                kayip *= (1.0 - PI_AYLIK / (1.0 + PI_AYLIK))
            reel += kayip
        # guncelle: servis odenir, dis akim gelir -> net sifir, tampon korunur
        m = np.maximum(m - servis + dis_akis, 0.0)

    return {
        "sigma": round(sigma, 2),
        "gini_mev": round(gini(mevduat), 3),
        "tampon_medyan": round(float(np.median(tampon_bas)), 2),
        "tampon_p10": round(float(np.percentile(tampon_bas, 10)), 2),
        "tampon_p90": round(float(np.percentile(tampon_bas, 90)), 2),
        "bas_sik_pay": round(float((tampon_bas < TAMPON_ESIK).mean()), 3),
        "bloke_periyot": bloke,
        "ort_sik_pay": round(float(np.mean(sik_paylari)), 3),
        "reel_kayip_tr": round(reel, 3),
        "fx": fx,
        "valf": valf,
    }

def main():
    sonuclar = []
    for sigma in [0.15, 0.4, 0.7, 1.1]:
        for fx in [False, True]:
            for valf in [False, True]:
                if not fx and valf:
                    continue
                sonuclar.append(calistir(sigma, fx, valf))

    df = pd.DataFrame(sonuclar)
    df.to_csv(KOK / "dagilim_stresi.csv", index=False)
    ozet = {
        "kaynak": "TCMB 2026-Q1 olculmus: firma mevduati 8.59 tr TL, aylik servis 1.67 tr TL (agregat ~5.1 ay)",
        "model": "lognormal dagilim, toplam korunur; dis akim her dugume kendi servisini verir (agregat tampon sabit)",
        "sikintili": "tampon < 3 ay",
        "bloke": "sikintili dugum payi >= 0.25 olan periyot sayisi (ufuk 6)",
        "soru": "yuksek konsantrasyon yerel sikinti payini veya FX reel kaybini artiriyor mu?",
        "sonuclar": sonuclar,
    }
    (KOK / "dagilim_stresi.json").write_text(json.dumps(ozet, indent=2, ensure_ascii=False))
    print(df.to_string(index=False))
    print("\nYazildi: dagilim_stresi.csv, dagilim_stresi.json")

if __name__ == "__main__":
    main()
