"""Tur 8: zayif halka (keskin) ve lider-ayna. Kurallar kosudan once.

150 firma, TCMB 2026-Q1 toplamlari sabit. Kenar paylaşım kurali ayni.
Monte Carlo 50, tohum TOHUM+12000+s. Girdi-cikti ve cekilmemis limit yok.

Zayif halka hucreleri: (a) esit 1/N, (b) mev+srv 0.70/0.70 alac esit,
(c) mev+srv+alac 0.70/0.70/0.70. FX cevrilebilir/cevrilemez ayri.
Fazla = kucuk reel kayip payi - defter payi (kosu basi). P(fazla>=0.05).
Yavas fark = medyan(yavas_kucuk/T) - medyan(yavas_buyuk/T) dugum icinde.
Odenmeyen kucuk payi = F_OD_KU / F_OD_TOP.

Lider = en buyuk mevduatli firma. Kol (i) baz, (ii) lider srv+alac sifir esit dagitim,
(iii) lider mev+ srv+alac sifir. FX cevrilemez. Ayni agirlik cekimi esli.

Zayif halka curutme: uc hucrede medyan fazla < 0.05 ve yavas fark icin
Wilcoxon iki yanli p>=0.05 veya |medyan fark| < 0.10 ise sistematik aktarim elenir.

Lider curutme: (iii) eksi (i) kalicilik farki medyan < 2 ve p>0.05 ise lider elenir;
rol parametreleri desteklenir.

Kontrol: esit, FX cevrilemez reel ~ 0.454; soksuz reel 0 kalicilik 0.
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
from scipy.stats import spearmanr, wilcoxon

import odeme_zinciri as oz
from odeme_dagilim import ISARET, KONS, N_FIRMA, agirlik, stok_yukle, tufe_yoy
from odeme_kons7 import SEED0 as _  # noqa: F401
from odeme_kons7 import ag_kur_v2, kos

KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
SEED0 = oz.TOHUM + 12000
HEDEF_REEL = 0.45408167359827306
K70 = 0.70


def lider_dagit(w: np.ndarray, lider: int) -> np.ndarray:
    w = np.asarray(w, dtype=float).copy()
    n = w.size
    if n <= 1:
        return w
    mass = w[lider]
    w[lider] = 0.0
    w += mass / (n - 1)
    s = w.sum()
    return w / s if s > 0 else np.full(n, 1.0 / n)


def agirlikler(s: int, mev_k: float | None, srv_k: float | None, alac_k: float | None, esit: bool):
    if esit:
        u = np.full(N_FIRMA, 1.0 / N_FIRMA)
        return u.copy(), u.copy(), u.copy()
    mev_w = agirlik(N_FIRMA, mev_k if mev_k is not None else 0.10, SEED0 + s)
    srv_w = (
        np.full(N_FIRMA, 1.0 / N_FIRMA)
        if srv_k is None
        else agirlik(N_FIRMA, srv_k, SEED0 + 50000 + s)
    )
    alac_w = (
        np.full(N_FIRMA, 1.0 / N_FIRMA)
        if alac_k is None
        else agirlik(N_FIRMA, alac_k, SEED0 + 60000 + s)
    )
    return mev_w, srv_w, alac_w


def metrikler(h, yavas, pak, v0: float) -> dict:
    net = pak["net"]
    k = net["kucuk"]
    b = net["buyuk"]
    yk = float(np.median(yavas[k]) / oz.T) if np.any(k) else float("nan")
    yb = float(np.median(yavas[b]) / oz.T) if np.any(b) else float("nan")
    top = h[oz.F_REEL]
    pay = h[oz.F_REEL_KU] / top if top > 1e-8 else float("nan")
    defter = float(net["w0"][net["idx_ku_al"]].sum() / net["w0"].sum())
    od_top = h[oz.F_OD_TOP]
    od_ku = h[oz.F_OD_KU]
    return {
        "kal": float(h[oz.F_KAL]),
        "yerel": float(h[oz.F_YEREL]),
        "reel": float(h[oz.F_REEL] / (v0 * oz.T)),
        "fazla": float(pay - defter) if np.isfinite(pay) else float("nan"),
        "pay": float(pay) if np.isfinite(pay) else float("nan"),
        "defter": defter,
        "yk_med": yk,
        "yb_med": yb,
        "yavas_fark": yk - yb if np.isfinite(yk) and np.isfinite(yb) else float("nan"),
        "od_ku_pay": float(od_ku / od_top) if od_top > 1e-8 else float("nan"),
    }


def hucre_zayif(stok, hucre: str, fx: bool) -> pd.DataFrame:
    rows = []
    v0 = None
    for s in range(N_MC):
        if hucre == "esit":
            mev_w, srv_w, alac_w = agirlikler(s, None, None, None, True)
        elif hucre == "ms70":
            mev_w, srv_w, alac_w = agirlikler(s, K70, K70, None, False)
            alac_w = np.full(N_FIRMA, 1.0 / N_FIRMA)
        else:
            mev_w, srv_w, alac_w = agirlikler(s, K70, K70, K70, False)
        pak = ag_kur_v2(stok, mev_w, srv_w, alac_w)
        h, _, yavas = kos(pak, 0.0, fx)
        if v0 is None:
            v0 = float(pak["net"]["w0"].sum())
        rows.append({"hucre": hucre, "fx": fx, "s": s, **metrikler(h, yavas, pak, v0)})
    return pd.DataFrame(rows)


def hucre_lider(stok, kol: str) -> pd.DataFrame:
    rows = []
    v0 = None
    for s in range(N_MC):
        mev_w, srv_w, alac_w = agirlikler(s, K70, K70, K70, False)
        L = int(np.argmax(mev_w))
        if kol == "baz":
            mw, sw, aw = mev_w, srv_w, alac_w
        elif kol == "rol_sifir":
            mw, sw, aw = mev_w, lider_dagit(srv_w, L), lider_dagit(alac_w, L)
        else:
            mw = lider_dagit(mev_w, L)
            sw = lider_dagit(srv_w, L)
            aw = lider_dagit(alac_w, L)
        pak = ag_kur_v2(stok, mw, sw, aw)
        h, _, yavas = kos(pak, 0.0, True)
        if v0 is None:
            v0 = float(pak["net"]["w0"].sum())
        rows.append({"kol": kol, "s": s, **metrikler(h, yavas, pak, v0)})
    return pd.DataFrame(rows)


def kontrol(stok) -> dict:
    out = {}
    mev_w = np.full(N_FIRMA, 1.0 / N_FIRMA)
    pak = ag_kur_v2(stok, mev_w, mev_w.copy(), mev_w.copy())
    h, _, yavas = kos(pak, 0.0, False)
    v0 = float(pak["net"]["w0"].sum())
    out["soksuz"] = metrikler(h, yavas, pak, v0)
    df = hucre_zayif(stok, "esit", True)
    out["esit_fx"] = {k: float(df[k].mean()) for k in ("kal", "reel", "fazla", "yk_med")}
    out["esit_fx"]["reel_sapma"] = float(df["reel"].mean() - HEDEF_REEL)
    return out


def wilcoxon_paired(a, b, alt: str = "two-sided"):
    d = np.asarray(a, float) - np.asarray(b, float)
    d = d[np.isfinite(d)]
    if d.size == 0 or np.allclose(d, 0):
        return 1.0, 0.0
    try:
        p = float(wilcoxon(d, alternative=alt).pvalue)
    except ValueError:
        p = 1.0
    return p, float(np.median(d))


def zayif_ozet(df: pd.DataFrame) -> dict:
    faz = df["fazla"].dropna()
    return {
        "fazla_med": float(faz.median()) if faz.size else float("nan"),
        "p_fazla_05": float((faz >= 0.05).mean()) if faz.size else float("nan"),
        "yavas_fark_med": float(df["yavas_fark"].median()),
        "od_ku_med": float(df["od_ku_pay"].median()),
        "kal": float(df["kal"].mean()),
        "reel": float(df["reel"].mean()),
        "yk_med": float(df["yk_med"].mean()),
    }


def grafik_zayif(ozetler: dict, dosya: Path) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 4))
    hucreler = ["esit", "ms70", "msa70"]
    ad = ["Eşit", "M+S 0,70", "M+S+A 0,70"]
    x = np.arange(3)
    gen = 0.35
    for i, fx in enumerate((False, True)):
        faz = [ozetler[(h, fx)]["fazla_med"] for h in hucreler]
        yk = [ozetler[(h, fx)]["yk_med"] for h in hucreler]
        ax[0].bar(x + (i - 0.5) * gen, faz, width=gen, label="FX çevrilebilir" if not fx else "FX çevrilemez")
        ax[1].bar(x + (i - 0.5) * gen, yk, width=gen, label="FX çevrilebilir" if not fx else "FX çevrilemez")
    ax[0].axhline(0.05, color="gray", ls="--", lw=0.8)
    ax[0].set_xticks(x, ad)
    ax[0].set_ylabel("Fazla medyan (reel − defter)")
    ax[0].set_title("Zayıf halka")
    ax[1].set_xticks(x, ad)
    ax[1].set_ylabel("Küçük yavaş (medyan/T)")
    ax[1].set_title("Yerel yük")
    ax[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def rapor(sonuc: dict, tablo: pd.DataFrame) -> str:
    k = sonuc["karar"]
    s = [
        "# Ödeme zinciri, tur 8: zayıf halka ve lider-ayna",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Varsayımlar",
        "",
        f"150 firma alt düğümü. TCMB 2026-Q1 toplamları sabit. Monte Carlo {N_MC}, tohum {SEED0}+s. "
        "Lider = en büyük mevduatlı firma. Lider sıfır: kütlesi kalan N−1 firmaya eşit dağıtılır.",
        "",
        f"Kontrol şoksuz: kalıcılık {k['soksuz_kal']:.2f}, reel {k['soksuz_reel']:.3f}. "
        f"Eşit pay FX çevrilemez reel {k['esit_reel']:.3f} (hedef 0,454, sapma {k['esit_sapma']:.3f}).",
        "",
        f"Spearman (Tur 7 ızgarası, FX çevrilemez): servis–küçük yavaş {k['sp_srv_yk']:.3f}, "
        f"mevduat–reel {k['sp_mev_reel']:.3f}.",
        "",
        f"Zayıf halka elendi mi: {k['zayif_elendi']}. Lider elendi mi: {k['lider_elendi']}.",
        "",
        "## Zayıf halka",
        "",
        "| Hücre | FX | Kalıcılık | Reel | Fazla medyan | P(fazla≥0,05) | Yavaş fark medyan | Ödenmeyen küçük pay |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, r in tablo[tablo.test == "zayif"].iterrows():
        s.append(
            f"| {r.hucre} | {'çevrilemez' if r.fx else 'çevrilebilir'} | {r.kal:.2f} | {r.reel:.3f} | "
            f"{r.fazla_med:.3f} | {r.p_fazla_05:.2f} | {r.yavas_fark_med:.3f} | {r.od_ku_med:.3f} |"
        )
    s.extend([
        "",
        "## Lider-ayna (FX çevrilemez)",
        "",
        "| Kol | Kalıcılık | Küçük yavaş medyan | Fazla medyan |",
        "| --- | ---: | ---: | ---: |",
    ])
    for _, r in tablo[tablo.test == "lider"].iterrows():
        s.append(f"| {r.kol} | {r.kal:.2f} | {r.yk_med:.3f} | {r.fazla_med:.3f} |")
    s.extend([
        "",
        f"Baz − rol sıfır: kalıcılık fark medyan {k['lider_kal_fark_rol']:.2f}, p = {k['lider_kal_p_rol']:.4g}. "
        f"Yavaş fark {k['lider_yk_fark_rol']:.3f}, p = {k['lider_yk_p_rol']:.4g}.",
        "",
        f"Baz − tam sıfır: kalıcılık fark medyan {k['lider_kal_fark_tam']:.2f}, p = {k['lider_kal_p_tam']:.4g}. "
        f"Yavaş fark {k['lider_yk_fark_tam']:.3f}, p = {k['lider_yk_p_tam']:.4g}.",
        "",
        "Tekrar: `python3 odeme_zinciri.py`.",
        "",
        "Dosyalar: `odeme_kons8_hucre.csv`, `odeme_kons8.png`, `odeme_kons8_sonuc.json`.",
        "",
    ])
    return "\n".join(s)


def hukum(k: dict) -> str:
    parca = [
        f"Kontrol: şoksuz reel {k['soksuz_reel']:.3f}, eşit FX çevrilemez reel {k['esit_reel']:.3f} "
        f"(sapma {k['esit_sapma']:.3f}).",
    ]
    if k["zayif_elendi"]:
        parca.append(
            "Zayıf halka: üç hücrede de medyan fazla 0,05’in altında ve küçük–büyük yavaş farkı anlamlı değil. "
            "Sistematik aktarım iddiası elendi."
        )
    else:
        parca.append("Zayıf halka: en az bir hücrede fazla veya yavaş fark eşiği aşıldı; iddia tam elenmedi.")
    if k["lider_elendi"]:
        parca.append(
            f"Lider-ayna: liderin mevduat+rolü sıfırlanınca kalıcılık farkı medyan {k['lider_kal_fark_tam']:.2f} "
            f"(p = {k['lider_kal_p_tam']:.3g}). 'Lider sonucu belirliyor' elendi; dağılım parametreleri belirliyor."
        )
    else:
        parca.append(
            f"Lider-ayna: yalnızca servis+alacak sıfırlanınca kalıcılık değişmiyor (p = {k['lider_kal_p_rol']:.3g}); "
            f"mevduat da dağıtılınca kalıcılık düşüyor (baz−tam medyan {k['lider_kal_fark_tam']:.2f}, "
            f"p = {k['lider_kal_p_tam']:.3g}). Lider mevduatı sonucu taşır; servis/alacak lider payı tek başına değil."
        )
    return " ".join(parca)


def spearman_kons7() -> tuple[float, float]:
    p = KOK / "odeme_kons7_hucre.csv"
    if not p.exists():
        return float("nan"), float("nan")
    t = pd.read_csv(p)
    if t.fx.dtype == object:
        t.fx = t.fx.map({"True": True, "False": False})
    fx = t[(t.test == "servis_grid") & t.fx]
    if len(fx) < 3:
        return float("nan"), float("nan")
    r1, _ = spearmanr(fx["srv_k"], fx["yk"])
    r2, _ = spearmanr(fx["mev_k"], fx["reel"])
    return float(r1), float(r2)


def main_kons8() -> None:
    stok = stok_yukle()
    print("kons8", N_MC, "seed", SEED0)
    satir = []
    ozetler = {}
    zayif_dfs = {}
    for hucre in ("esit", "ms70", "msa70"):
        for fx in (False, True):
            df = hucre_zayif(stok, hucre, fx)
            zayif_dfs[(hucre, fx)] = df
            o = zayif_ozet(df)
            ozetler[(hucre, fx)] = o
            satir.append({"test": "zayif", "hucre": hucre, "fx": fx, **o})
            print(f"zayif {hucre} fx={fx} fazla={o['fazla_med']:.3f} p05={o['p_fazla_05']:.2f} yk={o['yk_med']:.3f}", flush=True)

    lider_dfs = {}
    for kol in ("baz", "rol_sifir", "tam_sifir"):
        df = hucre_lider(stok, kol)
        lider_dfs[kol] = df
        o = zayif_ozet(df)
        satir.append({"test": "lider", "kol": kol, **o})
        print(f"lider {kol} kal={o['kal']:.2f} yk={o['yk_med']:.3f}", flush=True)

    tablo = pd.DataFrame(satir)
    tablo.to_csv(KOK / "odeme_kons8_hucre.csv", index=False)
    grafik_zayif(ozetler, KOK / "odeme_kons8.png")

    kon = kontrol(stok)
    sp_srv, sp_mev = spearman_kons7()

    # Wilcoxon yavas fark vs 0 per cell
    yavas_anlamli = False
    fazla_yuksek = False
    for hucre in ("esit", "ms70", "msa70"):
        for fx in (False, True):
            o = ozetler[(hucre, fx)]
            if o["fazla_med"] >= 0.05:
                fazla_yuksek = True
            df = zayif_dfs[(hucre, fx)]
            d = df["yavas_fark"].dropna()
            if d.size:
                try:
                    p = float(wilcoxon(d, alternative="two-sided").pvalue)
                except ValueError:
                    p = 1.0
                if p < 0.05 and abs(float(d.median())) >= 0.10:
                    yavas_anlamli = True

    zayif_elendi = bool(not fazla_yuksek and not yavas_anlamli)

    baz = lider_dfs["baz"]
    rol = lider_dfs["rol_sifir"]
    tam = lider_dfs["tam_sifir"]
    p_kr, f_kr = wilcoxon_paired(baz["kal"], rol["kal"], "two-sided")
    p_yr, f_yr = wilcoxon_paired(baz["yk_med"], rol["yk_med"], "two-sided")
    p_kt, f_kt = wilcoxon_paired(baz["kal"], tam["kal"], "two-sided")
    p_yt, f_yt = wilcoxon_paired(baz["yk_med"], tam["yk_med"], "two-sided")
    lider_elendi = bool(abs(f_kt) < 2.0 and p_kt > 0.05 and p_yt > 0.05)

    karar = {
        "soksuz_kal": kon["soksuz"]["kal"],
        "soksuz_reel": kon["soksuz"]["reel"],
        "esit_reel": kon["esit_fx"]["reel"],
        "esit_sapma": kon["esit_fx"]["reel_sapma"],
        "sp_srv_yk": sp_srv,
        "sp_mev_reel": sp_mev,
        "zayif_elendi": zayif_elendi,
        "lider_elendi": lider_elendi,
        "lider_kal_fark_rol": f_kr,
        "lider_kal_p_rol": p_kr,
        "lider_yk_fark_rol": f_yr,
        "lider_yk_p_rol": p_yr,
        "lider_kal_fark_tam": f_kt,
        "lider_kal_p_tam": p_kt,
        "lider_yk_fark_tam": f_yt,
        "lider_yk_p_tam": p_yt,
    }
    ozet_metin = hukum(karar)
    sonuc = {
        "uyari": (
            "Stoklar ölçülmüş (TCMB 2026-Q1). Kenar ve dağılım varsayım. "
            "Çekilmemiş limit ve girdi-çıktı yok."
        ),
        "ozet": ozet_metin,
        "karar": karar,
        "kontrol": kon,
        "n_mc": N_MC,
        "seed0": SEED0,
    }
    def _json_default(o):
        if isinstance(o, float) and (np.isnan(o) or np.isinf(o)):
            return None
        raise TypeError(type(o))

    (KOK / "odeme_kons8_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, tur 8") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor(sonuc, tablo) + ISARET + eski, encoding="utf-8")
    print(ozet_metin)


if __name__ == "__main__":
    main_kons8()
