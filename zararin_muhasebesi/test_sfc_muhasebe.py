"""Muhasebe ve ön kayıt. Çalıştır: python3 zararin_muhasebesi/test_sfc_muhasebe.py"""
import json
import sys
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent
sys.path.insert(0, str(KOK))
import sfc_model as M  # noqa: E402

TOL = 1e-6
ANAHTAR = ("pi_2029", "nr_2027q4", "nr_2028q4", "nr_2029", "borc_gsyh_2029", "gsyh_endeks_2029", "E_2029")
S0S7 = (
    "S0 Baz", "S2 Reel değerlenme sürer", "S1 Dış şok", "S4 Şok + erteleme",
    "S5 Şok + erteleme → tanıma", "S3 Şok + Yeldan seti", "S6 Sınır piyasa (merkez)",
    "S7 Sınır piyasa (sert)",
)


def ozet(o):
    y = M.real_gdp(o)
    return {
        "pi_2029": o["pi"][-1],
        "nr_2027q4": o["NR"][5],
        "nr_2028q4": o["NR"][9],
        "nr_2029": o["NR"][-1],
        "borc_gsyh_2029": o["debt"][-1],
        "gsyh_endeks_2029": float(y[-1] / y[0] * 100),
        "E_2029": o["E"][-1],
    }


def main() -> int:
    hata = []
    ac = M.acilis_bilanco()
    if ac["finansal_satir_mutlak_max"] >= 1e-6:
        hata.append(f"finansal satır {ac['finansal_satir_mutlak_max']}")
    if abs(ac["nw_eksi_pk"]) >= 1e-6:
        hata.append(f"nw-pK {ac['nw_eksi_pk']}")
    if abs(ac["banka_ozkaynak"] - M.BANKA_OZKAYNAK_TN) >= 1e-6:
        hata.append(f"banka özkaynak {ac['banka_ozkaynak']}")
    if M.TS_NPL_COEF != 0.5 or M.BANKA_OZKAYNAK_TN != 4.65:
        hata.append("katsayı sessizce değişti")
    adr = M.adres_stoklari()
    if adr is None or abs(adr["toplam_milyar"] - 19361.9) > 1e-9 or abs(M.TS_HAVUZ_MILYAR - adr["toplam_milyar"]) > 1e-9:
        hata.append(f"adres {adr}")
    V = json.loads((KOK / "veriler.json").read_text(encoding="utf-8"))
    for k in ("swap_haric_net_rezerv", "yabanci_hisse", "bist100"):
        if "[DOĞRULANMADI]" not in V["dogrulama"][k]["etiket"]:
            hata.append(f"haber etiketi {k}")
    if V["dogrulama"]["tufe_yillik"]["etiket"] != "kanıt":
        hata.append("tüfe etiketi")
    sur = M.kod_surumu()
    if not sur["sfc_sha256"] or len(sur["sfc_sha256"]) != 64:
        hata.append("kod sürümü yok")
    once = json.loads((KOK / "once_ozet.json").read_text(encoding="utf-8"))
    sc = M.all_scenarios()
    if sc["S4z Şok + erteleme, zombi kapalı"]["gam_z"] != 0.0 or sc["S5z Şok + erteleme → tanıma, zombi kapalı"]["gam_z"] != 0.0:
        hata.append("zombi varyantı kapalı değil")
    if sc["S4 Şok + erteleme"]["gam_z"] != M.BASE["gam_z"]:
        hata.append("S4 gam_z değişti")
    kosu = {}
    for ad, p in sc.items():
        o = M.simulate(p)
        c = o["_checks"]
        for k in ("hidden_max", "SI_max"):
            if c[k] >= 1e-8:
                hata.append(f"{ad} {k} {c[k]}")
        if abs(c["balance"]) >= 1e-8:
            hata.append(f"{ad} balance {c['balance']}")
        kosu[ad] = ozet(o)
        if ad in S0S7:
            for k in ANAHTAR:
                if abs(kosu[ad][k] - once["senaryo"][ad][k]) >= TOL:
                    hata.append(f"SAPMA {ad} {k} {kosu[ad][k]} {once['senaryo'][ad][k]}")
    sb = __import__("copy").deepcopy(M.BASE)
    sb["shock"] = M.shock_external
    for bg_name, bg in (("Baz", M.BASE), ("Dış şok", sb)):
        paket = {"paketsiz": M.simulate(__import__("copy").deepcopy(bg))}
        for k, ad in enumerate(M.TS_NAMES):
            paket[ad] = M.simulate(M.tek_sistem(__import__("copy").deepcopy(bg), k))
        for ad, o in paket.items():
            anahtar = f"{bg_name} · {ad if ad != 'paketsiz' else 'paketsiz'}"
            simdi = ozet(o)
            for k in ANAHTAR:
                if abs(simdi[k] - once["tek_sistem"][anahtar][k]) >= TOL:
                    hata.append(f"SAPMA TS {anahtar} {k}")
    y4 = kosu["S4 Şok + erteleme"]["gsyh_endeks_2029"]
    y4z = kosu["S4z Şok + erteleme, zombi kapalı"]["gsyh_endeks_2029"]
    if not (y4z > y4):
        hata.append(f"SAPMA S4z endeks {y4z} <= S4 {y4}")
    o4 = M.simulate(sc["S4 Şok + erteleme"])
    o4z = M.simulate(sc["S4z Şok + erteleme, zombi kapalı"])
    o5 = M.simulate(sc["S5 Şok + erteleme → tanıma"])
    o5z = M.simulate(sc["S5z Şok + erteleme → tanıma, zombi kapalı"])
    dy = float(np.sum(M.real_gdp(o5) - M.real_gdp(o4)) / 4 / 84)
    dyz = float(np.sum(M.real_gdp(o5z) - M.real_gdp(o4z)) / 4 / 84)
    if not (dyz < dy):
        hata.append(f"SAPMA tanıma avantajı kapalı {dyz} >= açık {dy}")
    if hata:
        print("KALDI")
        for h in hata:
            print(" -", h)
        return 1
    print("GECTI", len(sc), "senaryo; S4z endeks", round(y4z, 4), "S4", round(y4, 4), "dy", round(dy, 4), "dyz", round(dyz, 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
