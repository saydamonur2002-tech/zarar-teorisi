"""Lider ve üst %10 ölçeği. Monte Carlo koşmaz.

Lider, ödeme zincirinde en yüksek mevduatlı sentetik düğümdür (ODEME_ZINCIRI.md).
LIDER_MEVDUAT.md yürütme kasasıdır; bu düğüm değildir.
Üst %10 payları hedef paydır (aday). N ve k kod sabitidir.
"""
from __future__ import annotations

import ast
from pathlib import Path

from ortak import KOK, adres, r4, yaz_json


def _sabit(yol: Path, ad: str):
    agac = ast.parse(yol.read_text(encoding="utf-8"))
    for d in agac.body:
        if isinstance(d, ast.Assign):
            for t in d.targets:
                if isinstance(t, ast.Name) and t.id == ad:
                    return ast.literal_eval(d.value)
    raise SystemExit(ad)


def firma_nakit() -> float:
    for r in __import__("csv").DictReader((KOK / "tek_sistem_kopru_ham.csv").open(encoding="utf-8-sig")):
        if r["donem"] == "2026-Q1" and r["anahtar"] == "F_VF2":
            return float(r["milyar_tl"])
    raise SystemExit("F_VF2")


def main():
    dag = KOK / "odeme_dagilim.py"
    n = int(_sabit(dag, "N_FIRMA"))
    kons = tuple(_sabit(dag, "KONS"))
    k = round(0.10 * n)
    A = adres()
    F = firma_nakit()
    out = {
        "etiket": "kanit: N, k, F_VF2, DIBS paylari. aday: KONS hedef paylari, sentetik lider",
        "N_FIRMA": n,
        "ust_onda_adet": k,
        "konsantrasyon_hedef": list(kons),
        "firma_vf2_2026q1": r4(F),
        "ust_onda_nominal_aday": {str(c): r4(c * F) for c in kons},
        "adres": {"A_on": A["A_on"], "A_uc": A["A_uc"], "A_bant_ust": A["A_bant_ust"]},
        "emme": {"H": A["H"], "genis": A["genis"], "piyasa": A["piyasa"], "paylar": A["paylar"]},
        "kredi_bant": A["c_bant"],
        "hukum": {
            "lider": "ODEME_ZINCIRI.md: en yuksek mevduatli sentetik dugum",
            "ust10": "dagitim mahsup blogu kapatmaz; ust onda iddiasi elenmedi",
            "yurutme_kasasi": "LIDER_MEVDUAT.md ayri nesne",
        },
    }
    yaz_json("olcek_sonuc.json", out)
    print("olcek", n, k, F, A["H"], A["genis"])


if __name__ == "__main__":
    main()
