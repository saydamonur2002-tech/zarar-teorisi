"""Haftalık EVDS veri güncellemesi: yalnızca ham veri yenileme ve değişiklik özeti.

Dondurulmuş `*_ham.csv` dosyalarına (7 Ekim 2026 çekimi) dokunmaz; model girdileri ve testler aynı kalır.
Canlı kopya `veri_canli/<ad>.csv` dosyalarına yazılır. Karşılaştırma tabanı önceki canlı kopyadır;
henüz yoksa dondurulmuş `<ad>_ham.csv`. Hiçbir şey değişmediyse hiçbir dosya yazılmaz.
Model çıktıları (L/G matrisleri, skorlar) bu veriyle yeniden hesaplanmaz.

Çalıştırma: python3 haftalik_guncelle.py
Ortam: EVDS_BITIS (gg-aa-yyyy; varsayılan bugün, UTC), OZET_DOSYASI (tek satırlık özetin yazılacağı yol)
Girdi: veri_canli/kaynaklar.json (dosya, EVDS grubu, başlangıç; dondurulmuş dosyalardan türetildi)
Çıktı: veri_canli/<ad>.csv, veri_canli/GUNLUK.md, SON_GUNCELLEME.md
Çıkış kodu: 0 = sorun yok (değişiklik olsun olmasın); 1 = bir kaynak çekilemedi veya şüpheli küçüldü.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parent
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))

from evds_cek import fetch_group  # noqa: E402

BASLIK = ["Grup", "Donem", "Seri", "Ad", "Agg", "Deger"]
DENEME = 3
KUCULME_ESIGI = 0.8  # yeni çekim eski satır sayısının %80'inden azsa dosya yazılmaz
GUNLUK_SATIR = 60
ORNEK = 5


class CekmeHatasi(RuntimeError):
    pass


def oku(yol: Path) -> dict:
    """(grup, dönem, seri) -> (ad, agg, değer); eksik dosya ve NaN satırları atlanır."""
    veri: dict = {}
    if not yol.exists():
        return veri
    with open(yol, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            try:
                deger = float(r["Deger"])
                anahtar = (r["Grup"], r["Donem"], r["Seri"])
                ad, agg = r["Ad"], r["Agg"]
            except (KeyError, ValueError):
                continue
            if deger == deger:
                veri[anahtar] = (ad, agg, deger)
    return veri


def yaz(yol: Path, veri: dict) -> None:
    """Satır sırası sabit (grup, seri, dönem): git farkı yalnızca gerçek değişikliği gösterir."""
    yol.parent.mkdir(parents=True, exist_ok=True)
    gecici = yol.with_suffix(".csv.tmp")
    with open(gecici, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(BASLIK)
        for (grup, donem, seri), (ad, agg, deger) in sorted(veri.items(), key=lambda kv: (kv[0][0], kv[0][2], kv[0][1])):
            w.writerow([grup, donem, seri, ad, agg, deger])
    gecici.replace(yol)


def cek(liste: list[dict], bitis: str, getir=fetch_group, bekle=time.sleep) -> dict:
    """Bir dosyanın tüm gruplarını çeker; grup başına DENEME kez, boş yanıt hata sayılır."""
    veri: dict = {}
    for k in liste:
        for deneme in range(1, DENEME + 1):
            try:
                satirlar, _ = getir(k["grup"], start=k["baslangic"], end=bitis, freq="5")
                if not satirlar:
                    raise CekmeHatasi("boş yanıt")
                break
            except Exception as hata:  # noqa: BLE001 — ağ ve ayrıştırma hataları aynı yoldan ele alınır
                if deneme == DENEME:
                    raise CekmeHatasi(f"{k['grup']}: {hata}") from hata
                bekle(2**deneme)
        for grup, donem, seri, ad, agg, deger in satirlar:
            if deger == deger:
                veri[(grup, donem, seri)] = (ad, agg, deger)
    return veri


def karsilastir(eski: dict, yeni: dict) -> dict:
    """Yeni gözlem, silinen ve revizyon; revizyon serinin son dönemindeyse 'açık dönem' sayılır."""
    son: dict = {}
    for grup, donem, seri in yeni:
        if donem > son.get((grup, seri), ""):
            son[(grup, seri)] = donem
    yeni_k = sorted(set(yeni) - set(eski))
    acik, gecmis = [], []
    for k in sorted(set(eski) & set(yeni)):
        if eski[k][2] != yeni[k][2]:
            (acik if k[1] == son[(k[0], k[2])] else gecmis).append((k, eski[k][2], yeni[k][2]))
    eski_donem = {k[1] for k in eski}
    return {
        "yeni": yeni_k,
        "silinen": sorted(set(eski) - set(yeni)),
        "acik": acik,
        "gecmis": gecmis,
        "yeni_donemler": sorted({k[1] for k in yeni_k} - eski_donem),
        "son_once": max(eski_donem, default=""),
        "son_sonra": max((k[1] for k in yeni), default=""),
    }


def degisti(r: dict) -> bool:
    return bool(r["yeni"] or r["silinen"] or r["acik"] or r["gecmis"])


def goreli(eski: float, yeni: float) -> float:
    return abs(yeni - eski) / max(abs(eski), 1.0)


def ozet_yaz(sonuclar: dict, hatalar: dict, zaman: datetime, bitis: str, taban_donmus: list[str]) -> str:
    satir = [
        "# Son veri güncellemesi",
        "",
        f"Çalışma: {zaman:%Y-%m-%d %H:%M} UTC · EVDS3 anahtarsız uç nokta · bitiş tarihi {bitis}",
        "",
        "Karşılaştırma tabanı önceki canlı kopyadır (`veri_canli/`); ilk çalışmada dondurulmuş `*_ham.csv` (7 Ekim 2026). "
        "Model çıktıları bu veriyle yeniden hesaplanmaz.",
        "",
        "| Dosya | Yeni gözlem | Yeni dönem | Son dönem | Açık dönem güncellemesi | Geçmiş revizyon | Silinen |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: |",
    ]
    for ad, r in sonuclar.items():
        yd = ", ".join(r["yeni_donemler"][-3:]) + (" …" if len(r["yeni_donemler"]) > 3 else "") or "—"
        sd = r["son_sonra"] if r["son_once"] == r["son_sonra"] else f"{r['son_once'] or '—'} → {r['son_sonra']}"
        satir.append(f"| {ad} | {len(r['yeni'])} | {yd} | {sd} | {len(r['acik'])} | {len(r['gecmis'])} | {len(r['silinen'])} |")
    if taban_donmus:
        satir += ["", f"Not: {', '.join(taban_donmus)} için canlı kopya ilk kez oluşturuldu."]
    gecmis = [(goreli(e, y), ad, k, e, y) for ad, r in sonuclar.items() for k, e, y in r["gecmis"]]
    if gecmis:
        satir += ["", "## En büyük geçmiş revizyonlar", ""]
        for g, ad, (_, donem, seri), e, y in sorted(gecmis, reverse=True)[:ORNEK]:
            satir.append(f"- `{ad}` · `{seri}` · {donem}: {e:.6g} → {y:.6g} (%{100 * g:.2f})")
    acik = [(ad, k, e, y) for ad, r in sonuclar.items() for k, e, y in r["acik"]]
    if acik:
        satir += ["", f"Açık dönem güncellemesi ({len(acik)} seri): serinin en son dönemi, o dönem tamamlanana kadar "
                      "(ay veya çeyrek ortasında) haftadan haftaya değişebilir; revizyon sayılmamalı."]
    if hatalar:
        satir += ["", "## Çekilemeyen kaynaklar (dosya güncellenmedi)", ""]
        satir += [f"- `{ad}`: {h}" for ad, h in hatalar.items()]
    return "\n".join(satir) + "\n"


def gunluk_ekle(yol: Path, satir: str) -> None:
    onceki = []
    if yol.exists():
        onceki = [s for s in yol.read_text(encoding="utf-8").splitlines() if s.startswith("- ")]
    govde = "\n".join([satir] + onceki[: GUNLUK_SATIR - 1])
    yol.write_text("# Güncelleme günlüğü (en yeni üstte)\n\n" + govde + "\n", encoding="utf-8")


def calistir(kok: Path = KOK, bitis: str | None = None, simdi: datetime | None = None, getir=fetch_group, bekle=time.sleep) -> int:
    simdi = simdi or datetime.now(timezone.utc)
    bitis = bitis or os.environ.get("EVDS_BITIS") or simdi.strftime("%d-%m-%Y")
    canli_dizin = kok / "veri_canli"
    dosyalar: dict[str, list[dict]] = {}
    for k in json.loads((canli_dizin / "kaynaklar.json").read_text(encoding="utf-8")):
        dosyalar.setdefault(k["dosya"], []).append(k)

    sonuclar, hatalar, yazilan, ilk_kopya = {}, {}, [], []
    for ad, liste in dosyalar.items():
        canli = canli_dizin / f"{ad}.csv"
        taban = oku(canli if canli.exists() else kok / f"{ad}_ham.csv")
        try:
            yeni = cek(liste, bitis, getir, bekle)
        except CekmeHatasi as hata:
            hatalar[ad] = str(hata)
            continue
        if taban and len(yeni) < KUCULME_ESIGI * len(taban):
            hatalar[ad] = f"şüpheli küçülme: {len(taban)} → {len(yeni)} satır; dosya yazılmadı"
            continue
        r = karsilastir(taban, yeni)
        sonuclar[ad] = r
        if degisti(r) or not canli.exists():
            if not canli.exists():
                ilk_kopya.append(ad)
            yaz(canli, yeni)
            yazilan.append(ad)

    for ad, h in hatalar.items():
        print(f"HATA {ad}: {h}", file=sys.stderr)
    if yazilan:
        (kok / "SON_GUNCELLEME.md").write_text(ozet_yaz(sonuclar, hatalar, simdi, bitis, ilk_kopya), encoding="utf-8")
        degisenler = [ad for ad, r in sonuclar.items() if degisti(r)]
        yeni_n = sum(len(sonuclar[ad]["yeni"]) for ad in degisenler)
        rev_n = sum(len(sonuclar[ad]["gecmis"]) + len(sonuclar[ad]["acik"]) for ad in degisenler)
        if degisenler:
            ozet = f"{simdi:%Y-%m-%d}: {yeni_n} yeni gözlem, {rev_n} revizyon ({', '.join(degisenler)})"
            gunluk_ekle(canli_dizin / "GUNLUK.md", f"- {ozet}")
        else:
            ozet = f"{simdi:%Y-%m-%d}: değişiklik yok, canlı kopya oluşturuldu ({', '.join(ilk_kopya)})"
        if hatalar:
            ozet += f"; HATA: {', '.join(hatalar)}"
        if os.environ.get("OZET_DOSYASI"):
            Path(os.environ["OZET_DOSYASI"]).write_text(f"Veri güncellemesi {ozet}\n", encoding="utf-8")
        print(f"yazılan: {', '.join(yazilan)} | {ozet}")
    else:
        print("değişiklik yok; hiçbir dosya yazılmadı")
    return 1 if hatalar else 0


if __name__ == "__main__":
    sys.exit(calistir())
