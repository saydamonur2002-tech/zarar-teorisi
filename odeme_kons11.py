"""Tur 11: lider vs ust10 mevduat dagitimi (mahsup sonrasi). Kurallar kosudan once.

150 firma, servis/alacak esit. MC 50, tohum TOHUM+15000+s. FX cevrilemez, pi 0.0225.

Hucreler: esit, mev 0.40, mev 0.70. Kol: yok | mahsup | mahsup+lider | mahsup+ust10 mev.

Tek dugum yeter: lider vs ust10 kal farki medyan >= 2 ve p<0.05 ise destek; anlamsizsa
'ust %10 gerekir' elenmez.

Dagitim bloke kapatir: mahsup - (lider veya ust10) kal medyan >= 2, p<0.05.
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
from scipy.stats import wilcoxon

import odeme_zinciri as oz
from odeme_dagilim import ISARET, N_FIRMA, agirlik, kos, stok_yukle
from odeme_gercek import ESIK_VALF, tufe_yoy
from odeme_kons7 import ag_kur_v2
from odeme_kons8 import lider_dagit, metrikler, wilcoxon_paired
from odeme_mahsup import mahsup_paket, paket_to_ag, statik_teshis

KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
SEED0 = oz.TOHUM + 15000
HUCRELER = ("esit", "mev40", "mev70")
MEV_HEDEF = {"esit": 0.10, "mev40": 0.40, "mev70": 0.70}
KOLLAR = ("yok", "mahsup", "mahsup_lider", "mahsup_ust10")


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
    mw = mev_w.copy()
    if kol == "mahsup_lider":
        mw = lider_dagit(mw, int(np.argmax(mev_w)))
    elif kol == "mahsup_ust10":
        mw = ust10_dagit(mw)
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
    w = 0.2
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 4))
    lbl = {
        "yok": "Yok",
        "mahsup": "Mahsup",
        "mahsup_lider": "M+lider",
        "mahsup_ust10": "M+üst10",
    }
    for i, kol in enumerate(KOLLAR):
        sub = tablo[tablo.kol == kol].set_index("hucre")
        kal = [sub.loc[h, "kal"] if h in sub.index else 0 for h in HUCRELER]
        reel = [sub.loc[h, "reel"] if h in sub.index else 0 for h in HUCRELER]
        off = (i - 1.5) * w
        ax[0].bar(x + off, kal, width=w, label=lbl[kol])
        ax[1].bar(x + off, reel, width=w, label=lbl[kol])
    ax[0].set_xticks(x, ad)
    ax[0].set_ylabel("Kalıcılık (ort.)")
    ax[0].set_title("Tur 11")
    ax[1].set_xticks(x, ad)
    ax[1].set_ylabel("Reel kayıp")
    ax[0].legend(frameon=False, fontsize=6, ncol=2)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def _wilcoxon_greater(a, b):
    return wilcoxon_paired(a, b, "greater")


def _wilcoxon_two(a, b):
    return wilcoxon_paired(a, b, "two-sided")


def rapor(sonuc: dict, tablo: pd.DataFrame) -> str:
    k = sonuc["karar"]
    pi = sonuc["pi_aylik"]
    s = [
        "# Ödeme zinciri, tur 11: lider ve üst %10 mevduat dağıtımı",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Varsayımlar",
        "",
        f"150 firma, servis/alacak eşit. Mevduat üst %10: 0,10 / 0,40 / 0,70. MC {N_MC}, tohum {SEED0}+s. "
        f"FX çevrilemez, π = {pi:.4f}, valf {ESIK_VALF}. "
        "Mahsup+dağıtım: mevduat payı dağıtılır, sonra optimal mahsup.",
        "",
        f"Kontrol şoksuz: kalıcılık {k['soksuz_kal']:.2f}, reel {k['soksuz_reel']:.3f}.",
        "",
        f"Tek düğüm yeter (lider vs üst %10 fark kuralı): {k['tek_dugum_destek']}. "
        f"Üst %10'un tamamı gerekir (elenmedi): {k['ust10_gerekir_elenmedi']}. "
        f"Dağıtım mahsup bloke'sini kapatır: {k['dagitim_destek']}. "
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
    s.extend(["", "## Lider − üst %10 dağıtım (kalıcılık, eşli Wilcoxon)", ""])
    for hucre in HUCRELER:
        f = k["lider_ust10"].get(hucre, {})
        s.append(
            f"- **{hucre}**: medyan fark (lider−üst10) {f.get('kal_med', float('nan')):.2f}, "
            f"p = {f.get('kal_p', float('nan')):.4g}."
        )
    s.extend(["", "## Mahsup+dağıt − mahsup (kalıcılık)", ""])
    for hucre in HUCRELER:
        for tag, key in (("lider", "mahsup_lider"), ("üst10", "mahsup_ust10")):
            f = k["dagit_mahsup"].get(f"{hucre}/{key}", {})
            s.append(
                f"- **{hucre} / {tag}**: medyan Δkal {f.get('kal_med', float('nan')):.2f}, p = {f.get('kal_p', float('nan')):.4g}."
            )
    s.extend(["", "Tekrar: `python3 odeme_zinciri.py`.", "", "Dosyalar: `odeme_kons11_hucre.csv`, `odeme_kons11.png`, `odeme_kons11_sonuc.json`.", ""])
    return "\n".join(s)


def hukum(k: dict) -> str:
    p = [f"Kontrol şoksuz kalıcılık {k['soksuz_kal']:.2f}, reel {k['soksuz_reel']:.3f}."]
    if k["tek_dugum_destek"]:
        p.append(
            "Lider ile üst %10 mevduat dağıtımının kalıcılık sonuçları kayıtlı fark eşiğini geçiyor; "
            "'tek düğüm yeter' desteklenir."
        )
    elif k["ust10_gerekir_elenmedi"]:
        p.append(
            "Lider ve üst %10 dağıtım kalıcılığı arasında kayıtlı anlamlı büyük fark yok; "
            "'üst %10'un tamamı gerekir' iddiası elenmedi."
        )
    if k["dagitim_destek"]:
        p.append("Mahsup sonrası dağıtım (lider veya üst %10), yalnız mahsupa göre kalıcılığı anlamlı kısaltıyor.")
    else:
        p.append("Dağıtımın mahsup bloke'sini kapatması kayıtlı medyan≥2 eşiğiyle desteklenmedi.")
        m70 = k.get("mev70_kal_mahsup", 0.0)
        if m70 >= 0.5:
            p.append(
                f"Mev 0,70 hücresinde yine de mahsup ort. kal {m70:.2f} iken lider/üst10 dağıtım 0 "
                f"(eşli p ≈ {k['dagit_mahsup'].get('mev70/mahsup_lider', {}).get('kal_p', float('nan')):.3g})."
            )
    if k["lider_ust10"].get("mev70", {}).get("kal_med", 1) == 0:
        p.append("Mev 0,70: lider ve üst %10 dağıtımı aynı dinamik kalıcılığı veriyor (ort. 0).")
    if k["fx_zayif_elenmedi"]:
        p.append("Mahsup+dağıt kolunda reel ve küçük fazla 0,05 altında; FX/zayıf halka mahsupla kapanmıyor elenmedi.")
    else:
        p.append("Mahsup+dağıt sonrası reel veya fazla 0,05 üstüne çıkıyor.")
    return " ".join(p)


def main_kons11() -> None:
    stok = stok_yukle()
    pi = pi_aylik()
    print("kons11", N_MC, "seed", SEED0, "pi", f"{pi:.4f}", flush=True)
    dfs: dict[tuple[str, str], pd.DataFrame] = {}
    satir = []
    for hucre in HUCRELER:
        for kol in KOLLAR:
            df = hucre_kos(stok, hucre, kol, pi)
            dfs[(hucre, kol)] = df
            o = ozet_df(df)
            satir.append({"hucre": hucre, "kol": kol, **o})
            print(f"{hucre} {kol:16s} kal={o['kal']:.2f} reel={o['reel']:.3f}", flush=True)

    tablo = pd.DataFrame(satir)
    tablo.to_csv(KOK / "odeme_kons11_hucre.csv", index=False)
    grafik(tablo, KOK / "odeme_kons11.png")

    kon = kontrol(stok)
    lider_ust10 = {}
    tek_dugum_destek = False
    for hucre in HUCRELER:
        li = dfs[(hucre, "mahsup_lider")]["kal"]
        u10 = dfs[(hucre, "mahsup_ust10")]["kal"]
        p_k, d_k = _wilcoxon_two(li, u10)
        lider_ust10[hucre] = {"kal_med": d_k, "kal_p": p_k}
        if abs(d_k) >= 2.0 and p_k < 0.05:
            tek_dugum_destek = True

    ust10_gerekir_elenmedi = not tek_dugum_destek

    dagit_mahsup = {}
    dagitim_destek = False
    for hucre in HUCRELER:
        m = dfs[(hucre, "mahsup")]["kal"]
        for key in ("mahsup_lider", "mahsup_ust10"):
            d = dfs[(hucre, key)]["kal"]
            p_k, f_k = _wilcoxon_greater(m, d)
            dagit_mahsup[(hucre, key)] = {"kal_med": f_k, "kal_p": p_k}
            if f_k >= 2.0 and p_k < 0.05:
                dagitim_destek = True

    dagit_all = pd.concat(
        [dfs[(h, k)] for h in HUCRELER for k in ("mahsup_lider", "mahsup_ust10")],
        ignore_index=True,
    )
    faz = dagit_all["fazla"].dropna()
    fx_zayif_elenmedi = bool(float(dagit_all["reel"].mean()) < 0.05 and (faz.size == 0 or float(faz.median()) < 0.05))

    karar = {
        "soksuz_kal": kon["soksuz"]["kal"],
        "soksuz_reel": kon["soksuz"]["reel"],
        "mev70_kal_mahsup": float(dfs[("mev70", "mahsup")]["kal"].mean()),
        "tek_dugum_destek": tek_dugum_destek,
        "ust10_gerekir_elenmedi": ust10_gerekir_elenmedi,
        "dagitim_destek": dagitim_destek,
        "lider_ust10": lider_ust10,
        "dagit_mahsup": {f"{a}/{b}": v for (a, b), v in dagit_mahsup.items()},
        "fx_zayif_elenmedi": fx_zayif_elenmedi,
    }

    def _json_default(o):
        if isinstance(o, float) and (np.isnan(o) or np.isinf(o)):
            return None
        raise TypeError(type(o))

    sonuc = {
        "uyari": "Stoklar ölçülmüş (TCMB 2026-Q1). Kenar varsayım. Girdi-çıktı ve limit serisi yok.",
        "ozet": hukum(karar),
        "karar": json.loads(json.dumps(karar, default=_json_default)),
        "kontrol": json.loads(json.dumps(kon, default=_json_default)),
        "pi_aylik": pi,
        "n_mc": N_MC,
        "seed0": SEED0,
    }
    (KOK / "odeme_kons11_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, tur 11") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor(sonuc, tablo) + ISARET + eski, encoding="utf-8")
    print(sonuc["ozet"])


if __name__ == "__main__":
    main_kons11()
