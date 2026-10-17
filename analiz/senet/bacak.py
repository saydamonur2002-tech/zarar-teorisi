"""Taslak bacak. RAPOR.md:15-17,24,47,51.

Mevcut kâğıt patikası (adim4_adres_yonlendirme.kagit_patikasi) mevduat→kâğıt takasını,
düz primi ve kredi daralmasını yazar. Üretim tesisi bu dosyadadır: hasıla, mahsup
sonrası ağa nakit olarak konur. İki ölçek adaydır.

  A_on, A_uc : rev_adim4 çift sayım
  M = θ · A
  F_stok = M            aday: stok bu çeyrekte üretim tesisi
  F_akim = M / 4        aday: bir çeyrek dilimi
  nakit_i += F · w_i / Σw
  Π = τ · min(π · M, R) ; R ölçülmedi, τ=0 ise Π=0
"""
from __future__ import annotations

import json

import rev_sok
from mahsuplasma.mahsup import optimal_mahsup
from mahsuplasma.model import Parametreler, calistir, _tur
from mahsuplasma.odeme import sirali_odeme

from ortak import BETA, KUR, LAM, r2, r4, yaz_json

THETA = (0.0, 0.10, 0.25, 0.50)
PI = (0.02, 0.05)


def yukle_sayi():
    girdi = rev_sok.yukle()
    cift = json.loads(open(rev_sok.KOK / "rev_adim4_sonuc.json", encoding="utf-8").read())["cift_sayim"]
    bant = json.loads(open(rev_sok.KOK / "rev_adim4_sonuc.json", encoding="utf-8").read())["kredi_katsayisi"]["bant"]
    lam_ham = json.loads(open(rev_sok.KOK / "rev_adim2_sonuc.json", encoding="utf-8").read())["lambda_yildiz"]
    lams = sorted(x["lambda"] for x in lam_ham if x["rejim"] == "ceyreklik_akim")
    lam = lams[len(lams) // 2]
    if abs(lam - LAM) > 1e-9:
        raise SystemExit(f"lambda* {lam} beklenen {LAM}")
    return girdi, cift, bant, lam


def olc(g) -> dict:
    p = Parametreler(holding_odeme_orani=0.5, sart_kaldiraci=True, ucret_gecis_beta=BETA)
    r = calistir(g, p)
    a = r["asamalar"]["4_sart_kaldiraci"]
    t = r["teshis"]
    return {
        "temerrut": int(a["temerrut_sayisi"]),
        "kredi": r4(a["kredi_ihtiyaci"]),
        "kilitli": len(t["kilitli"]),
        "batik": len(t["batik"]),
        "kilitli_ad": list(t["kilitli"]),
        "batik_ad": list(t["batik"]),
        "zarar": r4(t["gercek_zarar"]),
    }


def agirlik(g0, kural: str) -> dict[str, float]:
    if kural == "borc":
        w: dict[str, float] = {}
        for b in g0.borclar:
            if g0.firmalar[b.borclu].katman == "araci":
                w[b.borclu] = w.get(b.borclu, 0.0) + b.tutar
        return w
    if kural == "acik":
        net = optimal_mahsup(g0)
        s = sirali_odeme(net, tur=_tur(net), holding_odeme_orani=1.0)
        return {ad: v for ad, v in s["kredi_ihtiyaci"].items() if v > 1e-8 and g0.firmalar[ad].katman == "araci"}
    raise ValueError(kural)


def dagit(g0, F: float, kural: str):
    g = g0.kopya()
    if F <= 1e-12:
        return g
    w = agirlik(g0, kural)
    top = sum(w.values())
    if top <= 1e-12:
        return g
    for ad, v in w.items():
        g.firmalar[ad].nakit += F * v / top
    return g


def acildi(m: dict) -> bool:
    return m["temerrut"] == 0 and m["kredi"] < 0.05


def min_F(g0, kural: str, kriter) -> float | None:
    def iyi(F: float) -> bool:
        m = olc(dagit(g0, F, kural))
        if kriter == "kopru":
            return acildi(m)
        if kriter == "kilit":
            return m["kilitli"] == 0
        return acildi(m) and m["kilitli"] == 0

    if iyi(0.0):
        return 0.0
    hi = 50.0
    while not iyi(hi):
        hi *= 2
        if hi > 200_000:
            return None
    lo = 0.0
    for _ in range(20):
        mid = (lo + hi) / 2
        if iyi(mid):
            hi = mid
        else:
            lo = mid
    return r2(hi)


def sfc(M_h: float, M_f: float, F: float, pi: float, tau: int, R: float) -> dict:
    M = M_h + M_f
    if tau == 0:
        R_et, Pi = 0.0, 0.0
    else:
        R_et = max(0.0, R)
        Pi = min(pi * M, R_et)
    nl = {"H": Pi, "F": (R_et - Pi), "B": 0.0, "K": 0.0, "D": -R_et}
    if abs(sum(nl.values())) > 1e-9 or Pi > tau * R_et + 1e-9:
        raise SystemExit("SFC")
    return {
        "M": r4(M),
        "F": r4(F),
        "Pi": r4(Pi),
        "R": R_et,
        "tau": tau,
        "nl": {k: r4(v) for k, v in nl.items()},
        "nl_toplam": 0.0,
        "nfp_toplam": 0.0,
        "Bp_rezerv_son": r4(-M + F),
        "Kp_TCMB_son": r4(M - F),
        "cikis_nakit": 0.0,
        "havadan_kupon": r4(pi * M),
        "kuram_prim_siniri": True,
    }


def paket(m: dict, F: float) -> dict:
    return {
        "F": r2(F),
        "temerrut": m["temerrut"],
        "kopru": m["kredi"],
        "kilitli": m["kilitli"],
        "batik": m["batik"],
        "zarar": m["zarar"],
        "acildi": acildi(m),
        "kilitli_ad": m["kilitli_ad"],
        "batik_ad": m["batik_ad"],
    }


def main():
    girdi, cift, bant, lam = yukle_sayi()
    A = {"on": float(cift["onerilen"]), "uc": float(cift["adres_toplam_eski"])}
    Ah = {"on": float(cift["H_VF2_ZP8"]), "uc": float(cift["H_VF2_ZP8"]) + float(cift["YP_gercek_kisi"])}
    g_tam, artis = rev_sok.ag_kur(KUR, lam, girdi)
    tam = {}
    for kural in ("borc", "acik"):
        for olcek, carpan in (("stok", 1.0), ("akim", 0.25)):
            for ad in ("on", "uc"):
                for th in THETA:
                    F = th * A[ad] * carpan
                    tam[f"{kural}|{olcek}|{ad}|{th}"] = paket(olc(dagit(g_tam, F, kural)), F)
    taban = {}
    for kural in ("borc", "acik"):
        for kriter in ("kopru", "kilit", "birlikte"):
            taban[f"{kural}|{kriter}"] = min_F(g_tam, kural, kriter)
    seyrek_g = []
    for s in range(rev_sok.TOHUM):
        ken = rev_sok.seyrek_kenar(girdi, 0.25, s)
        if ken is None:
            continue
        g, _ = rev_sok.ag_kur(KUR, lam, girdi, ken)
        seyrek_g.append(g)
    hucre = []
    for g in seyrek_g:
        for kural in ("borc", "acik"):
            for olcek, carpan in (("stok", 1.0), ("akim", 0.25)):
                for ad in ("on", "uc"):
                    for th in THETA:
                        F = th * A[ad] * carpan
                        m = olc(dagit(g, F, kural))
                        hucre.append((kural, olcek, ad, th, m["temerrut"], m["kredi"], m["kilitli"], m["batik"], acildi(m)))

    def _med(xs):
        s = sorted(xs)
        return s[len(s) // 2]

    ozet = {}
    for kural in ("borc", "acik"):
        for olcek in ("stok", "akim"):
            for ad in ("on", "uc"):
                for th in THETA:
                    alt = [h for h in hucre if h[0] == kural and h[1] == olcek and h[2] == ad and h[3] == th]
                    ozet[f"{kural}|{olcek}|{ad}|{th}"] = {
                        "n": len(alt),
                        "temerrut_med": _med([h[4] for h in alt]),
                        "kopru_med": r2(_med([h[5] for h in alt])),
                        "kilitli_med": _med([h[6] for h in alt]),
                        "batik_med": _med([h[7] for h in alt]),
                        "acilan_pay": r4(sum(1 for h in alt if h[8]) / len(alt)) if alt else None,
                    }
    seyrek_min = {}
    for kural in ("borc", "acik"):
        for kriter in ("kopru", "birlikte"):
            vals = [min_F(g, kural, kriter) for g in seyrek_g]
            sayi = [v for v in vals if v is not None]
            seyrek_min[f"{kural}|{kriter}"] = {
                "n": len(vals),
                "yok": sum(v is None for v in vals),
                "med": None if not sayi else _med(sayi),
                "min": None if not sayi else min(sayi),
                "max": None if not sayi else max(sayi),
            }
    prim = []
    for ad, AA in A.items():
        Mh = 0.10 * Ah[ad]
        Mf = 0.10 * (AA - Ah[ad])
        for olcek, carpan in (("stok", 1.0), ("akim", 0.25)):
            F = 0.10 * AA * carpan
            for pi in PI:
                prim.append({
                    "ad": ad, "olcek": olcek, "pi": pi,
                    "tau0": sfc(Mh, Mf, F, pi, 0, 0.0),
                    "tau1_R0": sfc(Mh, Mf, F, pi, 1, 0.0),
                    "tau1_R_esit_kupon": sfc(Mh, Mf, F, pi, 1, pi * 0.10 * AA),
                })
    c_alt, c_ust = float(bant[0]), float(bant[1])
    kredi_bant = {}
    for ad, AA in A.items():
        for th in THETA:
            M = th * AA
            kredi_bant[f"{ad}|{th}"] = {
                "M": r2(M),
                "eski_daralma_yil": [r2(c_alt * M), r2(c_ust * M)],
                "tesis_stok_daralma": 0.0,
                "tesis_akim_TCMB_kalan": r2(M - M / 4),
            }
    out = {
        "etiket": "aday: fungible nakit, stok ve akim olcekleri varsayim; R olculmedi",
        "lam": lam,
        "beta": BETA,
        "kur": KUR,
        "artis_banka": r4(artis),
        "A": A,
        "Ah": Ah,
        "c_bant": [c_alt, c_ust],
        "tam": tam,
        "tam_min_F": taban,
        "seyrek": ozet,
        "seyrek_min_F": seyrek_min,
        "prim_ornek_theta_0_10": prim,
        "kredi_bant": kredi_bant,
    }
    yaz_json("bacak_sonuc.json", out)
    print("bacak", out["artis_banka"], out["tam_min_F"])


if __name__ == "__main__":
    main()
