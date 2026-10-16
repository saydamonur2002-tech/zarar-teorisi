"""S5 kanal serilerini çeker. Karar SEKTOR_S5_ONKAYIT.md.

Kesim kaybı yoksa aktarım yazılmaz. Mevduat ve net pozisyon çekilmez.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
SON = "16-10-2026"

STOK = [
    ("TP.HPBITABLO6.26", "3", "last", "banka_yp_ticari"),
    ("TP.FDVY16", "5", "last", "firma_yurtici_banka_doviz_kredisi"),
]
AKIM = [
    ("TP.SATIM.USD", "2", "sum", "tcmb_satim_usd"),
    ("TP.SATIM.EUR", "2", "sum", "tcmb_satim_eur"),
    ("TP.SATIM.CHF", "2", "sum", "tcmb_satim_chf"),
    ("TP.SATIM.DEM", "2", "sum", "tcmb_satim_dem"),
]
YEDEK_FREQ = {"3": ["5"], "2": ["1", "5"], "5": []}


def cek(kod: str, freq: str, agg: str) -> dict:
    body = {
        "type": "json", "series": kod, "aggregationTypes": agg, "formulas": "0",
        "startDate": "01-01-1990", "endDate": SON, "frequency": freq,
        "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR",
        "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": False,
        "isRaporSayfasi": False,
    }
    try:
        data = get_json(f"{BASE}/fe", body)
    except Exception as exc:  # noqa: BLE001
        return {"kod": kod, "freq": freq, "durum": "hata", "hata": str(exc)[:200], "gozlem": []}
    key = kod.replace(".", "_")
    ad = (data.get("seriesNames") or {}).get(key)
    rows = []
    for it in data.get("items") or []:
        v = it.get(key)
        if v not in (None, ""):
            rows.append((str(it.get("Tarih")), float(str(v).replace(",", ""))))
    return {"kod": kod, "ad": ad, "freq": freq, "agg": agg, "durum": "var" if rows else "bos",
            "n": len(rows), "gozlem": rows}


def cek_kilit(kod: str, freq: str, agg: str) -> dict:
    denenen = [freq, *YEDEK_FREQ.get(freq, [])]
    son = None
    for f in denenen:
        son = cek(kod, f, agg)
        son["denenen_freq"] = denenen
        if son["durum"] == "var":
            return son
    return son


def ozet(s: dict) -> dict:
    g = s.get("gozlem") or []
    return {
        "kod": s["kod"], "ad": s.get("ad"), "durum": s["durum"], "freq": s.get("freq"),
        "agg": s.get("agg"), "n": s.get("n", 0),
        "ilk": g[0][0] if g else None, "son": g[-1][0] if g else None,
        "son_deger": g[-1][1] if g else None,
        "hata": s.get("hata"),
    }


def main() -> None:
    cekilen = [cek_kilit(*x[:3]) | {"rol": x[3]} for x in STOK + AKIM]
    ham = []
    for s in cekilen:
        for t, v in s.get("gozlem") or []:
            ham.append((s["rol"], s["kod"], s.get("ad"), s["freq"], s["agg"], t, v))
    with (KOK / "sektor_s5_ham.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rol", "kod", "ad", "freq", "agg", "tarih", "deger"])
        w.writerows(ham)
    sonuc = {
        "cekilme": date.today().isoformat(),
        "S5": "belirlenemiyor",
        "neden": "NACE kesiminde özkaynağı aşan döviz kaybı yok. Çekilen stok ve satış kesim etiketi taşımıyor.",
        "mevduat_ve_net": "cekilemedi",
        "seriler": [ozet(s) | {"rol": s["rol"]} for s in cekilen],
    }
    (KOK / "sektor_s5_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for s in sonuc["seriler"]:
        print(s["rol"], s["kod"], s["durum"], "n", s["n"], s["ilk"], s["son"], s["son_deger"], "freq", s["freq"])


if __name__ == "__main__":
    main()
