"""Taslak rant kapısı.

K1 ölçülebilir vekil: yalnız mahsup sonrası aracı firmanın ticari+ücret açığı;
   kendi nakdi önce bu borca yazılır. BANKA ve holding alacaklısına pay yok.
K2 firma tavanı = kendi açığı. Fazla K′'de kalır.
K3 yoğunlaşma: açığı olanlar arasında eşit pay tavanı 1/n (aday).
K4 pençe: fungible nakde konursa BANKA'ya kayan kısım ayrıca ölçülür; halkada o kayış 0.
K5 e-fatura / Sayıştay: repoda eşleşme ve ödenmeyen emir yok. Sıkı kapı uygun pay 0 (aday okuma).
Prim: endeks 1, R yok → ödenen prim 0. 6/7 prim havuzuna aittir, anaparaya değil.
"""
from __future__ import annotations

import rev_sok
from mahsuplasma.mahsup import optimal_mahsup
from mahsuplasma.model import Parametreler, calistir, _tur
from mahsuplasma.odeme import sirali_odeme

from ortak import BETA, KUR, LAM, adres, med, r2, r4, yaz_json

THETA = (0.10, 0.25, 0.50)


def sinif(ag, b):
    al = b.alacakli
    if al == "BANKA":
        return "banka"
    if al not in ag.firmalar or ag.firmalar[al].katman == "holding":
        return "holding"
    if b.ucret or ag.firmalar[al].katman == "hane":
        return "ucret"
    return "ticari"


def parcala_pro_rata(ag):
    tur = _tur(ag)
    nakit = {ad: f.nakit for ad, f in ag.firmalar.items()}
    kalan = [b.tutar for b in ag.borclar]
    for t in range(1, tur + 1):
        gelen = {ad: 0.0 for ad in ag.firmalar}
        vadeli = {}
        for k, b in enumerate(ag.borclar):
            if b.vade <= t and kalan[k] > 1e-12:
                vadeli.setdefault(b.borclu, []).append(k)
        for ad, idx in vadeli.items():
            istenen = sum(kalan[k] for k in idx)
            od = min(nakit[ad], istenen)
            pay = od / istenen if istenen else 0.0
            for k in idx:
                o = kalan[k] * pay
                kalan[k] -= o
                gelen[ag.borclar[k].alacakli] += o
            nakit[ad] -= od
        for ad, v in gelen.items():
            nakit[ad] += v
    out = {"ticari": 0.0, "ucret": 0.0, "banka": 0.0, "holding": 0.0}
    for k, b in enumerate(ag.borclar):
        out[sinif(ag, b)] += kalan[k]
    return {k: r4(v) for k, v in out.items()}


def halka(ag, butce, yogunlasma: bool):
    tur = _tur(ag)
    nakit = {ad: f.nakit for ad, f in ag.firmalar.items()}
    kalan = [b.tutar for b in ag.borclar]
    cekilen = 0.0
    for t in range(1, tur + 1):
        gelen = {ad: 0.0 for ad in ag.firmalar}
        vadeli = {}
        for k, b in enumerate(ag.borclar):
            if b.vade <= t and kalan[k] > 1e-12:
                vadeli.setdefault(b.borclu, []).append(k)
        ihtiyac = {}
        for ad, idx in vadeli.items():
            if ag.firmalar[ad].katman != "araci":
                continue
            prod = sum(kalan[k] for k in idx if sinif(ag, ag.borclar[k]) in ("ticari", "ucret"))
            ihtiyac[ad] = max(0.0, prod - nakit[ad])
        top = sum(ihtiyac.values())
        pay = {}
        if top > 1e-12 and butce - cekilen > 1e-12:
            n = len(ihtiyac)
            tavan = (top / n) if yogunlasma and n else None
            hak = {ad: (min(v, tavan) if tavan is not None else v) for ad, v in ihtiyac.items()}
            hak_top = sum(hak.values())
            olcek = min(1.0, (butce - cekilen) / hak_top) if hak_top else 0.0
            pay = {ad: hak[ad] * olcek for ad in hak}
        for ad, idx in vadeli.items():
            prod_idx = [k for k in idx if sinif(ag, ag.borclar[k]) in ("ticari", "ucret")]
            fin_idx = [k for k in idx if k not in prod_idx]
            prod = sum(kalan[k] for k in prod_idx)
            fin = sum(kalan[k] for k in fin_idx)
            kendi = min(nakit[ad], prod)
            ek = pay.get(ad, 0.0) if ag.firmalar[ad].katman == "araci" else 0.0
            ek = min(ek, max(0.0, prod - kendi))
            cekilen += ek
            ode_prod = kendi + ek
            if prod > 1e-12 and ode_prod > 0:
                p = ode_prod / prod
                for k in prod_idx:
                    o = kalan[k] * p
                    kalan[k] -= o
                    gelen[ag.borclar[k].alacakli] += o
            nakit[ad] -= kendi
            ode_fin = min(nakit[ad], fin)
            if fin > 1e-12 and ode_fin > 0:
                p = ode_fin / fin
                for k in fin_idx:
                    o = kalan[k] * p
                    kalan[k] -= o
                    gelen[ag.borclar[k].alacakli] += o
            nakit[ad] -= ode_fin
        for ad, v in gelen.items():
            nakit[ad] += v
    out = {"ticari": 0.0, "ucret": 0.0, "banka": 0.0, "holding": 0.0}
    araci = 0.0
    for k, b in enumerate(ag.borclar):
        sin = sinif(ag, b)
        out[sin] += kalan[k]
        if ag.firmalar[b.borclu].katman == "araci" and sin in ("ticari", "ucret"):
            araci += kalan[k]
    out = {k: r4(v) for k, v in out.items()}
    out["kopru"] = r4(sum(out[k] for k in ("ticari", "ucret", "banka", "holding")))
    out["cekilen"] = r4(cekilen)
    out["atil"] = r4(max(0.0, butce - cekilen))
    out["uretim_kalan"] = r4(out["ticari"] + out["ucret"])
    out["araci"] = r4(araci)
    return out


def fungible_banka(ag, F):
    g = ag.kopya()
    baz = parcala_pro_rata(g)
    s = sirali_odeme(g, tur=_tur(g), holding_odeme_orani=1.0)
    bosluk = {ad: v for ad, v in s["kredi_ihtiyaci"].items() if v > 1e-8 and g.firmalar[ad].katman == "araci"}
    top = sum(bosluk.values())
    if top > 0 and F > 0:
        for ad, v in bosluk.items():
            g.firmalar[ad].nakit += F * v / top
    sonra = parcala_pro_rata(g)
    return {
        "banka_baz": baz["banka"],
        "banka_sonra": sonra["banka"],
        "kayis": r4(max(0.0, baz["banka"] - sonra["banka"])),
        "kopru_sonra": r4(sum(sonra.values())),
    }


def _min_olcu(net, yogunlasma: bool, alan: str):
    def iyi(F):
        return halka(net, F, yogunlasma)[alan] < 0.05

    if iyi(0.0):
        return 0.0
    hi = 20.0
    while not iyi(hi):
        once = halka(net, hi, yogunlasma)[alan]
        hi *= 2
        if hi > 500_000:
            return None
        if abs(halka(net, hi, yogunlasma)[alan] - once) < 1e-6 and not iyi(hi):
            return None
    lo = 0.0
    for _ in range(22):
        mid = (lo + hi) / 2
        if iyi(mid):
            hi = mid
        else:
            lo = mid
    return r2(hi)


def min_butce(net, yogunlasma: bool):
    """Tüm ticari+ücret kalanı. Holding borçlusu kapanmazsa None."""
    return _min_olcu(net, yogunlasma, "uretim_kalan")


def min_araci(net, yogunlasma: bool = False):
    """Yalnız aracı borçlunun ticari+ücret kalanı 0,05 altına inen bütçe."""
    return _min_olcu(net, yogunlasma, "araci")


def _ozet_halka(hs: list[dict]) -> dict:
    return {
        "n": len(hs),
        "araci_med": r2(med([h["araci"] for h in hs])),
        "uretim_med": r2(med([h["uretim_kalan"] for h in hs])),
        "banka_med": r2(med([h["banka"] for h in hs])),
        "holding_med": r2(med([h["holding"] for h in hs])),
        "cekilen_med": r2(med([h["cekilen"] for h in hs])),
        "araci_kapanan": sum(h["araci"] < 0.05 for h in hs),
        "uretim_kapanan": sum(h["uretim_kalan"] < 0.05 for h in hs),
    }


def _min_ozet(vals: list) -> dict:
    sayi = [v for v in vals if v is not None]
    return {
        "n": len(vals),
        "yok": sum(v is None for v in vals),
        "med": None if not sayi else med(sayi),
        "min": None if not sayi else min(sayi),
        "max": None if not sayi else max(sayi),
    }


def main():
    girdi = rev_sok.yukle()
    A = adres()
    g, artis = rev_sok.ag_kur(KUR, LAM, girdi)
    p = Parametreler(holding_odeme_orani=0.5, sart_kaldiraci=True, ucret_gecis_beta=BETA)
    r = calistir(g, p)
    net = optimal_mahsup(g)
    baz = parcala_pro_rata(net)
    bol = halka(net, 1.0e9, False)
    yog = halka(net, 1.0e9, True)
    tam = {
        "artis": r4(artis),
        "baz_sinif": baz,
        "temerrut": int(r["asamalar"]["4_sart_kaldiraci"]["temerrut_sayisi"]),
        "kopru": r2(r["asamalar"]["4_sart_kaldiraci"]["kredi_ihtiyaci"]),
        "kilitli": len(r["teshis"]["kilitli"]),
        "batik": len(r["teshis"]["batik"]),
        "kilitli_ad": list(r["teshis"]["kilitli"]),
        "batik_ad": list(r["teshis"]["batik"]),
        "butce0": halka(net, 0.0, False),
        "bol_butce": bol,
        "yogun_butce": yog,
        "min_araci": min_araci(net, False),
        "min_araci_yogun": min_araci(net, True),
        "min_uretim": min_butce(net, False),
        "min_uretim_yogun": min_butce(net, True),
        "izgara": {},
    }
    for ad, AA in (("on", A["A_on"]), ("uc", A["A_uc"])):
        for olcek, c in (("stok", 1.0), ("akim", 0.25)):
            for th in THETA:
                butce = th * AA * c
                h = halka(net, butce, False)
                y = halka(net, butce, True)
                fug = fungible_banka(net, butce)
                tam["izgara"][f"{ad}|{olcek}|{th}"] = {
                    "butce": r2(butce),
                    "araci": h["araci"],
                    "banka": h["banka"],
                    "holding": h["holding"],
                    "cekilen": h["cekilen"],
                    "atil": h["atil"],
                    "uretim_kalan": h["uretim_kalan"],
                    "yogun_araci": y["araci"],
                    "yogun_cekilen": y["cekilen"],
                    "kayis": fug["kayis"],
                }
    nets = []
    for s in range(rev_sok.TOHUM):
        ken = rev_sok.seyrek_kenar(girdi, 0.25, s)
        if ken is None:
            continue
        gs, _ = rev_sok.ag_kur(KUR, LAM, girdi, ken)
        nets.append(optimal_mahsup(gs))
    bz = [parcala_pro_rata(n) for n in nets]
    seyrek = {
        "n": len(nets),
        "baz_med": {k: r2(med([b[k] for b in bz])) for k in ("ticari", "ucret", "banka", "holding")},
        "min_araci": _min_ozet([min_araci(n, False) for n in nets]),
        "min_araci_yogun": _min_ozet([min_araci(n, True) for n in nets]),
        "min_uretim": _min_ozet([min_butce(n, False) for n in nets]),
        "izgara": {},
    }
    for ad, AA in (("on", A["A_on"]), ("uc", A["A_uc"])):
        for olcek, c in (("stok", 1.0), ("akim", 0.25)):
            for th in THETA:
                butce = th * AA * c
                hs = [halka(n, butce, False) for n in nets]
                ys = [halka(n, butce, True) for n in nets]
                seyrek["izgara"][f"{ad}|{olcek}|{th}"] = {
                    "butce": r2(butce),
                    "halka": _ozet_halka(hs),
                    "yogun": _ozet_halka(ys),
                }
    out = {
        "etiket": "aday: e-fatura eslesmesi ve Sayistay emri olculmedi; halka yercekimi agi vekili",
        "lam": LAM,
        "beta": BETA,
        "kur": KUR,
        "A_on": A["A_on"],
        "A_uc": A["A_uc"],
        "tam": tam,
        "seyrek": seyrek,
        "k5_siki_uygun_pay": 0.0,
        "k5_not": "VADELI_KALICILIK odenmeyen emir bulunamadi; NACE_KAP ilgili taraf tutari yok. Siki okuma uygun pay 0.",
    }
    yaz_json("rant_sonuc.json", out)
    print("rant cekilen", bol["cekilen"], "min_araci", tam["min_araci"], "seyrek", seyrek["min_araci"])


if __name__ == "__main__":
    main()
