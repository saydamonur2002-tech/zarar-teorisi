"""Tur 12: Gini (mevduat) ve kalicilik. Kurallar kosudan once.

Tur 11 ile ayni hucre/kol. MC 50, tohum TOHUM+16000+s.
Gini: 150 firma mevduat payi. DeltaGini = Gini_kol - Gini_baz (baz = ham agirlik, yok kol).

Destek: |DeltaGini| < 0.05 iken mahsup - lider kal medyan >= 2, p<0.05 -> kucuk Gini degisimi bloke kirar.
Lider vs ust10: |Gini fark| >= 0.20 ve kal anlamsiz -> Gini degil tek dugum payi.
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
from odeme_dagilim import ISARET, N_FIRMA, agirlik, kos, stok_yukle
from odeme_gercek import ESIK_VALF, tufe_yoy
from odeme_kons7 import ag_kur_v2
from odeme_kons8 import lider_dagit, metrikler, wilcoxon_paired
from odeme_mahsup import mahsup_paket, paket_to_ag, statik_teshis

KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
SEED0 = oz.TOHUM + 16000
HUCRELER = ("esit", "mev40", "mev70")
MEV_HEDEF = {"esit": 0.10, "mev40": 0.40, "mev70": 0.70}
KOLLAR = ("yok", "mahsup", "mahsup_lider", "mahsup_ust10")
MAHSUP_KOLLAR = ("mahsup", "mahsup_lider", "mahsup_ust10")


def gini_mev(w: np.ndarray) -> float:
    x = np.asarray(w, dtype=float).ravel()
    x = x[x >= 0]
    if x.size == 0:
        return 0.0
    s = x.sum()
    if s <= 0:
        return 0.0
    x = np.sort(x / s)
    n = x.size
    cum = np.cumsum(x)
    g = 1.0 - 2.0 / n * np.sum(cum) + 1.0 / n
    return float(max(0.0, g))


def ust10_dagit(w: np.ndarray) -> np.ndarray:
    w = np.asarray(w, dtype=float).copy()
    n = w.size
    k = max(1, int(round(0.10 * n)))
    sira = np.argsort(w, kind="mergesort")
    ust = sira[-k:]
    mass = float(w[ust].sum())
    w[ust] = 0.0
    alt = np.ones(n, dtype=bool)
    alt[ust] = False
    w[alt] += mass / int(alt.sum())
    s = w.sum()
    return w / s if s > 0 else np.full(n, 1.0 / n)


def mev_kol(mev_w: np.ndarray, kol: str) -> np.ndarray:
    mw = mev_w.copy()
    if kol == "mahsup_lider":
        return lider_dagit(mw, int(np.argmax(mev_w)))
    if kol == "mahsup_ust10":
        return ust10_dagit(mw)
    return mw


def agirlikler(s: int, hucre: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    eq = np.full(N_FIRMA, 1.0 / N_FIRMA)
    if hucre == "esit":
        return eq.copy(), eq.copy(), eq.copy()
    mev_w = agirlik(N_FIRMA, MEV_HEDEF[hucre], SEED0 + s)
    return mev_w, eq.copy(), eq.copy()


def pi_aylik() -> float:
    t = tufe_yoy()
    return float((1.0 + t["yoy"]) ** (1.0 / 12.0) - 1.0)


def pak_hazir(stok, mev_w, srv_w, alac_w, kol: str) -> tuple[dict, dict, dict]:
    mw = mev_kol(mev_w, kol)
    pak0 = ag_kur_v2(stok, mw, srv_w, alac_w)
    ag0 = paket_to_ag(pak0)
    brut_once = ag0.brut_borc()
    if kol == "yok":
        return pak0, {"brut_once": brut_once, "brut_sonra": brut_once, "silinen_oran": 0.0}, statik_teshis(ag0)
    pak_m, oz, _, ag1 = mahsup_paket(pak0, "optimal")
    return pak_m, {
        "brut_once": oz["brut_once"],
        "brut_sonra": oz["brut_sonra"],
        "silinen_oran": oz["silinen_oran"],
    }, statik_teshis(ag1)


def hucre_kos(stok, hucre: str, kol: str, pi: float) -> pd.DataFrame:
    rows = []
    for s in range(N_MC):
        mev_w, srv_w, alac_w = agirlikler(s, hucre)
        gini_baz = gini_mev(mev_w)
        mw_kol = mev_kol(mev_w, kol)
        gini = gini_mev(mw_kol)
        pak_ref = ag_kur_v2(stok, mev_w, srv_w, alac_w)
        pak_run, brut, stat = pak_hazir(stok, mev_w, srv_w, alac_w, kol)
        h, _, yavas = kos(pak_run, pi, True)
        v0 = float(pak_ref["net"]["w0"].sum())
        rows.append(
            {
                "hucre": hucre,
                "kol": kol,
                "mev_hedef": MEV_HEDEF[hucre],
                "s": s,
                "gini": gini,
                "gini_baz": gini_baz,
                "delta_gini": gini - gini_baz,
                **brut,
                **stat,
                **metrikler(h, yavas, pak_run, v0),
            }
        )
    return pd.DataFrame(rows)


def kontrol(stok) -> dict:
    u = np.full(N_FIRMA, 1.0 / N_FIRMA)
    pak = ag_kur_v2(stok, u, u.copy(), u.copy())
    h0, _, y0 = kos(pak, 0.0, False)
    v0 = float(pak["net"]["w0"].sum())
    return {"soksuz": metrikler(h0, y0, pak, v0), "gini_esit": gini_mev(u)}


def ozet_df(df: pd.DataFrame) -> dict:
    faz = df["fazla"].dropna()
    return {
        "gini": float(df["gini"].mean()),
        "delta_gini": float(df["delta_gini"].mean()),
        "brut_once": float(df["brut_once"].mean()),
        "brut_sonra": float(df["brut_sonra"].mean()),
        "kal": float(df["kal"].mean()),
        "reel": float(df["reel"].mean()),
        "yk_med": float(df["yk_med"].mean()),
        "fazla_med": float(faz.median()) if faz.size else float("nan"),
        "p_fazla_05": float((faz >= 0.05).mean()) if faz.size else float("nan"),
    }


def grafik(tablo: pd.DataFrame, dosya: Path) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ad = ["Eşit", "Mev 0,40", "Mev 0,70"]
    x = np.arange(3)
    w = 0.2
    for i, kol in enumerate(KOLLAR):
        sub = tablo[tablo.kol == kol].set_index("hucre")
        g = [sub.loc[h, "gini"] if h in sub.index else 0 for h in HUCRELER]
        k = [sub.loc[h, "kal"] if h in sub.index else 0 for h in HUCRELER]
        off = (i - 1.5) * w
        ax[0].bar(x + off, g, width=w, label=kol)
        ax[1].bar(x + off, k, width=w, label=kol)
    ax[0].set_xticks(x, ad)
    ax[0].set_ylabel("Gini (ort.)")
    ax[0].set_title("Tur 12")
    ax[1].set_xticks(x, ad)
    ax[1].set_ylabel("Kalıcılık")
    ax[0].legend(frameon=False, fontsize=6, ncol=2)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def rapor(sonuc: dict, tablo: pd.DataFrame) -> str:
    k = sonuc["karar"]
    pi = sonuc["pi_aylik"]
    s = [
        "# Ödeme zinciri, tur 12: Gini ve kalıcılık",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Varsayımlar",
        "",
        f"150 firma mevduat Gini. Baz Gini = ham çekim (yok kol). ΔGini = Gini_kol − Gini_baz. "
        f"MC {N_MC}, tohum {SEED0}+s. FX çevrilemez, π = {pi:.4f}.",
        "",
        f"Kontrol şoksuz: kalıcılık {k['soksuz_kal']:.2f}, reel {k['soksuz_reel']:.3f}, Gini(eşit) {k['gini_kontrol']:.3f}.",
        "",
        f"Spearman Gini–kalıcılık (mahsup kolları): {k['sp_gini_kal']:.3f} (p = {k['sp_gini_kal_p']:.4g}).",
        f"Küçük ΔGini bloke kırar: {k['gini_kirar_destek']}. Gini değil tek düğüm payı: {k['gini_degil_lider']}. "
        f"FX/zayıf halka elenmedi: {k['fx_zayif_elenmedi']}.",
        "",
        "| Hücre | Kol | Gini | ΔGini | Brüt→sonra | Kal | Reel | Küçük yavaş | Fazla med |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, r in tablo.iterrows():
        faz = f"{r.fazla_med:.3f}" if np.isfinite(r.fazla_med) else "—"
        s.append(
            f"| {r.hucre} | {r.kol} | {r.gini:.3f} | {r.delta_gini:.3f} | {r.brut_sonra:.2f} | "
            f"{r.kal:.2f} | {r.reel:.3f} | {r.yk_med:.3f} | {faz} |"
        )
    s.extend(["", "## Lider − üst %10 (eşli)", ""])
    for hucre in HUCRELER:
        f = k["lider_ust10"].get(hucre, {})
        s.append(
            f"- **{hucre}**: ΔGini fark {f.get('dg_med', float('nan')):.3f}, Δkal {f.get('kal_med', float('nan')):.2f}, "
            f"p_kal = {f.get('kal_p', float('nan')):.4g}."
        )
    s.extend(["", "Tekrar: `python3 odeme_zinciri.py`.", "", "Dosyalar: `odeme_kons12_hucre.csv`, `odeme_kons12.png`, `odeme_kons12_sonuc.json`.", ""])
    return "\n".join(s)


def hukum(k: dict) -> str:
    p = [
        f"Kontrol: kalıcılık {k['soksuz_kal']:.2f}, reel {k['soksuz_reel']:.3f}, eşit Gini {k['gini_kontrol']:.3f}.",
        f"Spearman Gini–kalıcılık (mahsup kolları) {k['sp_gini_kal']:.3f} (p = {k['sp_gini_kal_p']:.3g}).",
    ]
    if k["gini_kirar_destek"]:
        p.append(
            f"Kayıtlı kural: |ΔGini| < 0,05 iken kalıcılık ≥2 düşüyor (mev70 eşli p = {k.get('gini_kirar_p', float('nan')):.3g}). "
            "Küçük Gini değişimi bloke'yi kırar desteklenir."
        )
    else:
        p.append("Küçük ΔGini + büyük kalıcılık düşüşü birlikte kayıtlı eşikte çıkmadı.")
    if k["gini_degil_lider"]:
        p.append(
            "Lider vs üst %10: Gini farkı ≥0,20, kalıcılık farkı anlamsız — Gini düşüşünden çok tek düğüm payı belirliyor."
        )
    else:
        p.append("Gini vs tek düğüm ayrımı kayıtlı kuralla desteklenmedi.")
    if k["fx_zayif_elenmedi"]:
        p.append("Mahsup+dağıt: reel ve fazla 0,05 altında; FX/zayıf halka mahsupla kapanmıyor elenmedi.")
    return " ".join(p)


def main_kons12() -> None:
    stok = stok_yukle()
    pi = pi_aylik()
    print("kons12", N_MC, "seed", SEED0, flush=True)
    dfs: dict[tuple[str, str], pd.DataFrame] = {}
    satir = []
    for hucre in HUCRELER:
        for kol in KOLLAR:
            df = hucre_kos(stok, hucre, kol, pi)
            dfs[(hucre, kol)] = df
            o = ozet_df(df)
            satir.append({"hucre": hucre, "kol": kol, **o})
            print(f"{hucre} {kol:16s} Gini={o['gini']:.3f} dG={o['delta_gini']:.3f} kal={o['kal']:.2f}", flush=True)

    tablo = pd.DataFrame(satir)
    tablo.to_csv(KOK / "odeme_kons12_hucre.csv", index=False)
    grafik(tablo, KOK / "odeme_kons12.png")

    kon = kontrol(stok)
    mahsup_pool = pd.concat([dfs[(h, k)] for h in HUCRELER for k in MAHSUP_KOLLAR], ignore_index=True)
    sp, sp_p = spearmanr(mahsup_pool["gini"], mahsup_pool["kal"])

    # Kucuk delta Gini + kal drop: mahsup vs lider, mev70, |delta_gini_lider| < 0.05
    m70m = dfs[("mev70", "mahsup")]
    m70l = dfs[("mev70", "mahsup_lider")]
    dg = np.abs(m70l["delta_gini"].values)
    mask = dg < 0.05
    p_kir, d_kir = wilcoxon_paired(m70m.loc[mask, "kal"], m70l.loc[mask, "kal"], "greater")
    if mask.sum() == 0:
        p_kir, d_kir = wilcoxon_paired(m70m["kal"], m70l["kal"], "greater")
    gini_kirar_destek = bool(np.median(np.abs(m70l["delta_gini"])) < 0.05 and d_kir >= 2.0 and p_kir < 0.05)

    lider_ust10 = {}
    gini_degil_lider = False
    for hucre in HUCRELER:
        li = dfs[(hucre, "mahsup_lider")]
        u10 = dfs[(hucre, "mahsup_ust10")]
        p_k, d_k = wilcoxon_paired(li["kal"], u10["kal"], "two-sided")
        dg_med = float(np.median(li["gini"] - u10["gini"]))
        lider_ust10[hucre] = {"dg_med": dg_med, "kal_med": d_k, "kal_p": p_k}
        if abs(dg_med) >= 0.20 and p_k >= 0.05:
            gini_degil_lider = True

    dagit = pd.concat([dfs[(h, k)] for h in HUCRELER for k in ("mahsup_lider", "mahsup_ust10")], ignore_index=True)
    faz = dagit["fazla"].dropna()
    fx_zayif_elenmedi = bool(float(dagit["reel"].mean()) < 0.05 and (faz.size == 0 or float(faz.median()) < 0.05))

    karar = {
        "soksuz_kal": kon["soksuz"]["kal"],
        "soksuz_reel": kon["soksuz"]["reel"],
        "gini_kontrol": kon["gini_esit"],
        "sp_gini_kal": float(sp),
        "sp_gini_kal_p": float(sp_p),
        "gini_kirar_destek": gini_kirar_destek,
        "gini_kirar_p": p_kir,
        "gini_kirar_dkal": d_kir,
        "gini_degil_lider": gini_degil_lider,
        "lider_ust10": lider_ust10,
        "fx_zayif_elenmedi": fx_zayif_elenmedi,
    }

    def _json_default(o):
        if isinstance(o, float) and (np.isnan(o) or np.isinf(o)):
            return None
        raise TypeError(type(o))

    sonuc = {
        "uyari": "Stoklar ölçülmüş (TCMB 2026-Q1). Kenar varsayım.",
        "ozet": hukum(karar),
        "karar": json.loads(json.dumps(karar, default=_json_default)),
        "kontrol": json.loads(json.dumps(kon, default=_json_default)),
        "pi_aylik": pi,
        "n_mc": N_MC,
        "seed0": SEED0,
    }
    (KOK / "odeme_kons12_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, tur 12") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor(sonuc, tablo) + ISARET + eski, encoding="utf-8")
    print(sonuc["ozet"])


if __name__ == "__main__":
    main_kons12()
