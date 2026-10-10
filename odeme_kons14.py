"""Tur 14: servis konsantrasyonu baglayici mi. Kurallar kosudan once.

MC 50, tohum TOHUM+14000+s. Mev 0.70 sabit x servis 0.10/0.30/0.50/0.70 (FX ayri).
Kontrol: servis esit x mev 0.10/0.40/0.70.
Lider servis sifir: mev70+srv70, liderin servis payi esit dagitilir.

Curutme: srv 0.10->0.70 kal medyan fark < 2 ve p>0.05 -> servis baglayici elenir.
Lider srv sifir kal dusmuyorsa tek dugum servisi elenir.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import odeme_zinciri as oz
from odeme_dagilim import ISARET, N_FIRMA, agirlik, kos, stok_yukle, ust10
from odeme_gercek import ESIK_VALF
from odeme_kons7 import ag_kur_v2
from odeme_kons8 import lider_dagit, wilcoxon_paired

KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
SEED0 = oz.TOHUM + 14000
MEV70 = 0.70
SRV_GRID = (0.10, 0.30, 0.50, 0.70)
MEV_KONTROL = (0.10, 0.40, 0.70)
PI = 0.0


def agirlik_mev_srv(s: int, mev_k: float, srv_k: float | None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    eq = np.full(N_FIRMA, 1.0 / N_FIRMA)
    mev_w = eq.copy() if mev_k <= 0.101 else agirlik(N_FIRMA, mev_k, SEED0 + s)
    if srv_k is None:
        srv_w = eq.copy()
    else:
        srv_w = eq.copy() if srv_k <= 0.101 else agirlik(N_FIRMA, srv_k, SEED0 + 50000 + s)
    return mev_w, srv_w, eq.copy()


def metrikler(h, yavas, pak, v0: float) -> dict:
    net = pak["net"]
    k = net["kucuk"]
    top = h[oz.F_REEL]
    pay = h[oz.F_REEL_KU] / top if top > 1e-8 else float("nan")
    defter = float(net["w0"][net["idx_ku_al"]].sum() / net["w0"].sum()) if net["w0"].sum() > 0 else float("nan")
    return {
        "kal": float(h[oz.F_KAL]),
        "yerel": float(h[oz.F_YEREL]),
        "reel": float(h[oz.F_REEL] / (v0 * oz.T)),
        "yk": float(np.median(yavas[k]) / oz.T) if np.any(k) else 0.0,
        "fazla": float(pay - defter) if np.isfinite(pay) else float("nan"),
        "ust10_mev": float(pak.get("ust10_mev", float("nan"))),
        "ust10_srv": float(pak.get("ust10_srv", float("nan"))),
    }


def kos_hucre(stok, mev_k: float, srv_k: float | None, fx: bool, s: int, srv_w_override=None) -> dict:
    mev_w, srv_w, alac_w = agirlik_mev_srv(s, mev_k, srv_k)
    if srv_w_override is not None:
        srv_w = srv_w_override
    pak = ag_kur_v2(stok, mev_w, srv_w, alac_w)
    h, _, yavas = kos(pak, PI, fx)
    v0 = float(pak["net"]["w0"].sum())
    return {"s": s, **metrikler(h, yavas, pak, v0)}


def grid_mev70(stok) -> pd.DataFrame:
    rows = []
    for srv_k in SRV_GRID:
        for fx in (False, True):
            for s in range(N_MC):
                rows.append(
                    {"test": "mev70_srv", "mev_k": MEV70, "srv_k": srv_k, "fx": fx, **kos_hucre(stok, MEV70, srv_k, fx, s)}
                )
    return pd.DataFrame(rows)


def grid_mev_kontrol(stok) -> pd.DataFrame:
    rows = []
    for mev_k in MEV_KONTROL:
        for fx in (False, True):
            for s in range(N_MC):
                rows.append(
                    {"test": "mev_kontrol", "mev_k": mev_k, "srv_k": None, "fx": fx, **kos_hucre(stok, mev_k, None, fx, s)}
                )
    return pd.DataFrame(rows)


def lider_servis(stok) -> pd.DataFrame:
    rows = []
    for fx in (False, True):
        for lider_sifir in (False, True):
            for s in range(N_MC):
                mev_w, srv_w, alac_w = agirlik_mev_srv(s, MEV70, MEV70)
                sw = lider_dagit(srv_w, int(np.argmax(mev_w))) if lider_sifir else srv_w
                pak = ag_kur_v2(stok, mev_w, sw, alac_w)
                h, _, yavas = kos(pak, PI, fx)
                v0 = float(pak["net"]["w0"].sum())
                rows.append(
                    {
                        "test": "lider_srv",
                        "fx": fx,
                        "lider_srv_sifir": lider_sifir,
                        "s": s,
                        **metrikler(h, yavas, pak, v0),
                    }
                )
    return pd.DataFrame(rows)


def ozet(df: pd.DataFrame) -> pd.DataFrame:
    gcols = ["test"]
    for c in ("mev_k", "srv_k", "fx", "lider_srv_sifir"):
        if c in df.columns:
            gcols.append(c)
    agg = {
        "kal": ("kal", "mean"),
        "yerel": ("yerel", "mean"),
        "reel": ("reel", "mean"),
        "yk": ("yk", "mean"),
        "fazla": ("fazla", "median"),
    }
    if "ust10_mev" in df.columns:
        agg["ust10_mev"] = ("ust10_mev", "mean")
    if "ust10_srv" in df.columns:
        agg["ust10_srv"] = ("ust10_srv", "mean")
    return df.groupby(gcols, dropna=False).agg(**agg).reset_index()


def grafik(tablo: pd.DataFrame, dosya: Path) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(9, 4))
    sub = tablo[(tablo.test == "mev70_srv") & tablo.fx]
    if sub.empty:
        plt.close(fig)
        return
    x = np.array(SRV_GRID)
    ax[0].plot(x, [sub[sub.srv_k == k].kal.iloc[0] for k in SRV_GRID], "o-", label="FX çevrilemez")
    sub2 = tablo[(tablo.test == "mev70_srv") & (~tablo.fx)]
    ax[0].plot(x, [sub2[sub2.srv_k == k].kal.iloc[0] for k in SRV_GRID], "s-", label="FX çevrilebilir")
    ax[0].set_xlabel("Servis üst %10 hedefi")
    ax[0].set_ylabel("Kalıcılık")
    ax[0].legend(frameon=False, fontsize=8)
    ax[1].plot(x, [sub[sub.srv_k == k].reel.iloc[0] for k in SRV_GRID], "o-")
    ax[1].set_xlabel("Servis üst %10")
    ax[1].set_ylabel("Reel (FX çevrilemez)")
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def _spearman_satir(etiket: str, fx: str, ad: str, r, p) -> str:
    if r is None or p is None or (isinstance(r, float) and np.isnan(r)):
        return f"Spearman ({etiket}, {fx}): {ad} tanımsız (tüm hücrelerde kal=0)."
    return f"Spearman ({etiket}, {fx}): {ad} {r:.3f} (p = {p:.4g})."


def rapor(sonuc: dict, ozet_df: pd.DataFrame) -> str:
    k = sonuc["karar"]
    s = [
        "# Ödeme zinciri, tur 14: servis konsantrasyonu",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Varsayımlar",
        "",
        f"150 firma. Lider = en yüksek mevduatlı sentetik düğüm (isim yok). MC {N_MC}, tohum {SEED0}+s. "
        f"π = {PI} (Tur 7 ile uyum). Valf eşiği {ESIK_VALF}. FX çevrilebilir/çevrilemez ayrı.",
        "",
        f"Servis konsantrasyonu bağlayıcı: {k['srv_baglayici']}. Tek düğüm servisi: {k['lider_srv_belirler']}. "
        f"Mevduat tek başına (servis eşit): kal FX çevrilebilir mev70 = {k['mev70_eq_kal_fxroll']:.2f}.",
        "",
        f"Spearman (mev70_srv, FX çevrilebilir): servis–kalıcılık {k['sp_srv_kal']:.3f} (p = {k['sp_srv_kal_p']:.4g}).",
        _spearman_satir("mev_kontrol", "FX çevrilemez", "mevduat–kalıcılık", k["sp_mev_kal"], k["sp_mev_kal_p"]),
        "",
        "### Mev 0,70 × servis (ortalama)",
        "",
        "| srv %10 | FX | Kalıcılık | Yerel | Küçük yavaş | Reel |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    m = ozet_df[ozet_df.test == "mev70_srv"]
    for _, r in m.iterrows():
        s.append(
            f"| {r.srv_k:.2f} | {'çevrilemez' if r.fx else 'çevrilebilir'} | {r.kal:.2f} | {r.yerel:.2f} | "
            f"{r.yk:.3f} | {r.reel:.3f} |"
        )
    s.extend(["", "### Mevduat kontrol (servis eşit)", "", "| Mev %10 | FX | Kalıcılık | Reel |", "| ---: | --- | ---: | ---: |"])
    c = ozet_df[ozet_df.test == "mev_kontrol"]
    for _, r in c.iterrows():
        s.append(f"| {r.mev_k:.2f} | {'çevrilemez' if r.fx else 'çevrilebilir'} | {r.kal:.2f} | {r.reel:.3f} |")
    s.extend([
        "",
        f"### Lider servis sıfır (mev70+srv70, FX çevrilebilir): kal fark medyan {k['lider_dkal']:.2f}, p = {k['lider_p']:.4g}.",
        "",
        "Tekrar: `python3 odeme_zinciri.py`.",
        "",
        "Dosyalar: `odeme_kons14_hucre.csv`, `odeme_kons14.png`, `odeme_kons14_sonuc.json`.",
        "",
    ])
    return "\n".join(s)


def main_kons14() -> None:
    stok = stok_yukle()
    print("kons14", N_MC, "seed", SEED0, flush=True)
    df1 = grid_mev70(stok)
    df2 = grid_mev_kontrol(stok)
    df3 = lider_servis(stok)
    df = pd.concat([df1, df2, df3], ignore_index=True)
    df.to_csv(KOK / "odeme_kons14_hucre.csv", index=False)
    oz = ozet(df)
    grafik(oz, KOK / "odeme_kons14.png")

    # Servis 0.10 vs 0.70 paired (mev70), FX rollable where tur7 effect
    d10 = df1[(df1.srv_k == 0.10) & (~df1.fx)].sort_values("s")
    d70 = df1[(df1.srv_k == 0.70) & (~df1.fx)].sort_values("s")
    p_srv, d_srv = wilcoxon_paired(d70["kal"], d10["kal"], "greater")
    srv_baglayici = bool(d_srv >= 2.0 and p_srv < 0.05)

    # Also check FX non-rollover
    d10f = df1[(df1.srv_k == 0.10) & df1.fx].sort_values("s")
    d70f = df1[(df1.srv_k == 0.70) & df1.fx].sort_values("s")
    p_srv2, d_srv2 = wilcoxon_paired(d70f["kal"], d10f["kal"], "greater")

    sp_srv, sp_srv_p = spearmanr(
        df1[~df1.fx]["srv_k"], df1[~df1.fx]["kal"]
    ) if len(df1) > 3 else (float("nan"), float("nan"))
    sp_mev, sp_mev_p = spearmanr(
        df2[df2.fx]["mev_k"], df2[df2.fx]["kal"]
    ) if len(df2) > 3 else (float("nan"), float("nan"))

    mev70_eq = df2[(df2.mev_k == 0.70) & (~df2.fx)]["kal"].mean()

    ld = df3[(df3.fx == False) & (~df3.lider_srv_sifir)].sort_values("s")
    ls = df3[(df3.fx == False) & df3.lider_srv_sifir].sort_values("s")
    p_ld, d_ld = wilcoxon_paired(ld["kal"], ls["kal"], "greater")
    lider_srv_belirler = bool(d_ld >= 2.0 and p_ld < 0.05)

    karar = {
        "srv_baglayici": srv_baglayici,
        "srv_fark_roll": d_srv,
        "srv_p_roll": p_srv,
        "srv_fark_fx": d_srv2,
        "srv_p_fx": p_srv2,
        "sp_srv_kal": float(sp_srv),
        "sp_srv_kal_p": float(sp_srv_p),
        "sp_mev_kal": float(sp_mev),
        "sp_mev_kal_p": float(sp_mev_p),
        "mev70_eq_kal_fxroll": mev70_eq,
        "lider_dkal": d_ld,
        "lider_p": p_ld,
        "lider_srv_belirler": lider_srv_belirler,
    }

    ozet_metin = (
        f"Mev 0,70: servis 0,10→0,70 kal fark (FX çevrilebilir) medyan {d_srv:.2f}, p = {p_srv:.3g}; "
        f"FX çevrilemez {d_srv2:.2f}, p = {p_srv2:.3g}. "
        f"Servis konsantrasyonu {'desteklenir' if srv_baglayici else 'elenir (kayıtlı eşik)'}. "
        f"Mevduat tek başına (servis eşit) kal çevrilebilir mev70 = {mev70_eq:.2f}. "
        f"Lider servis sıfır: kal fark {d_ld:.2f}, p = {p_ld:.3g} — "
        f"{'tek düğüm servisi desteklenir' if lider_srv_belirler else 'elenir'}."
    )

    def _jd(o):
        if isinstance(o, float) and (np.isnan(o) or np.isinf(o)):
            return None
        raise TypeError(type(o))

    sonuc = {
        "uyari": "Lider sentetik; TCMB sektör payı. Kenar varsayım.",
        "ozet": ozet_metin,
        "karar": karar,
        "n_mc": N_MC,
        "seed0": SEED0,
    }
    (KOK / "odeme_kons14_sonuc.json").write_text(
        json.dumps(json.loads(json.dumps(sonuc, default=_jd)), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, tur 14") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor(sonuc, oz) + ISARET + eski, encoding="utf-8")
    print(ozet_metin)


if __name__ == "__main__":
    main_kons14()
