"""9 Kasım 2026 veri penceresi: mevcut ham dosyalara yalnız yeni gözlem ekler.

Tarihsel satırı yeniden yazmaz. 2026-Q1 revizyonu ayrı loglanır, SFC paneline uygulanmaz.
Çalıştır: python3 veri_yenile.py
Çıktı: veri_guncelleme_log.json
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import evds_cek

KOK = Path(__file__).resolve().parent
END = "09-11-2026"
BAS = "01-01-2026"
LOG = KOK / "veri_guncelleme_log.json"

FIN_HAZNE = {
    "bie_finhestnks71011": "F",
    "bie_finhestnks71012": "B",
    "bie_finhestnks71013": "K",
    "bie_finhestnks71014": "H",
    "bie_finhestnks71015": "NPISH",
    "bie_finhestnks7102": "D",
    "bie_finhestnks7101": "TOPLAM",
}
STOK_HAZNE = {
    "bie_finhestnks11": "F",
    "bie_finhestnks14": "H",
    "bie_finhestnks12t": "PFK",
    "bie_finhestnks13": "GY",
    "bie_finhestnks2": "ROW",
}
ALTI = [
    ("faiz_ham.csv", ["bie_kt100h", "bie_kt210a"]),
    ("npl_ham.csv", ["bie_pbtop", "bie_hpbitablo6", "bie_hpbitablo2"]),
    ("butce_ham.csv", ["bie_kbmgel", "bie_kbmgid", "bie_kbgen"]),
    ("dis_borc_ham.csv", ["bie_brutdbborclu"]),
    ("prov_ham.csv", ["bie_pfvpbi10", "bie_kredi"]),
    ("s125_ham.csv", ["bie_finhestnks710125", "bie_finhestnks610125", "bie_finhestnks11"]),
    ("mahsup_evds_ham.csv", [
        "bie_finhestnks71011", "bie_finhestnks71012", "bie_finhestnks71013",
        "bie_finhestnks71014", "bie_finhestnks71015", "bie_finhestnks7102", "bie_finhestnks710121",
        "bie_finhestnks61011", "bie_finhestnks61012", "bie_finhestnks61013",
        "bie_finhestnks61014", "bie_finhestnks61015", "bie_finhestnks6102", "bie_finhestnks610121",
    ]),
    ("akim_ve_tcmb_ham.csv", [
        "bie_finhestnks6101", "bie_finhestnks61011", "bie_finhestnks61012", "bie_finhestnks61013",
        "bie_finhestnks61014", "bie_finhestnks61015", "bie_finhestnks6102", "bie_finhestnks610121",
        "bie_finhestnks710121",
    ]),
]


def _oku(yol: Path) -> tuple[list[str], list[dict]]:
    with yol.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def _yaz(yol: Path, alan: list[str], satirlar: list[dict]) -> None:
    with yol.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=alan, extrasaction="ignore")
        w.writeheader()
        w.writerows(satirlar)


def _ekle_alti(ad: str, gruplar: list[str], log: dict) -> None:
    yol = KOK / ad
    alan, satirlar = _oku(yol)
    anahtar = {(s["Grup"], s["Donem"], s["Seri"]) for s in satirlar}
    yeni = 0
    revizyon = []
    for g in gruplar:
        try:
            rows, nseri = evds_cek.fetch_group(g, start=BAS, end=END, freq="5")
        except Exception as exc:  # noqa: BLE001
            log["hata"].append({"dosya": ad, "grup": g, "neden": str(exc)})
            print(ad, g, "HATA", exc)
            continue
        print(ad, g, "seri", nseri, "satir", len(rows))
        for code, tarih, seri, isim, agg, deger in rows:
            k = (code, str(tarih), seri)
            if k in anahtar:
                if str(tarih) in ("2026-Q1", "2026-Q2") or str(tarih) >= "2026-07":
                    eski = next(s for s in satirlar if (s["Grup"], s["Donem"], s["Seri"]) == k)
                    try:
                        fark = float(deger) - float(eski["Deger"])
                    except ValueError:
                        continue
                    if abs(fark) > 1.0:
                        revizyon.append({"grup": code, "donem": str(tarih), "seri": seri, "eski": eski["Deger"], "yeni": deger, "uygulandi": False})
                continue
            satirlar.append({"Grup": code, "Donem": str(tarih), "Seri": seri, "Ad": isim, "Agg": agg, "Deger": deger})
            anahtar.add(k)
            yeni += 1
    if yeni:
        _yaz(yol, alan, satirlar)
    log["dosya"].append({"dosya": ad, "eklenen": yeni, "revizyon_uygulanmadi": len(revizyon)})
    log["revizyon_ornek"].extend(revizyon[:8])
    print(ad, "eklenen", yeni, "revizyon_log", len(revizyon))


def _ekle_finansal(log: dict) -> None:
    yol = KOK / "finansal_hesaplar_uzun.csv"
    alan, satirlar = _oku(yol)
    anahtar = {(s["Hazne"], s["Donem"], s["Seri"]) for s in satirlar}
    yeni = 0
    for g, hazne in FIN_HAZNE.items():
        try:
            rows, nseri = evds_cek.fetch_group(g, start=BAS, end=END, freq="5")
        except Exception as exc:  # noqa: BLE001
            log["hata"].append({"dosya": yol.name, "grup": g, "neden": str(exc)})
            print("finansal", g, "HATA", exc)
            continue
        print("finansal", g, hazne, nseri, len(rows))
        for _code, tarih, seri, _isim, _agg, deger in rows:
            k = (hazne, str(tarih), seri)
            if k in anahtar:
                if str(tarih) == "2026-Q1" and seri.endswith(("ZP34", "ZP5", "ZP8")):
                    eski = next(s for s in satirlar if (s["Hazne"], s["Donem"], s["Seri"]) == k)
                    log["q1_karsilastirma"].append({"hazne": hazne, "seri": seri, "depo": eski["Deger"], "evds": deger})
                continue
            satirlar.append({"Hazne": hazne, "Donem": str(tarih), "Seri": seri, "Deger": deger})
            anahtar.add(k)
            yeni += 1
    if yeni:
        _yaz(yol, alan, satirlar)
    log["dosya"].append({"dosya": yol.name, "eklenen": yeni})
    print("finansal eklenen", yeni)


def _ekle_stok_tavan(log: dict) -> None:
    yol = KOK / "stok_silim_tavan_ham.csv"
    alan, satirlar = _oku(yol)
    anahtar = {(s["grup"], s["donem"], s["seri"]) for s in satirlar}
    yeni = 0
    for g, hazne in STOK_HAZNE.items():
        try:
            rows, nseri = evds_cek.fetch_group(g, start=BAS, end=END, freq="5")
        except Exception as exc:  # noqa: BLE001
            log["hata"].append({"dosya": yol.name, "grup": g, "neden": str(exc)})
            print("stok_tavan", g, "HATA", exc)
            continue
        print("stok_tavan", g, nseri, len(rows))
        for code, tarih, seri, isim, agg, deger in rows:
            k = (code, str(tarih), seri)
            if k in anahtar:
                continue
            satirlar.append({"hazne": hazne, "grup": code, "donem": str(tarih), "seri": seri, "ad": isim, "agg": agg, "deger": deger})
            anahtar.add(k)
            yeni += 1
    if yeni:
        _yaz(yol, alan, satirlar)
    log["dosya"].append({"dosya": yol.name, "eklenen": yeni})
    print("stok_tavan eklenen", yeni)


def _seri(kod: str, freq: str) -> list[tuple[str, float]]:
    body_series = kod
    import json as _json
    import urllib.request
    body = {
        "type": "json", "series": body_series, "aggregationTypes": "last", "formulas": "0",
        "startDate": "01-01-2026", "endDate": END, "frequency": freq,
        "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR",
        "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False,
    }
    req = urllib.request.Request(
        evds_cek.BASE + "/fe", data=_json.dumps(body).encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            items = _json.loads(r.read().decode("utf-8-sig")).get("items") or []
    except Exception as exc:  # noqa: BLE001
        return [("HATA", str(exc))]  # type: ignore[list-item]
    key = kod.replace(".", "_")
    out = []
    for it in items:
        v = it.get(key)
        if v not in (None, ""):
            out.append((str(it["Tarih"]), float(str(v).replace(",", ""))))
    return out


def main() -> None:
    log: dict = {"cekme": "2026-11-09", "bitis": END, "kaynak": evds_cek.BASE, "dosya": [], "hata": [], "revizyon_ornek": [], "q1_karsilastirma": [], "sonda": {}}
    for ad, gruplar in ALTI:
        _ekle_alti(ad, gruplar, log)
    _ekle_finansal(log)
    _ekle_stok_tavan(log)
    for kod, freq in (
        ("TP.KTF17", "5"), ("TP.KTF10", "5"), ("TP.APIFON4", "5"),
        ("TP.TUKFIY2025.GENEL", "5"), ("TP.FE25.OKTG01", "5"), ("TP.FG.J0", "5"),
        ("TP.DK.USD.A.YTL", "5"), ("TP.FINHESTNKS11.ZP34", "5"), ("TP.FINHESTNKS11.ZP5", "5"),
        ("TP.FINHESTNKS14.ZP5", "5"), ("TP.FINHESTNKS14.ZP34", "5"),
        ("TP.HPBITABLO6.50", "5"), ("TP.AB.TOPLAM", "1"),
    ):
        seri = _seri(kod, freq)
        log["sonda"][kod] = seri[-6:]
        print(kod, seri[-4:])
    LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("yazildi", LOG)


if __name__ == "__main__":
    main()
