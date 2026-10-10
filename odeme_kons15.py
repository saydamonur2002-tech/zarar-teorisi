"""Tur 15: servis esigi (0.50–0.70) ve servis artisi. Kurallar kosudan once.

MC 50, tohum TOHUM+15000+s. Mev 0.70 sabit; servis ust %10: 0.50/0.55/0.60/0.65/0.70.
Lider servis sifir: mev70+srv70 (Tur 14 tekrari).

Curutme: 0.55–0.65 bandinda kal artmiyorsa sicrama 0.70'e ozgu.
Servis artisi (srv_k-0.10) ile kal Spearman < 0.3 ve p>0.05 ise arti baglayici zayiflar.
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
from odeme_dagilim import ISARET, N_FIRMA, agirlik, kos, stok_yukle
from odeme_gercek import ESIK_VALF
from odeme_kons7 import ag_kur_v2
from odeme_kons8 import lider_dagit, wilcoxon_paired

KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
SEED0 = oz.TOHUM + 15000
MEV70 = 0.70
SRV_GRID = (0.50, 0.55, 0.60, 0.65, 0.70)
SRV_BASE = 0.10
PI = 0.0
BAND = (0.55, 0.60, 0.65)
FAZLA_ESIK = 0.05


def agirlik_mev_srv(s: int, mev_k: float, srv_k: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    eq = np.full(N_FIRMA, 1.0 / N_FIRMA)
    mev_w = eq.copy() if mev_k <= 0.101 else agirlik(N_FIRMA, mev_k, SEED0 + s)
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


def kos_hucre(stok, srv_k: float, fx: bool, s: int, srv_w_override=None) -> dict:
    mev_w, srv_w, alac_w = agirlik_mev_srv(s, MEV70, srv_k)
    if srv_w_override is not None:
        srv_w = srv_w_override
    pak = ag_kur_v2(stok, mev_w, srv_w, alac_w)
    h, _, yavas = kos(pak, PI, fx)
    v0 = float(pak["net"]["w0"].sum())
    return {
        "s": s,
        "srv_artis": srv_k - SRV_BASE,
        **metrikler(h, yavas, pak, v0),
    }


def grid_esik(stok) -> pd.DataFrame:
    rows = []
    for srv_k in SRV_GRID:
        for fx in (False, True):
            for s in range(N_MC):
                rows.append(
                    {
                        "test": "esik",
                        "mev_k": MEV70,
                        "srv_k": srv_k,
                        "fx": fx,
                        **kos_hucre(stok, srv_k, fx, s),
                    }
                )
    return pd.DataFrame(rows)


def lider_servis(stok) -> pd.DataFrame:
    rows = []
    for fx in (False, True):
        for lider_sifir in (False, True):
            for s in range(N_MC):
                mev_w, srv_w, alac_w = agirlik_mev_srv(s, MEV70, 0.70)
                sw = lider_dagit(srv_w, int(np.argmax(mev_w))) if lider_sifir else srv_w
                pak = ag_kur_v2(stok, mev_w, sw, alac_w)
                h, _, yavas = kos(pak, PI, fx)
                v0 = float(pak["net"]["w0"].sum())
                rows.append(
                    {
                        "test": "lider_srv",
                        "mev_k": MEV70,
                        "srv_k": 0.70,
                        "fx": fx,
                        "lider_srv_sifir": lider_sifir,
                        "s": s,
                        "srv_artis": 0.70 - SRV_BASE,
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
        "srv_artis": ("srv_artis", "mean"),
    }
    if "ust10_srv" in df.columns:
        agg["ust10_srv"] = ("ust10_srv", "mean")
    return df.groupby(gcols, dropna=False).agg(**agg).reset_index()


def grafik(tablo: pd.DataFrame, dosya: Path) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(9, 4))
    x = np.array(SRV_GRID)
    sub = tablo[(tablo.test == "esik") & tablo.fx]
    sub2 = tablo[(tablo.test == "esik") & (~tablo.fx)]
    ax[0].plot(x, [sub[sub.srv_k == k].kal.iloc[0] for k in SRV_GRID], "o-", label="FX çevrilemez")
    ax[0].plot(x, [sub2[sub2.srv_k == k].kal.iloc[0] for k in SRV_GRID], "s-", label="FX çevrilebilir")
    ax[0].set_xlabel("Servis üst %10 hedefi")
    ax[0].set_ylabel("Kalıcılık (ortalama)")
    ax[0].legend(frameon=False, fontsize=8)
    ax[1].plot(x, [sub[sub.srv_k == k].reel.iloc[0] for k in SRV_GRID], "o-", label="FX çevrilemez")
    ax[1].set_xlabel("Servis üst %10")
    ax[1].set_ylabel("Reel kayıp")
    ax[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def _spearman_satir(etiket: str, fx: str, ad: str, r, p) -> str:
    if r is None or p is None or (isinstance(r, float) and np.isnan(r)):
        return f"Spearman ({etiket}, {fx}): {ad} tanımsız."
    return f"Spearman ({etiket}, {fx}): {ad} {r:.3f} (p = {p:.4g})."


def band_kal_artisi(df: pd.DataFrame, fx: bool) -> tuple[float, float, bool]:
    """Band (0.55–0.65) max kal vs 0.50 kal, esli MC; band artmiyor mu."""
    d50 = df[(df.srv_k == 0.50) & (df.fx == fx)].sort_values("s")
    band_max = []
    for s in range(N_MC):
        sub = df[(df.srv_k.isin(BAND)) & (df.fx == fx) & (df.s == s)]
        band_max.append(float(sub["kal"].max()) if len(sub) else 0.0)
    band_max = np.asarray(band_max)
    k50 = d50["kal"].to_numpy()
    p, d = wilcoxon_paired(band_max, k50, "greater")
    artmiyor = bool(d < 2.0 or p >= 0.05)
    return d, p, artmiyor


def rapor(sonuc: dict, ozet_df: pd.DataFrame) -> str:
    k = sonuc["karar"]
    s = [
        "# Ödeme zinciri, tur 15: servis eşiği",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Varsayımlar",
        "",
        f"150 firma. Lider = en yüksek mevduatlı sentetik düğüm. MC {N_MC}, tohum {SEED0}+s. "
        f"Mevduat üst %10 = {MEV70}. Servis eşiği {SRV_GRID}. π = {PI}. Valf {ESIK_VALF}. "
        f"Servis artısı = srv hedefi − {SRV_BASE} (eşit dağılım referansı). FX ayrı.",
        "",
        f"Sıçrama 0,70'e özgü (band 0,55–0,65 kal artmıyor): {k['sicrama_070_ozgu_roll']} (FX çevrilebilir), "
        f"{k['sicrama_070_ozgu_fx']} (FX çevrilemez).",
        f"Servis artısı bağlayıcı zayıflar: {k['artis_zayif_roll']} (FX çevrilebilir), {k['artis_zayif_fx']} (FX çevrilemez).",
        "",
        _spearman_satir("esik", "FX çevrilebilir", "servis artısı–kalıcılık", k["sp_artis_kal_roll"], k["sp_artis_kal_roll_p"]),
        _spearman_satir("esik", "FX çevrilebilir", "servis artısı–küçük yavaş", k["sp_artis_yk_roll"], k["sp_artis_yk_roll_p"]),
        _spearman_satir("esik", "FX çevrilemez", "servis artısı–kalıcılık", k["sp_artis_kal_fx"], k["sp_artis_kal_fx_p"]),
        _spearman_satir("esik", "FX çevrilemez", "servis artısı–küçük yavaş", k["sp_artis_yk_fx"], k["sp_artis_yk_fx_p"]),
        "",
        f"Lider servis sıfır (mev70+srv70, FX çevrilebilir): kal fark medyan {k['lider_dkal']:.2f}, p = {k['lider_p']:.4g}.",
        "",
        f"Reel artış (FX çevrilemez, srv 0,70 − 0,50): medyan {k['d_reel_median']:.4f}, p = {k['d_reel_p']:.4g}. "
        f"Küçük fazla medyan (srv 0,70): {k['fazla70_med']:.4f}; P(fazla≥{FAZLA_ESIK:.2f}) = {k['p_fazla70']:.2f}.",
        "",
        "### Servis eşiği (mev 0,70, ortalama)",
        "",
        "| srv %10 | FX | Kalıcılık | Yerel | Küçük yavaş | Reel |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    m = ozet_df[ozet_df.test == "esik"].sort_values(["srv_k", "fx"])
    for _, r in m.iterrows():
        s.append(
            f"| {r.srv_k:.2f} | {'çevrilemez' if r.fx else 'çevrilebilir'} | {r.kal:.2f} | {r.yerel:.2f} | "
            f"{r.yk:.3f} | {r.reel:.3f} |"
        )
    s.extend([
        "",
        "Tekrar: `python3 odeme_zinciri.py`.",
        "",
        "Dosyalar: `odeme_kons15_hucre.csv`, `odeme_kons15.png`, `odeme_kons15_sonuc.json`.",
        "",
    ])
    return "\n".join(s)


def main_kons15() -> None:
    stok = stok_yukle()
    print("kons15", N_MC, "seed", SEED0, flush=True)
    df1 = grid_esik(stok)
    df2 = lider_servis(stok)
    df = pd.concat([df1, df2], ignore_index=True)
    df.to_csv(KOK / "odeme_kons15_hucre.csv", index=False)
    oz = ozet(df)
    grafik(oz, KOK / "odeme_kons15.png")

    def sp_subset(fx: bool, col_y: str):
        sub = df1[df1.fx == fx]
        if len(sub) < 3:
            return float("nan"), float("nan")
        r, p = spearmanr(sub["srv_artis"], sub[col_y])
        return float(r), float(p)

    sp_k_roll, sp_k_roll_p = sp_subset(False, "kal")
    sp_y_roll, sp_y_roll_p = sp_subset(False, "yk")
    sp_k_fx, sp_k_fx_p = sp_subset(True, "kal")
    sp_y_fx, sp_y_fx_p = sp_subset(True, "yk")

    artis_zayif_roll = bool(sp_k_roll < 0.3 and sp_k_roll_p > 0.05) if np.isfinite(sp_k_roll) else False
    artis_zayif_fx = bool(sp_k_fx < 0.3 and sp_k_fx_p > 0.05) if np.isfinite(sp_k_fx) else False

    d_band_roll, p_band_roll, band_roll_artmiyor = band_kal_artisi(df1, False)
    d_band_fx, p_band_fx, band_fx_artmiyor = band_kal_artisi(df1, True)
    kal70_roll = df1[(df1.srv_k == 0.70) & (~df1.fx)]["kal"].median()
    kal70_fx = df1[(df1.srv_k == 0.70) & df1.fx]["kal"].median()
    sicrama_070_ozgu_roll = bool(band_roll_artmiyor and kal70_roll >= 2.0)
    sicrama_070_ozgu_fx = bool(band_fx_artmiyor and kal70_fx >= 2.0)

    d70f = df1[(df1.srv_k == 0.70) & df1.fx].sort_values("s")
    d50f = df1[(df1.srv_k == 0.50) & df1.fx].sort_values("s")
    p_reel, d_reel = wilcoxon_paired(d70f["reel"], d50f["reel"], "greater")
    faz70 = d70f["fazla"].dropna()
    fazla70_med = float(faz70.median()) if faz70.size else float("nan")
    p_fazla70 = float((faz70 >= FAZLA_ESIK).mean()) if faz70.size else float("nan")

    ld = df2[(~df2.fx) & (~df2.lider_srv_sifir)].sort_values("s")
    ls = df2[(~df2.fx) & df2.lider_srv_sifir].sort_values("s")
    p_ld, d_ld = wilcoxon_paired(ld["kal"], ls["kal"], "greater")

    karar = {
        "sicrama_070_ozgu_roll": sicrama_070_ozgu_roll,
        "sicrama_070_ozgu_fx": sicrama_070_ozgu_fx,
        "band_d_roll": d_band_roll,
        "band_p_roll": p_band_roll,
        "band_d_fx": d_band_fx,
        "band_p_fx": p_band_fx,
        "kal70_median_roll": float(kal70_roll),
        "kal70_median_fx": float(kal70_fx),
        "artis_zayif_roll": artis_zayif_roll,
        "artis_zayif_fx": artis_zayif_fx,
        "sp_artis_kal_roll": sp_k_roll,
        "sp_artis_kal_roll_p": sp_k_roll_p,
        "sp_artis_yk_roll": sp_y_roll,
        "sp_artis_yk_roll_p": sp_y_roll_p,
        "sp_artis_kal_fx": sp_k_fx,
        "sp_artis_kal_fx_p": sp_k_fx_p,
        "sp_artis_yk_fx": sp_y_fx,
        "sp_artis_yk_fx_p": sp_y_fx_p,
        "lider_dkal": d_ld,
        "lider_p": p_ld,
        "d_reel_median": d_reel,
        "d_reel_p": p_reel,
        "fazla70_med": fazla70_med,
        "p_fazla70": p_fazla70,
    }

    sicrama_metin = (
        "0,70'e özgü (band 0,55–0,65 artmıyor)"
        if sicrama_070_ozgu_roll
        else "kademeli: 0,50→0,70 arası kal artıyor, yalnızca 0,70 sıçraması değil"
    )
    ozet_metin = (
        f"Eşik taraması (FX çevrilebilir): kal ort. 0,50={df1[(df1.srv_k==0.50)&(~df1.fx)]['kal'].mean():.2f}, "
        f"0,55={df1[(df1.srv_k==0.55)&(~df1.fx)]['kal'].mean():.2f}, 0,60={df1[(df1.srv_k==0.60)&(~df1.fx)]['kal'].mean():.2f}, "
        f"0,65={df1[(df1.srv_k==0.65)&(~df1.fx)]['kal'].mean():.2f}, 0,70={df1[(df1.srv_k==0.70)&(~df1.fx)]['kal'].mean():.2f}; "
        f"{sicrama_metin}. "
        f"Servis artısı–kal Spearman (FX çevrilebilir) {sp_k_roll:.3f} (p = {sp_k_roll_p:.3g}); "
        f"{'artı bağlayıcı zayıflar' if artis_zayif_roll else 'artı–kal ilişkisi güçlü/kayıtlı eşik altında değil'}. "
        f"Lider servis sıfır kal fark {d_ld:.2f}, p = {p_ld:.3g}. "
        f"Reel artış 0,70−0,50 (FX çevrilemez) medyan {d_reel:.4f}; küçük fazla medyan {fazla70_med:.4f}, "
        f"P(fazla≥0,05) = {p_fazla70:.2f}."
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
    (KOK / "odeme_kons15_sonuc.json").write_text(
        json.dumps(json.loads(json.dumps(sonuc, default=_jd)), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, tur 15") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor(sonuc, oz) + ISARET + eski, encoding="utf-8")
    print(ozet_metin)


if __name__ == "__main__":
    main_kons15()
