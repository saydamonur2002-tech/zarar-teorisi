"""Kalan mevduat payi: VF.2 icinde merkezi yonetim disi sektorlerin payi.

Skor paydasi H+F+GY. Butun payda (H+F+GY+PFK+ROW) brut kapidir; PFK kalan sayilmaz.
Konsolide olmayan EVDS; konsolide 71011 kullanilmaz. Yuzde 70 esitlik degil, alt sinir.
Akis, stok tavani ve MY sicramasi bu teste girmez. Birim milyar TL, donem sonu.
Cikti: kalan_mevduat.csv, kalan_mevduat_sonuc.json, KALAN_MEVDUAT.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
DONEMLER = ("2025-Q2", "2025-Q3", "2026-Q1")
URL = "https://evds3.tcmb.gov.tr/tumSeriler"
SEKTOR = {"H": "14", "F": "11", "GY": "13", "MY": "1311", "PFK": "12T", "ROW": "2"}
EK = {"HHKAOK": "15", "S12": "12", "S1": "1"}
KIMDEN_KIME = {"2026-Q1": {"H": 15361.0, "F": 7195.0}}
ESIK_70 = 0.70
BIRLIKTE_TOL = 0.10


def _fetch(series: list[str]) -> dict[str, dict[str, float]]:
    body = {"type": "json", "series": "-".join(series), "aggregationTypes": "-".join("last" for _ in series),
            "formulas": "-".join("0" for _ in series), "startDate": "01-04-2025", "endDate": "10-10-2026", "frequency": "6",
            "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR", "yon": "0", "sira": "0",
            "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False}
    out: dict[str, dict[str, float]] = {}
    for it in get_json(f"{BASE}/fe", body)["items"]:
        for s in series:
            v = it.get(s.replace(".", "_"))
            if v not in (None, ""):
                out.setdefault(str(it["Tarih"]), {})[s] = float(str(v).replace(",", "")) / 1e6
    return out


def seri(kod: str, zp: int) -> str:
    return f"TP.FINHESTNKS{kod}.ZP{zp}"


def cek() -> dict:
    kodlar = list(SEKTOR.values()) + list(EK.values())
    q = _fetch([seri(k, z) for k in kodlar for z in (5, 7, 8)])
    veri = {}
    for d in DONEMLER:
        row = {}
        for s, k in {**SEKTOR, **EK}.items():
            row[s] = {"vf2": q.get(d, {}).get(seri(k, 5)), "vadesiz": q.get(d, {}).get(seri(k, 7)), "vadeli": q.get(d, {}).get(seri(k, 8))}
        veri[d] = row
    return veri


def r1(x):
    return None if x is None else round(x, 1)


def r3(x):
    return None if x is None else round(x, 3)


def y70(kalan) -> str:
    if kalan is None:
        return ""
    return "70in_ustunde" if kalan >= ESIK_70 else "70in_altinda"


def paylar(veri: dict) -> tuple[list[dict], dict]:
    rows, ozet = [], {}
    for d, v in veri.items():
        if any(v[s]["vf2"] is None for s in SEKTOR):
            ozet[d] = {"payda": "kurulamadi", "eksik": [s for s in SEKTOR if v[s]["vf2"] is None]}
            continue
        butun = sum(v[s]["vf2"] for s in ("H", "F", "GY", "PFK", "ROW"))
        hfg = sum(v[s]["vf2"] for s in ("H", "F", "GY"))
        my = v["MY"]["vf2"]
        for s in SEKTOR:
            x = v[s]
            rows.append({"donem": d, "sektor": s, "vf2_milyar": r1(x["vf2"]), "vadesiz": r1(x["vadesiz"]), "vadeli": r1(x["vadeli"]),
                         "pay_butun": r3(x["vf2"] / butun), "pay_hfg": r3(x["vf2"] / hfg) if s in ("H", "F", "GY", "MY") else None,
                         "seri": f"{seri(SEKTOR[s], 5)} | {seri(SEKTOR[s], 7)} | {seri(SEKTOR[s], 8)}",
                         "kaynak_url": f"{URL}/bie_finhestnks{SEKTOR[s].lower()}"})
        kalan_b, kalan_h = 1 - my / butun, 1 - my / hfg
        ozet[d] = {
            "payda_butun": r1(butun), "payda_hfg": r1(hfg), "my": r1(my),
            "pay_my_butun": r3(my / butun), "pay_my_hfg": r3(my / hfg),
            "kalan_butun": r3(kalan_b), "kalan_hfg": r3(kalan_h),
            "yuzde70": y70(kalan_h),
            "yuzde70_not": "esitlik degil; skor HFG; butun payda brut, skor degil",
            "H_pay_hfg": r3(v["H"]["vf2"] / hfg), "F_pay_hfg": r3(v["F"]["vf2"] / hfg),
            "GY_disi_MY_pay_hfg": r3((v["GY"]["vf2"] - my) / hfg),
            "payda_disi": {"HHKAOK": r1(v["HHKAOK"]["vf2"]), "diger_finansal_S12_eksi_PFK": r1(v["S12"]["vf2"] - v["PFK"]["vf2"]),
                           "S1_toplam_ekonomi": r1(v["S1"]["vf2"])},
            "cift_sayim_notu": "PFK VF.2 bankalararasi ve kendi icini tutar; butun payda brut, skor degil.",
            "kimden_kime_banka_bacagi": KIMDEN_KIME.get(d, {}),
        }
    return rows, ozet


def hipotez(veri: dict, ozet: dict) -> dict:
    hp = "olculdu" if all(isinstance(o.get("kalan_hfg"), float) for o in ozet.values()) else "test_edilemez"
    q2, q3 = veri["2025-Q2"], veri["2025-Q3"]

    def oran(s):
        a, b = q2[s]["vadeli"], q3[s]["vadeli"]
        return None if (a in (None, 0) or b is None) else (b - a) / a

    o = {s: oran(s) for s in ("MY", "H", "F", "GY", "PFK", "ROW")}
    birlikte = [s for s in ("H", "F") if o[s] is not None and o["MY"] is not None and abs(o[s] - o["MY"]) <= BIRLIKTE_TOL]
    hp2 = "birlikte" if birlikte else "ayri"
    return {
        "H-P": hp,
        "H-P_not": "Skor H+F+GY paydasinda MY disi pay. Butun paydadaki kalan skor degil." if hp == "olculdu" else "Payda kurulamadi.",
        "H-P2": hp2,
        "H-P2_not": ("2025-Q2->Q3 vadeli: " + ", ".join(f"{s} {o[s]:+.1%}" for s in o if o[s] is not None)
                     + f". Esik +-{BIRLIKTE_TOL:.0%}. " + ("Birlikte: " + ", ".join(birlikte) + ". Birlikte ayni neden degil."
                                                          if birlikte else "H ve F vadelisi MY ile ayni oranda degil.")),
        "vadeli_oransal_degisim_Q2_Q3": {s: r3(x) for s, x in o.items()},
        "vade_dilimi": "ayrilmadi; kalicilik cumlesi yok; H-K1 kapali",
    }


def rapor(ozet: dict, hip: dict) -> str:
    s = ["# Kalan mevduat payi", "",
         "Kalan = VF.2 - merkezi yonetim. Skor paydasi H+F+GY. Butun payda brut kapi, skor degil.",
         "Yuzde 70 esitlik degil. 70in_ustunde, alt sinirin ustu demektir.", "",
         "## Pay tablosu", "",
         "| Donem | Payda butun (brut) | Payda HFG (skor) | MY | MY/HFG | Kalan/HFG | %70 |",
         "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for d, o in ozet.items():
        if "payda_hfg" not in o:
            continue
        s.append(f"| {d} | {o['payda_butun']:,.1f} | {o['payda_hfg']:,.1f} | {o['my']:,.1f} | {o['pay_my_hfg']:.1%} | {o['kalan_hfg']:.1%} | {o['yuzde70']} |")
    s += ["", "## Yanlislayicilar", "", f"- **H-P:** `{hip['H-P']}`. {hip['H-P_not']}",
          f"- **H-P2:** `{hip['H-P2']}`. {hip['H-P2_not']}", "- Odenmeyen emir yok. H-K1 kapali.", ""]
    return "\n".join(s)


def main() -> None:
    veri = cek()
    rows, ozet = paylar(veri)
    hip = hipotez(veri, ozet)
    cols = ["donem", "sektor", "vf2_milyar", "vadesiz", "vadeli", "pay_butun", "pay_hfg", "seri", "kaynak_url"]
    with open(KOK / "kalan_mevduat.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})
    (KOK / "kalan_mevduat_sonuc.json").write_text(
        json.dumps({"birim": "milyar TL, donem sonu", "skor_payda": "H+F+GY", "butun_payda": "brut kapi, skor degil",
                    "ozet": ozet, "hipotez": hip}, ensure_ascii=False, indent=2), encoding="utf-8")
    (KOK / "KALAN_MEVDUAT.md").write_text(rapor(ozet, hip), encoding="utf-8")
    print(json.dumps({"H-P": hip["H-P"], "H-P2": hip["H-P2"], "yuzde70": {d: o.get("yuzde70") for d, o in ozet.items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
