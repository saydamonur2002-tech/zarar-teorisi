"""OVP revizyonlarından dışsal çapa. Stok-akışa yazmaz.

Son yayımlanan Orta Vadeli Program seçilir. Referans yılının öncesi, depodaki
EVDS Aralık/Aralık TÜFE'si varsa ondan doldurulur. İçinde bulunulan yıl ve
sonrası son OVP hücresinden gelir. Kur hedefi resmi tabloda yoksa boş kalır.

Çalıştır: python3 ovp_revizyon.py
Girdi: ovp_revizyonlar.json, bes_yil_senaryo_ham.json
Çıktı: ovp_revizyonlar.csv, ovp_capalar.json, ovp_revizyon_gunlugu.json, ovp_revizyon_gunlugu.md
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent
KAYIT = KOK / "ovp_revizyonlar.json"
HAM = KOK / "bes_yil_senaryo_ham.json"
S_TUFE = "TP.TUKFIY2025.GENEL"

DEGISKENLER = ("tufe_yil_sonu", "gsyh_buyume", "usd_try")
CSV_ALAN = ("yayin_tarihi", "ovp_donemi", "degisken", "yil", "deger", "rol", "birim", "kaynak_url")

# Senaryo Params.tufe_yol burada yalnız okunur diye duran sabit. Modül onu yazmaz.
SENARYO_TUFE_YOL = 0.28


def yukle(yol: Path | None = None) -> list[dict]:
    veri = json.loads((yol or KAYIT).read_text(encoding="utf-8"))
    kayit = []
    for ham in veri["kayitlar"]:
        if ham.get("deger") is None:
            continue
        kayit.append({**ham, "yil": int(ham["yil"]), "deger": float(ham["deger"])})
    return kayit


def _yayinlar(kayit: list[dict]) -> list[dict]:
    """Yayın tarihi + dönem, eskiden yeniye."""
    grup: dict[tuple[str, str], dict] = {}
    for satir in kayit:
        anahtar = (satir["yayin_tarihi"], satir["ovp_donemi"])
        grup.setdefault(anahtar, {"yayin_tarihi": satir["yayin_tarihi"], "ovp_donemi": satir["ovp_donemi"], "satirlar": []})
        grup[anahtar]["satirlar"].append(satir)
    return [grup[k] for k in sorted(grup)]


def son_yayin(kayit: list[dict]) -> dict:
    yayinlar = _yayinlar(kayit)
    if not yayinlar:
        raise ValueError("OVP kaydı yok")
    return yayinlar[-1]


def onceki_yayin(kayit: list[dict]) -> dict | None:
    yayinlar = _yayinlar(kayit)
    return yayinlar[-2] if len(yayinlar) >= 2 else None


def _hucre(yayin: dict | None, degisken: str, yil: int) -> dict | None:
    if yayin is None:
        return None
    for satir in yayin["satirlar"]:
        if satir["degisken"] == degisken and satir["yil"] == yil:
            return satir
    return None


def evds_tufe_yil_sonu(ham: dict, yil: int) -> float | None:
    """Aralık/Aralık, yüzde. Önceki Aralık yoksa None."""
    cur = ham.get(f"{yil}-12", {}).get(S_TUFE)
    prev = ham.get(f"{yil - 1}-12", {}).get(S_TUFE)
    if cur in (None, "") or prev in (None, "", 0):
        return None
    return round((float(cur) / float(prev) - 1) * 100, 2)


def evds_oku(yol: Path | None = None) -> dict:
    p = yol if yol is not None else HAM
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _evds(ham: dict, degisken: str, yil: int) -> float | None:
    if degisken == "tufe_yil_sonu":
        return evds_tufe_yil_sonu(ham, yil)
    return None


def capalar(kayit: list[dict], ham: dict, referans: date) -> dict:
    """Meta çapa. NFP, servis oranı ve bant anahtarı yok."""
    son = son_yayin(kayit)
    yillar = sorted({s["yil"] for s in kayit})

    hucreler = []
    for degisken in DEGISKENLER:
        for yil in yillar:
            if yil < referans.year:
                olcum = _evds(ham, degisken, yil)
                if olcum is None:
                    hucreler.append({
                        "degisken": degisken, "yil": yil, "deger": None, "kaynak": "bos",
                        "neden": "evds_yok", "ovp_donemi": None, "rol": None,
                    })
                else:
                    hucreler.append({
                        "degisken": degisken, "yil": yil, "deger": olcum, "kaynak": "evds",
                        "neden": f"{S_TUFE} Aralık/Aralık", "ovp_donemi": None, "rol": None,
                    })
                continue
            ovp = _hucre(son, degisken, yil)
            if ovp is None:
                hucreler.append({
                    "degisken": degisken, "yil": yil, "deger": None, "kaynak": "bos",
                    "neden": "ovp_hucre_yok", "ovp_donemi": son["ovp_donemi"], "rol": None,
                })
            else:
                hucreler.append({
                    "degisken": degisken, "yil": yil, "deger": ovp["deger"], "kaynak": "ovp",
                    "neden": ovp["rol"], "ovp_donemi": son["ovp_donemi"], "rol": ovp["rol"],
                    "kaynak_url": ovp["kaynak_url"],
                })

    yol = {}
    for yil in yillar:
        if yil < referans.year:
            continue
        h = _hucre(son, "tufe_yil_sonu", yil)
        if h is not None and h["rol"] == "program":
            yol[str(yil)] = round(h["deger"] / 100, 4)

    return {
        "stok_akis_baglanti": False,
        "referans_yil": referans.year,
        "son_ovp": {"yayin_tarihi": son["yayin_tarihi"], "ovp_donemi": son["ovp_donemi"]},
        "senaryo_tufe_yol_dokunulmadi": SENARYO_TUFE_YOL,
        "tufe_yol_ovp_program": yol,
        "hucreler": hucreler,
        "dogrulanamayan": [
            "usd_try: OVP Tablo 1.1 kur satırı yok",
            "gsyh_buyume geçmiş yıl: depoda EVDS yıllık hacim serisi bağlanmadı",
            "tufe_yil_sonu 2025 öncesi: bes_yil_senaryo_ham.json Aralık çifti yok (seri 2024-01'den)",
        ],
    }


def gunluk(kayit: list[dict]) -> dict:
    son = son_yayin(kayit)
    once = onceki_yayin(kayit)
    satirlar = []
    cift = set()
    for yayin in (son, once):
        if yayin is None:
            continue
        for s in yayin["satirlar"]:
            cift.add((s["degisken"], s["yil"]))
    for degisken, yil in sorted(cift):
        a = _hucre(son, degisken, yil)
        b = _hucre(once, degisken, yil)
        deger = None if a is None else a["deger"]
        eski = None if b is None else b["deger"]
        fark = None if deger is None or eski is None else round(deger - eski, 2)
        satirlar.append({
            "degisken": degisken,
            "yil": yil,
            "son": deger,
            "son_rol": None if a is None else a["rol"],
            "onceki": eski,
            "onceki_rol": None if b is None else b["rol"],
            "fark": fark,
        })
    return {
        "son": {"yayin_tarihi": son["yayin_tarihi"], "ovp_donemi": son["ovp_donemi"]},
        "onceki": None if once is None else {"yayin_tarihi": once["yayin_tarihi"], "ovp_donemi": once["ovp_donemi"]},
        "satirlar": satirlar,
    }


def _json(yol: Path, veri: dict) -> None:
    yol.write_text(json.dumps(veri, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _csv(yol: Path, kayit: list[dict]) -> None:
    sirali = sorted(kayit, key=lambda s: (s["yayin_tarihi"], s["ovp_donemi"], s["degisken"], s["yil"]))
    with yol.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_ALAN, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for s in sirali:
            w.writerow({k: s[k] for k in CSV_ALAN})


def _md(yol: Path, capa: dict, fark: dict) -> None:
    satir = [
        "# OVP çapa",
        "",
        "Stok-akışa bağlı değil. `uc_kural_senaryo` parametreleri yazılmaz.",
        "",
        f"Son yayın: {fark['son']['ovp_donemi']} ({fark['son']['yayin_tarihi']}).",
    ]
    if fark["onceki"]:
        satir.append(f"Önceki yayın: {fark['onceki']['ovp_donemi']} ({fark['onceki']['yayin_tarihi']}).")
    satir += [
        "",
        f"Senaryodaki `tufe_yol` {SENARYO_TUFE_YOL} duruyor. OVP program yılları ayrı yüzde-yol olarak durur.",
        "",
        "## Çapa",
        "",
        "| Değişken | Yıl | Değer | Kaynak |",
        "| --- | ---: | ---: | --- |",
    ]
    for h in capa["hucreler"]:
        deger = "—" if h["deger"] is None else h["deger"]
        satir.append(f"| {h['degisken']} | {h['yil']} | {deger} | {h['kaynak']} |")
    satir += [
        "",
        "## Revizyon",
        "",
        "Tablo iki OVP hücresini karşılaştırır. Çapa tablosundaki EVDS değeri buraya yazılmaz.",
        "",
        "| Değişken | Yıl | Son | Önceki | Fark |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for s in fark["satirlar"]:
        def _h(v):
            return "—" if v is None else v
        satir.append(f"| {s['degisken']} | {s['yil']} | {_h(s['son'])} | {_h(s['onceki'])} | {_h(s['fark'])} |")
    satir += ["", "## Doğrulanamayan", ""]
    satir += [f"- {n}" for n in capa["dogrulanamayan"]]
    satir.append("")
    yol.write_text("\n".join(satir), encoding="utf-8")


def yaz(kok: Path | None = None, referans: date | None = None, ham: dict | None = None) -> dict:
    kok = kok or KOK
    referans = referans or date.today()
    kayit = yukle(kok / "ovp_revizyonlar.json")
    if ham is None:
        ham = evds_oku(kok / "bes_yil_senaryo_ham.json")
    capa = capalar(kayit, ham, referans)
    fark = gunluk(kayit)
    _csv(kok / "ovp_revizyonlar.csv", kayit)
    _json(kok / "ovp_capalar.json", capa)
    _json(kok / "ovp_revizyon_gunlugu.json", fark)
    _md(kok / "ovp_revizyon_gunlugu.md", capa, fark)
    return {"capa": capa, "gunluk": fark}


def main() -> None:
    yaz()
    print("yazıldı: ovp_capalar.json, ovp_revizyon_gunlugu.json")


if __name__ == "__main__":
    main()
