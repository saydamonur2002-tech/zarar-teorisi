"""Açık kaynak kalibrasyon köprüsü (EVDS / depo xls / bütçe ham).

Senaryo parametrelerine giden taban girdileri mümkün olduğunca ölçüme bağlar.
Çalıştır: python3 acik_veri_kopru.py
Çıktı: acik_veri_ozet.json, acik_veri_ham.csv, ACIK_VERI_KOPRU.md
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from evds_cek import BASE, get_json
from hane_alt import ASGARI

KOK = Path(__file__).resolve().parent
OZET = KOK / "acik_veri_ozet.json"
HAM = KOK / "acik_veri_ham.csv"
DIS = KOK / "dis_veri" / "bekar_yasam.json"
CACHE = KOK / "acik_veri_evds_cache.json"

# BDDK tablo 6 (EVDS bie_hpbitablo6), bin TL
S_KART = "TP.HPBITABLO6.16"  # Bireysel kredi kartları
S_TUKETICI = "TP.HPBITABLO6.2"  # Tüketici kredileri toplam
S_TAKIP = "TP.HPBITABLO2.38"  # Takipteki alacaklar (bin TL)
S_KREDILER = "TP.HPBITABLO6.1"  # Yurt içi yerleşikler krediler üst? — 6.2 alt küme
S_TUFE = "TP.FG.J0"  # TÜFE genel endeks (2003=100), aylık


@dataclass
class Olcum:
    deger: float | None
    durum: str  # olculdu | varsayim | bulunamadi
    seri: str = ""
    tarih: str = ""
    not_: str = ""


def _fe(series: list[str], freq: str, start: str, end: str, agg: str = "last") -> dict[str, dict[str, float]]:
    body = {
        "type": "json",
        "series": "-".join(series),
        "aggregationTypes": "-".join(agg for _ in series),
        "formulas": "-".join("0" for _ in series),
        "startDate": start,
        "endDate": end,
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
    data = get_json(f"{BASE}/fe", body)
    out: dict[str, dict[str, float]] = {}
    for it in data["items"]:
        t = str(it["Tarih"])
        for s in series:
            v = it.get(s.replace(".", "_"))
            if v not in (None, ""):
                out.setdefault(t, {})[s] = float(str(v).replace(",", ""))
    return out


def _parse_tarih(t: str) -> datetime:
    parts = t.split("-")
    if len(parts) == 2:
        return datetime(int(parts[0]), int(parts[1]), 1)
    a, b, c = parts
    if len(a) == 4:
        return datetime(int(a), int(b), int(c))
    return datetime(int(c), int(b), int(a))


def _seri_zaman(seri: str, start="01-01-2024", end="07-10-2026") -> list[tuple[datetime, float]]:
    ham = _fe([seri], "2", start, end)
    rows = [(_parse_tarih(t), v[seri]) for t, v in ham.items()]
    rows.sort()
    return rows


def buyume_13_ay(seri: str, ref: datetime | None = None) -> Olcum:
    """BDDK haftalık stok: referans tarihe en yakın gözlem / ~13 ay önceki gözlem."""
    ref = ref or datetime(2026, 9, 25)
    rows = _seri_zaman(seri)
    if len(rows) < 2:
        return Olcum(None, "bulunamadi", seri, not_="EVDS gözlem yetersiz")
    cur = max((d, v) for d, v in rows if d <= ref)
    hedef = ref - timedelta(days=395)
    prev = max((d, v) for d, v in rows if d <= hedef)
    if prev[0] >= cur[0]:
        return Olcum(None, "bulunamadi", seri, not_="13 ay önceki gözlem yok")
    pct = round((cur[1] / prev[1] - 1) * 100, 2)
    return Olcum(
        pct,
        "olculdu",
        seri,
        f"{cur[0].date()} vs {prev[0].date()}",
        f"BDDK tablo 6/2 stok bin TL; BDDK tanımı, finansal hesap F.4 ile aynı değil",
    )


def tufe_yillik() -> Olcum:
    try:
        ham = _fe([S_TUFE], "2", "01-01-2024", "07-10-2026")
    except Exception as exc:  # noqa: BLE001
        return Olcum(None, "bulunamadi", S_TUFE, not_=str(exc))
    keys = sorted(ham.keys(), key=_parse_tarih)
    if len(keys) < 2:
        return Olcum(None, "bulunamadi", S_TUFE)
    t_cur = keys[-1]
    t_parts = _parse_tarih(t_cur)
    prev_candidates = [k for k in keys if _parse_tarih(k).year == t_parts.year - 1 and _parse_tarih(k).month == t_parts.month]
    prev_key = prev_candidates[-1] if prev_candidates else None
    if not prev_key or S_TUFE not in ham[t_cur] or S_TUFE not in ham.get(prev_key, {}):
        return Olcum(None, "bulunamadi", S_TUFE, t_cur)
    y = round((ham[t_cur][S_TUFE] / ham[prev_key][S_TUFE] - 1) * 100, 2)
    return Olcum(y, "olculdu", S_TUFE, t_cur, "EVDS aylık TÜFE yıllık değişim")


def butce_faiz_harcama_pay() -> Olcum:
    p = KOK / "butce_ham.csv"
    if not p.exists():
        return Olcum(0.131, "varsayim", "", not_="butce_ham.csv yok; önceki varsayılan")
    d = pd.read_csv(p, dtype={"Donem": str})
    d["sc"] = d["Seri"].str.replace("TP.KB.", "", regex=False)
    gid = d[d.Grup == "bie_kbmgid"].copy()
    gid["yil"] = gid.Donem.str[:4]
    faiz = gid[gid.sc.isin(["GID153", "GID161", "GID162", "GID163"])].groupby("yil").Deger.sum()
    top = gid[gid.sc == "GID001"].groupby("yil").Deger.sum()
    yil = str(max(set(faiz.index) & set(top.index)))
    pay = float(faiz[yil] / top[yil]) if top[yil] else None
    if pay is None:
        return Olcum(None, "bulunamadi", "TP.KB.GID153-163 / GID001")
    return Olcum(round(pay, 4), "olculdu", "MV bütce ham", yil, "Merkezi yönetim; K′ tam değil")


def tga_kredi_oran_evds() -> Olcum:
    rows_t = _seri_zaman(S_TAKIP)
    rows_k = _seri_zaman(S_TUKETICI)
    if not rows_t or not rows_k:
        return Olcum(None, "bulunamadi", f"{S_TAKIP}/{S_TUKETICI}")
    dt = min(rows_t[-1][0], rows_k[-1][0])
    t = next(v for d, v in reversed(rows_t) if d <= dt)
    k = next(v for d, v in reversed(rows_k) if d <= dt)
    oran = round(t / k * 100, 2) if k else None
    return Olcum(oran, "olculdu", "Takip/Tüketici stok", dt.strftime("%Y-%m-%d"), "EVDS; BDDK %2,90 vs EVDS %3,13 kapsam farkı olabilir")


def sektor_finansman() -> dict:
    from tek_sistem_kopru import sektor_bilanco

    return sektor_bilanco()


def bekar_yasam() -> Olcum:
    if DIS.exists():
        j = json.loads(DIS.read_text(encoding="utf-8"))
        return Olcum(float(j["deger_TL"]), "dis_veri", j.get("kaynak", "dis_veri"), j.get("tarih", ""), j.get("not", ""))
    return Olcum(
        48885.0,
        "varsayim",
        "TÜRK-İŞ (depo dışı)",
        "2026-09",
        "dis_veri/bekar_yasam.json ile güncellenebilir",
    )


def kapsama_asgari(yasam: float) -> Olcum:
    kap = round(ASGARI / yasam, 4) if yasam else None
    return Olcum(kap, "olculdu" if yasam else "bulunamadi", "net_asgari/bekar_yasam", "", f"ASGARI={ASGARI}")


def hane_ha_pay_siniri() -> dict:
    p = KOK / "akis_model_ozeti.json"
    if p.exists():
        j = json.loads(p.read_text(encoding="utf-8"))
        return j.get("hane_alt", {}).get("ima_edilen_Ha_borc_payi_ust_siniri", {})
    return {"not": "akis_model çalıştırılmadı"}


def derle() -> dict:
    kart = buyume_13_ay(S_KART)
    tuk = buyume_13_ay(S_TUKETICI)
    tufe = tufe_yillik()
    faiz_pay = butce_faiz_harcama_pay()
    tga = tga_kredi_oran_evds()
    yasam = bekar_yasam()
    kap = kapsama_asgari(yasam.deger or 48885.0)
    sektor = sektor_finansman()
    fin24 = sektor.get("finansman_gideri", {}).get(2024)
    faal24 = sektor.get("faaliyet_kari", {}).get(2024)
    oran24 = round(fin24 / faal24, 3) if fin24 and faal24 else None

    taban = {
        "tufe_yillik_2026": tufe.deger if tufe.deger is not None else 29.73,
        "kart_buyume_13h_yillik": kart.deger if kart.deger is not None else 33.4,
        "tuketici_kredi_13h_yillik": tuk.deger if tuk.deger is not None else 13.9,
        "asgari_net_ocak2026": ASGARI,
        "bekar_yasam_eyl2026": yasam.deger,
        "kapsama_bekar_yasam": kap.deger,
    }

    meta = {
        "taban_girdi": taban,
        "olcumler": {
            "kart_13h": asdict(kart),
            "tuketici_13h": asdict(tuk),
            "tufe": asdict(tufe),
            "butce_faiz_harcama_pay": asdict(faiz_pay),
            "tga_tuketici_oran_yuzde": asdict(tga),
            "bekar_yasam": asdict(yasam),
            "kapsama": asdict(kap),
            "finansman_faaliyet_2024": {
                "finansman_milyarTL": fin24,
                "faaliyet_kari_milyarTL": faal24,
                "oran": oran24,
                "durum": "olculdu" if oran24 else "bulunamadi",
                "kaynak": sektor.get("kaynak", ""),
            },
            "hane_Ha_borc_payi_ust_siniri": hane_ha_pay_siniri(),
        },
        "hala_varsayim": [
            "Ha borç payı (D_A_BASE)",
            "K′ bütçe dışı SGK/yerel",
            "KAP bilateral ağ",
            "lam/kappa",
            "rant konut getirisi / Ho payı",
        ],
    }
    return meta


def _md(meta: dict) -> str:
    o = meta["olcumler"]
    t = meta["taban_girdi"]
    lines = [
        "# Açık veri köprüsü",
        "",
        "Taban girdileri EVDS/BDDK tablo 6/2, MV bütçe ham, Sektör Bilançoları xls (varsa) ile güncellenir.",
        "",
        "| Alan | Değer | Durum |",
        "| --- | ---: | --- |",
        f"| Kart 13 ay büyüme % | {t['kart_buyume_13h_yillik']} | {o['kart_13h']['durum']} |",
        f"| Tüketici 13 ay büyüme % | {t['tuketici_kredi_13h_yillik']} | {o['tuketici_13h']['durum']} |",
        f"| TÜFE yıllık % | {t['tufe_yillik_2026']} | {o['tufe']['durum']} |",
        f"| Bekar yaşam TL | {t['bekar_yasam_eyl2026']} | {o['bekar_yasam']['durum']} |",
        f"| Kapsama (asgari/yaşam) | {t.get('kapsama_bekar_yasam')} | {o['kapsama']['durum']} |",
        f"| Bütçe faiz/harcama | {o['butce_faiz_harcama_pay']['deger']} | {o['butce_faiz_harcama_pay']['durum']} |",
        "",
        "Bekar yaşam: `dis_veri/bekar_yasam.json` (TÜRK-İŞ vb.) ile override.",
        "",
    ]
    return "\n".join(lines)


def taban_girdi(fallback: dict | None = None) -> dict:
    """uc_kural_senaryo ve senaryo modülleri için taban sözlüğü."""
    fb = fallback or {}
    if OZET.exists():
        j = json.loads(OZET.read_text(encoding="utf-8"))
        t = dict(j.get("taban_girdi", {}))
        t.setdefault("telafi_tufe_varsayim_yuzde", fb.get("telafi_tufe_varsayim_yuzde", 30.0))
        return t
    return fb


def main():
    meta = derle()
    OZET.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = []
    for k, v in meta["olcumler"].items():
        if isinstance(v, dict) and "deger" in v:
            rows.append({"kalem": k, **v})
    with HAM.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["kalem", "deger", "durum", "seri", "tarih", "not_"], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    (KOK / "ACIK_VERI_KOPRU.md").write_text(_md(meta), encoding="utf-8")
    print("=== acik_veri_kopru ===")
    print("kart_13h%", meta["taban_girdi"]["kart_buyume_13h_yillik"], meta["olcumler"]["kart_13h"]["durum"])
    print("tuketici_13h%", meta["taban_girdi"]["tuketici_kredi_13h_yillik"])
    print("tufe%", meta["taban_girdi"]["tufe_yillik_2026"])


if __name__ == "__main__":
    main()
