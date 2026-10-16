"""NDV, net altın ve TL–DTH artığı. Kurallar NDV_ALTIN_ONKAYIT.md.

Doğrulanmayan nesne kurulmaz. Katsayı yazılmaz.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent


def cek(kod: str, agg: str = "last", freq: str = "5") -> dict:
    body = {
        "type": "json", "series": kod, "aggregationTypes": agg, "formulas": "0",
        "startDate": "01-01-2002", "endDate": "16-10-2026", "frequency": freq,
        "decimalSeperator": ".", "decimal": "2", "dateFormat": "0", "lang": "TR",
        "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": False,
        "isRaporSayfasi": False,
    }
    try:
        data = get_json(f"{BASE}/fe", body)
    except Exception as exc:  # noqa: BLE001
        return {"kod": kod, "durum": "bulunamadi", "hata": str(exc)[:160], "n": 0}
    key = kod.replace(".", "_")
    ad = (data.get("seriesNames") or {}).get(key)
    if not ad:
        return {"kod": kod, "durum": "bulunamadi", "n": 0}
    vals = [str(it["Tarih"]) for it in data.get("items") or [] if it.get(key) not in (None, "")]
    return {"kod": kod, "ad": ad, "durum": "dogrulandi", "n": len(vals),
            "ilk": vals[0] if vals else None, "son": vals[-1] if vals else None}


def main() -> None:
    dogru = {
        "brut_rezerv_ndv_degil": cek("TP.AB.TOPLAM"),
        "altin_milyon_usd_miktar_degil": cek("TP.AB.C1"),
        "doviz_rezerv_milyon_usd": cek("TP.AB.C2"),
        "yabanci_aktif": cek("TP.AB.A02"),
        "yabanci_pasif": cek("TP.AB.A10"),
        "zorunlu_karsilik_bloke": cek("TP.AB.A19"),
        "acik_piyasa": cek("TP.AB.A24"),
        "tl_mevduat_faizi_3ay": cek("TP.TRY.MT02", "avg"),
        "usd_mevduat_faizi_3ay_dth_degil": cek("TP.USD.MT02", "avg"),
        "pka_dolar_12ay": cek("TP.PKAUO.S05.C.U", "avg"),
        "pka_enf_24ay": cek("TP.PKAUO.S01.F.U", "avg"),
        "usdtry": cek("TP.DK.USD.A.YTL"),
        "mevduat_toplam_yeni": cek("TP.HPBITABLO2.1"),
        "tl_mevduat_yeni": cek("TP.HPBITABLO2.3"),
        "yp_mevduat_yeni": cek("TP.HPBITABLO2.6"),
        "altin_mevduat_usd_yeni": cek("TP.HPBITABLO4.7"),
        "tl_mevduat_arsiv": cek("TP.MEVDUAT.I001"),
        "yp_mevduat_arsiv": cek("TP.MEVDUAT.I067"),
        "kiymetli_maden_arsiv": cek("TP.MEVDUAT.I0981"),
        "mevduat_toplam_arsiv": cek("TP.MEVDUAT.I114"),
        "kkm_tl_stok": cek("TP.KKM.K4"),
    }
    yok = ["swap_yukumlulugu", "altin_swap_ton", "altin_ons_fiyati", "altin_mevduat_gram",
           "dth_faizi_sepet", "ndv_swap_duzeltmeli", "niv_repo_tahvil_kkm"]
    sonuc = {
        "cekilme": date.today().isoformat(),
        "onkait": "NDV_ALTIN_ONKAYIT.md",
        "dogrulanan": dogru,
        "bulunamayan": yok,
        "swap_duzeltmesi": "yapilmadi",
        "swap_not": "TP.AB.A02 yabancı aktif ve TP.AB.A10 yabancı pasif duruyor. Ayrı swap stoku ve altın swap tonu yok. Brüt TP.AB.TOPLAM NDV yerine konmadı. Zorunlu karşılık blokesi TP.AB.A19 ayrı duruyor; NDV formülüne sokulmadı.",
        "artik": "kurulmadi",
        "kkm_teblig": "bu turda KKM tebliği indirilmedi. 21 Aralık 2021 tarihli açılan Resmî Gazete maddesi özel tüketim vergisi tebliğidir. Tarih oradan alınmadı.",
        "H1": "belirlenemiyor", "H2": "belirlenemiyor", "H3": "belirlenemiyor",
        "H4": "belirlenemiyor", "H5": "belirlenemiyor", "H6": "belirlenemiyor",
        "katsayi": None, "vif": None,
    }
    (KOK / "ndv_altin_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for k, v in dogru.items():
        print(k, v.get("durum"), v.get("n"), v.get("ilk"), v.get("son"))


if __name__ == "__main__":
    main()
