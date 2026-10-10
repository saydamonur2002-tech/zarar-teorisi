"""Faiz gecikme hipotezi. Kurallar kosudan once.

150 firma, TCMB 2026-Q1. MC 50, tohum TOHUM+13000+s.
Mev/serv > 3 ise odeme orani x (1-alpha). alpha 0 / 0.15 / 0.30.
Hucre: mev ust10 0.10/0.40/0.70 x servis esit veya servis 0.70. FX ayri.

Lider: en yuksek mevduatli dugum alpha=0.50, digerleri 0 (zorla).

Curutme: alpha>0 vs 0 kal/yavas medyan fark < 2 ve p>0.05 -> faiz iddiasi elenir.
Sadece servis konsantre iken artis -> mev tek basina yetmiyor.
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
from odeme_dagilim import F0, ISARET, N_FIRMA, agirlik, stok_yukle, ust10
from odeme_gercek import ESIK_VALF, tufe_yoy
from odeme_kons7 import ag_kur_v2
from odeme_kons8 import wilcoxon_paired

KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
SEED0 = oz.TOHUM + 13000
ALPHAS = (0.0, 0.15, 0.30)
FAIZ_ESIK = 3.0
HUCRELER = (
    ("mev10_eq", 0.10, True),
    ("mev40_eq", 0.40, True),
    ("mev70_eq", 0.70, True),
    ("mev10_s70", 0.10, False),
    ("mev40_s70", 0.40, False),
    ("mev70_s70", 0.70, False),
)


def pi_aylik() -> float:
    t = tufe_yoy()
    return float((1.0 + t["yoy"]) ** (1.0 / 12.0) - 1.0)


def agirlikler(s: int, mev_k: float, srv_esit: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    eq = np.full(N_FIRMA, 1.0 / N_FIRMA)
    if mev_k <= 0.101:
        mev_w = eq.copy()
    else:
        mev_w = agirlik(N_FIRMA, mev_k, SEED0 + s)
    if srv_esit:
        srv_w = eq.copy()
    else:
        srv_w = agirlik(N_FIRMA, 0.70, SEED0 + 50000 + s)
    return mev_w, srv_w, eq.copy()


def servis_dizi(stok, srv_w: np.ndarray) -> np.ndarray:
    from akis_model import IDX

    iF = IDX["F"]
    nd = F0 + srv_w.size
    serv = np.zeros(nd)
    kredi_f = float(stok["kredi_ay"][iF])
    diger_f = float(stok["diger_ay"][iF])
    serv[F0:] = (kredi_f + diger_f) * srv_w
    return serv


def paket(stok, mev_w, srv_w, alac_w) -> dict:
    pak = ag_kur_v2(stok, mev_w, srv_w, alac_w)
    pak["servis"] = servis_dizi(stok, srv_w)
    return pak


def kos_faiz(
    pak: dict,
    pi: float,
    fx: bool,
    faiz_alpha: float,
    *,
    lider: bool = False,
    lider_alpha: float = 0.50,
):
    nd = int(pak["lik"].size)
    dis = np.ones(nd, dtype=bool)
    if fx:
        dis[F0:] = False
    faiz_a = np.zeros(nd)
    lider_z = None
    if lider:
        L = F0 + int(np.argmax(pak["lik"][F0:]))
        faiz_a[L] = lider_alpha
        lider_z = np.zeros(nd, dtype=bool)
        lider_z[L] = True
    elif faiz_alpha > 0:
        faiz_a[F0:] = faiz_alpha
    return oz.tek_kosu_temiz(
        pak["net"],
        pak["lik"],
        pak["line"],
        oz.KILIT[oz.ORTA][0],
        oz.KILIT[oz.ORTA][1],
        oz.GECIKME[4],
        dis,
        enflasyon_esik=ESIK_VALF,
        enflasyon_pi=pi,
        reel=True,
        ithal=pak["ithal"],
        fx_ay=1.0,
        fx_sok=fx,
        fx_carpan=pak["fx"] if fx else None,
        fx_hizmet=0.0,
        faiz_gecikme=faiz_a,
        faiz_mev=pak["lik"],
        faiz_serv=pak["servis"],
        faiz_esik=FAIZ_ESIK,
        faiz_lider_zorla=lider_z,
    )


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
    }


def grid_kos(stok, pi: float) -> pd.DataFrame:
    rows = []
    for hucre, mev_k, srv_eq in HUCRELER:
        for fx in (False, True):
            for alpha in ALPHAS:
                for s in range(N_MC):
                    mev_w, srv_w, alac_w = agirlikler(s, mev_k, srv_eq)
                    pak = paket(stok, mev_w, srv_w, alac_w)
                    h, _, yavas = kos_faiz(pak, pi, fx, alpha)
                    v0 = float(pak["net"]["w0"].sum())
                    rows.append(
                        {
                            "hucre": hucre,
                            "mev_k": mev_k,
                            "srv_esit": srv_eq,
                            "fx": fx,
                            "alpha": alpha,
                            "s": s,
                            "ust10_mev": ust10(mev_w),
                            "ust10_srv": ust10(srv_w),
                            **metrikler(h, yavas, pak, v0),
                        }
                    )
    return pd.DataFrame(rows)


def lider_kos(stok, pi: float) -> pd.DataFrame:
    rows = []
    mev_k = 0.70
    for fx in (False, True):
        for lider in (False, True):
            for s in range(N_MC):
                mev_w, srv_w, alac_w = agirlikler(s, mev_k, True)
                pak = paket(stok, mev_w, srv_w, alac_w)
                h, _, yavas = kos_faiz(pak, pi, fx, 0.0, lider=lider, lider_alpha=0.50)
                v0 = float(pak["net"]["w0"].sum())
                rows.append(
                    {
                        "fx": fx,
                        "lider_gec": lider,
                        "s": s,
                        **metrikler(h, yavas, pak, v0),
                    }
                )
    return pd.DataFrame(rows)


def ozet_grup(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby(["hucre", "fx", "alpha"], as_index=False)
        .agg(
            kal=("kal", "mean"),
            yerel=("yerel", "mean"),
            reel=("reel", "mean"),
            yk=("yk", "mean"),
            fazla=("fazla", "median"),
        )
    )
    return g


def rapor(sonuc: dict, ozet: pd.DataFrame, lider: pd.DataFrame) -> str:
    k = sonuc["karar"]
    pi = sonuc["pi_aylik"]
    s = [
        "# Ödeme zinciri, faiz gecikme hipotezi (tur 13)",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Varsayımlar",
        "",
        f"150 firma. Mevduat/aylık servis > {FAIZ_ESIK} iken ödeme oranı ×(1−α). "
        f"α ∈ {{0, 0,15, 0,30}}. MC {N_MC}, tohum {SEED0}+s. π = {pi:.4f}. FX çevrilebilir/çevrilemez ayrı.",
        "",
        f"Kontrol şoksuz: kal {k['soksuz_kal']:.2f}, reel {k['soksuz_reel']:.3f}.",
        f"Faiz gecikme elendi: {k['faiz_elendi']}. Servis yükü bağımlılığı: {k['servis_notu']}.",
        "",
        f"Spearman (α>0, FX çevrilemez): mevduat–kalıcılık {k['sp_mev_kal']:.3f}, servis–kalıcılık {k['sp_srv_kal']:.3f}.",
        "",
        "## Hücre × α (ortalama; reel FX çevrilemez)",
        "",
        "| Hücre | α=0 kal | α=0,15 kal | α=0,30 kal | α=0 yavaş | α=0,30 yavaş | α=0 reel | α=0,30 reel | Yerel α=0 / 0,30 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for hucre, _mk, _se in HUCRELER:
        sub = ozet[(ozet.hucre == hucre) & (ozet.fx == True)]
        if sub.empty:
            continue
        r = {}
        for a in ALPHAS:
            sa = sub[sub.alpha == a]
            if not sa.empty:
                r[float(a)] = sa.iloc[0]
        if 0.0 not in r or 0.30 not in r:
            continue
        s.append(
            f"| {hucre} | {r[0.0]['kal']:.2f} | {r[0.15]['kal']:.2f} | {r[0.30]['kal']:.2f} | "
            f"{r[0.0]['yk']:.3f} | {r[0.30]['yk']:.3f} | {r[0.0]['reel']:.3f} | {r[0.30]['reel']:.3f} | "
            f"{r[0.0]['yerel']:.2f} / {r[0.30]['yerel']:.2f} |"
        )
    s.extend(["", "## Lider gecikme (mev 0,70, servis eşit, FX çevrilemez)", ""])
    ld = lider[(lider.fx == True)]
    for lider_on in (False, True):
        sub = ld[ld.lider_gec == lider_on]
        s.append(
            f"- Lider gecikme {'açık' if lider_on else 'kapalı'}: kal {sub['kal'].mean():.2f}, "
            f"yavaş {sub['yk'].mean():.3f}, yerel {sub['yerel'].mean():.2f}."
        )
    p = k.get("lider_p")
    s.append(f"- Eşli fark (kapalı − açık) kal medyan {k.get('lider_dkal', float('nan')):.2f}, p = {p:.4g}." if p else "")
    s.extend(["", "Tekrar: `python3 odeme_zinciri.py`.", "", "Dosyalar: `odeme_faiz13_hucre.csv`, `odeme_faiz13_sonuc.json`.", ""])
    return "\n".join(s)


def main_faiz13() -> None:
    stok = stok_yukle()
    pi = pi_aylik()
    print("faiz13", N_MC, "seed", SEED0, flush=True)
    df = grid_kos(stok, pi)
    df.to_csv(KOK / "odeme_faiz13_hucre.csv", index=False)
    oz = ozet_grup(df)
    ldf = lider_kos(stok, pi)
    ldf.to_csv(KOK / "odeme_faiz13_lider.csv", index=False)

    u = np.full(N_FIRMA, 1.0 / N_FIRMA)
    pk = paket(stok, u, u.copy(), u.copy())
    h0, _, y0 = kos_faiz(pk, 0.0, False, 0.0)
    v0 = float(pk["net"]["w0"].sum())
    soksuz = metrikler(h0, y0, pk, v0)

    faiz_elendi = True
    for hucre, _, _ in HUCRELER:
        for fx in (False, True):
            d0 = df[(df.hucre == hucre) & (df.fx == fx) & (df.alpha == 0.0)].sort_values("s")
            d1 = df[(df.hucre == hucre) & (df.fx == fx) & (df.alpha == 0.30)].sort_values("s")
            if len(d0) != len(d1):
                continue
            pk, dk = wilcoxon_paired(d1["kal"].values, d0["kal"].values, "greater")
            py, dy = wilcoxon_paired(d1["yk"].values, d0["yk"].values, "greater")
            if dk >= 2.0 and pk < 0.05:
                faiz_elendi = False
            if dy >= 0.10 and py < 0.05:
                faiz_elendi = False

    pos = df[(df.alpha > 0) & (df.fx == True)]
    sp_mev, _ = spearmanr(pos["ust10_mev"], pos["kal"]) if len(pos) > 2 else (float("nan"), float("nan"))
    sp_srv, _ = spearmanr(pos["ust10_srv"], pos["kal"]) if len(pos) > 2 else (float("nan"), float("nan"))

    mev70_eq = df[(df.hucre == "mev70_eq") & (df.fx == True) & (df.alpha > 0)]["kal"].mean()
    mev70_s70 = df[(df.hucre == "mev70_s70") & (df.fx == True) & (df.alpha > 0)]["kal"].mean()
    mev40_eq = df[(df.hucre == "mev40_eq") & (df.fx == True) & (df.alpha > 0)]["kal"].mean()
    if mev70_s70 > mev70_eq + 0.5 and mev40_eq < mev70_eq:
        servis_notu = "Etki servis konsantrasyonu ile güçleniyor; mevduat tek başına zayıf."
    elif faiz_elendi:
        servis_notu = "Anlamlı artış yok; servis/mev ayrımı belirsiz."
    else:
        servis_notu = "Mevduat konsantrasyonu da katkı veriyor olabilir."

    ld = ldf[ldf.fx == True]
    off = ld[~ld.lider_gec]
    on = ld[ld.lider_gec]
    p_ld, d_ld = wilcoxon_paired(off["kal"], on["kal"], "two-sided")

    ozet_metin = (
        f"Kontrol şoksuz kal {soksuz['kal']:.2f}, reel {soksuz['reel']:.3f}. "
        f"Faiz gecikme hipotezi {'elendi' if faiz_elendi else 'desteklendi'} (α>0 vs 0, kayıtlı eşikler). "
        f"{servis_notu} "
        f"Lider α=0,50 (mev70): kal fark medyan {d_ld:.2f}, p = {p_ld:.4g}."
    )

    karar = {
        "soksuz_kal": soksuz["kal"],
        "soksuz_reel": soksuz["reel"],
        "faiz_elendi": faiz_elendi,
        "servis_notu": servis_notu,
        "sp_mev_kal": float(sp_mev),
        "sp_srv_kal": float(sp_srv),
        "lider_dkal": d_ld,
        "lider_p": p_ld,
    }
    sonuc = {
        "uyari": "Kenar varsayım. Faiz geliri açık modellenmedi; mev/serv oranı ve α ile gecikme.",
        "ozet": ozet_metin,
        "karar": karar,
        "pi_aylik": pi,
        "n_mc": N_MC,
        "seed0": SEED0,
    }

    def _jd(o):
        if isinstance(o, float) and (np.isnan(o) or np.isinf(o)):
            return None
        raise TypeError(type(o))

    (KOK / "odeme_faiz13_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2, default=_jd) + "\n",
        encoding="utf-8",
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, faiz") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor(sonuc, oz, ldf) + ISARET + eski, encoding="utf-8")
    print(ozet_metin)


if __name__ == "__main__":
    main_faiz13()
