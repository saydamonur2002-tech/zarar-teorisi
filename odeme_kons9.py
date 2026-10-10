"""Tur 9: mahsup sonrasi Tur 8 soku. Kurallar kosudan once.

150 firma, TCMB 2026-Q1 toplamlari sabit. Kenar kurali ayni.
Monte Carlo 50, tohum TOHUM+13000+s. FX cevrilemez (hat x 0.30), valf pi Ocak 2026 aylik.

Hucreler: esit, mev+srv 0.70, mev+srv+alac 0.70. Kol: mahsupsuz (Tur 8) / optimal mahsup.

Destek: mahsupsuz - mahsup kalicilik medyan >= 2 ve Wilcoxon tek yanli p<0.05.
Mahsup reel kaybi ve kucuk fazlayi kapatmaz: reel fark ve fazla medyan < 0.05 ise iddia elenmez.

Kontrol soksuz: kalicilik 0, reel 0.
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
from odeme_kons8 import K70, metrikler, wilcoxon_paired
from odeme_mahsup import mahsup_paket, statik_teshis

KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
SEED0 = oz.TOHUM + 13000


def agirlikler(s: int, hucre: str):
    if hucre == "esit":
        u = np.full(N_FIRMA, 1.0 / N_FIRMA)
        return u.copy(), u.copy(), u.copy()
    mev_w = agirlik(N_FIRMA, K70, SEED0 + s)
    srv_w = agirlik(N_FIRMA, K70, SEED0 + 50000 + s)
    if hucre == "ms70":
        alac_w = np.full(N_FIRMA, 1.0 / N_FIRMA)
    else:
        alac_w = agirlik(N_FIRMA, K70, SEED0 + 60000 + s)
    return mev_w, srv_w, alac_w


def pi_aylik() -> float:
    t = tufe_yoy()
    return float((1.0 + t["yoy"]) ** (1.0 / 12.0) - 1.0)


def hucre_kos(stok, hucre: str, mahsup: bool, pi: float) -> pd.DataFrame:
    rows = []
    for s in range(N_MC):
        mev_w, srv_w, alac_w = agirlikler(s, hucre)
        pak = ag_kur_v2(stok, mev_w, srv_w, alac_w)
        ag0 = None
        if mahsup:
            pak_m, oz, ag0, ag1 = mahsup_paket(pak, "optimal")
            stat = statik_teshis(ag1)
            brut_once, brut_sonra = oz["brut_once"], oz["brut_sonra"]
            pak_run = pak_m
        else:
            from odeme_mahsup import paket_to_ag

            ag0 = paket_to_ag(pak)
            brut_once = brut_sonra = ag0.brut_borc()
            stat = statik_teshis(ag0)
            pak_run = pak
        h, _, yavas = kos(pak_run, pi, True)
        v0 = float(pak["net"]["w0"].sum())
        rows.append(
            {
                "hucre": hucre,
                "kol": "mahsup" if mahsup else "yok",
                "s": s,
                "brut_once": brut_once,
                "brut_sonra": brut_sonra,
                "silinen_oran": (brut_once - brut_sonra) / brut_once if brut_once else 0.0,
                **stat,
                **metrikler(h, yavas, pak_run, v0),
            }
        )
    return pd.DataFrame(rows)


def kontrol(stok, pi: float) -> dict:
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
    hucreler = ["esit", "ms70", "msa70"]
    ad = ["Eşit", "M+S 0,70", "M+S+A 0,70"]
    x = np.arange(3)
    w = 0.35
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 4))
    for i, kol in enumerate(("yok", "mahsup")):
        sub = tablo[tablo.kol == kol].set_index("hucre")
        kal = [sub.loc[h, "kal"] if h in sub.index else 0 for h in hucreler]
        reel = [sub.loc[h, "reel"] if h in sub.index else 0 for h in hucreler]
        off = (i - 0.5) * w
        ax[0].bar(x + off, kal, width=w, label="Mahsupsuz" if kol == "yok" else "Mahsup")
        ax[1].bar(x + off, reel, width=w, label="Mahsupsuz" if kol == "yok" else "Mahsup")
    ax[0].set_xticks(x, ad)
    ax[0].set_ylabel("Kalıcılık (ort.)")
    ax[0].set_title("Tur 9 — mahsup × şok")
    ax[1].set_xticks(x, ad)
    ax[1].set_ylabel("Reel kayıp")
    ax[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def rapor(sonuc: dict, tablo: pd.DataFrame) -> str:
    k = sonuc["karar"]
    pi = sonuc["pi_aylik"]
    s = [
        "# Ödeme zinciri, tur 9: mahsup + FX şoku",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Varsayımlar",
        "",
        f"150 firma. TCMB 2026-Q1 toplamları sabit. Monte Carlo {N_MC}, tohum {SEED0}+s. "
        f"FX çevrilemez (fx_sok, hat ×0,30). Valf eşiği {ESIK_VALF}, π aylık {pi:.4f} (Ocak 2026 TÜFE). "
        "Mahsup: optimal_mahsup (net pozisyon korunur). Şok mahsup sonrası aynı dinamik kural.",
        "",
        f"Kontrol şoksuz: kalıcılık {k['soksuz_kal']:.2f}, reel {k['soksuz_reel']:.3f}.",
        "",
        f"Mahsup kalıcılığı kısaltır (destek): {k['mahsup_kal_destek']}. "
        f"Mahsup reel/zayıf halkayı kapatmaz (elenmedi): {k['mahsup_reel_elenmedi']}.",
        "",
        "## Hücre × kol (ortalama)",
        "",
        "| Hücre | Kol | Brüt önce | Brüt sonra | Silinen % | Kalıcılık | Reel | Küçük yavaş | Fazla medyan | P(fazla≥0,05) | Temerrüt | Kilitli | Batık |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, r in tablo.iterrows():
        s.append(
            f"| {r.hucre} | {r.kol} | {r.brut_once:.2f} | {r.brut_sonra:.2f} | {100 * r.silinen_oran:.1f} | "
            f"{r.kal:.2f} | {r.reel:.3f} | {r.yk_med:.3f} | {r.fazla_med:.3f} | {r.p_fazla_05:.2f} | "
            f"{r.temerrut:.1f} | {r.kilitli:.1f} | {r.batik:.1f} |"
        )
    s.extend(["", "## Mahsup − mahsupsuz (Wilcoxon eşli)", ""])
    for hucre in ("esit", "ms70", "msa70"):
        p = k["fark"].get(hucre, {})
        s.append(
            f"- **{hucre}**: Δkal medyan {p.get('kal_med', float('nan')):.2f}, p = {p.get('kal_p', float('nan')):.4g}; "
            f"Δreel {p.get('reel_med', float('nan')):.3f}, p = {p.get('reel_p', float('nan')):.4g}; "
            f"Δfazla {p.get('fazla_med', float('nan')):.3f}."
        )
    s.extend(["", "Tekrar: `python3 odeme_zinciri.py`.", "", "Dosyalar: `odeme_kons9_hucre.csv`, `odeme_kons9.png`, `odeme_kons9_sonuc.json`.", ""])
    return "\n".join(s)


def hukum(k: dict) -> str:
    parca = [f"Kontrol şoksuz kalıcılık {k['soksuz_kal']:.2f}, reel {k['soksuz_reel']:.3f}."]
    if k["mahsup_kal_destek"]:
        parca.append(
            "En az bir hücrede mahsup, mahsupsuz koluna göre kalıcılığı anlamlı kısaltıyor "
            f"(ör. msa70 Δkal medyan {k['fark']['msa70']['kal_med']:.2f}, p = {k['fark']['msa70']['kal_p']:.3g}). "
            "'Mahsup sistemik bloke'yi kısaltır' desteklenir."
        )
    else:
        parca.append("Mahsup sonrası kalıcılık farkı pratik eşik veya p eşiğini geçmedi; 'bloke kısalır' iddiası bu turda desteklenmedi.")
    if k["mahsup_reel_elenmedi"]:
        parca.append(
            "Mahsup sonrası reel kayıp ve küçük fazla farkları 5 puanın altında; "
            "'mahsup FX kaybını ve zayıf halkayı kapatır' iddiası elenmedi (kapatmıyor)."
        )
    else:
        parca.append("Mahsup reel kayıp veya küçük fazlada anlamlı iyileşme gösterdi; 'kapatmaz' iddiası zayıfladı.")
    return " ".join(parca)


def main_kons9() -> None:
    stok = stok_yukle()
    pi = pi_aylik()
    print("kons9", N_MC, "seed", SEED0, "pi", f"{pi:.4f}", flush=True)
    dfs = {}
    satir = []
    for hucre in ("esit", "ms70", "msa70"):
        for mahsup in (False, True):
            df = hucre_kos(stok, hucre, mahsup, pi)
            dfs[(hucre, mahsup)] = df
            o = ozet_df(df)
            satir.append({"hucre": hucre, "kol": "mahsup" if mahsup else "yok", **o})
            print(
                f"{hucre} {'mahsup' if mahsup else 'yok':6s} kal={o['kal']:.2f} reel={o['reel']:.3f} "
                f"brut {o['brut_once']:.2f}->{o['brut_sonra']:.2f}",
                flush=True,
            )

    tablo = pd.DataFrame(satir)
    tablo.to_csv(KOK / "odeme_kons9_hucre.csv", index=False)
    grafik(tablo, KOK / "odeme_kons9.png")

    kon = kontrol(stok, pi)
    fark = {}
    kal_destek = False
    reel_elenmedi = True
    for hucre in ("esit", "ms70", "msa70"):
        y = dfs[(hucre, False)]
        m = dfs[(hucre, True)]
        p_k, d_k = wilcoxon_paired(y["kal"], m["kal"], "greater")
        p_r, d_r = wilcoxon_paired(y["reel"], m["reel"], "greater")
        p_f, d_f = wilcoxon_paired(y["fazla"], m["fazla"], "greater")
        fark[hucre] = {"kal_med": d_k, "kal_p": p_k, "reel_med": d_r, "reel_p": p_r, "fazla_med": d_f}
        if d_k >= 2.0 and p_k < 0.05:
            kal_destek = True
        faz_m = float(m["fazla"].median())
        reel_d = float(m["reel"].mean() - y["reel"].mean())
        if abs(reel_d) >= 0.05 or (np.isfinite(faz_m) and faz_m >= 0.05):
            reel_elenmedi = False

    karar = {
        "soksuz_kal": kon["soksuz"]["kal"],
        "soksuz_reel": kon["soksuz"]["reel"],
        "mahsup_kal_destek": kal_destek,
        "mahsup_reel_elenmedi": reel_elenmedi,
        "fark": fark,
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

    (KOK / "odeme_kons9_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, tur 9") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor(sonuc, tablo) + ISARET + eski, encoding="utf-8")
    print(ozet_metin)


if __name__ == "__main__":
    main_kons9()
