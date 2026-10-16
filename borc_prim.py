"""Borç/GSYH ve iç tahvil primi. Kurallar BORC_PRIM_ONKAYIT.md.

Tahvil faizi veya genel yönetim borç stoku yoksa denklem kurulmaz.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent


def cek(kod: str, agg: str, freq: str) -> dict:
    body = {
        "type": "json",
        "series": kod,
        "aggregationTypes": agg,
        "formulas": "0",
        "startDate": "01-01-2006",
        "endDate": "16-10-2026",
        "frequency": freq,
        "decimalSeperator": ".",
        "decimal": "4",
        "dateFormat": "0",
        "lang": "TR",
        "yon": "0",
        "sira": "0",
        "ozelFormuller": [],
        "groupSeperator": False,
        "isRaporSayfasi": False,
    }
    try:
        data = get_json(f"{BASE}/fe", body)
    except Exception as exc:  # noqa: BLE001
        return {"kod": kod, "hata": str(exc)[:200], "n": 0}
    key = kod.replace(".", "_")
    ad = (data.get("seriesNames") or {}).get(key)
    vals = []
    for it in data.get("items") or []:
        v = it.get(key)
        if v not in (None, ""):
            vals.append(str(it["Tarih"]))
    return {
        "kod": kod,
        "ad": ad,
        "n": len(vals),
        "ilk": vals[0] if vals else None,
        "son": vals[-1] if vals else None,
    }


def main() -> None:
    seri = {
        "fonlama": cek("TP.APIFON4", "avg", "5"),
        "toplanti_beklenti": cek("TP.PKAUO.S04.C.U", "avg", "5"),
        "ay_sonu_beklenti_ikame_degil": cek("TP.PKAUO.S04.A.U", "avg", "5"),
        "enf_beklenti_24ay": cek("TP.PKAUO.S01.F.U", "avg", "5"),
        "usd": cek("TP.DK.USD.A.YTL", "last", "5"),
        "gsyh": cek("TP.GSYIH20.BY.B1GQ", "sum", "6"),
        "f0_yukumluluk_borc_stoku_degil": cek("TP.FINHESTNKS13.ZP45", "last", "6"),
        "f3_senet_borc_stoku_degil": cek("TP.FINHESTNKS13.ZP31", "last", "6"),
    }
    sonuc = {
        "cekilme": date.today().isoformat(),
        "onkait": "BORC_PRIM_ONKAYIT.md",
        "tahvil_10y": None,
        "borc_stoku_genel_yonetim": None,
        "vix": None,
        "abd_10y": None,
        "seri": seri,
        "denklem": "kurulmadi",
        "neden": "10 yıllık gösterge tahvil faizi ve genel yönetim borç stoku çekilemedi. Prim ve borç/GSYH yazılmadı. F.0 ve F.3 yerine konmadı. Toplantı beklentisi n<36.",
        "H1": "belirlenemiyor",
        "H2": "belirlenemiyor",
        "H3": "belirlenemiyor",
        "H4": "belirlenemiyor",
        "katsayi": None,
    }
    (KOK / "borc_prim_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: sonuc[k] for k in ("H1", "neden")}, ensure_ascii=False))
    for k, v in seri.items():
        print(k, v.get("n"), v.get("ilk"), v.get("son"))


if __name__ == "__main__":
    main()
