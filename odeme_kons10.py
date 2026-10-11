"""Tur 10: mevduat konsantrasyonu x mahsup x lider mevduat dagitimi.

150 firma, TCMB 2026-Q1. Servis ve alacak esit (1/N). MC 50, tohum TOHUM+14000+s.
FX cevrilemez, pi aylik 0.0225 (Ocak 2026 TÜFE).

Hucreler: esit, mev ust10 0.40, mev ust10 0.70.
Kol: yok | optimal mahsup | lider mev dagit + mahsup.

Destek mev: ms40 vs ms70 kalicilik (yok kol) medyan fark >= 2, tek yanli p<0.05.
Destek lider: mahsup - mahsup_lider kal medyan >= 2, p<0.05 (esli).
Reel ve kucuk fazla < 0.05 ise 'FX/zayif halka mahsupla kapanmiyor' elenmez.
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
SEED0 = oz.TOHUM + 14000
HUCRELER = ("esit", "mev40", "mev70")
MEV_HEDEF = {"esit": 0.10, "mev40": 0.40, "mev70": 0.70}
KOLLAR = ("yok", "mahsup", "mahsup_lider")


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
    """Brut ozet, statik teshis, kosulacak pak."""
    if kol == "mahsup_lider":
        lider = int(np.argmax(mev_w))
        mev_w = lider_dagit(mev_w, lider)
    pak0 = ag_kur_v2(stok, mev_w, srv_w, alac_w)
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
    hedef = MEV_HEDEF[hucre]
    for s in range(N_MC):
        mev_w, srv_w, alac_w = agirlikler(s, hucre)
        pak_ref = ag_kur_v2(stok, mev_w, srv_w, alac_w)
        pak_run, brut, stat = pak_hazir(stok, mev_w, srv_w, alac_w, kol)
        h, _, yavas = kos(pak_run, pi, True)
        v0 = float(pak_ref["net"]["w0"].sum())
        rows.append(
            {
                "hucre": hucre,
                "kol": kol,
                "mev_hedef": hedef,
                "s": s,
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
    return {"soksuz": metrikler(h0, y0, pak, v0)}


def ozet_df(df: pd.DataFrame) -> dict:
    faz = df["fazla"].dropna()
    return {
        "brut_once": float(df["brut_once"].mean()),
        "brut_sonra": float(df["brut_sonra"].mean()),
        "silinen_oran": float(df["silinen_oran"].mean()),
        "kal": float(df["kal"].mean()),
        "reel": float(df["reel"].mean()),
        "yk_med": float(df["yk_med"].mean()),
        "fazla_med": float(faz.median()) if faz.size else float("nan"),
        "p_fazla_05": float((faz >= 0.05).mean()) if faz.size else float("nan"),
        "temerrut": float(df["temerrut"].mean()),
        "kilitli": float(df["kilitli"].mean()),
        "batik": float(df["batik"].mean()),
    }


def grafik(tablo: pd.DataFrame, dosya: Path) -> None:
    ad = ["Eşit", "Mev 0,40", "Mev 0,70"]
    x = np.arange(3)
    w = 0.25
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for i, kol in enumerate(KOLLAR):
        sub = tablo[tablo.kol == kol].set_index("hucre")
        kal = [sub.loc[h, "kal"] if h in sub.index else 0 for h in HUCRELER]
        reel = [sub.loc[h, "reel"] if h in sub.index else 0 for h in HUCRELER]
        off = (i - 1) * w
        lbl = {"yok": "Mahsupsuz", "mahsup": "Mahsup", "mahsup_lider": "Mahsup+lider mev"}[kol]
        ax[0].bar(x + off, kal, width=w, label=lbl)
        ax[1].bar(x + off, reel, width=w, label=lbl)
    ax[0].set_xticks(x, ad)
    ax[0].set_ylabel("Kalıcılık (ort.)")
    ax[0].set_title("Tur 10 — mevduat × mahsup")
    ax[1].set_xticks(x, ad)
    ax[1].set_ylabel("Reel kayıp")
    ax[0].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def rapor(sonuc: dict, tablo: pd.DataFrame) -> str:
    k = sonuc["karar"]
    pi = sonuc["pi_aylik"]
    s = [
        "# Ödeme zinciri, tur 10: mevduat konsantrasyonu ve mahsup",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Varsayımlar",
        "",
        f"150 firma. Servis ve alacak eşit (1/N). Mevduat üst %10 hedefleri 0,10 / 0,40 / 0,70. "
        f"Monte Carlo {N_MC}, tohum {SEED0}+s. FX çevrilemez, valf eşiği {ESIK_VALF}, π = {pi:.4f}. "
        "Mahsup+lider: lider mevduat payı eşit dağıtılır, ardından optimal mahsup.",
        "",
        f"Kontrol şoksuz: kalıcılık {k['soksuz_kal']:.2f}, reel {k['soksuz_reel']:.3f}.",
        "",
        f"Spearman mevduat hedefi – kalıcılık (mahsupsuz): {k.get('sp_mev_kal')} (kal sabitse tanımsız). "
        f"Mevduat – reel kayıp: {k['sp_mev_reel']:.3f} (p = {k['sp_mev_reel_p']:.4g}).",
        f"Mev konsantrasyonu kalıcılığı uzatır: {k['mev_destek']}. "
        f"Lider mevduat dağıtımı mahsup sonrası bloke kısaltır: {k['lider_destek']}. "
        f"FX/zayıf halka mahsupla kapanmıyor (elenmedi): {k['fx_zayif_elenmedi']}.",
        "",
        "## Hücre × kol",
        "",
        "| Hücre | Kol | Brüt önce | Brüt sonra | Kalıcılık | Reel | Küçük yavaş | Fazla medyan | P(fazla≥0,05) | Temerrüt | Kilitli | Batık |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, r in tablo.iterrows():
        s.append(
            f"| {r.hucre} | {r.kol} | {r.brut_once:.2f} | {r.brut_sonra:.2f} | {r.kal:.2f} | {r.reel:.3f} | "
            f"{r.yk_med:.3f} | {r.fazla_med:.3f} | {r.p_fazla_05:.2f} | {r.temerrut:.1f} | {r.kilitli:.1f} | {r.batik:.1f} |"
        )
    s.extend(["", "## Mahsup+lider − mahsup (Wilcoxon eşli, medyan fark)", ""])
    for hucre in HUCRELER:
        f = k["lider_fark"].get(hucre, {})
        s.append(
            f"- **{hucre}**: Δkal {f.get('kal_med', float('nan')):.2f}, p = {f.get('kal_p', float('nan')):.4g}; "
            f"Δreel {f.get('reel_med', float('nan')):.3f}."
        )
    s.extend(["", "Tekrar: `python3 odeme_zinciri.py`.", "", "Dosyalar: `odeme_kons10_hucre.csv`, `odeme_kons10.png`, `odeme_kons10_sonuc.json`.", ""])
    return "\n".join(s)


def hukum(k: dict) -> str:
    p = [
        f"Kontrol şoksuz kalıcılık {k['soksuz_kal']:.2f}, reel {k['soksuz_reel']:.3f}.",
        f"Spearman mevduat–reel (mahsupsuz) {k['sp_mev_reel']:.3f} (p = {k['sp_mev_reel_p']:.3g}).",
    ]
    if k["mev_destek"]:
        p.append(
            f"Mevduat 0,40 → 0,70 (mahsupsuz) kalıcılık medyan fark {k['mev_kal_fark']:.2f} periyot "
            f"(p = {k['mev_kal_p']:.3g}). Mevduat konsantrasyonu kalıcılığı uzatır desteklenir."
        )
    else:
        p.append(
            f"Mevduat 0,40 → 0,70 fark medyan {k['mev_kal_fark']:.2f}, p = {k['mev_kal_p']:.3g}; "
            "konsantrasyon–kalıcılık iddiası bu turda desteklenmedi."
        )
    if k["lider_destek"]:
        p.append(
            "Mahsup sonrası lider mevduat dağıtımı, yalnız mahsupa göre kalıcılığı anlamlı kısaltıyor "
            f"(en az bir hücrede Δkal medyan ≥ 2, p < 0,05)."
        )
    else:
        p.append(
            "Lider mevduat dağıtımı: önceden kayıtlı medyan ≥ 2 eşiği tutmadı "
            f"(mev70 mahsup ort. kal {k.get('mev70_kal_mahsup', float('nan')):.2f} → lider {k.get('mev70_kal_lider', float('nan')):.2f}, "
            f"eşli p = {k['lider_fark'].get('mev70', {}).get('kal_p', float('nan')):.3g})."
        )
    if k["fx_zayif_elenmedi"]:
        p.append("Mahsup kolunda reel kayıp ve küçük fazla 0,05 altında; 'FX/zayıf halka mahsupla kapanmıyor' elenmedi.")
    else:
        p.append("Mahsup sonrası reel veya fazla 0,05 üstüne çıkıyor; 'kapanmıyor' iddiası zayıflar.")
    return " ".join(p)


def _wilcoxon_greater(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    d = d[np.isfinite(d)]
    if d.size == 0 or np.allclose(d, 0):
        return 1.0, 0.0
    try:
        p = float(wilcoxon(d, alternative="greater").pvalue)
    except ValueError:
        p = 1.0
    return p, float(np.median(d))


def main_kons10() -> None:
    stok = stok_yukle()
    pi = pi_aylik()
    print("kons10", N_MC, "seed", SEED0, "pi", f"{pi:.4f}", flush=True)
    dfs: dict[tuple[str, str], pd.DataFrame] = {}
    satir = []
    for hucre in HUCRELER:
        for kol in KOLLAR:
            df = hucre_kos(stok, hucre, kol, pi)
            dfs[(hucre, kol)] = df
            o = ozet_df(df)
            satir.append({"hucre": hucre, "kol": kol, **o})
            print(f"{hucre} {kol:14s} kal={o['kal']:.2f} reel={o['reel']:.3f}", flush=True)

    tablo = pd.DataFrame(satir)
    tablo.to_csv(KOK / "odeme_kons10_hucre.csv", index=False)
    grafik(tablo, KOK / "odeme_kons10.png")

    kon = kontrol(stok)
    y40 = dfs[("mev40", "yok")]["kal"].values
    y70 = dfs[("mev70", "yok")]["kal"].values
    try:
        p_mev = float(wilcoxon(y70, y40, alternative="greater").pvalue)
    except ValueError:
        p_mev = 1.0
    mev_fark = float(np.median(y70) - np.median(y40))
    mev_destek = bool(mev_fark >= 2.0 and p_mev < 0.05)

    yok_all = pd.concat([dfs[(h, "yok")] for h in HUCRELER], ignore_index=True)
    if yok_all["kal"].nunique() > 1:
        sp, sp_p = spearmanr(yok_all["mev_hedef"], yok_all["kal"])
    else:
        sp, sp_p = float("nan"), float("nan")
    sp_reel, sp_reel_p = spearmanr(yok_all["mev_hedef"], yok_all["reel"])

    lider_fark = {}
    lider_destek = False
    for hucre in HUCRELER:
        m = dfs[(hucre, "mahsup")]
        ml = dfs[(hucre, "mahsup_lider")]
        p_k, d_k = _wilcoxon_greater(m["kal"], ml["kal"])
        p_r, d_r = _wilcoxon_greater(m["reel"], ml["reel"])
        lider_fark[hucre] = {"kal_med": d_k, "kal_p": p_k, "reel_med": d_r, "reel_p": p_r}
        if d_k >= 2.0 and p_k < 0.05:
            lider_destek = True

    mahsup_all = pd.concat([dfs[(h, "mahsup")] for h in HUCRELER], ignore_index=True)
    reel_m = float(mahsup_all["reel"].mean())
    faz_m = float(mahsup_all["fazla"].median()) if mahsup_all["fazla"].notna().any() else float("nan")
    fx_zayif_elenmedi = bool(reel_m < 0.05 and (not np.isfinite(faz_m) or faz_m < 0.05))

    karar = {
        "soksuz_kal": kon["soksuz"]["kal"],
        "soksuz_reel": kon["soksuz"]["reel"],
        "mev70_kal_mahsup": float(dfs[("mev70", "mahsup")]["kal"].mean()),
        "mev70_kal_lider": float(dfs[("mev70", "mahsup_lider")]["kal"].mean()),
        "sp_mev_kal": float(sp) if np.isfinite(sp) else None,
        "sp_mev_kal_p": float(sp_p) if np.isfinite(sp_p) else None,
        "sp_mev_reel": float(sp_reel),
        "sp_mev_reel_p": float(sp_reel_p),
        "mev_destek": mev_destek,
        "mev_kal_fark": mev_fark,
        "mev_kal_p": p_mev,
        "lider_destek": lider_destek,
        "lider_fark": lider_fark,
        "fx_zayif_elenmedi": fx_zayif_elenmedi,
    }
    ozet_metin = hukum(karar)

    def _json_default(o):
        if isinstance(o, float) and (np.isnan(o) or np.isinf(o)):
            return None
        raise TypeError(type(o))

    sonuc = {
        "uyari": "Stoklar ölçülmüş (TCMB 2026-Q1). Kenar varsayım. Girdi-çıktı ve limit serisi yok.",
        "ozet": ozet_metin,
        "karar": karar,
        "kontrol": json.loads(json.dumps(kon, default=_json_default)),
        "pi_aylik": pi,
        "n_mc": N_MC,
        "seed0": SEED0,
    }
    (KOK / "odeme_kons10_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, tur 10") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor(sonuc, tablo) + ISARET + eski, encoding="utf-8")
    print(ozet_metin)


if __name__ == "__main__":
    main_kons10()
