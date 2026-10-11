"""Varsayim esikleri. Esik kapiyi acmaz.

Gecis 0, 1/3, 1. Vade 30, 90, 180. Odenmeyen emir esiksiz.
2,54 = 7,62 x 1/3. 2,77 = 8,3 x 1/3. 2,5 RAPOR yaklasik. Uc ayri. Esitlenmez.
olculdu olmaz.
"""

from __future__ import annotations

import csv
import json
from fractions import Fraction
from pathlib import Path

KOK = Path(__file__).resolve().parent
GECIS_ESIK = (Fraction(0), Fraction(1, 3), Fraction(1))
VADE_ESIK = (30, 90, 180)
IZINLI_DURUM = {"varsayim", "kosullu", "ayrilmadi"}
NOT_13 = (
    " 2,54 = 7,62 x 1/3, bu dosya. 2,77 = 8,3 x 1/3, RAPOR orani, RAPOR yazmadi."
    " 2,5 RAPOR yaklasik cumlesi, hesap degil. Uc sayi ayri, esitlenmez, biri digerini duzeltmez."
)


def _json(p: str) -> dict:
    return json.loads((KOK / p).read_text(encoding="utf-8"))


def girdiler() -> dict:
    ta = _json("tavan_akis_sonuc.json")
    r25 = next(r for r in ta["satirlar"] if r["yil"] == "2025")
    tk = _json("tek_sistem_kopru_sonuc.json")
    ak = next(r for r in tk["mutabakat"] if r["blok"] == "akim" and r["donem"] == "2025" and r["kalem"] == "Net akis ticari")
    vk_rows = list(csv.DictReader((KOK / "vadeli_kalicilik.csv").open(encoding="utf-8-sig")))
    son = vk_rows[-1] if vk_rows else {}
    return {
        "itis_2025_yuzde": r25["oran_akim"],
        "tavan_akis_tavan_dolu": any(r["tavan"] not in (None, "") for r in ta["satirlar"]),
        "bddk_net_akis_2025": ak["tek_sistem_milyar"],
        "f4_akim_2025": ak["evds_milyar"],
        "bosluk_2025": round(ak["tek_sistem_milyar"] - ak["evds_milyar"], 1),
        "vade_kirilim": son.get("vade_kirilim", ""),
        "vade_donem": son.get("donem", ""),
    }


def _esik_str(fr: Fraction) -> str:
    return str(fr.numerator) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"


def satirlar(g: dict) -> list[dict]:
    R = []
    itis = g["itis_2025_yuzde"]
    for e in GECIS_ESIK:
        R.append({
            "kapi": "gecis", "esik": _esik_str(e), "girdi": itis,
            "cikti": round(itis * float(e), 2), "birim": "puan", "durum": "varsayim",
            "not": "itis 2025 = F.4 islem akimi / GSYH. Gecis bulunamadi." + (NOT_13 if e == Fraction(1, 3) else ""),
        })
    for v in VADE_ESIK:
        R.append({
            "kapi": "vade_gunu", "esik": v, "girdi": None,
            "cikti": "asilirsa uzar; asilmazsa uzamaz", "birim": "gun", "durum": "kosullu",
            "not": f"MY vade kirilimi '{g['vade_kirilim']}', ortalama gun bos ({g['vade_donem']}). Olcum degil.",
        })
    R.append({"kapi": "odenmeyen_emir", "esik": None, "girdi": None, "cikti": None,
              "birim": "milyar TL", "durum": "kosullu", "not": "Olcu yok. Esik konmaz."})
    R.append({"kapi": "bddk_akim", "esik": None, "girdi": g["bddk_net_akis_2025"],
              "cikti": g["bosluk_2025"], "birim": "milyar TL", "durum": "ayrilmadi",
              "not": f"{g['bddk_net_akis_2025']} - {g['f4_akim_2025']} = {g['bosluk_2025']}. Kur ve kapsam ayrilmadi."})
    return R


def etiketler(R, g):
    durumlar = {r["durum"] for r in R}
    hv = "ihlal" if ("olculdu" in durumlar or not durumlar <= IZINLI_DURUM) else "temiz"
    hv2 = "siser" if g["tavan_akis_tavan_dolu"] else "ayri"
    return {"H-V": hv, "H-V2": hv2,
            "H-V2_not": "2,54 sonuc sutununa gecmedi; 2,5 ve 2,77 ile esitlenmedi" if hv2 == "ayri" else "tavan dolu"}


def md(R, g, et) -> str:
    return "\n".join([
        "# Varsayim esikleri", "",
        "Kilitli uc kapi. Esik kapiyi acmaz. Konan esik `varsayim`.", "",
        "## Gecis", "",
        "| Esik | Itis | Tavan | Durum |", "| --- | ---: | ---: | --- |",
        "| 0 | 7,62 | 0,00 | varsayim |",
        "| 1/3 | 7,62 | 2,54 | varsayim |",
        "| 1 | 7,62 | 7,62 | varsayim |", "",
        "Uc sayi ayri. Esitlenmez. Biri digerini duzeltmez.", "",
        "| Sayi | Ne |", "| --- | --- |",
        "| 2,54 | 7,62 x 1/3. Bu dosya. Itis islem akimi. |",
        "| 2,77 | 8,3 x 1/3. RAPOR orani. RAPOR bunu yazmadi. |",
        "| 2,5 | RAPOR yaklasik cumlesi. Hesap degil. Referans. |", "",
        "## Vade", "",
        "| Esik | Cikti | Durum |", "| --- | --- | --- |",
        "| 30 | asilirsa uzar; asilmazsa uzamaz | kosullu |",
        "| 90 | asilirsa uzar; asilmazsa uzamaz | kosullu |",
        "| 180 | asilirsa uzar; asilmazsa uzamaz | kosullu |", "",
        "## Yanlislayicilar", "",
        f"- H-V: `{et['H-V']}`. olculdu yok.",
        f"- H-V2: `{et['H-V2']}`. {et['H-V2_not']}.",
        "",
    ])


def main() -> None:
    g = girdiler()
    R = satirlar(g)
    et = etiketler(R, g)
    alan = ["kapi", "esik", "girdi", "cikti", "birim", "durum", "not"]
    with (KOK / "varsayim_esik.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=alan)
        w.writeheader()
        for r in R:
            w.writerow({a: ("" if r[a] is None else r[a]) for a in alan})
    (KOK / "varsayim_esik_sonuc.json").write_text(
        json.dumps({"uc_sayi": {"2.54": "7.62x1/3", "2.77": "8.3x1/3", "2.5": "RAPOR yaklasik"},
                    "esitlenmez": True, "satirlar": R, **et}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    (KOK / "VARSAYIM_ESIK.md").write_text(md(R, g, et), encoding="utf-8")
    print(et)


if __name__ == "__main__":
    main()
