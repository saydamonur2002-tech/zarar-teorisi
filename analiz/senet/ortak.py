"""Taslak yardımcıları. Karar dosyalarına yazmaz.

Python dosya adında ve def/class adında «senet» geçmez: test_bes_adim.kontrol_senet
kökteki model kilidini (modellenmedi, kod yok) böyle tarar. Bu klasör o kilidin
dışında bir taslaktır; adim4.csv satırını doldurmaz.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("ZT_AG", "cevrimdisi")
os.environ.setdefault("MPLBACKEND", "Agg")

KOK = Path(__file__).resolve().parents[2]
CIKTI = Path(__file__).resolve().parent
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))
if str(KOK / "mahsup") not in sys.path:
    sys.path.insert(0, str(KOK / "mahsup"))

LAM = 1.0357
BETA = 0.0439
KUR = 19.29


def yaz_json(ad: str, obj) -> Path:
    p = CIKTI / ad
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return p


def yaz_csv(ad: str, alan: list[str], satirlar: list[dict]) -> Path:
    p = CIKTI / ad
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=alan, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for s in satirlar:
            w.writerow({k: s.get(k, "") for k in alan})
    return p


def med(xs: list):
    s = sorted(xs)
    return s[len(s) // 2]


def r4(x) -> float:
    return round(float(x), 4)


def r2(x) -> float:
    return round(float(x), 2)


def oku_json(ad: str) -> dict:
    return json.loads((KOK / ad).read_text(encoding="utf-8"))


def adres() -> dict:
    c = oku_json("rev_adim4_sonuc.json")
    cift, pay, bant = c["cift_sayim"], c["dibs_elinde_tutan"]["paylar_q1"], c["kredi_katsayisi"]["bant"]
    piyasa = float(pay["toplam_milyar"])
    h_pay = float(pay["S14"]) + float(pay["S11"])
    genis_pay = h_pay + float(pay["S1234"]) + float(pay["S128"]) + float(pay["S129"])
    gsyh = {}
    for r in csv.DictReader((KOK / "gsyh_pay.csv").open(encoding="utf-8-sig")):
        gsyh[int(r["yil"])] = float(r["gsyh_milyar_TL"])
    return {
        "A_on": float(cift["onerilen"]),
        "A_uc": float(cift["adres_toplam_eski"]),
        "A_bant_ust": float(cift["adres_toplam_yeni_bandi"][1]),
        "hane_vadeli": float(cift["H_VF2_ZP8"]),
        "yp_gercek": float(cift["YP_gercek_kisi"]),
        "c_bant": [float(bant[0]), float(bant[1])],
        "piyasa": piyasa,
        "H": r4(h_pay * piyasa),
        "genis": r4(genis_pay * piyasa),
        "paylar": {k: pay[k] for k in ("S11", "S14", "S121", "S122", "S1234", "S128", "S129", "S13", "S2")},
        "gsyh_2026": gsyh[2026],
        "gsyh": {str(y): gsyh[y] for y in range(2026, 2032)},
    }


def usd_ay() -> dict[str, float]:
    out = {}
    for r in csv.DictReader((KOK / "faiz_kur_ham.csv").open(encoding="utf-8-sig")):
        if r["usd"]:
            out[r["donem"]] = float(r["usd"])
    return out


def yp_stok() -> list[dict]:
    rows = []
    for r in csv.DictReader((KOK / "tek_sistem_kopru_ham.csv").open(encoding="utf-8-sig")):
        if r["anahtar"] == "gercek_kisi_YP" and r["milyar_tl"]:
            rows.append({"donem": r["donem"], "milyar_tl": float(r["milyar_tl"]), "seri": r["seri"]})
    return rows
