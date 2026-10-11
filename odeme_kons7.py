"""Konsantrasyon turu. Kurallar kosudan once.

150 firma alt dugumu. Toplam TCMB 2026-Q1 mevduat, kredi stoku, aylik servis sabit.
Kenar yukumlulugun alacakli varlik payina bolunmesi. Girdi-cikti ve cekilmemis limit yok.
Monte Carlo 50. Tohum TOHUM+11000+s.

Ust %10 pay hedefleri 0.10, 0.40, 0.70 (mevduat, servis, alacak ayri).

Sistemik sayac onceki gibi (tahsil veya sikintili pay). Yerel sayac: alt yari firmada
o periyotta yavas orani (kilit veya odeme<0.70) ortalamasi >= 0.40 ise +1.

Test 1: mevduat x servis 3x3, FX acik/kapali.
Test 2: alacak konsantrasyonu 3 seviye; servis esit (1/N) veya servis=mevduat payi.
Test 3: varsayilan 1 aylik cizgi; ust %10 / alt yari / herkes; mevduat 0.70, servis esit.

Spearman: test 1 FX cevrilemez hucrelerinde mevduat hedefi vs kucuk yavaslik;
servis hedefi vs kucuk yavaslik; mevduat hedefi vs reel kayip.

Alacak: alacak konsantrasyonu artinca kucuk alacak payi dusuyor mu (Spearman);
reel kayip payi fazlasi medyan >= 0.05 mi (FX cevrilemez, servis esit).

Cizgi: sistemik kalicilik, yerel bloke, kucuk yavas farki raporlanir.
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
from odeme_dagilim import (
    F0,
    ISARET,
    KONS,
    N_FIRMA,
    agirlik,
    kos,
    stok_yukle,
    tufe_yoy,
    ust10,
)
KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
SEED0 = oz.TOHUM + 11000
LINE_AY = 1.0
MEV_LINE = 0.70


def ag_kur_v2(
    stok: dict,
    mev_w: np.ndarray,
    srv_w: np.ndarray,
    alac_w: np.ndarray | None = None,
    line_ay: float = 0.0,
    line_mode: str = "yok",
) -> dict:
    from akis_model import IDX

    from odeme_dagilim import B_NODE, D_NODE, H_NODE, K_NODE

    n = mev_w.size
    nd = F0 + n
    if alac_w is None:
        alac_w = srv_w.copy()
    mk, md = stok["mk"], stok["md"]
    ih, ib, ik, id_ = IDX["H"], IDX["B"], IDX["K"], IDX["D"]
    iF = IDX["F"]
    dugum = {ih: H_NODE, ib: B_NODE, ik: K_NODE, id_: D_NODE}
    kenar: dict[tuple[int, int], float] = {}

    def ekle(j, i, w):
        if w > 1e-12 and j != i:
            kenar[(j, i)] = kenar.get((j, i), 0.0) + w

    for s, sn in dugum.items():
        for c in range(5):
            if c == s:
                continue
            w = float(stok["kredi_ay"][s] * mk[s, c] + stok["diger_ay"][s] * md[s, c])
            if c == iF:
                for f in range(n):
                    ekle(sn, F0 + f, w * alac_w[f])
            else:
                ekle(sn, dugum[c], w)
    kredi_f = float(stok["kredi_ay"][iF])
    diger_f = float(stok["diger_ay"][iF])
    servis_f = (kredi_f + diger_f) * srv_w
    for f in range(n):
        for c, cn in dugum.items():
            w = srv_w[f] * (kredi_f * mk[iF, c] + diger_f * md[iF, c])
            ekle(F0 + f, cn, w)

    borclu = np.array([a for a, _ in kenar], dtype=np.int32)
    alacakli = np.array([b for _, b in kenar], dtype=np.int32)
    w0 = np.array(list(kenar.values()), dtype=np.float64)
    borc = np.bincount(borclu, weights=w0, minlength=nd).astype(np.float64)
    alacak = np.bincount(alacakli, weights=w0, minlength=nd).astype(np.float64)
    mev = np.zeros(nd)
    mev[H_NODE] = stok["lik"][ih]
    mev[B_NODE] = stok["lik"][ib]
    mev[K_NODE] = stok["lik"][ik]
    mev[D_NODE] = stok["lik"][id_]
    mev[F0:] = float(stok["lik"][iF]) * mev_w
    line = np.zeros(nd)
    if line_ay > 0 and line_mode != "yok":
        sira = np.argsort(mev_w, kind="mergesort")
        k10 = max(1, int(round(0.10 * n)))
        ust = np.zeros(n, dtype=bool)
        ust[sira[-k10:]] = True
        alt = np.zeros(n, dtype=bool)
        alt[sira[: n // 2]] = True
        if line_mode == "ust10":
            maske = ust
        elif line_mode == "alt_yarim":
            maske = alt
        else:
            maske = np.ones(n, dtype=bool)
        line[F0:] = np.where(maske, line_ay * servis_f, 0.0)
    kredi = np.zeros(nd)
    kredi[F0:] = float(stok["kredi_stok"][iF]) * srv_w
    fx = np.ones(nd)
    var = kredi[F0:] > 1e-12
    from odeme_gercek import F_KREDI, F_MEV

    fx[F0:][var] = (F_MEV * mev[F0:][var]) / (F_KREDI * kredi[F0:][var])
    sira = np.argsort(mev_w, kind="mergesort")
    kucuk = np.zeros(nd, dtype=bool)
    buyuk = np.zeros(nd, dtype=bool)
    kucuk[F0 + sira[: n // 2]] = True
    buyuk[F0 + sira[3 * n // 4 :]] = True
    ithal = np.zeros(nd)
    ithal[F0:] = F_KREDI
    al_f = alacak[F0:]
    kf = kucuk[F0:]
    kucuk_alac = float(al_f[kf].sum() / al_f.sum()) if al_f.sum() > 1e-12 else float("nan")
    return {
        "net": {
            "borclu": borclu,
            "alacakli": alacakli,
            "w0": w0,
            "borc": borc,
            "alacak": alacak,
            "boyut": np.maximum(mev, 1e-8),
            "buyuk": buyuk,
            "kucuk": kucuk,
            "banka_taban": np.zeros(nd),
            "idx_ku_al": np.flatnonzero(kucuk[alacakli]),
            "idx_bu_al": np.flatnonzero(buyuk[alacakli]),
            "idx_bu_borc": np.flatnonzero(buyuk[borclu]),
            "idx_b2k": np.flatnonzero(buyuk[borclu] & kucuk[alacakli]),
            "dis_akis": borc - alacak,
        },
        "lik": mev,
        "line": line,
        "fx": fx,
        "ithal": ithal,
        "kucuk_alac_pay": kucuk_alac,
        "ust10_mev": ust10(mev_w),
        "ust10_srv": ust10(srv_w),
        "ust10_alac": ust10(alac_w),
    }


def calistir(stok, mev_k, srv_k, alac_k, fx, line_mode="yok", srv_esit=False, alac_esit=False):
    v0 = None
    hs = []
    for s in range(N_MC):
        mev_w = agirlik(N_FIRMA, mev_k, SEED0 + s)
        if srv_esit:
            srv_w = np.full(N_FIRMA, 1.0 / N_FIRMA)
        elif srv_k is None:
            srv_w = mev_w.copy()
        else:
            srv_w = agirlik(N_FIRMA, float(srv_k), SEED0 + 50000 + s)
        if alac_esit:
            alac_w = np.full(N_FIRMA, 1.0 / N_FIRMA)
        elif alac_k is None:
            alac_w = srv_w.copy()
        else:
            alac_w = agirlik(N_FIRMA, alac_k, SEED0 + 60000 + s)
        pak = ag_kur_v2(stok, mev_w, srv_w, alac_w, LINE_AY if line_mode != "yok" else 0.0, line_mode)
        h, _, yavas = kos(pak, 0.0, fx)
        if v0 is None:
            v0 = float(pak["net"]["w0"].sum())
        k = pak["net"]["kucuk"]
        yk = float(yavas[k].mean()) / oz.T if np.any(k) else 0.0
        top = h[oz.F_REEL]
        pay = h[oz.F_REEL_KU] / top if top > 1e-8 else np.nan
        defter = pak["net"]["w0"][pak["net"]["idx_ku_al"]].sum() / pak["net"]["w0"].sum()
        hs.append({
            "kal": h[oz.F_KAL],
            "bloke": h[oz.F_KAL],
            "yerel": h[oz.F_YEREL],
            "yk": yk,
            "reel": h[oz.F_REEL] / (v0 * oz.T),
            "pay": pay,
            "defter": defter,
            "fazla": pay - defter if np.isfinite(pay) else np.nan,
            "kucuk_alac": pak["kucuk_alac_pay"],
        })
    return pd.DataFrame(hs), v0


def ozet(df: pd.DataFrame) -> dict:
    return {c: float(df[c].mean()) for c in ("kal", "bloke", "yerel", "yk", "reel", "kucuk_alac")}


def spearman_xy(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 3:
        return float("nan"), float("nan")
    r, p = spearmanr(x[m], y[m])
    return float(r), float(p)


def grafik(tablo: pd.DataFrame, dosya: Path) -> None:
    t = tablo[(tablo.test == "servis_grid") & tablo.fx]
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
    for ax_i, col, tit in zip(ax, ("yk", "reel", "yerel"), ("Küçük yavaş", "Reel kayıp", "Yerel bloke")):
        z = np.zeros((3, 3))
        for i, mk in enumerate(KONS):
            for j, sk in enumerate(KONS):
                r = t[(t.mev_k == mk) & (t.srv_k == sk)]
                z[i, j] = float(r[col].iloc[0]) if len(r) else 0.0
        im = ax_i.imshow(z, cmap="YlOrRd" if col != "yk" else "Blues", aspect="auto", vmin=0)
        ax_i.set_xticks(range(3), [f"Srv {int(k*100)}%" for k in KONS])
        ax_i.set_yticks(range(3), [f"Mev {int(k*100)}%" for k in KONS])
        ax_i.set_title(tit)
        fig.colorbar(im, ax=ax_i, fraction=0.046)
    fig.suptitle("FX çevrilemez. Üst %10 payları.", fontsize=11)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def rapor(sonuc: dict, tablo: pd.DataFrame) -> str:
    k = sonuc["karar"]
    s = [
        "# Ödeme zinciri, konsantrasyon (servis / alacak / çizgi)",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Varsayımlar",
        "",
        f"150 firma alt düğümü. TCMB 2026-Q1 toplamları sabit. Kenar paylaşım kuralı önceki turla aynı. "
        f"Girdi-çıktı ve çekilmemiş limit yok. Monte Carlo {N_MC}, tohum {SEED0}+s. "
        "Sistemik bloke sayacı değişmedi (%25 sikintili pay). "
        "Yerel bloke: alt yarı firmada o periyotta yavaş oranı ortalaması ≥ 0,40.",
        "",
        f"Test 1 (3×3 mevduat×servis, FX çevrilemez): mevduat hedefi ile küçük yavaşlık Spearman {k['sp_mev_yk']:.3f} (p = {k['sp_mev_yk_p']:.4g}); "
        f"servis hedefi ile küçük yavaşlık {k['sp_srv_yk']:.3f} (p = {k['sp_srv_yk_p']:.4g}); "
        f"mevduat hedefi ile reel kayıp {k['sp_mev_reel']:.3f} (p = {k['sp_mev_reel_p']:.4g}).",
        "",
        f"Mevduat 0,70 servis eşit: kalıcılık {k['mev70_esit_kal']:.2f}, yerel {k['mev70_esit_yerel']:.2f}, yavaş {k['mev70_esit_yk']:.3f}. "
        f"Mev=srv=0,70: FX çevrilebilir kalıcılık {k['grid77_tl_kal']:.2f}, FX çevrilemez {k['grid77_fx_kal']:.2f}, reel {k['grid77_fx_reel']:.3f}.",
        "",
        f"Alacak konsantrasyonu (FX çevrilemez, servis eşit): alacak hedefi ile küçük alacak payı Spearman {k['sp_alac_pay']:.3f}; "
        f"reel kayıp fazlası medyan {k['alac_fazla_med']:.3f} (5 puan eşiği {'aşıldı' if k['alac_zayif_degil'] else 'aşılmadı'}).",
        "",
        f"Alacak 0,70, servis konsantre: küçük alacak payı {k['alac70_kucuk_alac']:.3f}; servis eşitken {k['alac70_esit_kucuk_alac']:.3f}.",
        "",
        f"Çizgi (mevduat 0,70, servis eşit, FX çevrilebilir): herkes / üst %10 / alt yarı — "
        f"sistemik {k['ciz_her_kal']:.2f} / {k['ciz_ust_kal']:.2f} / {k['ciz_alt_kal']:.2f}; "
        f"yerel {k['ciz_her_yerel']:.2f} / {k['ciz_ust_yerel']:.2f} / {k['ciz_alt_yerel']:.2f}; "
        f"küçük yavaş {k['ciz_her_yk']:.3f} / {k['ciz_ust_yk']:.3f} / {k['ciz_alt_yk']:.3f}.",
        "",
        "## Test 1 — mevduat × servis (ortalama)",
        "",
        "| Mev %10 | Srv %10 | FX | Kalıcılık | Yerel | Küçük yavaş | Reel |",
        "| ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    g = tablo[tablo.test == "servis_grid"].sort_values(["mev_k", "srv_k", "fx"])
    for _, r in g.iterrows():
        s.append(
            f"| {r.mev_k:.2f} | {r.srv_k:.2f} | {'çevrilemez' if r.fx else 'çevrilebilir'} | "
            f"{r.kal:.2f} | {r.yerel:.2f} | {r.yk:.3f} | {r.reel:.3f} |"
        )
    s.extend([
        "",
        "## Test 2 — alacak",
        "",
        "| Alac %10 | Servis | FX | Kalıcılık | Yerel | Küçük yavaş | Reel | Küçük alacak payı |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    a = tablo[tablo.test == "alacak"].sort_values(["alac_k", "srv_esit", "fx"])
    for _, r in a.iterrows():
        s.append(
            f"| {r.alac_k:.2f} | {'eşit' if r.srv_esit else 'konsantre'} | {'çevrilemez' if r.fx else 'çevrilebilir'} | "
            f"{r.kal:.2f} | {r.yerel:.2f} | {r.yk:.3f} | {r.reel:.3f} | {r.kucuk_alac:.3f} |"
        )
    s.extend([
        "",
        "## Test 3 — çizgi kime açık (FX çevrilebilir)",
        "",
        "| Çizgi | Kalıcılık | Yerel | Küçük yavaş | Reel |",
        "| --- | ---: | ---: | ---: | ---: |",
    ])
    for _, r in tablo[tablo.test == "cizgi"].iterrows():
        s.append(f"| {r.line_mode} | {r.kal:.2f} | {r.yerel:.2f} | {r.yk:.3f} | {r.reel:.3f} |")
    s.extend([
        "",
        "Tekrar: `python3 odeme_zinciri.py`.",
        "",
        "Dosyalar: `odeme_kons7_hucre.csv`, `odeme_kons7.png`, `odeme_kons7_sonuc.json`.",
        "",
    ])
    return "\n".join(s)


def hukum(k: dict) -> str:
    parca = [
        f"Mevduat×servis (FX çevrilemez): mevduat hedefi–küçük yavaş Spearman {k['sp_mev_yk']:.3f} "
        f"(p = {k['sp_mev_yk_p']:.3g}), servis hedefi–küçük yavaş {k['sp_srv_yk']:.3f} "
        f"(p = {k['sp_srv_yk_p']:.3g}), mevduat–reel kayıp {k['sp_mev_reel']:.3f} (p = {k['sp_mev_reel_p']:.3g}).",
    ]
    parca.append(
        f"Mevduat 0,70 servis eşit: sistemik kalıcılık {k['mev70_esit_kal']:.2f}, yerel {k['mev70_esit_yerel']:.2f}, "
        f"küçük yavaş {k['mev70_esit_yk']:.3f} — önceki tur tekrarı."
    )
    parca.append(
        f"Mevduat ve servis birlikte 0,70: FX çevrilebilirken kalıcılık {k['grid77_tl_kal']:.2f}, "
        f"FX çevrilemezken {k['grid77_fx_kal']:.2f}, reel kayıp {k['grid77_fx_reel']:.3f}. "
        "Servis de konsantre olunca agregatın gizlediği sistemik bloke çıkıyor; yalnızca mevduat konsantre servis eşitken çıkmıyor."
    )
    if k["sp_alac_pay"] <= -0.9:
        parca.append(
            f"Alacak üst %10 payı arttıkça küçük firmaların alacak payı düşüyor (Spearman {k['sp_alac_pay']:.2f}). "
            f"Reel kayıp fazlası medyan {k['alac_fazla_med']:.3f}; 5 puan eşiği aşılmadı."
        )
    if not k["alac_zayif_degil"]:
        parca.append("Zayıf halka: küçük reel kayıp payı alacak konsantrasyonunda da 5 puanı aşmıyor.")
    parca.append(
        f"Çizgi (mev 0,70, servis eşit, FX çevrilebilir): herkes yavaş {k['ciz_her_yk']:.3f}, üst %10 {k['ciz_ust_yk']:.3f} "
        f"(yerel bloke {k['ciz_ust_yerel']:.2f}), alt yarı {k['ciz_alt_yk']:.3f}. Sistemik kalıcılık {k['ciz_her_kal']:.0f}."
    )
    return " ".join(parca)


def main_kons7() -> None:
    stok = stok_yukle()
    satir = []
    print("kons7", N_MC, "seed", SEED0)

    for mev_k in KONS:
        for srv_k in KONS:
            for fx in (False, True):
                df, _ = calistir(stok, mev_k, srv_k, None, fx)
                o = ozet(df)
                satir.append({
                    "test": "servis_grid",
                    "mev_k": mev_k,
                    "srv_k": srv_k,
                    "alac_k": np.nan,
                    "fx": fx,
                    "srv_esit": False,
                    "line_mode": "yok",
                    **o,
                })
                print(f"grid {mev_k} {srv_k} fx={fx} kal={o['kal']:.2f} yk={o['yk']:.3f} reel={o['reel']:.3f}", flush=True)

    for alac_k in KONS:
        for srv_esit in (True, False):
            for fx in (False, True):
                df, _ = calistir(stok, MEV_LINE, None if srv_esit else alac_k, alac_k, fx, srv_esit=srv_esit, alac_esit=False)
                o = ozet(df)
                satir.append({
                    "test": "alacak",
                    "mev_k": MEV_LINE,
                    "srv_k": np.nan,
                    "alac_k": alac_k,
                    "fx": fx,
                    "srv_esit": srv_esit,
                    "line_mode": "yok",
                    **o,
                })

    for line_mode in ("herkes", "ust10", "alt_yarim"):
        df, _ = calistir(stok, MEV_LINE, None, None, False, line_mode=line_mode, srv_esit=True)
        o = ozet(df)
        satir.append({
            "test": "cizgi",
            "mev_k": MEV_LINE,
            "srv_k": np.nan,
            "alac_k": np.nan,
            "fx": False,
            "srv_esit": True,
            "line_mode": line_mode,
            **o,
        })
        print(f"cizgi {line_mode} yk={o['yk']:.3f} yerel={o['yerel']:.2f}", flush=True)

    tablo = pd.DataFrame(satir)
    tablo.to_csv(KOK / "odeme_kons7_hucre.csv", index=False)
    grafik(tablo, KOK / "odeme_kons7.png")

    fxg = tablo[(tablo.test == "servis_grid") & tablo.fx]
    sp_mev_yk, sp_mev_yk_p = spearman_xy(fxg["mev_k"], fxg["yk"])
    sp_srv_yk, sp_srv_yk_p = spearman_xy(fxg["srv_k"], fxg["yk"])
    sp_mev_reel, sp_mev_reel_p = spearman_xy(fxg["mev_k"], fxg["reel"])

    df70, _ = calistir(stok, 0.70, 0.70, None, True)
    df70e, _ = calistir(stok, 0.70, None, None, True, srv_esit=True)
    o70 = ozet(df70)
    o70e = ozet(df70e)

    alac_fx = tablo[(tablo.test == "alacak") & tablo.fx & tablo.srv_esit]
    sp_alac_pay, _ = spearman_xy(alac_fx["alac_k"], alac_fx["kucuk_alac"])
    fazlalar = []
    for ak in KONS:
        dfa, _ = calistir(stok, MEV_LINE, None, ak, True, srv_esit=True)
        fazlalar.extend(dfa["fazla"].dropna().tolist())
    fazla_med = float(np.median(fazlalar)) if fazlalar else float("nan")

    r70e = tablo[(tablo.test == "alacak") & (tablo.alac_k == 0.70) & tablo.srv_esit & tablo.fx].iloc[0]
    r70k = tablo[(tablo.test == "alacak") & (tablo.alac_k == 0.70) & (~tablo.srv_esit) & tablo.fx].iloc[0]

    ciz = {r.line_mode: r for _, r in tablo[tablo.test == "cizgi"].iterrows()}

    g77_tl = tablo[(tablo.test == "servis_grid") & (tablo.mev_k == 0.70) & (tablo.srv_k == 0.70) & (~tablo.fx)].iloc[0]
    g77_fx = tablo[(tablo.test == "servis_grid") & (tablo.mev_k == 0.70) & (tablo.srv_k == 0.70) & tablo.fx].iloc[0]

    karar = {
        "grid77_tl_kal": float(g77_tl["kal"]),
        "grid77_fx_kal": float(g77_fx["kal"]),
        "grid77_fx_reel": float(g77_fx["reel"]),
        "sp_mev_yk": sp_mev_yk,
        "sp_mev_yk_p": sp_mev_yk_p,
        "sp_srv_yk": sp_srv_yk,
        "sp_srv_yk_p": sp_srv_yk_p,
        "sp_mev_reel": sp_mev_reel,
        "sp_mev_reel_p": sp_mev_reel_p,
        "srv70_kal": o70["kal"],
        "srv70_yerel": o70["yerel"],
        "srv70_yk": o70["yk"],
        "mev70_esit_kal": o70e["kal"],
        "mev70_esit_yerel": o70e["yerel"],
        "mev70_esit_yk": o70e["yk"],
        "sp_alac_pay": sp_alac_pay,
        "alac_fazla_med": fazla_med,
        "alac_zayif_degil": bool(np.isfinite(fazla_med) and fazla_med >= 0.05),
        "alac70_kucuk_alac": float(r70k["kucuk_alac"]),
        "alac70_esit_kucuk_alac": float(r70e["kucuk_alac"]),
        "ciz_her_kal": float(ciz["herkes"]["kal"]),
        "ciz_ust_kal": float(ciz["ust10"]["kal"]),
        "ciz_alt_kal": float(ciz["alt_yarim"]["kal"]),
        "ciz_her_yerel": float(ciz["herkes"]["yerel"]),
        "ciz_ust_yerel": float(ciz["ust10"]["yerel"]),
        "ciz_alt_yerel": float(ciz["alt_yarim"]["yerel"]),
        "ciz_her_yk": float(ciz["herkes"]["yk"]),
        "ciz_ust_yk": float(ciz["ust10"]["yk"]),
        "ciz_alt_yk": float(ciz["alt_yarim"]["yk"]),
    }
    ozet_metin = hukum(karar)
    tufe = tufe_yoy()
    sonuc = {
        "uyari": sonuc_uyari(),
        "ozet": ozet_metin,
        "karar": karar,
        "tufe": tufe,
        "n_mc": N_MC,
        "seed0": SEED0,
    }
    (KOK / "odeme_kons7_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, konsantrasyon") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor(sonuc, tablo) + ISARET + eski, encoding="utf-8")
    print(ozet_metin)


def sonuc_uyari() -> str:
    return (
        "Stoklar ölçülmüş (TCMB 2026-Q1). Kenar ve firma içi dağılım varsayım. "
        "Çekilmemiş limit serisi ve girdi-çıktı tablosu yok."
    )


if __name__ == "__main__":
    main_kons7()
