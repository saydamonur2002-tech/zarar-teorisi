"""Hane ve firma tamponunun ay ay kapsaması.

Tanımlar depoda nasıl duruyorsa öyle kullanılır. Yeni tampon uydurulmaz.

Firma ve hane agregatı (`odeme_gercek`):
  likidite = para ve mevduat varlığı
  aylık servis = kredi × (kısa pay / 12 + (1 − kısa pay) / 60) + diğer yükümlülük / 12
  ay = likidite / aylık servis
  Vade (12 / 60 / 12) ölçülmemiş varsayımdır; formül değişmez.

İki okuma, ikisi de depoda:
  dış akım = servis (`dagilim_stresi`, ödeme zinciri): stok ay ay değişmez, ufukta tükenmez.
  kapsama takvimi: deponun "mevduat bunun X katı" cümlesi. Dış akım 0, stok her ay servis kadar azalır.

Ha net varlık (`hane_alt`): varlık payı %5, borç payı %40. NFP < 0 ise gözlem ayında tükenmiş.
Ha brüt: aynı paylarla mevduat / (borç × 0,35 / 12). Paylar ve %35 `uc_kural_senaryo` varsayımıdır.
alt20 borç/gelir ayı sabit 2,8'tir; ay yolu yoktur.

Ufuk: `odeme_zinciri.T` = 24 ay. Tükenme daha geçse tarih yine yazılır.
Dağılım bandı `dagilim_stresi` sigma ızgarası (lognormal, toplam korunur).

Çalıştır: python3 tampon_tukenme.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import dagilim_stresi as dg
import hane_alt
import odeme_gercek as og
import odeme_zinciri as oz
from akis_model import IDX, INSTR, load, panel

KOK = Path(__file__).resolve().parent
UFUK = oz.T
SIGMA = (0.15, 0.4, 0.7, 1.1)


def add_months(ym: str, n: int) -> str:
    y, m = (int(x) for x in ym.split("-"))
    m += n
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}"


def ceyrek_sonu(donem: str) -> str:
    y, q = donem.split("-Q")
    return f"{y}-{int(q) * 3:02d}"


def olc(donem: str) -> dict:
    stab, _, tcs, _ = load()
    A, Y = panel(stab, tcs, donem)
    ad = list(INSTR)
    ik, im, idg = ad.index("kredi"), ad.index("para_mevduat"), ad.index("diger")
    pay = og.kisa_pay(stab, tcs)
    aylik = Y[ik] * (pay / og.KISA_AY + (1.0 - pay) / og.UZUN_AY) + Y[idg] / og.DIGER_AY
    out = {}
    for s, i in IDX.items():
        lik = float(A[im, i] / 1e9)
        srv = float(aylik[i] / 1e9)
        borc = float(Y[:, i].sum() / 1e9)
        out[s] = {"likidite_tr": lik, "aylik_servis_tr": srv, "ay": None if srv <= 0 else lik / srv, "borc_tr": borc}
    return out


def tukenme_ayi(gozlem: str, ay: float | None) -> str | None:
    if ay is None:
        return None
    if ay <= 0:
        return gozlem
    return add_months(gozlem, math.ceil(ay - 1e-12))


def yol(gozlem: str, lik: float, srv: float, n: int, dis_akim: bool) -> list[dict]:
    satir = []
    for t in range(n + 1):
        stok = lik if dis_akim else max(lik - t * srv, 0.0)
        satir.append({"ay": add_months(gozlem, t), "stok_tr": round(stok, 4), "kalan_ay": None if srv <= 0 else round(stok / srv, 3)})
    return satir


def dagilim_band(mev: float, srv: float) -> list[dict]:
    satir = []
    for sigma in SIGMA:
        rng = np.random.default_rng(dg.TOHUM + int(sigma * 1000))
        m = dg.dagit(mev, dg.N, sigma, rng)
        s = dg.dagit(srv, dg.N, max(0.1, sigma * 0.6), rng)
        t = m / np.maximum(s, 1e-9)
        p10, p50, p90 = (float(x) for x in np.percentile(t, [10, 50, 90]))
        satir.append({
            "sigma": sigma,
            "p10_ay": round(p10, 2), "p50_ay": round(p50, 2), "p90_ay": round(p90, 2),
            "bas_sik_pay": round(float((t < dg.TAMPON_ESIK).mean()), 3),
        })
    return satir


def ha_satir(olcu_h: dict, gozlem: str) -> dict:
    varlik = 0.05 * olcu_h["likidite_tr"]
    borc = hane_alt.D_A_BASE * olcu_h["borc_tr"]
    nfp = varlik - borc
    srv = borc * 0.35 / 12
    ay = None if srv <= 0 else varlik / srv
    return {
        "varlik_payi": 0.05, "borc_payi": hane_alt.D_A_BASE, "servis_orani": 0.35,
        "varlik_tr": round(varlik, 3), "borc_tr": round(borc, 3), "NFP_tr": round(nfp, 3),
        "aylik_servis_tr": round(srv, 4), "brut_ay": None if ay is None else round(ay, 2),
        "net_tukenme": gozlem if nfp < 0 else "ufukta tükenmez (NFP artı; ay yolu tanımlı değil)",
        "brut_tukenme_dis_akim_sifir": tukenme_ayi(gozlem, ay),
        "not": "Paylar ve yıllık servis %35 varsayımdır (hane_alt, uc_kural_senaryo). Ölçülmüş hane altı mevduat serisi yoktur.",
    }


def ciz(paket: dict, dosya: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 4.6))
    for ad, renk in (("F", "#E45756"), ("H", "#4C78A8")):
        yol_s = paket["yol"][ad]["dis_akim_sifir"]
        xs = [r["ay"] for r in yol_s]
        ys = [r["stok_tr"] for r in yol_s]
        ax.plot(xs, ys, color=renk, label=f"{ad} stok, dış akım 0")
        ax.axhline(paket["olcu"][ad]["likidite_tr"], color=renk, ls="--", lw=1, label=f"{ad} stok, dış akım = servis")
    ax.set_title(f"Tampon stoku, {paket['donem']} sonu. Kesik çizgi model senaryosu (tükenmez).")
    ax.set_ylabel("trilyon TL")
    adim = max(1, len(paket["yol"]["F"]["dis_akim_sifir"]) // 8)
    ax.set_xticks(range(0, len(paket["yol"]["F"]["dis_akim_sifir"]), adim))
    ax.set_xticklabels([paket["yol"]["F"]["dis_akim_sifir"][i]["ay"] for i in range(0, len(paket["yol"]["F"]["dis_akim_sifir"]), adim)], rotation=45, ha="right")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def main() -> None:
    stab, _, tcs, _ = load()
    donemler = sorted({k[1] for k in stab if k[0] == "F" and k[1] >= "2026-Q1"})
    donem = donemler[-1]
    once = "2026-Q1" if "2026-Q1" in donemler else donemler[0]
    olcu = olc(donem)
    olcu_once = olc(once)
    gozlem = ceyrek_sonu(donem)
    ufuk_ciz = UFUK
    for s in ("H", "F"):
        ay = olcu[s]["ay"] or 0
        ufuk_ciz = max(ufuk_ciz, math.ceil(ay))
    ufuk_ciz = min(ufuk_ciz, 60)
    yollar = {}
    ozet = {}
    for s in ("H", "F"):
        lik, srv, ay = olcu[s]["likidite_tr"], olcu[s]["aylik_servis_tr"], olcu[s]["ay"]
        sifir = yol(gozlem, lik, srv, ufuk_ciz, False)
        akar = yol(gozlem, lik, srv, min(UFUK, ufuk_ciz), True)
        yollar[s] = {"dis_akim_sifir": sifir, "dis_akim_servis": akar}
        ozet[s] = {
            "likidite_tr": round(lik, 3), "aylik_servis_tr": round(srv, 3),
            "ay": None if ay is None else round(ay, 2),
            "tukenme_dis_akim_sifir": tukenme_ayi(gozlem, ay),
            "tukenme_dis_akim_servis": "tükenmez",
            "onceki": {
                "donem": once,
                "likidite_tr": round(olcu_once[s]["likidite_tr"], 3),
                "aylik_servis_tr": round(olcu_once[s]["aylik_servis_tr"], 3),
                "ay": None if olcu_once[s]["ay"] is None else round(olcu_once[s]["ay"], 2),
                "tukenme_dis_akim_sifir": tukenme_ayi(ceyrek_sonu(once), olcu_once[s]["ay"]),
            },
        }
    ha = ha_satir(olcu["H"], gozlem)
    ha_once = ha_satir(olcu_once["H"], ceyrek_sonu(once))
    band = dagilim_band(olcu["F"]["likidite_tr"], olcu["F"]["aylik_servis_tr"])
    for b in band:
        b["p10_tukenme"] = tukenme_ayi(gozlem, b["p10_ay"])
        b["p50_tukenme"] = tukenme_ayi(gozlem, b["p50_ay"])
        b["p90_tukenme"] = tukenme_ayi(gozlem, b["p90_ay"])
    paket = {
        "donem": donem,
        "gozlem_ayi": gozlem,
        "ufuk_ay": UFUK,
        "ufuk_kaynak": "odeme_zinciri.T = 24. Tablo, tükenme ayına kadar uzar (tavan 60).",
        "dagilim_ufuk_ay": dg.T,
        "tanim": {
            "agregat": "para_mevduat / aylık anapara servisi (odeme_gercek.ag_olc)",
            "dis_akim_servis": "dagilim_stresi: dış akım her düğüme kendi servisini verir, agregat stok sabit",
            "dis_akim_sifir": "aynı oranın takvimi; dış akım yok",
            "vade": "kısa kredi 12 ay, uzun kredi 60 ay, diğer 12 ay; ölçülmedi",
            "ha": "hane_alt payları ve uc_kural servis %35; ölçülmüş alt kırılım yok",
            "alt20": "uc_kural_senaryo.alt20_borc_gelir_ay = 2.8 sabit. Ay ay tükenme tanımı yok. 2.8 > 2.5 olduğu için limit stresi baştan açık.",
            "faiz_durdurma": "κ anapara servisini değiştirmez (adim3 yalnız tahakkuk). Tampon ayı κ=0.5 ile değişmez.",
            "fx": "FX mevduat/FX kredi bir oran (odeme_gercek); ay cinsinden tükenme tanımı yok.",
        },
        "olcu": ozet,
        "ha": {"guncel": ha, "onceki": ha_once},
        "firma_dagilim": band,
        "yol": yollar,
    }
    stab, _, tcs, _ = load()
    A, Y = panel(stab, tcs, donem)
    ik, im = list(INSTR).index("kredi"), list(INSTR).index("para_mevduat")
    fx_kredi = og.F_KREDI * float(Y[ik, IDX["F"]])
    fx_mev = og.F_MEV * float(A[im, IDX["F"]])
    paket["fx_kapsama_F"] = round(fx_mev / fx_kredi, 3) if fx_kredi else None
    paket.pop("yol")
    (KOK / "tampon_tukenme.json").write_text(json.dumps({**paket, "yol_ozet": {
        s: {"ilk": yollar[s]["dis_akim_sifir"][0], "son": yollar[s]["dis_akim_sifir"][-1]} for s in ("H", "F")
    }}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (KOK / "tampon_tukenme.csv").open("w", encoding="utf-8-sig", newline="") as f:
        import csv
        w = csv.writer(f)
        w.writerow(["sektor", "senaryo", "ay", "stok_trilyon", "kalan_ay"])
        for s in ("H", "F"):
            for ad, blok in (("dis_akim_sifir", yollar[s]["dis_akim_sifir"]), ("dis_akim_servis", yollar[s]["dis_akim_servis"])):
                for r in blok:
                    w.writerow([s, ad, r["ay"], r["stok_tr"], r["kalan_ay"]])
    paket["yol"] = yollar
    ciz(paket, KOK / "tampon_tukenme.png")
    print(json.dumps(ozet, ensure_ascii=False, indent=2))
    print("HA", json.dumps(ha, ensure_ascii=False))
    print("BAND", band)
    print("donem", donem)


if __name__ == "__main__":
    main()
