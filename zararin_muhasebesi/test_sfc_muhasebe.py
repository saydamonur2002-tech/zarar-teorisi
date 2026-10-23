"""Muhasebe ve ön kayıt. Çalıştır: python3 zararin_muhasebesi/test_sfc_muhasebe.py"""
import json
import sys
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent
sys.path.insert(0, str(KOK))
import sfc_model as M  # noqa: E402


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
    if M.TS_NPL_COEF != 0.5:
        hata.append("TS_NPL_COEF değişti")
    if abs(M.BANKA_OZKAYNAK_TN - 4.565252392) > 1e-9:
        hata.append(f"banka özkaynak sabiti {M.BANKA_OZKAYNAK_TN}")
    adr = M.adres_stoklari()
    if adr is None or abs(adr["toplam_milyar"] - 19361.9) > 1e-9 or abs(M.TS_HAVUZ_MILYAR - adr["toplam_milyar"]) > 1e-9:
        hata.append(f"adres {adr}")
    V = json.loads((KOK / "veriler.json").read_text(encoding="utf-8"))
    for k, d in V["dogrulama"].items():
        for alan in ("etiket", "seri", "tarih", "kaynak"):
            if alan not in d:
                hata.append(f"dogrulama alan {k}.{alan}")
    kanit = ("tufe_yillik", "usd_try", "politika_faizi", "brut_rezerv", "kv_dis_borc_kalan_vade", "reel_efektif_kur", "yabanci_hisse", "banka_ozkaynak_tn")
    dogrulanmadi = ("swap_haric_net_rezerv", "emek_payi", "buyume_yillik", "yabanci_takas_payi", "bist100")
    for k in kanit:
        if V["dogrulama"][k]["etiket"] != "kanıt":
            hata.append(f"kanıt etiketi {k}")
    for k in dogrulanmadi:
        if "[DOĞRULANMADI]" not in V["dogrulama"][k]["etiket"]:
            hata.append(f"doğrulanmadı etiketi {k}")
    if V["degerler"]["swap_haric_net_rezerv"] != 39.34 or V["degerler"]["bist100"] != 11220.37:
        hata.append("doğrulanmayan sayı değişti")
    sur = M.kod_surumu()
    if not sur["sfc_sha256"] or len(sur["sfc_sha256"]) != 64:
        hata.append("kod sürümü yok")
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
    sb = __import__("copy").deepcopy(M.BASE)
    sb["shock"] = M.shock_external
    for bg in (M.BASE, sb):
        M.simulate(__import__("copy").deepcopy(bg))
        for k in range(len(M.TS_NAMES)):
            o = M.simulate(M.tek_sistem(__import__("copy").deepcopy(bg), k))
            c = o["_checks"]
            if c["hidden_max"] >= 1e-8 or c["SI_max"] >= 1e-8 or abs(c["balance"]) >= 1e-8:
                hata.append(f"tek sistem muhasebe {c}")
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
