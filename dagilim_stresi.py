"""Dagilim stresi: olculmus TCMB 2026-Q1 stoklari uzerinde.

Toplam firma mevduati ve borc servisi korunur. Alt dugumlere lognormal
dagitimla atanir. Konsantrasyon parametresi (gini veya ust pay) taranir.
Amac: agregat tampon yerel blokeyi veya ek reel kaybi gizliyor mu?

Stoklar ODEME_ZINCIRI.md ve PR #3'ten: firma mevduati 8.59 tr TL,
aylik borc servisi 1.67 tr TL. FX kredi payi ~0.60. Cekilmemis limit yok.
Kenar olculmus fatura degil; burada da agregat paydan turetilir.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent
TOHUM = 20261010
N = 200  # alt dugum
T = 24
MEVDUAT_TOP = 8.59  # tr TL
SERVIS_AYLIK = 1.67
FX_KREDI_PAY = 0.596
PI_AYLIK = 0.0225  # Ocak 2026

def dagit(toplam: float, n: int, sigma: float, rng: np.random.Generator) -> np.ndarray:
    x = rng.lognormal(0.0, sigma, size=n)
    x = x / x.sum() * toplam
    return x

def calistir(sigma: float, fx_cevirme: bool = False, valf: bool = False) -> dict:
    rng = np.random.default_rng(TOHUM + int(sigma * 1000))
    mevduat = dagit(MEVDUAT_TOP, N, sigma, rng)
    borc_aylik = dagit(SERVIS_AYLIK, N, sigma * 0.8, rng)  # borc biraz daha esit
    # Basit: her dugum kendi servisini mevduattan oder. Yetersizse bloke.
    # FX: cevirilemezse servisin FX payi reel kayip.
    bloke = 0
    reel_kayip = 0.0
    for t in range(T):
        odeyemeyen = mevduat < borc_aylik
        bloke += int(odeyemeyen.mean() >= 0.25 or (mevduat.sum() / borc_aylik.sum()) < 0.70)
        if fx_cevirme:
            kayip = (borc_aylik * FX_KREDI_PAY * odeyemeyen).sum()
            reel_kayip += kayip
            if valf:
                # basit erime: kayip * pi/(1+pi) kadar azalir ama burada nominal
                pass
        # basit guncelleme: odeyebilenler mevduat dusurur (servis odenir)
        mevduat = np.maximum(mevduat - borc_aylik, 0.0)
        # dis akim yok; sadece stres
    return {
        "sigma": sigma,
        "gini_mevduat": float(gini(mevduat)),  # son
        "bloke_periyot": bloke,
        "reel_kayip_tr": reel_kayip,
        "fx": fx_cevirme,
        "valf": valf,
    }

def gini(x: np.ndarray) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    if x.sum() <= 0:
        return 0.0
    n = len(x)
    i = np.arange(1, n + 1)
    return float((2 * np.sum(i * x) / (n * x.sum())) - (n + 1) / n)

def main():
    sonuclar = []
    for sigma in [0.3, 0.6, 1.0, 1.5]:
        for fx in [False, True]:
            for valf in [False, True]:
                if not fx and valf:
                    continue
                sonuclar.append(calistir(sigma, fx, valf))
    df = pd.DataFrame(sonuclar)
    df.to_csv(KOK / "dagilim_stresi.csv", index=False)
    ozet = {
        "not": "Toplam stok korunur. Yuksek sigma = yuksek konsantrasyon. Bloke veya reel kayip artiyorsa agregat tampon dagilimi gizliyor.",
        "sonuclar": sonuclar,
    }
    (KOK / "dagilim_stresi.json").write_text(json.dumps(ozet, indent=2, ensure_ascii=False))
    print(df.to_string(index=False))
    print("Yazildi: dagilim_stresi.csv, dagilim_stresi.json")

if __name__ == "__main__":
    main()
